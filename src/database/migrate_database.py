"""
JobPulse - SQLite Database Migration

Safely migrates the existing JobPulse SQLite database to the
current historical snapshot schema.

The migration:

1. Creates a physical backup of the existing database.
2. Preserves current postings.
3. Preserves the skill taxonomy.
4. Preserves current skill mentions.
5. Preserves scrape-run history.
6. Preserves historical job snapshots.
7. Converts historical snapshot skill references from
   skill_id to skill_name when required.
8. Removes the dependency of job_snapshots on current postings.
9. Validates row counts before and after migration.
10. Safely detects an already-migrated database.
11. Rolls back on failure.

Run from the project root:

    python -m src.database.migrate_database
"""

from pathlib import Path
from datetime import datetime
import shutil
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "jobpulse.db"
)

BACKUP_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "backups"
)


TABLES = [
    "postings",
    "skills",
    "skill_mentions",
    "scrape_runs",
    "job_snapshots",
    "snapshot_skill_mentions",
]


def get_table_columns(connection, table_name):
    """Return column names for a SQLite table."""

    return {
        row[1]
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }


def table_exists(connection, table_name):
    """Check whether a table exists."""

    result = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return result is not None


def get_counts(connection):
    """Return row counts for all JobPulse tables."""

    counts = {}

    for table in TABLES:

        if table_exists(
            connection,
            table,
        ):
            counts[table] = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

        else:
            counts[table] = 0

    return counts


def print_counts(title, counts):
    """Print database row counts."""

    print()
    print(title)
    print("-" * len(title))

    for table, count in counts.items():
        print(
            f"{table:<30} {count}"
        )


def validate_required_tables(connection):
    """Ensure all required JobPulse tables exist."""

    missing_tables = [
        table
        for table in TABLES
        if not table_exists(
            connection,
            table,
        )
    ]

    if missing_tables:
        raise RuntimeError(
            "Database is missing required tables: "
            f"{missing_tables}"
        )


def is_already_migrated(connection):
    """
    Detect whether the database already uses the new
    historical snapshot structure.
    """

    snapshot_skill_columns = get_table_columns(
        connection,
        "snapshot_skill_mentions",
    )

    snapshot_columns = get_table_columns(
        connection,
        "job_snapshots",
    )

    # New schema uses skill_name.
    #
    # Old schema uses skill_id.
    #
    # If skill_name exists and skill_id does not,
    # the snapshot skill migration has already happened.

    snapshot_skills_migrated = (
        "skill_name" in snapshot_skill_columns
        and "skill_id" not in snapshot_skill_columns
    )

    # Check whether job_snapshots still has a foreign key
    # pointing to postings.

    foreign_keys = connection.execute(
        """
        PRAGMA foreign_key_list(job_snapshots)
        """
    ).fetchall()

    snapshots_independent = not any(
        row[2] == "postings"
        for row in foreign_keys
    )

    return (
        snapshot_skills_migrated
        and snapshots_independent
    )


def create_backup():
    """Create a timestamped physical database backup."""

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    BACKUP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        BACKUP_DIRECTORY
        / f"jobpulse_before_migration_{timestamp}.db"
    )

    shutil.copy2(
        DATABASE_FILE,
        backup_file,
    )

    return backup_file


def migrate_snapshot_skill_mentions(connection):
    """
    Convert snapshot_skill_mentions from skill_id to
    skill_name.

    The current skill taxonomy can change over time, so
    historical snapshots store the skill name directly.
    """

    columns = get_table_columns(
        connection,
        "snapshot_skill_mentions",
    )

    # Already migrated.
    if (
        "skill_name" in columns
        and "skill_id" not in columns
    ):
        print(
            "snapshot_skill_mentions is already migrated."
        )
        return

    if "skill_id" not in columns:
        raise RuntimeError(
            "snapshot_skill_mentions has neither "
            "'skill_id' nor 'skill_name'."
        )

    print(
        "Migrating snapshot_skill_mentions..."
    )

    connection.execute(
        """
        CREATE TABLE snapshot_skill_mentions_new (
            snapshot_id INTEGER NOT NULL,
            posting_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,

            PRIMARY KEY (
                snapshot_id,
                posting_id,
                skill_name
            ),

            FOREIGN KEY (snapshot_id)
                REFERENCES job_snapshots(snapshot_id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        INSERT INTO snapshot_skill_mentions_new (
            snapshot_id,
            posting_id,
            skill_name,
            confidence
        )
        SELECT
            ssm.snapshot_id,
            ssm.posting_id,
            s.skill_name,
            ssm.confidence
        FROM snapshot_skill_mentions AS ssm
        INNER JOIN skills AS s
            ON s.skill_id = ssm.skill_id
        """
    )

    connection.execute(
        """
        DROP TABLE snapshot_skill_mentions
        """
    )

    connection.execute(
        """
        ALTER TABLE snapshot_skill_mentions_new
        RENAME TO snapshot_skill_mentions
        """
    )


def migrate_job_snapshots(connection):
    """
    Remove the foreign key from job_snapshots to postings.

    Historical snapshots must survive even if a current
    posting is later removed.
    """

    foreign_keys = connection.execute(
        """
        PRAGMA foreign_key_list(job_snapshots)
        """
    ).fetchall()

    has_postings_foreign_key = any(
        row[2] == "postings"
        for row in foreign_keys
    )

    if not has_postings_foreign_key:
        print(
            "job_snapshots is already independent "
            "of postings."
        )
        return

    print(
        "Migrating job_snapshots..."
    )

    connection.execute(
        """
        CREATE TABLE job_snapshots_new (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,

            posting_id TEXT NOT NULL,
            snapshot_date DATE NOT NULL,

            job_title TEXT,
            company TEXT,
            location TEXT,
            experience TEXT,
            posted_date DATE,
            source TEXT,
            salary_min REAL,
            salary_max REAL,
            employment_type TEXT,
            category TEXT,

            UNIQUE (
                snapshot_date,
                posting_id
            )
        )
        """
    )

    connection.execute(
        """
        INSERT INTO job_snapshots_new (
            snapshot_id,
            posting_id,
            snapshot_date,
            job_title,
            company,
            location,
            experience,
            posted_date,
            source,
            salary_min,
            salary_max,
            employment_type,
            category
        )
        SELECT
            snapshot_id,
            posting_id,
            snapshot_date,
            job_title,
            company,
            location,
            experience,
            posted_date,
            source,
            salary_min,
            salary_max,
            employment_type,
            category
        FROM job_snapshots
        """
    )

    connection.execute(
        """
        DROP TABLE job_snapshots
        """
    )

    connection.execute(
        """
        ALTER TABLE job_snapshots_new
        RENAME TO job_snapshots
        """
    )


def create_indexes(connection):
    """Create indexes required by the current schema."""

    indexes = [
        """
        CREATE INDEX IF NOT EXISTS idx_postings_source
        ON postings(source)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_postings_posted_date
        ON postings(posted_date)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_postings_company
        ON postings(company)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_postings_location
        ON postings(location)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_skill_mentions_skill
        ON skill_mentions(skill_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_skill_mentions_posting
        ON skill_mentions(posting_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_scrape_runs_source
        ON scrape_runs(source)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_scrape_runs_timestamp
        ON scrape_runs(run_timestamp)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_job_snapshots_date
        ON job_snapshots(snapshot_date)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_job_snapshots_posting
        ON job_snapshots(posting_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS
            idx_snapshot_skill_mentions_snapshot
        ON snapshot_skill_mentions(snapshot_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS
            idx_snapshot_skill_mentions_skill
        ON snapshot_skill_mentions(skill_name)
        """,
    ]

    for index_sql in indexes:
        connection.execute(index_sql)


def validate_migration(
    connection,
    before_counts,
):
    """Validate that migration preserved database records."""

    after_counts = get_counts(
        connection
    )

    # ---------------------------------------------------------
    # Row-count preservation
    # ---------------------------------------------------------

    for table in before_counts:

        before = before_counts[table]
        after = after_counts[table]

        if before != after:
            raise RuntimeError(
                f"Migration changed row count for "
                f"'{table}'. "
                f"Before: {before}, "
                f"After: {after}"
            )

    # ---------------------------------------------------------
    # Current posting IDs
    # ---------------------------------------------------------

    duplicate_postings = connection.execute(
        """
        SELECT posting_id
        FROM postings
        GROUP BY posting_id
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    if duplicate_postings:
        raise RuntimeError(
            "Duplicate posting IDs detected after migration."
        )

    # ---------------------------------------------------------
    # Historical snapshot uniqueness
    # ---------------------------------------------------------

    duplicate_snapshots = connection.execute(
        """
        SELECT
            snapshot_date,
            posting_id,
            COUNT(*)
        FROM job_snapshots
        GROUP BY
            snapshot_date,
            posting_id
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    if duplicate_snapshots:
        raise RuntimeError(
            "Duplicate historical snapshots detected."
        )

    # ---------------------------------------------------------
    # Historical skill validation
    # ---------------------------------------------------------

    snapshot_skill_columns = get_table_columns(
        connection,
        "snapshot_skill_mentions",
    )

    if "skill_name" not in snapshot_skill_columns:
        raise RuntimeError(
            "snapshot_skill_mentions does not contain "
            "skill_name after migration."
        )

    missing_skill_names = connection.execute(
        """
        SELECT COUNT(*)
        FROM snapshot_skill_mentions
        WHERE skill_name IS NULL
           OR TRIM(skill_name) = ''
        """
    ).fetchone()[0]

    if missing_skill_names:
        raise RuntimeError(
            "Historical skill mentions contain "
            "missing skill names."
        )

    # ---------------------------------------------------------
    # Validate historical snapshots are independent
    # ---------------------------------------------------------

    foreign_keys = connection.execute(
        """
        PRAGMA foreign_key_list(job_snapshots)
        """
    ).fetchall()

    references_postings = any(
        row[2] == "postings"
        for row in foreign_keys
    )

    if references_postings:
        raise RuntimeError(
            "job_snapshots still references postings."
        )

    # ---------------------------------------------------------
    # Foreign key validation
    # ---------------------------------------------------------

    foreign_key_violations = connection.execute(
        """
        PRAGMA foreign_key_check
        """
    ).fetchall()

    if foreign_key_violations:
        raise RuntimeError(
            "Foreign key violations detected after "
            f"migration: {foreign_key_violations}"
        )

    return after_counts


def main():
    """Execute the database migration."""

    print()
    print("JobPulse - Database Migration")
    print("=============================")

    print(
        f"Database: {DATABASE_FILE}"
    )

    # ---------------------------------------------------------
    # Database existence
    # ---------------------------------------------------------

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    # ---------------------------------------------------------
    # Backup
    # ---------------------------------------------------------

    backup_file = create_backup()

    print()
    print(
        f"Backup created: {backup_file}"
    )

    # ---------------------------------------------------------
    # Connect
    # ---------------------------------------------------------

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    try:

        # -----------------------------------------------------
        # Validate tables
        # -----------------------------------------------------

        validate_required_tables(
            connection
        )

        # -----------------------------------------------------
        # Capture original counts
        # -----------------------------------------------------

        before_counts = get_counts(
            connection
        )

        print_counts(
            "Before migration",
            before_counts,
        )

        # -----------------------------------------------------
        # Detect already-migrated database
        # -----------------------------------------------------

        if is_already_migrated(
            connection
        ):

            print()
            print(
                "Database already uses the current "
                "historical schema."
            )

            print(
                "No structural migration is required."
            )

            create_indexes(
                connection
            )

            connection.commit()

            after_counts = validate_migration(
                connection,
                before_counts,
            )

            print_counts(
                "Validation after migration check",
                after_counts,
            )

            print()
            print("=" * 70)
            print("DATABASE MIGRATION CHECK PASSED")
            print("=" * 70)

            print()
            print(
                "The database was already migrated "
                "successfully."
            )

            print(
                f"Backup preserved at: {backup_file}"
            )

            return

        # -----------------------------------------------------
        # Begin migration transaction
        # -----------------------------------------------------

        connection.execute(
            "BEGIN"
        )

        # -----------------------------------------------------
        # Migrate historical skills
        # -----------------------------------------------------

        migrate_snapshot_skill_mentions(
            connection
        )

        # -----------------------------------------------------
        # Migrate historical snapshots
        # -----------------------------------------------------

        migrate_job_snapshots(
            connection
        )

        # -----------------------------------------------------
        # Recreate indexes
        # -----------------------------------------------------

        create_indexes(
            connection
        )

        # -----------------------------------------------------
        # Validate before commit
        # -----------------------------------------------------

        after_counts = validate_migration(
            connection,
            before_counts,
        )

        # -----------------------------------------------------
        # Commit
        # -----------------------------------------------------

        connection.commit()

        print_counts(
            "After migration",
            after_counts,
        )

        print()
        print("=" * 70)
        print("DATABASE MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print()
        print(
            f"Backup preserved at: {backup_file}"
        )

    except Exception:

        connection.rollback()

        print()
        print(
            "Migration failed."
        )

        print(
            "The SQLite transaction was rolled back."
        )

        print(
            f"Backup remains available at: "
            f"{backup_file}"
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()
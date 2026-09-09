import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/jobpulse.db")


def verify_and_cleanup():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        print("=" * 70)
        print("JOBPULSE HISTORY SCHEMA VALIDATION")
        print("=" * 70)

        # ---------------------------------------------------------
        # 1. Remove abandoned temporary table
        # ---------------------------------------------------------
        temporary_table_exists = cursor.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'job_snapshots_new'
            """
        ).fetchone()[0]

        if temporary_table_exists:
            cursor.execute("DROP TABLE job_snapshots_new")
            print("\nRemoved abandoned table: job_snapshots_new")
        else:
            print("\nNo abandoned migration table found.")

        # ---------------------------------------------------------
        # 2. Verify historical tables exist
        # ---------------------------------------------------------
        required_tables = [
            "job_snapshots",
            "snapshot_skill_mentions",
        ]

        print("\nRequired historical tables:")

        for table in required_tables:
            exists = cursor.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = ?
                """,
                (table,),
            ).fetchone()[0]

            if not exists:
                raise RuntimeError(
                    f"Required table is missing: {table}"
                )

            print(f"  PASS: {table}")

        # ---------------------------------------------------------
        # 3. Verify job_snapshots columns
        # ---------------------------------------------------------
        snapshot_columns = {
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(job_snapshots)"
            ).fetchall()
        }

        required_snapshot_columns = {
            "snapshot_id",
            "posting_id",
            "snapshot_date",
            "job_title",
            "company",
            "location",
            "experience",
            "posted_date",
            "source",
            "salary_min",
            "salary_max",
            "employment_type",
            "category",
        }

        missing = required_snapshot_columns - snapshot_columns

        if missing:
            raise RuntimeError(
                f"job_snapshots missing columns: {sorted(missing)}"
            )

        print("\nPASS: job_snapshots schema")

        # ---------------------------------------------------------
        # 4. Verify snapshot skill columns
        # ---------------------------------------------------------
        snapshot_skill_columns = {
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(snapshot_skill_mentions)"
            ).fetchall()
        }

        required_skill_columns = {
            "snapshot_id",
            "posting_id",
            "skill_name",
            "confidence",
        }

        missing = required_skill_columns - snapshot_skill_columns

        if missing:
            raise RuntimeError(
                "snapshot_skill_mentions missing columns: "
                f"{sorted(missing)}"
            )

        print("PASS: snapshot_skill_mentions schema")

        # ---------------------------------------------------------
        # 5. Verify historical tables do NOT depend on current data
        # ---------------------------------------------------------
        snapshot_fks = cursor.execute(
            "PRAGMA foreign_key_list(job_snapshots)"
        ).fetchall()

        for fk in snapshot_fks:
            referenced_table = fk[2]

            if referenced_table == "postings":
                raise RuntimeError(
                    "job_snapshots incorrectly depends on postings."
                )

        skill_snapshot_fks = cursor.execute(
            "PRAGMA foreign_key_list(snapshot_skill_mentions)"
        ).fetchall()

        for fk in skill_snapshot_fks:
            referenced_table = fk[2]

            if referenced_table != "job_snapshots":
                raise RuntimeError(
                    "snapshot_skill_mentions has an unexpected "
                    f"foreign key to {referenced_table}."
                )

        print(
            "\nPASS: Historical tables are independent "
            "of current postings/skills."
        )

        # ---------------------------------------------------------
        # 6. Verify current data
        # ---------------------------------------------------------
        postings = cursor.execute(
            "SELECT COUNT(*) FROM postings"
        ).fetchone()[0]

        skills = cursor.execute(
            "SELECT COUNT(*) FROM skills"
        ).fetchone()[0]

        skill_mentions = cursor.execute(
            "SELECT COUNT(*) FROM skill_mentions"
        ).fetchone()[0]

        print("\nCURRENT DATA")
        print("-" * 70)
        print(f"Postings:        {postings}")
        print(f"Skills:          {skills}")
        print(f"Skill mentions:  {skill_mentions}")

        # ---------------------------------------------------------
        # 7. Verify uniqueness constraint
        # ---------------------------------------------------------
        indexes = cursor.execute(
            "PRAGMA index_list(job_snapshots)"
        ).fetchall()

        unique_snapshot_index_found = False

        for index in indexes:
            index_name = index[1]
            is_unique = index[2]

            if is_unique:
                index_columns = [
                    row[2]
                    for row in cursor.execute(
                        f'PRAGMA index_info("{index_name}")'
                    ).fetchall()
                ]

                if index_columns == [
                    "snapshot_date",
                    "posting_id",
                ]:
                    unique_snapshot_index_found = True
                    break

        if not unique_snapshot_index_found:
            raise RuntimeError(
                "Missing UNIQUE(snapshot_date, posting_id) "
                "constraint."
            )

        print(
            "\nPASS: Duplicate same-day snapshots are prevented."
        )

        # ---------------------------------------------------------
        # 8. Historical row counts
        # ---------------------------------------------------------
        historical_snapshots = cursor.execute(
            "SELECT COUNT(*) FROM job_snapshots"
        ).fetchone()[0]

        historical_skills = cursor.execute(
            "SELECT COUNT(*) FROM snapshot_skill_mentions"
        ).fetchone()[0]

        print("\nHISTORICAL DATA")
        print("-" * 70)
        print(f"Snapshot jobs:       {historical_snapshots}")
        print(f"Snapshot skills:     {historical_skills}")

        connection.commit()

        print("\n" + "=" * 70)
        print("SUCCESS: Database history architecture is valid.")
        print("=" * 70)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    verify_and_cleanup()
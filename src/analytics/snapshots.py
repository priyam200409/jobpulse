from pathlib import Path
import sqlite3
from datetime import date


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_snapshot_table(connection):
    """
    Create the historical snapshot table.

    Historical snapshots are intentionally independent from the
    current postings table so that future refreshes cannot delete
    historical market observations.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS job_snapshots (
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

            UNIQUE(snapshot_date, posting_id)
        )
        """
    )


def create_snapshot_skill_table(connection):
    """
    Create historical skill mentions.

    Skill names are stored directly so historical analysis does
    not depend on the current skills table.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS snapshot_skill_mentions (
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


def snapshot_exists(connection, snapshot_date):
    """Return True when a snapshot already exists for the date."""

    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM job_snapshots
        WHERE snapshot_date = ?
        """,
        (snapshot_date,),
    ).fetchone()[0]

    return count > 0


def create_snapshot(snapshot_date=None):
    """
    Capture the current postings and skill mentions as an
    immutable historical snapshot.

    Returns the number of jobs captured.
    """

    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    connection = get_connection()

    try:
        create_snapshot_table(connection)
        create_snapshot_skill_table(connection)

        # -----------------------------------------------------
        # Prevent duplicate snapshots
        # -----------------------------------------------------

        if snapshot_exists(
            connection,
            snapshot_date,
        ):
            existing_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM job_snapshots
                WHERE snapshot_date = ?
                """,
                (snapshot_date,),
            ).fetchone()[0]

            print(
                f"Snapshot already exists for "
                f"{snapshot_date}."
            )
            print(
                f"Jobs in snapshot: {existing_count}"
            )

            return 0

        # -----------------------------------------------------
        # Read current postings
        # -----------------------------------------------------

        jobs = connection.execute(
            """
            SELECT
                posting_id,
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
            FROM postings
            """
        ).fetchall()

        if not jobs:
            print(
                "No postings found. "
                "Snapshot was not created."
            )

            return 0

        # -----------------------------------------------------
        # Insert historical postings
        # -----------------------------------------------------

        connection.executemany(
            """
            INSERT INTO job_snapshots (
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
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            [
                (
                    row[0],          # posting_id
                    snapshot_date,
                    row[1],          # job_title
                    row[2],          # company
                    row[3],          # location
                    row[4],          # experience
                    row[5],          # posted_date
                    row[6],          # source
                    row[7],          # salary_min
                    row[8],          # salary_max
                    row[9],          # employment_type
                    row[10],         # category
                )
                for row in jobs
            ],
        )

        # -----------------------------------------------------
        # Map posting IDs to snapshot IDs
        # -----------------------------------------------------

        snapshot_rows = connection.execute(
            """
            SELECT
                snapshot_id,
                posting_id
            FROM job_snapshots
            WHERE snapshot_date = ?
            """,
            (snapshot_date,),
        ).fetchall()

        snapshot_lookup = {
            posting_id: snapshot_id
            for snapshot_id, posting_id
            in snapshot_rows
        }

        # -----------------------------------------------------
        # Copy current skill mentions
        # -----------------------------------------------------

        skill_rows = connection.execute(
            """
            SELECT
                sm.posting_id,
                s.skill_name,
                sm.confidence
            FROM skill_mentions sm
            JOIN skills s
                ON sm.skill_id = s.skill_id
            """
        ).fetchall()

        historical_skills = []

        for posting_id, skill_name, confidence in skill_rows:

            snapshot_id = snapshot_lookup.get(
                posting_id
            )

            if snapshot_id is None:
                continue

            historical_skills.append(
                (
                    snapshot_id,
                    posting_id,
                    skill_name,
                    confidence,
                )
            )

        if historical_skills:

            connection.executemany(
                """
                INSERT INTO snapshot_skill_mentions (
                    snapshot_id,
                    posting_id,
                    skill_name,
                    confidence
                )
                VALUES (?, ?, ?, ?)
                """,
                historical_skills,
            )

        connection.commit()

        # -----------------------------------------------------
        # Validate snapshot
        # -----------------------------------------------------

        jobs_captured = connection.execute(
            """
            SELECT COUNT(*)
            FROM job_snapshots
            WHERE snapshot_date = ?
            """,
            (snapshot_date,),
        ).fetchone()[0]

        skills_captured = connection.execute(
            """
            SELECT COUNT(*)
            FROM snapshot_skill_mentions ssm
            JOIN job_snapshots js
                ON ssm.snapshot_id = js.snapshot_id
            WHERE js.snapshot_date = ?
            """,
            (snapshot_date,),
        ).fetchone()[0]

        print(
            f"Snapshot date: {snapshot_date}"
        )
        print(
            f"Jobs captured: {jobs_captured}"
        )
        print(
            f"Skill relationships captured: "
            f"{skills_captured}"
        )

        return jobs_captured

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


def get_snapshot_summary():
    """Return summary statistics for every historical snapshot."""

    connection = get_connection()

    try:

        query = """
        SELECT
            snapshot_date,
            COUNT(DISTINCT posting_id) AS job_count,
            COUNT(DISTINCT company) AS companies,
            COUNT(DISTINCT location) AS locations
        FROM job_snapshots
        GROUP BY snapshot_date
        ORDER BY snapshot_date
        """

        return connection.execute(
            query
        ).fetchall()

    finally:

        connection.close()


def main():

    print("\nJobPulse - Historical Snapshot")
    print("==============================")

    today = date.today().isoformat()

    jobs_saved = create_snapshot(today)

    if jobs_saved > 0:
        print(
            f"\nSuccessfully created baseline "
            f"snapshot for {today}."
        )

    print("\nSnapshot History")
    print("----------------")

    summary = get_snapshot_summary()

    if not summary:
        print("No snapshots available.")

    else:

        print(
            "Date         Jobs    Companies    Locations"
        )

        for row in summary:

            snapshot_date = row[0]
            jobs = row[1]
            companies = row[2]
            locations = row[3]

            print(
                f"{snapshot_date}  "
                f"{jobs:<7} "
                f"{companies:<12} "
                f"{locations}"
            )


if __name__ == "__main__":
    main()
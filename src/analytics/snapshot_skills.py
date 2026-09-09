from pathlib import Path
import sqlite3
from datetime import date

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_snapshot_skill_table():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_skill_mentions (
                snapshot_id INTEGER NOT NULL,
                posting_id TEXT NOT NULL,
                skill_id INTEGER NOT NULL,
                confidence REAL DEFAULT 1.0,

                PRIMARY KEY (
                    snapshot_id,
                    posting_id,
                    skill_id
                ),

                FOREIGN KEY (snapshot_id)
                    REFERENCES job_snapshots(snapshot_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (posting_id)
                    REFERENCES postings(posting_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (skill_id)
                    REFERENCES skills(skill_id)
                    ON DELETE CASCADE
            );
            """
        )

        connection.commit()

    finally:
        connection.close()


def create_skill_snapshot(snapshot_date=None):
    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    connection = get_connection()

    try:
        snapshot = connection.execute(
            """
            SELECT snapshot_id
            FROM job_snapshots
            WHERE snapshot_date = ?
            LIMIT 1
            """,
            (snapshot_date,),
        ).fetchone()

        if snapshot is None:
            print("No job snapshot found for this date.")
            return 0

        snapshot_id = snapshot[0]

        existing = connection.execute(
            """
            SELECT COUNT(*)
            FROM snapshot_skill_mentions
            WHERE snapshot_id = ?
            """,
            (snapshot_id,),
        ).fetchone()[0]

        if existing > 0:
            print(
                f"Skill snapshot already exists "
                f"for {snapshot_date}."
            )
            print(f"Skill relationships: {existing}")
            return existing

        skills = pd.read_sql_query(
            """
            SELECT
                posting_id,
                skill_id,
                confidence
            FROM skill_mentions
            """,
            connection,
        )

        if skills.empty:
            print("No skill relationships found.")
            return 0

        skills["snapshot_id"] = snapshot_id

        skills = skills[
            [
                "snapshot_id",
                "posting_id",
                "skill_id",
                "confidence",
            ]
        ]

        skills.to_sql(
            "snapshot_skill_mentions",
            connection,
            if_exists="append",
            index=False,
        )

        connection.commit()

        return len(skills)

    finally:
        connection.close()


def get_historical_skill_demand():
    query = """
    SELECT
        js.snapshot_date,
        s.skill_name AS skill,
        s.category,
        COUNT(DISTINCT ssm.posting_id) AS job_count
    FROM snapshot_skill_mentions ssm

    JOIN job_snapshots js
        ON ssm.snapshot_id = js.snapshot_id

    JOIN skills s
        ON ssm.skill_id = s.skill_id

    GROUP BY
        js.snapshot_date,
        s.skill_id,
        s.skill_name,
        s.category

    ORDER BY
        js.snapshot_date,
        job_count DESC;
    """

    connection = get_connection()

    try:
        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


def main():
    print("\nJobPulse - Historical Skill Snapshot")
    print("====================================")

    create_snapshot_skill_table()

    today = date.today().isoformat()

    count = create_skill_snapshot(today)

    print(f"Snapshot date: {today}")
    print(f"Skill relationships captured: {count}")

    print("\nHistorical Skill Demand")
    print("-----------------------")

    demand = get_historical_skill_demand()

    if demand.empty:
        print("No historical skill data available.")
    else:
        print(demand.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
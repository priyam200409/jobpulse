import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/jobpulse.db")


def inspect_database():
    if not DATABASE_PATH.exists():
        print(f"Database not found: {DATABASE_PATH}")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 70)
    print("JOBPULSE DATABASE INSPECTION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Tables
    # ---------------------------------------------------------
    print("\nTABLES")
    print("-" * 70)

    tables = cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    for (table,) in tables:
        print(f"- {table}")

    # ---------------------------------------------------------
    # Row counts
    # ---------------------------------------------------------
    print("\nROW COUNTS")
    print("-" * 70)

    for (table,) in tables:
        count = cursor.execute(
            f"SELECT COUNT(*) FROM [{table}]"
        ).fetchone()[0]

        print(f"{table:<30} {count}")

    # ---------------------------------------------------------
    # Important schemas
    # ---------------------------------------------------------
    important_tables = [
        "postings",
        "skills",
        "skill_mentions",
        "job_snapshots",
        "snapshot_skill_mentions",
        "scrape_runs",
    ]

    print("\nTABLE SCHEMAS")
    print("-" * 70)

    for table in important_tables:
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
            print(f"\n--- {table}: NOT FOUND ---")
            continue

        schema = cursor.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (table,),
        ).fetchone()[0]

        print(f"\n--- {table} ---")
        print(schema)

    # ---------------------------------------------------------
    # Columns
    # ---------------------------------------------------------
    print("\nCOLUMN DETAILS")
    print("-" * 70)

    for table in important_tables:
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
            continue

        print(f"\n--- {table} ---")

        columns = cursor.execute(
            f"PRAGMA table_info([{table}])"
        ).fetchall()

        for column in columns:
            column_id, name, data_type, not_null, default, primary_key = column

            print(
                f"{column_id}: "
                f"{name} | "
                f"{data_type} | "
                f"NOT NULL={not_null} | "
                f"DEFAULT={default} | "
                f"PK={primary_key}"
            )

    # ---------------------------------------------------------
    # Foreign keys
    # ---------------------------------------------------------
    print("\nFOREIGN KEYS")
    print("-" * 70)

    for table in important_tables:
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
            continue

        foreign_keys = cursor.execute(
            f"PRAGMA foreign_key_list([{table}])"
        ).fetchall()

        print(f"\n--- {table} ---")

        if not foreign_keys:
            print("No foreign keys")

        for fk in foreign_keys:
            print(fk)

    # ---------------------------------------------------------
    # Existing snapshot dates
    # ---------------------------------------------------------
    print("\nSNAPSHOT DATES")
    print("-" * 70)

    snapshot_exists = cursor.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'job_snapshots'
        """
    ).fetchone()[0]

    if snapshot_exists:
        rows = cursor.execute(
            """
            SELECT snapshot_date, COUNT(*)
            FROM job_snapshots
            GROUP BY snapshot_date
            ORDER BY snapshot_date
            """
        ).fetchall()

        if rows:
            for date, count in rows:
                print(f"{date}: {count} jobs")
        else:
            print("No historical snapshots found.")

    # ---------------------------------------------------------
    # Current data validation
    # ---------------------------------------------------------
    print("\nCURRENT DATA")
    print("-" * 70)

    for table in [
        "postings",
        "skills",
        "skill_mentions",
    ]:
        exists = cursor.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (table,),
        ).fetchone()[0]

        if exists:
            count = cursor.execute(
                f"SELECT COUNT(*) FROM [{table}]"
            ).fetchone()[0]

            print(f"{table}: {count}")

    connection.close()

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    inspect_database()
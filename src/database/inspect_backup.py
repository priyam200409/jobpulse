import sqlite3
from pathlib import Path


BACKUP_PATH = Path(
    "data/jobpulse_backup_before_history_fix.db"
)


def inspect_backup():
    if not BACKUP_PATH.exists():
        raise FileNotFoundError(
            f"Backup not found: {BACKUP_PATH}"
        )

    connection = sqlite3.connect(BACKUP_PATH)
    cursor = connection.cursor()

    print("=" * 70)
    print("JOBPULSE BACKUP INSPECTION")
    print("=" * 70)

    tables = cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    print("\nTABLES")
    print("-" * 70)

    for (table,) in tables:
        count = cursor.execute(
            f"SELECT COUNT(*) FROM [{table}]"
        ).fetchone()[0]

        print(f"{table:<30} {count}")

    print("\nSNAPSHOT DATES")
    print("-" * 70)

    exists = cursor.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'job_snapshots'
        """
    ).fetchone()[0]

    if exists:
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
            print("No snapshots found.")

    print("\nSNAPSHOT SKILLS")
    print("-" * 70)

    exists = cursor.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'snapshot_skill_mentions'
        """
    ).fetchone()[0]

    if exists:
        count = cursor.execute(
            "SELECT COUNT(*) FROM snapshot_skill_mentions"
        ).fetchone()[0]

        print(f"Snapshot skill relationships: {count}")

    connection.close()

    print("\n" + "=" * 70)
    print("BACKUP INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    inspect_backup()
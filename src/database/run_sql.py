from pathlib import Path

from src.database.database import get_connection


SQL_DIR = Path("sql")


def run_query(filename: str):
    """
    Execute a SQL file and print the results.
    """

    sql_file = SQL_DIR / filename

    if not sql_file.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_file}"
        )

    sql = sql_file.read_text(
        encoding="utf-8"
    )

    connection = get_connection()

    try:
        cursor = connection.execute(sql)

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        print("\n" + filename)
        print("=" * len(filename))

        print(" | ".join(columns))
        print("-" * 80)

        for row in rows:
            print(" | ".join(str(value) for value in row))

    finally:
        connection.close()


if __name__ == "__main__":
    run_query("skill_frequency.sql")
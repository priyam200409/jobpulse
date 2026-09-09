from src.database.database import get_connection


def main():

    connection = get_connection()

    print("\nJobPulse Database Summary")
    print("=========================")

    tables = [
        "postings",
        "skills",
        "skill_mentions",
        "scrape_runs",
    ]

    for table in tables:

        result = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()

        print(f"{table}: {result[0]}")

    connection.close()


if __name__ == "__main__":
    main()
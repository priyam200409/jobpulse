from src.database.database import get_connection


def check_tables():
    connection = get_connection()

    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
    )

    tables = cursor.fetchall()

    connection.close()

    print("\nJobPulse database tables:")
    print("-------------------------")

    for table in tables:
        print(table[0])


if __name__ == "__main__":
    check_tables()
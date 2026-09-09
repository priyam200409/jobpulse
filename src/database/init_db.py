from pathlib import Path

from src.database.database import get_connection


SCHEMA_FILE = Path("sql/schema.sql")


def initialize_database():
    """
    Create all JobPulse database tables.
    """

    connection = get_connection()

    schema = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    connection.executescript(schema)

    connection.commit()
    connection.close()

    print("JobPulse database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/jobpulse.db")


def get_connection():
    """
    Create and return a SQLite database connection.
    """
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection
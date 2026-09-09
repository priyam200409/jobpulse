import pandas as pd

from src.database.database import get_connection
from src.extraction.skill_dictionary import SKILL_TAXONOMY


JOBS_FILE = "data/processed/jobs_clean.csv"
SKILLS_FILE = "data/processed/job_skills.csv"


def load_postings(connection, jobs_df):
    """
    Load job postings into the postings table.
    """

    for _, job in jobs_df.iterrows():

        connection.execute(
            """
            INSERT OR IGNORE INTO postings (
                posting_id,
                job_title,
                company,
                location,
                experience,
                description,
                requirements,
                posted_date,
                source,
                job_url,
                scraped_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job["posting_id"],
                job["job_title"],
                job["company"],
                job["location"],
                job["experience"],
                job["description"],
                job["requirements"],
                job["posted_date"],
                job["source"],
                job["job_url"],
                job["scraped_at"],
            ),
        )


def load_skills(connection):
    """
    Load the skill taxonomy into the skills table.
    """

    for skill_name, category in SKILL_TAXONOMY.items():

        connection.execute(
            """
            INSERT OR IGNORE INTO skills (
                skill_name,
                category
            )
            VALUES (?, ?)
            """,
            (skill_name, category),
        )


def load_skill_mentions(connection, skill_df):
    """
    Connect job postings with their detected skills.
    """

    for _, row in skill_df.iterrows():

        result = connection.execute(
            """
            SELECT skill_id
            FROM skills
            WHERE skill_name = ?
            """,
            (row["skill"],),
        ).fetchone()

        if result is None:
            continue

        skill_id = result[0]

        connection.execute(
            """
            INSERT OR IGNORE INTO skill_mentions (
                posting_id,
                skill_id,
                confidence
            )
            VALUES (?, ?, ?)
            """,
            (
                row["posting_id"],
                skill_id,
                1.0,
            ),
        )


def main():

    print("\nJobPulse ETL Pipeline")
    print("=====================")

    # Load CSV files
    jobs_df = pd.read_csv(JOBS_FILE)
    skill_df = pd.read_csv(SKILLS_FILE)

    print(f"Jobs loaded from CSV: {len(jobs_df)}")
    print(f"Skill relationships loaded: {len(skill_df)}")

    # Database connection
    connection = get_connection()

    try:

        # Load postings
        load_postings(
            connection,
            jobs_df
        )

        # Load skills
        load_skills(
            connection
        )

        # Load job-skill relationships
        load_skill_mentions(
            connection,
            skill_df
        )

        connection.commit()

        print("\nETL completed successfully.")

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()
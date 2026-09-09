import pandas as pd

from src.database.database import get_connection


def load_jobs() -> pd.DataFrame:
    """Load all job postings from the database."""
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT *
            FROM postings
            """,
            connection,
        )
    finally:
        connection.close()


def load_skill_frequency() -> pd.DataFrame:
    """Return skill demand by number of job postings."""
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                s.skill_name,
                s.category,
                COUNT(DISTINCT sm.posting_id) AS job_count
            FROM skill_mentions sm
            JOIN skills s
                ON sm.skill_id = s.skill_id
            GROUP BY
                s.skill_id,
                s.skill_name,
                s.category
            ORDER BY
                job_count DESC,
                s.skill_name
            """,
            connection,
        )
    finally:
        connection.close()


def load_city_volume() -> pd.DataFrame:
    """Return job volume by city."""
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                location,
                COUNT(*) AS job_count
            FROM postings
            GROUP BY location
            ORDER BY job_count DESC
            """,
            connection,
        )
    finally:
        connection.close()


def load_experience_demand() -> pd.DataFrame:
    """Return job volume by experience requirement."""
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                experience,
                COUNT(*) AS job_count
            FROM postings
            WHERE experience IS NOT NULL
              AND TRIM(experience) <> ''
            GROUP BY experience
            ORDER BY job_count DESC
            """,
            connection,
        )
    finally:
        connection.close()


def calculate_market_kpis() -> dict:
    """Calculate high-level market KPIs."""
    jobs = load_jobs()
    skill_frequency = load_skill_frequency()

    total_jobs = len(jobs)
    unique_companies = jobs["company"].nunique()
    unique_cities = jobs["location"].nunique()
    unique_skills = skill_frequency["skill_name"].nunique()

    top_skill = (
        skill_frequency.iloc[0]["skill_name"]
        if not skill_frequency.empty
        else None
    )

    return {
        "total_jobs": total_jobs,
        "unique_companies": unique_companies,
        "unique_cities": unique_cities,
        "unique_skills": unique_skills,
        "top_skill": top_skill,
    }


def main():
    print("\nJobPulse Python Analytics")
    print("=========================")

    kpis = calculate_market_kpis()

    print("\nMarket KPIs")
    print("-----------")

    for key, value in kpis.items():
        print(f"{key}: {value}")

    print("\nTop Skills")
    print("----------")

    skills = load_skill_frequency()
    print(skills.head(10).to_string(index=False))

    print("\nCity Job Volume")
    print("----------------")

    cities = load_city_volume()
    print(cities.to_string(index=False))

    print("\nExperience Demand")
    print("-----------------")

    experience = load_experience_demand()
    print(experience.to_string(index=False))


if __name__ == "__main__":
    main()
    
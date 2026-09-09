from pathlib import Path
import sqlite3

import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "jobpulse.db"
)

EXPERIENCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_experience.csv"
)

GEOGRAPHY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_geography.csv"
)

DATA_QUALITY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "data_quality_report.csv"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create a read-only analytics connection to JobPulse SQLite.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    return sqlite3.connect(DATABASE_PATH)


# =========================================================
# MARKET SUMMARY
# =========================================================

def get_market_summary() -> dict:
    """
    Return high-level JobPulse market KPIs.
    """

    query = """
        SELECT
            COUNT(*) AS total_jobs,
            COUNT(DISTINCT company) AS unique_companies,
            COUNT(DISTINCT location) AS unique_locations,
            COUNT(DISTINCT job_title) AS unique_job_titles
        FROM postings;
    """

    with get_connection() as connection:

        row = connection.execute(query).fetchone()

    return {
        "total_jobs": row[0],
        "unique_companies": row[1],
        "unique_locations": row[2],
        "unique_job_titles": row[3],
    }


# =========================================================
# SKILL DEMAND
# =========================================================

def get_skill_demand() -> pd.DataFrame:
    """
    Return skill demand by number of unique job postings.

    One posting can mention multiple skills.
    """

    query = """
        SELECT
            s.skill_name AS skill,
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
            skill ASC;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            query,
            connection,
        )

    return df


# =========================================================
# SKILL PENETRATION
# =========================================================

def get_skill_penetration() -> pd.DataFrame:
    """
    Calculate the percentage of all postings containing
    each detected skill.
    """

    query = """
        SELECT
            s.skill_name AS skill,
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
            skill ASC;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            query,
            connection,
        )

        total_jobs = connection.execute(
            "SELECT COUNT(*) FROM postings"
        ).fetchone()[0]

    if total_jobs > 0:

        df["market_penetration_pct"] = (
            df["job_count"]
            / total_jobs
            * 100
        )

    else:

        df["market_penetration_pct"] = 0.0

    return df


# =========================================================
# CITY DEMAND
# =========================================================

def get_city_demand() -> pd.DataFrame:
    """
    Return job demand by actual city only.

    Nationwide, state-level, and unresolved records
    are excluded because they are not city-level demand.
    """

    if not GEOGRAPHY_FILE.exists():
        raise FileNotFoundError(
            f"Geography file not found: {GEOGRAPHY_FILE}"
        )

    geography = pd.read_csv(
        GEOGRAPHY_FILE
    )

    required_columns = {
        "city",
        "scope",
    }

    missing_columns = (
        required_columns
        - set(geography.columns)
    )

    if missing_columns:
        raise ValueError(
            "job_geography.csv is missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    city_demand = (
        geography[
            geography["scope"].eq("City")
            & geography["city"].notna()
            & geography["city"].ne("")
            & geography["city"].ne("Unknown")
        ]
        .groupby("city")
        .size()
        .reset_index(
            name="job_count"
        )
        .sort_values(
            ["job_count", "city"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    return city_demand

def get_geography_scope() -> pd.DataFrame:
    """
    Return job distribution by geographic scope.

    Scope categories:
        City
        Nationwide
        State
        Unresolved
    """

    if not GEOGRAPHY_FILE.exists():
        raise FileNotFoundError(
            f"Geography file not found: {GEOGRAPHY_FILE}"
        )

    geography = pd.read_csv(
        GEOGRAPHY_FILE
    )

    if "scope" not in geography.columns:
        raise ValueError(
            "job_geography.csv does not contain "
            "a 'scope' column."
        )

    scope_distribution = (
        geography
        .groupby("scope")
        .size()
        .reset_index(
            name="job_count"
        )
        .sort_values(
            "job_count",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return scope_distribution
# =========================================================
# EXPERIENCE DISTRIBUTION
# =========================================================

def get_experience_distribution() -> pd.DataFrame:
    """
    Return distribution of extracted experience requirements.
    """

    if not EXPERIENCE_FILE.exists():
        raise FileNotFoundError(
            f"Experience file not found: {EXPERIENCE_FILE}"
        )

    experience = pd.read_csv(
        EXPERIENCE_FILE
    )

    distribution = (
        experience[
            experience["experience_bucket"]
            != "Not specified"
        ]
        .groupby(
            "experience_bucket"
        )
        .size()
        .reset_index(
            name="job_count"
        )
        .sort_values(
            "job_count",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return distribution


# =========================================================
# EXPERIENCE SUMMARY
# =========================================================

def get_experience_summary() -> dict:
    """
    Return high-level experience coverage metrics.
    """

    if not EXPERIENCE_FILE.exists():
        raise FileNotFoundError(
            f"Experience file not found: {EXPERIENCE_FILE}"
        )

    experience = pd.read_csv(
        EXPERIENCE_FILE
    )

    total_jobs = len(experience)

    detected_jobs = (
        experience["experience_bucket"]
        != "Not specified"
    ).sum()

    fresher_jobs = (
        experience["experience_bucket"]
        == "Fresher"
    ).sum()

    coverage = (
        detected_jobs / total_jobs * 100
        if total_jobs > 0
        else 0
    )

    return {
        "total_jobs": total_jobs,
        "jobs_with_experience": int(detected_jobs),
        "experience_coverage_pct": round(
            float(coverage),
            2,
        ),
        "fresher_jobs": int(fresher_jobs),
    }


# =========================================================
# SALARY SUMMARY
# =========================================================

def get_salary_summary() -> dict:
    """
    Return salary coverage and summary statistics.

    Salary metrics are calculated only for postings
    containing salary information.
    """

    query = """
        SELECT
            COUNT(*) AS total_jobs,
            SUM(
                CASE
                    WHEN salary_min IS NOT NULL
                      OR salary_max IS NOT NULL
                    THEN 1
                    ELSE 0
                END
            ) AS jobs_with_salary,

            AVG(salary_min) AS average_salary_min,
            AVG(salary_max) AS average_salary_max
        FROM postings;
    """

    median_query = """
        SELECT
            salary_min,
            salary_max
        FROM postings
        WHERE
            salary_min IS NOT NULL
            OR salary_max IS NOT NULL
        ORDER BY salary_min;
    """

    with get_connection() as connection:

        row = connection.execute(
            query
        ).fetchone()

        salary_df = pd.read_sql_query(
            median_query,
            connection,
        )

    total_jobs = row[0] or 0
    jobs_with_salary = row[1] or 0

    coverage = (
        jobs_with_salary / total_jobs * 100
        if total_jobs > 0
        else 0
    )

    median_salary_min = (
        salary_df["salary_min"].median()
        if not salary_df.empty
        else None
    )

    median_salary_max = (
        salary_df["salary_max"].median()
        if not salary_df.empty
        else None
    )

    return {
        "total_jobs": int(total_jobs),
        "jobs_with_salary": int(jobs_with_salary),
        "salary_coverage_pct": round(
            coverage,
            2,
        ),
        "average_salary_min": (
            round(row[2], 2)
            if row[2] is not None
            else None
        ),
        "average_salary_max": (
            round(row[3], 2)
            if row[3] is not None
            else None
        ),
        "median_salary_min": (
            float(median_salary_min)
            if pd.notna(median_salary_min)
            else None
        ),
        "median_salary_max": (
            float(median_salary_max)
            if pd.notna(median_salary_max)
            else None
        ),
    }


# =========================================================
# SKILL CO-OCCURRENCE
# =========================================================

def get_skill_cooccurrence(
    limit: int = 20,
) -> pd.DataFrame:
    """
    Return the most common pairs of skills appearing
    in the same job posting.
    """

    query = """
        SELECT
            s1.skill_name AS skill_1,
            s2.skill_name AS skill_2,
            COUNT(DISTINCT sm1.posting_id) AS job_count

        FROM skill_mentions sm1

        JOIN skill_mentions sm2
            ON sm1.posting_id = sm2.posting_id
            AND sm1.skill_id < sm2.skill_id

        JOIN skills s1
            ON sm1.skill_id = s1.skill_id

        JOIN skills s2
            ON sm2.skill_id = s2.skill_id

        GROUP BY
            sm1.skill_id,
            sm2.skill_id,
            s1.skill_name,
            s2.skill_name

        ORDER BY
            job_count DESC,
            skill_1 ASC,
            skill_2 ASC

        LIMIT ?;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            query,
            connection,
            params=(limit,),
        )

    return df


# =========================================================
# JOB TITLE DEMAND
# =========================================================

def get_job_titles(
    limit: int = 20,
) -> pd.DataFrame:
    """
    Return the most common job titles.
    """

    query = """
        SELECT
            job_title,
            COUNT(*) AS job_count
        FROM postings
        WHERE
            job_title IS NOT NULL
            AND TRIM(job_title) != ''
        GROUP BY job_title
        ORDER BY
            job_count DESC,
            job_title ASC
        LIMIT ?;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            query,
            connection,
            params=(limit,),
        )

    return df


# =========================================================
# DATA QUALITY SUMMARY
# =========================================================

def get_data_quality() -> pd.DataFrame:
    """
    Return the generated data-quality report.
    """

    if not DATA_QUALITY_FILE.exists():
        raise FileNotFoundError(
            f"Data quality report not found: "
            f"{DATA_QUALITY_FILE}"
        )

    return pd.read_csv(
        DATA_QUALITY_FILE
    )


# =========================================================
# COMPLETE MARKET SNAPSHOT
# =========================================================

def get_market_snapshot() -> dict:
    """
    Return the primary analytical datasets required
    by the JobPulse dashboard.
    """

    return {
        "market_summary": get_market_summary(),
        "geography_scope": get_geography_scope(),
        "skill_demand": get_skill_demand(),
        "skill_penetration": get_skill_penetration(),
        "city_demand": get_city_demand(),
        "experience_distribution": (
            get_experience_distribution()
        ),
        "experience_summary": (
            get_experience_summary()
        ),
        "salary_summary": get_salary_summary(),
        "skill_cooccurrence": (
            get_skill_cooccurrence()
        ),
        "job_titles": get_job_titles(),
        "data_quality": get_data_quality(),
    }


# =========================================================
# VALIDATION / DEMO
# =========================================================

def main():

    print("\nJobPulse - Unified Analytics Engine")
    print("====================================")

    summary = get_market_summary()

    print("\nMarket Summary")
    print("--------------")

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )

    print("\nTop Skills")
    print("----------")

    print(
        get_skill_demand()
        .head(10)
        .to_string(index=False)
    )

    print("\nTop Cities")
    print("----------")

    print(
        get_city_demand()
        .head(10)
        .to_string(index=False)
    )

    print("\nExperience Summary")
    print("------------------")

    print(
        get_experience_summary()
    )

    print("\nSalary Summary")
    print("--------------")

    print(
        get_salary_summary()
    )

    print("\nTop Skill Relationships")
    print("-----------------------")

    print(
        get_skill_cooccurrence()
        .head(10)
        .to_string(index=False)
    )

    print("\nTop Job Titles")
    print("--------------")

    print(
        get_job_titles()
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
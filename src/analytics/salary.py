from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_salary_data():
    """Return jobs containing usable salary information."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        query = """
        SELECT
            posting_id,
            job_title,
            company,
            location,
            salary_min,
            salary_max,
            employment_type,
            category
        FROM postings
        WHERE
            salary_min IS NOT NULL
            OR salary_max IS NOT NULL;
        """

        return pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()


def calculate_salary_metrics(df):
    """Calculate salary coverage and summary statistics."""

    total_jobs = None

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        total_jobs = connection.execute(
            "SELECT COUNT(*) FROM postings"
        ).fetchone()[0]
    finally:
        connection.close()

    jobs_with_salary = len(df)

    coverage = (
        jobs_with_salary / total_jobs * 100
        if total_jobs
        else 0
    )

    valid_min = df["salary_min"].dropna()
    valid_max = df["salary_max"].dropna()

    metrics = {
        "total_jobs": total_jobs,
        "jobs_with_salary": jobs_with_salary,
        "salary_coverage_percentage": round(
            coverage,
            2
        ),
        "median_salary_min": (
            round(valid_min.median(), 2)
            if not valid_min.empty
            else None
        ),
        "median_salary_max": (
            round(valid_max.median(), 2)
            if not valid_max.empty
            else None
        ),
        "average_salary_min": (
            round(valid_min.mean(), 2)
            if not valid_min.empty
            else None
        ),
        "average_salary_max": (
            round(valid_max.mean(), 2)
            if not valid_max.empty
            else None
        ),
    }

    return metrics


def salary_by_city(df):
    """Calculate salary statistics by normalized raw location."""

    result = (
        df.groupby("location")
        .agg(
            jobs_with_salary=("posting_id", "nunique"),
            median_salary_min=("salary_min", "median"),
            median_salary_max=("salary_max", "median"),
        )
        .reset_index()
    )

    return result.sort_values(
        "jobs_with_salary",
        ascending=False
    )


def main():

    print("\nJobPulse - Salary Analytics")
    print("===========================")

    df = get_salary_data()

    print(
        f"Jobs with salary data: {len(df)}"
    )

    metrics = calculate_salary_metrics(df)

    print("\nSalary Metrics")
    print("--------------")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print("\nSalary by location:")

    city_salary = salary_by_city(df)

    print(
        city_salary
        .head(15)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
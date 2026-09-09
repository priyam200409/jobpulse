from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_snapshot_count():
    """Return the number of distinct historical snapshots."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT COUNT(DISTINCT snapshot_date)
            FROM job_snapshots
            """
        ).fetchone()[0]

    finally:
        connection.close()


def get_weekly_job_trends():
    """
    Calculate weekly snapshot job volume and WoW change.

    WoW is calculated only when a previous weekly observation
    exists. With fewer than two snapshots, the percentage is NULL.
    """

    query = """
    WITH weekly_jobs AS (
        SELECT
            strftime('%Y-%W', snapshot_date) AS week,
            MAX(snapshot_date) AS snapshot_date,
            COUNT(DISTINCT posting_id) AS job_count
        FROM job_snapshots
        GROUP BY strftime('%Y-%W', snapshot_date)
    ),

    weekly_with_previous AS (
        SELECT
            week,
            snapshot_date,
            job_count,
            LAG(job_count) OVER (
                ORDER BY snapshot_date
            ) AS previous_week_jobs
        FROM weekly_jobs
    )

    SELECT
        week,
        snapshot_date,
        job_count,
        previous_week_jobs,

        CASE
            WHEN previous_week_jobs IS NULL
                THEN NULL

            WHEN previous_week_jobs = 0
                THEN NULL

            ELSE ROUND(
                100.0 * (
                    job_count - previous_week_jobs
                ) / previous_week_jobs,
                2
            )
        END AS wow_change_percentage

    FROM weekly_with_previous

    ORDER BY snapshot_date;
    """

    connection = get_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()


def get_monthly_job_trends():
    """
    Calculate monthly snapshot job volume and MoM change.
    """

    query = """
    WITH monthly_jobs AS (
        SELECT
            strftime('%Y-%m', snapshot_date) AS month,
            MAX(snapshot_date) AS snapshot_date,
            COUNT(DISTINCT posting_id) AS job_count
        FROM job_snapshots
        GROUP BY strftime('%Y-%m', snapshot_date)
    ),

    monthly_with_previous AS (
        SELECT
            month,
            snapshot_date,
            job_count,
            LAG(job_count) OVER (
                ORDER BY snapshot_date
            ) AS previous_month_jobs
        FROM monthly_jobs
    )

    SELECT
        month,
        snapshot_date,
        job_count,
        previous_month_jobs,

        CASE
            WHEN previous_month_jobs IS NULL
                THEN NULL

            WHEN previous_month_jobs = 0
                THEN NULL

            ELSE ROUND(
                100.0 * (
                    job_count - previous_month_jobs
                ) / previous_month_jobs,
                2
            )
        END AS mom_change_percentage

    FROM monthly_with_previous

    ORDER BY snapshot_date;
    """

    connection = get_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()


def get_skill_trends():
    """
    Return historical skill demand using the immutable
    snapshot_skill_mentions table.
    """

    query = """
    SELECT
        js.snapshot_date,
        ssm.skill_name AS skill,
        COUNT(DISTINCT ssm.posting_id) AS job_count

    FROM snapshot_skill_mentions ssm

    JOIN job_snapshots js
        ON ssm.snapshot_id = js.snapshot_id

    GROUP BY
        js.snapshot_date,
        ssm.skill_name

    ORDER BY
        js.snapshot_date,
        job_count DESC,
        ssm.skill_name;
    """

    connection = get_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()


def main():

    print("\nJobPulse - Trend Analytics")
    print("==========================")

    snapshot_count = get_snapshot_count()

    print(
        f"\nHistorical snapshots available: "
        f"{snapshot_count}"
    )

    if snapshot_count < 2:

        print(
            "\nTrend status: INSUFFICIENT HISTORY"
        )

        print(
            "At least two historical snapshots are "
            "required for change calculations."
        )

    weekly = get_weekly_job_trends()

    print("\nWeekly Job Trends")
    print("-----------------")

    if weekly.empty:
        print("No historical data available.")

    else:
        print(
            weekly.to_string(
                index=False
            )
        )

    monthly = get_monthly_job_trends()

    print("\nMonthly Job Trends")
    print("------------------")

    if monthly.empty:
        print("No historical data available.")

    else:
        print(
            monthly.to_string(
                index=False
            )
        )

    skills = get_skill_trends()

    print("\nHistorical Skill Trends")
    print("-----------------------")

    if skills.empty:
        print("No historical skill data available.")

    else:
        print(
            skills.head(20).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()
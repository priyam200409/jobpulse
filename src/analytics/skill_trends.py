from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_skill_growth():
    """
    Compare the latest two historical snapshots.

    If fewer than two snapshots exist, growth percentages
    remain unavailable rather than being fabricated.
    """

    query = """
    WITH snapshot_dates AS (
        SELECT
            snapshot_date,
            ROW_NUMBER() OVER (
                ORDER BY snapshot_date DESC
            ) AS snapshot_rank
        FROM (
            SELECT DISTINCT snapshot_date
            FROM job_snapshots
        )
    ),

    skill_demand AS (
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
    ),

    current_period AS (
        SELECT
            sd.skill,
            sd.job_count AS current_jobs
        FROM skill_demand sd

        JOIN snapshot_dates dates
            ON sd.snapshot_date = dates.snapshot_date

        WHERE dates.snapshot_rank = 1
    ),

    previous_period AS (
        SELECT
            sd.skill,
            sd.job_count AS previous_jobs
        FROM skill_demand sd

        JOIN snapshot_dates dates
            ON sd.snapshot_date = dates.snapshot_date

        WHERE dates.snapshot_rank = 2
    ),

    combined AS (
        SELECT skill
        FROM current_period

        UNION

        SELECT skill
        FROM previous_period
    )

    SELECT
        combined.skill,

        COALESCE(
            current_period.current_jobs,
            0
        ) AS current_jobs,

        COALESCE(
            previous_period.previous_jobs,
            0
        ) AS previous_jobs,

        CASE
            WHEN previous_period.previous_jobs IS NULL
                THEN NULL

            ELSE
                COALESCE(
                    current_period.current_jobs,
                    0
                )
                -
                previous_period.previous_jobs
        END AS job_change,

        CASE
            WHEN previous_period.previous_jobs IS NULL
                THEN NULL

            WHEN previous_period.previous_jobs = 0
                THEN NULL

            ELSE ROUND(
                100.0 * (
                    COALESCE(
                        current_period.current_jobs,
                        0
                    )
                    -
                    previous_period.previous_jobs
                )
                /
                previous_period.previous_jobs,
                2
            )
        END AS growth_percentage

    FROM combined

    LEFT JOIN current_period
        ON combined.skill = current_period.skill

    LEFT JOIN previous_period
        ON combined.skill = previous_period.skill

    ORDER BY
        current_jobs DESC,
        combined.skill ASC;
    """

    connection = get_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
        )

    finally:
        connection.close()


def get_growing_skills(limit=10):
    """Return skills with positive growth."""

    growth = get_skill_growth()

    if growth.empty:
        return growth

    return (
        growth[
            growth["growth_percentage"] > 0
        ]
        .sort_values(
            [
                "growth_percentage",
                "job_change",
            ],
            ascending=False,
        )
        .head(limit)
    )


def get_declining_skills(limit=10):
    """Return skills with negative growth."""

    growth = get_skill_growth()

    if growth.empty:
        return growth

    return (
        growth[
            growth["growth_percentage"] < 0
        ]
        .sort_values(
            [
                "growth_percentage",
                "job_change",
            ],
            ascending=True,
        )
        .head(limit)
    )


def main():

    print(
        "\nJobPulse - Skill Growth Analytics"
    )

    print(
        "================================="
    )

    growth = get_skill_growth()

    if growth.empty:

        print(
            "\nNo historical skill data available."
        )

        return

    if growth["growth_percentage"].notna().sum() == 0:

        print(
            "\nSkill growth: INSUFFICIENT HISTORY"
        )

        print(
            "At least two snapshots are required "
            "to calculate skill growth."
        )

        print(
            "\nCurrent snapshot skill demand:"
        )

        print(
            growth[
                [
                    "skill",
                    "current_jobs",
                ]
            ].to_string(
                index=False
            )
        )

        return

    print("\nSkill Growth")
    print("------------")

    print(
        growth.to_string(
            index=False
        )
    )

    growing = get_growing_skills()

    print("\nGrowing Skills")
    print("--------------")

    if growing.empty:
        print("No growing skills.")

    else:
        print(
            growing.to_string(
                index=False
            )
        )

    declining = get_declining_skills()

    print("\nDeclining Skills")
    print("-----------------")

    if declining.empty:
        print("No declining skills.")

    else:
        print(
            declining.to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()
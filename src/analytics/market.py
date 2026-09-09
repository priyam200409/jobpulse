from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def get_market_summary():
    """Return high-level market metrics."""

    connection = get_connection()

    try:
        query = """
        SELECT
            COUNT(*) AS total_jobs,
            COUNT(DISTINCT company) AS unique_companies,
            COUNT(DISTINCT location) AS unique_locations,
            COUNT(DISTINCT job_title) AS unique_job_titles
        FROM postings;
        """

        return pd.read_sql_query(
            query,
            connection
        ).iloc[0].to_dict()

    finally:
        connection.close()


def get_skill_demand():
    """Return skill demand and penetration."""

    connection = get_connection()

    try:
        query = """
        WITH total_jobs AS (
            SELECT COUNT(*) AS total
            FROM postings
        ),

        skill_jobs AS (
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
        )

        SELECT
            skill,
            category,
            job_count,
            total_jobs.total AS total_jobs,
            ROUND(
                100.0 * job_count / total_jobs.total,
                2
            ) AS penetration_percentage
        FROM skill_jobs
        CROSS JOIN total_jobs
        ORDER BY
            job_count DESC,
            skill ASC;
        """

        return pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()


def get_city_demand():
    """Return job volume by location."""

    connection = get_connection()

    try:
        query = """
        SELECT
            location,
            COUNT(DISTINCT posting_id) AS job_count
        FROM postings
        GROUP BY location
        ORDER BY
            job_count DESC,
            location ASC;
        """

        return pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()


def get_skill_cooccurrence():
    """Return skill pairs appearing in the same jobs."""

    connection = get_connection()

    try:
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
            s1.skill_id,
            s2.skill_id,
            s1.skill_name,
            s2.skill_name

        ORDER BY
            job_count DESC,
            skill_1 ASC,
            skill_2 ASC;
        """

        return pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()


def get_job_titles():
    """Return job-title distribution."""

    connection = get_connection()

    try:
        query = """
        SELECT
            job_title,
            COUNT(*) AS job_count
        FROM postings
        GROUP BY job_title
        ORDER BY
            job_count DESC,
            job_title ASC;
        """

        return pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()


def get_salary_summary():
    """Return salary coverage and basic salary statistics."""

    connection = get_connection()

    try:
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

            ROUND(
                AVG(salary_min),
                2
            ) AS avg_salary_min,

            ROUND(
                AVG(salary_max),
                2
            ) AS avg_salary_max

        FROM postings;
        """

        return pd.read_sql_query(
            query,
            connection
        ).iloc[0].to_dict()

    finally:
        connection.close()
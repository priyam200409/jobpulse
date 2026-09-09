from pathlib import Path
from datetime import datetime, timezone
import sqlite3

import pandas as pd

from src.database.database import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOBS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)

SKILLS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_skills.csv"
)

SCHEMA_FILE = (
    PROJECT_ROOT
    / "sql"
    / "schema.sql"
)


POSTING_COLUMNS = [
    "posting_id",
    "job_title",
    "company",
    "location",
    "experience",
    "description",
    "requirements",
    "posted_date",
    "source",
    "job_url",
    "scraped_at",
    "salary_min",
    "salary_max",
    "employment_type",
    "category",
]


def initialize_database(connection):
    """Create required database tables if they do not exist."""

    schema = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    connection.executescript(schema)
    connection.commit()


def validate_inputs(jobs, skills_df):
    """Validate the processed input datasets before loading."""

    required_job_columns = {
        "posting_id",
        "job_title",
        "company",
        "location",
        "description",
        "posted_date",
        "source",
        "job_url",
    }

    required_skill_columns = {
        "posting_id",
        "skill",
        "confidence",
    }

    missing_job_columns = (
        required_job_columns - set(jobs.columns)
    )

    missing_skill_columns = (
        required_skill_columns - set(skills_df.columns)
    )

    if missing_job_columns:
        raise ValueError(
            "jobs_clean.csv is missing columns: "
            f"{sorted(missing_job_columns)}"
        )

    if missing_skill_columns:
        raise ValueError(
            "job_skills.csv is missing columns: "
            f"{sorted(missing_skill_columns)}"
        )

    if jobs["posting_id"].isna().any():
        raise ValueError(
            "jobs_clean.csv contains missing posting_id values."
        )

    if skills_df["posting_id"].isna().any():
        raise ValueError(
            "job_skills.csv contains missing posting_id values."
        )

    duplicate_jobs = jobs["posting_id"].duplicated().sum()

    if duplicate_jobs:
        raise ValueError(
            "jobs_clean.csv contains "
            f"{duplicate_jobs} duplicate posting IDs."
        )

    invalid_skill_relationships = (
        ~skills_df["posting_id"].isin(
            jobs["posting_id"]
        )
    ).sum()

    if invalid_skill_relationships:
        raise ValueError(
            "job_skills.csv contains skill relationships "
            "for posting IDs that are not present in jobs_clean.csv: "
            f"{invalid_skill_relationships}"
        )


def load_postings(connection, jobs):
    """
    Upsert current job postings.

    Existing posting IDs are updated.
    New posting IDs are inserted.
    """

    columns = [
        column
        for column in POSTING_COLUMNS
        if column in jobs.columns
    ]

    records = jobs[columns].where(
        pd.notna(jobs[columns]),
        None,
    ).to_dict("records")

    sql_columns = ", ".join(columns)

    update_columns = [
        column
        for column in columns
        if column != "posting_id"
    ]

    update_clause = ", ".join(
        f"{column}=excluded.{column}"
        for column in update_columns
    )

    placeholders = ", ".join(
        "?" for _ in columns
    )

    sql = f"""
        INSERT INTO postings (
            {sql_columns}
        )
        VALUES (
            {placeholders}
        )
        ON CONFLICT(posting_id)
        DO UPDATE SET
            {update_clause}
    """

    before = connection.execute(
        "SELECT COUNT(*) FROM postings"
    ).fetchone()[0]

    connection.executemany(
        sql,
        [
            tuple(record[column] for column in columns)
            for record in records
        ],
    )

    after = connection.execute(
        "SELECT COUNT(*) FROM postings"
    ).fetchone()[0]

    new_records = after - before

    return len(records), new_records


def load_skills(connection, skills_df):
    """
    Insert newly discovered skills into the skill dictionary.

    Existing skills are left unchanged.
    """

    from src.extraction.skill_dictionary import SKILL_TAXONOMY

    unique_skills = (
        skills_df["skill"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .unique()
    )

    records = []

    for skill in unique_skills:

        category = SKILL_TAXONOMY.get(
            skill,
            "Other",
        )

        records.append(
            (
                skill,
                category,
            )
        )

    connection.executemany(
        """
        INSERT INTO skills (
            skill_name,
            category
        )
        VALUES (?, ?)
        ON CONFLICT(skill_name)
        DO NOTHING
        """,
        records,
    )

    return len(records)


def load_skill_mentions(connection, skills_df):
    """
    Replace current skill mentions for affected postings.

    This prevents stale skill relationships when a posting's
    description changes between collection runs.
    """

    skill_lookup = pd.read_sql_query(
        """
        SELECT
            skill_id,
            skill_name
        FROM skills
        """,
        connection,
    )

    merged = skills_df.merge(
        skill_lookup,
        left_on="skill",
        right_on="skill_name",
        how="inner",
    )

    mentions = merged[
        [
            "posting_id",
            "skill_id",
            "confidence",
        ]
    ].drop_duplicates(
        subset=[
            "posting_id",
            "skill_id",
        ]
    )

    affected_postings = (
        skills_df["posting_id"]
        .dropna()
        .unique()
        .tolist()
    )

    if affected_postings:

        placeholders = ", ".join(
            "?" for _ in affected_postings
        )

        connection.execute(
            f"""
            DELETE FROM skill_mentions
            WHERE posting_id IN (
                {placeholders}
            )
            """,
            affected_postings,
        )

    records = [
        (
            row.posting_id,
            int(row.skill_id),
            float(row.confidence),
        )
        for row in mentions.itertuples(index=False)
    ]

    if records:
        connection.executemany(
            """
            INSERT INTO skill_mentions (
                posting_id,
                skill_id,
                confidence
            )
            VALUES (?, ?, ?)
            """,
            records,
        )

    return len(records)


def record_scrape_run(
    connection,
    source,
    records_collected,
    records_new,
    records_failed=0,
):
    """Record operational metadata for this ingestion run."""

    run_timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    connection.execute(
        """
        INSERT INTO scrape_runs (
            source,
            run_timestamp,
            records_collected,
            records_new,
            records_failed
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            source,
            run_timestamp,
            records_collected,
            records_new,
            records_failed,
        ),
    )


def main():

    print("\nJobPulse - Incremental Database Load")
    print("====================================")

    # ---------------------------------------------------------
    # 1. Read processed data
    # ---------------------------------------------------------

    if not JOBS_FILE.exists():
        raise FileNotFoundError(
            f"Jobs file not found: {JOBS_FILE}"
        )

    if not SKILLS_FILE.exists():
        raise FileNotFoundError(
            f"Skills file not found: {SKILLS_FILE}"
        )

    jobs = pd.read_csv(JOBS_FILE)

    skills_df = pd.read_csv(SKILLS_FILE)

    print(f"Clean jobs found: {len(jobs)}")
    print(
        f"Skill relationships found: "
        f"{len(skills_df)}"
    )

    # ---------------------------------------------------------
    # 2. Validate
    # ---------------------------------------------------------

    validate_inputs(
        jobs,
        skills_df,
    )

    connection = get_connection()

    try:

        # -----------------------------------------------------
        # 3. Initialize schema
        # -----------------------------------------------------

        initialize_database(
            connection
        )

        # -----------------------------------------------------
        # 4. Load current postings
        # -----------------------------------------------------

        (
            postings_processed,
            postings_new,
        ) = load_postings(
            connection,
            jobs,
        )

        # -----------------------------------------------------
        # 5. Load skills
        # -----------------------------------------------------

        skills_processed = load_skills(
            connection,
            skills_df,
        )

        # -----------------------------------------------------
        # 6. Load skill relationships
        # -----------------------------------------------------

        relationships_loaded = (
            load_skill_mentions(
                connection,
                skills_df,
            )
        )

        # -----------------------------------------------------
        # 7. Record ingestion run
        # -----------------------------------------------------

        record_scrape_run(
            connection=connection,
            source="Adzuna",
            records_collected=postings_processed,
            records_new=postings_new,
            records_failed=0,
        )

        # -----------------------------------------------------
        # 8. Commit everything atomically
        # -----------------------------------------------------

        connection.commit()

        # -----------------------------------------------------
        # 9. Verification
        # -----------------------------------------------------

        final_jobs = connection.execute(
            "SELECT COUNT(*) FROM postings"
        ).fetchone()[0]

        final_skills = connection.execute(
            "SELECT COUNT(*) FROM skills"
        ).fetchone()[0]

        final_mentions = connection.execute(
            "SELECT COUNT(*) FROM skill_mentions"
        ).fetchone()[0]

        print("\nDatabase Load Complete")
        print("----------------------")

        print(
            f"Jobs processed: "
            f"{postings_processed}"
        )

        print(
            f"New jobs added: "
            f"{postings_new}"
        )

        print(
            f"Skills processed: "
            f"{skills_processed}"
        )

        print(
            f"Skill relationships: "
            f"{relationships_loaded}"
        )

        print("\nDatabase totals")
        print("----------------")

        print(
            f"Jobs: "
            f"{final_jobs}"
        )

        print(
            f"Skills: "
            f"{final_skills}"
        )

        print(
            f"Skill mentions: "
            f"{final_mentions}"
        )

        print("\nScrape run recorded successfully.")

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()
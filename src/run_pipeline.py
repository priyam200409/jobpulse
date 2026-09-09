"""
JobPulse - Production Data Pipeline

End-to-end pipeline:

1. Collect jobs from Adzuna
2. Clean real job data
3. Extract skills
4. Load current data into SQLite
5. Build geography dataset
6. Extract experience requirements
7. Create historical snapshot
8. Validate final outputs

Run from the project root:

    python -m src.run_pipeline
"""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_step(
    step_number: int,
    total_steps: int,
    name: str,
    module: str,
):
    """Run one pipeline module and stop on failure."""

    print()
    print("=" * 70)
    print(f"[{step_number}/{total_steps}] {name}")
    print("=" * 70)

    command = [
        sys.executable,
        "-m",
        module,
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline step failed: {name} "
            f"(module: {module}, "
            f"exit code: {result.returncode})"
        )


def validate_outputs():
    """Validate processed outputs and database consistency."""

    import pandas as pd

    from src.database.database import get_connection

    processed_dir = PROJECT_ROOT / "data" / "processed"

    jobs_file = processed_dir / "jobs_clean.csv"
    skills_file = processed_dir / "job_skills.csv"
    geography_file = processed_dir / "job_geography.csv"
    experience_file = processed_dir / "job_experience.csv"

    required_files = [
        jobs_file,
        skills_file,
        geography_file,
        experience_file,
    ]

    # ---------------------------------------------------------
    # Check required files
    # ---------------------------------------------------------

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required pipeline output is missing: {file_path}"
            )

    # ---------------------------------------------------------
    # Read processed datasets
    # ---------------------------------------------------------

    jobs = pd.read_csv(jobs_file)
    skills = pd.read_csv(skills_file)
    geography = pd.read_csv(geography_file)
    experience = pd.read_csv(experience_file)

    # ---------------------------------------------------------
    # Validate clean jobs
    # ---------------------------------------------------------

    required_job_columns = {
        "posting_id",
    }

    missing_job_columns = (
        required_job_columns - set(jobs.columns)
    )

    if missing_job_columns:
        raise ValueError(
            "jobs_clean.csv is missing required columns: "
            f"{sorted(missing_job_columns)}"
        )

    if jobs.empty:
        raise ValueError(
            "jobs_clean.csv is empty."
        )

    if jobs["posting_id"].isna().any():
        raise ValueError(
            "jobs_clean.csv contains missing posting IDs."
        )

    if jobs["posting_id"].duplicated().any():
        raise ValueError(
            "jobs_clean.csv contains duplicate posting IDs."
        )

    # ---------------------------------------------------------
    # Validate skill relationships
    # ---------------------------------------------------------

    required_skill_columns = {
        "posting_id",
        "skill",
    }

    missing_skill_columns = (
        required_skill_columns - set(skills.columns)
    )

    if missing_skill_columns:
        raise ValueError(
            "job_skills.csv is missing required columns: "
            f"{sorted(missing_skill_columns)}"
        )

    if not skills.empty and skills["posting_id"].isna().any():
        raise ValueError(
            "job_skills.csv contains missing posting IDs."
        )

    invalid_skill_postings = (
        ~skills["posting_id"].isin(
            jobs["posting_id"]
        )
    ).sum()

    if invalid_skill_postings:
        raise ValueError(
            "job_skills.csv contains posting IDs "
            "not present in jobs_clean.csv: "
            f"{invalid_skill_postings}"
        )

    # ---------------------------------------------------------
    # Validate experience dataset
    #
    # Experience is generated directly from jobs_clean.csv.
    # Therefore it must contain exactly one row per currently
    # processed job.
    # ---------------------------------------------------------

    required_experience_columns = {
        "posting_id",
    }

    missing_experience_columns = (
        required_experience_columns
        - set(experience.columns)
    )

    if missing_experience_columns:
        raise ValueError(
            "job_experience.csv is missing required columns: "
            f"{sorted(missing_experience_columns)}"
        )

    if len(experience) != len(jobs):
        raise ValueError(
            "Experience dataset row count does not match "
            "jobs_clean.csv. "
            f"Experience: {len(experience)}, "
            f"Jobs: {len(jobs)}"
        )

    if experience["posting_id"].isna().any():
        raise ValueError(
            "job_experience.csv contains missing posting IDs."
        )

    if experience["posting_id"].duplicated().any():
        raise ValueError(
            "job_experience.csv contains duplicate posting IDs."
        )

    if not experience["posting_id"].isin(
        jobs["posting_id"]
    ).all():
        raise ValueError(
            "job_experience.csv contains posting IDs "
            "not present in jobs_clean.csv."
        )

    # ---------------------------------------------------------
    # Validate geography dataset
    #
    # Geography is generated from ALL current postings in
    # SQLite. Because the database is incremental, it can
    # contain more postings than the latest Adzuna collection.
    #
    # Therefore geography must be validated against the
    # database posting count, NOT jobs_clean.csv.
    # ---------------------------------------------------------

    required_geography_columns = {
        "posting_id",
    }

    missing_geography_columns = (
        required_geography_columns
        - set(geography.columns)
    )

    if missing_geography_columns:
        raise ValueError(
            "job_geography.csv is missing required columns: "
            f"{sorted(missing_geography_columns)}"
        )

    if geography["posting_id"].isna().any():
        raise ValueError(
            "job_geography.csv contains missing posting IDs."
        )

    if geography["posting_id"].duplicated().any():
        raise ValueError(
            "job_geography.csv contains duplicate posting IDs."
        )

    # ---------------------------------------------------------
    # Validate database
    # ---------------------------------------------------------

    connection = get_connection()

    try:
        database_job_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM postings
            """
        ).fetchone()[0]

        database_skill_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM skills
            """
        ).fetchone()[0]

        database_skill_mentions = connection.execute(
            """
            SELECT COUNT(*)
            FROM skill_mentions
            """
        ).fetchone()[0]

        snapshot_count = connection.execute(
            """
            SELECT COUNT(DISTINCT snapshot_date)
            FROM job_snapshots
            """
        ).fetchone()[0]

    finally:
        connection.close()

    # ---------------------------------------------------------
    # Geography must match current database postings
    # ---------------------------------------------------------

    if len(geography) != database_job_count:
        raise ValueError(
            "Geography dataset row count does not match "
            "the current database posting count. "
            f"Geography: {len(geography)}, "
            f"Database: {database_job_count}"
        )

    # ---------------------------------------------------------
    # Validate geography posting IDs against database
    # ---------------------------------------------------------

    connection = get_connection()

    try:
        database_posting_ids = {
            row[0]
            for row in connection.execute(
                """
                SELECT posting_id
                FROM postings
                """
            ).fetchall()
        }

    finally:
        connection.close()

    invalid_geography_postings = (
        ~geography["posting_id"].isin(
            database_posting_ids
        )
    ).sum()

    if invalid_geography_postings:
        raise ValueError(
            "job_geography.csv contains posting IDs "
            "not present in the current database: "
            f"{invalid_geography_postings}"
        )

    # ---------------------------------------------------------
    # Return validation summary
    # ---------------------------------------------------------

    return {
        "jobs_collected": len(jobs),
        "database_jobs": database_job_count,
        "skills": database_skill_count,
        "skill_relationships": len(skills),
        "database_skill_mentions": database_skill_mentions,
        "geography_rows": len(geography),
        "experience_rows": len(experience),
        "historical_snapshots": snapshot_count,
    }


def main():
    """Run the complete JobPulse production pipeline."""

    total_steps = 7

    print()
    print("JobPulse - Production Pipeline")
    print("==============================")
    print(f"Project root: {PROJECT_ROOT}")

    # ---------------------------------------------------------
    # 1. Collect
    # ---------------------------------------------------------

    run_step(
        1,
        total_steps,
        "Collecting real Adzuna job postings",
        "src.ingestion.adzuna_collector",
    )

    # ---------------------------------------------------------
    # 2. Clean
    # ---------------------------------------------------------

    run_step(
        2,
        total_steps,
        "Cleaning real job data",
        "src.ingestion.clean_real_jobs",
    )

    # ---------------------------------------------------------
    # 3. Extract skills
    # ---------------------------------------------------------

    run_step(
        3,
        total_steps,
        "Extracting job skills",
        "src.extraction.extract_job_skills",
    )

    # ---------------------------------------------------------
    # 4. Load database
    # ---------------------------------------------------------

    run_step(
        4,
        total_steps,
        "Loading current data into SQLite",
        "src.database.load_real_data",
    )

    # ---------------------------------------------------------
    # 5. Geography
    # ---------------------------------------------------------

    run_step(
        5,
        total_steps,
        "Normalizing job geography",
        "src.analytics.geography",
    )

    # ---------------------------------------------------------
    # 6. Experience
    # ---------------------------------------------------------

    run_step(
        6,
        total_steps,
        "Extracting experience requirements",
        "src.analytics.experience",
    )

    # ---------------------------------------------------------
    # 7. Historical snapshot
    # ---------------------------------------------------------

    run_step(
        7,
        total_steps,
        "Creating historical snapshot",
        "src.analytics.snapshots",
    )

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("PIPELINE VALIDATION")
    print("=" * 70)

    summary = validate_outputs()

    print(
        f"Jobs collected:          "
        f"{summary['jobs_collected']}"
    )

    print(
        f"Database jobs:           "
        f"{summary['database_jobs']}"
    )

    print(
        f"Skills:                  "
        f"{summary['skills']}"
    )

    print(
        f"Skill relationships:     "
        f"{summary['skill_relationships']}"
    )

    print(
        f"Database skill mentions: "
        f"{summary['database_skill_mentions']}"
    )

    print(
        f"Geography rows:          "
        f"{summary['geography_rows']}"
    )

    print(
        f"Experience rows:         "
        f"{summary['experience_rows']}"
    )

    print(
        f"Historical snapshots:    "
        f"{summary['historical_snapshots']}"
    )

    print()
    print("=" * 70)
    print("JOBPULSE PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
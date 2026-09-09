from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "adzuna_data_analyst_jobs.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "jobs_clean.csv"


def clean_text(value):
    """Remove HTML and normalize whitespace."""
    if pd.isna(value):
        return ""

    value = str(value)

    # Remove HTML
    value = BeautifulSoup(value, "html.parser").get_text(" ")

    # Normalize whitespace
    value = re.sub(r"\s+", " ", value).strip()

    return value


def normalize_company(value):
    """Clean company names."""
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in {"nan", "none", "null", ""}:
        return ""

    return value


def normalize_location(value):
    """Normalize location labels."""
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if not value or value.lower() in {"nan", "none", "null"}:
        return "Unknown"

    return value


def clean_jobs():
    print("\nJobPulse - Real Data Cleaning")
    print("==============================")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    initial_count = len(df)

    print(f"Raw records: {initial_count}")

    # ---------------------------------------------------------
    # 1. Standardize column names
    # ---------------------------------------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # ---------------------------------------------------------
    # 2. Remove completely empty rows
    # ---------------------------------------------------------
    df = df.dropna(how="all")

    # ---------------------------------------------------------
    # 3. Remove duplicate posting IDs
    # ---------------------------------------------------------
    df = df.drop_duplicates(
        subset=["posting_id"],
        keep="first"
    )

    # ---------------------------------------------------------
    # 4. Remove duplicate URLs
    # ---------------------------------------------------------
    df = df.drop_duplicates(
        subset=["job_url"],
        keep="first"
    )

    # ---------------------------------------------------------
    # 5. Clean text fields
    # ---------------------------------------------------------
    text_columns = [
        "job_title",
        "company",
        "location",
        "experience",
        "description",
        "requirements",
        "source",
        "job_url",
        "employment_type",
        "category",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].apply(clean_text)

    # ---------------------------------------------------------
    # 6. Normalize company and location
    # ---------------------------------------------------------
    df["company"] = df["company"].apply(normalize_company)
    df["location"] = df["location"].apply(normalize_location)

    # ---------------------------------------------------------
    # 7. Parse dates
    # ---------------------------------------------------------
    df["posted_date"] = pd.to_datetime(
        df["posted_date"],
        errors="coerce",
        utc=True
    )

    df["scraped_at"] = pd.to_datetime(
        df["scraped_at"],
        errors="coerce",
        utc=True
    )

    # ---------------------------------------------------------
    # 8. Numeric salary fields
    # ---------------------------------------------------------
    for column in ["salary_min", "salary_max"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 9. Description quality
    # ---------------------------------------------------------
    df["description_length"] = (
        df["description"]
        .fillna("")
        .str.len()
    )

    df["description_available"] = (
        df["description_length"] > 0
    )

    # ---------------------------------------------------------
    # 10. Salary availability
    # ---------------------------------------------------------
    df["salary_available"] = (
        df["salary_min"].notna()
        | df["salary_max"].notna()
    )

    # ---------------------------------------------------------
    # 11. Keep only records with essential fields
    # ---------------------------------------------------------
    df = df[
        df["posting_id"].notna()
        & df["job_title"].notna()
        & df["job_url"].notna()
    ]

    # ---------------------------------------------------------
    # 12. Sort newest jobs first
    # ---------------------------------------------------------
    df = df.sort_values(
        by="posted_date",
        ascending=False,
        na_position="last"
    )

    # ---------------------------------------------------------
    # 13. Save
    # ---------------------------------------------------------
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------
    final_count = len(df)

    print("\nCleaning completed.")
    print("-------------------")
    print(f"Raw records:          {initial_count}")
    print(f"Clean records:        {final_count}")
    print(f"Removed records:      {initial_count - final_count}")
    print(f"Companies:            {df['company'].nunique()}")
    print(f"Locations:            {df['location'].nunique()}")
    print(
        f"Salary available:     "
        f"{df['salary_available'].sum()}"
    )
    print(
        f"Descriptions present: "
        f"{df['description_available'].sum()}"
    )
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_jobs()
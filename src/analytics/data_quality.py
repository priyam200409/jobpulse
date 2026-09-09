from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "jobs_clean.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "data_quality_report.csv"


def calculate_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate measurable data-quality metrics."""

    total_records = len(df)

    if total_records == 0:
        raise ValueError("Dataset contains no records.")

    metrics = []

    def add_metric(metric, value, status="INFO"):
        metrics.append({
            "metric": metric,
            "value": value,
            "status": status,
        })

    # ---------------------------------------------------------
    # Completeness
    # ---------------------------------------------------------

    add_metric(
        "Total records",
        total_records,
        "PASS"
    )

    add_metric(
        "Unique posting IDs",
        df["posting_id"].nunique(),
        "PASS" if df["posting_id"].nunique() == total_records else "CHECK"
    )

    duplicate_ids = df["posting_id"].duplicated().sum()

    add_metric(
        "Duplicate posting IDs",
        duplicate_ids,
        "PASS" if duplicate_ids == 0 else "CHECK"
    )

    # ---------------------------------------------------------
    # Missing values
    # ---------------------------------------------------------

    important_columns = [
        "posting_id",
        "job_title",
        "company",
        "location",
        "description",
        "posted_date",
        "source",
        "job_url",
    ]

    for column in important_columns:
        missing_count = df[column].isna().sum()
        missing_percentage = (
            missing_count / total_records * 100
        )

        status = "PASS"

        if missing_percentage > 5:
            status = "CHECK"

        if missing_percentage > 20:
            status = "WARNING"

        add_metric(
            f"Missing {column} (%)",
            round(missing_percentage, 2),
            status
        )

    # ---------------------------------------------------------
    # Empty text values
    # ---------------------------------------------------------

    for column in [
        "job_title",
        "company",
        "location",
        "description",
        "job_url",
    ]:
        empty_count = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        empty_percentage = (
            empty_count / total_records * 100
        )

        status = "PASS"

        if empty_percentage > 5:
            status = "CHECK"

        if empty_percentage > 20:
            status = "WARNING"

        add_metric(
            f"Empty {column} (%)",
            round(empty_percentage, 2),
            status
        )

    # ---------------------------------------------------------
    # Description quality
    # ---------------------------------------------------------

    if "description_length" in df.columns:

        short_descriptions = (
            df["description_length"] < 100
        ).sum()

        short_percentage = (
            short_descriptions / total_records * 100
        )

        add_metric(
            "Short descriptions (<100 chars) (%)",
            round(short_percentage, 2),
            "PASS" if short_percentage < 20 else "CHECK"
        )

    # ---------------------------------------------------------
    # Salary coverage
    # ---------------------------------------------------------

    if "salary_available" in df.columns:

        salary_count = df["salary_available"].sum()

        salary_percentage = (
            salary_count / total_records * 100
        )

        add_metric(
            "Salary available (%)",
            round(salary_percentage, 2),
            "INFO"
        )

    # ---------------------------------------------------------
    # Date quality
    # ---------------------------------------------------------

    if "posted_date" in df.columns:

        invalid_dates = df["posted_date"].isna().sum()

        add_metric(
            "Invalid posted dates",
            invalid_dates,
            "PASS" if invalid_dates == 0 else "CHECK"
        )

        today = pd.Timestamp.now(tz="UTC")

        future_dates = (
            df["posted_date"] > today
        ).sum()

        add_metric(
            "Future posted dates",
            future_dates,
            "PASS" if future_dates == 0 else "CHECK"
        )

        # Jobs older than 90 days
        stale_cutoff = today - pd.Timedelta(days=90)

        stale_jobs = (
            df["posted_date"] < stale_cutoff
        ).sum()

        stale_percentage = (
            stale_jobs / total_records * 100
        )

        add_metric(
            "Stale postings (>90 days) (%)",
            round(stale_percentage, 2),
            "INFO"
        )

    # ---------------------------------------------------------
    # URL quality
    # ---------------------------------------------------------

    if "job_url" in df.columns:

        valid_urls = (
            df["job_url"]
            .fillna("")
            .astype(str)
            .str.startswith(("http://", "https://"))
        )

        invalid_url_count = (~valid_urls).sum()

        add_metric(
            "Invalid job URLs",
            invalid_url_count,
            "PASS" if invalid_url_count == 0 else "CHECK"
        )

    # ---------------------------------------------------------
    # Company coverage
    # ---------------------------------------------------------

    if "company" in df.columns:

        company_available = (
            df["company"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
        )

        company_percentage = (
            company_available.sum()
            / total_records
            * 100
        )

        add_metric(
            "Company information available (%)",
            round(company_percentage, 2),
            "PASS" if company_percentage >= 95 else "CHECK"
        )

    # ---------------------------------------------------------
    # Location coverage
    # ---------------------------------------------------------

    if "location" in df.columns:

        location_available = (
            df["location"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
        )

        location_percentage = (
            location_available.sum()
            / total_records
            * 100
        )

        add_metric(
            "Location information available (%)",
            round(location_percentage, 2),
            "PASS" if location_percentage >= 95 else "CHECK"
        )

    return pd.DataFrame(metrics)


def main():

    print("\nJobPulse - Data Quality Report")
    print("==============================")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Clean dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    df["posted_date"] = pd.to_datetime(
        df["posted_date"],
        errors="coerce",
        utc=True
    )

    report = calculate_data_quality(df)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nData Quality Metrics")
    print("--------------------")

    print(
        report.to_string(index=False)
    )

    print(
        f"\nReport saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
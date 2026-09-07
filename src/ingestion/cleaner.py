import pandas as pd


def clean_jobs(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Load raw job data, clean basic fields,
    remove duplicates, and save the processed dataset.
    """

    df = pd.read_csv(input_path)

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove duplicate posting IDs
    df = df.drop_duplicates(subset=["posting_id"])

    # Clean text columns
    text_columns = [
        "job_title",
        "company",
        "location",
        "experience",
        "description",
        "requirements",
        "source",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str).str.strip()

    # Convert dates
    df["posted_date"] = pd.to_datetime(
        df["posted_date"],
        errors="coerce"
    )

    df["scraped_at"] = pd.to_datetime(
        df["scraped_at"],
        errors="coerce"
    )

    # Save processed data
    df.to_csv(output_path, index=False)

    return df
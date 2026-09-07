from ingestion.cleaner import clean_jobs


INPUT_FILE = "data/sample/sample_jobs.csv"
OUTPUT_FILE = "data/processed/jobs_clean.csv"


def main():
    df = clean_jobs(INPUT_FILE, OUTPUT_FILE)

    print("\nJobPulse cleaning pipeline")
    print("---------------------------")
    print(f"Total jobs: {len(df)}")
    print(f"Unique companies: {df['company'].nunique()}")
    print(f"Unique cities: {df['location'].nunique()}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
from cleaner import clean_jobs


input_file = "data/sample/sample_jobs.csv"
output_file = "data/processed/jobs_clean.csv"

df = clean_jobs(input_file, output_file)

print("\nCleaning completed!")
print(f"Total jobs: {len(df)}")
print(f"Unique companies: {df['company'].nunique()}")
print(f"Unique cities: {df['location'].nunique()}")
print("\nJobs:")
print(df[["posting_id", "job_title", "company", "location"]])
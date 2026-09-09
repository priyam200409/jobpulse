"""
JobPulse - Adzuna Job Collector

Collects publicly available India Data Analyst job postings
through the official Adzuna API.

Credentials are loaded from environment variables:

ADZUNA_APP_ID
ADZUNA_APP_KEY

The collector stores the raw API response as CSV so that
the downstream cleaning/extraction pipeline can remain
separate from data collection.
"""

import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_FILE = RAW_DIR / "adzuna_data_analyst_jobs.csv"


# ============================================================
# ADZUNA CONFIGURATION
# ============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)

APP_ID = os.getenv(
    "ADZUNA_APP_ID"
)

APP_KEY = os.getenv(
    "ADZUNA_APP_KEY"
)

BASE_URL = (
    "https://api.adzuna.com/v1/api"
)

COUNTRY_CODE = "in"

SEARCH_TERM = "data analyst"

RESULTS_PER_PAGE = 20

MAX_JOBS = 500

REQUEST_DELAY_SECONDS = 0.5


# ============================================================
# VALIDATION
# ============================================================

def validate_credentials():

    if not APP_ID:

        raise ValueError(
            "ADZUNA_APP_ID is missing. "
            "Add it to the .env file."
        )

    if not APP_KEY:

        raise ValueError(
            "ADZUNA_APP_KEY is missing. "
            "Add it to the .env file."
        )


# ============================================================
# API REQUEST
# ============================================================

# ============================================================
# API REQUEST
# ============================================================

MAX_RETRIES = 4

RETRY_STATUS_CODES = {
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}


def fetch_page(page: int) -> dict:

    url = (
        f"{BASE_URL}/jobs/"
        f"{COUNTRY_CODE}/search/"
        f"{page}"
    )

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": SEARCH_TERM,
        "content-type": "application/json",
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=30,
            )

            if response.status_code in RETRY_STATUS_CODES:

                if attempt == MAX_RETRIES:
                    response.raise_for_status()

                wait_seconds = 2 ** attempt

                print(
                    f"Adzuna returned HTTP "
                    f"{response.status_code}. "
                    f"Retrying in "
                    f"{wait_seconds} seconds "
                    f"(attempt "
                    f"{attempt}/{MAX_RETRIES})..."
                )

                time.sleep(wait_seconds)

                continue

            response.raise_for_status()

            return response.json()

        except requests.RequestException:

            if attempt == MAX_RETRIES:
                raise

            wait_seconds = 2 ** attempt

            print(
                f"Request failed. "
                f"Retrying in "
                f"{wait_seconds} seconds "
                f"(attempt "
                f"{attempt}/{MAX_RETRIES})..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Unable to fetch Adzuna page {page} "
        f"after {MAX_RETRIES} attempts."
    )
# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(job: dict) -> dict:

    location = job.get(
        "location",
        {}
    )

    company = job.get(
        "company",
        {}
    )

    category = job.get(
        "category",
        {}
    )

    return {
        "posting_id": (
            f"adzuna_"
            f"{job.get('id', '')}"
        ),

        "job_title": (
            job.get("title")
            or ""
        ).strip(),

        "company": (
            company.get("display_name")
            if isinstance(company, dict)
            else ""
        ) or "",

        "location": (
            location.get("display_name")
            if isinstance(location, dict)
            else ""
        ) or "",

        "experience": "",

        "description": (
            job.get("description")
            or ""
        ).strip(),

        "requirements": "",

        "posted_date": (
            job.get("created")
            or ""
        ),

        "source": "Adzuna",

        "job_url": (
            job.get("redirect_url")
            or ""
        ),

        "scraped_at": (
            pd.Timestamp.now("UTC")
            .isoformat()
        ),

        "salary_min": job.get(
            "salary_min"
        ),

        "salary_max": job.get(
            "salary_max"
        ),

        "employment_type": (
            job.get("contract_type")
            or job.get("contract_time")
            or ""
        ),

        "category": (
            category.get("label")
            if isinstance(category, dict)
            else ""
        ) or "",
    }


# ============================================================
# COLLECT JOBS
# ============================================================

def collect_jobs(
    max_jobs: int = MAX_JOBS,
) -> pd.DataFrame:

    validate_credentials()

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_jobs = []

    page = 1

    print()
    print(
        "JobPulse - Adzuna Collector"
    )
    print(
        "============================"
    )
    print(
        f"Search: {SEARCH_TERM}"
    )
    print(
        f"Target jobs: {max_jobs}"
    )
    print()

    while len(all_jobs) < max_jobs:

        print(
            f"Fetching page {page}..."
        )

        try:

            response = fetch_page(
                page
            )

        except requests.HTTPError as error:

            print(
                f"API request failed: {error}"
            )

            break

        except requests.RequestException as error:

            print(
                f"Network error: {error}"
            )

            break

        results = response.get(
            "results",
            []
        )

        if not results:

            print(
                "No more jobs returned by API."
            )

            break

        for job in results:

            all_jobs.append(
                normalize_job(job)
            )

            if len(all_jobs) >= max_jobs:

                break

        print(
            f"Jobs collected: "
            f"{len(all_jobs)}"
        )

        page += 1

        time.sleep(
            REQUEST_DELAY_SECONDS
        )

    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        all_jobs
    )

    if df.empty:

        raise RuntimeError(
            "No jobs were collected."
        )

    # --------------------------------------------------------
    # DEDUPLICATION
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["posting_id"]
    )

    duplicates_removed = (
        before - len(df)
    )

    # --------------------------------------------------------
    # SAVE RAW DATA
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print(
        "Collection completed."
    )
    print(
        "---------------------"
    )

    print(
        f"Jobs collected: "
        f"{len(df)}"
    )

    print(
        f"Duplicates removed: "
        f"{duplicates_removed}"
    )

    print(
        f"Companies: "
        f"{df['company'].nunique()}"
    )

    print(
        f"Locations: "
        f"{df['location'].nunique()}"
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE}"
    )

    print()

    return df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    collect_jobs()
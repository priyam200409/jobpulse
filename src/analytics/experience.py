from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "job_experience.csv"
)


# =========================================================
# EXPERIENCE PATTERNS
# =========================================================

RANGE_PATTERNS = [
    r"\b(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
    r"\b(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
]

PLUS_PATTERNS = [
    r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)\b",
    r"\bminimum\s+of\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
    r"\bat\s+least\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
    r"\bminimum\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
]

SINGLE_PATTERNS = [
    r"\b(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\s+of\s+experience\b",
    r"\bexperience\s+of\s+(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\b",
    r"\b(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\s+experience\b",
    r"\bexperience\s*:\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
]

FRESHER_PATTERNS = [
    r"\bfresher\b",
    r"\bfreshers\b",
    r"\bentry[-\s]?level\b",
    r"\bno\s+experience\b",
    r"\bwithout\s+experience\b",
    r"\b0\s+(?:years?|yrs?)\s+(?:of\s+)?experience\b",
]


# =========================================================
# HELPERS
# =========================================================

def format_number(value: float) -> str:
    """
    Format an experience number cleanly.

    Examples:
        2.0 -> "2"
        2.5 -> "2.5"
    """

    if float(value).is_integer():
        return str(int(value))

    return str(value)


def build_result(
    minimum,
    maximum,
    bucket,
    source,
):
    return {
        "experience_min": minimum,
        "experience_max": maximum,
        "experience_bucket": bucket,
        "experience_source": source,
    }


# =========================================================
# EXPERIENCE EXTRACTION
# =========================================================

def extract_experience(text: str) -> dict:
    """
    Extract explicit years-of-experience requirements.

    Priority:

        1. Explicit ranges
        2. Plus/minimum requirements
        3. Single experience requirement
        4. Explicit fresher/entry-level language
        5. Not specified

    This ordering prevents generic words such as
    "graduate" from incorrectly overriding a real
    experience requirement.
    """

    if pd.isna(text):
        text = ""

    text = str(text)

    # -----------------------------------------------------
    # 1. Explicit experience range
    # -----------------------------------------------------

    for pattern in RANGE_PATTERNS:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            minimum = float(match.group(1))
            maximum = float(match.group(2))

            if maximum < minimum:
                return build_result(
                    None,
                    None,
                    "Not specified",
                    "invalid_range",
                )

            bucket = (
                f"{format_number(minimum)}-"
                f"{format_number(maximum)} years"
            )

            return build_result(
                minimum,
                maximum,
                bucket,
                "explicit_range",
            )

    # -----------------------------------------------------
    # 2. Plus / minimum experience
    # -----------------------------------------------------

    for pattern in PLUS_PATTERNS:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            minimum = float(match.group(1))

            bucket = (
                f"{format_number(minimum)}+ years"
            )

            return build_result(
                minimum,
                None,
                bucket,
                "minimum_requirement",
            )

    # -----------------------------------------------------
    # 3. Single explicit experience requirement
    # -----------------------------------------------------

    for pattern in SINGLE_PATTERNS:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            years = float(match.group(1))

            bucket = (
                f"{format_number(years)} years"
            )

            return build_result(
                years,
                years,
                bucket,
                "explicit_single",
            )

    # -----------------------------------------------------
    # 4. Fresher / entry-level
    # -----------------------------------------------------

    for pattern in FRESHER_PATTERNS:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            return build_result(
                0,
                0,
                "Fresher",
                "explicit_fresher",
            )

    # -----------------------------------------------------
    # 5. Not specified
    # -----------------------------------------------------

    return build_result(
        None,
        None,
        "Not specified",
        "not_found",
    )


# =========================================================
# BUILD EXPERIENCE DATASET
# =========================================================

def build_experience_dataset():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    jobs = pd.read_csv(INPUT_FILE)

    results = []

    for _, job in jobs.iterrows():

        text = (
            f"{job.get('job_title', '')} "
            f"{job.get('description', '')} "
            f"{job.get('requirements', '')}"
        )

        experience = extract_experience(text)

        results.append(
            {
                "posting_id": job["posting_id"],
                **experience,
            }
        )

    experience_df = pd.DataFrame(results)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    experience_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return experience_df


# =========================================================
# MAIN
# =========================================================

def main():

    df = build_experience_dataset()

    print("\nJobPulse - Experience Extraction")
    print("=================================")

    print(
        f"Jobs processed: {len(df)}"
    )

    print("\nExperience buckets:")
    print(
        df["experience_bucket"]
        .value_counts()
        .to_string()
    )

    detected = (
        df["experience_bucket"]
        != "Not specified"
    ).sum()

    coverage = (
        detected / len(df) * 100
        if len(df) > 0
        else 0
    )

    print("\nExperience detected:")

    print(
        f"{detected} / {len(df)} jobs"
    )

    print(
        f"Coverage: {coverage:.2f}%"
    )

    print("\nExtraction source:")

    print(
        df["experience_source"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nOutput: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
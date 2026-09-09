from pathlib import Path
import re
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobpulse.db"


CITY_ALIASES = {
    "Bangalore": [
        "bangalore",
        "bengaluru",
    ],
    "Hyderabad": [
        "hyderabad",
    ],
    "Mumbai": [
        "mumbai",
        "navi mumbai",
    ],
    "Pune": [
        "pune",
    ],
    "Chennai": [
        "chennai",
        "madras",
    ],
    "Delhi": [
        "delhi",
        "new delhi",
        "south delhi",
    ],
    "Noida": [
        "noida",
    ],
    "Gurgaon": [
        "gurgaon",
        "gurugram",
    ],
    "Ahmedabad": [
        "ahmedabad",
    ],
    "Kolkata": [
        "kolkata",
        "calcutta",
    ],
    "Coimbatore": [
        "coimbatore",
    ],
    "Vadodara": [
        "vadodara",
        "baroda",
    ],
    "Kochi": [
        "kochi",
        "cochin",
    ],
    "Lucknow": [
        "lucknow",
    ],
    "Jaipur": [
        "jaipur",
    ],
    "Indore": [
        "indore",
    ],
    "Chandigarh": [
        "chandigarh",
    ],
    "Mohali": [
        "mohali",
    ],
    "Mysore": [
        "mysore",
        "mysuru",
    ],
    "Mangalore": [
        "mangalore",
        "mangaluru",
    ],
    "Nagpur": [
        "nagpur",
    ],
    "Patna": [
        "patna",
    ],
    "Kanpur": [
        "kanpur",
    ],
    "Kota": [
        "kota",
    ],
    "Surat": [
        "surat",
    ],
    "Thane": [
        "thane",
    ],
    "Vijayawada": [
        "vijayawada",
    ],
    "Thiruvananthapuram": [
        "thiruvananthapuram",
        "trivandrum",
    ],
    "Ajmer": [
        "ajmer",
    ],
}


STATE_ALIASES = {
    "Karnataka": "karnataka",
    "Telangana": "telangana",
    "Maharashtra": "maharashtra",
    "Tamil Nadu": "tamil nadu",
    "Gujarat": "gujarat",
    "Haryana": "haryana",
    "Uttar Pradesh": "uttar pradesh",
    "West Bengal": "west bengal",
    "Kerala": "kerala",
    "Rajasthan": "rajasthan",
    "Punjab": "punjab",
    "Bihar": "bihar",
    "Delhi": "delhi",
}


def normalize_location(raw_location: str) -> dict:
    """
    Convert a raw location into:
    - city
    - state
    - scope
    """

    if pd.isna(raw_location):
        return {
            "city": "Unknown",
            "state": "Unknown",
            "scope": "Unknown",
        }

    location = str(raw_location).strip()

    if not location:
        return {
            "city": "Unknown",
            "state": "Unknown",
            "scope": "Unknown",
        }

    normalized = location.lower()

    # ---------------------------------------------------------
    # Nationwide / India-level locations
    # ---------------------------------------------------------

    if normalized in {
        "india",
        "india, india",
    }:
        return {
            "city": "Nationwide",
            "state": "All India",
            "scope": "Nationwide",
        }

    # ---------------------------------------------------------
    # City matching
    # ---------------------------------------------------------

    for city, aliases in CITY_ALIASES.items():

        for alias in aliases:

            if re.search(
                rf"\b{re.escape(alias)}\b",
                normalized,
            ):
                state = "Unknown"

                for state_name, state_alias in STATE_ALIASES.items():

                    if state_alias in normalized:
                        state = state_name
                        break

                # Delhi is both city and state
                if city == "Delhi":
                    state = "Delhi"

                return {
                    "city": city,
                    "state": state,
                    "scope": "City",
                }

    # ---------------------------------------------------------
    # State-only locations
    # ---------------------------------------------------------

    for state_name, state_alias in STATE_ALIASES.items():

        if normalized == state_alias or normalized == f"{state_alias}, india":

            return {
                "city": "Unknown",
                "state": state_name,
                "scope": "State",
            }

    # ---------------------------------------------------------
    # Unknown / unmatched
    # ---------------------------------------------------------

    return {
        "city": "Unknown",
        "state": "Unknown",
        "scope": "Unresolved",
    }


def build_geography_dataset():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        jobs = pd.read_sql_query(
            """
            SELECT
                posting_id,
                location
            FROM postings
            """,
            connection,
        )

    finally:
        connection.close()

    geography = jobs["location"].apply(
        normalize_location
    )

    geography_df = pd.DataFrame(
        geography.tolist()
    )

    result = pd.concat(
        [
            jobs.reset_index(drop=True),
            geography_df,
        ],
        axis=1,
    )

    output_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "job_geography.csv"
    )

    result.to_csv(
        output_file,
        index=False,
    )

    return result


if __name__ == "__main__":

    df = build_geography_dataset()

    print("\nJobPulse - Geographic Normalization")
    print("===================================")

    print(
        f"Jobs processed: {len(df)}"
    )

    print("\nScope:")
    print(
        df["scope"]
        .value_counts()
        .to_string()
    )

    print("\nTop cities:")

    city_counts = (
        df[df["scope"] == "City"]
        .groupby("city")
        .size()
        .sort_values(ascending=False)
        .head(15)
    )

    print(
        city_counts.to_string()
    )

    print(
        "\nOutput:"
        f" data/processed/job_geography.csv"
    )
from pathlib import Path

import pandas as pd

from src.extraction.skill_extractor import extract_skill_evidence


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
    / "job_skills.csv"
)


def build_skill_dataset(
    input_file: str,
    output_file: str,
) -> pd.DataFrame:

    jobs = pd.read_csv(input_file)

    skill_records = []

    for _, job in jobs.iterrows():

        description = str(
            job.get("description", "")
        )

        requirements = str(
            job.get("requirements", "")
        )

        text = (
            f"{description} "
            f"{requirements}"
        )

        evidence = extract_skill_evidence(text)

        for item in evidence:

            skill_records.append(
                {
                    "posting_id": job["posting_id"],
                    "skill": item["skill"],
                    "match_type": item["match_type"],
                    "confidence": item["confidence"],
                }
            )

    skill_df = pd.DataFrame(
        skill_records,
        columns=[
            "posting_id",
            "skill",
            "match_type",
            "confidence",
        ],
    )

    if not skill_df.empty:

        skill_df = skill_df.drop_duplicates(
            subset=[
                "posting_id",
                "skill",
            ]
        )

    skill_df.to_csv(
        output_file,
        index=False,
    )

    return skill_df


def main():

    print("\nJobPulse Skill Extraction")
    print("=========================")

    skill_df = build_skill_dataset(
        INPUT_FILE,
        OUTPUT_FILE,
    )

    jobs_with_skills = (
        skill_df["posting_id"]
        .nunique()
        if not skill_df.empty
        else 0
    )

    unique_skills = (
        skill_df["skill"]
        .nunique()
        if not skill_df.empty
        else 0
    )

    print(
        f"Jobs with detected skills: "
        f"{jobs_with_skills}"
    )

    print(
        f"Skill relationships: "
        f"{len(skill_df)}"
    )

    print(
        f"Unique skills: "
        f"{unique_skills}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    if not skill_df.empty:

        print("\nSkill frequency:")
        print(
            skill_df["skill"]
            .value_counts()
            .to_string()
        )

        print("\nMatch type:")
        print(
            skill_df["match_type"]
            .value_counts()
            .to_string()
        )


if __name__ == "__main__":
    main()
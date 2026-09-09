from pathlib import Path

import pandas as pd

from src.extraction.skill_extractor import extract_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_clean.csv"
)


def load_jobs():
    return pd.read_csv(INPUT_FILE)


def benchmark_extractor(df):
    detected_jobs = 0
    total_mentions = 0
    skill_counts = {}

    for _, job in df.iterrows():

        description = str(job.get("description", ""))
        requirements = str(job.get("requirements", ""))

        text = f"{description} {requirements}"

        skills = extract_skills(text)

        if skills:
            detected_jobs += 1

        total_mentions += len(skills)

        for skill in skills:
            skill_counts[skill] = (
                skill_counts.get(skill, 0) + 1
            )

    coverage = (
        detected_jobs / len(df) * 100
        if len(df) > 0
        else 0
    )

    return {
        "total_jobs": len(df),
        "jobs_with_detected_skills": detected_jobs,
        "coverage_percentage": round(coverage, 2),
        "total_skill_mentions": total_mentions,
        "unique_skills": len(skill_counts),
        "skill_counts": skill_counts,
    }


def main():

    print("\nJobPulse - Skill Extractor Benchmark")
    print("====================================")

    df = load_jobs()

    results = benchmark_extractor(df)

    print("\nExtraction Coverage")
    print("-------------------")

    print(
        f"Total jobs: "
        f"{results['total_jobs']}"
    )

    print(
        f"Jobs with detected skills: "
        f"{results['jobs_with_detected_skills']}"
    )

    print(
        f"Coverage: "
        f"{results['coverage_percentage']}%"
    )

    print(
        f"Total skill mentions: "
        f"{results['total_skill_mentions']}"
    )

    print(
        f"Unique skills detected: "
        f"{results['unique_skills']}"
    )

    print("\nSkill Frequency")
    print("---------------")

    skill_series = (
        pd.Series(results["skill_counts"])
        .sort_values(ascending=False)
    )

    print(skill_series.to_string())


if __name__ == "__main__":
    main()
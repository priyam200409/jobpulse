import pandas as pd

from src.analytics.job_market import (
    get_market_summary,
    get_skill_demand,
    get_skill_penetration,
    get_city_demand,
    get_experience_distribution,
    get_experience_summary,
    get_salary_summary,
    get_skill_cooccurrence,
    get_job_titles,
    get_data_quality,
    get_geography_scope,
    get_market_snapshot,
)


# =========================================================
# MARKET SUMMARY
# =========================================================

def test_market_summary_has_expected_structure():

    summary = get_market_summary()

    assert isinstance(summary, dict)

    assert "total_jobs" in summary
    assert "unique_companies" in summary
    assert "unique_locations" in summary
    assert "unique_job_titles" in summary


def test_market_summary_has_real_jobs():

    summary = get_market_summary()

    assert summary["total_jobs"] > 0


def test_market_summary_counts_are_valid():

    summary = get_market_summary()

    assert summary["unique_companies"] > 0
    assert summary["unique_locations"] > 0
    assert summary["unique_job_titles"] > 0

    assert (
        summary["unique_companies"]
        <= summary["total_jobs"]
    )

    assert (
        summary["unique_job_titles"]
        <= summary["total_jobs"]
    )


# =========================================================
# SKILL DEMAND
# =========================================================

def test_skill_demand_returns_dataframe():

    df = get_skill_demand()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_skill_demand_columns():

    df = get_skill_demand()

    expected_columns = {
        "skill",
        "category",
        "job_count",
    }

    assert expected_columns.issubset(
        df.columns
    )


def test_skill_demand_counts_are_positive():

    df = get_skill_demand()

    assert (
        df["job_count"] > 0
    ).all()


def test_skill_demand_is_sorted():

    df = get_skill_demand()

    counts = df["job_count"].tolist()

    assert counts == sorted(
        counts,
        reverse=True,
    )


# =========================================================
# SKILL PENETRATION
# =========================================================

def test_skill_penetration_returns_dataframe():

    df = get_skill_penetration()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_skill_penetration_columns():

    df = get_skill_penetration()

    expected_columns = {
        "skill",
        "category",
        "job_count",
        "market_penetration_pct",
    }

    assert expected_columns.issubset(
        df.columns
    )


def test_skill_penetration_is_valid():

    df = get_skill_penetration()

    assert (
        df["market_penetration_pct"] >= 0
    ).all()

    assert (
        df["market_penetration_pct"] <= 100
    ).all()


# =========================================================
# GEOGRAPHY
# =========================================================

def test_city_demand_returns_dataframe():

    df = get_city_demand()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_city_demand_columns():

    df = get_city_demand()

    assert "city" in df.columns
    assert "job_count" in df.columns


def test_city_demand_counts_are_positive():

    df = get_city_demand()

    assert (
        df["job_count"] > 0
    ).all()

# =========================================================
# GEOGRAPHY
# =========================================================

def test_city_demand_returns_dataframe():

    df = get_city_demand()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_city_demand_columns():

    df = get_city_demand()

    assert "city" in df.columns
    assert "job_count" in df.columns


def test_city_demand_counts_are_positive():

    df = get_city_demand()

    assert (
        df["job_count"] > 0
    ).all()


def test_city_demand_excludes_non_city_scopes():

    df = get_city_demand()

    assert (
        "Nationwide"
        not in df["city"].values
    )

    assert (
        "Unknown"
        not in df["city"].values
    )


def test_geography_scope_returns_expected_structure():

    df = get_geography_scope()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert not df.empty

    assert "scope" in df.columns
    assert "job_count" in df.columns


def test_geography_scope_counts_match_jobs():

    df = get_geography_scope()

    assert (
        df["job_count"].sum()
        == get_market_summary()["total_jobs"]
    )


# =========================================================
# EXPERIENCE
# =========================================================

def test_experience_distribution_returns_dataframe():

    df = get_experience_distribution()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_experience_distribution_columns():

    df = get_experience_distribution()

    assert "experience_bucket" in df.columns
    assert "job_count" in df.columns


def test_experience_summary_is_valid():

    summary = get_experience_summary()

    assert isinstance(summary, dict)

    assert summary["total_jobs"] > 0

    assert (
        0
        <= summary["experience_coverage_pct"]
        <= 100
    )

    assert (
        0
        <= summary["jobs_with_experience"]
        <= summary["total_jobs"]
    )

    assert (
        0
        <= summary["fresher_jobs"]
        <= summary["total_jobs"]
    )


# =========================================================
# SALARY
# =========================================================

def test_salary_summary_is_valid():

    summary = get_salary_summary()

    assert isinstance(summary, dict)

    assert summary["total_jobs"] > 0

    assert (
        0
        <= summary["salary_coverage_pct"]
        <= 100
    )

    assert (
        0
        <= summary["jobs_with_salary"]
        <= summary["total_jobs"]
    )


def test_salary_values_are_non_negative():

    summary = get_salary_summary()

    if summary["average_salary_min"] is not None:

        assert (
            summary["average_salary_min"]
            >= 0
        )

    if summary["average_salary_max"] is not None:

        assert (
            summary["average_salary_max"]
            >= 0
        )

    if summary["median_salary_min"] is not None:

        assert (
            summary["median_salary_min"]
            >= 0
        )

    if summary["median_salary_max"] is not None:

        assert (
            summary["median_salary_max"]
            >= 0
        )


# =========================================================
# SKILL CO-OCCURRENCE
# =========================================================

def test_skill_cooccurrence_returns_dataframe():

    df = get_skill_cooccurrence()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_skill_cooccurrence_columns():

    df = get_skill_cooccurrence()

    expected_columns = {
        "skill_1",
        "skill_2",
        "job_count",
    }

    assert expected_columns.issubset(
        df.columns
    )


def test_skill_cooccurrence_pairs_are_valid():

    df = get_skill_cooccurrence()

    assert (
        df["skill_1"]
        != df["skill_2"]
    ).all()

    assert (
        df["job_count"] > 0
    ).all()


# =========================================================
# JOB TITLES
# =========================================================

def test_job_titles_returns_dataframe():

    df = get_job_titles()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


def test_job_titles_columns():

    df = get_job_titles()

    assert "job_title" in df.columns
    assert "job_count" in df.columns


def test_job_title_counts_are_positive():

    df = get_job_titles()

    assert (
        df["job_count"] > 0
    ).all()


# =========================================================
# DATA QUALITY
# =========================================================

def test_data_quality_returns_dataframe():

    df = get_data_quality()

    assert isinstance(df, pd.DataFrame)

    assert not df.empty


# =========================================================
# COMPLETE MARKET SNAPSHOT
# =========================================================

def test_market_snapshot_contains_all_sections():

    snapshot = get_market_snapshot()

    expected_sections = {
        "market_summary",
        "skill_demand",
        "skill_penetration",
        "city_demand",
        "experience_distribution",
        "experience_summary",
        "salary_summary",
        "skill_cooccurrence",
        "job_titles",
        "data_quality",
    }

    assert expected_sections.issubset(
        snapshot.keys()
    )
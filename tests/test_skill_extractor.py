from src.extraction.skill_extractor import (
    extract_skills,
    extract_skill_evidence,
)


def test_basic_skill_extraction():
    text = """
    We require strong SQL, Excel and Power BI skills.
    """

    skills = extract_skills(text)

    assert "SQL" in skills
    assert "Excel" in skills
    assert "Power BI" in skills


def test_case_insensitive_extraction():
    text = """
    Experience with PYTHON, sql and tableau is required.
    """

    skills = extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "Tableau" in skills


def test_power_bi_variations():
    text = """
    Experience with PowerBI and Power BI dashboards.
    """

    skills = extract_skills(text)

    assert "Power BI" in skills
    assert skills.count("Power BI") == 1


def test_database_variations():
    text = """
    Experience with PostgreSQL, Postgres, MySQL,
    SQL Server and MongoDB.
    """

    skills = extract_skills(text)

    assert "PostgreSQL" in skills
    assert "MySQL" in skills
    assert "SQL Server" in skills
    assert "MongoDB" in skills


def test_machine_learning_variations():
    text = """
    Knowledge of Machine Learning, ML models and sklearn.
    """

    skills = extract_skills(text)

    assert "Machine Learning" in skills
    assert "Scikit-learn" in skills


def test_cloud_variations():
    text = """
    Experience with AWS, Microsoft Azure and
    Google Cloud Platform.
    """

    skills = extract_skills(text)

    assert "AWS" in skills
    assert "Azure" in skills
    assert "GCP" in skills


def test_no_false_r_match():
    text = """
    We are looking for a data analyst with strong
    Python and SQL skills.
    """

    skills = extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "R" not in skills


def test_empty_text():
    assert extract_skills("") == []


def test_duplicate_mentions_return_once():
    text = """
    SQL is required. Strong SQL experience is preferred.
    Advanced SQL knowledge is a plus.
    """

    skills = extract_skills(text)

    assert skills.count("SQL") == 1


def test_data_analyst_title_alone_is_not_data_analysis():
    text = """
    Job Title: Data Analyst
    """

    skills = extract_skills(text)

    assert "Data Analysis" not in skills


def test_explicit_data_analysis_requirement_is_detected():
    text = """
    The candidate will perform data analysis,
    identify trends and prepare analytical reports.
    """

    skills = extract_skills(text)

    assert "Data Analysis" in skills


def test_skill_evidence_returns_skill():
    text = """
    Strong SQL and Python experience required.
    """

    evidence = extract_skill_evidence(text)

    skills = [
        item["skill"]
        for item in evidence
    ]

    assert "SQL" in skills
    assert "Python" in skills


def test_skill_evidence_contains_confidence():
    text = """
    Strong SQL experience required.
    """

    evidence = extract_skill_evidence(text)

    sql = next(
        item
        for item in evidence
        if item["skill"] == "SQL"
    )

    assert sql["confidence"] == 1.0


def test_skill_evidence_contains_match_type():
    text = """
    Experience with PowerBI dashboards.
    """

    evidence = extract_skill_evidence(text)

    power_bi = next(
        item
        for item in evidence
        if item["skill"] == "Power BI"
    )

    assert power_bi["match_type"] == "alias"
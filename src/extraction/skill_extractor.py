import re

from src.extraction.skill_dictionary import SKILL_TAXONOMY


# =========================================================
# SKILL PATTERNS
# =========================================================
#
# Each skill contains one or more regex patterns.
#
# Pattern order matters:
#   - First pattern = canonical / explicit form
#   - Later patterns = aliases / variations
#
# The extractor remains deterministic and explainable.
# =========================================================

SKILL_PATTERNS = {

    # -----------------------------------------------------
    # ANALYTICS
    # -----------------------------------------------------

    "SQL": [
        r"\bsql\b",
    ],

    "Excel": [
        r"\bexcel\b",
        r"\bmicrosoft\s+excel\b",
        r"\bms\s+excel\b",
    ],

    "Google Sheets": [
        r"\bgoogle\s+sheets\b",
        r"\bgoogle\s+sheet\b",
        r"\bg[\s-]?sheets\b",
    ],

    "Statistics": [
        r"\bstatistics\b",
        r"\bstatistical\s+analysis\b",
        r"\bstatistical\s+methods?\b",
        r"\bstatistical\s+model(?:ing|ling)\b",
    ],

    "Data Analysis": [
        r"\bdata\s+analysis\b",
        r"\bdata[-\s]+analytics\b",
        r"\banalyze\s+data\b",
        r"\banalysing\s+data\b",
        r"\banalyzing\s+data\b",
    ],

    "Data Visualization": [
        r"\bdata\s+visuali[sz]ation\b",
        r"\bvisuali[sz]ation\b",
    ],

    "Business Analysis": [
        r"\bbusiness\s+analysis\b",
        r"\bbusiness\s+analyst\b",
    ],

    "KPI": [
        r"\bkpi\b",
        r"\bkpis\b",
        r"\bkey\s+performance\s+indicators?\b",
    ],

    # -----------------------------------------------------
    # BUSINESS INTELLIGENCE
    # -----------------------------------------------------

    "Power BI": [
        r"\bpower\s+bi\b",
        r"\bpowerbi\b",
    ],

    "Tableau": [
        r"\btableau\b",
    ],

    "Looker": [
        r"\blooker\b",
    ],

    "Qlik": [
        r"\bqlik\b",
    ],

    "DAX": [
        r"\bdax\b",
        r"\bdata\s+analysis\s+expressions?\b",
    ],

    "Power Query": [
        r"\bpower\s+query\b",
        r"\bpowerquery\b",
    ],

    "SSRS": [
        r"\bssrs\b",
        r"\bsql\s+server\s+reporting\s+services\b",
    ],

    # -----------------------------------------------------
    # PROGRAMMING
    # -----------------------------------------------------

    "Python": [
        r"\bpython\b",
    ],

    "R": [
        r"(?<![A-Za-z])R(?![A-Za-z])",
        r"\bR\s+programming\b",
        r"\bR\s+language\b",
        r"\bR\s+statistics\b",
    ],

    "Pandas": [
        r"\bpandas\b",
    ],

    "NumPy": [
        r"\bnumpy\b",
        r"\bnum\s*py\b",
    ],

    "Matplotlib": [
        r"\bmatplotlib\b",
    ],

    "Seaborn": [
        r"\bseaborn\b",
    ],

    # -----------------------------------------------------
    # DATABASES
    # -----------------------------------------------------

    "MySQL": [
        r"\bmysql\b",
        r"\bmy\s+sql\b",
    ],

    "PostgreSQL": [
        r"\bpostgresql\b",
        r"\bpostgres\b",
        r"\bpostgre\s+sql\b",
    ],

    "SQL Server": [
        r"\bsql\s+server\b",
        r"\bms\s+sql\s+server\b",
        r"\bmssql\b",
    ],

    "Oracle": [
        r"\boracle\s+(?:database|db)\b",
        r"\boracle\b",
    ],

    "MongoDB": [
        r"\bmongodb\b",
        r"\bmongo\s*db\b",
    ],

    # -----------------------------------------------------
    # CLOUD
    # -----------------------------------------------------

    "AWS": [
        r"\baws\b",
        r"\bamazon\s+web\s+services\b",
    ],

    "Azure": [
        r"\bazure\b",
        r"\bmicrosoft\s+azure\b",
    ],

    "GCP": [
        r"\bgcp\b",
        r"\bgoogle\s+cloud\s+platform\b",
        r"\bgoogle\s+cloud\b",
    ],

    "Snowflake": [
        r"\bsnowflake\b",
    ],

    "BigQuery": [
        r"\bbigquery\b",
        r"\bbig\s+query\b",
    ],

    # -----------------------------------------------------
    # DATA ENGINEERING
    # -----------------------------------------------------

    "ETL": [
        r"\betl\b",
        r"\bextract[\s-]*transform[\s-]*load\b",
    ],

    "Airflow": [
        r"\bairflow\b",
        r"\bapache\s+airflow\b",
    ],

    "Spark": [
        r"\bspark\b",
        r"\bapache\s+spark\b",
        r"\bpyspark\b",
    ],

    "Databricks": [
        r"\bdatabricks\b",
    ],

    "Data Warehousing": [
        r"\bdata\s+warehouse\b",
        r"\bdata\s+warehousing\b",
        r"\bdata\s+warehouse\s+concepts?\b",
    ],

    "SSIS": [
        r"\bssis\b",
        r"\bsql\s+server\s+integration\s+services\b",
    ],

    # -----------------------------------------------------
    # MACHINE LEARNING
    # -----------------------------------------------------

    "Machine Learning": [
        r"\bmachine\s+learning\b",
        r"\bmachine-learning\b",
        r"\bmachine\s+learning\s+models?\b",
        r"\bml\s+models?\b",
        r"\bml\s+algorithms?\b",
    ],

    "Scikit-learn": [
        r"\bscikit[-\s]?learn\b",
        r"\bsklearn\b",
    ],

    "NLP": [
        r"\bnlp\b",
        r"\bnatural\s+language\s+processing\b",
    ],

    "Deep Learning": [
        r"\bdeep\s+learning\b",
        r"\bdeep-learning\b",
    ],

    "TensorFlow": [
        r"\btensorflow\b",
        r"\btensor\s+flow\b",
    ],

    "PyTorch": [
        r"\bpytorch\b",
        r"\bpy\s*torch\b",
    ],
}


# =========================================================
# VALIDATE TAXONOMY
# =========================================================

def validate_skill_patterns():
    """
    Ensure every skill in the taxonomy has
    a corresponding extraction pattern.
    """

    missing = [
        skill
        for skill in SKILL_TAXONOMY
        if skill not in SKILL_PATTERNS
    ]

    if missing:
        raise ValueError(
            "Missing extraction patterns for: "
            + ", ".join(missing)
        )


# =========================================================
# EXTRACT SKILLS
# =========================================================

def extract_skills(text: str) -> list[str]:
    """
    Extract recognized skills from job text.

    Returns:
        List of canonical skill names.

    Each skill is returned at most once.

    Example:
        ["SQL", "Python", "Power BI"]
    """

    if not text:
        return []

    validate_skill_patterns()

    text = str(text)

    found_skills = []

    for skill in SKILL_TAXONOMY:

        patterns = SKILL_PATTERNS.get(skill, [])

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                found_skills.append(skill)
                break

    return found_skills


# =========================================================
# EXTRACT SKILL EVIDENCE
# =========================================================

def extract_skill_evidence(text: str) -> list[dict]:
    """
    Extract skills together with extraction evidence.

    Returns one record per detected skill.

    Example:
        [
            {
                "skill": "SQL",
                "match_type": "explicit",
                "confidence": 1.0
            },
            {
                "skill": "Power BI",
                "match_type": "alias",
                "confidence": 0.95
            }
        ]

    Match types:

        explicit
            Canonical skill expression.

        alias
            Alternative spelling or recognized variation.

    Confidence is deterministic and intended for
    auditability rather than statistical probability.
    """

    if not text:
        return []

    validate_skill_patterns()

    text = str(text)

    evidence = []

    for skill in SKILL_TAXONOMY:

        patterns = SKILL_PATTERNS.get(skill, [])

        for index, pattern in enumerate(patterns):

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            if index == 0:
                match_type = "explicit"
                confidence = 1.0
            else:
                match_type = "alias"
                confidence = 0.95

            evidence.append(
                {
                    "skill": skill,
                    "match_type": match_type,
                    "confidence": confidence,
                }
            )

            break

    return evidence
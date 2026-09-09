from src.analytics.experience import extract_experience


def test_experience_range():
    result = extract_experience(
        "Requires 2-4 years of experience."
    )

    assert result["experience_min"] == 2
    assert result["experience_max"] == 4
    assert result["experience_bucket"] == "2-4 years"


def test_experience_to_range():
    result = extract_experience(
        "Candidates should have 3 to 5 years experience."
    )

    assert result["experience_min"] == 3
    assert result["experience_max"] == 5


def test_plus_experience():
    result = extract_experience(
        "Minimum 3+ years of experience required."
    )

    assert result["experience_min"] == 3
    assert result["experience_max"] is None
    assert result["experience_bucket"] == "3+ years"


def test_at_least_experience():
    result = extract_experience(
        "At least 2 years of experience required."
    )

    assert result["experience_min"] == 2


def test_single_experience():
    result = extract_experience(
        "2 years of experience in data analytics."
    )

    assert result["experience_min"] == 2
    assert result["experience_max"] == 2


def test_fresher():
    result = extract_experience(
        "Freshers are welcome."
    )

    assert result["experience_bucket"] == "Fresher"
    assert result["experience_min"] == 0
    assert result["experience_max"] == 0


def test_entry_level():
    result = extract_experience(
        "This is an entry-level position."
    )

    assert result["experience_bucket"] == "Fresher"


def test_graduate_alone_is_not_fresher():
    result = extract_experience(
        "Graduate degree in computer science required."
    )

    assert result["experience_bucket"] == "Not specified"


def test_graduate_with_experience():
    result = extract_experience(
        "Graduate degree required with 3-5 years of experience."
    )

    assert result["experience_min"] == 3
    assert result["experience_max"] == 5
    assert result["experience_bucket"] == "3-5 years"


def test_no_experience():
    result = extract_experience(
        "No experience required."
    )

    assert result["experience_bucket"] == "Fresher"


def test_empty_text():
    result = extract_experience("")

    assert result["experience_bucket"] == "Not specified"


def test_invalid_reversed_range():
    result = extract_experience(
        "Requires 5-2 years of experience."
    )

    assert result["experience_bucket"] == "Not specified"
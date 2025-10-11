"""Contract tests for Module 002 output schema.

Validates that Candidate and SearchResult match the output schema.
These tests should FAIL until models are implemented (T012, T013).
"""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError
from datetime import datetime


@pytest.fixture
def output_schema():
    """Load output JSON schema."""
    schema_path = Path(__file__).parent.parent.parent / "specs" / "002-github-sourcer-module" / "contracts" / "output-schema.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def valid_candidate():
    """Valid Candidate object."""
    return {
        "github_username": "torvalds",
        "name": "Linus Torvalds",
        "bio": "Creator of Linux and Git",
        "location": "Portland, OR",
        "public_email": None,
        "top_repos": [
            {
                "name": "linux",
                "description": "Linux kernel source tree",
                "stars": 150000,
                "forks": 50000,
                "languages": ["C", "Assembly"],
                "url": "https://github.com/torvalds/linux"
            }
        ],
        "languages": ["Assembly", "C", "Shell"],  # Sorted alphabetically
        "contribution_count": 2500,
        "account_age_days": 5000,
        "followers": 200000,
        "profile_url": "https://github.com/torvalds",
        "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
        "fetched_at": "2025-10-06T10:30:00Z"
    }


@pytest.fixture
def valid_search_result():
    """Valid SearchResult metadata."""
    return {
        "total_candidates_found": 1247,
        "candidates_returned": 25,
        "search_timestamp": "2025-10-06T10:30:00Z",
        "rate_limit_remaining": 4875,
        "cache_hit": False,
        "execution_time_ms": 3420,
        "warnings": []
    }


def test_valid_candidate_passes_validation(output_schema, valid_candidate):
    """Valid Candidate should pass schema validation."""
    # Need to pass full schema for $ref resolution
    candidate_schema = output_schema["definitions"]["Candidate"]
    candidate_schema_with_defs = {**candidate_schema, "definitions": output_schema["definitions"]}
    validate(instance=valid_candidate, schema=candidate_schema_with_defs)


def test_valid_search_result_passes_validation(output_schema, valid_search_result):
    """Valid SearchResult should pass schema validation."""
    validate(instance=valid_search_result, schema=output_schema["definitions"]["SearchResult"])


def test_valid_output_passes_validation(output_schema, valid_candidate, valid_search_result):
    """Complete output with candidates + metadata should pass validation."""
    output = {
        "candidates": [valid_candidate],
        "metadata": valid_search_result
    }
    validate(instance=output, schema=output_schema)


def test_missing_github_username_fails(output_schema, valid_candidate):
    """Missing github_username should fail validation."""
    invalid = valid_candidate.copy()
    del invalid["github_username"]

    candidate_schema = output_schema["definitions"]["Candidate"]
    candidate_schema_with_defs = {**candidate_schema, "definitions": output_schema["definitions"]}

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=candidate_schema_with_defs)

    assert "'github_username' is a required property" in str(exc_info.value)


def test_candidates_returned_exceeds_25_fails(output_schema, valid_search_result):
    """candidates_returned > 25 should fail validation."""
    invalid = valid_search_result.copy()
    invalid["candidates_returned"] = 30

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=output_schema["definitions"]["SearchResult"])

    assert "30 is greater than the maximum of 25" in str(exc_info.value)


def test_negative_contribution_count_fails(output_schema, valid_candidate):
    """Negative contribution_count should fail validation."""
    invalid = valid_candidate.copy()
    invalid["contribution_count"] = -10

    candidate_schema = output_schema["definitions"]["Candidate"]
    candidate_schema_with_defs = {**candidate_schema, "definitions": output_schema["definitions"]}

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=candidate_schema_with_defs)

    assert "-10 is less than the minimum of 0" in str(exc_info.value)


def test_more_than_25_candidates_fails(output_schema, valid_candidate, valid_search_result):
    """More than 25 candidates in output should fail validation."""
    output = {
        "candidates": [valid_candidate] * 30,  # 30 candidates
        "metadata": valid_search_result
    }

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=output, schema=output_schema)

    # The error message will indicate that the array has too many items
    assert "too long" in str(exc_info.value).lower() or "30" in str(exc_info.value)


def test_more_than_5_repos_fails(output_schema, valid_candidate):
    """More than 5 repos in top_repos should fail validation."""
    invalid = valid_candidate.copy()
    invalid["top_repos"] = [
        {"name": f"repo{i}", "stars": 100, "forks": 10, "languages": ["Python"], "url": f"https://github.com/user/repo{i}"}
        for i in range(6)  # 6 repos
    ]

    candidate_schema = output_schema["definitions"]["Candidate"]
    candidate_schema_with_defs = {**candidate_schema, "definitions": output_schema["definitions"]}

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=candidate_schema_with_defs)

    # Error should mention "too long" or "maxItems"
    error_msg = str(exc_info.value).lower()
    assert "too long" in error_msg or "maxitems" in error_msg


def test_candidate_model_exists():
    """Test that Candidate model can be imported (will FAIL until T012 complete)."""
    try:
        from src.github_sourcer.models.candidate import Candidate
        assert Candidate is not None
    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_search_result_model_exists():
    """Test that SearchResult model can be imported (will FAIL until T013 complete)."""
    try:
        from src.github_sourcer.models.search_result import SearchResult
        assert SearchResult is not None
    except ImportError as e:
        pytest.fail(f"SearchResult model not implemented yet: {e}")


def test_candidate_pydantic_validation():
    """Test Candidate Pydantic model validation (will FAIL until T012 complete)."""
    try:
        from src.github_sourcer.models.candidate import Candidate

        # Valid candidate
        candidate = Candidate(
            github_username="torvalds",
            top_repos=[],
            languages=["C"],
            contribution_count=2500,
            account_age_days=5000,
            followers=200000,
            profile_url="https://github.com/torvalds",
            fetched_at=datetime.utcnow()
        )
        assert candidate.github_username == "torvalds"

        # Invalid candidate (negative contribution_count)
        with pytest.raises(Exception):  # Pydantic ValidationError
            Candidate(
                github_username="test",
                contribution_count=-10,  # Invalid
                account_age_days=100,
                followers=10,
                profile_url="https://github.com/test",
                top_repos=[],
                languages=[],
                fetched_at=datetime.utcnow()
            )

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")

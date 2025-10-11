"""Contract tests for Module 002 input schema.

Validates that JobRequirement from Module 001 matches expected input format.
"""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError


@pytest.fixture
def input_schema():
    """Load input JSON schema."""
    schema_path = Path(__file__).parent.parent.parent / "specs" / "002-github-sourcer-module" / "contracts" / "input-schema.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def valid_job_requirement():
    """Valid JobRequirement object (Module 001 output)."""
    return {
        "role": "Senior Python Developer",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["Docker", "PostgreSQL"],
        "years_of_experience": {
            "min": 5,
            "max": None,
            "range_text": "5+ years"
        },
        "seniority_level": "Senior",
        "location_preferences": ["India"],
        "domain": None,
        "confidence_scores": {
            "role": {"score": 0.95, "source": "explicit"}
        },
        "original_input": "Looking for Senior Python dev...",
        "schema_version": "1.0.0"
    }


def test_valid_job_requirement_passes_validation(input_schema, valid_job_requirement):
    """Valid JobRequirement should pass schema validation."""
    # Should not raise ValidationError
    validate(instance=valid_job_requirement, schema=input_schema)


def test_missing_required_skills_fails(input_schema, valid_job_requirement):
    """Missing required_skills should fail validation."""
    invalid = valid_job_requirement.copy()
    del invalid["required_skills"]

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=input_schema)

    assert "'required_skills' is a required property" in str(exc_info.value)


def test_missing_years_of_experience_fails(input_schema, valid_job_requirement):
    """Missing years_of_experience should fail validation."""
    invalid = valid_job_requirement.copy()
    del invalid["years_of_experience"]

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=input_schema)

    assert "'years_of_experience' is a required property" in str(exc_info.value)


def test_invalid_schema_version_fails(input_schema, valid_job_requirement):
    """Invalid schema_version format should fail validation."""
    invalid = valid_job_requirement.copy()
    invalid["schema_version"] = "invalid"

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=input_schema)

    assert "does not match" in str(exc_info.value)


def test_invalid_seniority_level_fails(input_schema, valid_job_requirement):
    """Seniority level not in enum should fail validation."""
    invalid = valid_job_requirement.copy()
    invalid["seniority_level"] = "InvalidLevel"

    with pytest.raises(ValidationError) as exc_info:
        validate(instance=invalid, schema=input_schema)

    assert "is not one of" in str(exc_info.value)


def test_empty_required_skills_passes(input_schema, valid_job_requirement):
    """Empty required_skills array is allowed (minItems: 0)."""
    valid = valid_job_requirement.copy()
    valid["required_skills"] = []

    # Should not raise
    validate(instance=valid, schema=input_schema)


def test_null_role_passes(input_schema, valid_job_requirement):
    """Null role is allowed."""
    valid = valid_job_requirement.copy()
    valid["role"] = None

    # Should not raise
    validate(instance=valid, schema=input_schema)

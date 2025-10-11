"""Contract tests for JD Parser output schema validation."""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError


@pytest.fixture
def output_schema():
    """Load output schema from contracts directory."""
    schema_path = Path(__file__).parent.parent.parent / "specs/001-jd-parser-module/contracts/output-schema.json"
    with open(schema_path) as f:
        return json.load(f)


class TestOutputContract:
    """Test that output conforms to output-schema.json contract."""

    def test_valid_complete_output(self, output_schema):
        """Valid output with all fields populated."""
        valid_output = {
            "role": "Senior Python Developer",
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "years_of_experience": {
                "min": 5,
                "max": None,
                "range_text": "5+ years"
            },
            "seniority_level": "Senior",
            "location_preferences": ["Remote", "San Francisco"],
            "domain": "Fintech",
            "confidence_scores": {
                "role": {
                    "score": 95,
                    "reasoning": "Explicitly stated in title",
                    "highlighted_spans": [{"start": 0, "end": 5, "text": "Senior"}]
                }
            },
            "original_input": "Senior Python Developer with 5+ years...",
            "schema_version": "1.0.0"
        }
        validate(instance=valid_output, schema=output_schema)

    def test_minimal_valid_output_with_role(self, output_schema):
        """Minimal valid output with only role (no required_skills)."""
        valid_output = {
            "role": "Developer",
            "required_skills": [],
            "preferred_skills": [],
            "years_of_experience": {"min": None, "max": None, "range_text": None},
            "seniority_level": None,
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {},
            "original_input": "Developer needed",
            "schema_version": "1.0.0"
        }
        validate(instance=valid_output, schema=output_schema)

    def test_minimal_valid_output_with_skills(self, output_schema):
        """Minimal valid output with only required_skills (no role)."""
        valid_output = {
            "role": None,
            "required_skills": ["Python"],
            "preferred_skills": [],
            "years_of_experience": {"min": None, "max": None, "range_text": None},
            "seniority_level": None,
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {},
            "original_input": "Python developer",
            "schema_version": "1.0.0"
        }
        validate(instance=valid_output, schema=output_schema)

    def test_invalid_seniority_level(self, output_schema):
        """Invalid seniority level should fail."""
        invalid_output = {
            "role": "Developer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "years_of_experience": {"min": None, "max": None, "range_text": None},
            "seniority_level": "Expert",  # Not in enum
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {},
            "original_input": "test",
            "schema_version": "1.0.0"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=output_schema)

    def test_negative_experience_fails(self, output_schema):
        """Negative years of experience should fail (minimum: 0)."""
        invalid_output = {
            "role": "Developer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "years_of_experience": {"min": -1, "max": None, "range_text": None},
            "seniority_level": None,
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {},
            "original_input": "test",
            "schema_version": "1.0.0"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=output_schema)

    def test_confidence_score_out_of_range(self, output_schema):
        """Confidence score outside 0-100 range should fail."""
        invalid_output = {
            "role": "Developer",
            "required_skills": ["Python"],
            "preferred_skills": [],
            "years_of_experience": {"min": None, "max": None, "range_text": None},
            "seniority_level": None,
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {
                "role": {
                    "score": 150,  # > 100
                    "reasoning": "test",
                    "highlighted_spans": []
                }
            },
            "original_input": "test",
            "schema_version": "1.0.0"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=output_schema)

    def test_missing_required_fields(self, output_schema):
        """Missing required fields should fail."""
        invalid_output = {
            "role": "Developer"
            # Missing required_skills, years_of_experience, etc.
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=output_schema)

    def test_invalid_schema_version_format(self, output_schema):
        """Schema version must match semver pattern."""
        invalid_output = {
            "role": "Developer",
            "required_skills": [],
            "preferred_skills": [],
            "years_of_experience": {"min": None, "max": None, "range_text": None},
            "seniority_level": None,
            "location_preferences": [],
            "domain": None,
            "confidence_scores": {},
            "original_input": "test",
            "schema_version": "1.0"  # Invalid semver (needs 1.0.0)
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=output_schema)

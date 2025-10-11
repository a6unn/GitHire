"""Contract tests for JD Parser input schema validation."""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError


@pytest.fixture
def input_schema():
    """Load input schema from contracts directory."""
    schema_path = Path(__file__).parent.parent.parent / "specs/001-jd-parser-module/contracts/input-schema.json"
    with open(schema_path) as f:
        return json.load(f)


class TestInputContract:
    """Test that input validation conforms to input-schema.json contract."""

    def test_valid_minimal_input(self, input_schema):
        """Valid input with only required 'text' field."""
        valid_input = {
            "text": "Senior Python developer with 5+ years experience"
        }
        # Should not raise ValidationError
        validate(instance=valid_input, schema=input_schema)

    def test_valid_input_with_language(self, input_schema):
        """Valid input with explicit language field."""
        valid_input = {
            "text": "React developer needed",
            "language": "en"
        }
        validate(instance=valid_input, schema=input_schema)

    def test_empty_text_fails(self, input_schema):
        """Empty text should fail validation (minLength: 1)."""
        invalid_input = {
            "text": ""
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_input, schema=input_schema)

    def test_missing_text_fails(self, input_schema):
        """Missing required 'text' field should fail."""
        invalid_input = {
            "language": "en"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_input, schema=input_schema)

    def test_invalid_language_fails(self, input_schema):
        """Non-English language should fail (only 'en' allowed)."""
        invalid_input = {
            "text": "Python developer",
            "language": "es"  # Spanish not supported
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_input, schema=input_schema)

    def test_additional_properties_fail(self, input_schema):
        """Additional properties not in schema should fail."""
        invalid_input = {
            "text": "Java developer",
            "extra_field": "not allowed"
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_input, schema=input_schema)

    def test_text_must_be_string(self, input_schema):
        """Text field must be a string."""
        invalid_input = {
            "text": 12345  # Number instead of string
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_input, schema=input_schema)

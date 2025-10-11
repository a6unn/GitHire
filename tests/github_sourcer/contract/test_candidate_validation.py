"""
Contract Tests for Candidate Validation Rules (Module 002)
===========================================================
These tests validate that Candidate objects enforce business rules and
constraints from the Module 002 specification.

TDD Approach: These tests WILL FAIL until we implement validation logic
in the Candidate model (e.g., skill_confidence_scores must match skills list)

Specification Reference: modules/002-github-sourcer-module/spec.md
- BR-001: skill_confidence_scores keys must match skills list
- BR-002: match_score must be <= max(skill_confidence_scores)
- BR-003: location_parsed confidence must reflect matching method
- BR-004: All confidence scores must be 0.0-1.0 range
"""

import pytest
from pydantic import ValidationError
from src.github_sourcer.models.candidate import Candidate


class TestCandidateValidationRules:
    """Contract tests for Candidate business rule validation"""

    def test_skill_confidence_keys_must_match_skills_list(self):
        """BR-001: skill_confidence_scores keys must be subset of skills"""
        valid_candidate = {
            "name": "John Doe",
            "github_url": "https://github.com/johndoe",
            "github_username": "johndoe",
            "email": None,
            "skills": ["Python", "React", "PostgreSQL"],
            "skill_confidence_scores": {
                "Python": 0.90,
                "React": 0.85,
                "PostgreSQL": 0.78
            },
            "bio": "Full Stack Developer",
            "location": "Bengaluru",
            "public_repos": 50,
            "followers": 100,
            "match_score": 0.86,
            "matched_skills": ["Python", "React"]
        }

        # Should succeed - all confidence score keys are in skills list
        candidate = Candidate(**valid_candidate)
        assert len(candidate.skill_confidence_scores) == 3

    def test_skill_confidence_with_extra_skill_fails(self):
        """BR-001: Confidence score for skill not in skills list should fail"""
        invalid_candidate = {
            "name": "Jane Smith",
            "github_url": "https://github.com/janesmith",
            "github_username": "janesmith",
            "email": None,
            "skills": ["Python", "Django"],
            "skill_confidence_scores": {
                "Python": 0.90,
                "Django": 0.85,
                "Flask": 0.80  # NOT in skills list!
            },
            "bio": "Backend Developer",
            "location": "Chennai",
            "public_repos": 30,
            "followers": 60,
            "match_score": 0.85,
            "matched_skills": ["Python", "Django"]
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**invalid_candidate)

        error_str = str(exc_info.value)
        assert "skill_confidence_scores" in error_str or "Flask" in error_str

    def test_match_score_must_not_exceed_max_confidence(self):
        """BR-002: match_score should not exceed max skill_confidence_scores"""
        invalid_candidate = {
            "name": "Bob Wilson",
            "github_url": "https://github.com/bobw",
            "github_username": "bobw",
            "email": None,
            "skills": ["JavaScript", "TypeScript"],
            "skill_confidence_scores": {
                "JavaScript": 0.70,
                "TypeScript": 0.65
            },
            "bio": "Frontend Developer",
            "location": "San Francisco",
            "public_repos": 25,
            "followers": 40,
            "match_score": 0.95,  # Invalid: higher than max confidence (0.70)
            "matched_skills": ["JavaScript"]
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**invalid_candidate)

        error_str = str(exc_info.value)
        assert "match_score" in error_str

    def test_location_parsed_confidence_matches_method(self):
        """BR-003: location_parsed confidence must be consistent with matched_via"""
        # Exact match should have high confidence (0.95-1.0)
        candidate_exact = {
            "name": "Alice Lee",
            "github_url": "https://github.com/alicel",
            "github_username": "alicel",
            "email": None,
            "skills": ["Go"],
            "skill_confidence_scores": {"Go": 0.88},
            "bio": "Backend Engineer",
            "location": "Mumbai, India",
            "location_parsed": {
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "confidence": 1.0,
                "matched_via": "city_exact"
            },
            "public_repos": 15,
            "followers": 25,
            "match_score": 0.88,
            "matched_skills": ["Go"]
        }

        candidate = Candidate(**candidate_exact)
        assert candidate.location_parsed["confidence"] >= 0.95
        assert candidate.location_parsed["matched_via"] == "city_exact"

    def test_location_fuzzy_match_has_lower_confidence(self):
        """BR-003: Fuzzy matches should have confidence < 1.0"""
        candidate_fuzzy = {
            "name": "Carlos Martinez",
            "github_url": "https://github.com/carlosm",
            "github_username": "carlosm",
            "email": None,
            "skills": ["Rust"],
            "skill_confidence_scores": {"Rust": 0.82},
            "bio": "Systems Programmer",
            "location": "Bangalore",  # Fuzzy match to "Bengaluru"
            "location_parsed": {
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "confidence": 1.0,  # Invalid: fuzzy match should have < 1.0
                "matched_via": "city_fuzzy",
                "fuzzy_match_score": 0.85
            },
            "public_repos": 12,
            "followers": 18,
            "match_score": 0.82,
            "matched_skills": ["Rust"]
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**candidate_fuzzy)

        error_str = str(exc_info.value)
        assert "location_parsed" in error_str or "confidence" in error_str

    def test_state_match_has_medium_confidence(self):
        """BR-003: State-level matches should have confidence 0.6-0.8"""
        candidate_state = {
            "name": "Diana Chen",
            "github_url": "https://github.com/dianac",
            "github_username": "dianac",
            "email": None,
            "skills": ["Swift"],
            "skill_confidence_scores": {"Swift": 0.85},
            "bio": "iOS Developer",
            "location": "California",
            "location_parsed": {
                "city": None,
                "state": "California",
                "country": "United States",
                "confidence": 0.70,
                "matched_via": "state_exact"
            },
            "public_repos": 20,
            "followers": 35,
            "match_score": 0.85,
            "matched_skills": ["Swift"]
        }

        candidate = Candidate(**candidate_state)
        assert 0.60 <= candidate.location_parsed["confidence"] <= 0.80
        assert candidate.location_parsed["matched_via"] == "state_exact"

    def test_country_match_has_low_confidence(self):
        """BR-003: Country-level matches should have confidence 0.3-0.5"""
        candidate_country = {
            "name": "Ethan Brown",
            "github_url": "https://github.com/ethanb",
            "github_username": "ethanb",
            "email": None,
            "skills": ["Kotlin"],
            "skill_confidence_scores": {"Kotlin": 0.80},
            "bio": "Android Developer",
            "location": "United States",
            "location_parsed": {
                "city": None,
                "state": None,
                "country": "United States",
                "confidence": 0.40,
                "matched_via": "country_exact"
            },
            "public_repos": 18,
            "followers": 28,
            "match_score": 0.80,
            "matched_skills": ["Kotlin"]
        }

        candidate = Candidate(**candidate_country)
        assert 0.30 <= candidate.location_parsed["confidence"] <= 0.50
        assert candidate.location_parsed["matched_via"] == "country_exact"

    def test_all_confidence_scores_in_valid_range(self):
        """BR-004: All confidence scores must be 0.0-1.0"""
        # Test match_score out of range
        invalid_match_score = {
            "name": "Test User",
            "github_url": "https://github.com/test",
            "github_username": "testuser1",
            "email": None,
            "skills": ["Python"],
            "skill_confidence_scores": {"Python": 0.85},
            "bio": "Developer",
            "location": "Remote",
            "public_repos": 10,
            "followers": 15,
            "match_score": 1.5,  # Invalid: > 1.0
            "matched_skills": ["Python"]
        }

        with pytest.raises(ValidationError):
            Candidate(**invalid_match_score)

    def test_skill_confidence_negative_fails(self):
        """BR-004: Negative confidence scores should fail"""
        invalid_negative = {
            "name": "Test User",
            "github_url": "https://github.com/test",
            "github_username": "testuser2",
            "email": None,
            "skills": ["JavaScript"],
            "skill_confidence_scores": {"JavaScript": -0.1},  # Invalid: < 0.0
            "bio": "Developer",
            "location": "Remote",
            "public_repos": 5,
            "followers": 8,
            "match_score": 0.60,
            "matched_skills": ["JavaScript"]
        }

        with pytest.raises(ValidationError):
            Candidate(**invalid_negative)

    def test_matched_skills_must_be_subset_of_skills(self):
        """BR-005: matched_skills must be subset of skills list"""
        invalid_matched_skills = {
            "name": "Test User",
            "github_url": "https://github.com/test",
            "github_username": "testuser3",
            "email": None,
            "skills": ["Python", "Django"],
            "skill_confidence_scores": {"Python": 0.85, "Django": 0.80},
            "bio": "Developer",
            "location": "Pune",
            "public_repos": 22,
            "followers": 38,
            "match_score": 0.85,
            "matched_skills": ["Python", "Flask"]  # Flask not in skills!
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**invalid_matched_skills)

        error_str = str(exc_info.value)
        assert "matched_skills" in error_str

    def test_detection_method_must_be_valid_enum(self):
        """BR-006: detection_method must be from allowed values"""
        valid_methods = ["dependency_graph", "ensemble_fallback", "manual"]

        for method in valid_methods:
            candidate = {
                "name": "Test User",
                "github_url": "https://github.com/test",
                "github_username": "testuser4",
                "email": None,
                "skills": ["Python"],
                "skill_confidence_scores": {"Python": 0.85},
                "bio": "Developer",
                "location": "Remote",
                "public_repos": 10,
                "followers": 15,
                "match_score": 0.85,
                "matched_skills": ["Python"],
                "detection_method": method
            }
            c = Candidate(**candidate)
            assert c.detection_method == method

    def test_invalid_detection_method_fails(self):
        """BR-006: Invalid detection_method should fail"""
        invalid_candidate = {
            "name": "Test User",
            "github_url": "https://github.com/test",
            "github_username": "testuser5",
            "email": None,
            "skills": ["Python"],
            "skill_confidence_scores": {"Python": 0.85},
            "bio": "Developer",
            "location": "Remote",
            "public_repos": 10,
            "followers": 15,
            "match_score": 0.85,
            "matched_skills": ["Python"],
            "detection_method": "invalid_method"
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**invalid_candidate)

        error_str = str(exc_info.value)
        assert "detection_method" in error_str

    def test_github_url_must_be_valid_format(self):
        """BR-007: github_url must be valid GitHub profile URL"""
        invalid_urls = [
            "not-a-url",
            "https://gitlab.com/user",
            "https://github.com",  # No username
            "github.com/user",  # Missing https://
        ]

        for invalid_url in invalid_urls:
            candidate = {
                "name": "Test User",
                "github_url": invalid_url,
                "github_username": "testuser6",
                "email": None,
                "skills": ["Python"],
                "bio": "Developer",
                "location": "Remote",
                "public_repos": 10,
                "followers": 15,
                "match_score": 0.75,
                "matched_skills": ["Python"]
            }

            with pytest.raises(ValidationError) as exc_info:
                Candidate(**candidate)

            error_str = str(exc_info.value)
            assert "github_url" in error_str

    def test_valid_github_url_formats(self):
        """BR-007: Valid GitHub URL formats should pass"""
        valid_urls = [
            "https://github.com/username",
            "https://github.com/user-name",
            "https://github.com/user_name",
            "https://github.com/UserName123",
        ]

        for valid_url in valid_urls:
            candidate = {
                "name": "Test User",
                "github_url": valid_url,
                "github_username": "testuser7",
                "email": None,
                "skills": ["Python"],
                "bio": "Developer",
                "location": "Remote",
                "public_repos": 10,
                "followers": 15,
                "match_score": 0.75,
                "matched_skills": ["Python"]
            }
            c = Candidate(**candidate)
            assert str(c.github_url) == valid_url

    def test_email_validation_if_provided(self):
        """BR-008: Email must be valid format if provided"""
        invalid_emails = ["not-an-email", "@example.com", "user@", "user"]

        for invalid_email in invalid_emails:
            candidate = {
                "name": "Test User",
                "github_url": "https://github.com/test",
                "github_username": "testuser8",
                "email": invalid_email,
                "skills": ["Python"],
                "bio": "Developer",
                "location": "Remote",
                "public_repos": 10,
                "followers": 15,
                "match_score": 0.75,
                "matched_skills": ["Python"]
            }

            with pytest.raises(ValidationError) as exc_info:
                Candidate(**candidate)

            error_str = str(exc_info.value)
            assert "email" in error_str

    def test_public_repos_and_followers_must_be_non_negative(self):
        """BR-009: public_repos and followers must be >= 0"""
        invalid_candidate = {
            "name": "Test User",
            "github_url": "https://github.com/test",
            "github_username": "testuser9",
            "email": None,
            "skills": ["Python"],
            "bio": "Developer",
            "location": "Remote",
            "public_repos": -5,  # Invalid: negative
            "followers": 10,
            "match_score": 0.75,
            "matched_skills": ["Python"]
        }

        with pytest.raises(ValidationError):
            Candidate(**invalid_candidate)

"""
Contract Tests for Candidate Output Schema (Module 002)
=========================================================
These tests validate that the Candidate model returns enhanced metadata fields
from the Module 002 specification (skill_confidence_scores, location_parsed,
sourcing_metadata, etc.)

TDD Approach: These tests WILL FAIL until we update the Candidate model
in src/models.py to include the new enhanced output fields.

Specification Reference: modules/002-github-sourcer-module/spec.md
- FR-003: Output schema must include skill confidence scores
- FR-004: Output schema must include parsed location hierarchy
- FR-005: Output schema must include sourcing metadata
"""

import pytest
from pydantic import ValidationError
from src.github_sourcer.models.candidate import Candidate


class TestCandidateOutputSchema:
    """Contract tests for Candidate output validation"""

    def test_minimal_valid_candidate(self):
        """Test that minimal required fields still work (backward compatibility)"""
        minimal_candidate = {
            "name": "John Doe",
            "github_url": "https://github.com/johndoe",
            "github_username": "johndoe",
            "email": None,
            "skills": ["Python", "React"],
            "bio": "Software Engineer",
            "location": "Bengaluru, India",
            "public_repos": 42,
            "followers": 150,
            "match_score": 0.85,
            "matched_skills": ["Python"]
        }

        candidate = Candidate(**minimal_candidate)
        assert candidate.name == "John Doe"
        assert str(candidate.github_url) == "https://github.com/johndoe"
        assert candidate.match_score == 0.85

    def test_skill_confidence_scores_field(self):
        """Test that skill_confidence_scores dict is included (FR-003)"""
        candidate_with_confidence = {
            "name": "Jane Smith",
            "github_url": "https://github.com/janesmith",
            "github_username": "janesmith",
            "email": "jane@example.com",
            "skills": ["Python", "TensorFlow", "pandas"],
            "skill_confidence_scores": {
                "Python": 0.95,
                "TensorFlow": 0.82,
                "pandas": 0.88
            },
            "bio": "ML Engineer",
            "location": "San Francisco, CA",
            "public_repos": 68,
            "followers": 320,
            "match_score": 0.92,
            "matched_skills": ["Python", "TensorFlow"]
        }

        candidate = Candidate(**candidate_with_confidence)
        assert candidate.skill_confidence_scores["Python"] == 0.95
        assert candidate.skill_confidence_scores["TensorFlow"] == 0.82
        assert candidate.skill_confidence_scores["pandas"] == 0.88

    def test_skill_confidence_scores_range_validation(self):
        """Test that skill confidence scores must be 0.0-1.0"""
        invalid_candidate = {
            "name": "Invalid User",
            "github_url": "https://github.com/invalid",
            "github_username": "invaliduser",
            "email": None,
            "skills": ["JavaScript"],
            "skill_confidence_scores": {
                "JavaScript": 1.5  # Invalid: > 1.0
            },
            "bio": "Developer",
            "location": "Remote",
            "public_repos": 10,
            "followers": 5,
            "match_score": 0.60,
            "matched_skills": ["JavaScript"]
        }

        with pytest.raises(ValidationError) as exc_info:
            Candidate(**invalid_candidate)

        # Should fail with validation error
        assert "skill_confidence_scores" in str(exc_info.value)

    def test_location_parsed_hierarchy_field(self):
        """Test that location_parsed contains hierarchical breakdown (FR-004)"""
        candidate_with_parsed_location = {
            "name": "Rajesh Kumar",
            "github_url": "https://github.com/rajeshk",
            "github_username": "rajeshk",
            "email": None,
            "skills": ["Java", "Spring Boot"],
            "skill_confidence_scores": {
                "Java": 0.90,
                "Spring Boot": 0.75
            },
            "bio": "Backend Developer",
            "location": "Bengaluru, Karnataka, India",
            "location_parsed": {
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "confidence": 0.95,
                "matched_via": "city_exact"
            },
            "public_repos": 35,
            "followers": 80,
            "match_score": 0.78,
            "matched_skills": ["Java", "Spring Boot"]
        }

        candidate = Candidate(**candidate_with_parsed_location)
        assert candidate.location_parsed["city"] == "Bengaluru"
        assert candidate.location_parsed["state"] == "Karnataka"
        assert candidate.location_parsed["country"] == "India"
        assert candidate.location_parsed["confidence"] == 0.95
        assert candidate.location_parsed["matched_via"] == "city_exact"

    def test_sourcing_metadata_field(self):
        """Test that sourcing_metadata includes pipeline details (FR-005)"""
        candidate_with_metadata = {
            "name": "Alice Johnson",
            "github_url": "https://github.com/alicej",
            "github_username": "alicej",
            "email": "alice@example.com",
            "skills": ["React", "TypeScript", "Node.js"],
            "skill_confidence_scores": {
                "React": 0.88,
                "TypeScript": 0.82,
                "Node.js": 0.79
            },
            "bio": "Full Stack Developer",
            "location": "New York, NY",
            "location_parsed": {
                "city": "New York",
                "state": "New York",
                "country": "United States",
                "confidence": 1.0,
                "matched_via": "city_exact"
            },
            "public_repos": 55,
            "followers": 210,
            "match_score": 0.86,
            "matched_skills": ["React", "TypeScript", "Node.js"],
            "sourcing_metadata": {
                "discovered_via": "github_search",
                "discovery_query": "language:TypeScript location:\"New York\"",
                "profile_enriched_via": "graphql_batch",
                "skills_detected_via": "dependency_graph",
                "location_matched_via": "hierarchical_exact",
                "processing_timestamp": "2025-10-09T10:30:00Z",
                "total_pipeline_time_ms": 450
            }
        }

        candidate = Candidate(**candidate_with_metadata)
        assert candidate.sourcing_metadata["discovered_via"] == "github_search"
        assert candidate.sourcing_metadata["skills_detected_via"] == "dependency_graph"
        assert candidate.sourcing_metadata["location_matched_via"] == "hierarchical_exact"
        assert candidate.sourcing_metadata["total_pipeline_time_ms"] == 450

    def test_detection_method_field(self):
        """Test that detection_method indicates which pipeline was used (FR-006)"""
        candidate_with_method = {
            "name": "Carlos Rodriguez",
            "github_url": "https://github.com/carlosr",
            "github_username": "carlosr",
            "email": None,
            "skills": ["Go", "Kubernetes", "Docker"],
            "skill_confidence_scores": {
                "Go": 0.91,
                "Kubernetes": 0.87,
                "Docker": 0.84
            },
            "bio": "DevOps Engineer",
            "location": "Austin, TX",
            "location_parsed": {
                "city": "Austin",
                "state": "Texas",
                "country": "United States",
                "confidence": 1.0,
                "matched_via": "city_exact"
            },
            "public_repos": 47,
            "followers": 130,
            "match_score": 0.89,
            "matched_skills": ["Go", "Kubernetes", "Docker"],
            "detection_method": "dependency_graph",
            "sourcing_metadata": {
                "discovered_via": "github_search",
                "skills_detected_via": "dependency_graph",
                "location_matched_via": "hierarchical_exact"
            }
        }

        candidate = Candidate(**candidate_with_method)
        assert candidate.detection_method == "dependency_graph"

    def test_fallback_detection_method(self):
        """Test ensemble fallback when dependency graph fails (FR-007)"""
        candidate_with_fallback = {
            "name": "Priya Sharma",
            "github_url": "https://github.com/priyas",
            "github_username": "priyas",
            "email": None,
            "skills": ["Python", "Django", "PostgreSQL"],
            "skill_confidence_scores": {
                "Python": 0.78,
                "Django": 0.72,
                "PostgreSQL": 0.68
            },
            "bio": "Backend Developer",
            "location": "Chennai, Tamil Nadu",
            "location_parsed": {
                "city": "Chennai",
                "state": "Tamil Nadu",
                "country": "India",
                "confidence": 0.95,
                "matched_via": "city_exact"
            },
            "public_repos": 28,
            "followers": 65,
            "match_score": 0.74,
            "matched_skills": ["Python", "Django", "PostgreSQL"],
            "detection_method": "ensemble_fallback",
            "sourcing_metadata": {
                "discovered_via": "github_search",
                "skills_detected_via": "ensemble_fallback",
                "ensemble_signals_used": [
                    "repository_topics",
                    "repository_languages",
                    "repository_names"
                ],
                "dependency_graph_failed": True,
                "dependency_graph_error": "502_bad_gateway"
            }
        }

        candidate = Candidate(**candidate_with_fallback)
        assert candidate.detection_method == "ensemble_fallback"
        assert candidate.sourcing_metadata["dependency_graph_failed"] is True
        assert len(candidate.sourcing_metadata["ensemble_signals_used"]) == 3

    def test_location_fuzzy_match_metadata(self):
        """Test location parsed with fuzzy matching (FR-008)"""
        candidate_fuzzy_location = {
            "name": "Michael Chen",
            "github_url": "https://github.com/michaelc",
            "github_username": "michaelc",
            "email": None,
            "skills": ["Rust", "WebAssembly"],
            "skill_confidence_scores": {
                "Rust": 0.93,
                "WebAssembly": 0.81
            },
            "bio": "Systems Programmer",
            "location": "Bangalore, India",  # User wrote "Bangalore" not "Bengaluru"
            "location_parsed": {
                "city": "Bengaluru",  # Normalized to canonical form
                "state": "Karnataka",
                "country": "India",
                "confidence": 0.85,
                "matched_via": "city_fuzzy",
                "original_input": "Bangalore",
                "fuzzy_match_score": 0.85
            },
            "public_repos": 19,
            "followers": 42,
            "match_score": 0.81,
            "matched_skills": ["Rust"]
        }

        candidate = Candidate(**candidate_fuzzy_location)
        assert candidate.location_parsed["city"] == "Bengaluru"
        assert candidate.location_parsed["matched_via"] == "city_fuzzy"
        assert candidate.location_parsed["original_input"] == "Bangalore"
        assert candidate.location_parsed["fuzzy_match_score"] == 0.85

    def test_hierarchical_state_match_metadata(self):
        """Test location matched at state level (FR-009)"""
        candidate_state_match = {
            "name": "Sarah Lee",
            "github_url": "https://github.com/sarahl",
            "github_username": "sarahl",
            "email": None,
            "skills": ["Swift", "iOS"],
            "skill_confidence_scores": {
                "Swift": 0.90,
                "iOS": 0.88
            },
            "bio": "iOS Developer",
            "location": "California",  # Only state, no city
            "location_parsed": {
                "city": None,
                "state": "California",
                "country": "United States",
                "confidence": 0.70,  # Lower confidence for state-only match
                "matched_via": "state_exact"
            },
            "public_repos": 31,
            "followers": 95,
            "match_score": 0.77,
            "matched_skills": ["Swift"]
        }

        candidate = Candidate(**candidate_state_match)
        assert candidate.location_parsed["city"] is None
        assert candidate.location_parsed["state"] == "California"
        assert candidate.location_parsed["matched_via"] == "state_exact"
        assert candidate.location_parsed["confidence"] == 0.70

    def test_complete_enhanced_candidate(self):
        """Test Candidate with ALL enhanced output fields"""
        complete_candidate = {
            "name": "David Kim",
            "github_url": "https://github.com/davidk",
            "github_username": "davidk",
            "email": "david@example.com",
            "skills": ["Python", "pandas", "scikit-learn", "TensorFlow"],
            "skill_confidence_scores": {
                "Python": 0.95,
                "pandas": 0.92,
                "scikit-learn": 0.88,
                "TensorFlow": 0.85
            },
            "bio": "Data Scientist @ Tech Corp",
            "location": "Bengaluru, Karnataka, India",
            "location_parsed": {
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "confidence": 0.95,
                "matched_via": "city_exact"
            },
            "public_repos": 73,
            "followers": 280,
            "match_score": 0.91,
            "matched_skills": ["Python", "pandas", "scikit-learn", "TensorFlow"],
            "detection_method": "dependency_graph",
            "sourcing_metadata": {
                "discovered_via": "github_search",
                "discovery_query": "language:Python pandas scikit-learn location:Bengaluru",
                "profile_enriched_via": "graphql_batch",
                "skills_detected_via": "dependency_graph",
                "location_matched_via": "hierarchical_exact",
                "processing_timestamp": "2025-10-09T10:35:00Z",
                "total_pipeline_time_ms": 520,
                "graphql_batch_id": "batch_001",
                "graphql_batch_size": 50
            }
        }

        candidate = Candidate(**complete_candidate)

        # Validate all fields
        assert candidate.name == "David Kim"
        assert candidate.email == "david@example.com"
        assert len(candidate.skills) == 4
        assert len(candidate.skill_confidence_scores) == 4
        assert candidate.skill_confidence_scores["Python"] == 0.95

        assert candidate.location_parsed["city"] == "Bengaluru"
        assert candidate.location_parsed["state"] == "Karnataka"
        assert candidate.location_parsed["country"] == "India"

        assert candidate.detection_method == "dependency_graph"
        assert candidate.sourcing_metadata["discovered_via"] == "github_search"
        assert candidate.sourcing_metadata["total_pipeline_time_ms"] == 520

    def test_optional_fields_can_be_none(self):
        """Test that optional enhanced fields can be None/omitted"""
        minimal_candidate = {
            "name": "Test User",
            "github_url": "https://github.com/testuser",
            "github_username": "testuser",
            "email": None,
            "skills": ["JavaScript"],
            "bio": "Developer",
            "location": "Remote",
            "public_repos": 5,
            "followers": 10,
            "match_score": 0.60,
            "matched_skills": ["JavaScript"]
        }

        candidate = Candidate(**minimal_candidate)

        # These fields should be optional
        assert not hasattr(candidate, "skill_confidence_scores") or candidate.skill_confidence_scores is None
        assert not hasattr(candidate, "location_parsed") or candidate.location_parsed is None
        assert not hasattr(candidate, "detection_method") or candidate.detection_method is None
        assert not hasattr(candidate, "sourcing_metadata") or candidate.sourcing_metadata is None

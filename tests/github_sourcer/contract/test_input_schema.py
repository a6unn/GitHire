"""
Contract Tests for JobRequirement Input Schema (Module 002)
==============================================================
These tests validate that the JobRequirement model accepts enhanced fields
from the Module 002 specification (sourcing_source_config, skill_confidence_min,
location_hierarchy_enabled, etc.)

TDD Approach: These tests WILL FAIL until we update the JobRequirement model
in src/models.py to include the new enhanced fields.

Specification Reference: modules/002-github-sourcer-module/spec.md
- FR-001: Input schema must accept all enhanced configuration fields
- FR-002: Backward compatibility with existing JobRequirement format
"""

import pytest
from pydantic import ValidationError
from src.jd_parser.models import JobRequirement


class TestJobRequirementInputSchema:
    """Contract tests for JobRequirement input validation"""

    def test_minimal_valid_job_requirement(self):
        """Test that minimal required fields still work (backward compatibility)"""
        minimal_job = {
            "role": "Senior Software Engineer",
            "required_skills": ["Python", "FastAPI"],
            "original_input": "Looking for a Senior Software Engineer with Python and FastAPI skills in Bengaluru, India"
        }

        job_req = JobRequirement(**minimal_job)
        assert job_req.role == "Senior Software Engineer"
        assert job_req.required_skills == ["Python", "FastAPI"]

    def test_enhanced_sourcing_source_config(self):
        """Test that sourcing_source_config field accepts valid values (FR-025)"""
        enhanced_job = {
            "role": "Machine Learning Engineer",
            "required_skills": ["Python", "TensorFlow"],
            "location": "San Francisco, CA",
            "original_input": "We need a Machine Learning Engineer with Python and TensorFlow experience in San Francisco, CA",
            "sourcing_source_config": {
                "github_enabled": True,
                "linkedin_enabled": False,
                "stackoverflow_enabled": False
            }
        }

        job_req = JobRequirement(**enhanced_job)
        assert job_req.sourcing_source_config["github_enabled"] is True
        assert job_req.sourcing_source_config["linkedin_enabled"] is False

    def test_skill_confidence_min_threshold(self):
        """Test that skill_confidence_min accepts float values 0.0-1.0 (FR-026)"""
        job_with_confidence = {
            "role": "Data Scientist",
            "required_skills": ["pandas", "NumPy"],
            "location": "Remote",
            "original_input": "Data Scientist position in Remote with pandas and NumPy expertise required",
            "skill_confidence_min": 0.75  # Minimum 75% confidence
        }

        job_req = JobRequirement(**job_with_confidence)
        assert job_req.skill_confidence_min == 0.75

    def test_skill_confidence_min_invalid_range(self):
        """Test that skill_confidence_min rejects out-of-range values"""
        invalid_job = {
            "role": "Backend Engineer",
            "required_skills": ["Node.js"],
            "location": "New York",
            "original_input": "Backend Engineer needed in New York with strong Node.js background",
            "skill_confidence_min": 1.5  # Invalid: > 1.0
        }

        with pytest.raises(ValidationError) as exc_info:
            JobRequirement(**invalid_job)

        # Should fail with validation error about range
        assert "skill_confidence_min" in str(exc_info.value)

    def test_location_hierarchy_enabled_flag(self):
        """Test location_hierarchy_enabled boolean field (FR-027)"""
        job_with_hierarchy = {
            "role": "Frontend Developer",
            "required_skills": ["React", "TypeScript"],
            "location": "Chennai",
            "original_input": "Frontend Developer role in Chennai requiring React and TypeScript skills",
            "location_hierarchy_enabled": True  # Enable city→state→country matching
        }

        job_req = JobRequirement(**job_with_hierarchy)
        assert job_req.location_hierarchy_enabled is True

    def test_location_fuzzy_match_enabled_flag(self):
        """Test location_fuzzy_match_enabled boolean field (FR-028)"""
        job_with_fuzzy = {
            "role": "DevOps Engineer",
            "required_skills": ["Kubernetes", "Docker"],
            "location": "Bangalore",  # Should match "Bengaluru" with fuzzy matching
            "original_input": "DevOps Engineer opening in Bangalore with Kubernetes and Docker experience",
            "location_fuzzy_match_enabled": True,
            "location_fuzzy_threshold": 0.80  # 80% similarity required
        }

        job_req = JobRequirement(**job_with_fuzzy)
        assert job_req.location_fuzzy_match_enabled is True
        assert job_req.location_fuzzy_threshold == 0.80

    def test_bigquery_discovery_config(self):
        """Test BigQuery discovery configuration (FR-029)"""
        job_with_bigquery = {
            "role": "Full Stack Developer",
            "required_skills": ["React", "Node.js", "PostgreSQL"],
            "location": "India",
            "original_input": "Full Stack Developer position in India with React, Node.js, and PostgreSQL skills",
            "bigquery_discovery_enabled": True,
            "bigquery_time_range_days": 30  # Last 30 days of GHArchive data
        }

        job_req = JobRequirement(**job_with_bigquery)
        assert job_req.bigquery_discovery_enabled is True
        assert job_req.bigquery_time_range_days == 30

    def test_graphql_batching_config(self):
        """Test GraphQL batching configuration (FR-030)"""
        job_with_batching = {
            "role": "Backend Engineer",
            "required_skills": ["Go", "gRPC"],
            "location": "Seattle",
            "original_input": "Backend Engineer opportunity in Seattle with Go and gRPC expertise required",
            "graphql_batching_enabled": True,
            "graphql_batch_size": 50  # Batch 50 profiles per request
        }

        job_req = JobRequirement(**job_with_batching)
        assert job_req.graphql_batching_enabled is True
        assert job_req.graphql_batch_size == 50

    def test_dependency_graph_detection_config(self):
        """Test Dependency Graph detection configuration (FR-031)"""
        job_with_dep_graph = {
            "role": "Python Developer",
            "required_skills": ["Django", "Celery"],
            "location": "London",
            "original_input": "Python Developer wanted in London with Django and Celery experience for our backend team",
            "dependency_graph_enabled": True,
            "dependency_graph_fallback_to_ensemble": True
        }

        job_req = JobRequirement(**job_with_dep_graph)
        assert job_req.dependency_graph_enabled is True
        assert job_req.dependency_graph_fallback_to_ensemble is True

    def test_max_candidates_config(self):
        """Test max_candidates configuration (FR-032)"""
        job_with_limit = {
            "role": "Cloud Architect",
            "required_skills": ["AWS", "Terraform"],
            "location": "Austin",
            "original_input": "Cloud Architect position in Austin with AWS and Terraform infrastructure expertise",
            "max_candidates": 50  # Return top 50 instead of default 25
        }

        job_req = JobRequirement(**job_with_limit)
        assert job_req.max_candidates == 50

    def test_complete_enhanced_job_requirement(self):
        """Test JobRequirement with ALL enhanced fields"""
        complete_job = {
            "role": "Senior Data Engineer",
            "required_skills": ["Python", "Spark", "Airflow", "Kafka"],
            "location": "Bengaluru, Karnataka, India",
            "original_input": "Senior Data Engineer needed in Bengaluru with Python, Spark, Airflow, and Kafka for big data pipelines",

            # Enhanced sourcing configuration
            "sourcing_source_config": {
                "github_enabled": True,
                "linkedin_enabled": False,
                "stackoverflow_enabled": False
            },

            # Skills detection configuration
            "skill_confidence_min": 0.70,
            "dependency_graph_enabled": True,
            "dependency_graph_fallback_to_ensemble": True,

            # Location filtering configuration
            "location_hierarchy_enabled": True,
            "location_fuzzy_match_enabled": True,
            "location_fuzzy_threshold": 0.85,

            # Discovery configuration
            "bigquery_discovery_enabled": False,
            "bigquery_time_range_days": 30,

            # Performance configuration
            "graphql_batching_enabled": True,
            "graphql_batch_size": 50,
            "max_candidates": 25
        }

        job_req = JobRequirement(**complete_job)

        # Validate all fields
        assert job_req.role == "Senior Data Engineer"
        assert len(job_req.required_skills) == 4

        assert job_req.sourcing_source_config["github_enabled"] is True
        assert job_req.skill_confidence_min == 0.70
        assert job_req.location_hierarchy_enabled is True
        assert job_req.location_fuzzy_match_enabled is True
        assert job_req.location_fuzzy_threshold == 0.85
        assert job_req.bigquery_discovery_enabled is False
        assert job_req.graphql_batching_enabled is True
        assert job_req.graphql_batch_size == 50
        assert job_req.max_candidates == 25

    def test_default_values_for_optional_fields(self):
        """Test that optional enhanced fields have sensible defaults"""
        minimal_job = {
            "role": "Software Engineer",
            "required_skills": ["JavaScript"],
            "location": "Remote",
            "original_input": "Software Engineer role for Remote work with JavaScript development"
        }

        job_req = JobRequirement(**minimal_job)

        # Verify defaults match spec.md defaults
        assert job_req.skill_confidence_min == 0.50  # Default 50%
        assert job_req.location_hierarchy_enabled is True  # Default enabled
        assert job_req.location_fuzzy_match_enabled is True  # Default enabled
        assert job_req.location_fuzzy_threshold == 0.80  # Default 80%
        assert job_req.bigquery_discovery_enabled is False  # Default disabled
        assert job_req.graphql_batching_enabled is True  # Default enabled
        assert job_req.graphql_batch_size == 50  # Default batch size
        assert job_req.max_candidates == 25  # Default limit

    def test_skill_normalization_hint(self):
        """Test that skill aliases are preserved for normalization (FR-033)"""
        job_with_aliases = {
            "role": "React Developer",
            "required_skills": ["react", "reactjs", "React.js"],  # All should normalize to "React"
            "location": "San Francisco",
            "original_input": "React Developer position in San Francisco working with modern React.js frameworks and libraries"
        }

        job_req = JobRequirement(**job_with_aliases)
        # The model should preserve original input for normalization later
        assert len(job_req.required_skills) == 3
        assert "react" in job_req.required_skills
        assert "reactjs" in job_req.required_skills

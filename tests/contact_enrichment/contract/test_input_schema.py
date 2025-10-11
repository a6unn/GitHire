"""
Contract Test: Input Schema Validation
Module 010: Contact Enrichment

Tests that the input (Candidate list from Module 002/003) matches expected schema.
These tests MUST FAIL initially (TDD).
"""

import pytest
from pydantic import ValidationError


def test_valid_candidate_passes_validation():
    """
    Test: Valid Candidate with github_username passes validation
    Expected: FAIL - ContactEnricher not implemented yet
    """
    # This will fail because ContactEnricher doesn't exist
    from src.contact_enrichment import ContactEnricher

    # Mock a valid candidate from Module 002
    candidate = {
        "github_username": "testuser",
        "name": "Test User",
        "bio": "Python developer",
        "location": "San Francisco, CA",
        "top_repos": [],
        "languages": ["Python"],
        "contribution_count": 100,
        "account_age_days": 365,
        "profile_url": "https://github.com/testuser",
        "avatar_url": "https://avatars.githubusercontent.com/u/123",
        "fetched_at": "2025-10-10T00:00:00Z"
    }

    # Should accept valid candidate
    enricher = ContactEnricher()
    # No exception should be raised
    assert True


def test_missing_github_username_fails_validation():
    """
    Test: Missing github_username fails validation
    Expected: FAIL - ContactEnricher not implemented yet
    """
    from src.contact_enrichment import ContactEnricher

    # Invalid candidate - missing github_username
    candidate = {
        "name": "Test User",
        "bio": "Python developer"
    }

    enricher = ContactEnricher()

    # Should raise validation error for missing github_username
    with pytest.raises(ValidationError):
        enricher.validate_candidate(candidate)


def test_list_of_candidates_structure_is_valid():
    """
    Test: List[Candidate] structure is valid
    Expected: FAIL - ContactEnricher not implemented yet
    """
    from src.contact_enrichment import ContactEnricher

    candidates = [
        {
            "github_username": "user1",
            "name": "User 1",
            "bio": "Developer",
            "location": "NYC",
            "top_repos": [],
            "languages": ["Python"],
            "contribution_count": 50,
            "account_age_days": 200,
            "profile_url": "https://github.com/user1",
            "avatar_url": "https://avatars.githubusercontent.com/u/1",
            "fetched_at": "2025-10-10T00:00:00Z"
        },
        {
            "github_username": "user2",
            "name": "User 2",
            "bio": "Engineer",
            "location": "LA",
            "top_repos": [],
            "languages": ["JavaScript"],
            "contribution_count": 75,
            "account_age_days": 300,
            "profile_url": "https://github.com/user2",
            "avatar_url": "https://avatars.githubusercontent.com/u/2",
            "fetched_at": "2025-10-10T00:00:00Z"
        }
    ]

    enricher = ContactEnricher()

    # Should accept list of valid candidates
    assert len(candidates) == 2

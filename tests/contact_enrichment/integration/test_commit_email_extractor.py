"""
Integration Test: Layer 2 - Commit Email Extraction
Module 010: Contact Enrichment

Tests the CommitEmailExtractor service's ability to extract emails from commit history.
These tests MUST FAIL initially (TDD).
"""

import pytest


@pytest.mark.asyncio
async def test_extract_commit_emails_from_events():
    """
    Test: Extract unique emails from public events (commits)
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    # Mock GitHub events API response
    events_data = [
        {
            "type": "PushEvent",
            "payload": {
                "commits": [
                    {"author": {"email": "test@gmail.com"}},
                    {"author": {"email": "test@gmail.com"}},  # Duplicate
                    {"author": {"email": "user@company.com"}},
                ]
            },
        }
    ]

    result = await extractor.extract("testuser", events_data)

    # Should return deduplicated emails
    assert len(result) == 2
    assert "test@gmail.com" in result
    assert "user@company.com" in result


@pytest.mark.asyncio
async def test_extract_commit_emails_filters_noreply():
    """
    Test: Noreply emails from commits are filtered
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    events_data = [
        {
            "type": "PushEvent",
            "payload": {
                "commits": [
                    {"author": {"email": "test@gmail.com"}},
                    {"author": {"email": "12345+user@users.noreply.github.com"}},
                ]
            },
        }
    ]

    result = await extractor.extract("testuser", events_data)

    # Noreply should be filtered
    assert len(result) == 1
    assert "test@gmail.com" in result
    assert "12345+user@users.noreply.github.com" not in result


@pytest.mark.asyncio
async def test_extract_commit_emails_filters_spam_domains():
    """
    Test: Spam domain emails from commits are filtered
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    events_data = [
        {
            "type": "PushEvent",
            "payload": {
                "commits": [
                    {"author": {"email": "test@gmail.com"}},
                    {"author": {"email": "fake@example.com"}},
                    {"author": {"email": "user@test.com"}},
                ]
            },
        }
    ]

    result = await extractor.extract("testuser", events_data)

    # Spam domains should be filtered
    assert len(result) == 1
    assert "test@gmail.com" in result


@pytest.mark.asyncio
async def test_extract_commit_emails_handles_empty_events():
    """
    Test: Empty events list returns empty result
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    result = await extractor.extract("testuser", [])

    assert result == []


@pytest.mark.asyncio
async def test_extract_commit_emails_ignores_non_push_events():
    """
    Test: Non-PushEvent events are ignored
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    events_data = [
        {"type": "WatchEvent", "payload": {}},  # Not a PushEvent
        {"type": "ForkEvent", "payload": {}},  # Not a PushEvent
        {
            "type": "PushEvent",
            "payload": {"commits": [{"author": {"email": "test@gmail.com"}}]},
        },
    ]

    result = await extractor.extract("testuser", events_data)

    # Only PushEvent should be processed
    assert len(result) == 1
    assert "test@gmail.com" in result


@pytest.mark.asyncio
async def test_extract_commit_emails_handles_missing_author():
    """
    Test: Events with missing author field are handled gracefully
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    events_data = [
        {
            "type": "PushEvent",
            "payload": {
                "commits": [
                    {"author": {"email": "test@gmail.com"}},
                    {},  # Missing author
                ]
            },
        }
    ]

    result = await extractor.extract("testuser", events_data)

    # Should handle missing author gracefully
    assert len(result) == 1
    assert "test@gmail.com" in result


@pytest.mark.asyncio
async def test_extract_commit_emails_records_source():
    """
    Test: Contact source is recorded as 'commit'
    Expected: FAIL - CommitEmailExtractor not implemented
    """
    from src.contact_enrichment.services.commit_email_extractor import (
        CommitEmailExtractor,
    )

    extractor = CommitEmailExtractor(github_token="fake_token")

    events_data = [
        {
            "type": "PushEvent",
            "payload": {"commits": [{"author": {"email": "test@gmail.com"}}]},
        }
    ]

    result = await extractor.extract_with_sources("testuser", events_data)

    # Should return tuples of (email, source)
    assert len(result) == 1
    assert result[0] == ("test@gmail.com", "commit")

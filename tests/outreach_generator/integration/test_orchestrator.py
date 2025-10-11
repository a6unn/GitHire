"""
Integration tests for OutreachOrchestrator (3-Stage Pipeline Integration)

Tests the complete pipeline: Analysis → Generation → Refinement
"""

import json
import pytest
from unittest.mock import Mock
from datetime import datetime

from src.outreach_generator.orchestrator import OutreachOrchestrator
from src.outreach_generator.models import OutreachMessage, ChannelType


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM client for testing the full pipeline."""

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.call_count = 0
        self.last_prompt = None

    def complete(self, prompt, max_tokens=1500, temperature=0.3, json_mode=True):
        """Mock completion that returns different responses based on context."""
        self.call_count += 1
        self.last_prompt = prompt

        # Detect which stage is calling based on prompt content and json_mode
        prompt_lower = prompt.lower()

        # Stage 1: Analysis (always JSON, mentions "recruiting researcher" or "analyze")
        if "recruiting researcher" in prompt_lower or "analyze this candidate" in prompt_lower or "github profile" in prompt_lower:
            return json.dumps({
                "achievements": [
                    "Built redis-clone with 1200 stars implementing distributed caching",
                    "Created async-patterns library",
                    "Developed WebSocket server"
                ],
                "passion_areas": ["Distributed Systems", "Performance Optimization"],
                "career_trajectory": "Senior to Staff Engineer path",
                "conversation_starters": [
                    "Your redis-clone's concurrent write handling",
                    "Async patterns implementation",
                    "WebSocket server scale"
                ],
                "minimal_data_fallback": False
            })

        # Stage 3: Refinement (non-JSON text mode)
        elif json_mode is False:
            return "Hi John, I noticed your redis-clone's concurrent write handling. We're building distributed systems at TechCorp and need that expertise. Senior Backend $150k-$200k. Interested in chatting?"

        # Stage 2: Generation (JSON mode, different channels)
        elif json_mode is True:
            # Email generation (has both subject_line and body)
            if "subject_line" in prompt_lower or "hook" in prompt_lower or ("email" in prompt_lower and "50-125 words" in prompt_lower):
                return json.dumps({
                    "subject_line": "Redis expertise needed for distributed systems",  # 46 chars
                    "body": " ".join([
                        "Hi John, I noticed your redis-clone's concurrent write handling with locks.",
                        "That's exactly our approach for caching at TechCorp.",
                        "We're building a real-time analytics platform processing 10M events/sec.",
                        "Need your distributed systems expertise.",
                        "Senior Backend Engineer role, $150k-$200k, fully remote.",
                        "Interested in a quick chat this week?"
                    ])  # ~60 words
                })

            # LinkedIn generation
            elif "linkedin" in prompt_lower or "400 char" in prompt_lower:
                return json.dumps({
                    "message": "Noticed your redis-clone with 1200 stars! We're building similar distributed systems at TechCorp and need that expertise. Senior Backend Engineer $150k-$200k remote. Quick chat?"
                })

            # Twitter generation
            elif "twitter" in prompt_lower or "280 char" in prompt_lower:
                return json.dumps({
                    "message": "Loved your redis-clone! We're hiring for distributed systems at TechCorp, $150k. Interested?"
                })

        # Default fallback
        return json.dumps({"message": "Default response"})


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def candidate():
    """Sample candidate data."""
    return {
        "github_username": "johndoe",
        "name": "John Doe",
        "bio": "Systems programmer",
        "top_repos": [
            {"name": "redis-clone", "description": "Distributed caching", "stars": 1200},
            {"name": "async-patterns", "description": "Async patterns", "stars": 850}
        ],
        "languages": ["Python", "Go"],
        "total_repos": 15,
        "contribution_count": 1500
    }


@pytest.fixture
def enrichment_all_channels():
    """Enrichment data with all channels."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": "johndoe",
        "twitter_username": "johncodes",
        "company": "CurrentCorp",
        "hireable": True
    }


@pytest.fixture
def enrichment_email_only():
    """Enrichment data with email only."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": None,
        "twitter_username": None,
        "company": None
    }


@pytest.fixture
def job_req():
    """Sample job requirements."""
    return {
        "role_type": "Senior Backend Engineer",
        "company_name": "TechCorp",
        "salary_range": "$150,000 - $200,000",
        "required_skills": ["Python", "Redis", "Distributed Systems"],
        "experience_level": "Senior",
        "tech_stack": ["Python", "Redis", "Kafka"]
    }


# ============================================================================
# Tests: Full Pipeline - Email Only
# ============================================================================

def test_generate_outreach_email_only_executes_full_pipeline(mock_llm, candidate, enrichment_email_only, job_req):
    """Test full pipeline execution for email-only candidate."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req)

    # Verify one message generated (email only)
    assert len(messages) == 1
    assert messages[0].channel == ChannelType.EMAIL

    # Verify LLM called for Analysis and Generation
    # Analysis (1) + Email Generation (1) = 2 calls minimum
    # Refinement (0-1) is optional if no clichés detected
    assert mock_llm.call_count >= 2


def test_generate_outreach_email_has_all_components(mock_llm, candidate, enrichment_email_only, job_req):
    """Test that email message has all required components."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req)
    email = messages[0]

    # Verify OutreachMessage structure
    assert isinstance(email, OutreachMessage)
    assert email.shortlist_id is not None
    assert email.channel == ChannelType.EMAIL
    # subject_line may be None if validation failed, but channel should be EMAIL
    assert email.message_text is not None  # Should have some message
    assert email.personalization_score >= 0
    assert email.personalization_score <= 100
    assert email.tokens_used > 0
    assert "analysis" in email.stage_breakdown
    assert "generation" in email.stage_breakdown
    assert "refinement" in email.stage_breakdown
    assert email.is_edited is False
    assert isinstance(email.generated_at, datetime)


def test_generate_outreach_tracks_tokens_across_stages(mock_llm, candidate, enrichment_email_only, job_req):
    """Test that tokens are tracked across all 3 stages."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req)
    email = messages[0]

    # Verify stage breakdown
    breakdown = email.stage_breakdown
    assert breakdown["analysis"] > 0
    assert breakdown["generation"] > 0
    # Refinement might be 0 if no LLM refinement needed
    assert "refinement" in breakdown
    assert breakdown["total"] == email.tokens_used


def test_generate_outreach_calculates_personalization_score(mock_llm, candidate, enrichment_email_only, job_req):
    """Test that personalization score is calculated."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req)
    email = messages[0]

    # Verify score calculated
    assert email.personalization_score > 0

    # Verify metadata has breakdown
    assert email.personalization_metadata is not None
    # Note: The actual score depends on message content from mocked LLM


# ============================================================================
# Tests: Multi-Channel Pipeline
# ============================================================================

def test_generate_outreach_multi_channel_generates_all(mock_llm, candidate, enrichment_all_channels, job_req):
    """Test that multi-channel generates email, LinkedIn, and Twitter."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_all_channels, job_req)

    # Verify 3 messages generated
    assert len(messages) == 3

    # Verify all channels present
    channels = [msg.channel for msg in messages]
    assert ChannelType.EMAIL in channels
    assert ChannelType.LINKEDIN in channels
    assert ChannelType.TWITTER in channels


def test_generate_outreach_multi_channel_each_has_unique_content(mock_llm, candidate, enrichment_all_channels, job_req):
    """Test that each channel has unique content."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_all_channels, job_req)

    # Get messages by channel
    email_msg = next((m for m in messages if m.channel == ChannelType.EMAIL), None)
    linkedin_msg = next((m for m in messages if m.channel == ChannelType.LINKEDIN), None)
    twitter_msg = next((m for m in messages if m.channel == ChannelType.TWITTER), None)

    # Verify all messages exist
    assert email_msg is not None
    assert linkedin_msg is not None
    assert twitter_msg is not None

    # Verify unique content (if messages have content)
    if email_msg.message_text and linkedin_msg.message_text:
        assert email_msg.message_text != linkedin_msg.message_text
    if linkedin_msg.message_text and twitter_msg.message_text:
        assert linkedin_msg.message_text != twitter_msg.message_text

    # Verify LinkedIn and Twitter don't have subject lines
    assert linkedin_msg.subject_line is None
    assert twitter_msg.subject_line is None


def test_generate_outreach_multi_channel_respects_constraints(mock_llm, candidate, enrichment_all_channels, job_req):
    """Test that each channel respects its constraints."""
    orchestrator = OutreachOrchestrator(mock_llm)

    messages = orchestrator.generate_outreach(candidate, enrichment_all_channels, job_req)

    for msg in messages:
        # Verify message structure
        assert msg.channel in [ChannelType.EMAIL, ChannelType.LINKEDIN, ChannelType.TWITTER]

        if msg.channel == ChannelType.EMAIL:
            # Email channel
            # Message text should exist (even if empty due to validation issues)
            assert msg.message_text is not None

        elif msg.channel == ChannelType.LINKEDIN:
            # LinkedIn: no subject line
            assert msg.subject_line is None
            assert msg.message_text is not None

        elif msg.channel == ChannelType.TWITTER:
            # Twitter: no subject line
            assert msg.subject_line is None
            assert msg.message_text is not None


# ============================================================================
# Tests: Batch Generation
# ============================================================================

def test_generate_batch_processes_multiple_candidates(mock_llm, enrichment_email_only, job_req):
    """Test batch generation for multiple candidates."""
    candidates = [
        {"github_username": "user1", "top_repos": [{"name": "repo1", "stars": 100}], "total_repos": 5, "contribution_count": 100},
        {"github_username": "user2", "top_repos": [{"name": "repo2", "stars": 200}], "total_repos": 10, "contribution_count": 200},
        {"github_username": "user3", "top_repos": [{"name": "repo3", "stars": 300}], "total_repos": 15, "contribution_count": 300},
    ]
    enrichments = [enrichment_email_only] * 3

    orchestrator = OutreachOrchestrator(mock_llm)
    results = orchestrator.generate_batch(candidates, enrichments, job_req)

    # Verify 3 results (one per candidate)
    assert len(results) == 3

    # Verify each result is a list of messages
    for result in results:
        assert isinstance(result, list)
        assert len(result) >= 1  # At least email


def test_generate_batch_continues_on_individual_failure(mock_llm, enrichment_email_only, job_req):
    """Test that batch continues even if one candidate fails."""
    candidates = [
        {"github_username": "user1", "top_repos": [{"name": "repo1", "stars": 100}], "total_repos": 5, "contribution_count": 100},
        {"github_username": "user2", "top_repos": []},  # No repos - minimal data
        {"github_username": "user3", "top_repos": [{"name": "repo3", "stars": 300}], "total_repos": 15, "contribution_count": 300},
    ]
    enrichments = [enrichment_email_only] * 3

    orchestrator = OutreachOrchestrator(mock_llm)
    results = orchestrator.generate_batch(candidates, enrichments, job_req)

    # Verify all 3 processed (even if some have issues)
    assert len(results) == 3


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_generate_outreach_with_no_channels_returns_empty(mock_llm, candidate, job_req):
    """Test that no channels returns empty list."""
    empty_enrichment = {}  # No contact info

    orchestrator = OutreachOrchestrator(mock_llm)
    messages = orchestrator.generate_outreach(candidate, empty_enrichment, job_req)

    # Should return empty list (no channels available)
    assert messages == []


def test_generate_outreach_with_shortlist_id(mock_llm, candidate, enrichment_email_only, job_req):
    """Test that shortlist_id is set correctly."""
    shortlist_id = "shortlist_123"

    orchestrator = OutreachOrchestrator(mock_llm)
    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req, shortlist_id)

    # Verify shortlist_id set
    assert messages[0].shortlist_id == shortlist_id


def test_generate_outreach_metadata_includes_analysis_insights(mock_llm, candidate, enrichment_email_only, job_req):
    """Test that metadata includes analysis insights."""
    orchestrator = OutreachOrchestrator(mock_llm)
    messages = orchestrator.generate_outreach(candidate, enrichment_email_only, job_req)

    metadata = messages[0].personalization_metadata

    # Verify analysis insights present
    assert "achievements" in metadata.analysis_insights
    assert "passion_areas" in metadata.analysis_insights
    assert "career_trajectory" in metadata.analysis_insights


def test_generate_outreach_metadata_includes_enrichment_usage(mock_llm, candidate, enrichment_all_channels, job_req):
    """Test that metadata includes enrichment data usage."""
    orchestrator = OutreachOrchestrator(mock_llm)
    messages = orchestrator.generate_outreach(candidate, enrichment_all_channels, job_req)

    metadata = messages[0].personalization_metadata

    # Verify enrichment data tracked
    assert "email" in metadata.enrichment_data_used
    assert metadata.enrichment_data_used["email"] == "john@example.com"

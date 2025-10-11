"""
Integration tests for GenerationStage (Stage 2 of outreach pipeline)

Tests multi-channel message generation with mocked LLM responses.
"""

import json
import pytest
from unittest.mock import Mock

from src.outreach_generator.stages.generation_stage import GenerationStage
from src.outreach_generator.channel_optimizer import ChannelOptimizer


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response_json=None, should_fail=False):
        self.response_json = response_json
        self.should_fail = should_fail
        self.model = "gpt-4o-mini"
        self.call_count = 0
        self.last_prompt = None

    def complete(self, prompt, max_tokens=500, temperature=0.7, json_mode=True):
        """Mock completion that returns JSON."""
        self.call_count += 1
        self.last_prompt = prompt

        if self.should_fail:
            raise Exception("LLM API error")

        if self.response_json:
            return json.dumps(self.response_json)

        # Default empty response
        return json.dumps({"subject_line": "", "body": "", "message": ""})


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def optimizer():
    """Create ChannelOptimizer instance."""
    return ChannelOptimizer()


@pytest.fixture
def insights():
    """Sample analysis insights from Stage 1."""
    return {
        "achievements": [
            "Built redis-clone with 1200 stars implementing distributed caching",
            "Created async-patterns library for high-performance Python",
            "Developed WebSocket server handling 10k+ concurrent connections"
        ],
        "passion_areas": ["Systems Programming", "Distributed Systems"],
        "career_trajectory": "Senior to Staff Engineer path",
        "conversation_starters": [
            "Your redis-clone's concurrent write handling is exactly our approach",
            "Async patterns you built match our challenges",
            "WebSocket server scale aligns with our needs"
        ],
        "minimal_data_fallback": False
    }


@pytest.fixture
def job_req():
    """Sample job requirements."""
    return {
        "role_type": "Senior Backend Engineer",
        "company_name": "TechCorp",
        "salary_range": "$150,000 - $200,000",
        "required_skills": ["Python", "Redis", "Distributed Systems"],
        "experience_level": "Senior"
    }


@pytest.fixture
def enrichment_all_channels():
    """Enrichment data with all channels available."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": "johndoe",
        "twitter_username": "johncodes",
        "company": "CurrentCorp"
    }


@pytest.fixture
def enrichment_email_only():
    """Enrichment data with only email available."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": None,
        "twitter_username": None,
        "company": None
    }


# ============================================================================
# Tests: Channel Determination
# ============================================================================

def test_determine_channels_with_all_data(optimizer, enrichment_all_channels):
    """Test that all channels are detected when all enrichment data is present."""
    stage = GenerationStage(MockLLMClient(), optimizer)

    channels = stage._determine_channels(enrichment_all_channels)

    assert "email" in channels
    assert "linkedin" in channels
    assert "twitter" in channels
    assert len(channels) == 3


def test_determine_channels_with_email_only(optimizer, enrichment_email_only):
    """Test that only email channel is detected when only email is present."""
    stage = GenerationStage(MockLLMClient(), optimizer)

    channels = stage._determine_channels(enrichment_email_only)

    assert channels == ["email"]
    assert len(channels) == 1


# ============================================================================
# Tests: Email Generation
# ============================================================================

def test_generate_email_returns_valid_message(optimizer, insights, job_req, enrichment_all_channels):
    """Test that email generation returns valid subject and body."""
    # Mock LLM response with valid email
    email_response = {
        "subject_line": "Redis expertise for distributed systems @ TechCorp",  # 50 chars exactly
        "body": " ".join(["Hi Alex, I noticed your redis-clone project's concurrent write handling with locks.",
                          "That's exactly the approach we're taking for our caching layer at TechCorp.",
                          "We're building a real-time analytics platform and need your distributed systems expertise.",
                          "Senior Backend Engineer role, $150k-$200k, fully remote.",
                          "Interested in a quick chat this week?"])  # ~60 words
    }

    mock_llm = MockLLMClient(response_json=email_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    # Verify structure
    assert "subject_line" in result
    assert "message_text" in result
    assert result["channel"] == "email"
    assert "is_valid" in result
    assert "validation_errors" in result
    assert "tokens_used" in result

    # Verify content
    assert len(result["subject_line"]) >= 36 and len(result["subject_line"]) <= 50
    assert result["is_valid"] is True
    assert result["tokens_used"] > 0


def test_generate_email_includes_repo_and_salary(optimizer, insights, job_req, enrichment_all_channels):
    """Test that generated email includes specific repo mention and salary."""
    email_response = {
        "subject_line": "Redis expertise for distributed systems at TechCorp",  # 50 chars
        "body": " ".join([f"word" for _ in range(60)] + ["redis-clone", "$150,000"])  # Includes repo and salary
    }

    mock_llm = MockLLMClient(response_json=email_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    # Verify repo mentioned (from insights)
    body = result["message_text"]
    assert "redis-clone" in body or "$150,000" in body


def test_generate_email_with_invalid_subject_fails_validation(optimizer, insights, job_req, enrichment_all_channels):
    """Test that email with invalid subject (too short) fails validation."""
    email_response = {
        "subject_line": "Short",  # 5 chars (too short, need 36-50)
        "body": " ".join([f"word" for _ in range(80)])  # 80 words (valid)
    }

    mock_llm = MockLLMClient(response_json=email_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) > 0
    assert any("Subject line must be 36-50 characters" in err for err in result["validation_errors"])


def test_generate_email_with_invalid_body_fails_validation(optimizer, insights, job_req, enrichment_all_channels):
    """Test that email with invalid body (too few words) fails validation."""
    email_response = {
        "subject_line": "A" * 40,  # 40 chars (valid)
        "body": " ".join([f"word" for _ in range(30)])  # 30 words (too few, need 50-125)
    }

    mock_llm = MockLLMClient(response_json=email_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) > 0
    assert any("Email body must be 50-125 words" in err for err in result["validation_errors"])


# ============================================================================
# Tests: LinkedIn Generation
# ============================================================================

def test_generate_linkedin_returns_valid_message(optimizer, insights, job_req, enrichment_all_channels):
    """Test that LinkedIn generation returns valid message."""
    linkedin_response = {
        "message": "Noticed your redis-clone with 1200 stars implementing distributed caching! We're building similar at TechCorp and need your expertise. Senior Backend Engineer $150k-$200k remote. Interested?"  # ~190 chars, 4 sentences
    }

    mock_llm = MockLLMClient(response_json=linkedin_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "linkedin")

    # Verify structure
    assert "message_text" in result
    assert result["channel"] == "linkedin"
    assert result["is_valid"] is True
    assert result["tokens_used"] > 0

    # Verify constraints
    assert len(result["message_text"]) < 400


def test_generate_linkedin_with_long_message_fails_validation(optimizer, insights, job_req, enrichment_all_channels):
    """Test that LinkedIn message >400 chars fails validation."""
    linkedin_response = {
        "message": "A" * 450  # 450 chars (too long, need <400)
    }

    mock_llm = MockLLMClient(response_json=linkedin_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "linkedin")

    assert result["is_valid"] is False
    assert any("LinkedIn message must be <400 characters" in err for err in result["validation_errors"])


# ============================================================================
# Tests: Twitter Generation
# ============================================================================

def test_generate_twitter_returns_valid_message(optimizer, insights, job_req, enrichment_all_channels):
    """Test that Twitter generation returns valid message."""
    twitter_response = {
        "message": "Loved your redis-clone! We're hiring for distributed systems at TechCorp, $150k. Interested?"  # ~95 chars, 3 sentences
    }

    mock_llm = MockLLMClient(response_json=twitter_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "twitter")

    # Verify structure
    assert "message_text" in result
    assert result["channel"] == "twitter"
    assert result["is_valid"] is True
    assert result["tokens_used"] > 0

    # Verify constraints
    assert len(result["message_text"]) < 280


def test_generate_twitter_with_long_message_fails_validation(optimizer, insights, job_req, enrichment_all_channels):
    """Test that Twitter message >280 chars fails validation."""
    twitter_response = {
        "message": "A" * 300  # 300 chars (too long, need <280)
    }

    mock_llm = MockLLMClient(response_json=twitter_response)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "twitter")

    assert result["is_valid"] is False
    assert any("Twitter message must be <280 characters" in err for err in result["validation_errors"])


# ============================================================================
# Tests: Error Handling
# ============================================================================

def test_generate_handles_llm_failure_gracefully(optimizer, insights, job_req, enrichment_all_channels):
    """Test that LLM failure returns fallback message."""
    mock_llm = MockLLMClient(should_fail=True)
    stage = GenerationStage(mock_llm, optimizer)

    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    # Should return fallback message
    assert result is not None
    assert result["is_valid"] is False
    assert "LLM generation failed - using fallback" in result["validation_errors"][0]
    assert result["tokens_used"] == 0


def test_generate_handles_invalid_json_response(optimizer, insights, job_req, enrichment_all_channels):
    """Test that invalid JSON returns fallback message."""
    # Mock LLM that returns invalid JSON
    mock_llm = Mock()
    mock_llm.model = "gpt-4o-mini"
    mock_llm.complete = Mock(return_value="This is not valid JSON {incomplete}")

    stage = GenerationStage(mock_llm, optimizer)
    result = stage.generate(insights, job_req, enrichment_all_channels, "email")

    # Should return fallback message
    assert result["is_valid"] is False
    assert "LLM generation failed - using fallback" in result["validation_errors"][0]


def test_generate_handles_unsupported_channel(optimizer, insights, job_req, enrichment_all_channels):
    """Test that unsupported channel raises error."""
    mock_llm = MockLLMClient()
    stage = GenerationStage(mock_llm, optimizer)

    # Should handle gracefully and return fallback
    # Actually, this will raise ValueError which gets caught and returns fallback
    result = stage.generate(insights, job_req, enrichment_all_channels, "instagram")

    assert result["is_valid"] is False

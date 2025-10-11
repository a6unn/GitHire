"""
Integration tests for PersonalizationScorer

Tests personalization scoring based on repo mentions, technical details,
enrichment data usage, and unique insights.
"""

import pytest
from src.outreach_generator.personalization_scorer import PersonalizationScorer


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def scorer():
    """Create PersonalizationScorer instance."""
    return PersonalizationScorer()


@pytest.fixture
def candidate():
    """Sample candidate data."""
    return {
        "github_username": "johndoe",
        "name": "John Doe",
        "top_repos": [
            {"name": "redis-clone", "description": "Distributed caching system", "stars": 1200},
            {"name": "async-patterns", "description": "Async patterns library", "stars": 850},
            {"name": "websocket-server", "description": "Real-time WebSocket server", "stars": 600}
        ]
    }


@pytest.fixture
def enrichment():
    """Sample enrichment data with all fields."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": "johndoe",
        "twitter_username": "johncodes",
        "blog_url": "https://john.dev",
        "company": "CurrentCorp"
    }


@pytest.fixture
def minimal_enrichment():
    """Minimal enrichment data (email only)."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": None,
        "twitter_username": None,
        "blog_url": None,
        "company": None
    }


# ============================================================================
# Tests: Repo Mention Scoring
# ============================================================================

def test_score_with_repo_mention_gets_30_points(scorer, candidate, enrichment):
    """Test that message with repo mention gets +30 points."""
    message = "Hi John, I noticed your redis-clone project with 1200 stars."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["repo_mention"] is True
    assert score >= 30


def test_score_without_repo_mention_gets_0_repo_points(scorer, candidate, enrichment):
    """Test that message without repo mention gets 0 repo points."""
    message = "Hi John, I saw your GitHub profile and was impressed."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["repo_mention"] is False


def test_score_with_multiple_repo_mentions(scorer, candidate, enrichment):
    """Test that multiple repo mentions still count as one (30 points max)."""
    message = "Hi John, your redis-clone and async-patterns projects are impressive!"

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["repo_mention"] is True
    # Should still be counted once for scoring purposes


# ============================================================================
# Tests: Technical Detail Scoring
# ============================================================================

def test_score_with_technical_detail_gets_30_points(scorer, candidate, enrichment):
    """Test that message with technical detail gets +30 points."""
    message = "Your redis-clone's concurrent write handling with locks is exactly our approach."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["technical_detail"] is True
    assert score >= 30


def test_score_with_specific_technology_mention(scorer, candidate, enrichment):
    """Test that specific technology mentions count as technical detail."""
    message = "We're using Redis and Kafka for our distributed system."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["technical_detail"] is True


def test_score_with_architecture_terms(scorer, candidate, enrichment):
    """Test that architecture terms count as technical detail."""
    message = "Your distributed microservices architecture with event-driven design is impressive."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["technical_detail"] is True


def test_score_with_performance_metrics(scorer, candidate, enrichment):
    """Test that performance metrics count as technical detail."""
    message = "Your WebSocket server handling 10k+ connections is exactly what we need."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["technical_detail"] is True


def test_score_without_technical_detail_gets_0_tech_points(scorer, candidate, enrichment):
    """Test that generic message gets 0 technical points."""
    message = "Hi John, we have a great opportunity for you."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["technical_detail"] is False


# ============================================================================
# Tests: Unique Insight Scoring
# ============================================================================

def test_score_with_company_mention_gets_20_points(scorer, candidate, enrichment):
    """Test that mentioning current company gets +20 points."""
    message = "Hi John, I see you're at CurrentCorp. We're building something similar at TechCorp."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["unique_insight"] is True
    assert score >= 20


def test_score_with_blog_mention_gets_20_points(scorer, candidate, enrichment):
    """Test that mentioning blog gets +20 points."""
    message = "Hi John, I read your post on john.dev about distributed systems."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["unique_insight"] is True


def test_score_without_unique_insight_gets_0_insight_points(scorer, candidate, enrichment):
    """Test that message without unique insights gets 0 points."""
    message = "Hi John, your GitHub work is impressive."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["unique_insight"] is False


# ============================================================================
# Tests: Enrichment Usage Scoring
# ============================================================================

def test_score_with_enrichment_data_gets_20_points(scorer, candidate, enrichment):
    """Test that having enrichment data gets +20 points."""
    message = "Hi John, any generic message."

    score, breakdown = scorer.score(message, candidate, enrichment)

    assert breakdown["enrichment_usage"] is True
    assert score >= 20


def test_score_with_minimal_enrichment_gets_20_points(scorer, candidate, minimal_enrichment):
    """Test that even minimal enrichment (email only) gets +20 points."""
    message = "Hi John, any message."

    score, breakdown = scorer.score(message, candidate, minimal_enrichment)

    assert breakdown["enrichment_usage"] is True


def test_score_with_no_enrichment_gets_0_enrichment_points(scorer, candidate):
    """Test that no enrichment data gets 0 points."""
    empty_enrichment = {}
    message = "Hi John, your work is great."

    score, breakdown = scorer.score(message, candidate, empty_enrichment)

    assert breakdown["enrichment_usage"] is False


# ============================================================================
# Tests: Full Personalization Scoring
# ============================================================================

def test_score_fully_personalized_message_gets_100_points(scorer, candidate, enrichment):
    """Test that fully personalized message gets 100 points."""
    message = "Hi John, I noticed your redis-clone's concurrent write handling while you were at CurrentCorp. Your distributed architecture with async patterns is exactly what we need at TechCorp. $150k-$200k. Interested?"

    score, breakdown = scorer.score(message, candidate, enrichment)

    # Should have all components
    assert breakdown["repo_mention"] is True  # redis-clone mentioned
    assert breakdown["technical_detail"] is True  # concurrent, distributed, async mentioned
    assert breakdown["unique_insight"] is True  # CurrentCorp mentioned
    assert breakdown["enrichment_usage"] is True  # has enrichment data
    assert score == 100
    assert breakdown["total_points"] == 100


def test_score_generic_message_gets_low_score(scorer, candidate, minimal_enrichment):
    """Test that generic message gets low score (<40)."""
    message = "Hi John, we have an opportunity for you at our company. Interested in learning more?"

    score, breakdown = scorer.score(message, candidate, minimal_enrichment)

    # Should only get enrichment_usage points
    assert breakdown["repo_mention"] is False
    assert breakdown["technical_detail"] is False
    assert breakdown["unique_insight"] is False
    assert breakdown["enrichment_usage"] is True  # minimal enrichment present
    assert score == 20  # Only enrichment points
    assert score < 40


def test_score_moderately_personalized_message(scorer, candidate, enrichment):
    """Test moderately personalized message (repo mention + enrichment)."""
    message = "Hi John, I saw your redis-clone project. We're hiring at TechCorp."

    score, breakdown = scorer.score(message, candidate, enrichment)

    # Should have repo_mention and enrichment_usage
    assert breakdown["repo_mention"] is True
    assert breakdown["enrichment_usage"] is True
    assert score >= 50  # At least 30 + 20 = 50 points


# ============================================================================
# Tests: Breakdown Structure
# ============================================================================

def test_score_returns_correct_breakdown_structure(scorer, candidate, enrichment):
    """Test that score returns properly structured breakdown."""
    message = "Hi John, your redis-clone's async handling is impressive!"

    score, breakdown = scorer.score(message, candidate, enrichment)

    # Verify all expected keys present
    assert "repo_mention" in breakdown
    assert "technical_detail" in breakdown
    assert "unique_insight" in breakdown
    assert "enrichment_usage" in breakdown
    assert "total_points" in breakdown
    assert "max_points" in breakdown

    # Verify types
    assert isinstance(breakdown["repo_mention"], bool)
    assert isinstance(breakdown["technical_detail"], bool)
    assert isinstance(breakdown["unique_insight"], bool)
    assert isinstance(breakdown["enrichment_usage"], bool)
    assert isinstance(breakdown["total_points"], int)
    assert breakdown["max_points"] == 100

    # Verify total_points matches score
    assert breakdown["total_points"] == int(score)


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_score_empty_message(scorer, candidate, enrichment):
    """Test scoring empty message."""
    message = ""

    score, breakdown = scorer.score(message, candidate, enrichment)

    # Should only get enrichment_usage (data is present)
    assert score == 20
    assert breakdown["enrichment_usage"] is True
    assert breakdown["repo_mention"] is False
    assert breakdown["technical_detail"] is False


def test_score_with_no_repos(scorer, enrichment):
    """Test scoring when candidate has no repos."""
    candidate_no_repos = {
        "github_username": "newdev",
        "top_repos": []
    }
    message = "Hi there, we're hiring at TechCorp for a distributed systems role."

    score, breakdown = scorer.score(message, candidate_no_repos, enrichment)

    # Can't get repo_mention points (no repos to mention)
    assert breakdown["repo_mention"] is False
    # But can still get technical_detail and enrichment points
    assert breakdown["technical_detail"] is True  # "distributed systems"
    assert breakdown["enrichment_usage"] is True

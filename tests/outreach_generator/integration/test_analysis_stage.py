"""
Integration tests for AnalysisStage (Stage 1 of outreach pipeline)

Tests deep GitHub profile analysis with mocked LLM responses.
"""

import json
import pytest
from unittest.mock import Mock, MagicMock

from src.outreach_generator.stages.analysis_stage import AnalysisStage


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response_json=None, should_fail=False):
        self.response_json = response_json
        self.should_fail = should_fail
        self.model = "gpt-4o-mini"  # Has model attribute like OpenAI client
        self.call_count = 0
        self.last_prompt = None

    def complete(self, prompt, max_tokens=1500, temperature=0.3, json_mode=True):
        """Mock completion that returns JSON."""
        self.call_count += 1
        self.last_prompt = prompt

        if self.should_fail:
            raise Exception("LLM API error")

        if self.response_json:
            return json.dumps(self.response_json)

        # Default response
        return json.dumps({
            "achievements": [
                "Built system with 1k stars",
                "Contributed to open source",
                "Technical leadership"
            ],
            "passion_areas": ["Systems Programming", "Distributed Systems"],
            "career_trajectory": "Senior to Staff Engineer path",
            "conversation_starters": [
                "Your distributed caching work",
                "Async patterns implementation",
                "Performance optimization expertise"
            ],
            "minimal_data_fallback": False
        })


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def rich_candidate():
    """Candidate with rich GitHub data."""
    return {
        "github_username": "johndoe",
        "name": "John Doe",
        "bio": "Systems programmer passionate about distributed systems",
        "location": "San Francisco, CA",
        "top_repos": [
            {
                "name": "redis-clone",
                "description": "Distributed caching system with concurrent write handling",
                "language": "Python",
                "stars": 1200
            },
            {
                "name": "async-patterns",
                "description": "Async/await patterns for high-performance Python",
                "language": "Python",
                "stars": 850
            },
            {
                "name": "websocket-server",
                "description": "Real-time WebSocket server handling 10k+ connections",
                "language": "Python",
                "stars": 600
            }
        ],
        "languages": ["Python", "Go", "Rust"],
        "total_repos": 15,
        "contribution_count": 1500
    }


@pytest.fixture
def minimal_candidate():
    """Candidate with minimal GitHub data."""
    return {
        "github_username": "newdev",
        "name": "New Developer",
        "bio": "Learning to code",
        "location": "New York, NY",
        "top_repos": [
            {
                "name": "hello-world",
                "description": "My first repository",
                "language": "Python",
                "stars": 0
            }
        ],
        "languages": ["Python"],
        "total_repos": 1,
        "contribution_count": 10
    }


@pytest.fixture
def enrichment_data():
    """Sample enrichment data from Module 010."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": "johndoe",
        "twitter_username": "johncodes",
        "blog_url": "https://john.dev",
        "company": "TechCorp",
        "hireable": True
    }


@pytest.fixture
def minimal_enrichment():
    """Minimal enrichment data."""
    return {
        "primary_email": "new@example.com",
        "linkedin_username": None,
        "twitter_username": None,
        "blog_url": None,
        "company": None,
        "hireable": None
    }


@pytest.fixture
def job_req():
    """Sample job requirements."""
    return {
        "role_type": "Senior Backend Engineer",
        "required_skills": ["Python", "Redis", "Distributed Systems"],
        "experience_level": "Senior",
        "company_name": "TechCorp",
        "salary_range": "$150,000 - $200,000",
        "tech_stack": ["Python", "Redis", "Kafka", "Kubernetes"]
    }


# ============================================================================
# Tests: Analysis with Rich Data
# ============================================================================

def test_analysis_with_rich_data_returns_structured_insights(rich_candidate, enrichment_data, job_req):
    """Test analysis with rich data returns all required fields."""
    # Setup mock LLM
    mock_response = {
        "achievements": [
            "Built redis-clone with 1.2k stars implementing distributed caching",
            "Created async-patterns library with 850 stars for high-performance Python",
            "Developed WebSocket server handling 10k+ concurrent connections"
        ],
        "passion_areas": ["Systems Programming", "Distributed Systems", "Performance Optimization"],
        "career_trajectory": "Senior to Staff Engineer path",
        "conversation_starters": [
            "Your redis-clone's concurrent write handling is exactly our approach",
            "Async patterns you built match our 10M+ events/sec challenges",
            "WebSocket server scale aligns with our real-time platform needs"
        ],
        "minimal_data_fallback": False
    }

    mock_llm = MockLLMClient(response_json=mock_response)
    stage = AnalysisStage(mock_llm)

    # Execute analysis
    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Verify structure
    assert "achievements" in insights
    assert "passion_areas" in insights
    assert "career_trajectory" in insights
    assert "conversation_starters" in insights
    assert "minimal_data_fallback" in insights
    assert "tokens_used" in insights

    # Verify content
    assert len(insights["achievements"]) == 3
    assert len(insights["conversation_starters"]) == 3
    assert insights["minimal_data_fallback"] is False
    assert insights["tokens_used"] > 0


def test_analysis_calls_llm_with_candidate_context(rich_candidate, enrichment_data, job_req):
    """Test that analysis includes candidate context in prompt."""
    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Verify LLM was called
    assert mock_llm.call_count == 1

    # Verify prompt contains candidate data
    prompt = mock_llm.last_prompt
    assert "johndoe" in prompt
    assert "redis-clone" in prompt
    assert "TechCorp" in prompt  # From job_req
    assert "Senior Backend Engineer" in prompt


def test_analysis_includes_enrichment_data_in_prompt(rich_candidate, enrichment_data, job_req):
    """Test that enrichment data is included in analysis prompt."""
    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    prompt = mock_llm.last_prompt

    # Verify enrichment data in prompt
    assert "john@example.com" in prompt or "Email:" in prompt
    assert "johndoe" in prompt  # LinkedIn username
    assert "johncodes" in prompt or "Twitter:" in prompt
    assert "john.dev" in prompt or "Blog:" in prompt
    assert "TechCorp" in prompt  # Company


# ============================================================================
# Tests: Analysis with Minimal Data
# ============================================================================

def test_analysis_with_minimal_data_uses_fallback_prompt(minimal_candidate, minimal_enrichment, job_req):
    """Test that minimal data scenario uses fallback prompt."""
    mock_response = {
        "achievements": [
            "Early career developer with GitHub presence",
            "Learning Python fundamentals",
            "Shows initiative in software development"
        ],
        "passion_areas": ["Python", "Software Development"],
        "career_trajectory": "Early career - great fit for learning opportunities",
        "conversation_starters": [
            "Your interest in Python aligns with our tech stack",
            "We offer mentorship for growing developers",
            "Great opportunity to level up your skills at TechCorp"
        ],
        "minimal_data_fallback": True
    }

    mock_llm = MockLLMClient(response_json=mock_response)
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(minimal_candidate, minimal_enrichment, job_req)

    # Verify fallback flag is set
    assert insights["minimal_data_fallback"] is True

    # Verify insights focus on potential rather than achievements
    assert any("early" in a.lower() or "learning" in a.lower() or "initiative" in a.lower()
               for a in insights["achievements"])


def test_analysis_minimal_data_has_less_than_3_repos(minimal_candidate, minimal_enrichment, job_req):
    """Test that candidates with < 3 repos trigger minimal data path."""
    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(minimal_candidate, minimal_enrichment, job_req)

    # Should use fallback for minimal data
    # Verify by checking the prompt contains fallback indicators
    prompt = mock_llm.last_prompt
    assert "minimal" in prompt.lower() or "potential" in prompt.lower()


# ============================================================================
# Tests: Error Handling
# ============================================================================

def test_analysis_handles_llm_failure_gracefully(rich_candidate, enrichment_data, job_req):
    """Test that LLM failure returns fallback insights."""
    mock_llm = MockLLMClient(should_fail=True)
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Should return fallback insights
    assert insights is not None
    assert "achievements" in insights
    assert insights["minimal_data_fallback"] is True
    assert insights["tokens_used"] == 0  # No tokens used in fallback


def test_analysis_handles_invalid_json_response(rich_candidate, enrichment_data, job_req):
    """Test that invalid JSON returns fallback insights."""
    # Mock LLM that returns invalid JSON
    mock_llm = Mock()
    mock_llm.model = "gpt-4o-mini"
    mock_llm.complete = Mock(return_value="This is not valid JSON {incomplete}")

    stage = AnalysisStage(mock_llm)
    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Should return fallback insights
    assert insights["minimal_data_fallback"] is True


def test_analysis_validates_llm_output_structure(rich_candidate, enrichment_data, job_req):
    """Test that incomplete LLM output is validated and filled."""
    # Mock LLM with incomplete response
    incomplete_response = {
        "achievements": ["Only one achievement"],
        # Missing passion_areas
        "career_trajectory": "Unknown",
        # Missing conversation_starters
    }

    mock_llm = MockLLMClient(response_json=incomplete_response)
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Verify validation fills in missing fields
    assert len(insights["achievements"]) >= 1
    assert len(insights["passion_areas"]) >= 1  # Should be filled with defaults
    assert len(insights["conversation_starters"]) >= 1  # Should be filled with defaults


# ============================================================================
# Tests: Token Tracking
# ============================================================================

def test_analysis_tracks_tokens_used(rich_candidate, enrichment_data, job_req):
    """Test that tokens used are tracked."""
    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Verify tokens_used is present and > 0
    assert "tokens_used" in insights
    assert insights["tokens_used"] > 0
    assert isinstance(insights["tokens_used"], int)


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_analysis_with_no_enrichment_data(rich_candidate, job_req):
    """Test analysis works with empty enrichment data."""
    empty_enrichment = {}

    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, empty_enrichment, job_req)

    # Should still work
    assert insights is not None
    assert len(insights["achievements"]) >= 1


def test_analysis_with_no_top_repos(enrichment_data, job_req):
    """Test analysis with candidate having no top_repos."""
    candidate_no_repos = {
        "github_username": "emptydoe",
        "name": "Empty Doe",
        "bio": "Developer",
        "top_repos": [],
        "languages": ["Python"],
        "total_repos": 0,
        "contribution_count": 5
    }

    mock_llm = MockLLMClient()
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(candidate_no_repos, enrichment_data, job_req)

    # Should use minimal data fallback
    assert insights is not None
    prompt = mock_llm.last_prompt
    assert "No repositories available" in prompt or "minimal" in prompt.lower()


def test_analysis_limits_achievements_to_3(rich_candidate, enrichment_data, job_req):
    """Test that achievements are limited to top 3."""
    # Mock LLM with many achievements
    many_achievements = {
        "achievements": ["Achievement " + str(i) for i in range(10)],
        "passion_areas": ["Area 1", "Area 2"],
        "career_trajectory": "Path",
        "conversation_starters": ["Starter " + str(i) for i in range(10)],
        "minimal_data_fallback": False
    }

    mock_llm = MockLLMClient(response_json=many_achievements)
    stage = AnalysisStage(mock_llm)

    insights = stage.analyze(rich_candidate, enrichment_data, job_req)

    # Verify limited to 3
    assert len(insights["achievements"]) <= 3
    assert len(insights["conversation_starters"]) <= 3

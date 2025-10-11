"""Integration tests for skill matcher."""

import pytest
from unittest.mock import Mock

from src.ranking_engine.skill_matcher import SkillMatcher


class TestSkillMatcher:
    """Test skill matching with exact and semantic matching."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        return Mock()

    def test_exact_match_case_insensitive(self, mock_llm_client):
        """Test exact matching works case-insensitively."""
        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "JavaScript", "Docker"]
        candidate = ["python", "javascript", "Go"]

        matched, missing = matcher.match_skills(required, candidate)

        # Python and JavaScript should match exactly (case-insensitive)
        assert "Python" in matched
        assert "JavaScript" in matched
        assert "Docker" in missing
        assert len(matched) == 2
        assert len(missing) == 1

    def test_exact_match_with_whitespace(self, mock_llm_client):
        """Test exact matching handles whitespace."""
        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "FastAPI"]
        candidate = [" python ", "fastapi "]

        matched, missing = matcher.match_skills(required, candidate)

        assert len(matched) == 2
        assert len(missing) == 0

    def test_no_matches(self, mock_llm_client):
        """Test when no skills match."""
        # Mock LLM to return no matches
        mock_llm_client.complete.return_value = '''
        {
            "matched_skills": [],
            "missing_skills": ["Python", "Docker"]
        }
        '''

        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Docker"]
        candidate = ["Java", "C++"]

        matched, missing = matcher.match_skills(required, candidate)

        assert len(matched) == 0
        assert len(missing) == 2
        assert "Python" in missing
        assert "Docker" in missing

    def test_all_matches(self, mock_llm_client):
        """Test when all skills match exactly."""
        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "JavaScript", "Docker"]
        candidate = ["Python", "JavaScript", "Docker", "Go"]

        matched, missing = matcher.match_skills(required, candidate)

        # Should match all exactly without needing LLM
        assert len(matched) == 3
        assert len(missing) == 0
        # LLM should not be called since all matched exactly
        mock_llm_client.complete.assert_not_called()

    def test_semantic_matching_with_llm(self, mock_llm_client):
        """Test semantic matching using LLM."""
        # Mock LLM to return semantic match
        mock_llm_client.complete.return_value = '''
        {
            "matched_skills": ["Frontend Development"],
            "missing_skills": []
        }
        '''

        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Frontend Development"]
        candidate = ["Python", "React", "Vue"]

        matched, missing = matcher.match_skills(required, candidate)

        # Python matches exactly, Frontend Development matches semantically
        assert len(matched) == 2
        assert "Python" in matched
        assert "Frontend Development" in matched
        assert len(missing) == 0

        # LLM should be called for remaining skill (Frontend Development)
        mock_llm_client.complete.assert_called_once()

    def test_partial_semantic_match(self, mock_llm_client):
        """Test partial semantic matching."""
        # Mock LLM to return partial match
        mock_llm_client.complete.return_value = '''
        {
            "matched_skills": ["Web Framework"],
            "missing_skills": ["Machine Learning"]
        }
        '''

        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Web Framework", "Machine Learning"]
        candidate = ["Python", "FastAPI", "Flask"]

        matched, missing = matcher.match_skills(required, candidate)

        assert len(matched) == 2  # Python (exact) + Web Framework (semantic)
        assert "Python" in matched
        assert "Web Framework" in matched
        assert "Machine Learning" in missing

    def test_empty_required_skills(self, mock_llm_client):
        """Test with no required skills."""
        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = []
        candidate = ["Python", "JavaScript"]

        matched, missing = matcher.match_skills(required, candidate)

        assert matched == []
        assert missing == []
        mock_llm_client.complete.assert_not_called()

    def test_empty_candidate_languages(self, mock_llm_client):
        """Test with no candidate languages."""
        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Docker"]
        candidate = []

        matched, missing = matcher.match_skills(required, candidate)

        assert matched == []
        assert missing == required
        mock_llm_client.complete.assert_not_called()

    def test_llm_returns_invalid_json(self, mock_llm_client):
        """Test fallback when LLM returns invalid JSON."""
        # Mock LLM to return invalid JSON
        mock_llm_client.complete.return_value = "This is not JSON"

        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Kubernetes"]
        candidate = ["Python", "Docker"]

        matched, missing = matcher.match_skills(required, candidate)

        # Python should match exactly, Kubernetes should fall to missing
        assert "Python" in matched
        assert "Kubernetes" in missing

    def test_llm_exception_fallback(self, mock_llm_client):
        """Test fallback when LLM raises exception."""
        # Mock LLM to raise exception
        mock_llm_client.complete.side_effect = Exception("API error")

        matcher = SkillMatcher(llm_client=mock_llm_client)

        required = ["Python", "Machine Learning"]
        candidate = ["Python", "TensorFlow"]

        matched, missing = matcher.match_skills(required, candidate)

        # Python should match exactly, ML should fall to missing
        assert "Python" in matched
        assert "Machine Learning" in missing

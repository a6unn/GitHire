"""Integration tests for prompt templates."""

import pytest

from src.outreach_generator.prompts.formal_template import build_formal_prompt
from src.outreach_generator.prompts.casual_template import build_casual_prompt


class TestFormalPrompt:
    """Test formal prompt template generation."""

    @pytest.fixture
    def sample_repos(self):
        """Sample repository list."""
        return [
            {
                "name": "fastapi-backend",
                "description": "Production FastAPI backend",
                "stars": 120,
                "languages": ["Python"]
            },
            {
                "name": "docker-compose",
                "description": "Docker templates",
                "stars": 45,
                "languages": ["Shell"]
            }
        ]

    def test_formal_prompt_includes_candidate_username(self, sample_repos):
        """Test formal prompt includes candidate username."""
        prompt = build_formal_prompt(
            candidate_name="John Doe",
            candidate_username="johndoe",
            candidate_bio="Python developer",
            job_role="Senior Backend Engineer",
            job_skills=["Python", "FastAPI"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "johndoe" in prompt
        assert "@johndoe" in prompt

    def test_formal_prompt_includes_job_role(self, sample_repos):
        """Test formal prompt includes job role."""
        prompt = build_formal_prompt(
            candidate_name="Jane Smith",
            candidate_username="janesmith",
            candidate_bio="",
            job_role="Lead DevOps Engineer",
            job_skills=["Kubernetes", "Docker"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "Lead DevOps Engineer" in prompt

    def test_formal_prompt_includes_repos(self, sample_repos):
        """Test formal prompt includes repository names."""
        prompt = build_formal_prompt(
            candidate_name="Dev User",
            candidate_username="devuser",
            candidate_bio="",
            job_role="Software Engineer",
            job_skills=["Python"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "fastapi-backend" in prompt
        assert "docker-compose" in prompt

    def test_formal_prompt_deep_depth_mentions_detail(self, sample_repos):
        """Test deep depth includes detailed analysis instruction."""
        prompt = build_formal_prompt(
            candidate_name="Alice",
            candidate_username="alice",
            candidate_bio="",
            job_role="Engineer",
            job_skills=["Python"],
            relevant_repos=sample_repos,
            depth="deep"
        )

        assert "detailed" in prompt.lower() or "thoroughly" in prompt.lower()

    def test_formal_prompt_handles_empty_repos(self):
        """Test formal prompt handles candidate with no repos."""
        prompt = build_formal_prompt(
            candidate_name="Newbie",
            candidate_username="newbie",
            candidate_bio="",
            job_role="Junior Developer",
            job_skills=["JavaScript"],
            relevant_repos=[],
            depth="surface"
        )

        assert "minimal" in prompt.lower() or "potential" in prompt.lower()
        assert "newbie" in prompt

    def test_formal_prompt_includes_bio_when_present(self, sample_repos):
        """Test formal prompt includes bio if provided."""
        bio = "Full-stack developer with 5 years experience"
        prompt = build_formal_prompt(
            candidate_name="Bob",
            candidate_username="bob",
            candidate_bio=bio,
            job_role="Engineer",
            job_skills=["Python"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert bio in prompt

    def test_formal_prompt_omits_bio_when_empty(self, sample_repos):
        """Test formal prompt handles empty bio gracefully."""
        prompt = build_formal_prompt(
            candidate_name="Charlie",
            candidate_username="charlie",
            candidate_bio="",
            job_role="Engineer",
            job_skills=["Go"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        # Should not have "Bio: " if bio is empty
        assert "Bio: " not in prompt or "Bio:" not in prompt


class TestCasualPrompt:
    """Test casual prompt template generation."""

    @pytest.fixture
    def sample_repos(self):
        """Sample repository list."""
        return [
            {
                "name": "cool-project",
                "description": "Awesome side project",
                "stars": 80,
                "languages": ["JavaScript"]
            }
        ]

    def test_casual_prompt_includes_candidate_info(self, sample_repos):
        """Test casual prompt includes candidate information."""
        prompt = build_casual_prompt(
            candidate_name="Sam",
            candidate_username="samdev",
            candidate_bio="JavaScript enthusiast",
            job_role="Frontend Engineer",
            job_skills=["React", "TypeScript"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "samdev" in prompt
        assert "Frontend Engineer" in prompt

    def test_casual_prompt_has_different_tone_than_formal(self, sample_repos):
        """Test casual prompt has conversational tone instructions."""
        casual = build_casual_prompt(
            candidate_name="Taylor",
            candidate_username="taylor",
            candidate_bio="",
            job_role="Engineer",
            job_skills=["Python"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "casual" in casual.lower() or "conversational" in casual.lower() or "friendly" in casual.lower()

    def test_casual_prompt_includes_repos(self, sample_repos):
        """Test casual prompt includes repository names."""
        prompt = build_casual_prompt(
            candidate_name="Alex",
            candidate_username="alex",
            candidate_bio="",
            job_role="Developer",
            job_skills=["JavaScript"],
            relevant_repos=sample_repos,
            depth="medium"
        )

        assert "cool-project" in prompt

    def test_casual_prompt_depth_variations(self, sample_repos):
        """Test casual prompt has different instructions for depth levels."""
        deep = build_casual_prompt(
            candidate_name="User",
            candidate_username="user",
            candidate_bio="",
            job_role="Role",
            job_skills=["Skill"],
            relevant_repos=sample_repos,
            depth="deep"
        )

        surface = build_casual_prompt(
            candidate_name="User",
            candidate_username="user",
            candidate_bio="",
            job_role="Role",
            job_skills=["Skill"],
            relevant_repos=sample_repos,
            depth="surface"
        )

        # Deep should mention multiple projects or details
        assert deep != surface
        assert len(deep) > 100  # Should have content


class TestPromptComparison:
    """Test differences between formal and casual prompts."""

    def test_formal_vs_casual_tone_difference(self):
        """Test that formal and casual prompts have different tone instructions."""
        repos = [{"name": "repo", "description": "test", "stars": 10, "languages": ["Python"]}]

        formal = build_formal_prompt(
            candidate_name="Test",
            candidate_username="test",
            candidate_bio="",
            job_role="Engineer",
            job_skills=["Python"],
            relevant_repos=repos,
            depth="medium"
        )

        casual = build_casual_prompt(
            candidate_name="Test",
            candidate_username="test",
            candidate_bio="",
            job_role="Engineer",
            job_skills=["Python"],
            relevant_repos=repos,
            depth="medium"
        )

        # Formal should mention "professional" or "formal"
        assert "professional" in formal.lower() or "formal" in formal.lower()

        # Casual should mention "casual" or "friendly" or "conversational"
        assert ("casual" in casual.lower() or "friendly" in casual.lower() or
                "conversational" in casual.lower())

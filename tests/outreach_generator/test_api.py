"""API-level tests for outreach generator public API."""

import pytest
from unittest.mock import Mock

from src.outreach_generator import generate_outreach, generate_outreach_batch
from src.outreach_generator.models import ToneStyle
from src.ranking_engine.models import RankedCandidate, ScoreBreakdown
from src.github_sourcer.models.candidate import Candidate
from src.jd_parser.models import JobRequirement, YearsOfExperience


class TestPublicAPI:
    """Test public API functions."""

    @pytest.fixture
    def job_req(self):
        """Sample job requirement."""
        return JobRequirement(
            role="Software Engineer",
            required_skills=["Python"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=3, max=None, range_text="3+ years"),
            location_preferences=["Remote"],
            seniority_level="Mid-level",
            original_input="Looking for Software Engineer with 3+ years Python experience."
        )

    @pytest.fixture
    def ranked_candidate(self):
        """Sample ranked candidate."""
        candidate = Candidate(
            github_username="testuser",
            name="Test User",
            bio="Python developer",
            location="USA",
            email=None,
            company=None,
            followers=100,
            following=50,
            public_repos=20,
            contribution_count=500,
            account_age_days=1000,
            languages=["Python"],
            top_repos=[],
            profile_url="https://github.com/testuser"
        )

        return RankedCandidate(
            candidate=candidate,
            rank=1,
            total_score=75.0,
            skill_match_score=70.0,
            activity_score=75.0,
            experience_score=75.0,
            domain_score=70.0,
            score_breakdown=ScoreBreakdown(
                matched_skills=["Python"],
                missing_skills=[],
                activity_reasoning="Good",
                experience_reasoning="Mid",
                domain_reasoning="N/A"
            )
        )

    def test_generate_outreach_returns_message(self, job_req, ranked_candidate, monkeypatch):
        """Test generate_outreach returns OutreachMessage."""
        # Mock LLM client to avoid real API calls
        mock_llm = Mock()
        mock_llm.generate_text.return_value = {
            "content": """Hi Test User,

I came across your GitHub profile and was impressed by your Python work.
We're looking for a Software Engineer and I think you'd be a great fit.
Your experience aligns well with what we're building. The position involves
backend development and working with modern Python frameworks. I'd love to
discuss this opportunity further with you.

Would you be interested in chatting more? Let me know if you'd like to connect!

Best regards""",
            "usage": {"total_tokens": 100}
        }

        # Patch LLMClient to return mock
        from src.jd_parser import llm_client
        monkeypatch.setattr(llm_client, "LLMClient", lambda: mock_llm)

        message = generate_outreach(ranked_candidate, job_req)

        assert message.candidate_username == "testuser"
        assert message.rank == 1
        assert message.tone == ToneStyle.FORMAL
        assert len(message.message_text) > 0

    def test_generate_outreach_with_casual_tone(self, job_req, ranked_candidate, monkeypatch):
        """Test generate_outreach with casual tone."""
        mock_llm = Mock()
        mock_llm.generate_text.return_value = {
            "content": """Hey Test User!

Saw your GitHub profile and loved your Python projects. We're hiring for
a Software Engineer role and thought you might be interested. It's a cool
opportunity to work on interesting backend systems. Let me know if you want
to learn more about it!

Cheers""" + " " * 200,  # Pad to meet length requirement
            "usage": {"total_tokens": 80}
        }

        from src.jd_parser import llm_client
        monkeypatch.setattr(llm_client, "LLMClient", lambda: mock_llm)

        message = generate_outreach(ranked_candidate, job_req, tone="casual")

        assert message.tone == ToneStyle.CASUAL

    def test_generate_outreach_batch_returns_list(self, job_req, monkeypatch):
        """Test generate_outreach_batch returns list of messages."""
        candidates = []
        for i in range(3):
            candidate = Candidate(
                github_username=f"user{i}",
                name=f"User {i}",
                bio="Developer",
                location="USA",
                email=None,
                company=None,
                followers=100,
                following=50,
                public_repos=20,
                contribution_count=500,
                account_age_days=1000,
                languages=["Python"],
                top_repos=[],
                profile_url=f"https://github.com/user{i}"
            )

            ranked = RankedCandidate(
                candidate=candidate,
                rank=i+1,
                total_score=70.0,
                skill_match_score=65.0,
                activity_score=70.0,
                experience_score=70.0,
                domain_score=65.0,
                score_breakdown=ScoreBreakdown(
                    matched_skills=["Python"],
                    missing_skills=[],
                    activity_reasoning="Good",
                    experience_reasoning="Mid",
                    domain_reasoning="N/A"
                )
            )
            candidates.append(ranked)

        mock_llm = Mock()
        mock_llm.generate_text.return_value = {
            "content": """Hi there,

I noticed your GitHub profile and wanted to reach out about a software engineering
role we're hiring for. Your Python background looks like a good fit for what we're
building. The position involves backend development with modern frameworks and working
on distributed systems. Let me know if you'd be interested in learning more!

Best regards""",
            "usage": {"total_tokens": 90}
        }

        from src.jd_parser import llm_client
        monkeypatch.setattr(llm_client, "LLMClient", lambda: mock_llm)

        messages = generate_outreach_batch(candidates, job_req)

        assert len(messages) == 3
        assert all(isinstance(msg.candidate_username, str) for msg in messages)
        # Diversity scores should be calculated
        assert all(hasattr(msg.personalization_metadata, "diversity_score") for msg in messages)

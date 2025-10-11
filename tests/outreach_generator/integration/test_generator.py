"""Integration tests for OutreachGenerator."""

import pytest
from unittest.mock import Mock, MagicMock

from src.outreach_generator.generator import OutreachGenerator
from src.outreach_generator.models import ToneStyle
from src.ranking_engine.models import RankedCandidate, ScoreBreakdown
from src.github_sourcer.models.candidate import Candidate, Repository
from src.jd_parser.models import JobRequirement, YearsOfExperience


class TestOutreachGenerator:
    """Test OutreachGenerator message generation."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create mocked LLM client."""
        mock = Mock()
        # Default successful response
        mock.generate_text.return_value = {
            "content": """Hi John,

I came across your GitHub profile and was really impressed by your fastapi-backend project.
Your work with FastAPI and PostgreSQL aligns perfectly with what we're building. We're looking
for a Senior Python Developer to join our team and work on similar distributed systems.

Your experience with production backends would be valuable for this role. The position involves
designing scalable APIs and working with modern Python frameworks. I'd love to discuss how your
background fits with what we're doing.

Would you be interested in chatting more about this opportunity? Let me know if you'd like to connect!

Best regards""",
            "usage": {"total_tokens": 150}
        }
        return mock

    @pytest.fixture
    def job_req(self):
        """Create sample job requirement."""
        return JobRequirement(
            role="Senior Python Developer",
            required_skills=["Python", "FastAPI", "Docker"],
            preferred_skills=["PostgreSQL"],
            years_of_experience=YearsOfExperience(min=5, max=None, range_text="5+ years"),
            location_preferences=["Remote"],
            seniority_level="Senior",
            original_input="Looking for Senior Python Developer with 5+ years experience."
        )

    @pytest.fixture
    def ranked_candidate(self):
        """Create sample ranked candidate."""
        candidate = Candidate(
            github_username="johndoe",
            name="John Doe",
            bio="Python backend engineer",
            location="USA",
            email=None,
            company="TechCorp",
            followers=200,
            following=100,
            public_repos=30,
            contribution_count=1500,
            account_age_days=2000,
            languages=["Python", "Go"],
            top_repos=[
                Repository(
                    name="fastapi-backend",
                    description="Production FastAPI backend",
                    stars=150,
                    forks=30,
                    languages=["Python"],
                    url="https://github.com/johndoe/fastapi-backend"
                ),
                Repository(
                    name="docker-utils",
                    description="Docker utilities",
                    stars=50,
                    forks=10,
                    languages=["Shell"],
                    url="https://github.com/johndoe/docker-utils"
                )
            ],
            profile_url="https://github.com/johndoe"
        )

        breakdown = ScoreBreakdown(
            matched_skills=["Python", "FastAPI"],
            missing_skills=["Docker"],
            activity_reasoning="High activity",
            experience_reasoning="Senior level",
            domain_reasoning="N/A"
        )

        return RankedCandidate(
            candidate=candidate,
            rank=1,
            total_score=85.0,
            skill_match_score=75.0,
            activity_score=90.0,
            experience_score=85.0,
            domain_score=80.0,
            score_breakdown=breakdown
        )

    def test_generate_formal_message_success(self, mock_llm_client, job_req, ranked_candidate):
        """Test successful formal message generation."""
        generator = OutreachGenerator(llm_client=mock_llm_client)

        message = generator.generate(ranked_candidate, job_req, tone="formal")

        assert message.candidate_username == "johndoe"
        assert message.rank == 1
        assert message.tone == ToneStyle.FORMAL
        assert message.fallback_applied is False
        assert message.confidence_score > 70  # High confidence (has repos, bio, etc.)
        assert message.tokens_used == 150
        assert len(message.message_text) > 0
        assert "John" in message.message_text or "johndoe" in message.message_text

        # Check metadata
        assert "fastapi-backend" in message.personalization_metadata.referenced_repositories
        assert len(message.personalization_metadata.referenced_skills) > 0

        # Verify LLM was called
        mock_llm_client.generate_text.assert_called_once()

    def test_generate_casual_message_success(self, mock_llm_client, job_req, ranked_candidate):
        """Test successful casual message generation."""
        generator = OutreachGenerator(llm_client=mock_llm_client)

        message = generator.generate(ranked_candidate, job_req, tone="casual")

        assert message.tone == ToneStyle.CASUAL
        assert message.fallback_applied is False
        mock_llm_client.generate_text.assert_called_once()

    def test_generate_with_no_repos_lower_confidence(self, mock_llm_client, job_req):
        """Test generation for candidate with no repositories."""
        # Candidate with no repos
        candidate = Candidate(
            github_username="newbie",
            name="New Developer",
            bio="Just starting",
            location=None,
            email=None,
            company=None,
            followers=10,
            following=5,
            public_repos=0,
            contribution_count=50,
            account_age_days=90,
            languages=[],
            top_repos=[],
            profile_url="https://github.com/newbie"
        )

        ranked = RankedCandidate(
            candidate=candidate,
            rank=15,
            total_score=45.0,
            skill_match_score=30.0,
            activity_score=40.0,
            experience_score=50.0,
            domain_score=60.0,
            score_breakdown=ScoreBreakdown(
                matched_skills=[],
                missing_skills=["Python"],
                activity_reasoning="Low",
                experience_reasoning="Junior",
                domain_reasoning="N/A"
            )
        )

        generator = OutreachGenerator(llm_client=mock_llm_client)
        message = generator.generate(ranked, job_req, tone="formal")

        # Lower confidence due to no repos
        assert message.confidence_score < 70
        assert message.personalization_metadata.referenced_repositories == []

    def test_generate_fallback_on_llm_failure(self, job_req, ranked_candidate):
        """Test fallback message when LLM fails."""
        mock_llm = Mock()
        mock_llm.generate_text.side_effect = Exception("LLM API error")

        generator = OutreachGenerator(llm_client=mock_llm)
        message = generator.generate(ranked_candidate, job_req, tone="formal")

        assert message.fallback_applied is True
        assert message.confidence_score < 50  # Low confidence for fallback
        assert message.tokens_used == 0
        assert "johndoe" in message.message_text.lower()

    def test_generate_fallback_on_validation_failure(self, job_req, ranked_candidate):
        """Test fallback when validation fails."""
        mock_llm = Mock()
        # Return message that's too short (will fail validation)
        mock_llm.generate_text.return_value = {
            "content": "Hi John!",  # Too short
            "usage": {"total_tokens": 5}
        }

        generator = OutreachGenerator(llm_client=mock_llm)
        message = generator.generate(ranked_candidate, job_req, tone="formal")

        assert message.fallback_applied is True
        assert message.confidence_score < 50

    def test_generate_batch_multiple_candidates(self, mock_llm_client, job_req):
        """Test batch generation for multiple candidates."""
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
                top_repos=[
                    Repository(
                        name=f"project-{i}",
                        description=f"Project {i}",
                        stars=50,
                        forks=10,
                        languages=["Python"],
                        url=f"https://github.com/user{i}/project-{i}"
                    )
                ],
                profile_url=f"https://github.com/user{i}"
            )

            ranked = RankedCandidate(
                candidate=candidate,
                rank=i+1,
                total_score=80.0 - i*5,
                skill_match_score=75.0,
                activity_score=80.0,
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
            candidates.append(ranked)

        generator = OutreachGenerator(llm_client=mock_llm_client)
        messages = generator.generate_batch(candidates, job_req, tone="formal")

        assert len(messages) == 3
        assert all(msg.candidate_username.startswith("user") for msg in messages)
        # Diversity scores should be calculated
        assert all(msg.personalization_metadata.diversity_score >= 0 for msg in messages)

    def test_confidence_calculation_factors(self, job_req):
        """Test confidence score calculation with different data completeness."""
        # Create custom mock that returns different messages for each candidate
        mock_llm = Mock()
        def generate_for_candidate(prompt):
            if "complete" in prompt.lower():
                return {
                    "content": """Hi Complete User,

I came across your profile and was impressed by your Python projects proj1 and proj2.
Your extensive experience aligns well with our Senior Python Developer role. We're building
distributed systems and your background would be valuable. The position involves architecting
scalable backends and mentoring junior engineers.

Would love to discuss this opportunity further. Let me know if you're interested in connecting!

Best regards""",
                    "usage": {"total_tokens": 120}
                }
            else:
                return {
                    "content": """Hi minimal,

I noticed your GitHub profile and wanted to reach out about an opportunity. Even though you're
early in your career, we have roles that could be a good fit for developers looking to grow.
We offer mentorship and a supportive environment for junior engineers. The role involves
working with Python and learning modern backend development practices.

Let me know if you'd be interested in learning more about this role!

Best""",
                    "usage": {"total_tokens": 90}
                }

        mock_llm.generate_text.side_effect = generate_for_candidate

        # Complete profile
        complete_candidate = Candidate(
            github_username="complete",
            name="Complete User",
            bio="Experienced developer",
            location="USA",
            email=None,
            company="TechCorp",
            followers=200,
            following=100,
            public_repos=50,
            contribution_count=2000,
            account_age_days=2500,
            languages=["Python"],
            top_repos=[
                Repository(
                    name="proj1",
                    description="Project 1",
                    stars=100,
                    forks=20,
                    languages=["Python"],
                    url="https://github.com/complete/proj1"
                ),
                Repository(
                    name="proj2",
                    description="Project 2",
                    stars=80,
                    forks=15,
                    languages=["Python"],
                    url="https://github.com/complete/proj2"
                )
            ],
            profile_url="https://github.com/complete"
        )

        # Minimal profile
        minimal_candidate = Candidate(
            github_username="minimal",
            name=None,
            bio=None,
            location=None,
            email=None,
            company=None,
            followers=10,
            following=5,
            public_repos=1,
            contribution_count=50,
            account_age_days=100,
            languages=[],
            top_repos=[],
            profile_url="https://github.com/minimal"
        )

        generator = OutreachGenerator(llm_client=mock_llm)

        complete_ranked = RankedCandidate(
            candidate=complete_candidate,
            rank=1,
            total_score=90.0,
            skill_match_score=85.0,
            activity_score=90.0,
            experience_score=90.0,
            domain_score=85.0,
            score_breakdown=ScoreBreakdown(
                matched_skills=["Python"],
                missing_skills=[],
                activity_reasoning="High",
                experience_reasoning="Senior",
                domain_reasoning="N/A"
            )
        )

        minimal_ranked = RankedCandidate(
            candidate=minimal_candidate,
            rank=20,
            total_score=40.0,
            skill_match_score=30.0,
            activity_score=40.0,
            experience_score=45.0,
            domain_score=35.0,
            score_breakdown=ScoreBreakdown(
                matched_skills=[],
                missing_skills=["Python"],
                activity_reasoning="Low",
                experience_reasoning="Junior",
                domain_reasoning="N/A"
            )
        )

        complete_msg = generator.generate(complete_ranked, job_req)
        minimal_msg = generator.generate(minimal_ranked, job_req)

        # Complete profile should have higher confidence
        assert complete_msg.confidence_score > minimal_msg.confidence_score

    def test_diversity_score_calculation(self, mock_llm_client, job_req):
        """Test diversity scores are calculated for batch messages."""
        # Create 2 candidates
        candidates = []
        for i in range(2):
            candidate = Candidate(
                github_username=f"dev{i}",
                name=f"Developer {i}",
                bio="Python engineer",
                location="USA",
                email=None,
                company=None,
                followers=150,
                following=75,
                public_repos=25,
                contribution_count=1000,
                account_age_days=1500,
                languages=["Python"],
                top_repos=[
                    Repository(
                        name=f"repo-{i}",
                        description=f"Repository {i}",
                        stars=75,
                        forks=15,
                        languages=["Python"],
                        url=f"https://github.com/dev{i}/repo-{i}"
                    )
                ],
                profile_url=f"https://github.com/dev{i}"
            )

            ranked = RankedCandidate(
                candidate=candidate,
                rank=i+1,
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
            candidates.append(ranked)

        generator = OutreachGenerator(llm_client=mock_llm_client)
        messages = generator.generate_batch(candidates, job_req)

        # Diversity scores should be set
        for msg in messages:
            assert 0 <= msg.personalization_metadata.diversity_score <= 100

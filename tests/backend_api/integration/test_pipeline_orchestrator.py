"""Integration tests for PipelineOrchestrator."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from src.backend_api.pipeline import PipelineOrchestrator, PipelineException
from src.jd_parser.models import JobRequirement
from src.github_sourcer.models import SearchResult, Candidate, Repository
from src.ranking_engine.models import RankedCandidate
from src.outreach_generator.models import OutreachMessage, ToneStyle, PersonalizationMetadata


@pytest.fixture
def sample_job_requirement():
    """Sample job requirement."""
    return JobRequirement(
        role="Senior Python Developer",
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Docker"],
        original_input="Looking for a Senior Python Developer with FastAPI experience",
    )


@pytest.fixture
def sample_candidates():
    """Sample candidates."""
    return [
        Candidate(
            github_username="dev1",
            profile_url="https://github.com/dev1",
            name="Developer One",
            bio="Python developer",
            location="SF",
            public_email=None,
            top_repos=[
                Repository(
                    name="repo1",
                    url="https://github.com/dev1/repo1",
                    description="Python project",
                    languages=["Python"],
                    stars=10,
                    forks=5,
                    is_fork=False,
                    created_at=datetime(2020, 1, 1),
                    updated_at=datetime(2024, 1, 1),
                )
            ],
            languages=["Python"],
            contribution_count=100,
            account_age_days=365,
        )
    ]


@pytest.fixture
def sample_search_result(sample_candidates):
    """Sample search result."""
    return {
        "candidates": sample_candidates,
        "metadata": {
            "total_candidates_found": 1,
            "candidates_returned": 1,
            "rate_limit_remaining": 1000,
            "cache_hit": False,
            "execution_time_ms": 100,
        }
    }


@pytest.fixture
def sample_ranked_candidates(sample_candidates):
    """Sample ranked candidates."""
    from src.ranking_engine.models import ScoreBreakdown
    return [
        RankedCandidate(
            candidate=sample_candidates[0],
            rank=1,
            total_score=85.5,
            skill_match_score=90.0,
            experience_score=80.0,
            activity_score=85.0,
            domain_score=75.0,
            score_breakdown=ScoreBreakdown(
                skill_matches=["Python"],
                skill_gaps=["FastAPI"],
                total_skills_required=2,
                total_skills_matched=1,
                activity_reasoning="Active contributor",
                experience_reasoning="Experienced developer",
                domain_reasoning="Relevant domain",
            ),
        )
    ]


@pytest.fixture
def sample_outreach_messages(sample_ranked_candidates):
    """Sample outreach messages."""
    return [
        OutreachMessage(
            candidate_username="dev1",
            rank=1,
            message_text="Hi Developer One, we have an opportunity...",
            tone=ToneStyle.FORMAL,
            confidence_score=85.0,
            personalization_metadata=PersonalizationMetadata(
                referenced_repositories=["repo1"],
                referenced_skills=["Python"],
            ),
            tokens_used=100,
            fallback_applied=False,
        )
    ]


class TestPipelineOrchestrator:
    """Test PipelineOrchestrator."""

    @pytest.mark.asyncio
    async def test_successful_pipeline_execution(
        self,
        sample_job_requirement,
        sample_search_result,
        sample_ranked_candidates,
        sample_outreach_messages,
    ):
        """Test successful execution of full pipeline."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github, \
             patch("src.backend_api.pipeline.rank_candidates") as mock_rank_candidates, \
             patch("src.backend_api.pipeline.generate_outreach_batch") as mock_generate_outreach:

            # Setup mocks
            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.return_value = sample_search_result
            mock_rank_candidates.return_value = sample_ranked_candidates
            mock_generate_outreach.return_value = sample_outreach_messages

            # Execute pipeline
            result = await orchestrator.execute_pipeline("Job description here")

            # Verify result structure
            assert result["status"] == "success"
            assert "job_requirement" in result
            assert "candidates" in result
            assert "ranked_candidates" in result
            assert "outreach_messages" in result
            assert "metadata" in result

            # Verify metadata
            assert result["metadata"]["candidates_found"] == 1
            assert result["metadata"]["candidates_ranked"] == 1
            assert result["metadata"]["messages_generated"] == 1
            assert "execution_time_seconds" in result["metadata"]

            # Verify progress
            assert orchestrator.progress == 100

            # Verify all modules were called
            mock_parse_jd.assert_called_once()
            mock_search_github.assert_called_once()
            mock_rank_candidates.assert_called_once()
            mock_generate_outreach.assert_called_once()

    @pytest.mark.asyncio
    async def test_module_001_failure(self):
        """Test pipeline failure at Module 001."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd:
            mock_parse_jd.side_effect = Exception("JD parsing failed")

            with pytest.raises(PipelineException) as exc_info:
                await orchestrator.execute_pipeline("Invalid JD")

            assert "Module 001" in str(exc_info.value)
            assert "Failed to parse job description" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_module_002_failure(self, sample_job_requirement):
        """Test pipeline failure at Module 002."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github:

            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.side_effect = Exception("GitHub search failed")

            with pytest.raises(PipelineException) as exc_info:
                await orchestrator.execute_pipeline("Job description")

            assert "Module 002" in str(exc_info.value)
            assert "Failed to search GitHub" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_module_003_failure(
        self, sample_job_requirement, sample_search_result
    ):
        """Test pipeline failure at Module 003."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github, \
             patch("src.backend_api.pipeline.rank_candidates") as mock_rank_candidates:

            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.return_value = sample_search_result
            mock_rank_candidates.side_effect = Exception("Ranking failed")

            with pytest.raises(PipelineException) as exc_info:
                await orchestrator.execute_pipeline("Job description")

            assert "Module 003" in str(exc_info.value)
            assert "Failed to rank candidates" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_module_004_failure(
        self,
        sample_job_requirement,
        sample_search_result,
        sample_ranked_candidates,
    ):
        """Test pipeline failure at Module 004."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github, \
             patch("src.backend_api.pipeline.rank_candidates") as mock_rank_candidates, \
             patch("src.backend_api.pipeline.generate_outreach_batch") as mock_generate_outreach:

            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.return_value = sample_search_result
            mock_rank_candidates.return_value = sample_ranked_candidates
            mock_generate_outreach.side_effect = Exception("Outreach generation failed")

            with pytest.raises(PipelineException) as exc_info:
                await orchestrator.execute_pipeline("Job description")

            assert "Module 004" in str(exc_info.value)
            assert "Failed to generate outreach messages" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_progress_tracking(
        self,
        sample_job_requirement,
        sample_search_result,
        sample_ranked_candidates,
        sample_outreach_messages,
    ):
        """Test pipeline progress tracking."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github, \
             patch("src.backend_api.pipeline.rank_candidates") as mock_rank_candidates, \
             patch("src.backend_api.pipeline.generate_outreach_batch") as mock_generate_outreach:

            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.return_value = sample_search_result
            mock_rank_candidates.return_value = sample_ranked_candidates
            mock_generate_outreach.return_value = sample_outreach_messages

            # Execute pipeline
            await orchestrator.execute_pipeline("Job description")

            # Check final progress
            progress = orchestrator.get_progress()
            assert progress["progress_percentage"] == 100
            assert progress["current_module"] == "Module 004: Outreach Generator"
            assert "elapsed_time_seconds" in progress
            assert "estimated_remaining_seconds" in progress

    @pytest.mark.asyncio
    async def test_module_results_tracking(
        self,
        sample_job_requirement,
        sample_search_result,
        sample_ranked_candidates,
        sample_outreach_messages,
    ):
        """Test that module results are tracked correctly."""
        orchestrator = PipelineOrchestrator()

        with patch("src.backend_api.pipeline.parse_jd") as mock_parse_jd, \
             patch("src.backend_api.pipeline.search_github") as mock_search_github, \
             patch("src.backend_api.pipeline.rank_candidates") as mock_rank_candidates, \
             patch("src.backend_api.pipeline.generate_outreach_batch") as mock_generate_outreach:

            mock_parse_jd.return_value = sample_job_requirement
            mock_search_github.return_value = sample_search_result
            mock_rank_candidates.return_value = sample_ranked_candidates
            mock_generate_outreach.return_value = sample_outreach_messages

            result = await orchestrator.execute_pipeline("Job description")

            # Verify module results are tracked
            module_results = result["metadata"]["module_results"]
            assert "module_001" in module_results
            assert "module_002" in module_results
            assert "module_003" in module_results
            assert "module_004" in module_results

            assert module_results["module_001"]["status"] == "success"
            assert module_results["module_002"]["status"] == "success"
            assert module_results["module_003"]["status"] == "success"
            assert module_results["module_004"]["status"] == "success"

    def test_pipeline_exception_structure(self):
        """Test PipelineException structure."""
        original_error = ValueError("Original error")
        exc = PipelineException(
            message="Test error",
            module_name="Module 001",
            original_error=original_error,
        )

        assert exc.message == "Test error"
        assert exc.module_name == "Module 001"
        assert exc.original_error == original_error
        assert "Module 001" in str(exc)
        assert "Test error" in str(exc)

    @pytest.mark.asyncio
    async def test_initial_progress_state(self):
        """Test initial progress state before execution."""
        orchestrator = PipelineOrchestrator()

        progress = orchestrator.get_progress()
        assert progress["progress_percentage"] == 0
        assert progress["current_module"] is None
        assert progress["elapsed_time_seconds"] == 0

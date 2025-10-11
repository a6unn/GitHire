"""Pipeline orchestrator for executing recruitment pipeline modules sequentially."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.jd_parser import parse_jd
from src.jd_parser.models import JobRequirement
from src.github_sourcer import search_github
from src.github_sourcer.models import SearchResult
from src.ranking_engine import rank_candidates
from src.ranking_engine.models import RankedCandidate
# from src.outreach_generator import generate_outreach_batch  # Module 004 now uses endpoint-based approach
from src.outreach_generator.models import OutreachMessage

logger = logging.getLogger(__name__)


class PipelineException(Exception):
    """Custom exception for pipeline execution errors."""

    def __init__(self, message: str, module_name: str, original_error: Optional[Exception] = None):
        self.message = message
        self.module_name = module_name
        self.original_error = original_error
        super().__init__(f"[{module_name}] {message}")


class PipelineOrchestrator:
    """Orchestrates the execution of all recruitment pipeline modules."""

    def __init__(self):
        """Initialize the pipeline orchestrator."""
        self.current_module: Optional[str] = None
        self.progress: int = 0
        self.start_time: Optional[datetime] = None
        self.module_results: Dict[str, Any] = {}

    def _execute_module_001(self, job_description: str) -> JobRequirement:
        """Execute Module 001: JD Parser.

        Args:
            job_description: Raw job description text

        Returns:
            Parsed JobRequirement object

        Raises:
            PipelineException: If parsing fails
        """
        try:
            self.current_module = "Module 001: JD Parser"
            logger.info(f"Executing {self.current_module}")

            job_requirement = parse_jd(job_description)

            self.module_results["module_001"] = {
                "status": "success",
                "job_requirement": job_requirement.model_dump(),
            }
            self.progress = 25

            return job_requirement

        except Exception as e:
            logger.error(f"Module 001 failed: {str(e)}")
            raise PipelineException(
                message=f"Failed to parse job description: {str(e)}",
                module_name="Module 001",
                original_error=e,
            )

    async def _execute_module_002(self, job_requirement: JobRequirement) -> dict:
        """Execute Module 002: GitHub Sourcer (async).

        Args:
            job_requirement: Parsed job requirement

        Returns:
            Dict with candidates and metadata

        Raises:
            PipelineException: If search fails
        """
        try:
            self.current_module = "Module 002: GitHub Sourcer"
            logger.info(f"Executing {self.current_module}")

            search_result = await search_github(job_requirement)

            self.module_results["module_002"] = {
                "status": "success",
                "candidates_found": len(search_result["candidates"]),
            }
            self.progress = 50

            return search_result

        except Exception as e:
            logger.error(f"Module 002 failed: {str(e)}")
            raise PipelineException(
                message=f"Failed to search GitHub: {str(e)}",
                module_name="Module 002",
                original_error=e,
            )

    def _execute_module_003(
        self, candidates: list, job_requirement: JobRequirement
    ) -> list[RankedCandidate]:
        """Execute Module 003: Candidate Ranker.

        Args:
            candidates: List of candidate objects
            job_requirement: Job requirement for ranking

        Returns:
            List of ranked candidates

        Raises:
            PipelineException: If ranking fails
        """
        try:
            self.current_module = "Module 003: Candidate Ranker"
            logger.info(f"Executing {self.current_module}")

            ranked_candidates = rank_candidates(candidates, job_requirement)

            self.module_results["module_003"] = {
                "status": "success",
                "candidates_ranked": len(ranked_candidates),
            }
            self.progress = 75

            return ranked_candidates

        except Exception as e:
            logger.error(f"Module 003 failed: {str(e)}")
            raise PipelineException(
                message=f"Failed to rank candidates: {str(e)}",
                module_name="Module 003",
                original_error=e,
            )

    def _execute_module_004(
        self, ranked_candidates: list[RankedCandidate], job_requirement: JobRequirement
    ) -> list[OutreachMessage]:
        """Execute Module 004: Outreach Generator.

        NOTE: Module 004 now uses endpoint-based approach. Use the /shortlist/{username}/outreach endpoint instead.
        This method is deprecated and will be removed.

        Args:
            ranked_candidates: List of ranked candidates
            job_requirement: Job requirement for personalization

        Returns:
            Empty list (outreach generation now done via endpoints)

        Raises:
            PipelineException: If generation fails
        """
        try:
            self.current_module = "Module 004: Outreach Generator"
            logger.info(f"Executing {self.current_module} (DEPRECATED - use endpoint-based approach)")

            # Module 004 now uses endpoint-based approach with OutreachOrchestrator
            # Users should call POST /projects/{project_id}/shortlist/{username}/outreach
            outreach_messages = []

            self.module_results["module_004"] = {
                "status": "skipped",
                "messages_generated": 0,
                "note": "Use endpoint-based outreach generation instead"
            }
            self.progress = 100

            return outreach_messages

        except Exception as e:
            logger.error(f"Module 004 failed: {str(e)}")
            raise PipelineException(
                message=f"Failed to generate outreach messages: {str(e)}",
                module_name="Module 004",
                original_error=e,
            )

    async def execute_pipeline(self, job_description: str) -> dict:
        """Execute the full recruitment pipeline.

        Args:
            job_description: Raw job description text

        Returns:
            Dictionary with pipeline results including:
            - job_requirement: Parsed job requirement
            - candidates: List of candidates found
            - ranked_candidates: List of ranked candidates
            - outreach_messages: List of generated messages
            - metadata: Execution metadata

        Raises:
            PipelineException: If any module fails
        """
        try:
            self.start_time = datetime.utcnow()
            self.progress = 0
            self.module_results = {}

            logger.info("Starting recruitment pipeline execution")

            # Module 001: Parse JD
            job_requirement = self._execute_module_001(job_description)

            # Module 002: Search GitHub (async)
            search_result = await self._execute_module_002(job_requirement)

            # Module 003: Rank Candidates
            ranked_candidates = self._execute_module_003(
                search_result["candidates"], job_requirement
            )

            # Module 004: Generate Outreach
            outreach_messages = self._execute_module_004(
                ranked_candidates, job_requirement
            )

            end_time = datetime.utcnow()
            execution_time = (end_time - self.start_time).total_seconds()

            logger.info(
                f"Pipeline execution completed in {execution_time:.2f}s, "
                f"{len(outreach_messages)} messages generated"
            )

            return {
                "status": "success",
                "job_requirement": job_requirement.model_dump(mode='json'),
                "candidates": [c.model_dump(mode='json') for c in search_result["candidates"]],
                "ranked_candidates": [rc.model_dump(mode='json') for rc in ranked_candidates],
                "outreach_messages": [om.model_dump(mode='json') for om in outreach_messages],
                "metadata": {
                    "execution_time_seconds": execution_time,
                    "candidates_found": len(search_result["candidates"]),
                    "candidates_ranked": len(ranked_candidates),
                    "messages_generated": len(outreach_messages),
                    "start_time": self.start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "module_results": self.module_results,
                },
            }

        except PipelineException:
            # Re-raise pipeline exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            logger.error(f"Unexpected pipeline error: {str(e)}")
            raise PipelineException(
                message=f"Unexpected error: {str(e)}",
                module_name=self.current_module or "Unknown",
                original_error=e,
            )

    def get_progress(self) -> dict:
        """Get current pipeline execution progress.

        Returns:
            Dictionary with progress information
        """
        elapsed_time = 0
        if self.start_time:
            elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()

        # Estimate total time based on current progress
        estimated_total_time = (elapsed_time / self.progress * 100) if self.progress > 0 else 0
        estimated_remaining_time = max(0, estimated_total_time - elapsed_time)

        return {
            "current_module": self.current_module,
            "progress_percentage": self.progress,
            "elapsed_time_seconds": elapsed_time,
            "estimated_remaining_seconds": estimated_remaining_time,
            "module_results": self.module_results,
        }

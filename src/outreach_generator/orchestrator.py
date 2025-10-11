"""
Outreach Orchestrator - Integrates the 3-Stage Pipeline

This module orchestrates the complete outreach generation pipeline:
Stage 1 (Analysis) → Stage 2 (Generation) → Stage 3 (Refinement)
"""

import logging
from typing import Optional
from datetime import datetime

from src.jd_parser.llm_client import LLMClient
from .models import OutreachMessage, PersonalizationMetadata, ChannelType
from .stages.analysis_stage import AnalysisStage
from .stages.generation_stage import GenerationStage
from .stages.refinement_stage import RefinementStage
from .channel_optimizer import ChannelOptimizer
from .cliche_detector import ClicheDetector
from .personalization_scorer import PersonalizationScorer


logger = logging.getLogger(__name__)


class OutreachOrchestrator:
    """
    Orchestrates the 3-stage outreach generation pipeline.

    Pipeline:
    1. AnalysisStage: Deep GitHub profile analysis
    2. GenerationStage: Multi-channel message generation
    3. RefinementStage: Quality validation and polishing

    Returns a list of OutreachMessage objects (one per channel).

    Usage:
        >>> orchestrator = OutreachOrchestrator(llm_client)
        >>> messages = orchestrator.generate_outreach(candidate, enrichment, job_req)
        >>> for msg in messages:
        ...     print(f"{msg.channel}: {msg.personalization_score}")
        email: 85
        linkedin: 78
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Outreach Orchestrator.

        Args:
            llm_client: LLM client (OpenAI GPT-4 or Anthropic Claude)
        """
        self.llm_client = llm_client

        # Initialize all stages and helpers
        self.analysis_stage = AnalysisStage(llm_client)
        self.channel_optimizer = ChannelOptimizer()
        self.generation_stage = GenerationStage(llm_client, self.channel_optimizer)
        self.cliche_detector = ClicheDetector()
        self.personalization_scorer = PersonalizationScorer()
        self.refinement_stage = RefinementStage(
            llm_client,
            self.cliche_detector,
            self.personalization_scorer
        )

    def generate_outreach(
        self,
        candidate: dict,
        enrichment: dict,
        job_req: dict,
        shortlist_id: Optional[str] = None
    ) -> list[OutreachMessage]:
        """
        Generate outreach messages for a single candidate.

        Executes the 3-stage pipeline and returns OutreachMessage objects.

        Args:
            candidate: Candidate data from GitHub (username, repos, etc.)
            enrichment: Enriched contact data (email, linkedin, twitter, etc.)
            job_req: Job requirements (role, company, salary, etc.)
            shortlist_id: Optional shortlist ID for tracking

        Returns:
            List of OutreachMessage objects (one per available channel)

        Example:
            >>> orchestrator = OutreachOrchestrator(llm_client)
            >>> messages = orchestrator.generate_outreach(candidate, enrichment, job_req)
            >>> print(f"Generated {len(messages)} messages")
            Generated 3 messages
            >>> print(messages[0].personalization_score)
            85
        """
        try:
            logger.info(f"Starting outreach generation for {candidate.get('github_username')}")

            # Stage 1: Analysis
            logger.info("Stage 1: Analyzing GitHub profile")
            insights = self.analysis_stage.analyze(candidate, enrichment, job_req)
            tokens_analysis = insights.get("tokens_used", 0)

            # Determine available channels
            channels = self.generation_stage._determine_channels(enrichment)
            logger.info(f"Available channels: {channels}")

            if not channels:
                logger.warning("No channels available (missing contact info)")
                return []

            # Generate messages for each channel
            outreach_messages = []

            for channel in channels:
                try:
                    logger.info(f"Processing channel: {channel}")

                    # Stage 2: Generation
                    logger.info(f"Stage 2: Generating {channel} message")
                    raw_message = self.generation_stage.generate(
                        insights,
                        job_req,
                        enrichment,
                        channel,
                        candidate
                    )
                    tokens_generation = raw_message.get("tokens_used", 0)

                    # Stage 3: Refinement
                    logger.info(f"Stage 3: Refining {channel} message")
                    refined_message = self.refinement_stage.refine(
                        raw_message,
                        candidate,
                        enrichment,
                        insights
                    )
                    tokens_refinement = refined_message.get("tokens_used", 0)

                    # Build PersonalizationMetadata
                    metadata = self._build_metadata(
                        insights,
                        refined_message,
                        enrichment
                    )

                    # Calculate total tokens
                    total_tokens = tokens_analysis + tokens_generation + tokens_refinement

                    # Build stage breakdown
                    stage_breakdown = {
                        "analysis": tokens_analysis,
                        "generation": tokens_generation,
                        "refinement": tokens_refinement,
                        "total": total_tokens
                    }

                    # Create OutreachMessage object
                    # Handle subject_line: only set if it's a non-empty string, otherwise None
                    subject = refined_message.get("subject_line")
                    if subject and len(subject.strip()) > 0:
                        subject_line = subject
                    else:
                        subject_line = None

                    outreach_msg = OutreachMessage(
                        shortlist_id=shortlist_id or f"candidate_{candidate.get('github_username')}",
                        channel=ChannelType(channel),
                        subject_line=subject_line,
                        message_text=refined_message["message_text"],
                        personalization_score=refined_message["personalization_score"],
                        personalization_metadata=metadata,
                        tokens_used=total_tokens,
                        stage_breakdown=stage_breakdown,
                        is_edited=False,
                        generated_at=datetime.utcnow()
                    )

                    outreach_messages.append(outreach_msg)
                    logger.info(f"✓ {channel} message complete: score={refined_message['personalization_score']}")

                except Exception as e:
                    logger.error(f"Failed to generate {channel} message: {e}")
                    # Continue with other channels
                    continue

            logger.info(f"Outreach generation complete: {len(outreach_messages)} messages generated")
            return outreach_messages

        except Exception as e:
            logger.error(f"Error in outreach generation pipeline: {e}")
            return []

    def generate_batch(
        self,
        candidates: list[dict],
        enrichments: list[dict],
        job_req: dict
    ) -> list[list[OutreachMessage]]:
        """
        Generate outreach messages for multiple candidates.

        Args:
            candidates: List of candidate dicts
            enrichments: List of enrichment dicts (same order as candidates)
            job_req: Job requirements (same for all candidates)

        Returns:
            List of lists - one inner list per candidate

        Example:
            >>> orchestrator = OutreachOrchestrator(llm_client)
            >>> results = orchestrator.generate_batch(candidates, enrichments, job_req)
            >>> print(f"Generated for {len(results)} candidates")
            Generated for 10 candidates
        """
        results = []

        for i, (candidate, enrichment) in enumerate(zip(candidates, enrichments)):
            logger.info(f"Processing candidate {i+1}/{len(candidates)}: {candidate.get('github_username')}")

            messages = self.generate_outreach(candidate, enrichment, job_req)
            results.append(messages)

        return results

    def _build_metadata(
        self,
        insights: dict,
        refined_message: dict,
        enrichment: dict
    ) -> PersonalizationMetadata:
        """
        Build PersonalizationMetadata from pipeline results.

        Args:
            insights: Analysis insights from Stage 1
            refined_message: Refined message from Stage 3
            enrichment: Enrichment data

        Returns:
            PersonalizationMetadata object
        """
        # Extract referenced repositories
        referenced_repos = []
        breakdown = refined_message.get("personalization_breakdown", {})
        if breakdown.get("repo_mention"):
            # Could extract repo names from message, but for now just mark that repos were mentioned
            # This would be enhanced in production to extract actual repo names
            referenced_repos = ["repo mentioned"]  # Placeholder

        # Extract technical details
        technical_details = []
        if breakdown.get("technical_detail"):
            technical_details = ["technical detail mentioned"]  # Placeholder

        # Build enrichment data used
        enrichment_used = {}
        if enrichment.get("primary_email"):
            enrichment_used["email"] = enrichment["primary_email"]
        if enrichment.get("linkedin_username"):
            enrichment_used["linkedin"] = enrichment["linkedin_username"]
        if enrichment.get("twitter_username"):
            enrichment_used["twitter"] = enrichment["twitter_username"]
        if enrichment.get("company"):
            enrichment_used["company"] = enrichment["company"]

        metadata = PersonalizationMetadata(
            referenced_repositories=referenced_repos,
            technical_details_mentioned=technical_details,
            enrichment_data_used=enrichment_used,
            analysis_insights={
                "achievements": insights.get("achievements", []),
                "passion_areas": insights.get("passion_areas", []),
                "career_trajectory": insights.get("career_trajectory", ""),
                "minimal_data_fallback": insights.get("minimal_data_fallback", False)
            },
            cliches_removed=refined_message.get("cliches_removed", []),
            quality_flags=refined_message.get("quality_flags", [])
        )

        return metadata

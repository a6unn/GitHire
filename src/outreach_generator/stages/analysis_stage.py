"""
Stage 1: Analysis - Deep GitHub Profile Analysis

This module implements the first stage of the 3-stage outreach pipeline.
Uses GPT-4 to analyze GitHub profiles and extract personalization insights.
"""

import json
import logging
from typing import Optional

from src.jd_parser.llm_client import LLMClient
from ..prompts.analysis_prompt import build_analysis_prompt, build_minimal_data_fallback_prompt


logger = logging.getLogger(__name__)


class AnalysisStage:
    """
    Stage 1: Deep GitHub Profile Analysis

    Analyzes candidate GitHub profiles using GPT-4 to identify:
    - Top 3 technical achievements
    - Passion areas and interests
    - Career trajectory
    - Unique conversation starters

    Supports fallback for candidates with minimal data.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Analysis Stage.

        Args:
            llm_client: LLM client (OpenAI GPT-4 or Anthropic Claude)
        """
        self.llm_client = llm_client

    def analyze(
        self,
        candidate: dict,
        enrichment: dict,
        job_req: dict
    ) -> dict:
        """
        Analyze candidate GitHub profile and extract personalization insights.

        Args:
            candidate: Candidate data from GitHub
                - github_username (str)
                - name (str)
                - bio (str)
                - top_repos (list): List of top repositories
                - languages (list): Programming languages
                - total_repos (int)
                - contribution_count (int)
            enrichment: Enriched contact data from Module 010
                - primary_email (str)
                - linkedin_username (str)
                - twitter_username (str)
                - blog_url (str)
                - company (str)
                - hireable (bool)
            job_req: Job requirements from Module 001
                - role_type (str)
                - required_skills (list)
                - experience_level (str)
                - company_name (str)
                - salary_range (str)
                - tech_stack (list)

        Returns:
            Dictionary with analysis insights:
                {
                    "achievements": list[str],  # Top 3 technical achievements
                    "passion_areas": list[str],  # Technical interests
                    "career_trajectory": str,  # Career path assessment
                    "conversation_starters": list[str],  # 3 unique hooks
                    "minimal_data_fallback": bool,  # Whether fallback was used
                    "tokens_used": int  # LLM tokens consumed
                }

        Example:
            >>> stage = AnalysisStage(llm_client)
            >>> insights = stage.analyze(candidate, enrichment, job_req)
            >>> print(insights["achievements"][0])
            "Built redis-clone with 1.2k stars implementing distributed caching"
        """
        try:
            # Check if this is a minimal data scenario
            total_repos = candidate.get("total_repos", 0)
            top_repos = candidate.get("top_repos", [])

            is_minimal_data = total_repos < 3 or len(top_repos) < 3

            # Build appropriate prompt
            if is_minimal_data:
                logger.info(f"Using minimal data fallback for candidate: {candidate.get('github_username')}")
                prompt = build_minimal_data_fallback_prompt(candidate, enrichment, job_req)
            else:
                prompt = build_analysis_prompt(candidate, enrichment, job_req)

            # Call LLM with JSON mode for structured output
            logger.info(f"Calling LLM for analysis of {candidate.get('github_username')}")

            # Use OpenAI's JSON mode if available
            if hasattr(self.llm_client, 'complete'):
                # Check if it's OpenAI client (supports json_mode)
                if hasattr(self.llm_client, 'model'):
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=1500,
                        temperature=0.3,
                        json_mode=True
                    )
                else:
                    # Anthropic or other client
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=1500,
                        temperature=0.3
                    )
            else:
                raise AttributeError("LLM client does not have 'complete' method")

            # Parse JSON response
            try:
                insights = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Response: {response[:200]}")
                # Fallback to minimal insights
                insights = self._create_fallback_insights(candidate, job_req)

            # Add tokens used (estimate based on response length)
            # GPT-4 tokens ~= characters / 4
            tokens_estimate = (len(prompt) + len(response)) // 4
            insights["tokens_used"] = tokens_estimate

            # Validate insights structure
            insights = self._validate_insights(insights)

            logger.info(f"Analysis complete for {candidate.get('github_username')}: {insights.get('minimal_data_fallback')}")

            return insights

        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            # Return fallback insights on error
            return self._create_fallback_insights(candidate, job_req)

    def _validate_insights(self, insights: dict) -> dict:
        """
        Validate and sanitize analysis insights.

        Ensures all required fields are present with correct types.

        Args:
            insights: Raw insights from LLM

        Returns:
            Validated insights dictionary
        """
        validated = {
            "achievements": insights.get("achievements", []),
            "passion_areas": insights.get("passion_areas", []),
            "career_trajectory": insights.get("career_trajectory", "Not determined"),
            "conversation_starters": insights.get("conversation_starters", []),
            "minimal_data_fallback": insights.get("minimal_data_fallback", False),
            "tokens_used": insights.get("tokens_used", 0),
        }

        # Ensure lists have at least 1 item
        if not validated["achievements"]:
            validated["achievements"] = ["GitHub contributor"]
        if not validated["passion_areas"]:
            validated["passion_areas"] = ["Software Development"]
        if not validated["conversation_starters"]:
            validated["conversation_starters"] = ["Your GitHub profile shows strong technical skills"]

        # Ensure lists don't exceed 3 items
        validated["achievements"] = validated["achievements"][:3]
        validated["conversation_starters"] = validated["conversation_starters"][:3]

        return validated

    def _create_fallback_insights(self, candidate: dict, job_req: dict) -> dict:
        """
        Create fallback insights when LLM fails or data is insufficient.

        Args:
            candidate: Candidate data
            job_req: Job requirements

        Returns:
            Basic insights dictionary
        """
        username = candidate.get("github_username", "Unknown")
        role = job_req.get("role_type", "Software Engineer")
        company = job_req.get("company_name", "Our Company")

        return {
            "achievements": [
                f"Active GitHub user ({username})",
                "Demonstrates technical engagement on GitHub",
                "Shows initiative in software development"
            ],
            "passion_areas": ["Software Development", "Technology"],
            "career_trajectory": "Growing developer interested in new opportunities",
            "conversation_starters": [
                f"We're looking for developers passionate about technology at {company}",
                f"Your GitHub profile shows potential for our {role} role",
                f"Interested in learning more about opportunities at {company}?"
            ],
            "minimal_data_fallback": True,
            "tokens_used": 0,
        }

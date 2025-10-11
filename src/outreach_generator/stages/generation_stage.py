"""
Stage 2: Generation - Multi-Channel Message Generation

This module implements the second stage of the 3-stage outreach pipeline.
Uses GPT-4 to generate personalized messages for email, LinkedIn, and Twitter.
"""

import json
import logging
from typing import Optional

from src.jd_parser.llm_client import LLMClient
from ..channel_optimizer import ChannelOptimizer
from ..prompts.generation_prompt import (
    build_email_prompt,
    build_linkedin_prompt,
    build_twitter_prompt
)


logger = logging.getLogger(__name__)


class GenerationStage:
    """
    Stage 2: Multi-Channel Message Generation

    Generates personalized outreach messages for different channels using GPT-4.
    Uses insights from Stage 1 analysis to craft channel-specific messages.

    Supported channels:
    - Email: 50-125 words, subject 36-50 chars
    - LinkedIn: <400 chars, 3-4 sentences
    - Twitter: <280 chars, 2-3 sentences
    """

    def __init__(self, llm_client: LLMClient, channel_optimizer: ChannelOptimizer):
        """
        Initialize Generation Stage.

        Args:
            llm_client: LLM client (OpenAI GPT-4 or Anthropic Claude)
            channel_optimizer: ChannelOptimizer for validation and formatting
        """
        self.llm_client = llm_client
        self.channel_optimizer = channel_optimizer

    def _determine_channels(self, enrichment: dict) -> list[str]:
        """
        Determine available channels based on enrichment data.

        Args:
            enrichment: Enrichment data from Module 010

        Returns:
            List of available channels ("email", "linkedin", "twitter")

        Example:
            >>> stage = GenerationStage(llm_client, optimizer)
            >>> channels = stage._determine_channels({
            ...     "primary_email": "john@example.com",
            ...     "linkedin_username": "johndoe",
            ...     "twitter_username": None
            ... })
            >>> print(channels)
            ['email', 'linkedin']
        """
        channels = []

        # Check for email
        if enrichment.get("primary_email"):
            channels.append("email")

        # Check for LinkedIn
        if enrichment.get("linkedin_username"):
            channels.append("linkedin")

        # Check for Twitter
        if enrichment.get("twitter_username"):
            channels.append("twitter")

        return channels

    def generate(
        self,
        insights: dict,
        job_req: dict,
        enrichment: dict,
        channel: str,
        candidate: dict = None
    ) -> dict:
        """
        Generate outreach message for a specific channel.

        Args:
            insights: Analysis insights from Stage 1 (achievements, passion_areas, etc.)
            job_req: Job requirements (role, company, salary_range, etc.)
            enrichment: Enrichment data (email, linkedin, twitter, etc.)
            channel: Channel to generate for ("email", "linkedin", "twitter")

        Returns:
            Dictionary with generated message:
            {
                "subject_line": str (email only),
                "message_text": str,
                "channel": str,
                "is_valid": bool,
                "validation_errors": list[str],
                "tokens_used": int
            }

        Example:
            >>> stage = GenerationStage(llm_client, optimizer)
            >>> result = stage.generate(insights, job_req, enrichment, "email")
            >>> print(result["is_valid"])
            True
            >>> print(result["message_text"])
            "Hi Alex, I noticed your redis-clone project..."
        """
        try:
            # Build appropriate prompt based on channel
            if channel == "email":
                prompt = build_email_prompt(insights, job_req, enrichment, candidate)
            elif channel == "linkedin":
                prompt = build_linkedin_prompt(insights, job_req, enrichment, candidate)
            elif channel == "twitter":
                prompt = build_twitter_prompt(insights, job_req, enrichment, candidate)
            else:
                raise ValueError(f"Unsupported channel: {channel}")

            logger.info(f"Generating {channel} message using LLM")

            # Call LLM with JSON mode
            if hasattr(self.llm_client, 'complete'):
                if hasattr(self.llm_client, 'model'):
                    # OpenAI client with JSON mode
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=500 if channel == "email" else 250,
                        temperature=0.7,  # Higher temp for creativity
                        json_mode=True
                    )
                else:
                    # Anthropic or other client
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=500 if channel == "email" else 250,
                        temperature=0.7
                    )
            else:
                raise AttributeError("LLM client does not have 'complete' method")

            # Parse JSON response
            try:
                message_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                return self._create_fallback_message(channel, job_req)

            # Extract message based on channel
            if channel == "email":
                subject = message_data.get("subject_line", "")
                body = message_data.get("body", "")
                # Validate and format using ChannelOptimizer
                result = self.channel_optimizer.format_for_email(subject, body)
            elif channel == "linkedin":
                message_text = message_data.get("message", "")
                result = self.channel_optimizer.format_for_linkedin(message_text)
            elif channel == "twitter":
                message_text = message_data.get("message", "")
                result = self.channel_optimizer.format_for_twitter(message_text)

            # Calculate tokens used (estimate based on prompt + response length)
            tokens_used = (len(prompt) + len(response)) // 4
            result["tokens_used"] = tokens_used

            logger.info(f"{channel.capitalize()} generation complete: valid={result['is_valid']}, tokens={tokens_used}")

            return result

        except Exception as e:
            logger.error(f"Error during {channel} generation: {e}")
            return self._create_fallback_message(channel, job_req)

    def _create_fallback_message(self, channel: str, job_req: dict) -> dict:
        """
        Create fallback message when LLM generation fails.

        Args:
            channel: Channel to create fallback for
            job_req: Job requirements

        Returns:
            Basic message dictionary with is_valid=False
        """
        role = job_req.get("role_type", "Software Engineer")
        company = job_req.get("company_name", "Our Company")
        salary = job_req.get("salary_range", "Competitive salary")

        if channel == "email":
            subject = f"{role} opportunity at {company} - {salary}"
            body = " ".join([
                f"I came across your GitHub profile and was impressed by your work.",
                f"We're hiring for a {role} role at {company} with a salary range of {salary}.",
                "This could be a great opportunity to grow your career with us.",
                "Would you be interested in learning more?",
                "Let me know if you'd like to schedule a quick chat."
            ])
            return {
                "subject_line": subject,
                "message_text": body,
                "channel": "email",
                "is_valid": False,
                "validation_errors": ["LLM generation failed - using fallback"],
                "tokens_used": 0
            }
        elif channel == "linkedin":
            message = f"Hi! Saw your GitHub work. We're hiring for {role} at {company}, {salary}. Interested in chatting?"
            return {
                "message_text": message,
                "channel": "linkedin",
                "is_valid": False,
                "validation_errors": ["LLM generation failed - using fallback"],
                "tokens_used": 0
            }
        elif channel == "twitter":
            message = f"Impressed by your GitHub! {role} at {company}, {salary}. Interested?"
            return {
                "message_text": message,
                "channel": "twitter",
                "is_valid": False,
                "validation_errors": ["LLM generation failed - using fallback"],
                "tokens_used": 0
            }
        else:
            # Unsupported channel - return generic fallback
            return {
                "message_text": f"{role} at {company}, {salary}",
                "channel": channel,
                "is_valid": False,
                "validation_errors": [f"Unsupported channel: {channel}"],
                "tokens_used": 0
            }

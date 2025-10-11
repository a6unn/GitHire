"""
Stage 3: Refinement - Quality Validation and Polishing

This module implements the third stage of the 3-stage outreach pipeline.
Uses ClicheDetector, PersonalizationScorer, and optional LLM refinement
to ensure message quality.
"""

import json
import logging
import re
from typing import Optional

from src.jd_parser.llm_client import LLMClient
from ..cliche_detector import ClicheDetector
from ..personalization_scorer import PersonalizationScorer
from ..prompts.refinement_prompt import build_refinement_prompt


logger = logging.getLogger(__name__)


class RefinementStage:
    """
    Stage 3: Quality Validation and Message Refinement

    Refines generated messages by:
    1. Detecting and removing clichés
    2. Verifying specific repo mentions
    3. Verifying CTA clarity
    4. Calculating personalization score
    5. Setting quality flags if score < 70

    Can optionally use LLM for intelligent refinement.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient],
        cliche_detector: ClicheDetector,
        personalization_scorer: PersonalizationScorer
    ):
        """
        Initialize Refinement Stage.

        Args:
            llm_client: LLM client for intelligent refinement (optional)
            cliche_detector: ClicheDetector instance
            personalization_scorer: PersonalizationScorer instance
        """
        self.llm_client = llm_client
        self.cliche_detector = cliche_detector
        self.personalization_scorer = personalization_scorer

    def refine(
        self,
        message: dict,
        candidate: dict,
        enrichment: dict,
        insights: dict
    ) -> dict:
        """
        Refine and validate outreach message quality.

        Args:
            message: Generated message dict from Stage 2 (GenerationStage)
                - message_text: str
                - subject_line: Optional[str] (for email)
                - channel: str
            candidate: Candidate data (username, top_repos, etc.)
            enrichment: Enrichment data (email, linkedin, company, etc.)
            insights: Analysis insights from Stage 1

        Returns:
            Refined message dict with quality metadata:
            {
                "message_text": str,  # Refined message
                "subject_line": Optional[str],  # Refined subject (email only)
                "channel": str,
                "cliches_removed": list[str],
                "personalization_score": float,  # 0-100
                "personalization_breakdown": dict,
                "quality_flags": list[str],  # e.g., ["low_personalization"]
                "specific_mention_verified": bool,
                "cta_clarity_verified": bool,
                "tokens_used": int
            }

        Example:
            >>> stage = RefinementStage(llm_client, detector, scorer)
            >>> refined = stage.refine(message, candidate, enrichment, insights)
            >>> print(refined["personalization_score"])
            85
        """
        try:
            message_text = message.get("message_text", "")
            subject_line = message.get("subject_line")
            channel = message.get("channel", "email")

            tokens_used = 0

            # Step 1: Detect clichés
            detected_cliches = self.cliche_detector.detect(message_text)
            logger.info(f"Detected {len(detected_cliches)} clichés in message")

            # Step 2: Remove clichés (or use LLM for intelligent refinement)
            if detected_cliches:
                if self.llm_client:
                    # Use LLM for intelligent refinement
                    logger.info("Using LLM for intelligent cliché refinement")
                    refined_text, llm_tokens = self._llm_refine(
                        message_text,
                        candidate,
                        detected_cliches
                    )
                    tokens_used += llm_tokens
                else:
                    # Use simple removal
                    logger.info("Using simple cliché removal")
                    refined_text, _ = self.cliche_detector.remove(message_text)
            else:
                refined_text = message_text

            # Step 3: Verify specific mentions
            specific_mention_verified = self._verify_specific_mentions(
                refined_text,
                candidate
            )

            # Step 4: Verify CTA clarity
            cta_clarity_verified = self._verify_cta_clarity(refined_text)

            # Step 5: Calculate personalization score
            score, breakdown = self.personalization_scorer.score(
                refined_text,
                candidate,
                enrichment
            )

            # Step 6: Set quality flags
            quality_flags = []
            if score < 70:
                quality_flags.append("low_personalization")
            if not specific_mention_verified:
                quality_flags.append("no_specific_repo_mention")
            if not cta_clarity_verified:
                quality_flags.append("unclear_cta")

            logger.info(f"Refinement complete: score={score}, flags={quality_flags}")

            return {
                "message_text": refined_text,
                "subject_line": subject_line,  # Keep original subject
                "channel": channel,
                "cliches_removed": detected_cliches,
                "personalization_score": score,
                "personalization_breakdown": breakdown,
                "quality_flags": quality_flags,
                "specific_mention_verified": specific_mention_verified,
                "cta_clarity_verified": cta_clarity_verified,
                "tokens_used": tokens_used
            }

        except Exception as e:
            logger.error(f"Error during refinement: {e}")
            # Return original message with error flags
            return {
                "message_text": message.get("message_text", ""),
                "subject_line": message.get("subject_line"),
                "channel": message.get("channel", "email"),
                "cliches_removed": [],
                "personalization_score": 0,
                "personalization_breakdown": {},
                "quality_flags": ["refinement_error"],
                "specific_mention_verified": False,
                "cta_clarity_verified": False,
                "tokens_used": 0
            }

    def _llm_refine(
        self,
        message: str,
        candidate: dict,
        detected_cliches: list[str]
    ) -> tuple[str, int]:
        """
        Use LLM for intelligent message refinement.

        Args:
            message: Message text to refine
            candidate: Candidate data
            detected_cliches: List of detected clichés

        Returns:
            Tuple of (refined_message, tokens_used)
        """
        try:
            # Build refinement prompt
            prompt = build_refinement_prompt(message, candidate, detected_cliches)

            # Call LLM
            if hasattr(self.llm_client, 'complete'):
                if hasattr(self.llm_client, 'model'):
                    # OpenAI client
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=500,
                        temperature=0.5,  # Moderate creativity
                        json_mode=False  # Text output, not JSON
                    )
                else:
                    # Anthropic or other client
                    response = self.llm_client.complete(
                        prompt,
                        max_tokens=500,
                        temperature=0.5
                    )
            else:
                raise AttributeError("LLM client does not have 'complete' method")

            # Calculate tokens
            tokens_used = (len(prompt) + len(response)) // 4

            # Return refined message
            return (response.strip(), tokens_used)

        except Exception as e:
            logger.error(f"LLM refinement failed: {e}, falling back to simple removal")
            # Fallback to simple removal
            refined, _ = self.cliche_detector.remove(message)
            return (refined, 0)

    def _verify_specific_mentions(self, message: str, candidate: dict) -> bool:
        """
        Verify that message mentions at least one specific repository by name.

        Args:
            message: Message text
            candidate: Candidate data with top_repos

        Returns:
            True if at least one repo is mentioned
        """
        top_repos = candidate.get("top_repos", [])

        for repo in top_repos:
            repo_name = repo.get("name", "")
            if repo_name:
                # Check for repo name (case-insensitive, word boundary)
                pattern = re.compile(r'\b' + re.escape(repo_name) + r'\b', re.IGNORECASE)
                if pattern.search(message):
                    return True

        return False

    def _verify_cta_clarity(self, message: str) -> bool:
        """
        Verify that message has a clear call-to-action.

        Looks for action words: chat, discuss, connect, schedule, call, meeting
        Or link patterns: http://, calendly

        Args:
            message: Message text

        Returns:
            True if CTA is clear
        """
        # Check for action words
        action_words = [
            "chat", "discuss", "connect", "schedule", "call", "meeting",
            "talk", "speak", "conversation", "interested"
        ]

        message_lower = message.lower()
        for word in action_words:
            if re.search(r'\b' + word + r'\b', message_lower):
                return True

        # Check for link patterns
        if "http://" in message or "https://" in message or "calendly" in message_lower:
            return True

        return False

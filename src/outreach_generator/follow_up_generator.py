"""
Follow-Up Sequence Generator

This module generates personalized follow-up sequences for outreach messages.
Uses different "angles" to maintain engagement without being pushy:
- Day 3 (Reminder): Brief reminder with different repo mention
- Day 7 (Technical Challenge): Preview actual technical problem from role
- Day 14 (Soft Close): Final gentle close with opt-out option

Research shows that 2-3 follow-ups increase response rates by 50-80%.
"""

import logging
from typing import Optional
from datetime import datetime

from src.jd_parser.llm_client import LLMClient
from .models import OutreachMessage, FollowUpSequence, FollowUpAngle
from .prompts.followup_prompt import build_followup_prompt


logger = logging.getLogger(__name__)


class FollowUpGenerator:
    """
    Generates follow-up sequences for outreach messages.

    Creates 3 follow-ups with different angles:
    1. Day 3 (Reminder): Brief reminder + different repo mention
    2. Day 7 (Technical Challenge): Technical problem preview
    3. Day 14 (Soft Close): Final gentle close with opt-out

    Usage:
        >>> generator = FollowUpGenerator(llm_client)
        >>> follow_ups = generator.generate_sequence(outreach_message, job_req, candidate)
        >>> print(f"Generated {len(follow_ups)} follow-ups")
        Generated 3 follow-ups
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Follow-Up Generator.

        Args:
            llm_client: LLM client (OpenAI GPT-4 or Anthropic Claude)
        """
        self.llm_client = llm_client

    def generate_sequence(
        self,
        outreach_message: OutreachMessage,
        job_req: dict,
        candidate: dict
    ) -> list[FollowUpSequence]:
        """
        Generate 3-part follow-up sequence for an outreach message.

        Creates follow-ups with different angles:
        - Day 3: Reminder with different repo mention
        - Day 7: Technical challenge preview
        - Day 14: Soft close with opt-out

        Args:
            outreach_message: Original outreach message
            job_req: Job requirements (role, company, tech stack, etc.)
            candidate: Candidate data (username, repos, etc.)

        Returns:
            List of 3 FollowUpSequence objects

        Example:
            >>> generator = FollowUpGenerator(llm_client)
            >>> follow_ups = generator.generate_sequence(outreach_msg, job_req, candidate)
            >>> print(follow_ups[0].angle, follow_ups[0].scheduled_days_after)
            reminder 3
        """
        try:
            logger.info(f"Generating follow-up sequence for outreach message {outreach_message.shortlist_id}")

            follow_ups = []

            # Follow-Up 1: Day 3 (Reminder)
            followup_1 = self._generate_single_followup(
                outreach_message=outreach_message,
                job_req=job_req,
                candidate=candidate,
                sequence_num=1,
                scheduled_days_after=3,
                angle=FollowUpAngle.REMINDER
            )
            follow_ups.append(followup_1)

            # Follow-Up 2: Day 7 (Technical Challenge)
            followup_2 = self._generate_single_followup(
                outreach_message=outreach_message,
                job_req=job_req,
                candidate=candidate,
                sequence_num=2,
                scheduled_days_after=7,
                angle=FollowUpAngle.TECHNICAL_CHALLENGE
            )
            follow_ups.append(followup_2)

            # Follow-Up 3: Day 14 (Soft Close)
            followup_3 = self._generate_single_followup(
                outreach_message=outreach_message,
                job_req=job_req,
                candidate=candidate,
                sequence_num=3,
                scheduled_days_after=14,
                angle=FollowUpAngle.SOFT_CLOSE
            )
            follow_ups.append(followup_3)

            logger.info(f"Generated {len(follow_ups)} follow-ups")
            return follow_ups

        except Exception as e:
            logger.error(f"Error generating follow-up sequence: {e}")
            return []

    def _generate_single_followup(
        self,
        outreach_message: OutreachMessage,
        job_req: dict,
        candidate: dict,
        sequence_num: int,
        scheduled_days_after: int,
        angle: FollowUpAngle
    ) -> FollowUpSequence:
        """
        Generate a single follow-up message.

        Args:
            outreach_message: Original outreach message
            job_req: Job requirements
            candidate: Candidate data
            sequence_num: Sequence number (1-3)
            scheduled_days_after: Days after original message (3, 7, 14)
            angle: Follow-up angle (reminder, technical_challenge, soft_close)

        Returns:
            FollowUpSequence object
        """
        try:
            # Build prompt based on angle
            prompt = build_followup_prompt(
                original_message=outreach_message.message_text,
                job_req=job_req,
                candidate=candidate,
                sequence_num=sequence_num,
                angle=angle.value
            )

            # Call LLM
            if hasattr(self.llm_client, 'complete'):
                response = self.llm_client.complete(
                    prompt,
                    max_tokens=300,  # Follow-ups should be brief
                    temperature=0.7,  # Moderate creativity
                    json_mode=False  # Text output
                )
            else:
                raise AttributeError("LLM client does not have 'complete' method")

            # Create FollowUpSequence object
            follow_up = FollowUpSequence(
                outreach_message_id=outreach_message.shortlist_id,  # Will be DB ID in production
                sequence_number=sequence_num,
                scheduled_days_after=scheduled_days_after,
                message_text=response.strip(),
                angle=angle,
                generated_at=datetime.utcnow()
            )

            logger.info(f"Generated follow-up {sequence_num}: {angle.value}")
            return follow_up

        except Exception as e:
            logger.error(f"Error generating follow-up {sequence_num}: {e}")
            # Return empty follow-up as fallback
            return FollowUpSequence(
                outreach_message_id=outreach_message.shortlist_id,
                sequence_number=sequence_num,
                scheduled_days_after=scheduled_days_after,
                message_text="[Error generating follow-up]",
                angle=angle,
                generated_at=datetime.utcnow()
            )

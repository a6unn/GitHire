"""Main outreach generator that orchestrates all components."""

import logging
from typing import Optional
from datetime import datetime

from src.jd_parser.models import JobRequirement
from src.jd_parser.llm_client import LLMClient
from src.ranking_engine.models import RankedCandidate

from .models import OutreachMessage, PersonalizationMetadata, ToneStyle
from .personalization import PersonalizationEngine
from .content_validator import ContentValidator
from .prompts.formal_template import build_formal_prompt
from .prompts.casual_template import build_casual_prompt

logger = logging.getLogger(__name__)


class OutreachGenerator:
    """Generates personalized outreach messages for ranked candidates."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize outreach generator.

        Args:
            llm_client: LLM client for message generation (creates default OpenAI client if None)
        """
        if llm_client is None:
            from src.jd_parser.llm_client import OpenAIClient
            self.llm_client = OpenAIClient()
        else:
            self.llm_client = llm_client

        self.personalization_engine = PersonalizationEngine()
        self.content_validator = ContentValidator()

        logger.info("OutreachGenerator initialized")

    def generate(
        self,
        ranked_candidate: RankedCandidate,
        job_requirement: JobRequirement,
        tone: str = "formal"
    ) -> OutreachMessage:
        """
        Generate personalized outreach message for a single candidate.

        Args:
            ranked_candidate: Ranked candidate from Module 003
            job_requirement: Job requirements from Module 001
            tone: Message tone ("formal" or "casual")

        Returns:
            OutreachMessage with generated content and metadata
        """
        candidate = ranked_candidate.candidate
        logger.info(f"Generating outreach for {candidate.github_username} (rank {ranked_candidate.rank})")

        # Step 1: Analyze candidate and select repos
        relevant_repos = self.personalization_engine.select_relevant_repos(
            candidate,
            job_requirement
        )

        # Step 2: Determine personalization depth
        depth = self.personalization_engine.determine_personalization_depth(
            ranked_candidate.rank
        )

        # Step 3: Build LLM prompt
        candidate_name = candidate.name or candidate.github_username
        prompt = self._build_prompt(
            candidate_name=candidate_name,
            candidate_username=candidate.github_username,
            candidate_bio=candidate.bio or "",
            job_role=job_requirement.role or "Software Engineer",
            job_skills=job_requirement.required_skills,
            relevant_repos=relevant_repos,
            depth=depth,
            tone=tone
        )

        # Step 4: Generate message with LLM
        try:
            message_text = self.llm_client.complete(prompt, max_tokens=500, temperature=0.7, json_mode=False)
            tokens_used = len(message_text.split())  # Approximate token count
        except Exception as e:
            logger.error(f"LLM generation failed for {candidate.github_username}: {e}")
            # Fallback to generic message
            return self._create_fallback_message(
                candidate.github_username,
                ranked_candidate.rank,
                tone
            )

        # Step 5: Validate content
        is_valid, validation_errors = self.content_validator.validate(
            message_text,
            candidate
        )

        fallback_applied = False
        if not is_valid:
            logger.warning(
                f"Validation failed for {candidate.github_username}: {validation_errors}. "
                "Using fallback."
            )
            return self._create_fallback_message(
                candidate.github_username,
                ranked_candidate.rank,
                tone
            )

        # Step 6: Calculate confidence score
        confidence = self._calculate_confidence(
            candidate=candidate,
            relevant_repos=relevant_repos,
            validation_passed=is_valid
        )

        # Step 7: Build metadata
        metadata = self._build_metadata(
            relevant_repos=relevant_repos,
            matched_skills=ranked_candidate.score_breakdown.matched_skills,
            tone=tone,
            depth=depth,
            rank=ranked_candidate.rank
        )

        # Step 8: Create OutreachMessage
        outreach_message = OutreachMessage(
            candidate_username=candidate.github_username,
            rank=ranked_candidate.rank,
            message_text=message_text,
            tone=ToneStyle(tone),
            confidence_score=confidence,
            personalization_metadata=metadata,
            tokens_used=tokens_used,
            fallback_applied=fallback_applied,
            generated_at=datetime.now()
        )

        logger.info(
            f"Generated message for {candidate.github_username}: "
            f"confidence={confidence:.1f}, tokens={tokens_used}"
        )

        return outreach_message

    def generate_batch(
        self,
        ranked_candidates: list[RankedCandidate],
        job_requirement: JobRequirement,
        tone: str = "formal"
    ) -> list[OutreachMessage]:
        """
        Generate outreach messages for multiple candidates.

        Args:
            ranked_candidates: List of ranked candidates
            job_requirement: Job requirements
            tone: Message tone

        Returns:
            List of OutreachMessage objects
        """
        logger.info(f"Generating batch of {len(ranked_candidates)} messages")

        messages = []
        for ranked_candidate in ranked_candidates:
            message = self.generate(ranked_candidate, job_requirement, tone)
            messages.append(message)

        # Calculate diversity scores
        messages = self._calculate_diversity_scores(messages)

        logger.info(f"Batch generation complete: {len(messages)} messages")
        return messages

    def _build_prompt(
        self,
        candidate_name: str,
        candidate_username: str,
        candidate_bio: str,
        job_role: str,
        job_skills: list[str],
        relevant_repos: list[dict],
        depth: str,
        tone: str
    ) -> str:
        """Build appropriate prompt based on tone."""
        if tone == "casual":
            return build_casual_prompt(
                candidate_name,
                candidate_username,
                candidate_bio,
                job_role,
                job_skills,
                relevant_repos,
                depth
            )
        else:
            return build_formal_prompt(
                candidate_name,
                candidate_username,
                candidate_bio,
                job_role,
                job_skills,
                relevant_repos,
                depth
            )

    def _calculate_confidence(
        self,
        candidate,
        relevant_repos: list[dict],
        validation_passed: bool
    ) -> float:
        """
        Calculate confidence score for message quality.

        Based on:
        - Data availability (repos, bio, location)
        - Validation result
        """
        score = 60.0  # Base score

        # Repo availability
        if len(relevant_repos) >= 2:
            score += 20.0
        elif len(relevant_repos) == 1:
            score += 10.0
        else:
            score -= 20.0  # No repos reduces confidence

        # Profile completeness
        if candidate.bio:
            score += 10.0
        if candidate.location:
            score += 5.0
        if candidate.name:
            score += 5.0

        # Validation
        if not validation_passed:
            score -= 20.0

        # Clamp to 0-100
        return max(0.0, min(100.0, score))

    def _build_metadata(
        self,
        relevant_repos: list[dict],
        matched_skills: list[str],
        tone: str,
        depth: str,
        rank: int
    ) -> PersonalizationMetadata:
        """Build personalization metadata."""
        repo_names = [repo["name"] for repo in relevant_repos]

        tone_reason = f"Rank {rank} - {depth} personalization depth"

        return PersonalizationMetadata(
            referenced_repositories=repo_names,
            referenced_skills=matched_skills,
            tone_adjustment_reason=tone_reason,
            diversity_score=100.0  # Will be updated in batch processing
        )

    def _create_fallback_message(
        self,
        username: str,
        rank: int,
        tone: str
    ) -> OutreachMessage:
        """Create fallback message when generation/validation fails."""
        if tone == "casual":
            message_text = f"""Hi {username},

I came across your GitHub profile and wanted to reach out about an exciting opportunity. We're building something interesting and I think you might be a good fit.

Would love to chat more if you're open to it. Let me know!

Best"""
        else:
            message_text = f"""Dear {username},

I hope this message finds you well. I came across your GitHub profile and wanted to reach out regarding a potential opportunity that may align with your background.

I would appreciate the opportunity to discuss this further at your convenience. Please let me know if you would be interested in learning more.

Best regards"""

        metadata = PersonalizationMetadata(
            referenced_repositories=[],
            referenced_skills=[],
            tone_adjustment_reason=f"Fallback message - rank {rank}",
            diversity_score=50.0
        )

        return OutreachMessage(
            candidate_username=username,
            rank=rank,
            message_text=message_text,
            tone=ToneStyle(tone),
            confidence_score=30.0,  # Low confidence for fallback
            personalization_metadata=metadata,
            tokens_used=0,
            fallback_applied=True,
            generated_at=datetime.now()
        )

    def _calculate_diversity_scores(
        self,
        messages: list[OutreachMessage]
    ) -> list[OutreachMessage]:
        """
        Calculate diversity scores for messages in a batch.

        Measures how unique each message is compared to others.
        Simple implementation: check for repeated phrases.
        """
        if len(messages) <= 1:
            return messages

        # Extract message texts
        texts = [msg.message_text.lower() for msg in messages]

        # For each message, calculate uniqueness
        updated_messages = []
        for i, message in enumerate(messages):
            # Count how many other messages share common phrases
            current_text = texts[i]
            words = set(current_text.split())

            similarity_scores = []
            for j, other_text in enumerate(texts):
                if i == j:
                    continue

                other_words = set(other_text.split())
                overlap = len(words & other_words)
                total = len(words | other_words)

                similarity = (overlap / total) * 100 if total > 0 else 0
                similarity_scores.append(similarity)

            # Diversity = 100 - average similarity
            avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
            diversity = max(0.0, 100.0 - avg_similarity)

            # Update metadata with diversity score
            updated_metadata = PersonalizationMetadata(
                referenced_repositories=message.personalization_metadata.referenced_repositories,
                referenced_skills=message.personalization_metadata.referenced_skills,
                tone_adjustment_reason=message.personalization_metadata.tone_adjustment_reason,
                diversity_score=diversity
            )

            # Create new message with updated metadata
            updated_message = OutreachMessage(
                candidate_username=message.candidate_username,
                rank=message.rank,
                message_text=message.message_text,
                tone=message.tone,
                confidence_score=message.confidence_score,
                personalization_metadata=updated_metadata,
                tokens_used=message.tokens_used,
                fallback_applied=message.fallback_applied,
                generated_at=message.generated_at
            )
            updated_messages.append(updated_message)

        return updated_messages

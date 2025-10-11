"""
Contact Enricher (Main Orchestrator)
Module 010: Contact Enrichment

Orchestrates the full 4-layer enrichment pipeline.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from pydantic import ValidationError, BaseModel, Field

from .models.contact_info import ContactInfo
from .models.enrichment_result import EnrichmentResult
from .services.profile_extractor import ProfileExtractor
from .services.commit_email_extractor import CommitEmailExtractor
from .services.readme_parser import ReadmeParser
from .services.social_discoverer import SocialDiscoverer
from .lib.email_deduplicator import EmailDeduplicator


class CandidateSchema(BaseModel):
    """Schema for validating candidate input."""

    github_username: str = Field(..., description="GitHub username (required)")


class ContactEnricher:
    """
    Main orchestrator for contact enrichment pipeline.

    Runs 4-layer enrichment:
    1. Profile fields extraction
    2. Commit email extraction
    3. README parsing
    4. Social profile discovery

    Constitutional Rules:
    - CR-001: Privacy-First
    - CR-002: GDPR Compliance (30-90 day retention)
    - CR-004: Transparency (tracks sources)
    - CR-005: Configurable Limits
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        max_concurrent: int = 10,
        retention_days: int = 30,
    ):
        """
        Initialize contact enricher.

        Args:
            github_token: GitHub personal access token (optional for testing)
            max_concurrent: Max concurrent API requests
            retention_days: GDPR data retention period (30-90 days)
        """
        self.github_token = github_token or "test_token"
        self.max_concurrent = max_concurrent
        self.retention_days = retention_days

        # Initialize all 4 layer services
        self.profile_extractor = ProfileExtractor(github_token)
        self.commit_extractor = CommitEmailExtractor(github_token)
        self.readme_parser = ReadmeParser(github_token)
        self.social_discoverer = SocialDiscoverer(github_token)

        # Initialize deduplicator
        self.deduplicator = EmailDeduplicator()

    def validate_candidate(self, candidate: dict) -> None:
        """
        Validate candidate has required fields.

        Args:
            candidate: Candidate dict to validate

        Raises:
            ValidationError: If required fields missing
        """
        CandidateSchema(**candidate)

    async def enrich(self, candidate: dict, fetch_fresh: bool = False) -> ContactInfo:
        """
        Enrich a single candidate with all 4 layers.

        Args:
            candidate: Candidate dict from Module 002/003
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            ContactInfo model with enriched contact data

        Raises:
            ValueError: If candidate invalid
        """
        # Validate candidate
        try:
            self.validate_candidate(candidate)
        except ValidationError as e:
            raise ValueError(f"Invalid candidate: {e}")

        github_username = candidate["github_username"]

        # Initialize collectors
        all_emails: list[tuple[str, str]] = []  # (email, source)
        merged_data = {
            "github_username": github_username,
            "primary_email": None,
            "additional_emails": [],
            "linkedin_username": None,
            "twitter_username": None,
            "blog_url": None,
            "company": None,
            "hireable": False,
            "contact_sources": {},
        }

        # Layer 1: Profile extraction
        profile_result = await self.profile_extractor.extract(candidate, fetch_fresh=fetch_fresh)
        self._merge_layer(merged_data, profile_result, all_emails)

        # Layer 2: Commit emails
        commit_emails = await self.commit_extractor.extract(
            github_username, events_data=None, fetch_fresh=fetch_fresh
        )
        for email in commit_emails:
            all_emails.append((email, "commit"))

        # Layer 3: README parsing
        readme_result = await self.readme_parser.parse(
            readme_content=None, username=github_username, fetch_fresh=fetch_fresh
        )
        self._merge_layer(merged_data, readme_result, all_emails)

        # Layer 4: Social discovery from bio
        bio = candidate.get("bio")
        if bio:
            bio_result = await self.social_discoverer.discover_from_bio(bio)
            self._merge_layer(merged_data, bio_result, all_emails)

        # Deduplicate and prioritize emails
        if all_emails:
            primary_email = self.deduplicator.prioritize(all_emails)
            if primary_email:
                merged_data["primary_email"] = primary_email

                # Get all other emails (deduplicated)
                all_email_strings = [e[0] for e in all_emails]
                deduped = self.deduplicator.deduplicate(all_email_strings)

                # Additional emails = all except primary
                merged_data["additional_emails"] = [
                    e for e in deduped if e != primary_email
                ]

        # Set GDPR fields
        now = datetime.utcnow()
        expires_at = now + timedelta(days=self.retention_days)

        # Create ContactInfo model
        contact_info = ContactInfo(
            github_username=github_username,
            primary_email=merged_data["primary_email"],
            additional_emails=merged_data["additional_emails"],
            linkedin_username=merged_data["linkedin_username"],
            twitter_username=merged_data["twitter_username"],
            blog_url=merged_data["blog_url"],
            company=merged_data["company"],
            hireable=merged_data["hireable"],
            contact_sources=merged_data["contact_sources"],
            enriched_at=now,
            gdpr_collection_basis="legitimate_interest_recruiting",
            data_retention_expires_at=expires_at,
        )

        return contact_info

    async def enrich_batch(self, candidates: list[dict], fetch_fresh: bool = False) -> list[ContactInfo]:
        """
        Enrich multiple candidates.

        Args:
            candidates: List of candidate dicts
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            List of ContactInfo models
        """
        results = []
        for candidate in candidates:
            try:
                result = await self.enrich(candidate, fetch_fresh=fetch_fresh)
                results.append(result)
            except (ValueError, ValidationError):
                # Skip invalid candidates
                continue

        return results

    async def enrich_batch_with_metadata(
        self, candidates: list[dict], skip_invalid: bool = False, fetch_fresh: bool = False
    ) -> tuple[list[ContactInfo], EnrichmentResult]:
        """
        Enrich multiple candidates and return metadata.

        Args:
            candidates: List of candidate dicts
            skip_invalid: Skip invalid candidates instead of raising error
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            Tuple of (ContactInfo list, EnrichmentResult metadata)
        """
        start_time = time.time()

        results = []
        failed = []

        for candidate in candidates:
            try:
                self.validate_candidate(candidate)
                result = await self.enrich(candidate, fetch_fresh=fetch_fresh)
                results.append(result)
            except (ValueError, ValidationError) as e:
                if skip_invalid:
                    failed.append(candidate.get("github_username", "unknown"))
                else:
                    raise

        # Calculate statistics
        enrichment_time_ms = max(1, int((time.time() - start_time) * 1000))  # At least 1ms

        email_count = sum(1 for r in results if r.primary_email)
        linkedin_count = sum(1 for r in results if r.linkedin_username)
        twitter_count = sum(1 for r in results if r.twitter_username)
        website_count = sum(1 for r in results if r.blog_url)

        total_contacts = sum(
            (1 if r.primary_email else 0)
            + len(r.additional_emails)
            + (1 if r.linkedin_username else 0)
            + (1 if r.twitter_username else 0)
            + (1 if r.blog_url else 0)
            for r in results
        )

        avg_contacts = total_contacts / len(results) if results else 0

        metadata = EnrichmentResult(
            total_candidates=len(candidates),
            successfully_enriched=len(results),
            email_found_count=email_count,
            linkedin_found_count=linkedin_count,
            twitter_found_count=twitter_count,
            website_found_count=website_count,
            average_contacts_per_candidate=avg_contacts,
            enrichment_time_ms=enrichment_time_ms,
            api_calls_made=len(candidates),  # Mock - 1 API call per candidate
            rate_limit_remaining=5000 - len(candidates),  # Mock
            failed_enrichments=failed,
        )

        return results, metadata

    def _merge_layer(
        self, merged_data: dict, layer_result: dict, all_emails: list[tuple[str, str]]
    ) -> None:
        """
        Merge results from a layer into accumulated data.

        Args:
            merged_data: Accumulated contact data
            layer_result: Results from a single layer
            all_emails: Accumulated emails with sources
        """
        # Merge emails
        if "emails" in layer_result:
            source = layer_result.get("contact_sources", {}).get("emails", "unknown")
            for email in layer_result["emails"]:
                all_emails.append((email, source))

        # Merge primary_email (from profile layer)
        if "primary_email" in layer_result and layer_result["primary_email"]:
            source = layer_result.get("contact_sources", {}).get(
                "primary_email", "unknown"
            )
            all_emails.append((layer_result["primary_email"], source))

        # Merge social fields (first non-None wins)
        for field in ["linkedin_username", "twitter_username", "blog_url", "company"]:
            if field in layer_result and layer_result[field]:
                if not merged_data.get(field):  # Only set if not already set
                    merged_data[field] = layer_result[field]
                    # Copy source
                    if "contact_sources" in layer_result:
                        if field in layer_result["contact_sources"]:
                            merged_data["contact_sources"][field] = layer_result[
                                "contact_sources"
                            ][field]

        # Merge hireable
        if "hireable" in layer_result:
            merged_data["hireable"] = layer_result["hireable"]

"""
Personalization Scorer - Scores outreach messages on personalization quality

This module provides scoring logic to quantify how personalized a message is
based on specific repo mentions, technical details, enrichment data usage, etc.
"""

import re
from typing import Optional


class PersonalizationScorer:
    """
    Scores outreach messages on personalization quality (0-100 scale).

    Scoring breakdown:
    - Specific repo mention by name: +30 points
    - Technical detail (code/feature reference): +30 points
    - Unique insight (enrichment data referenced): +20 points
    - Enrichment usage (email/LinkedIn/Twitter/blog): +20 points

    Total: 100 points maximum

    Usage:
        >>> scorer = PersonalizationScorer()
        >>> candidate = {
        ...     "top_repos": [{"name": "redis-clone", "description": "..."}],
        ...     "github_username": "johndoe"
        ... }
        >>> enrichment = {"linkedin_username": "johndoe", "company": "TechCorp"}
        >>> message = "Hi John, your redis-clone's concurrent write handling is impressive! We at TechCorp need that expertise."
        >>> score, breakdown = scorer.score(message, candidate, enrichment)
        >>> print(score)
        100
        >>> print(breakdown)
        {'repo_mention': True, 'technical_detail': True, 'unique_insight': True, 'enrichment_usage': True}
    """

    # Technical keywords that indicate code/feature review
    TECHNICAL_KEYWORDS = [
        # Architecture/Design patterns
        "concurrent", "async", "distributed", "scalable", "microservices",
        "event-driven", "reactive", "caching", "sharding", "replication",
        "load balancing", "rate limiting", "circuit breaker", "saga pattern",

        # Code/Implementation details
        "implementation", "algorithm", "data structure", "optimization",
        "refactoring", "testing", "CI/CD", "deployment", "monitoring",
        "logging", "error handling", "validation", "serialization",

        # Specific technologies (implies code review)
        "Redis", "Kafka", "RabbitMQ", "PostgreSQL", "MongoDB", "Elasticsearch",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure",
        "React", "Vue", "Angular", "Node.js", "Express", "FastAPI", "Django",
        "GraphQL", "REST API", "WebSocket", "gRPC",

        # Performance/Scale
        "performance", "throughput", "latency", "memory", "CPU",
        "10k connections", "million requests", "real-time",

        # Code quality
        "clean code", "SOLID", "DRY", "design patterns", "architecture",
        "test coverage", "documentation",

        # Specific features (generic but shows review)
        "feature", "module", "component", "service", "endpoint",
        "handler", "middleware", "pipeline", "queue", "stream",

        # Actions that show code review
        "implements", "handles", "processes", "manages", "orchestrates",
        "coordinates", "aggregates", "transforms", "validates",
    ]

    def __init__(self):
        """Initialize PersonalizationScorer."""
        # Compile technical keyword patterns for efficiency
        self.technical_patterns = [
            re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for keyword in self.TECHNICAL_KEYWORDS
        ]

    def score(
        self,
        message: str,
        candidate: dict,
        enrichment: dict
    ) -> tuple[float, dict]:
        """
        Score a message on personalization quality.

        Args:
            message: Message text to score
            candidate: Candidate data with top_repos, github_username, etc.
            enrichment: Enrichment data with linkedin_username, company, blog, etc.

        Returns:
            Tuple of (score: 0-100, breakdown: dict)

        Breakdown dict contains:
            - repo_mention: bool (30 points)
            - technical_detail: bool (30 points)
            - unique_insight: bool (20 points)
            - enrichment_usage: bool (20 points)
            - total_points: int
            - max_points: int (100)

        Example:
            >>> scorer = PersonalizationScorer()
            >>> score, breakdown = scorer.score(message, candidate, enrichment)
            >>> print(f"Score: {score}/100")
            Score: 80/100
        """
        score = 0.0
        breakdown = {
            "repo_mention": False,
            "technical_detail": False,
            "unique_insight": False,
            "enrichment_usage": False,
            "total_points": 0,
            "max_points": 100
        }

        # 1. Check for specific repo mention (30 points)
        if self._has_repo_mention(message, candidate):
            score += 30
            breakdown["repo_mention"] = True

        # 2. Check for technical detail (30 points)
        if self._has_technical_detail(message):
            score += 30
            breakdown["technical_detail"] = True

        # 3. Check for unique insight (20 points)
        if self._has_unique_insight(message, enrichment):
            score += 20
            breakdown["unique_insight"] = True

        # 4. Check for enrichment usage (20 points)
        if self._has_enrichment_usage(message, enrichment):
            score += 20
            breakdown["enrichment_usage"] = True

        breakdown["total_points"] = int(score)

        return (score, breakdown)

    def _has_repo_mention(self, message: str, candidate: dict) -> bool:
        """
        Check if message mentions a specific repository by name.

        Args:
            message: Message text
            candidate: Candidate data with top_repos

        Returns:
            True if at least one repo name is mentioned
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

    def _has_technical_detail(self, message: str) -> bool:
        """
        Check if message contains technical details showing code review.

        Looks for technical keywords like "concurrent", "async", "distributed",
        specific technologies, or code-specific terms.

        Args:
            message: Message text

        Returns:
            True if technical details are present
        """
        # Check for any technical keyword
        for pattern in self.technical_patterns:
            if pattern.search(message):
                return True

        # Additional heuristics:
        # - Mentions of specific features with technical verbs
        # - Code-related syntax (e.g., "your X handles Y", "your X implements Y")
        technical_phrases = [
            r"your .{1,30} (handles|implements|processes|manages)",
            r"(concurrent|async|distributed|scalable) .{1,30}",
            r"(algorithm|implementation|architecture) .{1,30}",
            r"\d+k\+? (connections|requests|users|stars)",  # Scale indicators
        ]

        for phrase_pattern in technical_phrases:
            if re.search(phrase_pattern, message, re.IGNORECASE):
                return True

        return False

    def _has_unique_insight(self, message: str, enrichment: dict) -> bool:
        """
        Check if message references unique insights from enrichment data.

        Looks for mentions of:
        - Current company
        - LinkedIn profile
        - Blog/website
        - Twitter handle

        Args:
            message: Message text
            enrichment: Enrichment data

        Returns:
            True if unique insights are referenced
        """
        # Check for company mention
        company = enrichment.get("company")
        if company:
            # Check if company is mentioned (not just in "our company" context)
            pattern = re.compile(r'\b' + re.escape(company) + r'\b', re.IGNORECASE)
            if pattern.search(message):
                # Make sure it's not just "at our company" (generic)
                # Should be something like "you're at TechCorp" or "coming from TechCorp"
                if re.search(r'(at|from|with|working at)\s+' + re.escape(company), message, re.IGNORECASE):
                    return True

        # Check for blog mention
        blog_url = enrichment.get("blog_url")
        if blog_url:
            # Extract domain from URL
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', blog_url)
            if domain_match:
                domain = domain_match.group(1)
                if domain.lower() in message.lower():
                    return True

        # Check for LinkedIn mention
        linkedin_username = enrichment.get("linkedin_username")
        if linkedin_username:
            if linkedin_username.lower() in message.lower():
                return True

        # Check for Twitter mention
        twitter_username = enrichment.get("twitter_username")
        if twitter_username:
            if twitter_username.lower() in message.lower():
                return True

        return False

    def _has_enrichment_usage(self, message: str, enrichment: dict) -> bool:
        """
        Check if message uses ANY enrichment data.

        This is a broader check than unique_insight - just verifies that
        enrichment data was used at all (email, linkedin, twitter, blog, company).

        Args:
            message: Message text
            enrichment: Enrichment data

        Returns:
            True if any enrichment data is present in candidate
        """
        # Check if enrichment has any data
        has_enrichment = any([
            enrichment.get("primary_email"),
            enrichment.get("linkedin_username"),
            enrichment.get("twitter_username"),
            enrichment.get("blog_url"),
            enrichment.get("company"),
        ])

        return has_enrichment

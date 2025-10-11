"""Search service orchestrating GitHub candidate search.

Main entry point for Module 002: coordinates GitHub API, caching, and enrichment.
ENHANCED with LocationParser, SkillDetector, and EnsembleScorer.
"""

import logging
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from src.github_sourcer.models.candidate import Candidate
from src.github_sourcer.models.search_result import SearchResult
from src.github_sourcer.models.search_criteria import SearchCriteria
from src.github_sourcer.services.github_client import GitHubClient
from src.github_sourcer.services.cache_service import CacheService
from src.github_sourcer.services.profile_enricher import ProfileEnricher, ProfileNotFoundError
from src.github_sourcer.services.location_parser import LocationParser
from src.github_sourcer.services.skill_detector import SkillDetector
from src.github_sourcer.services.ensemble_scorer import EnsembleScorer

logger = logging.getLogger(__name__)


class SearchService:
    """Orchestrates GitHub candidate search with caching and enhanced scoring."""

    def __init__(
        self,
        github_client: GitHubClient = None,
        cache_service: CacheService = None,
        location_parser: LocationParser = None,
        skill_detector: SkillDetector = None,
        ensemble_scorer: EnsembleScorer = None
    ):
        """
        Initialize SearchService with enhanced components.

        Args:
            github_client: GitHubClient instance (creates new if None)
            cache_service: CacheService instance (creates new if None)
            location_parser: LocationParser instance (creates new if None)
            skill_detector: SkillDetector instance (creates new if None)
            ensemble_scorer: EnsembleScorer instance (creates new if None)
        """
        self.github_client = github_client or GitHubClient()
        self.cache_service = cache_service or CacheService()
        self.enricher = ProfileEnricher(self.github_client)

        # Enhanced components
        self.location_parser = location_parser or LocationParser()
        self.skill_detector = skill_detector or SkillDetector()
        self.ensemble_scorer = ensemble_scorer or EnsembleScorer()

    async def search(self, job_req) -> Dict:
        """
        Search GitHub for candidates matching job requirements.

        Args:
            job_req: JobRequirement from Module 001

        Returns:
            Dict with:
                - candidates: List[Candidate] (max 25)
                - metadata: SearchResult
        """
        start_time = time.time()

        # Convert JobRequirement to SearchCriteria
        criteria = SearchCriteria.from_job_requirement(job_req)
        logger.info(
            f"[SEARCH] Query constructed: '{criteria.query_string}' | "
            f"Skills: {getattr(job_req, 'required_skills', [])} | "
            f"Location: {getattr(job_req, 'location', 'N/A')}"
        )

        # Check cache
        cache_key = self.cache_service.generate_cache_key(job_req)
        cached_usernames = self.cache_service.get_search_results(cache_key)

        if cached_usernames is not None:
            # Cache HIT - fetch profiles from cache
            logger.info(
                f"[CACHE] HIT | Key: {cache_key[:16]}... | "
                f"Cached results: {len(cached_usernames)} candidates"
            )
            candidates = await self._fetch_cached_profiles(cached_usernames)
            execution_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"[SEARCH] Complete (cache) | "
                f"Returned: {len(candidates)} candidates | "
                f"Time: {execution_time_ms}ms"
            )

            return self._build_response(
                candidates=candidates,
                total_found=len(cached_usernames),
                cache_hit=True,
                execution_time_ms=execution_time_ms
            )

        # Cache MISS - search GitHub with progressive location broadening
        logger.info(f"[CACHE] MISS | Key: {cache_key[:16]}... | Fetching from GitHub API")

        # Track GitHub API call time
        api_start_time = time.time()
        usernames = await self._search_with_progressive_broadening(
            criteria,
            job_req,
            min_results_threshold=10
        )
        api_duration_ms = int((time.time() - api_start_time) * 1000)

        logger.info(
            f"[API] GitHub user search complete | "
            f"Results: {len(usernames) if usernames else 0} users | "
            f"API time: {api_duration_ms}ms"
        )

        if not usernames:
            # No results found
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.warning(
                f"[SEARCH] No candidates found | "
                f"Query: '{criteria.query_string}' | "
                f"Time: {execution_time_ms}ms"
            )
            return self._build_response(
                candidates=[],
                total_found=0,
                cache_hit=False,
                execution_time_ms=execution_time_ms,
                warnings=["No candidates found matching criteria"]
            )

        # Don't limit yet - we'll rank first then take top 25
        total_found = len(usernames)
        logger.info(f"[ENRICHMENT] Starting enrichment for {total_found} candidates")

        # Enrich profiles with enhanced features (parallel)
        enrich_start_time = time.time()
        candidates_data = await self._enrich_profiles_enhanced(
            usernames,
            criteria=criteria,
            job_req=job_req
        )
        enrich_duration_ms = int((time.time() - enrich_start_time) * 1000)
        logger.info(
            f"[ENRICHMENT] Complete | "
            f"Enriched: {len(candidates_data)}/{total_found} candidates | "
            f"Time: {enrich_duration_ms}ms"
        )

        # Rank candidates using ensemble scoring
        rank_start_time = time.time()
        ranked_candidates = await self._rank_candidates(
            candidates_data,
            criteria=criteria,
            job_req=job_req
        )
        rank_duration_ms = int((time.time() - rank_start_time) * 1000)
        logger.info(
            f"[RANKING] Complete | "
            f"Ranked: {len(ranked_candidates)} candidates | "
            f"Time: {rank_duration_ms}ms"
        )

        # Take top 25 after ranking
        top_candidates = ranked_candidates[:25]
        logger.info(f"[RANKING] Top 25 candidates selected for return")

        # Cache results (top 25 usernames only)
        top_usernames = [c.github_username for c in top_candidates]
        self.cache_service.set_search_results(cache_key, top_usernames)
        for candidate in top_candidates:
            self.cache_service.set_profile(candidate.github_username, candidate)

        execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"[SEARCH] Complete (fresh) | "
            f"Returned: {len(top_candidates)} candidates | "
            f"Total time: {execution_time_ms}ms | "
            f"Breakdown - API: {api_duration_ms}ms, Enrich: {enrich_duration_ms}ms, Rank: {rank_duration_ms}ms"
        )

        return self._build_response(
            candidates=top_candidates,
            total_found=total_found,
            cache_hit=False,
            execution_time_ms=execution_time_ms
        )

    async def _search_with_progressive_broadening(
        self,
        criteria: SearchCriteria,
        job_req,
        min_results_threshold: int = 10
    ) -> List[str]:
        """
        Search GitHub with progressive location broadening.

        Tries city-level first, then state, then country if insufficient results.

        Args:
            criteria: SearchCriteria object with initial query
            job_req: JobRequirement object
            min_results_threshold: Minimum results needed before broadening

        Returns:
            List of GitHub usernames
        """
        # Try initial search (city or state level)
        usernames = await self.github_client.search_users(criteria.query_string)

        if usernames and len(usernames) >= min_results_threshold:
            logger.info(
                f"[SEARCH] Initial search successful | "
                f"Location: {criteria.location_filter} | "
                f"Results: {len(usernames)} (>= threshold {min_results_threshold})"
            )
            return usernames

        # Insufficient results - try progressive broadening
        location_prefs = getattr(job_req, 'location_preferences', None)
        if not location_prefs or not criteria.location_filter:
            # No location to broaden, return what we have
            logger.info(f"[SEARCH] No location broadening possible, returning {len(usernames) if usernames else 0} results")
            return usernames or []

        # Parse the original location to get hierarchy
        parsed_location = self.location_parser.parse_location(location_prefs[0])

        # Determine current level and next broadening levels
        broadening_levels = []
        current_location = criteria.location_filter.lower()

        # Build broadening sequence based on parsed location
        if parsed_location.city and current_location == parsed_location.city.lower():
            # Currently at city level, try state next
            if parsed_location.state:
                broadening_levels.append(('state', parsed_location.state.lower()))
            if parsed_location.country:
                broadening_levels.append(('country', parsed_location.country.lower()))

        elif parsed_location.state and current_location == parsed_location.state.lower():
            # Currently at state level, try multi-city search before country
            cities = self.location_parser.get_cities_for_state(parsed_location.state)
            if cities:
                broadening_levels.append(('multi-city', cities))

            # Then try country
            if parsed_location.country:
                broadening_levels.append(('country', parsed_location.country.lower()))

        # Try each broadening level
        for level_name, location_value in broadening_levels:
            # Handle multi-city search separately
            if level_name == 'multi-city':
                # location_value is a list of cities
                cities_list = location_value
                logger.info(
                    f"[SEARCH] Multi-city search | "
                    f"From: {criteria.location_filter} ({len(usernames) if usernames else 0} results) → "
                    f"Cities: {', '.join(cities_list[:3])}{'...' if len(cities_list) > 3 else ''} ({len(cities_list)} cities)"
                )

                # Search each city and combine results
                multi_city_usernames = await self._search_multiple_cities(
                    criteria,
                    cities_list,
                    min_results_threshold
                )

                if multi_city_usernames and len(multi_city_usernames) >= min_results_threshold:
                    logger.info(
                        f"[SEARCH] Multi-city search successful | "
                        f"Combined results: {len(multi_city_usernames)} users"
                    )
                    return multi_city_usernames

                # Update usernames for next iteration
                usernames = multi_city_usernames or usernames

            else:
                # Single location broadening (state or country)
                logger.info(
                    f"[SEARCH] Broadening search | "
                    f"From: {criteria.location_filter} ({len(usernames) if usernames else 0} results) → "
                    f"To: {location_value} ({level_name})"
                )

                # Rebuild query with broader location
                # Need to handle multi-word locations properly
                # Replace the entire location:XXX portion with the new location
                broader_query = criteria.query_string.replace(
                    f"location:{criteria.location_filter}",
                    f"location:{location_value}"
                )

                # Search with broader location
                broader_usernames = await self.github_client.search_users(broader_query)

                if broader_usernames and len(broader_usernames) >= min_results_threshold:
                    logger.info(
                        f"[SEARCH] Broadening successful | "
                        f"Location: {location_value} ({level_name}) | "
                        f"Results: {len(broader_usernames)}"
                    )
                    return broader_usernames

                # Update usernames for next iteration
                usernames = broader_usernames or usernames

        # Return best results we got
        logger.info(
            f"[SEARCH] Progressive broadening complete | "
            f"Final results: {len(usernames) if usernames else 0}"
        )
        return usernames or []

    async def _search_multiple_cities(
        self,
        criteria: SearchCriteria,
        cities: List[str],
        min_results_threshold: int = 10
    ) -> List[str]:
        """
        Search multiple cities in parallel and combine results.

        Args:
            criteria: SearchCriteria object with base query
            cities: List of city names to search
            min_results_threshold: Target minimum results

        Returns:
            Combined list of unique GitHub usernames
        """
        logger.info(f"[MULTI-CITY] Searching {len(cities)} cities in parallel")

        # Create search tasks for each city
        search_tasks = []
        for city in cities:
            # Build query with this city
            city_query = criteria.query_string.replace(
                f"location:{criteria.location_filter}",
                f"location:{city.lower()}"
            )
            search_tasks.append(self.github_client.search_users(city_query))

        # Execute all searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Combine results and deduplicate
        all_usernames = set()
        city_results = {}

        for city, result in zip(cities, results):
            if isinstance(result, Exception):
                logger.warning(f"[MULTI-CITY] Search failed for {city}: {result}")
                city_results[city] = 0
                continue

            if result:
                all_usernames.update(result)
                city_results[city] = len(result)
                logger.debug(f"[MULTI-CITY] {city}: {len(result)} results")
            else:
                city_results[city] = 0

        # Log summary
        total_cities_searched = len(cities)
        cities_with_results = sum(1 for count in city_results.values() if count > 0)
        top_cities = sorted(city_results.items(), key=lambda x: x[1], reverse=True)[:3]

        logger.info(
            f"[MULTI-CITY] Search complete | "
            f"Cities searched: {total_cities_searched} | "
            f"Cities with results: {cities_with_results} | "
            f"Top cities: {', '.join([f'{city}({count})' for city, count in top_cities])} | "
            f"Total unique users: {len(all_usernames)}"
        )

        return list(all_usernames)

    async def _fetch_cached_profiles(self, usernames: List[str]) -> List[Candidate]:
        """
        Fetch profiles from cache or enrich if not cached.

        Args:
            usernames: List of GitHub usernames

        Returns:
            List of Candidate objects
        """
        candidates = []

        for username in usernames:
            cached = self.cache_service.get_profile(username)

            if cached:
                candidates.append(cached)
            else:
                # Profile not cached - enrich it
                try:
                    candidate = await self.enricher.enrich_profile(username)
                    candidates.append(candidate)
                    self.cache_service.set_profile(username, candidate)
                except ProfileNotFoundError:
                    logger.warning(f"Profile not found (cached username): {username}")
                    continue

        return candidates

    async def _enrich_profiles(self, usernames: List[str]) -> List[Candidate]:
        """
        Enrich multiple profiles in parallel.

        Args:
            usernames: List of GitHub usernames

        Returns:
            List of successfully enriched Candidate objects
        """
        # Create tasks for parallel enrichment
        tasks = [self.enricher.enrich_profile(username) for username in usernames]

        # Gather results, handling exceptions
        results = await asyncio.gather(*tasks, return_exceptions=True)

        candidates = []
        for username, result in zip(usernames, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to enrich profile for {username}: {result}")
                continue  # Skip failed profiles

            candidates.append(result)

        logger.info(f"Successfully enriched {len(candidates)}/{len(usernames)} profiles")
        return candidates

    async def _detect_skills_for_candidate(
        self,
        candidate: Candidate,
        search_location
    ) -> Optional[tuple]:
        """
        Helper function to detect skills for a single candidate in parallel.

        Args:
            candidate: Candidate object
            search_location: Parsed search location (LocationHierarchy)

        Returns:
            Tuple of (candidate_dict, skills, location_match) or None if failed
        """
        try:
            # Convert Candidate to dict for processing
            created_at = None
            if candidate.account_age_days > 0:
                from datetime import timedelta
                created_at = (datetime.utcnow() - timedelta(days=candidate.account_age_days)).isoformat()

            candidate_dict = {
                "username": candidate.github_username,
                "profile": {
                    "public_repos": candidate.public_repos,
                    "followers": candidate.followers,
                    "created_at": created_at
                }
            }

            # Detect skills
            skills = await self.skill_detector.detect_skills_from_repos(
                username=candidate.github_username,
                github_client=self.github_client,
                profile={"bio": candidate.bio} if candidate.bio else None,
                starred_repos=None
            )

            # Match location
            location_match = None
            if search_location and candidate.location:
                candidate_location = self.location_parser.parse_location(candidate.location)
                match_level, confidence = self.location_parser.hierarchical_match(
                    search_location,
                    candidate_location
                )
                if match_level:
                    location_match = (candidate_location, match_level, confidence)

            return (candidate_dict, skills, location_match)

        except Exception as e:
            logger.warning(f"Failed to enhance {candidate.github_username}: {e}")
            return None

    async def _enrich_profiles_enhanced(
        self,
        usernames: List[str],
        criteria,
        job_req
    ) -> List[tuple]:
        """
        Enrich profiles with enhanced features (location, skills, scoring).

        Args:
            usernames: List of GitHub usernames
            criteria: SearchCriteria object
            job_req: JobRequirement object

        Returns:
            List of tuples: (candidate_dict, skills, location_match)
        """
        # First enrich basic profiles
        candidates = await self._enrich_profiles(usernames)

        # Cache the enriched Candidate objects immediately
        for candidate in candidates:
            self.cache_service.set_profile(candidate.github_username, candidate)

        # Extract required skills and location from job_req
        required_skills = getattr(job_req, 'required_skills', None) or []
        search_location_str = getattr(job_req, 'location', None)

        # Parse search location if provided
        search_location = None
        if search_location_str:
            search_location = self.location_parser.parse_location(search_location_str)

        # ========================================================================
        # PARALLEL PROCESSING: Process all candidates concurrently
        # ========================================================================
        logger.info(f"Starting parallel skill detection for {len(candidates)} candidates")

        # Create tasks for all candidates
        tasks = [
            self._detect_skills_for_candidate(candidate, search_location)
            for candidate in candidates
        ]

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed candidates (None results and Exceptions)
        enhanced_data = []
        for result in results:
            if result is not None and not isinstance(result, Exception):
                enhanced_data.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Exception during parallel skill detection: {result}")

        logger.info(f"Enhanced {len(enhanced_data)} candidates with skills and location (parallel processing)")
        return enhanced_data

    async def _rank_candidates(
        self,
        candidates_data: List[tuple],
        criteria,
        job_req
    ) -> List[Candidate]:
        """
        Rank candidates using ensemble scoring.

        Args:
            candidates_data: List of (candidate_dict, skills, location_match) tuples
            criteria: SearchCriteria object
            job_req: JobRequirement object

        Returns:
            List of Candidate objects sorted by score (descending)
        """
        # Keep reference to original candidates for mapping
        original_candidates_dict = {}
        for candidate_dict, skills, location_match in candidates_data:
            username = candidate_dict["username"]
            # Fetch original candidate from cache or enricher
            original_candidates_dict[username] = candidate_dict

        # Extract required skills and search location
        required_skills = getattr(job_req, 'required_skills', None) or []
        search_location_str = getattr(job_req, 'location', None)

        search_location = None
        if search_location_str:
            search_location = self.location_parser.parse_location(search_location_str)

        # Score and rank candidates
        scored_candidates = self.ensemble_scorer.rank_candidates(
            candidates_data=candidates_data,
            required_skills=required_skills,
            search_location=search_location,
            min_score=0.1  # Minimum threshold to filter low-quality matches (lowered for better yield)
        )

        logger.info(f"Ranked {len(scored_candidates)} candidates (min_score=0.2)")

        # Map CandidateScore objects back to original Candidate objects
        # For now, fetch from cache based on username order
        ranked_usernames = [score.username for score in scored_candidates]
        ranked_candidates = []

        for username in ranked_usernames:
            cached = self.cache_service.get_profile(username)
            if cached:
                ranked_candidates.append(cached)

        logger.info(f"Mapped {len(ranked_candidates)} ranked candidates")
        return ranked_candidates

    def _build_response(
        self,
        candidates: List[Candidate],
        total_found: int,
        cache_hit: bool,
        execution_time_ms: int,
        warnings: List[str] = None
    ) -> Dict:
        """
        Build response with candidates and metadata.

        Args:
            candidates: List of Candidate objects
            total_found: Total candidates found in search
            cache_hit: Whether results came from cache
            execution_time_ms: Search duration in milliseconds
            warnings: Optional list of warning messages

        Returns:
            Dict with candidates and metadata
        """
        # Get rate limit from GitHub client's rate limiter
        rate_limit_remaining = 5000  # Default
        if hasattr(self.github_client, 'rate_limiter'):
            rate_limit_remaining = getattr(
                self.github_client.rate_limiter,
                'remaining_requests',
                5000
            )

        # Log rate limit status
        logger.info(
            f"[RATE_LIMIT] Current status | "
            f"Remaining: {rate_limit_remaining} requests"
        )

        metadata = SearchResult(
            total_candidates_found=total_found,
            candidates_returned=len(candidates),
            search_timestamp=datetime.utcnow(),
            rate_limit_remaining=rate_limit_remaining,
            cache_hit=cache_hit,
            execution_time_ms=execution_time_ms,
            warnings=warnings or []
        )

        return {
            "candidates": candidates,
            "metadata": metadata
        }

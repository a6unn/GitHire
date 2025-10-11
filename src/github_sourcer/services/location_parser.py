"""
LocationParser Service
======================
Parse and match locations with hierarchical city/state/country support.

Part of Module 002: GitHub Sourcer - Enhanced Location Matching
"""

import logging
from typing import Tuple, Optional
from src.github_sourcer.models.location_hierarchy import LocationHierarchy
from src.github_sourcer.lib.fuzzy_matcher import FuzzyMatcher
from src.github_sourcer.lib.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class LocationParser:
    """
    Parse location strings into hierarchical components.

    Supports:
    - City/state/country parsing
    - Location aliases (Bangalore → Bengaluru)
    - Fuzzy matching for typos
    - Hierarchical matching with priority scoring
    """

    # Priority scores for hierarchical matching
    CITY_MATCH_SCORE = 1.0
    STATE_MATCH_SCORE = 0.7
    COUNTRY_MATCH_SCORE = 0.3

    def __init__(self, fuzzy_threshold: float = 0.8):
        """
        Initialize LocationParser.

        Args:
            fuzzy_threshold: Minimum similarity for fuzzy matching (default: 0.8)
        """
        self.fuzzy_matcher = FuzzyMatcher(threshold=fuzzy_threshold)
        self.config_loader = ConfigLoader()

        # Load configuration data
        try:
            self.location_aliases = self.config_loader.load_location_aliases()
            self.cities_database = self.config_loader.load_cities_database()
            self.state_cities_mapping = self._load_state_cities_mapping()
            logger.info(
                f"LocationParser initialized with {len(self.cities_database)} cities, "
                f"{len(self.state_cities_mapping.get('indian_states', {}))} Indian states, "
                f"{len(self.state_cities_mapping.get('us_states', {}))} US states"
            )
        except Exception as e:
            logger.warning(f"Failed to load location data: {e}. Using minimal defaults.")
            self.location_aliases = {"city_aliases": {}}
            self.cities_database = []
            self.state_cities_mapping = {"indian_states": {}, "us_states": {}}

    def parse_location(self, location_str: str) -> LocationHierarchy:
        """
        Parse location string into hierarchical components.

        Args:
            location_str: Location string (e.g., "Chennai, Tamil Nadu, India")

        Returns:
            LocationHierarchy with parsed components

        Examples:
            >>> parser = LocationParser()
            >>> loc = parser.parse_location("Chennai, Tamil Nadu, India")
            >>> loc.city
            'Chennai'
            >>> loc.state
            'Tamil Nadu'
            >>> loc.country
            'India'
        """
        if not location_str or not location_str.strip():
            return LocationHierarchy(
                original_text="",
                city=None,
                state=None,
                country=None,
                match_confidence=0.0,
                match_level=None
            )

        original_text = location_str.strip()

        # Handle special cases
        if original_text.lower() == "remote":
            return LocationHierarchy(
                original_text=original_text,
                city=None,
                state=None,
                country=None,
                match_confidence=1.0,
                match_level=None
            )

        # Parse components (split by comma)
        parts = [part.strip() for part in original_text.split(",") if part.strip()]

        city = None
        state = None
        country = None
        confidence = 1.0
        match_level = None

        if len(parts) >= 3:
            # Full format: "City, State, Country"
            city = self._normalize_city(parts[0])
            state = parts[1]
            country = parts[2]
            match_level = "city"
        elif len(parts) == 2:
            # Two parts: could be "City, Country" or "City, State"
            city = self._normalize_city(parts[0])
            # Try to determine if second part is country or state
            if self._is_country(parts[1]):
                country = parts[1]
            else:
                state = parts[1]
            match_level = "city"
        elif len(parts) == 1:
            # Single part: could be city, state, or country
            part = parts[0]

            # Check if it's a country first
            if self._is_country(part):
                country = part
                match_level = "country"
                confidence = 0.9
            # Check if it's a known state
            elif self._is_state(part):
                state = part
                country = self._get_country_for_state(part)  # Auto-fill country
                match_level = "state"
                confidence = 0.95
            # Check if it's a known city
            elif self._find_city(part):
                city = self._find_city(part)
                match_level = "city"
                confidence = 1.0  # High confidence for known city
            else:
                # Default: assume it's a city
                city = self._normalize_city(part)
                match_level = "city"
                confidence = 0.9  # Higher confidence for normalized city

        return LocationHierarchy(
            original_text=original_text,
            city=city,
            state=state,
            country=country,
            match_confidence=confidence,
            match_level=match_level
        )

    def hierarchical_match(
        self,
        search_location: LocationHierarchy,
        candidate_location: LocationHierarchy
    ) -> Tuple[Optional[str], float]:
        """
        Match locations hierarchically with priority scoring.

        Priority: City (1.0) > State (0.7) > Country (0.3)

        Args:
            search_location: Parsed search location
            candidate_location: Parsed candidate location

        Returns:
            Tuple of (match_level: str | None, confidence: float)

        Examples:
            >>> parser = LocationParser()
            >>> search = parser.parse_location("Chennai")
            >>> candidate = parser.parse_location("Chennai, Tamil Nadu, India")
            >>> level, conf = parser.hierarchical_match(search, candidate)
            >>> level
            'city'
            >>> conf
            1.0
        """
        # Try city match first (highest priority)
        if search_location.city and candidate_location.city:
            if self._locations_match(search_location.city, candidate_location.city):
                return ("city", self.CITY_MATCH_SCORE)

        # Try state match
        if search_location.state and candidate_location.state:
            if self._locations_match(search_location.state, candidate_location.state):
                return ("state", self.STATE_MATCH_SCORE)

        # Try country match (lowest priority)
        if search_location.country and candidate_location.country:
            if self._locations_match(search_location.country, candidate_location.country):
                return ("country", self.COUNTRY_MATCH_SCORE)

        # No match
        return (None, 0.0)

    def _normalize_city(self, city_name: str) -> str:
        """
        Normalize city name using aliases.

        Examples:
            "Bangalore" → "Bengaluru"
            "Bombay" → "Mumbai"
        """
        if not city_name:
            return city_name

        city_lower = city_name.strip().lower()

        # Check city aliases
        city_aliases = self.location_aliases.get("city_aliases", {})

        for canonical_city, alias_data in city_aliases.items():
            if isinstance(alias_data, dict):
                canonical = alias_data.get("canonical", canonical_city)
                aliases = alias_data.get("aliases", [])

                # Check if city_name matches canonical or any alias
                if city_lower == canonical.lower():
                    return canonical

                for alias in aliases:
                    if city_lower == alias.lower():
                        return canonical

        # Try fuzzy matching against known cities
        known_cities = [city.get("name") for city in self.cities_database if city.get("name")]
        if known_cities:
            best_match, confidence = self.fuzzy_matcher.find_best_match(
                city_name, known_cities, threshold=0.75  # Lower threshold for typos
            )
            if best_match and confidence >= 0.75:
                logger.debug(f"Fuzzy matched '{city_name}' to '{best_match}' (confidence={confidence})")
                return best_match

        # Check aliases with fuzzy matching
        for canonical_city, alias_data in city_aliases.items():
            if isinstance(alias_data, dict):
                canonical = alias_data.get("canonical", canonical_city)
                all_variants = [canonical] + alias_data.get("aliases", [])

                best_match, confidence = self.fuzzy_matcher.find_best_match(
                    city_name, all_variants, threshold=0.75
                )
                if best_match and confidence >= 0.75:
                    logger.debug(f"Fuzzy matched '{city_name}' to '{canonical}' via alias (confidence={confidence})")
                    return canonical

        # Return as-is if no match found
        return city_name

    def _find_city(self, name: str) -> Optional[str]:
        """Find city in database."""
        if not name:
            return None

        name_lower = name.strip().lower()

        # Exact match
        for city in self.cities_database:
            city_name = city.get("name", "")
            if city_name.lower() == name_lower:
                return city_name

        # Fuzzy match
        known_cities = [city.get("name") for city in self.cities_database if city.get("name")]
        if known_cities:
            best_match, confidence = self.fuzzy_matcher.find_best_match(
                name, known_cities, threshold=0.85
            )
            if best_match:
                return best_match

        return None

    def _is_country(self, name: str) -> bool:
        """Check if name is a country."""
        common_countries = [
            "india", "usa", "united states", "uk", "united kingdom",
            "canada", "australia", "germany", "france", "singapore",
            "japan", "china", "brazil", "mexico", "russia"
        ]
        return name.strip().lower() in common_countries

    def _is_state(self, name: str) -> bool:
        """Check if name is a state/province."""
        # Common Indian states and US states
        common_states = [
            # Indian states
            "tamil nadu", "karnataka", "maharashtra", "kerala", "gujarat",
            "rajasthan", "andhra pradesh", "telangana", "west bengal", "punjab",
            "haryana", "uttar pradesh", "madhya pradesh", "bihar", "odisha",
            # US states
            "california", "texas", "new york", "florida", "illinois",
            "pennsylvania", "ohio", "georgia", "north carolina", "michigan",
            "washington", "oregon", "massachusetts"
        ]
        return name.strip().lower() in common_states

    def _get_country_for_state(self, state: str) -> Optional[str]:
        """Get the country for a known state."""
        indian_states = [
            "tamil nadu", "karnataka", "maharashtra", "kerala", "gujarat",
            "rajasthan", "andhra pradesh", "telangana", "west bengal", "punjab",
            "haryana", "uttar pradesh", "madhya pradesh", "bihar", "odisha"
        ]
        us_states = [
            "california", "texas", "new york", "florida", "illinois",
            "pennsylvania", "ohio", "georgia", "north carolina", "michigan",
            "washington", "oregon", "massachusetts"
        ]

        state_lower = state.strip().lower()
        if state_lower in indian_states:
            return "India"
        elif state_lower in us_states:
            return "United States"
        return None

    def _locations_match(self, loc1: str, loc2: str) -> bool:
        """Check if two location strings match (case-insensitive)."""
        if not loc1 or not loc2:
            return False

        # Exact match (case-insensitive)
        if loc1.strip().lower() == loc2.strip().lower():
            return True

        # Fuzzy match with high threshold
        matched, _ = self.fuzzy_matcher.fuzzy_match(loc1, loc2, threshold=0.9)
        return matched

    def get_cities_database(self) -> list:
        """Get loaded cities database."""
        return self.cities_database

    def get_location_aliases(self) -> dict:
        """Get loaded location aliases."""
        return self.location_aliases

    def get_aliases(self, city_name: str) -> list[str]:
        """
        Get aliases for a city name.

        Args:
            city_name: City name to look up

        Returns:
            List of aliases
        """
        city_aliases = self.location_aliases.get("city_aliases", {})

        for canonical_city, alias_data in city_aliases.items():
            if isinstance(alias_data, dict):
                canonical = alias_data.get("canonical", canonical_city)
                if canonical.lower() == city_name.lower():
                    return alias_data.get("aliases", [])

        return []

    def _load_state_cities_mapping(self) -> dict:
        """
        Load state-to-cities mapping from YAML config.

        Returns:
            Dict with indian_states and us_states mappings
        """
        import yaml
        from pathlib import Path

        config_path = Path(__file__).parent.parent.parent / "config" / "state_cities_mapping.yaml"

        try:
            with open(config_path, "r") as f:
                mapping = yaml.safe_load(f)
                logger.debug(f"Loaded state-cities mapping from {config_path}")
                return mapping or {"indian_states": {}, "us_states": {}}
        except FileNotFoundError:
            logger.warning(f"State-cities mapping file not found at {config_path}")
            return {"indian_states": {}, "us_states": {}}
        except Exception as e:
            logger.error(f"Failed to load state-cities mapping: {e}")
            return {"indian_states": {}, "us_states": {}}

    def get_cities_for_state(self, state_name: str) -> list[str]:
        """
        Get list of major cities for a given state.

        Args:
            state_name: State name (e.g., "Tamil Nadu", "California")

        Returns:
            List of major city names for that state

        Examples:
            >>> parser = LocationParser()
            >>> parser.get_cities_for_state("Tamil Nadu")
            ['Chennai', 'Coimbatore', 'Trichy', 'Madurai', 'Salem', 'Erode']
        """
        if not state_name:
            return []

        state_lower = state_name.strip().lower().replace(" ", "_")

        # Check Indian states
        indian_states = self.state_cities_mapping.get("indian_states", {})
        if state_lower in indian_states:
            return indian_states[state_lower].get("major_cities", [])

        # Check US states
        us_states = self.state_cities_mapping.get("us_states", {})
        if state_lower in us_states:
            return us_states[state_lower].get("major_cities", [])

        logger.debug(f"No cities mapping found for state: {state_name}")
        return []

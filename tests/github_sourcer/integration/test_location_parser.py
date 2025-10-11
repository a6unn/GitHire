"""
Integration Tests for LocationParser (T011A)
=============================================
Tests for location parsing and hierarchical matching.

TDD Approach: These tests WILL FAIL until LocationParser is implemented.

Specification Reference: specs/002-github-sourcer-module/tasks.md T011A
"""

import pytest
from src.github_sourcer.services.location_parser import LocationParser, LocationHierarchy


class TestLocationParser:
    """Integration tests for location parsing and matching"""

    def test_location_parser_initialization(self):
        """Test that LocationParser can be instantiated"""
        parser = LocationParser()
        assert parser is not None

    def test_parse_full_location_string(self):
        """Test: 'Chennai, Tamil Nadu, India' → structured components"""
        parser = LocationParser()

        location = parser.parse_location("Chennai, Tamil Nadu, India")

        assert location.city == "Chennai"
        assert location.state == "Tamil Nadu"
        assert location.country == "India"
        assert location.original_text == "Chennai, Tamil Nadu, India"
        assert location.match_confidence == 1.0  # Exact match
        assert location.match_level == "city"

    def test_parse_city_only(self):
        """Test parsing city name only"""
        parser = LocationParser()

        location = parser.parse_location("Bangalore")

        assert location.city == "Bangalore" or location.city == "Bengaluru"  # Alias mapping
        assert location.original_text == "Bangalore"
        assert location.match_confidence >= 0.9  # High confidence

    def test_bangalore_bengaluru_alias_mapping(self):
        """Test: 'Bangalore' → matches 'Bengaluru' via aliases"""
        parser = LocationParser()

        bangalore = parser.parse_location("Bangalore")
        bengaluru = parser.parse_location("Bengaluru")

        # Both should resolve to same canonical city
        assert bangalore.city == bengaluru.city or "Bangalore" in parser.get_aliases("Bengaluru")

    def test_fuzzy_match_typo(self):
        """Test: 'Bangalor' (typo) → fuzzy matches 'Bangalore' with reduced confidence"""
        parser = LocationParser()

        location = parser.parse_location("Bangalor")

        # Should still match Bangalore/Bengaluru
        assert location.city in ["Bangalore", "Bengaluru"]
        assert location.match_confidence < 1.0  # Reduced due to typo
        assert location.match_confidence >= 0.7  # But still reasonable

    def test_hierarchical_city_match(self):
        """Test: search='Chennai' matches city level (confidence 1.0)"""
        parser = LocationParser()

        search_location = parser.parse_location("Chennai")
        candidate_location = parser.parse_location("Chennai, Tamil Nadu, India")

        match_level, confidence = parser.hierarchical_match(search_location, candidate_location)

        assert match_level == "city"
        assert confidence == 1.0  # Perfect city match

    def test_hierarchical_state_match(self):
        """Test: search='Tamil Nadu' matches state level (confidence 0.7)"""
        parser = LocationParser()

        search_location = parser.parse_location("Tamil Nadu")
        candidate_location = parser.parse_location("Chennai, Tamil Nadu, India")

        match_level, confidence = parser.hierarchical_match(search_location, candidate_location)

        assert match_level == "state"
        assert confidence == 0.7  # State-level match

    def test_hierarchical_country_match(self):
        """Test: search='India' matches country level (confidence 0.3)"""
        parser = LocationParser()

        search_location = parser.parse_location("India")
        candidate_location = parser.parse_location("Mumbai, Maharashtra, India")

        match_level, confidence = parser.hierarchical_match(search_location, candidate_location)

        assert match_level == "country"
        assert confidence == 0.3  # Country-level match (lowest priority)

    def test_no_match_different_countries(self):
        """Test: Different countries should not match"""
        parser = LocationParser()

        search_location = parser.parse_location("San Francisco, USA")
        candidate_location = parser.parse_location("Chennai, India")

        match_level, confidence = parser.hierarchical_match(search_location, candidate_location)

        assert match_level is None
        assert confidence == 0.0

    def test_partial_location_string(self):
        """Test parsing partial location (city, country only)"""
        parser = LocationParser()

        location = parser.parse_location("Mumbai, India")

        assert location.city == "Mumbai"
        assert location.country == "India"
        assert location.state is None  # No state provided

    def test_remote_location(self):
        """Test parsing 'Remote' location"""
        parser = LocationParser()

        location = parser.parse_location("Remote")

        assert location.original_text == "Remote"
        assert location.city is None
        assert location.state is None
        assert location.country is None
        assert location.match_level is None

    def test_case_insensitive_matching(self):
        """Test case-insensitive location matching"""
        parser = LocationParser()

        location1 = parser.parse_location("CHENNAI")
        location2 = parser.parse_location("chennai")
        location3 = parser.parse_location("Chennai")

        # All should normalize to same city
        assert location1.city == location2.city == location3.city

    def test_load_cities_database(self):
        """Test that cities.json database loads successfully"""
        parser = LocationParser()

        cities = parser.get_cities_database()

        assert len(cities) >= 20  # At least 20 cities in database
        assert isinstance(cities, list)

        # Verify structure of first city
        if cities:
            city = cities[0]
            assert "name" in city
            assert "country_name" in city or "country" in city

    def test_location_aliases_loaded(self):
        """Test that location_aliases.json loads successfully"""
        parser = LocationParser()

        aliases = parser.get_location_aliases()

        assert isinstance(aliases, dict)
        assert "city_aliases" in aliases

    def test_multiple_city_variants(self):
        """Test handling multiple city name variants"""
        parser = LocationParser()

        # Test common city variants
        locations = [
            "Bengaluru",
            "Bangalore",
            "Bengalooru"  # Less common spelling
        ]

        parsed = [parser.parse_location(loc) for loc in locations]

        # All should resolve to similar canonical form
        # (exact matching depends on aliases configuration)
        assert all(p.city is not None for p in parsed)

    def test_priority_scoring_constants(self):
        """Test that priority scores match specification (city=1.0, state=0.7, country=0.3)"""
        parser = LocationParser()

        # These should be constants in LocationParser
        assert parser.CITY_MATCH_SCORE == 1.0
        assert parser.STATE_MATCH_SCORE == 0.7
        assert parser.COUNTRY_MATCH_SCORE == 0.3

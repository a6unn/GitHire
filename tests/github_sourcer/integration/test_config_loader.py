"""
Integration Tests for ConfigLoader (T011E)
===========================================
Tests for configuration file loading.

TDD Approach: These tests WILL FAIL until ConfigLoader is implemented.

Specification Reference: modules/002-github-sourcer-module/tasks.md T011E
"""

import pytest
from pathlib import Path
from src.github_sourcer.lib.config_loader import ConfigLoader, ConfigurationError


class TestConfigLoader:
    """Integration tests for configuration loading"""

    def test_config_loader_initialization(self):
        """Test that ConfigLoader can be instantiated"""
        config_loader = ConfigLoader()
        assert config_loader is not None

    def test_load_skill_weights_yaml(self):
        """Test loading skill_weights.yaml with all required weights"""
        config_loader = ConfigLoader()

        weights = config_loader.load_skill_weights()

        # Verify structure
        assert "primary_method" in weights
        assert "fallback_weights" in weights
        assert "confidence_thresholds" in weights

        # Verify primary method
        assert weights["primary_method"]["name"] == "dependency_graph"
        assert weights["primary_method"]["weight"] == 0.50

        # Verify fallback weights sum to reasonable value
        fallback = weights["fallback_weights"]
        assert "repository_topics" in fallback
        assert "repository_languages" in fallback
        assert "repository_names" in fallback
        assert "bio_starred_repos" in fallback
        assert "commit_messages" in fallback

        # Verify confidence thresholds
        thresholds = weights["confidence_thresholds"]
        assert thresholds["minimum"] == 0.50
        assert thresholds["high"] == 0.80
        assert thresholds["expert"] == 0.90

    def test_load_detection_config_yaml(self):
        """Test loading detection_config.yaml with thresholds, timeouts"""
        config_loader = ConfigLoader()

        config = config_loader.load_detection_config()

        # Verify GraphQL batching config
        assert "graphql_batching" in config
        assert config["graphql_batching"]["enabled"] is True
        assert config["graphql_batching"]["batch_size"] == 50

        # Verify BigQuery config
        assert "bigquery" in config
        assert isinstance(config["bigquery"]["enabled"], bool)

        # Verify location filtering config
        assert "location_filtering" in config
        assert config["location_filtering"]["hierarchy_enabled"] is True

        # Verify priority scores
        priority = config["location_filtering"]["priority_scores"]
        assert priority["city_match"] == 1.0
        assert priority["state_match"] == 0.7
        assert priority["country_match"] == 0.3

    def test_load_skill_aliases_json(self):
        """Test loading skill_aliases.json for skill normalization"""
        config_loader = ConfigLoader()

        aliases = config_loader.load_skill_aliases()

        # Verify it's a dictionary
        assert isinstance(aliases, dict)

        # Verify some common skills exist
        assert "React" in aliases or "react" in aliases or any("react" in k.lower() for k in aliases.keys())

        # Verify structure of at least one skill
        # Should have canonical form and aliases list
        skill_entry = next(iter(aliases.values()))
        assert "canonical" in skill_entry
        assert "aliases" in skill_entry
        assert isinstance(skill_entry["aliases"], list)

    def test_load_location_aliases_json(self):
        """Test loading location_aliases.json for location variants"""
        config_loader = ConfigLoader()

        aliases = config_loader.load_location_aliases()

        # Verify it's a dictionary
        assert isinstance(aliases, dict)

        # Should have city_aliases
        assert "city_aliases" in aliases

        # Verify structure: should have entries like "Bangalore" -> "Bengaluru"
        city_aliases = aliases["city_aliases"]
        assert isinstance(city_aliases, dict)

        # Check for at least one city with variants
        if city_aliases:
            city_entry = next(iter(city_aliases.values()))
            assert "canonical" in city_entry
            assert "aliases" in city_entry
            assert isinstance(city_entry["aliases"], list)

    def test_load_cities_database_json(self):
        """Test loading cities.json database"""
        config_loader = ConfigLoader()

        cities = config_loader.load_cities_database()

        # Verify it's a list
        assert isinstance(cities, list)

        # Should have at least 20 cities (starter database)
        assert len(cities) >= 20

        # Verify structure of first city
        if cities:
            city = cities[0]
            assert "name" in city
            # Cities use country_name and state_name (not country/state)
            assert "country_name" in city or "country" in city
            # May have state_name, state, latitude, longitude

    def test_missing_config_file_raises_clear_error(self):
        """Test that missing config file raises ConfigurationError with clear message"""
        config_loader = ConfigLoader(config_dir="/nonexistent/path")

        with pytest.raises(ConfigurationError) as exc_info:
            config_loader.load_skill_weights()

        # Error message should mention the file that's missing
        error_msg = str(exc_info.value)
        assert "skill_weights" in error_msg or "not found" in error_msg

    def test_invalid_yaml_syntax_raises_error(self, tmp_path):
        """Test that invalid YAML syntax raises clear error"""
        # Create a temporary invalid YAML file
        invalid_yaml_path = tmp_path / "skill_weights.yaml"
        invalid_yaml_path.write_text("primary_method:\n  name: dependency_graph\n  weight: [invalid\n")

        config_loader = ConfigLoader(config_dir=str(tmp_path))

        with pytest.raises(ConfigurationError) as exc_info:
            config_loader.load_skill_weights()

        error_msg = str(exc_info.value)
        assert "yaml" in error_msg.lower() or "parse" in error_msg.lower()

    def test_invalid_json_syntax_raises_error(self, tmp_path):
        """Test that invalid JSON syntax raises clear error"""
        # Create a temporary invalid JSON file
        invalid_json_path = tmp_path / "skill_aliases.json"
        invalid_json_path.write_text('{"React": {"canonical": "React", "aliases": [}')

        # skill_aliases.json is in data_dir, not config_dir
        config_loader = ConfigLoader(data_dir=str(tmp_path))

        with pytest.raises(ConfigurationError) as exc_info:
            config_loader.load_skill_aliases()

        error_msg = str(exc_info.value)
        assert "json" in error_msg.lower() or "parse" in error_msg.lower()

    def test_config_files_cached_after_first_load(self):
        """Test that config files are cached and not reloaded on every call"""
        config_loader = ConfigLoader()

        # Load once
        weights1 = config_loader.load_skill_weights()

        # Load again - should return cached version (same object)
        weights2 = config_loader.load_skill_weights()

        # Should be the same object (cached)
        assert weights1 is weights2

    def test_all_config_files_loadable(self):
        """Test that all configuration files can be loaded without errors"""
        config_loader = ConfigLoader()

        # Try loading all config files
        skill_weights = config_loader.load_skill_weights()
        detection_config = config_loader.load_detection_config()
        skill_aliases = config_loader.load_skill_aliases()
        location_aliases = config_loader.load_location_aliases()
        cities = config_loader.load_cities_database()

        # All should be loaded successfully
        assert skill_weights is not None
        assert detection_config is not None
        assert skill_aliases is not None
        assert location_aliases is not None
        assert cities is not None

    def test_config_directory_resolution(self):
        """Test that ConfigLoader correctly resolves config directory path"""
        config_loader = ConfigLoader()

        # Should default to src/config and src/data directories
        config_dir = config_loader.config_dir
        data_dir = config_loader.data_dir

        assert config_dir is not None
        assert data_dir is not None

        # Directories should exist
        assert Path(config_dir).exists()
        assert Path(data_dir).exists()

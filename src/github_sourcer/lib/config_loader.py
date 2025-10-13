"""Configuration loader for GitHub Sourcer.

Loads configuration files (YAML/JSON) for skills, locations, and detection settings.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration files cannot be loaded or are invalid."""
    pass


class ConfigLoader:
    """Loads and caches configuration files for GitHub Sourcer."""

    def __init__(self, config_dir: Optional[str] = None, data_dir: Optional[str] = None):
        """
        Initialize ConfigLoader.

        Args:
            config_dir: Path to configuration directory (defaults to src/config)
            data_dir: Path to data directory (defaults to src/data)
        """
        if config_dir is None:
            # Default to src/config relative to project root
            self.config_dir = Path(__file__).parents[2] / "config"
        else:
            self.config_dir = Path(config_dir)

        if data_dir is None:
            # Default to src/data relative to project root
            self.data_dir = Path(__file__).parents[2] / "data"
        else:
            self.data_dir = Path(data_dir)

        # Cache for loaded config files
        self._cache: Dict[str, Any] = {}

    def load_skill_weights(self) -> Dict[str, Any]:
        """
        Load skill_weights.yaml configuration.

        Returns:
            Dictionary with primary_method, fallback_weights, and confidence_thresholds

        Raises:
            ConfigurationError: If file not found or invalid YAML
        """
        cache_key = "skill_weights"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.config_dir / "skill_weights.yaml"
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            self._cache[cache_key] = config
            logger.debug(f"Loaded skill weights from {file_path}")
            return config

        except FileNotFoundError:
            raise ConfigurationError(
                f"Configuration file not found: {file_path}. "
                "Please ensure skill_weights.yaml exists in src/config/"
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML syntax in {file_path}: {e}"
            )

    def load_detection_config(self) -> Dict[str, Any]:
        """
        Load detection_config.yaml configuration.

        Returns:
            Dictionary with graphql_batching, bigquery, location_filtering, etc.

        Raises:
            ConfigurationError: If file not found or invalid YAML
        """
        cache_key = "detection_config"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.config_dir / "detection_config.yaml"
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            self._cache[cache_key] = config
            logger.debug(f"Loaded detection config from {file_path}")
            return config

        except FileNotFoundError:
            raise ConfigurationError(
                f"Configuration file not found: {file_path}. "
                "Please ensure detection_config.yaml exists in src/config/"
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML syntax in {file_path}: {e}"
            )

    def load_skill_aliases(self) -> Dict[str, Any]:
        """
        Load skill_aliases.json for skill normalization.

        Returns:
            Dictionary mapping skill names to canonical forms and aliases

        Raises:
            ConfigurationError: If file not found or invalid JSON
        """
        cache_key = "skill_aliases"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.data_dir / "skill_aliases.json"
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Handle both formats: direct dict or nested under "aliases" key
            if "aliases" in data:
                aliases = data["aliases"]
            else:
                aliases = data

            self._cache[cache_key] = aliases
            logger.debug(f"Loaded {len(aliases)} skill aliases from {file_path}")
            return aliases

        except FileNotFoundError:
            raise ConfigurationError(
                f"Data file not found: {file_path}. "
                "Please ensure skill_aliases.json exists in src/data/"
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON syntax in {file_path}: {e}"
            )

    def load_location_aliases(self) -> Dict[str, Any]:
        """
        Load location_aliases.json for location variant mapping.

        Returns:
            Dictionary with city_aliases mapping location variants

        Raises:
            ConfigurationError: If file not found or invalid JSON
        """
        cache_key = "location_aliases"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.data_dir / "location_aliases.json"
        try:
            with open(file_path, "r") as f:
                aliases = json.load(f)

            self._cache[cache_key] = aliases
            logger.debug(f"Loaded location aliases from {file_path}")
            return aliases

        except FileNotFoundError:
            raise ConfigurationError(
                f"Data file not found: {file_path}. "
                "Please ensure location_aliases.json exists in src/data/"
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON syntax in {file_path}: {e}"
            )

    def load_cities_database(self) -> List[Dict[str, Any]]:
        """
        Load cities.json database.

        Returns:
            List of city dictionaries with name, country, state, etc.

        Raises:
            ConfigurationError: If file not found or invalid JSON
        """
        cache_key = "cities_database"
        if cache_key in self._cache:
            return self._cache[cache_key]

        file_path = self.data_dir / "cities.json"
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Handle both formats: direct list or nested under "cities" key
            if isinstance(data, dict) and "cities" in data:
                cities = data["cities"]
            elif isinstance(data, list):
                cities = data
            else:
                raise ConfigurationError(
                    f"Invalid cities database format in {file_path}. "
                    "Expected a list or a dict with 'cities' key"
                )

            self._cache[cache_key] = cities
            logger.debug(f"Loaded {len(cities)} cities from {file_path}")
            return cities

        except FileNotFoundError:
            raise ConfigurationError(
                f"Data file not found: {file_path}. "
                "Please ensure cities.json exists in src/data/"
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON syntax in {file_path}: {e}"
            )

    def clear_cache(self) -> None:
        """Clear all cached configuration files."""
        self._cache.clear()
        logger.debug("Configuration cache cleared")

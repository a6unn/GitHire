"""
Noreply Email Filter Library
Module 010: Contact Enrichment

Filters privacy-protected email addresses (noreply, no-reply, automated).
Constitutional Rule CR-001: Privacy-First - Respect user's choice to hide email.
"""

from typing import Optional
import yaml
from pathlib import Path


class NoreplyFilter:
    """
    Filters privacy-protected email addresses.

    Respects user privacy by filtering:
    - GitHub noreply emails (users.noreply.github.com)
    - GitLab/Bitbucket noreply emails
    - Generic noreply patterns
    - Automated/system emails

    Constitutional Rule CR-001: Privacy-First
    Constitutional Rule CR-003: No Hardcoding (patterns loaded from YAML)
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the noreply filter.

        Args:
            config_path: Path to noreply_patterns.yaml (defaults to module config)
        """
        if config_path is None:
            # Default to module config directory
            module_dir = Path(__file__).parent.parent
            config_path = module_dir / "config" / "noreply_patterns.yaml"

        # Load patterns from YAML (CR-003: No Hardcoding)
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Flatten all pattern lists into a single list
        self.patterns: list[str] = []
        for category in [
            "github_noreply",
            "generic_noreply",
            "gitlab_noreply",
            "bitbucket_noreply",
            "automated",
        ]:
            if category in config:
                self.patterns.extend(config[category])

    def is_noreply(self, email: Optional[str]) -> bool:
        """
        Check if an email is a privacy-protected noreply address.

        Args:
            email: Email address to check

        Returns:
            True if email is noreply/automated, False otherwise
        """
        # Defensive: Handle None and empty strings
        if not email:
            return False

        # Case-insensitive matching
        email_lower = email.lower()

        # Check against all loaded patterns
        for pattern in self.patterns:
            if pattern.lower() in email_lower:
                return True

        return False

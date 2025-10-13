"""
Spam Domain Filter Library
Module 010: Contact Enrichment

Filters fake, test, and disposable email domains.
"""

from typing import Optional
import yaml
from pathlib import Path


class SpamFilter:
    """
    Filters spam, test, and disposable email domains.

    Filters:
    - Test domains (example.com, test.com - RFC 2606)
    - Localhost and loopback addresses
    - Disposable email services
    - Invalid placeholder domains
    - Development/staging domains

    Constitutional Rule CR-003: No Hardcoding (domains loaded from YAML)
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the spam filter.

        Args:
            config_path: Path to spam_domains.yaml (defaults to module config)
        """
        if config_path is None:
            # Default to module config directory
            module_dir = Path(__file__).parent.parent
            config_path = module_dir / "config" / "spam_domains.yaml"

        # Load spam domains from YAML (CR-003: No Hardcoding)
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Flatten all domain lists into a single set for fast lookup
        self.spam_domains: set[str] = set()
        for category in [
            "test_domains",
            "localhost",
            "disposable",
            "invalid",
            "development",
        ]:
            if category in config:
                self.spam_domains.update(config[category])

    def is_spam_domain(self, email: Optional[str]) -> bool:
        """
        Check if an email uses a spam/test domain.

        Args:
            email: Email address to check

        Returns:
            True if domain is spam/test/disposable, False otherwise
        """
        # Defensive: Handle None and empty strings
        if not email:
            return False

        # Extract domain from email
        if "@" not in email:
            return False

        domain = email.split("@")[1].lower()

        # Check against spam domain set (case-insensitive)
        return domain in {d.lower() for d in self.spam_domains}

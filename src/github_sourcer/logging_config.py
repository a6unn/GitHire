"""Logging configuration for GitHub Sourcer module.

Provides structured logging with appropriate levels.
"""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """
    Configure logging for GitHub Sourcer.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Parse level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific module levels
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce httpx noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # Reduce urllib3 noise

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {level} level")


# Auto-configure on import
configure_logging()

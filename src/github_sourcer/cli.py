"""Command-line interface for GitHub Sourcer.

Allows standalone usage: python -m src.github_sourcer.cli --input job.json
"""

import argparse
import json
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

from src.jd_parser.models import JobRequirement
from src.github_sourcer.services.search_service import SearchService
from src.github_sourcer.models.candidate import Candidate
from src.github_sourcer.models.search_result import SearchResult


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GitHub Sourcer - Find developers based on job requirements"
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to JobRequirement JSON file (output from Module 001)"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to output JSON file (default: stdout)"
    )

    parser.add_argument(
        "--pretty",
        "-p",
        action="store_true",
        help="Pretty-print JSON output"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )

    return parser.parse_args()


def load_job_requirement(file_path: str) -> JobRequirement:
    """
    Load JobRequirement from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        JobRequirement object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        with open(path, "r") as f:
            data = json.load(f)

        job_req = JobRequirement(**data)
        logger.info(f"Loaded JobRequirement from {file_path}")
        return job_req

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Failed to parse JobRequirement: {e}")


def format_output(candidates: list[Candidate], metadata: SearchResult, pretty: bool = False) -> str:
    """
    Format output as JSON.

    Args:
        candidates: List of Candidate objects
        metadata: SearchResult metadata
        pretty: Whether to pretty-print JSON

    Returns:
        JSON string
    """
    output = {
        "candidates": [c.model_dump(mode="json") for c in candidates],
        "metadata": metadata.model_dump(mode="json")
    }

    indent = 2 if pretty else None
    return json.dumps(output, indent=indent, default=str)


async def main_async(args):
    """
    Async main function.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Load input
        job_req = load_job_requirement(args.input)

        # Search GitHub
        logger.info("Searching GitHub for candidates...")
        service = SearchService()
        result = await service.search(job_req)

        # Format output
        output_json = format_output(
            result["candidates"],
            result["metadata"],
            pretty=args.pretty
        )

        # Write output
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                f.write(output_json)
            logger.info(f"Results written to {args.output}")
        else:
            # Print to stdout
            print(output_json)

        # Print summary to stderr
        metadata = result["metadata"]
        logger.info(
            f"Search complete: {metadata.candidates_returned}/{metadata.total_candidates_found} candidates, "
            f"cache_hit={metadata.cache_hit}, execution_time={metadata.execution_time_ms}ms"
        )

        return 0

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def main():
    """Main entry point."""
    args = parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run async main
    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

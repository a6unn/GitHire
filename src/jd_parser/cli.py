"""CLI entry point for JD Parser module."""

import sys
import json
import argparse
from pathlib import Path
from .parser import JDParser
from pydantic import ValidationError


def main():
    """
    CLI entry point for parsing job descriptions.

    Usage:
        python -m src.jd_parser.cli "Senior Python Developer with 5+ years..."
        python -m src.jd_parser.cli --file job_description.txt
        echo "React developer" | python -m src.jd_parser.cli --stdin
    """
    parser = argparse.ArgumentParser(
        description="Extract structured requirements from job descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse inline text
  python -m src.jd_parser.cli "Senior Python Developer with 5+ years experience"

  # Parse from file
  python -m src.jd_parser.cli --file job_description.txt

  # Parse from stdin
  echo "React developer needed" | python -m src.jd_parser.cli --stdin

  # Pretty print JSON output
  python -m src.jd_parser.cli "Java developer" --pretty
        """
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Job description text (if not using --file or --stdin)"
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        help="Read job description from file"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read job description from stdin"
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        help="Pretty-print JSON output"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="LLM provider to use (default: openai)"
    )

    args = parser.parse_args()

    # Get input text
    if args.file:
        jd_text = args.file.read_text()
    elif args.stdin:
        jd_text = sys.stdin.read()
    elif args.text:
        jd_text = args.text
    else:
        parser.error("Must provide text, --file, or --stdin")

    # Initialize parser
    try:
        jd_parser = JDParser()
    except Exception as e:
        print(f"Error initializing parser: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse job description
    try:
        result = jd_parser.parse(jd_text)

        # Convert to JSON
        output = result.model_dump(mode="json")

        # Print output
        if args.pretty:
            print(json.dumps(output, indent=2))
        else:
            print(json.dumps(output))

        sys.exit(0)

    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error parsing job description: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

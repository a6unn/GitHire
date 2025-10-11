"""Main JD Parser class - orchestrates LLM extraction, validation, and normalization."""

import json
import logging
from pathlib import Path
from typing import Optional

from .llm_client import create_llm_client, LLMClient
from .models import JobRequirement, ConfidenceScore, YearsOfExperience
from .skill_normalizer import SkillNormalizer
from .validators import validate_input, validate_output
from pydantic import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# File handler for detailed logs
file_handler = logging.FileHandler('jd_parser.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)


class JDParser:
    """Job Description Parser - extracts structured requirements from free text."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        skill_normalizer: Optional[SkillNormalizer] = None,
        prompt_template_path: Optional[Path] = None
    ):
        """
        Initialize JD Parser.

        Args:
            llm_client: LLM client for extraction (default: OpenAI GPT-4o-mini)
            skill_normalizer: Skill normalizer (default: uses skill_mappings.json)
            prompt_template_path: Path to extraction prompt template
        """
        # Initialize LLM client
        if llm_client is None:
            llm_client = create_llm_client("openai")
        self.llm_client = llm_client

        # Initialize skill normalizer
        if skill_normalizer is None:
            skill_normalizer = SkillNormalizer(llm_client=llm_client)
        self.skill_normalizer = skill_normalizer

        # Load prompt template
        if prompt_template_path is None:
            prompt_template_path = Path(__file__).parent / "prompts" / "extraction_prompt.txt"
        with open(prompt_template_path) as f:
            self.prompt_template = f.read()

        logger.info("JDParser initialized with LLM client and skill normalizer")

    def parse(self, jd_text: str, language: str = "en") -> JobRequirement:
        """
        Parse job description and extract structured requirements.

        Args:
            jd_text: Free-text job description
            language: Input language (default: "en")

        Returns:
            JobRequirement object with extracted data

        Raises:
            ValidationError: If input/output validation fails
            ValueError: If LLM fails to extract minimum required fields
        """
        # Step 1: Validate input
        jd_text = jd_text.strip()  # Remove leading/trailing whitespace
        if not jd_text:
            raise ValueError("Job description text cannot be empty or whitespace-only")

        logger.info(f"Parsing JD ({len(jd_text)} chars)")
        validate_input(jd_text, language)

        # Step 2: Extract using LLM
        raw_extraction = self._extract_with_llm(jd_text)

        # Step 3: Normalize skills
        raw_extraction = self._normalize_skills(raw_extraction)

        # Step 4: Build JobRequirement object
        try:
            job_req = JobRequirement(
                role=raw_extraction.get("role"),
                required_skills=raw_extraction.get("required_skills", []),
                preferred_skills=raw_extraction.get("preferred_skills", []),
                years_of_experience=YearsOfExperience(**raw_extraction.get("years_of_experience", {})),
                seniority_level=raw_extraction.get("seniority_level"),
                location_preferences=raw_extraction.get("location_preferences", []),
                domain=raw_extraction.get("domain"),
                confidence_scores=self._parse_confidence_scores(raw_extraction.get("confidence_scores", {})),
                original_input=jd_text,
                schema_version="1.0.0"
            )
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            raise ValueError(f"Failed to extract minimum required fields: {e}")

        # Step 5: Validate output
        validated = validate_output(job_req)

        logger.info(f"✓ Parsed successfully: role={validated.role}, skills={len(validated.required_skills)}")
        return validated

    def _extract_with_llm(self, jd_text: str) -> dict:
        """
        Use LLM to extract structured data from JD.

        Args:
            jd_text: Job description text

        Returns:
            Dictionary with extracted fields

        Raises:
            ValueError: If LLM fails or returns invalid JSON
        """
        # Fill prompt template
        prompt = self.prompt_template.format(job_description=jd_text)

        logger.debug(f"LLM prompt length: {len(prompt)} chars")

        try:
            # Get LLM response
            logger.debug(f"Sending prompt to LLM (length: {len(prompt)} chars)")
            response = self.llm_client.complete(prompt, max_tokens=2000, temperature=0.3)

            # Log full prompt and response for audit
            logger.debug(f"LLM prompt:\n{prompt}")
            logger.debug(f"LLM response:\n{response}")

            # Parse JSON
            extracted = json.loads(response)
            logger.info(f"✓ LLM extraction successful: extracted {len(extracted)} fields")
            return extracted

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"LLM extraction failed: invalid JSON response")
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            raise ValueError(f"LLM extraction failed: {e}")

    def _normalize_skills(self, extraction: dict) -> dict:
        """
        Normalize skill names in extracted data.

        Args:
            extraction: Raw extraction dictionary

        Returns:
            Updated dictionary with normalized skills
        """
        if "required_skills" in extraction:
            extraction["required_skills"] = self.skill_normalizer.normalize_list(
                extraction["required_skills"]
            )

        if "preferred_skills" in extraction:
            extraction["preferred_skills"] = self.skill_normalizer.normalize_list(
                extraction["preferred_skills"]
            )

        logger.debug(f"Normalized skills: required={extraction.get('required_skills')}, "
                    f"preferred={extraction.get('preferred_skills')}")

        return extraction

    def _parse_confidence_scores(self, scores_dict: dict) -> dict[str, ConfidenceScore]:
        """
        Parse confidence scores from LLM response.

        Args:
            scores_dict: Dictionary of confidence scores from LLM

        Returns:
            Dictionary mapping field names to ConfidenceScore objects
        """
        parsed = {}
        for field, score_data in scores_dict.items():
            if isinstance(score_data, dict) and "score" in score_data and "reasoning" in score_data:
                parsed[field] = ConfidenceScore(
                    score=score_data["score"],
                    reasoning=score_data["reasoning"],
                    highlighted_spans=score_data.get("highlighted_spans", [])
                )
        return parsed

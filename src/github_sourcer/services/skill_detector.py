"""
SkillDetector Service
=====================
Detect skills from GitHub repositories using dependency graphs and ensemble scoring.

Part of Module 002: GitHub Sourcer - Enhanced Skill Detection
"""

import logging
import re
from typing import Optional, List, Dict
from collections import defaultdict
from src.github_sourcer.models.skill_confidence import SkillConfidence
from src.github_sourcer.lib.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class SkillDetector:
    """
    Detect skills from GitHub profiles with high accuracy.

    Supports:
    - Primary detection via GitHub Dependency Graph API (80-85% accuracy)
    - Fallback ensemble detection via topics/bio/languages (70-75% accuracy)
    - Multi-signal aggregation with weighted scoring
    - Skill normalization and deduplication
    """

    # Signal weights for ensemble scoring
    SIGNAL_WEIGHTS = {
        'dependency_graph': 0.85,      # Highest confidence
        'repository_topics': 0.65,     # Medium-high confidence
        'repository_name': 0.60,       # Medium-high confidence (NEW: validated 60% coverage, 7.8 repos/candidate)
        'bio_mention': 0.55,           # Medium confidence
        'repository_language': 0.5,    # Medium-low confidence (ensure single occurrence meets threshold)
        'starred_repos': 0.35          # Lower confidence (optional)
    }

    # Common programming language names for normalization
    SKILL_NORMALIZATIONS = {
        'react.js': 'React',
        'react': 'React',
        'reactjs': 'React',
        'vue.js': 'Vue',
        'vue': 'Vue',
        'vuejs': 'Vue',
        'angular': 'Angular',
        'angularjs': 'Angular',
        'node.js': 'Node.js',
        'nodejs': 'Node.js',
        'node': 'Node.js',
        'python': 'Python',
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'java': 'Java',
        'c++': 'C++',
        'c#': 'C#',
        'go': 'Go',
        'rust': 'Rust',
        'ruby': 'Ruby',
        'php': 'PHP',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'scikit-learn': 'Scikit-Learn',
        'tensorflow': 'TensorFlow',
        'keras': 'Keras',
        'pytorch': 'PyTorch',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'express': 'Express',
        'expressjs': 'Express',
        'spring': 'Spring',
        'spring boot': 'Spring Boot',
        'springboot': 'Spring Boot',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'k8s': 'Kubernetes',
        'aws': 'AWS',
        'azure': 'Azure',
        'gcp': 'Google Cloud',
        'google cloud': 'Google Cloud',
        'postgresql': 'PostgreSQL',
        'postgres': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'mongo': 'MongoDB',
        'redis': 'Redis',
        'elasticsearch': 'Elasticsearch',
        'graphql': 'GraphQL',
        'rest': 'REST',
        'restful': 'REST',
        'git': 'Git',
        'github': 'GitHub',
        'gitlab': 'GitLab',
        'machine learning': 'Machine Learning',
        'deep learning': 'Deep Learning',
        'artificial intelligence': 'AI',
        'ai': 'AI',
        'ml': 'Machine Learning',
        'data science': 'Data Science',
        'frontend': 'Frontend',
        'backend': 'Backend',
        'fullstack': 'Full Stack',
        'full-stack': 'Full Stack',
        'devops': 'DevOps',
    }

    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize SkillDetector.

        Args:
            min_confidence: Minimum confidence threshold for skills (default: 0.5)
        """
        self.min_confidence = min_confidence
        self.config_loader = ConfigLoader()

        # Load skill aliases configuration
        try:
            self.skill_aliases = self.config_loader.load_skill_aliases()
            logger.info("SkillDetector initialized with skill aliases")
        except Exception as e:
            logger.warning(f"Failed to load skill aliases: {e}. Using built-in normalizations.")
            self.skill_aliases = {}

    async def detect_skills_from_repos(
        self,
        username: str,
        github_client,
        profile: Optional[Dict] = None,
        starred_repos: Optional[List[Dict]] = None,
        max_repos: int = 15
    ) -> List[SkillConfidence]:
        """
        Detect skills from user's repositories.

        Args:
            username: GitHub username
            github_client: GitHubClient instance
            profile: User profile dict (for bio analysis)
            starred_repos: List of starred repositories (optional signal)
            max_repos: Maximum number of repos to analyze (default: 15)

        Returns:
            List of SkillConfidence objects sorted by confidence (highest first)

        Examples:
            >>> detector = SkillDetector()
            >>> client = GitHubClient(token="...")
            >>> skills = await detector.detect_skills_from_repos("torvalds", client)
            >>> skills[0].skill_name
            'C'
            >>> skills[0].confidence_score
            0.85
        """
        # Fetch user repositories
        repos = await github_client.get_repos(username)

        if not repos:
            logger.debug(f"No repositories found for user {username}")
            return []

        # ========================================================================
        # PERFORMANCE OPTIMIZATION: Limit repos to analyze
        # ========================================================================
        original_count = len(repos)
        repos = repos[:max_repos]  # Take only top N (already sorted by stars from API)
        if original_count > max_repos:
            logger.debug(
                f"Limiting analysis for {username}: "
                f"{original_count} repos → {max_repos} repos (top starred)"
            )

        # Aggregate skill signals across all repos
        skill_signals: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # 1. Primary detection: Dependency Graph API
        for repo in repos:
            try:
                dep_graph = await github_client.get_dependency_graph(username, repo.get("name", ""))

                if dep_graph and "dependencies" in dep_graph:
                    for dep in dep_graph["dependencies"]:
                        package_name = dep.get("package_name", "")
                        if package_name:
                            # Normalize package name to skill
                            skill = self._extract_skill_from_package(package_name)
                            if skill:
                                skill_signals[skill]["dependency_graph"] = self.SIGNAL_WEIGHTS["dependency_graph"]
            except Exception as e:
                logger.debug(f"Could not fetch dependency graph for {username}/{repo.get('name')}: {e}")

        # 2. Fallback ensemble detection
        for repo in repos:
            # 2a. Repository topics
            topics = repo.get("topics", [])
            for topic in topics:
                skill = self.normalize_skill(topic)
                if skill:
                    # Increment weight (multiple occurrences increase confidence)
                    current_weight = skill_signals[skill]["repository_topics"]
                    skill_signals[skill]["repository_topics"] = max(
                        current_weight + 0.2,
                        self.SIGNAL_WEIGHTS["repository_topics"]
                    )

            # 2b. Repository language
            language = repo.get("language")
            if language:
                skill = self.normalize_skill(language)
                if skill:
                    current_weight = skill_signals[skill]["repository_language"]
                    skill_signals[skill]["repository_language"] = max(
                        current_weight + 0.15,
                        self.SIGNAL_WEIGHTS["repository_language"]
                    )

            # 2c. Repository name analysis (NEW: Validated signal)
            # Check if repo name contains framework keywords
            # Evidence: 60% coverage, avg 7.8 framework repos per matching candidate
            repo_name = repo.get("name", "").lower()
            repo_desc = (repo.get("description") or "").lower()

            # Extract skills from repo name AND description for better coverage
            detected_skills_from_name = self._extract_skills_from_text(repo_name)
            for skill in detected_skills_from_name:
                # Repository name is a strong signal - increment weight for each occurrence
                current_weight = skill_signals[skill]["repository_name"]
                skill_signals[skill]["repository_name"] = max(
                    current_weight + 0.20,  # +20% per repo with skill in name
                    self.SIGNAL_WEIGHTS["repository_name"]
                )

            # 2d. Repository description
            description = repo.get("description", "")
            if description:
                detected_skills = self._extract_skills_from_text(description)
                for skill in detected_skills:
                    skill_signals[skill]["repository_description"] = 0.4

        # 3. Bio mentions
        if profile and profile.get("bio"):
            bio = profile["bio"]
            detected_skills = self._extract_skills_from_text(bio)
            for skill in detected_skills:
                skill_signals[skill]["bio_mention"] = self.SIGNAL_WEIGHTS["bio_mention"]

        # 4. Starred repositories (optional signal)
        if starred_repos:
            for starred_repo in starred_repos[:50]:  # Limit to 50 most recent
                topics = starred_repo.get("topics", [])
                for topic in topics:
                    skill = self.normalize_skill(topic)
                    if skill:
                        skill_signals[skill]["starred_repos"] = self.SIGNAL_WEIGHTS["starred_repos"]

        # Convert signals to SkillConfidence objects
        skill_confidences = []

        for skill_name, signals in skill_signals.items():
            # Calculate weighted confidence score
            confidence_score = self._calculate_confidence(signals)

            # Determine if primary detection
            is_primary = "dependency_graph" in signals

            # Create SkillConfidence object
            if confidence_score >= self.min_confidence:
                skill_confidences.append(SkillConfidence(
                    skill_name=skill_name,
                    confidence_score=min(confidence_score, 1.0),  # Cap at 1.0
                    detection_signals=list(signals.keys()),
                    signal_weights=dict(signals),
                    is_primary_detection=is_primary
                ))

        # Deduplicate and sort by confidence
        skill_confidences = self._deduplicate_skills(skill_confidences)
        skill_confidences.sort(key=lambda s: s.confidence_score, reverse=True)

        logger.info(f"Detected {len(skill_confidences)} skills for user {username}")

        return skill_confidences

    def normalize_skill(self, skill_name: str) -> str:
        """
        Normalize skill name to canonical form.

        Examples:
            >>> detector = SkillDetector()
            >>> detector.normalize_skill("React.js")
            'React'
            >>> detector.normalize_skill("scikit-learn")
            'Scikit-Learn'
        """
        if not skill_name:
            return skill_name

        skill_lower = skill_name.strip().lower()

        # Check built-in normalizations first
        if skill_lower in self.SKILL_NORMALIZATIONS:
            return self.SKILL_NORMALIZATIONS[skill_lower]

        # Check skill aliases from config
        for canonical_skill, alias_data in self.skill_aliases.items():
            if isinstance(alias_data, dict):
                canonical = alias_data.get("canonical", canonical_skill)
                aliases = alias_data.get("aliases", [])

                # Check if skill_name matches canonical or any alias
                if skill_lower == canonical.lower():
                    return canonical

                for alias in aliases:
                    if skill_lower == alias.lower():
                        return canonical

        # Return title-cased version if no normalization found
        return skill_name.strip().title()

    def get_skill_aliases(self) -> Dict:
        """Get loaded skill aliases configuration."""
        return self.skill_aliases

    def _extract_skill_from_package(self, package_name: str) -> Optional[str]:
        """
        Extract skill name from package/dependency name.

        Examples:
            'pandas' → 'Pandas'
            'scikit-learn' → 'Scikit-Learn'
            'react-dom' → 'React'
            '@tensorflow/tfjs' → 'TensorFlow'
        """
        if not package_name:
            return None

        # Remove scope for npm packages (@angular/core → angular/core)
        package_name = re.sub(r'^@', '', package_name)

        # Extract base name (tensorflow/tfjs → tensorflow)
        base_name = package_name.split('/')[0]

        # Remove common suffixes
        base_name = re.sub(r'-(dom|core|common|http|router|cli|dev|prod)$', '', base_name)

        # Normalize
        return self.normalize_skill(base_name)

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skill names from text (bio, description).

        Uses keyword matching against known skills.
        """
        if not text:
            return []

        text_lower = text.lower()
        detected_skills = []

        # Check against all known skill normalizations
        for skill_variant, canonical_skill in self.SKILL_NORMALIZATIONS.items():
            # Use word boundary matching to avoid false positives
            pattern = r'\b' + re.escape(skill_variant) + r'\b'
            if re.search(pattern, text_lower):
                if canonical_skill not in detected_skills:
                    detected_skills.append(canonical_skill)

        # Check against skill aliases
        for canonical_skill, alias_data in self.skill_aliases.items():
            if isinstance(alias_data, dict):
                canonical = alias_data.get("canonical", canonical_skill)
                all_variants = [canonical] + alias_data.get("aliases", [])

                for variant in all_variants:
                    pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                    if re.search(pattern, text_lower):
                        if canonical not in detected_skills:
                            detected_skills.append(canonical)

        return detected_skills

    def _calculate_confidence(self, signals: Dict[str, float]) -> float:
        """
        Calculate confidence score from weighted signals.

        Uses maximum signal strength with boost for multiple signals.
        """
        if not signals:
            return 0.0

        # Primary detection gets full weight
        if "dependency_graph" in signals:
            return signals["dependency_graph"]

        # For ensemble detection, sum all signal weights
        total_weight = sum(signals.values())

        # Boost factor: more signals = higher confidence (up to 1.5x)
        num_signals = len(signals)
        boost_factor = min(1.0 + (num_signals - 1) * 0.15, 1.5)

        confidence = min(total_weight * boost_factor, 1.0)

        return confidence

    def _deduplicate_skills(self, skills: List[SkillConfidence]) -> List[SkillConfidence]:
        """
        Deduplicate skills, keeping highest confidence for each unique skill.
        """
        skill_map: Dict[str, SkillConfidence] = {}

        for skill in skills:
            skill_key = skill.skill_name.lower()

            if skill_key not in skill_map:
                skill_map[skill_key] = skill
            else:
                # Keep skill with highest confidence
                if skill.confidence_score > skill_map[skill_key].confidence_score:
                    skill_map[skill_key] = skill

        return list(skill_map.values())

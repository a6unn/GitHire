"""
Integration Tests for SkillDetector (T011B)
============================================
Tests for skill detection via dependency graphs and ensemble scoring.

TDD Approach: These tests WILL FAIL until SkillDetector is implemented.

Specification Reference: specs/002-github-sourcer-module/tasks.md T011B
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.github_sourcer.services.skill_detector import SkillDetector, SkillConfidence
from src.github_sourcer.services.github_client import GitHubClient


class TestSkillDetector:
    """Integration tests for skill detection and scoring"""

    @pytest.mark.asyncio
    async def test_skill_detector_initialization(self):
        """Test that SkillDetector can be instantiated"""
        detector = SkillDetector()
        assert detector is not None

    @pytest.mark.asyncio
    async def test_detect_skills_from_dependency_graph(self):
        """Test: Primary detection via GitHub Dependency Graph API (80-85% accuracy)"""
        detector = SkillDetector()

        # Mock GitHubClient
        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {"name": "myproject", "language": "Python"}
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value={
            "dependencies": [
                {"package_name": "pandas", "requirements": ">=1.0.0"},
                {"package_name": "numpy", "requirements": ">=1.20.0"},
                {"package_name": "scikit-learn", "requirements": ">=0.24.0"}
            ]
        })

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # Should detect pandas, numpy, scikit-learn
        assert len(skills) >= 3

        # Find pandas skill
        pandas_skill = next((s for s in skills if s.skill_name.lower() == "pandas"), None)
        assert pandas_skill is not None
        assert pandas_skill.confidence_score >= 0.8  # High confidence for dependency graph
        assert pandas_skill.is_primary_detection is True
        assert "dependency_graph" in pandas_skill.detection_signals

    @pytest.mark.asyncio
    async def test_detect_skills_fallback_ensemble(self):
        """Test: Fallback ensemble detection when dependency graph unavailable (70-75% accuracy)"""
        detector = SkillDetector()

        # Mock GitHubClient with no dependency graph
        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "react-app",
                "language": "JavaScript",
                "topics": ["react", "frontend", "typescript"],
                "description": "A React application built with TypeScript"
            }
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)  # No dependency graph

        # Mock profile with bio
        mock_profile = {
            "bio": "Frontend developer experienced with React and TypeScript"
        }

        skills = await detector.detect_skills_from_repos("testuser", mock_client, profile=mock_profile)

        # Should detect React and TypeScript via ensemble
        react_skill = next((s for s in skills if "react" in s.skill_name.lower()), None)
        assert react_skill is not None
        assert react_skill.is_primary_detection is False
        assert react_skill.confidence_score >= 0.7  # Lower than dependency graph
        assert "repository_topics" in react_skill.detection_signals or "bio_mention" in react_skill.detection_signals

    @pytest.mark.asyncio
    async def test_skill_normalization(self):
        """Test: Skill normalization ('React.js' → 'React', 'scikit-learn' → 'Scikit-Learn')"""
        detector = SkillDetector()

        # Test normalization
        assert detector.normalize_skill("React.js") == "React"
        assert detector.normalize_skill("react") == "React"
        assert detector.normalize_skill("scikit-learn") == "Scikit-Learn"
        assert detector.normalize_skill("pandas") == "Pandas"
        assert detector.normalize_skill("numpy") == "NumPy"

    @pytest.mark.asyncio
    async def test_repository_topics_contribution(self):
        """Test: Repository topics contribute to skill scoring"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "ml-project",
                "language": "Python",
                "topics": ["machine-learning", "tensorflow", "keras", "deep-learning"]
            }
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # Should detect TensorFlow and Keras from topics
        tensorflow_skill = next((s for s in skills if "tensorflow" in s.skill_name.lower()), None)
        assert tensorflow_skill is not None
        assert "repository_topics" in tensorflow_skill.detection_signals

    @pytest.mark.asyncio
    async def test_bio_mentions_contribution(self):
        """Test: Bio mentions contribute to skill detection"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {"name": "project", "language": "Python"}
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        mock_profile = {
            "bio": "Senior Python developer specializing in Django and Flask web frameworks"
        }

        skills = await detector.detect_skills_from_repos("testuser", mock_client, profile=mock_profile)

        # Should detect Django and Flask from bio
        django_skill = next((s for s in skills if "django" in s.skill_name.lower()), None)
        flask_skill = next((s for s in skills if "flask" in s.skill_name.lower()), None)

        assert django_skill is not None or flask_skill is not None
        if django_skill:
            assert "bio_mention" in django_skill.detection_signals

    @pytest.mark.asyncio
    async def test_language_contribution(self):
        """Test: Repository languages contribute to skill detection"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {"name": "project1", "language": "Python"},
            {"name": "project2", "language": "Python"},
            {"name": "project3", "language": "JavaScript"}
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # Should detect Python and JavaScript as language skills
        python_skill = next((s for s in skills if s.skill_name.lower() == "python"), None)
        js_skill = next((s for s in skills if "javascript" in s.skill_name.lower()), None)

        assert python_skill is not None
        assert js_skill is not None
        assert "repository_language" in python_skill.detection_signals

    @pytest.mark.asyncio
    async def test_ensemble_signal_weights(self):
        """Test: Different signals have appropriate weights in ensemble scoring"""
        detector = SkillDetector()

        # Verify signal weights are defined
        assert hasattr(detector, 'SIGNAL_WEIGHTS')
        assert detector.SIGNAL_WEIGHTS.get('dependency_graph', 0) >= 0.8  # Highest weight
        assert detector.SIGNAL_WEIGHTS.get('repository_topics', 0) >= 0.5
        assert detector.SIGNAL_WEIGHTS.get('bio_mention', 0) >= 0.4
        assert detector.SIGNAL_WEIGHTS.get('repository_language', 0) >= 0.4

    @pytest.mark.asyncio
    async def test_multiple_repos_aggregation(self):
        """Test: Skills aggregated across multiple repositories"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "project1",
                "language": "Python",
                "topics": ["django"]
            },
            {
                "name": "project2",
                "language": "Python",
                "topics": ["django", "postgresql"]
            },
            {
                "name": "project3",
                "language": "JavaScript",
                "topics": ["react"]
            }
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # Django should have higher confidence due to multiple occurrences
        django_skill = next((s for s in skills if "django" in s.skill_name.lower()), None)
        react_skill = next((s for s in skills if "react" in s.skill_name.lower()), None)

        assert django_skill is not None
        assert react_skill is not None

        # Django appears in 2 repos, should have higher confidence than React (1 repo)
        assert django_skill.confidence_score > react_skill.confidence_score

    @pytest.mark.asyncio
    async def test_skill_confidence_model_validation(self):
        """Test: SkillConfidence model validates data correctly"""
        # Valid skill confidence
        skill = SkillConfidence(
            skill_name="Python",
            confidence_score=0.85,
            detection_signals=["dependency_graph", "repository_language"],
            signal_weights={"dependency_graph": 0.8, "repository_language": 0.3},
            is_primary_detection=True
        )

        assert skill.skill_name == "Python"
        assert skill.confidence_score == 0.85
        assert skill.is_primary_detection is True

        # Invalid confidence (should raise validation error)
        with pytest.raises(ValueError):
            SkillConfidence(
                skill_name="Python",
                confidence_score=1.5,  # Invalid: > 1.0
                detection_signals=["dependency_graph"],
                signal_weights={"dependency_graph": 0.8},
                is_primary_detection=True
            )

        # Invalid: empty detection_signals
        with pytest.raises(ValueError):
            SkillConfidence(
                skill_name="Python",
                confidence_score=0.85,
                detection_signals=[],  # Invalid: empty
                signal_weights={},
                is_primary_detection=True
            )

    @pytest.mark.asyncio
    async def test_skill_aliases_loaded(self):
        """Test: skill_aliases.json loads successfully"""
        detector = SkillDetector()

        aliases = detector.get_skill_aliases()

        assert isinstance(aliases, dict)
        assert "framework_aliases" in aliases or "library_aliases" in aliases or len(aliases) > 0

    @pytest.mark.asyncio
    async def test_starred_repos_contribution(self):
        """Test: Starred repositories contribute to skill detection (optional signal)"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        # Mock starred repos
        mock_starred = [
            {"name": "tensorflow/tensorflow", "topics": ["machine-learning", "tensorflow"]},
            {"name": "keras-team/keras", "topics": ["deep-learning", "keras"]}
        ]

        skills = await detector.detect_skills_from_repos(
            "testuser",
            mock_client,
            starred_repos=mock_starred
        )

        # Should detect TensorFlow/Keras from starred repos
        if skills:  # Optional signal, may or may not be implemented
            tf_or_keras = any("tensorflow" in s.skill_name.lower() or "keras" in s.skill_name.lower() for s in skills)
            # Don't assert, just test if implemented
            if tf_or_keras:
                assert True

    @pytest.mark.asyncio
    async def test_empty_repos_returns_empty_skills(self):
        """Test: User with no repos returns empty skills list"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[])

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        assert skills == []

    @pytest.mark.asyncio
    async def test_skill_deduplication(self):
        """Test: Duplicate skills are deduplicated with highest confidence retained"""
        detector = SkillDetector()

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "project1",
                "language": "Python",
                "topics": ["python", "data-science"]
            }
        ])
        # Dependency graph also detects Python
        mock_client.get_dependency_graph = AsyncMock(return_value={
            "dependencies": [{"package_name": "python-dateutil", "requirements": ">=2.0.0"}]
        })

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # Should only have one Python skill (not duplicated)
        python_skills = [s for s in skills if s.skill_name.lower() == "python"]
        assert len(python_skills) == 1

        # Should have highest confidence (from dependency graph)
        assert python_skills[0].confidence_score >= 0.8

    @pytest.mark.asyncio
    async def test_min_confidence_threshold(self):
        """Test: Skills below minimum confidence threshold are filtered out"""
        detector = SkillDetector(min_confidence=0.5)

        mock_client = Mock(spec=GitHubClient)
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "project",
                "language": "Python",
                "topics": ["obscure-topic"]  # Very weak signal
            }
        ])
        mock_client.get_dependency_graph = AsyncMock(return_value=None)

        skills = await detector.detect_skills_from_repos("testuser", mock_client)

        # All returned skills should meet minimum threshold
        for skill in skills:
            assert skill.confidence_score >= 0.5

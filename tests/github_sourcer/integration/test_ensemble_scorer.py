"""
Integration Tests for EnsembleScorer (T011C)
=============================================
Tests for ensemble scoring combining multiple signals for candidate ranking.

TDD Approach: These tests WILL FAIL until EnsembleScorer is implemented.

Specification Reference: specs/002-github-sourcer-module/tasks.md T011C
"""

import pytest
from src.github_sourcer.services.ensemble_scorer import EnsembleScorer, CandidateScore
from src.github_sourcer.models.skill_confidence import SkillConfidence
from src.github_sourcer.models.location_hierarchy import LocationHierarchy


class TestEnsembleScorer:
    """Integration tests for ensemble scoring and ranking"""

    def test_ensemble_scorer_initialization(self):
        """Test that EnsembleScorer can be instantiated"""
        scorer = EnsembleScorer()
        assert scorer is not None

    def test_score_candidate_with_all_signals(self):
        """Test: Candidate with skill match, location match, and activity → high score"""
        scorer = EnsembleScorer()

        # Mock candidate data
        candidate = {
            "username": "johndoe",
            "profile": {
                "public_repos": 50,
                "followers": 1000,
                "created_at": "2018-01-01T00:00:00Z"
            }
        }

        # Skills with high confidence
        skills = [
            SkillConfidence(
                skill_name="Python",
                confidence_score=0.85,
                detection_signals=["dependency_graph"],
                signal_weights={"dependency_graph": 0.85},
                is_primary_detection=True
            ),
            SkillConfidence(
                skill_name="Django",
                confidence_score=0.8,
                detection_signals=["dependency_graph"],
                signal_weights={"dependency_graph": 0.85},
                is_primary_detection=True
            )
        ]

        # Location match
        search_location = LocationHierarchy(
            original_text="Chennai",
            city="Chennai",
            state=None,
            country=None,
            match_confidence=1.0,
            match_level="city"
        )

        candidate_location = LocationHierarchy(
            original_text="Chennai, Tamil Nadu, India",
            city="Chennai",
            state="Tamil Nadu",
            country="India",
            match_confidence=1.0,
            match_level="city"
        )

        # Required skills
        required_skills = ["Python", "Django"]

        score = scorer.score_candidate(
            candidate=candidate,
            skills=skills,
            location_match=(candidate_location, "city", 1.0),
            search_location=search_location,
            required_skills=required_skills
        )

        assert isinstance(score, CandidateScore)
        assert score.total_score >= 0.8  # High score for all signals matching
        assert score.skill_match_score > 0
        assert score.location_match_score > 0
        assert score.activity_score > 0

    def test_score_candidate_skill_matching(self):
        """Test: Skill matching contributes to score (weight: 0.5)"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "pythondev",
            "profile": {"public_repos": 10, "followers": 50}
        }

        # Strong skill match
        skills = [
            SkillConfidence(
                skill_name="Python",
                confidence_score=0.9,
                detection_signals=["dependency_graph"],
                signal_weights={"dependency_graph": 0.85},
                is_primary_detection=True
            )
        ]

        required_skills = ["Python"]

        score = scorer.score_candidate(
            candidate=candidate,
            skills=skills,
            required_skills=required_skills
        )

        assert score.skill_match_score >= 0.8  # Strong match
        assert "skill_match" in score.signal_contributions

    def test_score_candidate_location_matching(self):
        """Test: Location matching contributes to score (weight: 0.3)"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "localdev",
            "profile": {"public_repos": 10, "followers": 50}
        }

        search_location = LocationHierarchy(
            original_text="Bangalore",
            city="Bengaluru",
            state=None,
            country=None,
            match_confidence=1.0,
            match_level="city"
        )

        candidate_location = LocationHierarchy(
            original_text="Bengaluru, Karnataka, India",
            city="Bengaluru",
            state="Karnataka",
            country="India",
            match_confidence=1.0,
            match_level="city"
        )

        score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            location_match=(candidate_location, "city", 1.0),
            search_location=search_location
        )

        assert score.location_match_score >= 0.9  # City-level match
        assert "location_match" in score.signal_contributions

    def test_score_candidate_activity_scoring(self):
        """Test: Activity (repos, followers, recency) contributes to score (weight: 0.2)"""
        scorer = EnsembleScorer()

        # Highly active candidate
        active_candidate = {
            "username": "activedev",
            "profile": {
                "public_repos": 100,
                "followers": 5000,
                "created_at": "2020-01-01T00:00:00Z"
            }
        }

        # Less active candidate
        inactive_candidate = {
            "username": "inactivedev",
            "profile": {
                "public_repos": 5,
                "followers": 10,
                "created_at": "2015-01-01T00:00:00Z"
            }
        }

        active_score = scorer.score_candidate(
            candidate=active_candidate,
            skills=[]
        )

        inactive_score = scorer.score_candidate(
            candidate=inactive_candidate,
            skills=[]
        )

        assert active_score.activity_score > inactive_score.activity_score
        assert "activity" in active_score.signal_contributions

    def test_ensemble_weights_correct(self):
        """Test: Ensemble weights sum to 1.0 (skill:0.5, location:0.3, activity:0.2)"""
        scorer = EnsembleScorer()

        assert hasattr(scorer, 'ENSEMBLE_WEIGHTS')
        assert scorer.ENSEMBLE_WEIGHTS.get('skill_match', 0) == 0.5
        assert scorer.ENSEMBLE_WEIGHTS.get('location_match', 0) == 0.3
        assert scorer.ENSEMBLE_WEIGHTS.get('activity', 0) == 0.2

        # Weights should sum to 1.0
        total_weight = sum(scorer.ENSEMBLE_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001  # Allow for floating point precision

    def test_rank_candidates(self):
        """Test: rank_candidates() returns candidates sorted by total_score (descending)"""
        scorer = EnsembleScorer()

        candidate1 = {
            "username": "candidate1",
            "profile": {"public_repos": 100, "followers": 1000}
        }

        candidate2 = {
            "username": "candidate2",
            "profile": {"public_repos": 50, "followers": 500}
        }

        candidate3 = {
            "username": "candidate3",
            "profile": {"public_repos": 20, "followers": 100}
        }

        # High skill match for candidate1
        skills1 = [
            SkillConfidence(
                skill_name="Python",
                confidence_score=0.9,
                detection_signals=["dependency_graph"],
                signal_weights={"dependency_graph": 0.85},
                is_primary_detection=True
            )
        ]

        # Medium skill match for candidate2
        skills2 = [
            SkillConfidence(
                skill_name="Python",
                confidence_score=0.7,
                detection_signals=["repository_topics"],
                signal_weights={"repository_topics": 0.6},
                is_primary_detection=False
            )
        ]

        # No skills for candidate3
        skills3 = []

        required_skills = ["Python"]

        candidates_data = [
            (candidate1, skills1, None),
            (candidate2, skills2, None),
            (candidate3, skills3, None)
        ]

        ranked = scorer.rank_candidates(
            candidates_data=candidates_data,
            required_skills=required_skills
        )

        assert len(ranked) == 3
        # Should be sorted by score (descending)
        assert ranked[0].username == "candidate1"
        assert ranked[1].username == "candidate2"
        assert ranked[2].username == "candidate3"

        # Scores should be descending
        assert ranked[0].total_score >= ranked[1].total_score
        assert ranked[1].total_score >= ranked[2].total_score

    def test_skill_match_score_calculation(self):
        """Test: Skill match score based on overlap with required skills"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "skilldev",
            "profile": {"public_repos": 10, "followers": 50}
        }

        # Has 2 out of 3 required skills
        skills = [
            SkillConfidence(skill_name="Python", confidence_score=0.9,
                          detection_signals=["dependency_graph"], signal_weights={}, is_primary_detection=True),
            SkillConfidence(skill_name="Django", confidence_score=0.8,
                          detection_signals=["dependency_graph"], signal_weights={}, is_primary_detection=True),
            SkillConfidence(skill_name="JavaScript", confidence_score=0.7,
                          detection_signals=["repository_topics"], signal_weights={}, is_primary_detection=False)
        ]

        required_skills = ["Python", "Django", "React"]  # Missing React

        score = scorer.score_candidate(
            candidate=candidate,
            skills=skills,
            required_skills=required_skills
        )

        # 2 out of 3 skills matched with high confidence
        # Formula: (2/3) * avg_confidence(0.9, 0.8) = 0.667 * 0.85 = 0.567
        assert 0.55 <= score.skill_match_score <= 0.7

    def test_hierarchical_location_scoring(self):
        """Test: City match (1.0) > State match (0.7) > Country match (0.3)"""
        scorer = EnsembleScorer()

        candidate = {"username": "geotest", "profile": {"public_repos": 10}}

        search_location = LocationHierarchy(
            original_text="Chennai",
            city="Chennai",
            state=None,
            country=None,
            match_confidence=1.0,
            match_level="city"
        )

        # City-level match
        city_match_location = LocationHierarchy(
            original_text="Chennai, Tamil Nadu, India",
            city="Chennai",
            state="Tamil Nadu",
            country="India",
            match_confidence=1.0,
            match_level="city"
        )

        city_score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            location_match=(city_match_location, "city", 1.0),
            search_location=search_location
        )

        # State-level match
        search_state = LocationHierarchy(
            original_text="Tamil Nadu",
            city=None,
            state="Tamil Nadu",
            country=None,
            match_confidence=1.0,
            match_level="state"
        )

        state_score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            location_match=(city_match_location, "state", 0.7),
            search_location=search_state
        )

        # Country-level match
        search_country = LocationHierarchy(
            original_text="India",
            city=None,
            state=None,
            country="India",
            match_confidence=1.0,
            match_level="country"
        )

        country_score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            location_match=(city_match_location, "country", 0.3),
            search_location=search_country
        )

        assert city_score.location_match_score > state_score.location_match_score
        assert state_score.location_match_score > country_score.location_match_score

    def test_candidate_score_model_validation(self):
        """Test: CandidateScore model validates data correctly"""
        # Valid candidate score
        score = CandidateScore(
            username="testuser",
            total_score=0.85,
            skill_match_score=0.9,
            location_match_score=0.8,
            activity_score=0.7,
            signal_contributions={
                "skill_match": 0.45,
                "location_match": 0.24,
                "activity": 0.14
            }
        )

        assert score.username == "testuser"
        assert score.total_score == 0.85

        # Invalid: total_score > 1.0
        with pytest.raises(ValueError):
            CandidateScore(
                username="testuser",
                total_score=1.5,  # Invalid
                skill_match_score=0.9,
                location_match_score=0.8,
                activity_score=0.7,
                signal_contributions={}
            )

        # Invalid: total_score < 0.0
        with pytest.raises(ValueError):
            CandidateScore(
                username="testuser",
                total_score=-0.1,  # Invalid
                skill_match_score=0.9,
                location_match_score=0.8,
                activity_score=0.7,
                signal_contributions={}
            )

    def test_activity_score_components(self):
        """Test: Activity score considers repos, followers, and account age"""
        scorer = EnsembleScorer()

        # Test repos contribution
        many_repos = {"username": "repomaster", "profile": {"public_repos": 200, "followers": 10}}
        few_repos = {"username": "beginner", "profile": {"public_repos": 5, "followers": 10}}

        score_many = scorer.score_candidate(candidate=many_repos, skills=[])
        score_few = scorer.score_candidate(candidate=few_repos, skills=[])

        # More repos should contribute to higher activity score
        assert score_many.activity_score > score_few.activity_score

    def test_missing_location_handled_gracefully(self):
        """Test: Missing location data doesn't crash scoring"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "nolocdev",
            "profile": {"public_repos": 10, "followers": 50}
        }

        # No location data provided
        score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            location_match=None
        )

        assert score.location_match_score == 0.0
        assert score.total_score >= 0.0  # Should still have activity score

    def test_missing_skills_handled_gracefully(self):
        """Test: Empty skills list doesn't crash scoring"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "noskilldev",
            "profile": {"public_repos": 10, "followers": 50}
        }

        score = scorer.score_candidate(
            candidate=candidate,
            skills=[],
            required_skills=["Python"]
        )

        assert score.skill_match_score == 0.0
        assert score.total_score >= 0.0  # Should still have activity score

    def test_no_required_skills_uses_all_skills(self):
        """Test: If no required_skills specified, consider all detected skills"""
        scorer = EnsembleScorer()

        candidate = {
            "username": "multiskill",
            "profile": {"public_repos": 50, "followers": 500}
        }

        skills = [
            SkillConfidence(skill_name="Python", confidence_score=0.9,
                          detection_signals=["dependency_graph"], signal_weights={}, is_primary_detection=True),
            SkillConfidence(skill_name="Django", confidence_score=0.85,
                          detection_signals=["dependency_graph"], signal_weights={}, is_primary_detection=True),
            SkillConfidence(skill_name="PostgreSQL", confidence_score=0.8,
                          detection_signals=["repository_topics"], signal_weights={}, is_primary_detection=False)
        ]

        # No required skills - should consider all skills
        score = scorer.score_candidate(
            candidate=candidate,
            skills=skills,
            required_skills=None
        )

        assert score.skill_match_score > 0  # Should have positive skill score
        assert score.total_score > 0

    def test_rank_candidates_with_min_score_threshold(self):
        """Test: rank_candidates() can filter by minimum score threshold"""
        scorer = EnsembleScorer()

        candidate1 = {"username": "highscore", "profile": {"public_repos": 100, "followers": 1000}}
        candidate2 = {"username": "lowscore", "profile": {"public_repos": 5, "followers": 10}}

        skills1 = [
            SkillConfidence(skill_name="Python", confidence_score=0.9,
                          detection_signals=["dependency_graph"], signal_weights={}, is_primary_detection=True)
        ]

        candidates_data = [
            (candidate1, skills1, None),
            (candidate2, [], None)
        ]

        # Rank with minimum threshold of 0.5
        ranked = scorer.rank_candidates(
            candidates_data=candidates_data,
            required_skills=["Python"],
            min_score=0.5
        )

        # Should only include candidates above threshold
        assert all(c.total_score >= 0.5 for c in ranked)
        assert len(ranked) <= 2  # May filter out low-scoring candidate

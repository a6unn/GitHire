"""Contract tests for Candidate validation rules.

Tests Pydantic validation logic for Candidate model.
These tests will FAIL until T012 (Candidate model) is implemented.
"""

import pytest
from datetime import datetime


def test_candidate_model_imports():
    """Test that Candidate and Repository models can be imported."""
    try:
        from src.github_sourcer.models.candidate import Candidate, Repository
        assert Candidate is not None
        assert Repository is not None
    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_negative_contribution_count_fails():
    """contribution_count < 0 should raise ValidationError."""
    try:
        from src.github_sourcer.models.candidate import Candidate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Candidate(
                github_username="test",
                contribution_count=-10,  # Invalid
                account_age_days=100,
                followers=10,
                profile_url="https://github.com/test",
                top_repos=[],
                languages=[],
                fetched_at=datetime.utcnow()
            )

        assert "greater than or equal to 0" in str(exc_info.value).lower()

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_negative_account_age_fails():
    """account_age_days < 0 should raise ValidationError."""
    try:
        from src.github_sourcer.models.candidate import Candidate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Candidate(
                github_username="test",
                contribution_count=100,
                account_age_days=-5,  # Invalid
                followers=10,
                profile_url="https://github.com/test",
                top_repos=[],
                languages=[],
                fetched_at=datetime.utcnow()
            )

        assert "greater than or equal to 0" in str(exc_info.value).lower()

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_top_repos_truncated_to_5():
    """top_repos with >5 items should be truncated to 5."""
    try:
        from src.github_sourcer.models.candidate import Candidate, Repository

        repos = [
            Repository(
                name=f"repo{i}",
                description=f"Description {i}",
                stars=100 - i,
                forks=10,
                languages=["Python"],
                url=f"https://github.com/user/repo{i}"
            )
            for i in range(10)  # 10 repos
        ]

        candidate = Candidate(
            github_username="test",
            contribution_count=100,
            account_age_days=365,
            followers=10,
            profile_url="https://github.com/test",
            top_repos=repos,
            languages=["Python"],
            fetched_at=datetime.utcnow()
        )

        # Should only keep top 5
        assert len(candidate.top_repos) == 5

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_languages_deduplicated_and_sorted():
    """languages should be deduplicated and sorted alphabetically."""
    try:
        from src.github_sourcer.models.candidate import Candidate

        candidate = Candidate(
            github_username="test",
            contribution_count=100,
            account_age_days=365,
            followers=10,
            profile_url="https://github.com/test",
            top_repos=[],
            languages=["Python", "JavaScript", "Python", "C", "JavaScript"],  # Duplicates
            fetched_at=datetime.utcnow()
        )

        # Should be deduplicated and sorted
        assert candidate.languages == ["C", "JavaScript", "Python"]

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_empty_username_fails():
    """Empty github_username should raise ValidationError."""
    try:
        from src.github_sourcer.models.candidate import Candidate
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Candidate(
                github_username="",  # Invalid
                contribution_count=100,
                account_age_days=365,
                followers=10,
                profile_url="https://github.com/test",
                top_repos=[],
                languages=[],
                fetched_at=datetime.utcnow()
            )

        assert "at least 1 character" in str(exc_info.value).lower()

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_fetched_at_defaults_to_now():
    """fetched_at should default to current time if not provided."""
    try:
        from src.github_sourcer.models.candidate import Candidate

        before = datetime.utcnow()
        candidate = Candidate(
            github_username="test",
            contribution_count=100,
            account_age_days=365,
            followers=10,
            profile_url="https://github.com/test",
            top_repos=[],
            languages=[]
            # fetched_at not provided - should default
        )
        after = datetime.utcnow()

        # Should be set to current time
        assert before <= candidate.fetched_at <= after

    except ImportError as e:
        pytest.fail(f"Candidate model not implemented yet: {e}")


def test_repository_validation():
    """Repository model should validate required fields."""
    try:
        from src.github_sourcer.models.candidate import Repository
        from pydantic import ValidationError

        # Valid repository
        repo = Repository(
            name="linux",
            description="Linux kernel",
            stars=150000,
            forks=50000,
            languages=["C", "Assembly"],
            url="https://github.com/torvalds/linux"
        )
        assert repo.name == "linux"

        # Invalid: negative stars
        with pytest.raises(ValidationError):
            Repository(
                name="test",
                stars=-10,  # Invalid
                forks=5,
                languages=["Python"],
                url="https://github.com/test/test"
            )

    except ImportError as e:
        pytest.fail(f"Repository model not implemented yet: {e}")

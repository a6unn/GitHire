"""Integration tests for PersonalizationEngine."""

import pytest

from src.outreach_generator.personalization import PersonalizationEngine
from src.github_sourcer.models.candidate import Candidate, Repository
from src.jd_parser.models import JobRequirement, YearsOfExperience


class TestPersonalizationEngine:
    """Test PersonalizationEngine repo selection and depth determination."""

    @pytest.fixture
    def engine(self):
        """Create PersonalizationEngine instance."""
        return PersonalizationEngine()

    @pytest.fixture
    def python_job_req(self):
        """Create job requirement for Python developer."""
        return JobRequirement(
            role="Senior Python Developer",
            required_skills=["Python", "FastAPI", "Docker"],
            preferred_skills=["PostgreSQL"],
            years_of_experience=YearsOfExperience(min=5, max=None, range_text="5+ years"),
            location_preferences=["Remote"],
            seniority_level="Senior",
            original_input="Looking for a Senior Python Developer with 5+ years experience in FastAPI and Docker."
        )

    @pytest.fixture
    def go_job_req(self):
        """Create job requirement for Go developer."""
        return JobRequirement(
            role="Backend Engineer",
            required_skills=["Go", "Kubernetes"],
            preferred_skills=["Docker"],
            years_of_experience=YearsOfExperience(min=3, max=None, range_text="3+ years"),
            location_preferences=["Remote"],
            seniority_level="Mid-level",
            original_input="Looking for a Backend Engineer with 3+ years experience in Go and Kubernetes."
        )

    @pytest.fixture
    def candidate_with_python_repos(self):
        """Create candidate with Python repositories."""
        return Candidate(
            github_username="pythondev",
            name="Python Developer",
            bio="Full-stack Python engineer",
            location="India",
            email=None,
            company=None,
            followers=150,
            following=50,
            public_repos=25,
            contribution_count=1200,
            account_age_days=1500,
            languages=["Python", "JavaScript", "Shell"],
            top_repos=[
                Repository(
                    name="fastapi-backend",
                    description="Production FastAPI backend with PostgreSQL",
                    stars=120,
                    forks=25,
                    languages=["Python"],
                    url="https://github.com/pythondev/fastapi-backend"
                ),
                Repository(
                    name="docker-compose-templates",
                    description="Docker compose files for microservices",
                    stars=45,
                    forks=10,
                    languages=["Shell"],
                    url="https://github.com/pythondev/docker-compose-templates"
                ),
                Repository(
                    name="ml-experiments",
                    description="Machine learning experiments in Python",
                    stars=30,
                    forks=5,
                    languages=["Python"],
                    url="https://github.com/pythondev/ml-experiments"
                )
            ],
            profile_url="https://github.com/pythondev"
        )

    @pytest.fixture
    def candidate_with_go_repos(self):
        """Create candidate with Go repositories."""
        return Candidate(
            github_username="gopher",
            name="Go Developer",
            bio="Backend engineer specializing in Go",
            location="USA",
            email=None,
            company="TechCorp",
            followers=200,
            following=80,
            public_repos=30,
            contribution_count=1500,
            account_age_days=2000,
            languages=["Go", "Python", "Shell"],
            top_repos=[
                Repository(
                    name="k8s-operator",
                    description="Kubernetes operator written in Go",
                    stars=250,
                    forks=50,
                    languages=["Go"],
                    url="https://github.com/gopher/k8s-operator"
                ),
                Repository(
                    name="grpc-microservice",
                    description="gRPC microservice template",
                    stars=100,
                    forks=20,
                    languages=["Go"],
                    url="https://github.com/gopher/grpc-microservice"
                ),
                Repository(
                    name="dotfiles",
                    description="My dotfiles",
                    stars=5,
                    forks=1,
                    languages=["Shell"],
                    url="https://github.com/gopher/dotfiles"
                )
            ],
            profile_url="https://github.com/gopher"
        )

    @pytest.fixture
    def candidate_with_no_repos(self):
        """Create candidate with no repositories."""
        return Candidate(
            github_username="newbie",
            name="New Developer",
            bio="Just starting out",
            location="Remote",
            email=None,
            company=None,
            followers=10,
            following=20,
            public_repos=0,
            contribution_count=50,
            account_age_days=90,
            languages=[],
            top_repos=[],
            profile_url="https://github.com/newbie"
        )

    def test_select_relevant_repos_python_match(self, engine, python_job_req, candidate_with_python_repos):
        """Test selecting repos when candidate has matching Python repos."""
        repos = engine.select_relevant_repos(candidate_with_python_repos, python_job_req)

        assert len(repos) == 3
        # Top repo should be fastapi-backend (matches Python, FastAPI, PostgreSQL)
        assert repos[0]["name"] == "fastapi-backend"
        assert "Python" in repos[0]["languages"]
        assert repos[0]["relevance_score"] > 0

        # Verify all repos have required fields
        for repo in repos:
            assert "name" in repo
            assert "description" in repo
            assert "stars" in repo
            assert "languages" in repo
            assert "relevance_score" in repo

    def test_select_relevant_repos_sorted_by_relevance(self, engine, python_job_req, candidate_with_python_repos):
        """Test repos are sorted by relevance score."""
        repos = engine.select_relevant_repos(candidate_with_python_repos, python_job_req)

        # fastapi-backend should score highest (Python + FastAPI keywords)
        assert repos[0]["name"] == "fastapi-backend"
        # Second should be either docker or ml-experiments (Python repos)
        assert repos[1]["name"] in ["docker-compose-templates", "ml-experiments"]

        # Verify scores are descending
        assert repos[0]["relevance_score"] >= repos[1]["relevance_score"]
        assert repos[1]["relevance_score"] >= repos[2]["relevance_score"]

    def test_select_relevant_repos_go_job_python_candidate(self, engine, go_job_req, candidate_with_python_repos):
        """Test selecting repos when candidate's skills don't match job (Python dev for Go job)."""
        repos = engine.select_relevant_repos(candidate_with_python_repos, go_job_req)

        # Should still return repos (fallback to most popular)
        assert len(repos) == 3
        # fastapi-backend has most stars, should rank high despite no Go match
        assert repos[0]["name"] == "fastapi-backend"

    def test_select_relevant_repos_no_repos(self, engine, python_job_req, candidate_with_no_repos):
        """Test selecting repos when candidate has no repositories."""
        repos = engine.select_relevant_repos(candidate_with_no_repos, python_job_req)

        assert repos == []

    def test_select_relevant_repos_returns_top_3(self, engine, python_job_req):
        """Test that only top 3 repos are returned even if candidate has more."""
        # Create candidate with 5 repos
        candidate = Candidate(
            github_username="prolific",
            name="Prolific Dev",
            bio="Lots of projects",
            location="Remote",
            email=None,
            company=None,
            followers=100,
            following=50,
            public_repos=50,
            contribution_count=800,
            account_age_days=1200,
            languages=["Python"],
            top_repos=[
                Repository(name=f"repo-{i}", description="Python project", stars=i*10, forks=i*2,
                          languages=["Python"], url=f"https://github.com/prolific/repo-{i}")
                for i in range(1, 6)
            ],
            profile_url="https://github.com/prolific"
        )

        repos = engine.select_relevant_repos(candidate, python_job_req)

        assert len(repos) == 3

    def test_determine_personalization_depth_deep(self, engine):
        """Test depth determination for top-ranked candidates (1-5)."""
        assert engine.determine_personalization_depth(1) == "deep"
        assert engine.determine_personalization_depth(3) == "deep"
        assert engine.determine_personalization_depth(5) == "deep"

    def test_determine_personalization_depth_medium(self, engine):
        """Test depth determination for mid-ranked candidates (6-15)."""
        assert engine.determine_personalization_depth(6) == "medium"
        assert engine.determine_personalization_depth(10) == "medium"
        assert engine.determine_personalization_depth(15) == "medium"

    def test_determine_personalization_depth_surface(self, engine):
        """Test depth determination for lower-ranked candidates (16+)."""
        assert engine.determine_personalization_depth(16) == "surface"
        assert engine.determine_personalization_depth(20) == "surface"
        assert engine.determine_personalization_depth(100) == "surface"

    def test_repo_scoring_language_match(self, engine):
        """Test that repos with matching language score higher."""
        python_repo = Repository(
            name="test-repo",
            description="A test repo",
            stars=10,
            forks=2,
            languages=["Python"],
            url="https://github.com/user/test-repo"
        )

        go_repo = Repository(
            name="other-repo",
            description="Another repo",
            stars=10,
            forks=2,
            languages=["Go"],
            url="https://github.com/user/other-repo"
        )

        python_score = engine._score_repo(python_repo, ["python"], None)
        go_score = engine._score_repo(go_repo, ["python"], None)

        assert python_score > go_score

    def test_repo_scoring_keyword_match_in_description(self, engine):
        """Test that repos with job keywords in description score higher."""
        fastapi_repo = Repository(
            name="backend",
            description="FastAPI backend with PostgreSQL",
            stars=10,
            forks=2,
            languages=["Python"],
            url="https://github.com/user/backend"
        )

        generic_repo = Repository(
            name="script",
            description="Some Python script",
            stars=10,
            forks=2,
            languages=["Python"],
            url="https://github.com/user/script"
        )

        fastapi_score = engine._score_repo(fastapi_repo, ["python", "fastapi", "postgresql"], None)
        generic_score = engine._score_repo(generic_repo, ["python", "fastapi", "postgresql"], None)

        assert fastapi_score > generic_score

    def test_repo_scoring_domain_relevance(self, engine):
        """Test that domain relevance boosts score."""
        ml_repo = Repository(
            name="ml-project",
            description="Machine learning experiments",
            stars=10,
            forks=2,
            languages=["Python"],
            url="https://github.com/user/ml-project"
        )

        generic_repo = Repository(
            name="utils",
            description="Utility functions",
            stars=10,
            forks=2,
            languages=["Python"],
            url="https://github.com/user/utils"
        )

        ml_score = engine._score_repo(ml_repo, ["python"], "machine learning")
        generic_score = engine._score_repo(generic_repo, ["python"], "machine learning")

        assert ml_score > generic_score

    def test_repo_scoring_stars_contribute(self, engine):
        """Test that stars contribute to score (as tie-breaker)."""
        high_stars_repo = Repository(
            name="popular",
            description="Popular repo",
            stars=500,
            forks=100,
            languages=["Python"],
            url="https://github.com/user/popular"
        )

        low_stars_repo = Repository(
            name="unpopular",
            description="Less popular repo",
            stars=5,
            forks=1,
            languages=["Python"],
            url="https://github.com/user/unpopular"
        )

        high_score = engine._score_repo(high_stars_repo, ["python"], None)
        low_score = engine._score_repo(low_stars_repo, ["python"], None)

        # Both match Python, but stars should make high_score slightly higher
        assert high_score > low_score

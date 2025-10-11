"""Integration tests for ContentValidator."""

import pytest

from src.outreach_generator.content_validator import ContentValidator
from src.github_sourcer.models.candidate import Candidate


class TestContentValidator:
    """Test ContentValidator safety and quality checks."""

    @pytest.fixture
    def validator(self):
        """Create ContentValidator instance."""
        return ContentValidator()

    @pytest.fixture
    def sample_candidate(self):
        """Create sample candidate."""
        return Candidate(
            github_username="johndoe",
            name="John Doe",
            bio="Software Engineer",
            location="USA",
            email=None,
            company=None,
            followers=100,
            following=50,
            public_repos=20,
            contribution_count=500,
            account_age_days=1000,
            languages=["Python"],
            top_repos=[],
            profile_url="https://github.com/johndoe"
        )

    def test_valid_message_passes(self, validator, sample_candidate):
        """Test that a well-formed message passes validation."""
        message = """
        Hi John,

        I came across your GitHub profile and was impressed by your Python work.
        We're looking for a Senior Backend Engineer and I think you'd be a great fit.
        Your experience with backend systems really aligns with what we're building.
        The role involves working on distributed microservices using Python and Go.
        You'd be joining a team of talented engineers working on challenging problems.

        Would love to chat more about this opportunity. Let me know if you're interested
        in learning more about the position and our company!

        Best regards
        """

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is True
        assert len(errors) == 0

    def test_too_short_message_rejected(self, validator, sample_candidate):
        """Test that messages shorter than 50 words are rejected."""
        message = "Hi John, interested in a job? Let me know!"

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert any("too short" in err.lower() for err in errors)

    def test_too_long_message_rejected(self, validator, sample_candidate):
        """Test that messages longer than 1000 words are rejected."""
        # Create a very long message (> 1000 words)
        message = " ".join(["word"] * 1100)

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert any("too long" in err.lower() for err in errors)

    def test_offensive_content_rejected(self, validator, sample_candidate):
        """Test that offensive language is rejected."""
        message = """
        Hi John,

        I noticed your GitHub profile and your projects look stupid.
        We're looking for engineers and I think you might be interested.
        """ + " ".join(["filler"] * 50)  # Pad to meet length requirement

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert any("offensive" in err.lower() for err in errors)

    def test_message_without_candidate_mention_flagged(self, validator, sample_candidate):
        """Test that messages not mentioning candidate are flagged."""
        message = """
        Hello,

        We are looking for a Software Engineer to join our team.
        This is a great opportunity to work on cutting-edge technology
        with a talented team. """ + " ".join(["More details about the role."] * 10)

        message += " Please reach out if interested."

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert any("mention candidate" in err.lower() for err in errors)

    def test_message_mentions_username_passes(self, validator, sample_candidate):
        """Test that message mentioning username passes candidate check."""
        message = """
        Hi johndoe,

        I found your GitHub profile and was impressed by your work.
        We have an exciting opportunity for a backend engineer.
        """ + " ".join(["More details."] * 15)

        message += " Would love to connect and discuss further!"

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is True
        assert len(errors) == 0

    def test_message_mentions_first_name_passes(self, validator, sample_candidate):
        """Test that message mentioning first name passes candidate check."""
        message = """
        Hello John,

        I came across your profile and wanted to reach out about a position.
        """ + " ".join(["More context about role."] * 15)

        message += " Let me know if you'd like to discuss!"

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is True
        assert len(errors) == 0

    def test_message_without_cta_flagged(self, validator, sample_candidate):
        """Test that messages without call-to-action are flagged."""
        message = """
        Hi John Doe,

        I saw your GitHub profile and was impressed by your Python projects.
        We are hiring for a Senior Engineer role at our company.
        The role involves working on distributed systems and microservices.
        """ + " ".join(["More details about the company."] * 10)

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert any("call-to-action" in err.lower() for err in errors)

    def test_message_with_various_cta_keywords_passes(self, validator, sample_candidate):
        """Test that various CTA keywords are recognized."""
        cta_messages = [
            "Hi John, impressed by your work. Would love to connect!",
            "Hi John, great profile! Let's discuss this opportunity.",
            "Hi John, interested in chatting about a role?",
            "Hi John, can we schedule a call to talk more?",
            "Hi John, please reply if you're interested in learning more."
        ]

        for base_message in cta_messages:
            # Pad to meet length requirement (50+ words)
            padding = " We are building an exciting product with a talented team of engineers. " \
                     "The role involves working on distributed systems, microservices, and cloud infrastructure. " \
                     "You would have the opportunity to work with cutting-edge technology and solve interesting problems. " \
                     "Our company is growing rapidly and we are looking for talented individuals to join us."
            message = base_message + padding

            is_valid, errors = validator.validate(message, sample_candidate)
            assert is_valid is True, f"Message with CTA should pass: {base_message}"

    def test_candidate_without_name_uses_username(self, validator):
        """Test validation for candidate without display name."""
        candidate = Candidate(
            github_username="devuser",
            name=None,  # No display name
            bio="Developer",
            location=None,
            email=None,
            company=None,
            followers=50,
            following=30,
            public_repos=10,
            contribution_count=200,
            account_age_days=500,
            languages=["JavaScript"],
            top_repos=[],
            profile_url="https://github.com/devuser"
        )

        message = """
        Hi devuser,

        I noticed your JavaScript projects on GitHub and wanted to reach out
        about an exciting opportunity. We are looking for talented frontend engineers
        to join our team and work on building modern web applications. The role involves
        React, TypeScript, and cloud infrastructure. You would be working with a great
        team of engineers solving interesting technical challenges.

        Let me know if you're interested in connecting and learning more about this role!
        """

        is_valid, errors = validator.validate(message, candidate)

        assert is_valid is True
        assert len(errors) == 0

    def test_multiple_validation_errors(self, validator, sample_candidate):
        """Test that multiple errors are reported."""
        # Too short + no CTA + no candidate mention
        message = "Short message about a job."

        is_valid, errors = validator.validate(message, sample_candidate)

        assert is_valid is False
        assert len(errors) >= 2  # At least too short + no candidate mention

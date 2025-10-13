"""
Email Validator Library
Module 010: Contact Enrichment

Validates email addresses using RFC 5322 standards.
"""

from typing import Optional
from email_validator import validate_email as email_validator_validate, EmailNotValidError


class EmailValidator:
    """
    Validates email addresses using the email-validator library.

    Uses RFC 5322 standards for email validation.
    Supports:
    - Standard emails: test@gmail.com
    - Subdomains: test@mail.example.com
    - Plus addressing: test+label@gmail.com
    """

    def validate(self, email: Optional[str]) -> bool:
        """
        Validate an email address.

        Args:
            email: Email address to validate (can be None or empty)

        Returns:
            True if email is valid, False otherwise
        """
        # Defensive: Handle None and empty strings
        if not email:
            return False

        try:
            # Use email-validator library for RFC 5322 compliance
            email_validator_validate(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

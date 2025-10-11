"""Unit tests for authentication utilities."""

import pytest
from datetime import datetime, timedelta
from jose import JWTError

from src.backend_api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to different salts
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token generation and validation."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "user@example.com", "user_id": "123"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test JWT token decoding."""
        data = {"sub": "user@example.com", "user_id": "123"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded["sub"] == "user@example.com"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded

    def test_create_token_with_custom_expiration(self):
        """Test JWT token with custom expiration."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=15)

        now = datetime.utcnow()
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = decode_access_token(token)

        # Check expiration is approximately 15 minutes from now
        exp_time = datetime.utcfromtimestamp(decoded["exp"])
        expected_exp = now + expires_delta

        # Allow 2 second tolerance for test execution time
        assert abs((exp_time - expected_exp).total_seconds()) < 2

    def test_decode_invalid_token(self):
        """Test decoding invalid JWT token."""
        invalid_token = "invalid.token.here"

        with pytest.raises(JWTError):
            decode_access_token(invalid_token)

    def test_decode_expired_token(self):
        """Test decoding expired JWT token."""
        data = {"sub": "user@example.com"}
        # Create token that expired 1 hour ago
        expires_delta = timedelta(hours=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_token_contains_expiration(self):
        """Test that token contains expiration field."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

        # Verify expiration is in the future
        exp_time = datetime.fromtimestamp(decoded["exp"])
        assert exp_time > datetime.utcnow()

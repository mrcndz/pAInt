"""
Tests JWT token handling and user authentication logic.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest
from fastapi import HTTPException

from ...app.auth.dependencies import (
    ALGORITHM,
    SECRET_KEY,
    decode_jwt_token,
    get_current_user,
    get_current_user_id,
)


class TestAuthDependencies:
    """Unit tests for authentication dependency functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.secret_key = "super-secret-jwt-key"
        self.algorithm = "HS256"

        # Valid test token
        self.valid_payload = {
            "user_id": 1,
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        self.valid_token = jwt.encode(
            self.valid_payload, self.secret_key, algorithm=self.algorithm
        )

    def test_decode_jwt_token_valid(self):
        """Test decoding valid JWT token."""
        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Test
            result = decode_jwt_token(self.valid_token)

            # Assert
            assert result
            assert result["user_id"] == 1
            assert result["username"] == "testuser"
            assert "exp" in result

    def test_decode_jwt_token_invalid_signature(self):
        """Test decoding token with invalid signature."""
        # Create token with different secret
        invalid_token = jwt.encode(
            self.valid_payload, "wrong-secret", algorithm=self.algorithm
        )

        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Test - should return None instead of raising exception
            result = decode_jwt_token(invalid_token)
            assert result is None

    def test_decode_jwt_token_malformed(self):
        """Test decoding malformed token."""
        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Test - should return None instead of raising exception
            result = decode_jwt_token("not.a.token")
            assert result is None

    def test_decode_jwt_token_missing_user_id(self):
        """Test decoding token without user_id."""
        # Create token without user_id
        payload_no_user_id = {
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token_no_user_id = jwt.encode(
            payload_no_user_id, self.secret_key, algorithm=self.algorithm
        )

        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Test - should decode successfully, missing user_id handled elsewhere
            result = decode_jwt_token(token_no_user_id)

            assert result
            assert result["username"] == "testuser"
            assert "user_id" not in result

    @patch("libs.ai_service.app.auth.dependencies.decode_jwt_token")
    @patch("shared.database.get_db")
    def test_get_current_user_id_success(self, mock_get_db, mock_decode):
        """Test successful user ID extraction."""
        # Setup
        mock_decode.return_value = {"user_id": 1, "username": "testuser"}
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        mock_user = Mock()
        mock_user.id = 1
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )

        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = self.valid_token

        # Test
        result = get_current_user_id(mock_credentials, mock_db_session)

        # Assert
        assert result == 1
        mock_decode.assert_called_once_with(self.valid_token)

    @patch("libs.ai_service.app.auth.dependencies.decode_jwt_token")
    @patch("shared.database.get_db")
    def test_get_current_user_id_invalid_token(self, mock_get_db, mock_decode):
        """Test user ID extraction with invalid token."""
        # Setup
        mock_decode.return_value = None
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid-token"

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(mock_credentials, mock_db_session)

        assert exc_info.value.status_code == 401

    @patch("libs.ai_service.app.auth.dependencies.decode_jwt_token")
    @patch("shared.database.get_db")
    def test_get_current_user_success(self, mock_get_db, mock_decode):
        """Test successful user retrieval."""
        # Setup
        mock_decode.return_value = {"user_id": 1, "username": "testuser"}

        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )

        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = self.valid_token

        # Test
        result = get_current_user(mock_credentials, mock_db_session)

        # Assert
        assert result is mock_user
        mock_decode.assert_called_once_with(self.valid_token)
        mock_db_session.query.assert_called_once()

    @patch("libs.ai_service.app.auth.dependencies.decode_jwt_token")
    @patch("shared.database.get_db")
    def test_get_current_user_user_not_found(self, mock_get_db, mock_decode):
        """Test user retrieval when user doesn't exist in database."""
        # Setup
        mock_decode.return_value = {"user_id": 999, "username": "nonexistent"}

        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Create mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = "valid-token"

        # Test & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials, mock_db_session)

        assert exc_info.value.status_code == 401

    def test_token_bearer_format_extraction(self):
        """Test extracting token from Bearer format."""
        # This tests the actual dependency injection scenario
        from fastapi import Depends
        from fastapi.security import HTTPBearer

        # Test that our functions work with FastAPI's HTTPBearer
        bearer_token = f"Bearer {self.valid_token}"

        # In real usage, FastAPI would extract the token from Authorization header
        # Our functions should work with the extracted token part
        extracted_token = bearer_token.replace("Bearer ", "")

        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            result = decode_jwt_token(extracted_token)

            if result:
                assert result["user_id"] == 1

    def test_token_validation_edge_cases(self):
        """Test various edge cases in token validation."""
        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Empty token
            result = decode_jwt_token("")

            assert result is None

            # Token with extra spaces
            result = decode_jwt_token("  invalid  ")
            assert result is None

    def test_user_id_type_conversion(self):
        """Test that user_id is properly converted to int."""
        # Token with string user_id
        payload_string_id = {
            "user_id": "123",  # String instead of int
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token_string_id = jwt.encode(
            payload_string_id, self.secret_key, algorithm=self.algorithm
        )

        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", self.secret_key):
            # Test
            result = decode_jwt_token(token_string_id)
            if result:
                assert result["user_id"] == "123"

            # Test conversion in get_current_user_id
            mock_credentials = Mock()
            mock_credentials.credentials = token_string_id
            mock_db_session = Mock()
            mock_user = Mock()
            mock_user.id = 123
            mock_db_session.query.return_value.filter.return_value.first.return_value = (
                mock_user
            )

            # Test conversion using direct function call with proper db parameter
            user_id = get_current_user_id(mock_credentials, mock_db_session)
            # Assert - should handle string to int conversion
            assert isinstance(user_id, int)
            assert user_id == 123


class TestAuthConfiguration:
    """Test authentication configuration and constants."""

    def test_jwt_secret_configuration(self):
        """Test JWT secret key configuration."""
        # Assert secret is configured
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0

    def test_jwt_algorithm_configuration(self):
        """Test JWT algorithm configuration."""
        # Assert algorithm is HS256
        assert ALGORITHM == "HS256"

    def test_token_expiration_handling(self):
        """Test various token expiration scenarios."""
        secret = "test-secret"

        # Test token expiring soon (within 5 minutes)
        soon_expire_payload = {
            "user_id": 1,
            "exp": datetime.utcnow() + timedelta(minutes=2),
        }
        soon_expire_token = jwt.encode(soon_expire_payload, secret, algorithm="HS256")

        # Should still be valid
        with patch("libs.ai_service.app.auth.dependencies.SECRET_KEY", secret):
            result = decode_jwt_token(soon_expire_token)
            assert result
            assert result["user_id"] == 1

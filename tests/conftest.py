"""
Pytest configuration for integration testing.
"""

import os
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from libs.shared.database import get_db

from .test_models import TestBase


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine with in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Create all tables
    TestBase.metadata.create_all(bind=engine)

    return engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(test_db_session):
    """Test client for CRUD API with test database."""
    from unittest.mock import AsyncMock

    from libs.api.app.main import app
    from libs.shared.database import get_async_db

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    async def override_get_async_db():
        # Create a mock async session that delegates to sync session
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(
            side_effect=lambda q: test_db_session.execute(q)
        )
        mock_session.commit = AsyncMock(side_effect=lambda: test_db_session.commit())
        mock_session.refresh = AsyncMock(
            side_effect=lambda obj: test_db_session.refresh(obj)
        )
        mock_session.add = lambda obj: test_db_session.add(obj)
        mock_session.delete = lambda obj: test_db_session.delete(obj)
        yield mock_session

    # Override both sync and async database dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def ai_client(test_db_session):
    """Test client for AI service with test database."""
    from libs.ai_service.app.main import app
    from libs.shared.database import get_db

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
    }


@pytest.fixture
def test_jwt_token():
    """Generate test JWT token."""
    from datetime import datetime, timedelta

    import jwt

    payload = {
        "sub": "1",
        "username": "testuser",
        "role": "user",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, "super-secret-jwt-key", algorithm="HS256")


@pytest.fixture
def auth_headers(test_jwt_token):
    """Auth headers with JWT token."""
    return {"Authorization": f"Bearer {test_jwt_token}"}


@pytest.fixture
def auth_use_cases(test_db_session):
    """Get auth use cases with test database session."""
    from libs.api.app.auth.services import AuthUseCases

    from .test_repositories import SyncSQLAlchemyUserRepository

    # Create a sync repository for testing
    user_repository = SyncSQLAlchemyUserRepository(test_db_session)
    return AuthUseCases(
        user_repository=user_repository,
        secret_key="super-secret-jwt-key",
        algorithm="HS256",
        access_token_expire_hours=24,
    )


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Mocked AI response"))]
    )
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    mock = Mock()
    mock.search.return_value = [
        {
            "id": "test-1",
            "name": "Test Paint",
            "color": "Blue",
            "price": 50.0,
            "relevance_score": 0.9,
        }
    ]
    return mock


@pytest.fixture
def sample_paint_data():
    """Sample paint data for testing."""
    return {
        "name": "Test Paint Blue",
        "color": "Blue",
        "product_line": "Premium",
        "environment": "internal",
        "finish_type": "matte",
        "price": 89.90,
    }


@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Mock only external dependencies like OpenAI API."""
    with (
        patch("openai.OpenAI") as mock_openai,
        patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
    ):
        # Mock OpenAI client
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mocked AI response"))]
        )
        mock_client.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])]
        )
        mock_openai.return_value = mock_client

        yield

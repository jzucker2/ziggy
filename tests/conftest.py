import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def app_instance():
    """Return the FastAPI app instance."""
    return app


@pytest.fixture
def base_url():
    """Return the base URL for testing."""
    return "http://testserver"

import os

os.environ["PROTECT_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "test-url"
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["GROQ_API_KEY"] = "test-key"
os.environ["PROMETHEUS_METRICS_USERNAME"] = "test-name"
os.environ["PROMETHEUS_METRICS_PASSWORD"] = "test-pass"
os.environ["USE_MOCK_LLM"] = "test-mock"


import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.core.dependencies import get_db

@pytest.fixture(scope='function')
def mock_db():
    return MagicMock()

@pytest.fixture(scope="function")
def client(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db]=override_get_db
    with TestClient(app) as C:
        yield C
    
    app.dependency_overrides.clear()
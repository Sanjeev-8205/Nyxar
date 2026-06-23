import os

os.environ["TESTING"] = "true"
os.environ["PROTECT_API_KEY"] = "test-key"

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as C:
        yield C
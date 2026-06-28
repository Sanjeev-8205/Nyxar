import os
import base64
import io

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

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
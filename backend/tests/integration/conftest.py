import io, base64, os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

os.environ["TESTING"] = "true"
if not os.getenv("GITHUB_ACTIONS"):
    load_dotenv(Path(__file__).resolve().parents[2] / ".env.test", override=True)

from app.main import app
from models.batch_job_model import BatchJob
from app.core.database import Base, init_db
from app.core.dependencies import get_db
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()
    from app.core.database import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db():
    from app.core.database import engine
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def batch_job(db):
    job = BatchJob(
        filename="test.csv",
        status="completed",
        model_name="RoBERTa Transformer",
        total_rows=10,
        processed_rows=10,
        progress=100,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def auth_headers():
    return {"X-API-key": "test-key"}


@pytest.fixture
def invalid_auth_headers():
    return {"X-API-key": "wrong-key"}


@pytest.fixture
def missing_auth_headers():
    return {"X-API-key": ""}


@pytest.fixture
def prometheus_env(monkeypatch):
    monkeypatch.setenv("PROMETHEUS_METRICS_USERNAME", "test-name")
    monkeypatch.setenv("PROMETHEUS_METRICS_PASSWORD", "test-pass")


@pytest.fixture
def prometheus_headers():
    credentials = base64.b64encode(b"test-name:test-pass").decode()
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture
def prediction_payload():
    def _payload(text, model):
        return {"text": text, "model": model}
    return _payload


@pytest.fixture
def sample_csv():
    csv = io.BytesIO(b"text\nI love this product\nSuch a bad product")
    csv.name = "reviews.csv"
    return csv


@pytest.fixture
def empty_csv():
    csv = io.BytesIO(b"")
    csv.name = "empty.csv"
    return csv


@pytest.fixture
def wrong_file():
    file_ = io.BytesIO(b"hello")
    file_.name = "hello.txt"
    return file_


@pytest.fixture
def missing_text_column():
    csv = io.BytesIO(b"name\nJohn\nWinston")
    csv.name = "missing_text_column.csv"
    return csv


@pytest.fixture
def models():
    return ["Logistic Regression", "Bi-LSTM", "RoBERTa Transformer"]
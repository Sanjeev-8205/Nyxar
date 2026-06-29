# Deployment

## Deployment Topology

| Service | Platform | Runtime |
|---|---|---|
| FastAPI backend | Hugging Face Spaces (Docker SDK) | Python 3.11, CPU-only |
| Streamlit frontend | Streamlit Cloud | Python 3.12 |
| PostgreSQL database | Neon (serverless Postgres) | us-east-1 |
| ML models | Hugging Face Hub | Downloaded at container startup |

The two application services are fully independent. The frontend communicates with the backend exclusively via HTTP. Neither service shares a filesystem or process space with the other.

---

## Hugging Face Spaces Architecture

The backend runs as a Docker container on Hugging Face Spaces. The `Dockerfile` defines the full build:

```
Base image:     python:3.11-slim
PyTorch:        CPU-only wheel (torch==2.10.0+cpu)
Port:           7860 (HF Spaces standard)
Entrypoint:     uvicorn app.main:app --host 0.0.0.0 --port 7860
```

PyTorch CPU is installed first as a separate `RUN` layer to maximize Docker layer caching. The remaining dependencies follow in a second layer.

**Cold start behavior:** On container startup, the lifespan handler runs `setup_logging()` first, then `preload_models()` and `warmup()` before the server begins accepting requests. This means all three ML models are downloaded from HuggingFace Hub, loaded into memory, and warmed up before the first request is served. Cold start time is dominated by the model download step.

The `TRANSFORMERS_CACHE` environment variable is set to `/app/cache` to ensure transformer-related downloads land inside the container rather than a default home directory path.

---

## CI/CD Pipeline

Deploys are managed via GitHub Actions. The workflow is defined in `.github/workflows/backend_deploy.yml`.

**Trigger conditions:**

| Trigger | Behaviour |
|---|---|
| Push to `main` (any path) | Runs test job only — no deploy |
| Push of `v*` tag | Runs test job, then deploy job if tests pass |
| `workflow_dispatch` (manual button) | Runs test job, then deploy job if tests pass |

**Deploying a new version:**
```bash
git tag v1.1.0
git push origin v1.1.0
```

This triggers the full pipeline. The test job must pass before the deploy job runs. A failing test blocks the deploy entirely.

**Manual redeploy (without a code change):**
Use the workflow_dispatch button in GitHub Actions → Actions tab → Deploy Backend to HF Spaces → Run workflow. This is useful when an environment variable has been updated on HF Spaces and you want to resync without a code change.

**Pipeline stages:**

```
test job:
  ├── Checkout monorepo
  ├── Set up Python 3.11
  ├── Install requirements-ci.txt + requirements-test.txt
  └── pytest tests/ -v  (TESTING=true, PROTECT_API_KEY=test-key, TEST_DATABASE_URL=<test-db>)

deploy job (needs: test):
  ├── Checkout monorepo
  ├── Clone HF Spaces repo
  ├── rsync backend/ → hf-space/ (excludes .git)
  ├── Commit with message from github.sha
  └── Push to HF Spaces
```

`tests/unit/` runs against mocked models with no database. `tests/integration/` exercises real request/response flows — auth, validation, error paths, response contracts, Prometheus auth — against a dedicated test database (`TEST_DATABASE_URL`), kept separate from the production Neon instance the deployed backend uses. Both layers run in the same CI step; a failure in either blocks the deploy job.

**Commit message on HF Spaces:** The deploy commit message is derived from the GitHub commit that triggered the workflow using `git log -1 --pretty=%s ${{ github.sha }}`. This works correctly for tag pushes, branch pushes, and manual dispatch — unlike `github.event.head_commit.message` which is unpopulated for tag-triggered workflows.

**CI dependency split:** `requirements-ci.txt` strips all heavy ML packages (PyTorch, TensorFlow, ONNX Runtime). Tests mock model inference via `dependency_overrides` and `MagicMock`, so the full ML stack is not required in CI. This prevents disk exhaustion on the GitHub Actions runner.

---

## Model Storage

Models are not bundled in the Docker image. They are stored as separate repositories on HuggingFace Hub and downloaded at startup via `snapshot_download`.

| Model Key | HuggingFace Repo |
|---|---|
| `logistic` | `Sanjeev2501/nyxar-logistic-sentiment` |
| `bilstm` | `Sanjeev2501/nyxar-bilstm-sentiment` |
| `roberta` | `Sanjeev2501/nyxar-roberta-sentiment` |

Each repo contains the model artifacts and any required tokenizer or vectorizer files. `snapshot_download` pulls the full repo contents to a local path, which is then used by the loader functions.

**Why separate repos rather than bundling in the image:** Docker images on HF Spaces are rebuilt on each push. Bundling large model files in the image would make every rebuild slow and storage-intensive. Keeping models on Hub repos decouples model updates from application code changes.

---

## Environment Variables

| Variable | Used By | Purpose |
|---|---|---|
| `DATABASE_URL` | `app/core/database.py` | PostgreSQL connection string |
| `GEMINI_API_KEY` | LLM services | Gemini API authentication |
| `GROQ_API_KEY` | LLM services | Groq API authentication |
| `PROMETHEUS_METRICS_USERNAME` | `prometheus_metrics_routes.py` | Metrics endpoint Basic Auth |
| `PROMETHEUS_METRICS_PASSWORD` | `prometheus_metrics_routes.py` | Metrics endpoint Basic Auth |
| `PROTECT_API_KEY` | `app/core/security.py` | API key for all non-health endpoints |
| `TEST_DATABASE_URL` | `tests/integration/conftest.py` | Dedicated test database connection string, used only by integration tests — kept separate from the production Neon database |

All variables are managed as HF Spaces Secrets and never committed to the repository. The `PROTECT_API_KEY` is stored in plaintext in HF Spaces Secrets; comparison in the application uses `secrets.compare_digest` to prevent timing attacks.

For the Streamlit frontend, `NYXAR_API_KEY` is stored in Streamlit Cloud Secrets and injected as the `X-Api-Key` header on every backend request.

---

## Persistent Storage

The only persistent state is the PostgreSQL database. Five tables are created at startup via `Base.metadata.create_all(bind=engine)` if they do not already exist.

Uploaded CSV files are written to `/app/upload/` within the container. This directory is not persistent across container restarts — it is a transient working directory for batch jobs in flight. Results are persisted to PostgreSQL before the job is marked complete.

Application logs are written to stdout. HF Spaces captures stdout and makes it available in the Space logs panel. Logs are structured JSON (via `structlog`) and are not persisted beyond the container's lifetime.

---

## Database Configuration

Neon Postgres (us-east-1) is used as the database. The SQLAlchemy engine is configured with:

```python
pool_pre_ping=True   # Validate connections before use
pool_recycle=300     # Recycle connections every 5 minutes
```

`pool_pre_ping` prevents stale connection errors from Neon's connection pooling behavior. `pool_recycle` prevents connections from being held longer than Neon's idle timeout.

The database region (us-east-1) was chosen to minimize latency from the HF Spaces backend, which also runs in us-east-1. A database in a different region would add round-trip time to every batch job's buffered writes.

---

## Security

- All API endpoints except `/health` require a valid `X-Api-Key` header. Verification uses `secrets.compare_digest` for constant-time comparison.
- The Prometheus metrics endpoint is additionally protected with HTTP Basic Auth.
- Environment variables containing credentials are managed as HF Spaces Secrets and Streamlit Cloud Secrets — never committed to the repository.
- The `.gitignore` explicitly excludes `.env`, model directories, log directories, and cache directories.
- Uploaded CSV files are written with UUID-prefixed filenames to prevent filename collisions and predictable paths.
- Failed authentication attempts are logged at `warning` level with structlog, making brute-force attempts visible in HF Spaces logs.
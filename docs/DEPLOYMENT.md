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
spaCy model:    en_core_web_sm (downloaded during build)
Port:           7860 (HF Spaces standard)
Entrypoint:     uvicorn app.main:app --host 0.0.0.0 --port 7860
```

PyTorch CPU is installed first as a separate `RUN` layer to maximize Docker layer caching. The remaining dependencies follow in a second layer.

**Cold start behavior:** On container startup, the lifespan handler runs `preload_models()` and `warmup()` synchronously before the server begins accepting requests. This means all three ML models are downloaded from HuggingFace Hub, loaded into memory, and warmed up before the first request is served. Cold start time is dominated by the model download step.

The `TRANSFORMERS_CACHE` environment variable is set to `/app/cache` to ensure transformer-related downloads land inside the container rather than a default home directory path.

---

## Model Storage

Models are not bundled in the Docker image. They are stored as separate repositories on HuggingFace Hub and downloaded at startup via `snapshot_download`.

| Model Key | HuggingFace Repo |
|---|---|
| `logistic` | `Sanjeev2501/nyxar-logistic-sentiment` |
| `bilstm` | `Sanjeev2501/nyxar-bilstm-sentiment` |
| `roberta` | `Sanjeev2501/nyxar-roberta-sentiment` |

Each repo contains the model artifacts and any required tokenizer or vectorizer files. `snapshot_download` pulls the full repo contents to a local path, which is then used by the loader functions.

**Why separate repos rather than bundling in the image:**
Docker images on HF Spaces are rebuilt on each push. Bundling large model files in the image would make every rebuild slow and storage-intensive. Keeping models on Hub repos decouples model updates from application code changes.

---

## Environment Variables

| Variable | Used By | Purpose |
|---|---|---|
| `DATABASE_URL` | `app/core/database.py` | PostgreSQL connection string |
| `GEMINI_API_KEY` | LLM services | Gemini API authentication |
| `GROQ_API_KEY` | LLM services | Groq API authentication |
| `PROMETHEUS_METRICS_USERNAME` | `prometheus_metrics_routes.py` | Metrics endpoint auth |
| `PROMETHEUS_METRICS_PASSWORD` | `prometheus_metrics_routes.py` | Metrics endpoint auth |

---

## Persistent Storage

The only persistent state is the PostgreSQL database. Five tables are created at startup via `Base.metadata.create_all(bind=engine)` if they do not already exist.

Uploaded CSV files are written to `/app/upload/` within the container. This directory is not persistent across container restarts — it is a transient working directory for batch jobs in flight. Results are persisted to PostgreSQL before the job is marked complete.

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

## Security Considerations

- The Prometheus metrics endpoint is the only authenticated endpoint. All other API endpoints are publicly accessible.
- Environment variables containing credentials are managed as HF Spaces Secrets and never committed to the repository.
- The `.gitignore` explicitly excludes `.env`, model directories, log directories, and cache directories.
- Uploaded CSV files are written with UUID-prefixed filenames to prevent filename collisions and predictable paths.

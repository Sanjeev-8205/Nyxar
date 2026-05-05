FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install PyTorch CPU
RUN pip install --prefer-binary --timeout=1000 --retries=10 \
    torch==2.10.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --prefer-binary --timeout=1000 --retries=10 \
    -r requirements.txt

# Download spacy model
RUN python -m spacy download en_core_web_sm

# Copy full project
COPY . .

# Cache dir for transformers
ENV TRANSFORMERS_CACHE=/app/cache

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
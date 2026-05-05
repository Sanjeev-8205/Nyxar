FROM python:3.12.12

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir \
    --index-url https://pypi.org/simple \
    streamlit requests pandas matplotlib

CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
import os

os.environ["TESTING"] = "true"
os.environ["PROTECT_API_KEY"] = "test-key"
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["GROQ_API_KEY"] = "test-key"
os.environ["PROMETHEUS_METRICS_USERNAME"] = "test-name"
os.environ["PROMETHEUS_METRICS_PASSWORD"] = "test-pass"
os.environ["USE_MOCK_LLM"] = "true"
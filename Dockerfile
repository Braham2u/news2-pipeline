# Pinned slim base image for a small, reproducible runtime environment.
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies first so this layer is cached when only
# application code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Container-level health check used by the deployment environment.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; \
    sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status == 200 else sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

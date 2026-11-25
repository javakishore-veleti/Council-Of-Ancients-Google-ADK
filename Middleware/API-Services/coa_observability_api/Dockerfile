# Slim image for coa_observability_api (no google-adk).
# Build from repo root:
#   docker build -f Middleware/API-Services/coa_observability_api/Dockerfile -t council-coa-observability-api .

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Middleware/API-Services \
    PORT=8088

RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "prometheus-client>=0.21.0" \
    "opentelemetry-api>=1.28.0" \
    "opentelemetry-sdk>=1.28.0" \
    "opentelemetry-exporter-otlp-proto-grpc>=1.28.0"

COPY Middleware/API-Services/coa_observability_api /app/Middleware/API-Services/coa_observability_api

EXPOSE 8088 9108

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=10 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/healthz', timeout=2)"

CMD ["uvicorn", "coa_observability_api.presentation.app:app", "--host", "0.0.0.0", "--port", "8088"]

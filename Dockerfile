FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/audit data/state

ENV PYTHONPATH=/app
ENV MARKET_DATA_PROVIDER=stub
ENV AUDIT_LOG_PATH=/app/data/audit/audit.jsonl
ENV STATE_PATH=/app/data/state
ENV APPROVAL_SECRET=changeme

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "apps.fincept_aiops.app:app", "--host", "0.0.0.0", "--port", "8000"]

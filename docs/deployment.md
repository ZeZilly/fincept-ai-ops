# Deployment

## Local
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn apps.fincept_aiops.app:app --reload --port 8000
```

## Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "apps.fincept_aiops.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Vercel
See `vercel.json` in root.

## Environment Variables
```
MARKET_DATA_PROVIDER=stub
AUDIT_LOG_PATH=./data/audit/audit.jsonl
STATE_PATH=./data/state
APPROVAL_SECRET=changeme
DEBUG=true
LIVE_TRADING=false
```

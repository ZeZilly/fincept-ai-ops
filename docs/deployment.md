# Deployment Guide

## Local Development

```bash
git clone https://github.com/ZeZilly/fincept-ai-ops
cd fincept-ai-ops
cp .env.example .env
pip install -r requirements.txt
uvicorn apps.fincept_aiops.app:app --reload --port 8000
```

Open: http://localhost:8000/docs

## Docker

```bash
docker build -t fincept-ai-ops .
docker run -p 8000:8000 --env-file .env fincept-ai-ops
```

## Docker Compose (API + MCP)

```bash
cp .env.example .env
# Edit .env — set APPROVAL_SECRET and CORS_ORIGINS
docker-compose up -d
```

## Vercel

1. Push to `main` branch
2. vercel.com/new → Import `ZeZilly/fincept-ai-ops`
3. Set env vars: `APPROVAL_SECRET`, `CORS_ORIGINS`, `MARKET_DATA_PROVIDER`
4. Deploy

## Environment Variables (Required in Production)

| Variable | Default | Description |
|---|---|---|
| `APPROVAL_SECRET` | `changeme` | **CHANGE THIS** — webhook auth |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `MARKET_DATA_PROVIDER` | `stub` | `stub` or `yfinance` |
| `RISK_MAX_SIZE_PCT` | `0.10` | Max position size (10%) |
| `RISK_MAX_DAILY_LOSS_PCT` | `0.05` | Daily loss stop (5%) |
| `RATE_LIMIT_PER_MIN` | `60` | Rate limit per IP |

## MCP Server (Claude Integration)

Add to Claude Desktop `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fincept-ai-ops": {
      "command": "python",
      "args": ["/path/to/fincept-ai-ops/mcp/server.py"],
      "env": {
        "MARKET_DATA_PROVIDER": "yfinance",
        "STATE_PATH": "/path/to/data/state"
      }
    }
  }
}
```

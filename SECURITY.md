# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x (mvp) | ✅ Active |

## Reporting a Vulnerability

Do **not** open a public GitHub issue for security vulnerabilities.

Please report security issues directly to the maintainer:
- **LinkedIn**: [Zeki Oguz](https://no.linkedin.com/in/zekiogz)

Expect a response within 72 hours. Critical vulnerabilities will be patched within 7 days.

## Security Principles

This project is built with the following security guarantees:

- All secrets and API keys are loaded via **environment variables only** — never hardcoded
- No broker action is taken without an **audit log entry**
- No trade execution is allowed without **human approval** (webhook gate)
- All API endpoints require **API key authentication**
- Risk limits are **env-configurable hard limits** — not code constants
- Rate limiting and request size limits enforced at middleware level

## Known Limitations

- Git history contains removed sensitive documents (pre-v1.0.0). These have been deleted from the working tree but remain in git history. A `git filter-repo` cleanup is planned for v1.1.0.

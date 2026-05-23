# Contributing to fincept-ai-ops

Thank you for your interest in contributing.

## Principles

This project prioritizes:
1. **Safety over speed** — no change should reduce human oversight
2. **Auditability** — every agent action must remain traceable
3. **Simplicity** — fewer agents with clear roles over many agents with overlapping scope

## Getting Started

```bash
git clone https://github.com/ZeZilly/fincept-ai-ops
cd fincept-ai-ops
pip install -r requirements.txt
cp .env.example .env  # fill in your values
python -m pytest tests/
```

## Branch Strategy

- `main` — production-ready code only
- `feature/*` — new features
- `fix/*` — bug fixes
- `docs/*` — documentation only changes

All changes to `main` must go through a Pull Request. Direct push to `main` is not allowed.

## Pull Request Checklist

- [ ] Tests pass (`pytest tests/`)
- [ ] No secrets or API keys in code
- [ ] Audit log entries added for any new agent action
- [ ] CHANGELOG.md updated
- [ ] Human approval gate preserved for any execution path

## Code Style

- Python: PEP 8, type hints preferred
- Max function length: 50 lines
- All agent methods must have docstrings

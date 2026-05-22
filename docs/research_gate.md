# Research Gate

## Pipeline Steps
1. Validate contract
2. Enrich input
3. Generate signal candidate
4. Score and rank
5. Evaluate risk
6. Persist state
7. Emit briefing packet

## Rejection Rules
- Required field missing
- confidence < 0.70
- sources_checked < 2
- Schema validation error
- Unsupported asset or timeframe
- Unresolved contradictory source cluster

## Required Artifacts
- latest_signal_candidate.json
- latest_risk.json
- latest_briefing.json

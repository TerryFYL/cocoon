---
name: cocoon-retrieval-trigger
description: "Spaced-repetition retrieval practice trigger injected at Cocoon session start"
metadata:
  openclaw:
    emoji: "🔁"
    events: ["agent:bootstrap"]
    requires:
      bins: ["python3"]
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Retrieval Trigger Hook

Injects spaced-repetition retrieval practice prompts at the start of Cocoon sessions.

## Algorithm

Modified SM-2 spaced repetition:
- Initial interval: 24h
- Multiplier: 2.2x per successful recall
- Ease factor: starts at 2.5, adjusts per result
- Max interval: 30 days

## Stage Gating

- Stage 1 (< 5 sessions): not triggered
- Stage 2+: up to 1 retrieval practice per session

## Data Files

- `~/.openclaw/cocoon/retrieval_schedule.json` — SM-2 item schedule

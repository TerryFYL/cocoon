---
name: cocoon-mindset-monitor
description: "Detects mindset regression signals and adjusts scaffold during Cocoon sessions"
metadata:
  openclaw:
    emoji: "🫀"
    events: ["message:received"]
    requires:
      bins: ["python3"]
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Mindset Monitor Hook

Detects mindset regression signals during Cocoon sessions and logs scaffold adjustment guidance.

## Regression Levels

- **Level 0**: Normal
- **Level 1** (mild): Over-confirmation, decision avoidance → scaffold +0.10
- **Level 2** (moderate): Persistent avoidance, ability denial → scaffold +0.20
- **Level 3** (severe): Learned helplessness, identity denial → scaffold +0.35, safety rebuild

## Data Files

- `~/.openclaw/cocoon/mindset_log.jsonl` — regression signal log

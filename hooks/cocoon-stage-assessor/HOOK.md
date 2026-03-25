---
name: cocoon-stage-assessor
description: "Updates scaffold level and evaluates stage transitions on Cocoon session start"
metadata:
  openclaw:
    emoji: "📊"
    events: ["agent:bootstrap"]
    requires:
      bins: ["python3"]
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Stage Assessor Hook

Updates the user's scaffold level and evaluates stage transitions at the start of each Cocoon session.

## Scaffold Formula

`scaffold(t) = S_min + (S_max - S_min) × e^(-λ × t)`

where `t` = accumulated session count within current stage.

## Five Stages

1. 敬畏者 — S_max=0.80, S_min=0.30, λ=0.15
2. 工具使用者 — S_max=0.70, S_min=0.20, λ=0.20
3. 协作者 — S_max=0.50, S_min=0.10, λ=0.25
4. 编排者 — S_max=0.30, S_min=0.05, λ=0.30
5. 思想者 — S_max=0.15, S_min=0.00, λ=0.35

## Data Files

- `~/.openclaw/cocoon/user_state.json` — scaffold, stage, subskills
- `~/.openclaw/cocoon/assessment_history.jsonl` — per-session log

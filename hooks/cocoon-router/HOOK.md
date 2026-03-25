---
name: cocoon-router
description: "Session tracker and intent signal router for Cocoon learning system"
metadata:
  openclaw:
    emoji: "🧭"
    events: ["agent:bootstrap", "message:received"]
    requires:
      bins: []
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Router Hook

Tracks active Cocoon sessions and detects intent signals to route between agents (搭档/同行者/镜子).

## Routing Signals

- `task` → 搭档 (cocoon-partner): execution-oriented messages
- `reflect` → 同行者 (cocoon-companion): reflective/emotional messages
- `progress` → 镜子 (cocoon-mirror): self-observation messages
- `ambiguous` → stays with current agent

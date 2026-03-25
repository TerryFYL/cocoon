---
name: cocoon-router
description: "Session tracker for Cocoon learning system"
metadata:
  openclaw:
    emoji: "🧭"
    events: ["agent:bootstrap", "message:received"]
    requires:
      bins: []
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Router Hook

Tracks active Cocoon sessions. Intent routing is handled by each Agent's LLM (SOUL.md 边界与切换 section) — no longer done via regex in the hook.

## Session Tracking

- `agent:bootstrap` → records active agent to `active_agent.json`
- Other hooks (`mindset-monitor`, etc.) use this to determine if they're in a Cocoon session
- Session TTL: 1 hour

## 意图路由

已移至 LLM 层。各 Agent 根据 SOUL.md 中的"边界与切换"规则自行判断消息是否属于自己，如果不是则建议用户切换到合适的 Agent。

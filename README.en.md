# 🦋 Cocoon

**Don't teach AI. Grow through it.**

> From Awe to Mastery — 5 stages, 3 companions, 1 metamorphosis.

[中文](README.md) | English

---

## What Is This

Cocoon is an AI learning system that runs on [OpenClaw](https://openclaw.ai).

It's not a course. Not a tutorial. Not a prompt template library. It's three AI personas — **Partner, Companion, Mirror** — that walk with you through real tasks as you transform from "I don't know how to use AI" to "I use AI to redefine problems."

## Why

The biggest problem with learning AI isn't prompt engineering. It's:

- Fear of trying, fear of failing
- Growing dependent — feeling useless without AI
- Learning tricks without changing how you think
- Nobody telling you "you've changed"

Cocoon solves these. Not by teaching. By **doing things together**.

## Three Personas

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  🔬 Partner  │     │ 🌿 Companion │     │  🪞 Mirror   │
│              │     │              │     │              │
│ "Let's do it"│     │"What are you │     │ "You've      │
│              │     │  thinking?"  │     │  changed"    │
│              │     │              │     │              │
│ Shows up for │     │ Shows up when│     │ Shows up     │
│   tasks      │     │  you reflect │     │  rarely      │
│              │     │              │     │              │
│ → Competence │     │ → Autonomy   │     │ → Relatedness│
└─────────────┘     └─────────────┘     └─────────────┘
                         ↑
              Self-Determination Theory (SDT)
             Competence × Autonomy × Relatedness
```

**Partner**: Your senior colleague. Takes tasks, executes, leaves key decisions to you. Doesn't teach — works alongside you.

**Companion**: A friend on a walk. No answers, just questions. One at a time. Helps you find your own clarity.

**Mirror**: An anthropologist's field notes. No judgment, only observations. Shows up rarely, but precisely.

## Five Stages

```
Stage 1        Stage 2          Stage 3        Stage 4        Stage 5
  Awe     →   Tool User    →  Collaborator → Orchestrator →  Thinker

scaffold 0.80  scaffold 0.70   scaffold 0.50  scaffold 0.30  scaffold 0.15
AI does 80%    AI does 60%     50/50          You do 80%     You lead
```

The scaffold decays automatically. As you grow stronger, AI steps back. Not a preset curriculum — dynamically adjusted based on your actual behavior.

## Core Mechanisms

| Mechanism | What | How |
|-----------|------|-----|
| **Intent Router** | Auto-detects message type | Chinese regex → routes to Partner/Companion/Mirror |
| **Scaffold Decay** | AI involvement decreases as you grow | Exponential decay `s_min + (s_max - s_min) × e^(-λt)` |
| **Aha Detector** | Captures your eureka moments | 18 cognitive leap patterns + confidence scoring |
| **Mindset Monitor** | Detects frustration & learned helplessness | 3-level alert + auto scaffold increase |
| **Spaced Retrieval** | Reinforces learned skills | Modified SM-2, weakest skills first |
| **Stage Assessor** | Evaluates readiness for next stage | Multi-signal (sessions + subskills + behavioral signals) |

## Quick Start

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed
- Python 3.8+

### Install

```bash
git clone https://github.com/anthropics/cocoon.git
cd cocoon
bash scripts/install.sh
```

### Use

Switch to the `cocoon-partner` agent in OpenClaw, then just say what you want to do:

```
You: Help me write a data cleaning script
Partner: What format is the data source? Give me a sample file to see the structure.
```

No learning curve. **Just start doing things.** The system adapts to your behavior automatically.

### Reset

```bash
bash scripts/cleanup.sh
```

## Design Philosophy

1. **Do, don't study.** No syllabus, no exercises. Bring real tasks, we work together.
2. **Accompany, don't teach.** None of the three personas is a teacher.
3. **Dynamic, not fixed.** Scaffold auto-decays, personas auto-switch, stages auto-transition.
4. **Safe, not judgmental.** When you struggle, the system silently takes over more work. No "you can do it!" — just action.
5. **See, don't praise.** Mirror only describes change. "Three weeks ago you asked at every step. This time you wrote the whole flow."

## Theoretical Foundation

- **Self-Determination Theory (SDT)** — Deci & Ryan
- **Zone of Proximal Development (ZPD)** — Vygotsky
- **Constructionism** — Papert
- **Spaced Repetition** — Ebbinghaus → SM-2
- **Flow** — Csikszentmihalyi
- **Deliberate Practice** — Ericsson

## Contributing

PRs welcome! Especially:

- Intent routing regex for new languages (currently Chinese only)
- New aha-moment detection patterns
- New spaced retrieval practice templates
- Adapters for non-OpenClaw platforms

## License

MIT

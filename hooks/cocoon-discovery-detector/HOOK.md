---
name: cocoon-discovery-detector
description: "Detects aha moments and cognitive leaps during Cocoon sessions"
metadata:
  openclaw:
    emoji: "💡"
    events: ["message:received"]
    requires:
      bins: ["python3"]
    install: [{ "id": "local", "kind": "local", "label": "Local hook" }]
---

# Cocoon Discovery Detector Hook

Detects "aha moments" — sudden understanding, cognitive leaps, and realization signals during Cocoon sessions.

## Discovery Types

- `realization` — sudden understanding ("原来如此", "我突然明白")
- `connection` — linking two concepts ("这跟...一样")
- `paradigm_shift` — reversing prior understanding ("我以前以为...其实")
- `generalization` — self-extracted patterns ("我发现...规律")
- `boundary_insight` — human-AI capability awareness
- `metacognition` — awareness of one's own thinking patterns

## Data Files

- `~/.openclaw/cocoon/discoveries/discovery_log.jsonl` — discovery records

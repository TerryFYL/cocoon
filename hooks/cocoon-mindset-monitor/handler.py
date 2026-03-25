"""
Mindset Monitor Hook
====================
事件: message:received
功能: 检测用户心态回退信号（习得性无助、决策回避等）
"""

import json
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

DATA_DIR = Path.home() / ".openclaw" / "cocoon"
STATE_FILE = DATA_DIR / "user_state.json"
MINDSET_LOG = DATA_DIR / "mindset_log.jsonl"

REGRESSION_PATTERNS = {
    "mild": [
        (r"(?:这样)?(?:对吗|可以吗|行吗|是不是|对不对)[?？]", "over_confirmation", 0.4),
        (r"(?:你(?:来)?(?:决定|选择|定)(?:吧)?|你觉得(?:哪个|怎样)(?:好|比较好))", "decision_avoidance", 0.5),
        (r"我(?:是不是|可能)(?:不太|不够)(?:会|懂|理解|明白)", "mild_self_doubt", 0.4),
        (r"(?:还是)?(?:你|AI)(?:直接|帮我)(?:做|写|决定)(?:吧|就好)", "over_reliance", 0.5),
    ],
    "moderate": [
        (r"我(?:不想|不敢|害怕|担心)(?:自己)?(?:做|试|选|决定)", "avoidance", 0.7),
        (r"我(?:做|搞|弄)不(?:好|了|来|到)", "ability_denial", 0.7),
        (r"(?:还是|算了).+?(?:你来|你做|你帮我|你直接)", "regression", 0.6),
        (r"(?:越来越|完全)(?:不知道|搞不懂|迷糊|混乱)", "anxiety", 0.7),
        (r"(?:别人|其他人|人家)(?:都|很快|很容易)(?:会|能|懂)", "comparison_self_deprecation", 0.8),
    ],
    "severe": [
        (r"(?:我(?:就是|永远|根本))(?:不行|学不会|做不到|不适合)", "learned_helplessness", 0.9),
        (r"(?:算了|放弃|不学了|不干了|太难了)", "giving_up", 0.8),
        (r"我(?:不是|不配|不适合)(?:做|学|用)(?:这|AI|编程)", "identity_denial", 0.9),
        (r"(?:烦死了|受不了|崩溃|想哭|太痛苦)", "emotional_collapse", 0.8),
    ],
}

SESSION_WINDOW = 1800
MILD_THRESHOLD = 2
MODERATE_THRESHOLD = 2
SEVERE_THRESHOLD = 1

@dataclass
class MindsetSignal:
    timestamp: str
    level: str
    pattern_name: str
    confidence: float
    trigger_text: str
    user_stage: int

@dataclass
class MindsetState:
    current_level: int = 0
    signals_in_window: list = field(default_factory=list)
    total_mild: int = 0
    total_moderate: int = 0
    total_severe: int = 0
    last_alert_time: str = ""
    consecutive_sessions_with_regression: int = 0
    def to_dict(self):
        return asdict(self)

def load_user_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"current_stage": 1, "scaffold_level": 0.80}

def load_mindset_state():
    state = MindsetState()
    if not MINDSET_LOG.exists():
        return state
    now = datetime.now()
    window_start = now - timedelta(seconds=SESSION_WINDOW)
    with open(MINDSET_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                ts = datetime.fromisoformat(record.get("timestamp", ""))
                if ts >= window_start:
                    state.signals_in_window.append(record)
                level = record.get("level", "")
                if level == "mild": state.total_mild += 1
                elif level == "moderate": state.total_moderate += 1
                elif level == "severe": state.total_severe += 1
            except (json.JSONDecodeError, ValueError):
                continue
    return state

def save_signal(signal):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(MINDSET_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(signal), ensure_ascii=False) + "\n")

def detect_regression_signals(message, user_stage):
    signals = []
    now = datetime.now().isoformat()
    for level_name, patterns in REGRESSION_PATTERNS.items():
        for pattern, pattern_name, base_confidence in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if not match:
                continue
            confidence = base_confidence
            if user_stage >= 3 and level_name in ("mild", "moderate"):
                confidence = min(1.0, confidence + 0.1)
            elif user_stage >= 4 and level_name == "mild":
                confidence = min(1.0, confidence + 0.15)
            if re.search(r"(?:不是说|并不是|我不觉得|不是真的|开玩笑)", message):
                confidence *= 0.3
            if re.search(r"(?:他说|她说|有人说|文章里)", message[:30]):
                confidence *= 0.2
            if confidence >= 0.35:
                signals.append(MindsetSignal(timestamp=now, level=level_name, pattern_name=pattern_name, confidence=round(confidence, 3), trigger_text=message[:200], user_stage=user_stage))
    return signals

def assess_regression_level(state, new_signals):
    window_signals = state.signals_in_window + [asdict(s) for s in new_signals]
    mild_count = sum(1 for s in window_signals if s.get("level") == "mild")
    moderate_count = sum(1 for s in window_signals if s.get("level") == "moderate")
    severe_count = sum(1 for s in window_signals if s.get("level") == "severe")
    if severe_count >= SEVERE_THRESHOLD: return 3
    if moderate_count >= MODERATE_THRESHOLD: return 2
    if mild_count >= MILD_THRESHOLD: return 1
    for signal in new_signals:
        if signal.level == "severe" and signal.confidence >= 0.75: return 3
    return 0

def generate_response_guidance(level, user_stage, signals):
    if level == 0:
        return {"adjust": False}
    primary_pattern = signals[0].pattern_name if signals else "unknown"
    guidance = {"adjust": True, "regression_level": level, "primary_signal": primary_pattern}
    if level == 1:
        guidance.update({"scaffold_adjustment": 0.10, "agent_behavior": ["适当增加执行比例", "决策点给更明确的选项", "不提及用户的犹豫或不确定"], "forbidden_responses": ["你是不是不太确定", "没关系，慢慢来", "你可以的"]})
    elif level == 2:
        guidance.update({"scaffold_adjustment": 0.20, "agent_behavior": ["显著增加执行比例，接管更多工作", "把复杂决策拆成更小的选择", "用快速的小成功重建节奏", "不讨论情绪或状态"], "forbidden_responses": ["要不要换个简单的", "你好像有点累", "这个确实很难"], "recovery_strategy": "small_wins"})
    elif level == 3:
        guidance.update({"scaffold_adjustment": 0.35, "agent_behavior": ["几乎完全接管执行", "只留非常简单的确认型决策（是/否）", "快速产出可见的结果", "绝对不讨论用户的情绪状态", "绝对不评价用户的能力", "只做事，让结果说话"], "forbidden_responses": ["你很棒", "加油", "别担心", "没关系", "慢慢来", "你已经做得很好了"], "recovery_strategy": "safety_rebuild", "escalation_note": "如果 Level 3 持续超过2个session，考虑是否需要人工介入"})
    return guidance

def on_message_received(event):
    message = event.get("message", "")
    if not message or len(message.strip()) < 2:
        return {"regression_detected": False, "regression_level": 0, "signals": [], "guidance": {"adjust": False}, "scaffold_adjustment": 0.0}
    user_state = load_user_state()
    user_stage = user_state.get("current_stage", 1)
    new_signals = detect_regression_signals(message, user_stage)
    if not new_signals:
        return {"regression_detected": False, "regression_level": 0, "signals": [], "guidance": {"adjust": False}, "scaffold_adjustment": 0.0}
    for signal in new_signals:
        save_signal(signal)
    mindset_state = load_mindset_state()
    level = assess_regression_level(mindset_state, new_signals)
    guidance = generate_response_guidance(level, user_stage, new_signals)
    return {"regression_detected": level > 0, "regression_level": level, "signals": [asdict(s) for s in new_signals], "guidance": guidance, "scaffold_adjustment": guidance.get("scaffold_adjustment", 0.0)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=str, required=True, help="JSON event string")
    args = parser.parse_args()
    try:
        event = json.loads(args.event)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    result = on_message_received(event)
    print(json.dumps(result, ensure_ascii=False))

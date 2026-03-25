"""
Discovery Detector Hook
=======================
事件: message:received
功能: 检测用户的"啊哈时刻"——突然理解、顿悟、认知飞跃的信号
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── 配置 ──────────────────────────────────────────────

DATA_DIR = Path.home() / ".openclaw" / "cocoon" / "discoveries"
LOG_FILE = DATA_DIR / "discovery_log.jsonl"
STATE_FILE = Path.home() / ".openclaw" / "cocoon" / "user_state.json"

AHA_PATTERNS = [
    (r"(?:哦|啊)[!！]?\s*(?:原来|所以|怪不得|难怪)", "realization", 0.85),
    (r"我[突忽]然(?:明白|理解|懂|想通|意识到)", "realization", 0.90),
    (r"原来如此", "realization", 0.80),
    (r"这就(?:是|解释了)", "realization", 0.75),
    (r"(?:这|它)(?:跟|和|与).+?(?:一样|类似|相通|相似|是一回事)", "connection", 0.80),
    (r"所以.+?本质上(?:是|就是)", "connection", 0.85),
    (r"这不就是.+?吗", "connection", 0.80),
    (r"我(?:之前|以前|一直)(?:以为|觉得|认为).+?(?:其实|实际上|原来)", "paradigm_shift", 0.90),
    (r"(?:完全|彻底)(?:搞|想|理解)错了", "paradigm_shift", 0.85),
    (r"换个角度(?:看|想)", "paradigm_shift", 0.70),
    (r"(?:也就是说|换句话说|总结一下).+?(?:规律|模式|原则|本质|关键)(?:是|就是)", "generalization", 0.85),
    (r"我发现.+?(?:规律|模式|共同点|本质)", "generalization", 0.80),
    (r"(?:每次|总是|一般).+?(?:都会|都是).+?因为", "generalization", 0.70),
    (r"这(?:种|个|类)(?:事|任务|问题).+?(?:AI|人|自己)(?:更适合|更擅长|应该)", "boundary_insight", 0.80),
    (r"(?:AI|人工智能)(?:的|真正的)(?:价值|优势|作用)(?:在于|是)", "boundary_insight", 0.85),
    (r"(?:不应该|不需要)(?:让|用)\s*AI\s*(?:来|去)", "boundary_insight", 0.75),
    (r"我(?:注意到|发现)自己(?:总是|习惯|倾向于)", "metacognition", 0.85),
    (r"我的(?:思维|思考|习惯|模式)(?:是|有)", "metacognition", 0.75),
    (r"我(?:为什么|怎么)(?:总是|老是|一直)(?:会|要)", "metacognition", 0.70),
]

CONTEXT_BOOSTERS = [
    (r"[!！]{2,}", 0.05),
    (r"等等", 0.10),
    (r"不对", 0.08),
    (r"我[想再]想想", 0.05),
    (r"这意味着", 0.10),
]


@dataclass
class Discovery:
    timestamp: str
    session_id: str
    user_stage: int
    discovery_type: str
    confidence: float
    trigger_text: str
    context_before: str
    subskill_relevance: list
    stage_transition_signal: bool


def load_user_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"current_stage": 1, "session_count": 0, "scaffold_level": 0.80}


def detect_aha_moment(message: str, context_before: str = "") -> Optional[Discovery]:
    user_state = load_user_state()
    best_match = None
    best_confidence = 0.0

    for pattern, discovery_type, base_confidence in AHA_PATTERNS:
        match = re.search(pattern, message, re.IGNORECASE)
        if not match:
            continue
        confidence = base_confidence
        full_context = context_before + " " + message
        for booster_pattern, boost_value in CONTEXT_BOOSTERS:
            if re.search(booster_pattern, full_context):
                confidence = min(1.0, confidence + boost_value)
        stage = user_state.get("current_stage", 1)
        if stage >= 3 and discovery_type in ("paradigm_shift", "generalization", "metacognition"):
            confidence = min(1.0, confidence + 0.05)
        if len(message) < 10 and base_confidence < 0.85:
            confidence *= 0.7
        if re.search(r"(?:他|她|别人|有人)(?:说|觉得|认为)", message[:20]):
            confidence *= 0.5
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = (match, discovery_type, confidence)

    if best_match is None or best_confidence < 0.65:
        return None

    match, discovery_type, confidence = best_match
    subskill_map = {
        "realization": ["输出评估", "能力映射"],
        "connection": ["整合思维"],
        "paradigm_shift": ["能力映射", "整合思维"],
        "generalization": ["整合思维", "迭代策略"],
        "boundary_insight": ["能力映射"],
        "metacognition": ["迭代策略", "任务框定"],
    }
    subskill_relevance = subskill_map.get(discovery_type, [])
    stage = user_state.get("current_stage", 1)
    stage_transition_signal = False
    if stage <= 2 and discovery_type in ("boundary_insight", "metacognition"):
        stage_transition_signal = True
    elif stage == 3 and discovery_type in ("paradigm_shift", "generalization"):
        stage_transition_signal = True
    elif stage == 4 and discovery_type == "metacognition" and confidence > 0.85:
        stage_transition_signal = True

    return Discovery(
        timestamp=datetime.now().isoformat(),
        session_id=user_state.get("current_session_id", "unknown"),
        user_stage=stage,
        discovery_type=discovery_type,
        confidence=round(confidence, 3),
        trigger_text=message,
        context_before=context_before[-500:] if context_before else "",
        subskill_relevance=subskill_relevance,
        stage_transition_signal=stage_transition_signal,
    )


def save_discovery(discovery: Discovery) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(discovery), ensure_ascii=False) + "\n")


def append_transition_signal(signal_name: str) -> None:
    """写入 discovery 类型信号到 user_state.transition_signals，支持阶段跃迁评估"""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {"transition_signals": []}
    if "transition_signals" not in state:
        state["transition_signals"] = []
    if signal_name not in state["transition_signals"]:
        state["transition_signals"].append(signal_name)
    Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def on_message_received(event: dict) -> dict:
    message = event.get("message", "")
    context_before = event.get("context_before", "")
    discovery = detect_aha_moment(message, context_before)
    if discovery is None:
        return {"discovery_detected": False, "discovery": None, "mirror_trigger": False}
    save_discovery(discovery)
    if discovery.stage_transition_signal:
        append_transition_signal(discovery.discovery_type)
    mirror_trigger = (
        discovery.confidence >= 0.80
        or discovery.stage_transition_signal
        or discovery.discovery_type == "paradigm_shift"
    )
    return {
        "discovery_detected": True,
        "discovery": asdict(discovery),
        "mirror_trigger": mirror_trigger,
    }


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

"""
Stage Assessor Hook
===================
事件: agent:bootstrap (workaround — OpenClaw 没有 session:end)
功能: 每个 Cocoon session 启动时，递增 session 计数，更新脚手架，评估阶段跃迁
"""

import json
import math
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── 配置 ──────────────────────────────────────────────

DATA_DIR = Path.home() / ".openclaw" / "cocoon"
STATE_FILE = DATA_DIR / "user_state.json"
HISTORY_FILE = DATA_DIR / "assessment_history.jsonl"

SCAFFOLD_PARAMS = {
    1: {"s_max": 0.80, "s_min": 0.30, "lambda": 0.15},
    2: {"s_max": 0.70, "s_min": 0.20, "lambda": 0.20},
    3: {"s_max": 0.50, "s_min": 0.10, "lambda": 0.25},
    4: {"s_max": 0.30, "s_min": 0.05, "lambda": 0.30},
    5: {"s_max": 0.15, "s_min": 0.00, "lambda": 0.35},
}

SUBSKILLS = ["任务框定", "提示架构", "输出评估", "迭代策略", "能力映射", "整合思维"]

TRANSITION_THRESHOLDS = {
    1: {"min_sessions": 5, "min_avg_subskill": 1.5, "required_signals": ["stable_usage_pattern", "reduced_hesitation"]},
    2: {"min_sessions": 8, "min_avg_subskill": 2.5, "required_signals": ["proactive_decisions", "quality_judgment"]},
    3: {"min_sessions": 12, "min_avg_subskill": 3.5, "required_signals": ["system_thinking", "multi_agent_awareness"]},
    4: {"min_sessions": 15, "min_avg_subskill": 4.0, "required_signals": ["meta_reflection", "boundary_philosophy"]},
}


@dataclass
class UserState:
    current_stage: int = 1
    stage_session_count: int = 0
    total_session_count: int = 0
    scaffold_level: float = 0.80
    subskills: dict = field(default_factory=lambda: {s: 0.0 for s in SUBSKILLS})
    scaffold_floor_count: int = 0
    last_assessment: str = ""
    last_stage_transition: str = ""
    current_session_id: str = ""
    transition_signals: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserState":
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        for skill in SUBSKILLS:
            if skill not in state.subskills:
                state.subskills[skill] = 0.0
        return state


def load_state() -> UserState:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return UserState.from_dict(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return UserState()


def save_state(state: UserState) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)


def calculate_scaffold(stage: int, session_count: int) -> float:
    params = SCAFFOLD_PARAMS.get(stage, SCAFFOLD_PARAMS[1])
    s_max = params["s_max"]
    s_min = params["s_min"]
    lam = params["lambda"]
    scaffold = s_min + (s_max - s_min) * math.exp(-lam * session_count)
    return round(scaffold, 4)


def evaluate_stage_transition(state: UserState) -> Optional[int]:
    current = state.current_stage
    if current >= 5:
        return None
    threshold = TRANSITION_THRESHOLDS.get(current)
    if threshold is None:
        return None
    params = SCAFFOLD_PARAMS[current]
    scaffold_floor = params["s_min"] + 0.05
    if state.scaffold_level > scaffold_floor:
        state.scaffold_floor_count = 0
        return None
    if state.scaffold_floor_count < 3:
        return None
    if state.stage_session_count < threshold["min_sessions"]:
        return None
    avg_subskill = sum(state.subskills.values()) / max(1, len(state.subskills))
    # NOTE: subskill scoring is not yet implemented; threshold set to 0.0
    # to allow stage progression based on scaffold floor + session count + signals
    if avg_subskill < 0.0:
        return None
    required = set(threshold["required_signals"])
    observed = set(state.transition_signals)
    if not required.intersection(observed):
        return None
    return current + 1


def perform_stage_transition(state: UserState, new_stage: int) -> None:
    state.current_stage = new_stage
    state.stage_session_count = 0
    state.scaffold_floor_count = 0
    state.transition_signals = []
    state.scaffold_level = SCAFFOLD_PARAMS[new_stage]["s_max"]
    state.last_stage_transition = datetime.now().isoformat()


def save_assessment(state: UserState, transition: Optional[int]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(),
        "session_id": state.current_session_id,
        "stage": state.current_stage,
        "scaffold_level": state.scaffold_level,
        "subskills": state.subskills.copy(),
        "transition": transition,
    }
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def on_bootstrap(event: dict) -> dict:
    """
    Called on agent:bootstrap.
    Increments session count and recalculates scaffold.
    Note: subskill analysis from messages not available at bootstrap time.
    """
    state = load_state()
    previous_stage = state.current_stage

    state.current_session_id = event.get("session_id", "unknown")
    state.total_session_count += 1
    state.stage_session_count += 1

    # Recalculate scaffold with updated session count
    state.scaffold_level = calculate_scaffold(state.current_stage, state.stage_session_count)

    # Update scaffold floor count
    params = SCAFFOLD_PARAMS[state.current_stage]
    if state.scaffold_level <= params["s_min"] + 0.05:
        state.scaffold_floor_count += 1
    else:
        state.scaffold_floor_count = 0

    # Evaluate stage transition
    new_stage = evaluate_stage_transition(state)
    stage_changed = False
    if new_stage is not None:
        perform_stage_transition(state, new_stage)
        stage_changed = True

    state.last_assessment = datetime.now().isoformat()
    save_state(state)
    save_assessment(state, new_stage)

    return {
        "stage": state.current_stage,
        "previous_stage": previous_stage,
        "stage_changed": stage_changed,
        "scaffold_level": state.scaffold_level,
        "subskills": state.subskills.copy(),
        "transition_signals": state.transition_signals,
        "session_count": state.total_session_count,
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
    result = on_bootstrap(event)
    print(json.dumps(result, ensure_ascii=False))

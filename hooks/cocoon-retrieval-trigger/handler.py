"""
Retrieval Trigger Hook
======================
事件: agent:bootstrap
功能: 间隔检索练习触发器（改良 SM-2 间隔重复）
"""

import json
import math
import random
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


# ── 配置 ──────────────────────────────────────────────

DATA_DIR = Path.home() / ".openclaw" / "cocoon"
STATE_FILE = DATA_DIR / "user_state.json"
RETRIEVAL_FILE = DATA_DIR / "retrieval_schedule.json"

INITIAL_INTERVAL_HOURS = 24
INTERVAL_MULTIPLIER = 2.2
MIN_INTERVAL_HOURS = 12
MAX_INTERVAL_HOURS = 720
EASE_FACTOR_DEFAULT = 2.5
EASE_FACTOR_MIN = 1.3
EASE_FACTOR_ADJUSTMENT = 0.1
MAX_RETRIEVALS_PER_SESSION = 1

RETRIEVAL_TEMPLATES = {
    "任务框定": [
        {
            "type": "scenario",
            "prompt": "假设你要让 AI 帮你 {scenario}。你会怎么描述这个任务？关键的约束和期望输出是什么？",
            "scenarios": [
                "重构一个混乱的配置文件",
                "分析一组用户反馈找出规律",
                "设计一个新功能的技术方案",
                "写一封给技术团队的邮件",
                "调试一个间歇性出现的bug",
            ],
        },
        {
            "type": "reflection",
            "prompt": "上次你让 AI 做 {past_task} 的时候，任务描述中有没有什么关键信息是后来补充的？如果重新来一次，你会在一开始就包含什么？",
        },
    ],
    "提示架构": [
        {
            "type": "scenario",
            "prompt": "你要用 AI 完成一个需要多步骤的任务：{scenario}。你会怎么拆分步骤？",
            "scenarios": [
                "把一份研究论文改写成技术博客",
                "把单体应用的一个模块拆成微服务",
                "根据数据做月度分析报告",
                "设计并实现一个 API 接口",
            ],
        },
    ],
    "输出评估": [
        {
            "type": "judgment",
            "prompt": "AI 刚生成了一个 {artifact}。在检查它之前，你会关注哪几个维度来判断它的质量？",
            "artifacts": [
                "数据库架构设计",
                "代码重构方案",
                "技术调研报告",
                "自动化测试脚本",
            ],
        },
    ],
    "迭代策略": [
        {
            "type": "scenario",
            "prompt": "AI 的第一版输出不符合期望。具体问题是 {problem}。你的下一步是什么——你会怎么调整你的指令？",
            "problems": [
                "方向对了但细节不够精确",
                "格式正确但内容过于泛化",
                "技术上正确但不适合目标受众",
                "答案完整但太冗长",
            ],
        },
    ],
    "能力映射": [
        {
            "type": "boundary",
            "prompt": "在 {task} 这个任务中，哪些部分你更信任 AI 来做，哪些部分你一定要自己做？为什么？",
            "tasks": [
                "写一篇需要原创洞见的分析文章",
                "设计一个面向新用户的产品体验",
                "做一个涉及商业判断的技术选型",
                "处理一个有敏感数据的分析任务",
            ],
        },
    ],
    "整合思维": [
        {
            "type": "connection",
            "prompt": "你最近在 {domain_a} 中用了某种方法。这种方法能不能迁移到 {domain_b}？如果能，需要怎么调整？",
            "domain_pairs": [
                ("代码开发", "写作"),
                ("数据分析", "项目规划"),
                ("调试", "学习新概念"),
                ("系统设计", "团队管理"),
            ],
        },
    ],
}


@dataclass
class RetrievalItem:
    skill: str
    template_type: str
    created_at: str
    next_review: str
    interval_hours: float
    ease_factor: float
    review_count: int
    last_result: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RetrievalItem":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def load_retrieval_schedule() -> list:
    try:
        with open(RETRIEVAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [RetrievalItem.from_dict(item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_retrieval_schedule(items: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(RETRIEVAL_FILE, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)


def load_user_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"current_stage": 1, "subskills": {}, "total_session_count": 0}


def get_weakest_skills(user_state: dict, top_n: int = 2) -> list:
    subskills = user_state.get("subskills", {})
    if not subskills:
        return ["任务框定", "提示架构"]
    sorted_skills = sorted(subskills.items(), key=lambda x: x[1])
    return [skill for skill, _ in sorted_skills[:top_n]]


def generate_retrieval_prompt(skill: str, user_state: dict) -> Optional[dict]:
    templates = RETRIEVAL_TEMPLATES.get(skill, [])
    if not templates:
        return None
    template = random.choice(templates)
    template_type = template["type"]
    prompt_template = template["prompt"]
    if template_type == "scenario" and "scenarios" in template:
        scenario = random.choice(template["scenarios"])
        prompt = prompt_template.format(scenario=scenario)
    elif template_type == "judgment" and "artifacts" in template:
        artifact = random.choice(template["artifacts"])
        prompt = prompt_template.format(artifact=artifact)
    elif template_type == "boundary" and "tasks" in template:
        task = random.choice(template["tasks"])
        prompt = prompt_template.format(task=task)
    elif template_type == "connection" and "domain_pairs" in template:
        domain_a, domain_b = random.choice(template["domain_pairs"])
        prompt = prompt_template.format(domain_a=domain_a, domain_b=domain_b)
    elif template_type == "reflection":
        prompt = prompt_template.format(past_task="之前的任务")
    else:
        prompt = prompt_template
    return {"skill": skill, "prompt": prompt, "type": template_type}


def get_due_retrievals(schedule: list, now: datetime) -> list:
    due = []
    for item in schedule:
        try:
            next_review = datetime.fromisoformat(item.next_review)
            if now >= next_review:
                due.append(item)
        except ValueError:
            continue
    return due


def create_new_retrieval_items(user_state: dict, existing_skills: set) -> list:
    weak_skills = get_weakest_skills(user_state)
    new_items = []
    now = datetime.now()
    for skill in weak_skills:
        if skill not in existing_skills:
            item = RetrievalItem(
                skill=skill,
                template_type="mixed",
                created_at=now.isoformat(),
                next_review=(now + timedelta(hours=INITIAL_INTERVAL_HOURS)).isoformat(),
                interval_hours=INITIAL_INTERVAL_HOURS,
                ease_factor=EASE_FACTOR_DEFAULT,
                review_count=0,
            )
            new_items.append(item)
    return new_items


def on_bootstrap(event: dict) -> dict:
    now = datetime.now()
    user_state = load_user_state()
    stage = user_state.get("current_stage", 1)

    # Stage 1 users with < 5 sessions: skip retrieval
    if stage < 2 and user_state.get("total_session_count", 0) < 5:
        return {
            "retrieval_triggered": False,
            "retrieval_prompts": [],
            "schedule_summary": {"total_items": 0, "due_items": 0, "next_due_in_hours": -1},
        }

    schedule = load_retrieval_schedule()
    existing_skills = {item.skill for item in schedule}
    new_items = create_new_retrieval_items(user_state, existing_skills)
    schedule.extend(new_items)
    due_items = get_due_retrievals(schedule, now)
    retrieval_prompts = []
    if due_items:
        weak_skills = get_weakest_skills(user_state, top_n=6)
        skill_priority = {skill: i for i, skill in enumerate(weak_skills)}
        due_items.sort(key=lambda item: skill_priority.get(item.skill, 99))
        for item in due_items[:MAX_RETRIEVALS_PER_SESSION]:
            prompt_data = generate_retrieval_prompt(item.skill, user_state)
            if prompt_data:
                retrieval_prompts.append(prompt_data)

    next_due_hours = -1
    future_items = [
        item for item in schedule
        if datetime.fromisoformat(item.next_review) > now
    ]
    if future_items:
        nearest = min(future_items, key=lambda x: datetime.fromisoformat(x.next_review))
        delta = datetime.fromisoformat(nearest.next_review) - now
        next_due_hours = round(delta.total_seconds() / 3600, 1)

    save_retrieval_schedule(schedule)
    return {
        "retrieval_triggered": len(retrieval_prompts) > 0,
        "retrieval_prompts": retrieval_prompts,
        "schedule_summary": {
            "total_items": len(schedule),
            "due_items": len(due_items),
            "next_due_in_hours": next_due_hours,
        },
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

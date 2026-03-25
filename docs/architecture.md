# 架构设计

## 系统总览

```
用户消息
    │
    ▼
┌──────────────────┐
│  cocoon-router   │  ← Hook: 意图信号检测
│  (handler.js)    │     task / reflect / progress / ambiguous
└──────┬───────────┘
       │
       ├──→ cocoon-mindset-monitor  ← Hook: 心态回退检测 (message:received)
       │    (handler.py)
       │
       ├──→ cocoon-discovery-detector ← Hook: 啊哈时刻检测 (message:received)
       │    (handler.py)
       │
       ▼
┌──────────────────────────────────────────────┐
│              OpenClaw Agent Runtime            │
│                                                │
│  ┌────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │  搭档       │ │  同行者       │ │  镜子     │ │
│  │  Partner    │ │  Companion   │ │  Mirror  │ │
│  │  (SOUL.md)  │ │  (SOUL.md)   │ │ (SOUL.md)│ │
│  └────────────┘ └──────────────┘ └──────────┘ │
└──────────────────────────────────────────────┘
       ▲                    ▲
       │                    │
  cocoon-stage-assessor     cocoon-retrieval-trigger
  (agent:bootstrap)         (agent:bootstrap)
  脚手架衰减+阶段跃迁      间隔检索练习注入
```

## 组件清单

### Agents (3)

| Agent | 文件 | SDT 需求 | 说明 |
|-------|------|----------|------|
| cocoon-partner | SOUL.md, BOOTSTRAP.md, IDENTITY.md, stage-config.md, USER.md | 胜任感 | 主 agent，内置三姿态切换 |
| cocoon-companion | SOUL.md, stage-config.md | 自主感 | 反思对话，不给答案 |
| cocoon-mirror | SOUL.md, stage-config.md | 联结感 | 跨 session 行为观察 |

### Hooks (5)

| Hook | 事件 | 语言 | 说明 |
|------|------|------|------|
| cocoon-router | agent:bootstrap, message:received | JS | 会话追踪 + 意图信号分类 |
| cocoon-discovery-detector | message:received | JS→Python | 啊哈时刻检测（18种模式） |
| cocoon-stage-assessor | agent:bootstrap | JS→Python | session 计数 + 脚手架衰减 + 阶段跃迁评估 |
| cocoon-retrieval-trigger | agent:bootstrap | JS→Python | SM-2 间隔检索 + bootstrap 文件注入 |
| cocoon-mindset-monitor | message:received | JS→Python | 心态回退信号检测（3级） |

### 数据文件

所有数据存储在 `~/.openclaw/cocoon/`：

| 文件 | 用途 |
|------|------|
| user_state.json | 用户状态：阶段、脚手架、六子技能评分 |
| retrieval_schedule.json | SM-2 检索调度 |
| assessment_history.jsonl | 每 session 评估记录 |
| mindset_log.jsonl | 心态回退信号日志 |
| discoveries/discovery_log.jsonl | 啊哈时刻记录 |
| active_agent.json | 当前活跃 agent（TTL 1小时） |

## Hook 架构模式

所有行为 Hook 共享相同的架构模式：

```
handler.js (薄层)
    │
    ├── 1. 事件过滤（是否在 Cocoon session 中）
    ├── 2. TTL 检查（active_agent.json, 1小时）
    ├── 3. 调用 Python 子进程
    └── 4. 处理结果（日志/注入bootstrap文件）
          │
          ▼
handler.py (核心逻辑)
    │
    ├── 模式匹配 / 算法计算
    ├── 状态读写（JSON/JSONL）
    └── 返回 JSON 结果
```

**为什么 JS + Python 双层？**
- JS 是 OpenClaw Hook 的原生格式，负责事件接口
- Python 处理复杂逻辑（正则、数学、状态管理），更易维护和测试
- cocoon-router 是唯一纯 JS 的 Hook（路由逻辑简单，不需要 Python）

## 六子技能

搭档在执行过程中隐式训练六个子技能：

| 子技能 | 训练方式 |
|--------|----------|
| 任务框定 | 通过让用户参与需求澄清 |
| 提示架构 | 通过展示任务分解过程 |
| 输出评估 | 通过留决策点让用户判断质量 |
| 迭代策略 | 通过失败处理流程 |
| 能力映射 | 通过指出人-AI边界 |
| 整合思维 | 通过跨任务连接 |

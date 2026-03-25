# 快速上手

## 安装

### 1. 确保 OpenClaw 已安装

Cocoon 运行在 OpenClaw 之上。如果还没有安装：https://openclaw.ai

### 2. 克隆并安装

```bash
git clone https://github.com/TerryFYL/cocoon.git
cd cocoon
bash scripts/install.sh
```

安装脚本会：
- 将三个 Agent 注册到 OpenClaw
- 安装五个 Hook
- 初始化数据目录

### 3. 填写用户档案

安装后编辑 `~/.openclaw/workspace-cocoon-partner/USER.md`，填入你的基本信息。

## 使用

### 开始

在 OpenClaw 中切换到 `cocoon-partner` agent。然后直接说你想做什么：

```
你：帮我写个 Python 爬虫
搭档：目标网站是哪个？需要爬什么数据？
```

**就这样。** 不需要学命令，不需要看文档。做事就行。

### 三种模式自动切换

系统会根据你说话的方式自动切换角色：

| 你说的话 | 系统识别为 | 响应角色 |
|---------|-----------|---------|
| "帮我写个脚本" | 任务信号 | 搭档 |
| "我不确定该用哪个方案" | 反思信号 | 同行者 |
| "我发现我用AI的方式变了" | 进度信号 | 镜子 |

你不需要手动切换。说话就行。

### 查看你的状态

数据文件在 `~/.openclaw/cocoon/user_state.json`：

```json
{
  "current_stage": 1,
  "scaffold_level": 0.80,
  "subskills": {
    "任务框定": 0.0,
    "提示架构": 0.0,
    ...
  }
}
```

### 重置

想重新开始？

```bash
bash cocoon/scripts/cleanup.sh
```

会自动备份当前数据再重置。

## 自定义

### 调整脚手架参数

编辑 `~/.openclaw/workspace-cocoon-partner/stage-config.md` 中的衰减参数：

```
| 阶段 | S_max | S_min | lambda |
```

- 增大 `lambda` = 衰减更快（AI 更快放手）
- 增大 `S_min` = AI 永远保持更多介入

### 添加检索练习模板

编辑 `hooks/cocoon-retrieval-trigger/handler.py` 中的 `RETRIEVAL_TEMPLATES`。

### 添加啊哈时刻模式

编辑 `hooks/cocoon-discovery-detector/handler.py` 中的 `AHA_PATTERNS`。

## 常见问题

**Q: 我已经很会用 AI 了，这个系统对我有用吗？**
A: 有。手动修改 `user_state.json` 的 `current_stage` 到 3 或 4，跳过前面的阶段。

**Q: 支持英文吗？**
A: Agent 的 SOUL.md 是中文的（行为指令），但你可以用任何语言跟它对话。意图路由的正则目前只支持中文，PR 欢迎。

**Q: 不用 OpenClaw 能用吗？**
A: 目前不能。但核心设计（SOUL.md + stage-config.md）可以手动适配到任何 AI Agent 平台。

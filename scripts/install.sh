#!/bin/bash
# Cocoon - AI Learning System for OpenClaw
# 一键安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
COCOON_DATA="$OPENCLAW_DIR/cocoon"

echo "🦋 Cocoon 安装开始..."
echo ""

# 检查 OpenClaw 目录
if [ ! -d "$OPENCLAW_DIR" ]; then
  echo "❌ 未检测到 OpenClaw 安装目录 (~/.openclaw)"
  echo "   请先安装 OpenClaw: https://openclaw.ai"
  exit 1
fi

# 安装 Agents
echo "📦 安装 Agents..."
for agent in cocoon-partner cocoon-companion cocoon-mirror; do
  AGENT_DIR="$OPENCLAW_DIR/workspace-$agent"
  mkdir -p "$AGENT_DIR"

  # 复制 agent 文件
  SRC="$SCRIPT_DIR/agents/$agent"
  if [ -d "$SRC" ]; then
    cp "$SRC/SOUL.md" "$AGENT_DIR/" 2>/dev/null || true
    cp "$SRC/stage-config.md" "$AGENT_DIR/" 2>/dev/null || true
    cp "$SRC/BOOTSTRAP.md" "$AGENT_DIR/" 2>/dev/null || true
    cp "$SRC/IDENTITY.md" "$AGENT_DIR/" 2>/dev/null || true

    # USER.md: 如果已存在则不覆盖
    if [ ! -f "$AGENT_DIR/USER.md" ] && [ -f "$SRC/USER.md.template" ]; then
      cp "$SRC/USER.md.template" "$AGENT_DIR/USER.md"
      echo "   ⚠️  请编辑 $AGENT_DIR/USER.md 填入你的信息"
    fi
  fi

  # 注册 agent（创建 agent 目录）
  mkdir -p "$OPENCLAW_DIR/agents/$agent/agent"

  echo "   ✅ $agent"
done

# 安装 Hooks
echo "📦 安装 Hooks..."
for hook in cocoon-router cocoon-discovery-detector cocoon-stage-assessor cocoon-retrieval-trigger cocoon-mindset-monitor; do
  HOOK_DIR="$OPENCLAW_DIR/hooks/$hook"
  SRC="$SCRIPT_DIR/hooks/$hook"

  if [ -d "$SRC" ]; then
    mkdir -p "$HOOK_DIR"
    cp "$SRC"/* "$HOOK_DIR/"
    echo "   ✅ $hook"
  fi
done

# 初始化数据目录
echo "📦 初始化数据..."
mkdir -p "$COCOON_DATA/discoveries"

if [ ! -f "$COCOON_DATA/user_state.json" ]; then
  cp "$SCRIPT_DIR/data/user_state.json" "$COCOON_DATA/"
fi

if [ ! -f "$COCOON_DATA/retrieval_schedule.json" ]; then
  cp "$SCRIPT_DIR/data/retrieval_schedule.json" "$COCOON_DATA/"
fi

touch "$COCOON_DATA/assessment_history.jsonl"
touch "$COCOON_DATA/mindset_log.jsonl"
touch "$COCOON_DATA/discoveries/discovery_log.jsonl"

echo ""
echo "🦋 Cocoon 安装完成！"
echo ""
echo "开始使用："
echo "  在 OpenClaw 中切换到 cocoon-partner agent 即可开始"
echo "  系统会自动路由你的消息到合适的角色（搭档/同行者/镜子）"
echo ""
echo "数据目录: $COCOON_DATA"
echo "重置数据: bash $(dirname "$0")/cleanup.sh"

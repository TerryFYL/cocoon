#!/bin/bash
# Cocoon - 数据重置脚本
# 重置所有学习数据，用于测试或重新开始

set -e

COCOON_DIR="$HOME/.openclaw/cocoon"
BACKUP_DIR="$COCOON_DIR/backups/$(date +%Y%m%d-%H%M%S)"

# 创建备份
if [ -f "$COCOON_DIR/user_state.json" ]; then
  mkdir -p "$BACKUP_DIR"
  cp -r "$COCOON_DIR"/*.json "$BACKUP_DIR/" 2>/dev/null || true
  cp -r "$COCOON_DIR"/*.jsonl "$BACKUP_DIR/" 2>/dev/null || true
  [ -d "$COCOON_DIR/discoveries" ] && cp -r "$COCOON_DIR/discoveries" "$BACKUP_DIR/" 2>/dev/null || true
  echo "备份已保存至: $BACKUP_DIR"
fi

# 重置状态
cat > "$COCOON_DIR/user_state.json" << 'EOF'
{
  "current_stage": 1,
  "stage_session_count": 0,
  "total_session_count": 0,
  "scaffold_level": 0.80,
  "subskills": {
    "任务框定": 0.0,
    "提示架构": 0.0,
    "输出评估": 0.0,
    "迭代策略": 0.0,
    "能力映射": 0.0,
    "整合思维": 0.0
  },
  "scaffold_floor_count": 0,
  "last_assessment": "",
  "last_stage_transition": "",
  "current_session_id": "",
  "transition_signals": []
}
EOF

echo "[]" > "$COCOON_DIR/retrieval_schedule.json"
> "$COCOON_DIR/assessment_history.jsonl"
> "$COCOON_DIR/mindset_log.jsonl"
mkdir -p "$COCOON_DIR/discoveries"
> "$COCOON_DIR/discoveries/discovery_log.jsonl"
rm -f "$COCOON_DIR/active_agent.json"

echo "🦋 Cocoon 数据已重置为初始状态"

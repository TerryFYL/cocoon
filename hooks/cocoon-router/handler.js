/**
 * Cocoon Router Hook
 *
 * 1. On agent:bootstrap — detects if a Cocoon agent started, writes active_agent.json
 * 2. On message:received — checks if in cocoon session, detects routing signal type
 */
import fs from "node:fs/promises";
import path from "node:path";

const HOME = process.env.HOME || "";
const COCOON_DIR = path.join(HOME, ".openclaw", "cocoon");
const ACTIVE_AGENT_FILE = path.join(COCOON_DIR, "active_agent.json");
const COCOON_AGENT_IDS = ["cocoon-partner", "cocoon-companion", "cocoon-mirror"];
const COCOON_SESSION_TTL_MS = 3600000; // 1 hour

// Routing signal patterns
const SIGNAL_PATTERNS = {
  task: /帮[我一]|[写做实现创建删除修复调试]一个|代码|脚本|函数|执行|运行|部署|能不能帮|请帮/,
  reflect: /感觉|觉得|不确定|为什么我|想聊聊|我在想|有点困惑|说说|我怎么|我有点/,
  progress: /我发现|我注意到|我进步|我变了|我以前|我现在|我的模式|我的规律|我的思维/,
};

/**
 * Extract agent ID from workspace dir path
 * e.g. "/home/user/.openclaw/workspace-cocoon-partner" → "cocoon-partner"
 */
function extractAgentId(workspaceDir) {
  if (!workspaceDir) return null;
  const base = path.basename(workspaceDir);
  const match = base.match(/^workspace-(.+)$/);
  return match ? match[1] : null;
}

/**
 * Check if currently in an active cocoon session (within TTL)
 */
async function isCocoonSession() {
  try {
    const raw = await fs.readFile(ACTIVE_AGENT_FILE, "utf-8");
    const data = JSON.parse(raw);
    const age = Date.now() - (data.ts || 0);
    return age < COCOON_SESSION_TTL_MS && COCOON_AGENT_IDS.includes(data.agent_id);
  } catch {
    return false;
  }
}

/**
 * Detect routing signal type from message content
 */
function detectSignal(message) {
  if (!message) return "ambiguous";
  for (const [type, pattern] of Object.entries(SIGNAL_PATTERNS)) {
    if (pattern.test(message)) return type;
  }
  return "ambiguous";
}

const cocoonRouter = async (event) => {
  // On bootstrap: record active agent if it's a cocoon agent
  if (event.type === "agent" && event.action === "bootstrap") {
    const context = event.context || {};
    const agentId = extractAgentId(context.workspaceDir);
    if (agentId && COCOON_AGENT_IDS.includes(agentId)) {
      try {
        await fs.mkdir(COCOON_DIR, { recursive: true });
        await fs.writeFile(
          ACTIVE_AGENT_FILE,
          JSON.stringify({ agent_id: agentId, ts: Date.now() })
        );
        console.log(`[cocoon-router] Cocoon session started: ${agentId}`);
      } catch (err) {
        console.error(
          "[cocoon-router] Failed to write active_agent.json:",
          err instanceof Error ? err.message : String(err)
        );
      }
    }
    return;
  }

  // On message received: detect signal type for analytics
  if (event.type !== "message" || event.action !== "received") return;
  if (!(await isCocoonSession())) return;

  const content = event.context?.content;
  if (!content) return;

  const signalType = detectSignal(content);
  if (signalType !== "ambiguous") {
    console.log(`[cocoon-router] Signal: ${signalType} | ${content.slice(0, 60)}`);
  }
};

export default cocoonRouter;

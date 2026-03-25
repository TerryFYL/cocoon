/**
 * Cocoon Router Hook
 *
 * 1. On agent:bootstrap — detects if a Cocoon agent started, writes active_agent.json
 *    (其他 hook 如 mindset-monitor 依赖这个判断是否在 cocoon session)
 * 2. On message:received — 意图路由已移至 LLM（各 Agent 的 SOUL.md 里自行判断边界）
 *    此处不再做正则匹配
 */
import fs from "node:fs/promises";
import path from "node:path";

const HOME = process.env.HOME || "";
const COCOON_DIR = path.join(HOME, ".openclaw", "cocoon");
const ACTIVE_AGENT_FILE = path.join(COCOON_DIR, "active_agent.json");
const COCOON_AGENT_IDS = ["cocoon-partner", "cocoon-companion", "cocoon-mirror"];
const COCOON_SESSION_TTL_MS = 3600000; // 1 hour

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

  // On message received: 意图路由由各 Agent 的 LLM 自行判断
  // 此处不再做正则匹配或信号检测
};

export default cocoonRouter;

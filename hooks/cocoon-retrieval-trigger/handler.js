/**
 * Cocoon Retrieval Trigger Hook
 *
 * On cocoon agent bootstrap: checks retrieval schedule and injects
 * due practice prompts as COCOON_RETRIEVAL.md bootstrap file.
 */
import { execFile } from "node:child_process";
import path from "node:path";

const HOME = process.env.HOME || "";
const HANDLER_PY = path.join(
  HOME,
  ".openclaw",
  "hooks",
  "cocoon-retrieval-trigger",
  "handler.py"
);
const COCOON_AGENT_IDS = ["cocoon-partner", "cocoon-companion", "cocoon-mirror"];

function extractAgentId(workspaceDir) {
  if (!workspaceDir) return null;
  const base = path.basename(workspaceDir);
  const match = base.match(/^workspace-(.+)$/);
  return match ? match[1] : null;
}

function callPythonRetrieval(sessionId) {
  return new Promise((resolve) => {
    const eventJson = JSON.stringify({
      session_id: sessionId,
      timestamp: new Date().toISOString(),
    });
    execFile(
      "python3",
      [HANDLER_PY, "--event", eventJson],
      { timeout: 15000, encoding: "utf-8" },
      (error, stdout) => {
        if (!error && stdout.trim()) {
          try {
            resolve(JSON.parse(stdout.trim()));
          } catch {
            resolve(null);
          }
        } else {
          if (error)
            console.error(
              "[cocoon-retrieval-trigger] Python error:",
              error instanceof Error ? error.message : String(error)
            );
          resolve(null);
        }
      }
    );
  });
}

const cocoonRetrievalTrigger = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  const context = event.context || {};
  const agentId = extractAgentId(context.workspaceDir);
  if (!agentId || !COCOON_AGENT_IDS.includes(agentId)) return;

  const sessionId = `${agentId}-${Date.now()}`;
  const result = await callPythonRetrieval(sessionId);

  if (result?.retrieval_triggered && result.retrieval_prompts?.length > 0) {
    const prompts = result.retrieval_prompts;
    const content = [
      "# Cocoon 检索练习",
      "",
      "> 间隔重复练习提示，帮助你巩固已学技能。",
      "",
      ...prompts.map((p) => `**[${p.skill}]** ${p.prompt}`),
    ].join("\n");

    const bootstrapFiles = context.bootstrapFiles || [];
    bootstrapFiles.push({
      name: "COCOON_RETRIEVAL.md",
      path: "/tmp/cocoon-retrieval-prompt.md",
      content,
      missing: false,
    });
    context.bootstrapFiles = bootstrapFiles;

    console.log(`[cocoon-retrieval-trigger] Injected ${prompts.length} retrieval prompt(s)`);
  }
};

export default cocoonRetrievalTrigger;

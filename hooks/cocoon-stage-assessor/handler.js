/**
 * Cocoon Stage Assessor Hook
 *
 * On cocoon agent bootstrap: increment session count, recalculate scaffold,
 * evaluate stage transitions via handler.py.
 */
import { execFile } from "node:child_process";
import path from "node:path";

const HOME = process.env.HOME || "";
const HANDLER_PY = path.join(
  HOME,
  ".openclaw",
  "hooks",
  "cocoon-stage-assessor",
  "handler.py"
);
const COCOON_AGENT_IDS = ["cocoon-partner", "cocoon-companion", "cocoon-mirror"];

function extractAgentId(workspaceDir) {
  if (!workspaceDir) return null;
  const base = path.basename(workspaceDir);
  const match = base.match(/^workspace-(.+)$/);
  return match ? match[1] : null;
}

function callPythonAssessor(sessionId) {
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
              "[cocoon-stage-assessor] Python error:",
              error instanceof Error ? error.message : String(error)
            );
          resolve(null);
        }
      }
    );
  });
}

const cocoonStageAssessor = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  const context = event.context || {};
  const agentId = extractAgentId(context.workspaceDir);
  if (!agentId || !COCOON_AGENT_IDS.includes(agentId)) return;

  const sessionId = `${agentId}-${Date.now()}`;
  const result = await callPythonAssessor(sessionId);
  if (result) {
    const { stage, scaffold_level, stage_changed } = result;
    if (stage_changed) {
      console.log(
        `[cocoon-stage-assessor] Stage transition → Stage ${stage}! scaffold=${scaffold_level}`
      );
    } else {
      console.log(`[cocoon-stage-assessor] Stage=${stage} scaffold=${scaffold_level}`);
    }
  }
};

export default cocoonStageAssessor;

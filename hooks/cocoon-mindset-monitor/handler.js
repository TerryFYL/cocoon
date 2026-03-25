/**
 * Cocoon Mindset Monitor Hook
 *
 * Detects mindset regression signals in Cocoon session messages.
 * Calls handler.py and logs scaffold adjustment guidance.
 */
import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";

const HOME = process.env.HOME || "";
const COCOON_DIR = path.join(HOME, ".openclaw", "cocoon");
const ACTIVE_AGENT_FILE = path.join(COCOON_DIR, "active_agent.json");
const HANDLER_PY = path.join(
  HOME,
  ".openclaw",
  "hooks",
  "cocoon-mindset-monitor",
  "handler.py"
);
const COCOON_AGENT_IDS = ["cocoon-partner", "cocoon-companion", "cocoon-mirror"];
const COCOON_SESSION_TTL_MS = 3600000;

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

function callPythonMonitor(message) {
  return new Promise((resolve) => {
    const eventJson = JSON.stringify({
      message,
      timestamp: new Date().toISOString(),
    });
    execFile(
      "python3",
      [HANDLER_PY, "--event", eventJson],
      { timeout: 10000, encoding: "utf-8" },
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
              "[cocoon-mindset-monitor] Python error:",
              error instanceof Error ? error.message : String(error)
            );
          resolve(null);
        }
      }
    );
  });
}

const cocoonMindsetMonitor = async (event) => {
  if (event.type !== "message" || event.action !== "received") return;
  if (!(await isCocoonSession())) return;

  const content = event.context?.content;
  if (!content || typeof content !== "string") return;

  const result = await callPythonMonitor(content);
  if (result?.regression_detected) {
    const level = result.regression_level;
    const adj = result.scaffold_adjustment;
    console.log(`[cocoon-mindset-monitor] Regression L${level} detected, scaffold +${adj}`);
  }
};

export default cocoonMindsetMonitor;

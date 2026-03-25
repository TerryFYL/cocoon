/**
 * Cocoon Discovery Detector Hook
 *
 * Detects aha moments in user messages during active Cocoon sessions.
 * Calls handler.py via subprocess and records discoveries.
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
  "cocoon-discovery-detector",
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

function callPythonHandler(message) {
  return new Promise((resolve) => {
    const eventJson = JSON.stringify({ message, context_before: "" });
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
              "[cocoon-discovery-detector] Python error:",
              error instanceof Error ? error.message : String(error)
            );
          resolve(null);
        }
      }
    );
  });
}

const cocoonDiscoveryDetector = async (event) => {
  if (event.type !== "message" || event.action !== "received") return;
  if (!(await isCocoonSession())) return;

  const content = event.context?.content;
  if (!content || typeof content !== "string") return;

  const result = await callPythonHandler(content);
  if (result?.discovery_detected) {
    const d = result.discovery;
    console.log(
      `[cocoon-discovery-detector] ${d.discovery_type} conf=${d.confidence} mirror_trigger=${result.mirror_trigger}`
    );
  }
};

export default cocoonDiscoveryDetector;

import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function inspectRangeSnapshotPptx(pptxPath) {
  const script = path.resolve(__dirname, "..", "scripts", "inspect_range_snapshot.py");
  const result = spawnSync("python", [script, "--pptx", pptxPath], { encoding: "utf-8" });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || "inspect failed");
  }
  return JSON.parse(result.stdout);
}

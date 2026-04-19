import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function renderRangeSnapshotPptx(spec, outputPath) {
  const script = path.resolve(__dirname, "..", "scripts", "render_range_snapshot.py");
  const templatePath = path.resolve(__dirname, "..", "templates", "range_snapshot_template.pptx");

  if (!fs.existsSync(templatePath)) {
    const createScript = path.resolve(__dirname, "..", "scripts", "create_template.py");
    const created = spawnSync("python", [createScript, "--output", templatePath], { encoding: "utf-8" });
    if (created.status !== 0) {
      throw new Error(created.stderr || created.stdout || "template bootstrap failed");
    }
  }

  const result = spawnSync(
    "python",
    [script, "--template", templatePath, "--output", outputPath, "--spec-json", JSON.stringify(spec)],
    { encoding: "utf-8" },
  );

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || "render failed");
  }
}

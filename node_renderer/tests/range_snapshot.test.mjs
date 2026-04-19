import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { renderRangeSnapshotPptx } from "../src/renderer.mjs";
import { inspectRangeSnapshotPptx } from "../src/parser.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = path.resolve(__dirname, "tmp");

const specBase = {
  chart_family: "range_snapshot",
  categories_col: "行业",
  min_col: "min",
  max_col: "max",
  average_col: "avg",
  current_col: "cur",
  rows: [
    { category: "A", min: 10, max: 20, average: 15, current: 18 },
    { category: "B", min: 12, max: 25, average: 19, current: 22 },
  ],
};

function readChartXml(file) {
  const py = `import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); print(z.read('ppt/charts/chart1.xml').decode('utf-8'))`;
  const ret = spawnSync("python", ["-c", py, file], { encoding: "utf-8" });
  assert.equal(ret.status, 0, ret.stderr);
  return ret.stdout;
}

test("vertical render test", () => {
  const file = path.join(outDir, "vertical.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "vertical" }, file);
  const xml = readChartXml(file);
  assert.ok(/barDir val="col"/.test(xml));
});

test("horizontal render test", () => {
  const file = path.join(outDir, "horizontal.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "horizontal" }, file);
  const xml = readChartXml(file);
  assert.ok(/barDir val="bar"/.test(xml));
});

test("axis_break metadata test", () => {
  const file = path.join(outDir, "axis_break.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "vertical", axis_break: { enabled: true, min: 5, max: 30 } }, file);
  const parsed = inspectRangeSnapshotPptx(file);
  assert.equal(parsed.axis_break.enabled, true);
  assert.equal(parsed.axis_break.min, 5);
  assert.equal(parsed.axis_break.max, 30);
});

test("embedded workbook existence test", () => {
  const file = path.join(outDir, "workbook_exists.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "vertical" }, file);
  const py = `import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); print(any(n.startswith('ppt/embeddings/') and n.endswith('.xlsx') for n in z.namelist()))`;
  const ret = spawnSync("python", ["-c", py, file], { encoding: "utf-8" });
  assert.equal(ret.status, 0, ret.stderr);
  assert.equal(ret.stdout.trim(), "True");
});

test("metadata existence test", () => {
  const file = path.join(outDir, "metadata_exists.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "vertical" }, file);
  const parsed = inspectRangeSnapshotPptx(file);
  assert.equal(parsed.chart_family, "range_snapshot");
  assert.equal(parsed.categories_col, "行业");
});

test("parse recovery test", () => {
  const file = path.join(outDir, "parse_recovery.pptx");
  renderRangeSnapshotPptx({ ...specBase, orientation: "horizontal", axis_break: { enabled: true, min: 5, max: 30 } }, file);
  const parsed = inspectRangeSnapshotPptx(file);
  assert.equal(parsed.orientation, "horizontal");
  assert.equal(parsed.min_col, "min");
  assert.equal(parsed.max_col, "max");
  assert.equal(parsed.average_col, "avg");
  assert.equal(parsed.current_col, "cur");
  assert.equal(parsed.rows.length, 2);
  assert.equal(parsed.rows[0].category, "A");
});

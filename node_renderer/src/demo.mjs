import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderRangeSnapshotPptx } from "./renderer.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rows = [
  { category: "银行", min: 82, max: 95, average: 89, current: 91 },
  { category: "券商", min: 70, max: 86, average: 78, current: 81 },
  { category: "保险", min: 64, max: 80, average: 72, current: 75 },
];

const base = {
  chart_family: "range_snapshot",
  categories_col: "行业",
  min_col: "区间下沿",
  max_col: "区间上沿",
  average_col: "历史均值",
  current_col: "当前值",
  rows,
};

const outDir = path.resolve(__dirname, "..", "demo_output");
renderRangeSnapshotPptx({ ...base, orientation: "vertical" }, path.join(outDir, "range_snapshot_vertical_demo.pptx"));
renderRangeSnapshotPptx({ ...base, orientation: "horizontal" }, path.join(outDir, "range_snapshot_horizontal_demo.pptx"));
renderRangeSnapshotPptx(
  { ...base, orientation: "vertical", axis_break: { enabled: true, min: 60, max: 100 } },
  path.join(outDir, "range_snapshot_axis_break_demo.pptx"),
);
console.log("demo pptx files generated.");

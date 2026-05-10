# Node/TS OOXML renderer POC 设计说明（range_snapshot）

> 状态：POC，仅用于验证 Node/TS 是否可复刻 Python 的 raw OOXML 路线。

## 1) Python 当前 render chain（对齐目标）

当前 `pptchartengine` Python 路线是混合模式：

1. 先用 `python-pptx` bootstrap chart part + embedded workbook。
2. 再直接改 chart OOXML（plotArea / axis / series）。
3. 同步 embedded workbook 数据。
4. 写入隐藏 metadata sheet。
5. parser 解析时优先恢复 metadata + workbook，保证语义 round-trip。

本 POC 在 Node/TS 端保持同样思路：**模板引导 + OOXML改写 + workbook改写 + metadata + parse/inspect**。

## 2) range_snapshot semantic contract（本 POC 定义）

`chart_family = range_snapshot`，输入字段：

- `categories_col`
- `min_col`
- `max_col`
- `average_col`
- `current_col`
- `orientation` (`vertical` / `horizontal`)
- `axis_break` (可选，POC 为语义字段 + 轴范围注入)
- `rows`（语义行数据）

输出要求：

- 生成可打开 `.pptx`
- 图表为原生 chart（非图片）
- embedded workbook 可编辑
- metadata 可被 parse 恢复

## 3) Node/TS 映射方案

- 新增独立目录 `node_renderer/`，不改 Python 包结构。
- 使用 `node_renderer/templates/range_snapshot_template.pptx` 作为 bootstrap 模板。
- 渲染时：
  - 改 `ppt/charts/chart1.xml`：
    - `c:barDir` 切换 vertical/horizontal
    - 重写 `c:ser` 中 `c:cat/c:numRef` 的缓存数据
    - 当有 `axis_break` 时写入 value axis `c:min/c:max`
  - 改 embedded workbook：
    - 主数据表写 categories/min/max/average/current
    - 新建隐藏 `_pptchartengine_meta` sheet 写语义元数据
- parse/inspect：直接读 metadata sheet 并恢复语义结构。

## 4) POC 边界

- 仅覆盖 `range_snapshot` family。
- 不迁移 combo/waterfall/scatter/bubble。
- 不做 Python 主实现替换。
- `axis_break` 仅实现结构级最小支持（metadata + 轴范围注入），不是完整视觉断轴算法。

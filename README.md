# pptchartengine

`pptchartengine` 是一个面向金融研究与报告场景的底层 **可编辑 PowerPoint 图表引擎**。它的目标不是“把数据画成一张图”，而是：

- 生成原生可编辑 `.pptx` 图表，而不是截图或图片嵌入
- 让图表在 PowerPoint 里仍然保持可选中、可改色、可改字、可继续编辑
- 在生成后保留足够语义信息，支持从图表反向恢复配置和数据结构

这个仓库的成熟核心仍然是图表内核与图表级 round-trip；此外还包含一层**仍在扩展中的 semantic component layer**，用于承接单页内的 panel / matrix / chart+table 复合组件。跨页编排、模板替换、连接器、作业声明、CLI 工作流仍然由上层仓库 `pptfi` 负责。

## 仓库定位

### `pptchartengine` 负责什么

- editable chart primitives
- 图表级布局、样式、日期轴、双轴控制
- 语义 metadata 写入与 round-trip 解析
- 金融报告常见图族
- 实验性的单页 semantic component / panel family

### `pptchartengine` 不负责什么

- 跨页/模板级页面编排
- 数据源连接和抽取
- job schema / render pipeline / CLI 命令行入口
- 模板替换、批量渲染、报告 QA

### 与 `pptfi` 的边界

| 仓库 | 角色 | 典型内容 |
| --- | --- | --- |
| `pptchartengine` | 图表中心的 Python SDK | `create_*_chart()`、`parse_*()`、layout/style/date-axis、metadata round-trip、实验性 semantic component |
| `pptfi` | 上层解决方案仓库 | CLI、connectors、composer、job 规范、模板工作流、报告级装配 |

如果你要的是“给一页或一张图加一个可编辑图表能力”，先看这里；如果你要的是“从数据源到整份 PPT 报告的完整流水线”，应该去看 `pptfi`。

## 核心设计原则

### 1. Native editable first

优先输出 PowerPoint 原生图表、形状和表格对象，而不是图片。

### 2. Round-trip first

生成端会把语义信息写入嵌入 workbook 的隐藏元数据 sheet；解析端优先读取 metadata，而不是完全依赖 XML 猜测。目标是让“生成后再解析回来继续改”成为一条可行路径。

### 3. Business semantics on top of geometry

底层几何图元仍然是 combo / waterfall / scatter / bubble 等标准能力，但在其上又加了一层 `semantic_family`，把基金报告里更接近业务语言的页面结构映射到这些几何能力。当前这层对单图 family 已经比较清楚，对 panel / matrix / chart+table 复合组件仍然属于扩展中能力。

### 4. Finance-report oriented, not generic chart zoo

这个引擎优先服务金融分析与养老金报告场景，不追求覆盖所有 PowerPoint 图表类型。

## 能力地图

### 基础图族

| 图族 | 主入口 | 说明 |
| --- | --- | --- |
| Combo | `create_combo_chart()` | `bar / line / area` 组合、双轴、stacked、percent-stacked、日期轴 |
| Waterfall | `create_waterfall_chart()` | editable stacked bridge、总计/小计、connector line、round-trip |
| Scatter | `create_scatter_chart()` | 独立散点图，支持反向恢复 `x/y` 语义 |
| Bubble | `create_bubble_chart()` | 独立气泡图，支持反向恢复 `x/y/size` 语义 |

### 扩展图族

| 图族 | 主入口 | 说明 |
| --- | --- | --- |
| Range Snapshot | `create_range_snapshot_chart()` | 估值区间快照，支持 min/max/average/current、横竖版、轴断裂、overlay、round-trip |

### 语义 family 层

`semantic_family` 面向类似 `demo01.html` 的金融分析看板和事实卡片，把业务语义映射到已有底层几何能力或表格/shape 组合。它更接近“单页 semantic component API”，不是完整报告编排器。

| Family | 基底能力 | 说明 |
| --- | --- | --- |
| `performance_compare` | combo | 基金与基准/同类/中位数的时序比较 |
| `distribution_plus_history` | combo | 某时点构成分布或历史配置变化 |
| `style_box` | scatter | 二维风格定位箱体 |
| `style_allocation` | combo | 风格桶配置比例 / 超配比例 |
| `factor_exposure` | combo | 因子暴露对比与历史演化 |
| `score_overlay` | combo | 原值叠加分位或相对得分 |
| `concentration` | combo | 集中度与相对得分 |
| `event_timeline` | combo + overlay | 时序主图叠加事件带/阶段带 |
| `attribution_decomposition` | waterfall | 收益来源 / 贡献拆解 |
| `ranked_tile_matrix` | shapes | 排名/配比 tile 矩阵 |
| `heatmap_matrix` | shapes | heatmap 矩阵 |
| `table_plus_chart_composite` | chart + table | 左图右表复合卡片 |
| `factor_attribution_panel` | chart + panel | 左图右侧解释面板 |
| `regime_table_panel` | event chart + table | 阶段图 + 区间收益表 |
| `manager_timeline_profile` | profile + compare chart | 基金经理任职画像 + 对比 |
| `award_timeline_panel` | table / empty state | 获奖记录面板 |
| `selection_timing_grid` | judgment grid | 选股/择时多周期判断栅格 |
| `dual_chart_panel` | chart + chart | 左右双图并排 |
| `holding_detail` | table / detail | 持仓明细、债券明细、基金明细面板 |

主入口：

- `create_semantic_chart()`
- `list_semantic_families()`
- `get_semantic_chart_spec()`
- `parse_semantic_chart_from_layout_info()`

## 公开 API 速览

### 创建端

- `create_combo_chart()`
- `create_waterfall_chart()`
- `create_scatter_chart()`
- `create_bubble_chart()`
- `create_range_snapshot_chart()`
- `create_semantic_chart()`

### 解析端

- `parse_chart_from_pptx()`
- `parse_all_charts_from_pptx()`
- `parse_waterfall_chart()`
- `parse_waterfall_from_pptx()`
- `parse_scatter_chart()`
- `parse_scatter_from_pptx()`
- `parse_bubble_chart()`
- `parse_bubble_from_pptx()`
- `parse_range_snapshot_chart()`
- `parse_range_snapshot_from_pptx()`

### 语义辅助

- `prepare_waterfall_dataframe()`
- `restore_waterfall_dataframe()`
- `prepare_range_snapshot_dataframe()`
- `restore_range_snapshot_dataframe()`
- `get_waterfall_spec()`
- `get_range_snapshot_spec()`
- `list_semantic_families()`
- `get_semantic_chart_spec()`

### 预设与配置

- `CHART_PRESET_FUNCTIONS`
- `FINANCE_PRESET_FUNCTIONS`
- `RANGE_SNAPSHOT_PRESET_FUNCTIONS`
- `VERTICAL_VALUATION_PRESET_FUNCTIONS`
- `DateAxisConfig`
- `ChartLayoutConfig`
- `StyleConfig`

## 安装

要求：

- Python `>= 3.10`

安装：

```bash
pip install -e .
```

当前核心依赖：

- `python-pptx>=1.0.2`
- `pandas>=2.2.0`
- `lxml`
- `openpyxl>=3.1.5`

## Quickstart

### 1. Combo 图

```python
import pandas as pd
from pptx import Presentation
from pptchartengine import create_combo_chart

df = pd.DataFrame(
    {
        "年份": [2021, 2022, 2023, 2024],
        "营收": [100, 110, 120, 140],
        "利润": [10, 12, 15, 18],
    }
)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

create_combo_chart(
    slide=slide,
    df=df,
    categories_col="年份",
    series_config=[
        {"key": "营收", "name": "营收(亿元)", "type": "bar", "axis": "primary"},
        {"key": "利润", "name": "利润(亿元)", "type": "line", "axis": "secondary"},
    ],
)

prs.save("combo-demo.pptx")
```

### 2. Waterfall 图

```python
import pandas as pd
from pptx import Presentation
from pptchartengine import create_waterfall_chart

df = pd.DataFrame(
    {
        "阶段": ["期初收益", "权益贡献", "债券贡献", "汇率拖累", "期末收益"],
        "贡献": [8.5, 2.1, 1.3, -1.8, 10.1],
        "度量": ["total", "relative", "relative", "relative", "total"],
    }
)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

create_waterfall_chart(
    slide=slide,
    df=df,
    categories_col="阶段",
    value_col="贡献",
    measure_col="度量",
)

prs.save("waterfall-demo.pptx")
```

### 3. Range Snapshot 图

```python
import pandas as pd
from pptx import Presentation
from pptchartengine import create_range_snapshot_chart

df = pd.DataFrame(
    {
        "market": ["China", "EM", "Europe", "U.S."],
        "range_min": [7.8, 7.5, 8.2, 10.2],
        "range_max": [24.5, 18.1, 19.7, 22.7],
        "average": [11.2, 11.7, 13.1, 16.0],
        "current": [13.8, 14.0, 14.6, 22.7],
    }
)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

create_range_snapshot_chart(
    slide=slide,
    df=df,
    categories_col="market",
    min_col="range_min",
    max_col="range_max",
    average_col="average",
    current_col="current",
    orientation="vertical",
)

prs.save("range-snapshot-demo.pptx")
```

### 4. Semantic Family 图

```python
import pandas as pd
from pptx import Presentation
from pptchartengine import PERFORMANCE_COMPARE_FAMILY, create_semantic_chart

df = pd.DataFrame(
    {
        "日期": pd.date_range("2025-01-01", periods=5, freq="ME"),
        "基金": [0.01, 0.03, 0.02, 0.04, 0.06],
        "沪深300": [0.00, 0.01, 0.015, 0.02, 0.03],
    }
)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

create_semantic_chart(
    slide=slide,
    family=PERFORMANCE_COMPARE_FAMILY,
    df=df,
    categories_col="日期",
    series_entries=[
        {"key": "基金", "name": "基金", "role": "fund", "type": "line"},
        {"key": "沪深300", "name": "沪深300", "role": "benchmark", "type": "line"},
    ],
    title="绩效对比",
)

prs.save("semantic-performance-demo.pptx")
```

### 5. Round-trip 解析

```python
from pptchartengine import parse_chart_from_pptx

chart_df, series_config, chart_type, layout_info = parse_chart_from_pptx("combo-demo.pptx")

print(chart_type)
print(series_config)
print(layout_info)
```

对 `range_snapshot` 也可以直接解析为更高层语义结果：

```python
from pptchartengine import parse_range_snapshot_from_pptx

result = parse_range_snapshot_from_pptx("range-snapshot-demo.pptx")

print(result.categories_col)
print(result.df.head())
print(result.orientation)
```

## Range Snapshot 说明

`range_snapshot` 用于“历史区间 + 当前值 + 均值”的估值快照类页面，典型字段是：

- 分类维度：`categories_col`
- 区间下界：`min_col`
- 区间上界：`max_col`
- 历史均值：`average_col`
- 当前值：`current_col`

当前支持：

- `vertical` / `horizontal`
- average tick overlays
- current marker / current label overlays
- axis break 压缩
- 语义 round-trip

相关接口：

- `build_range_snapshot_preset()`
- `create_range_snapshot_chart()`
- `prepare_range_snapshot_dataframe()`
- `restore_range_snapshot_dataframe()`
- `get_range_snapshot_spec()`
- `parse_range_snapshot_from_pptx()`

内置预设注册表：

- `RANGE_SNAPSHOT_PRESET_FUNCTIONS`
  - `估值快照 - 全市场竖版`
  - `估值快照 - 行业竖版带轴断裂`
- `VERTICAL_VALUATION_PRESET_FUNCTIONS`
  - `ASX 200 valuation`
  - `S&P 500 valuation`
  - `MSCI EMU valuation`
  - `MSCI Japan valuation`

## Round-trip 设计

这是这个仓库最重要的设计原则之一。

生成端会把语义信息写进嵌入 workbook 的隐藏元数据 sheet，解析端会优先读 metadata。目标是恢复：

- `categories_col`
- `series key / name / type / axis / grouping`
- waterfall 的 `value_col / measure_col / totals`
- scatter / bubble 的 `x_col / y_col / size_col`
- range snapshot 的 `min / max / average / current / orientation`
- semantic family 的 `family`、`base_chart_family` 和 family metadata

这意味着图表不是一次性产物，而可以成为可回读、可继承、可再加工的中间资产。

## 当前安全范围

### 相对稳定

- combo 图族中的柱、线、面积组合
- 双轴 financial time-series
- stacked / percent-stacked
- standalone waterfall
- standalone scatter
- standalone bubble
- range snapshot 的基础 round-trip 能力
- metadata 增强的图表解析

### 正在扩展

- semantic family 层
- chart + table / chart + panel / shape matrix 这类复合页面能力
- overlay 与 plot-area 几何估算
- semantic component 的持久化发现与更完整的 round-trip

### 暂未支持或暂不建议

- candlestick / OHLC
- sankey / mekko / tornado
- scatter / bubble 与 bar/line/area 混搭
- scatter 与 bubble 在同一个 `create_combo_chart()` 调用中混用
- 把这个仓库直接当作报告编排器使用

## 测试

```bash
python -m pytest tests/test_package_contract.py
```

当前契约测试主要覆盖：

- 公开导出接口
- financial presets
- combo round-trip
- stacked / percent-stacked round-trip
- waterfall 语义 round-trip
- scatter / bubble round-trip
- range snapshot round-trip
- semantic family registry 与 metadata round-trip

## 目录结构

```text
pptchartengine/
├── src/pptchartengine/
│   ├── __init__.py
│   ├── api.py
│   ├── builder.py
│   ├── cleaner.py
│   ├── date_axis.py
│   ├── layout.py
│   ├── parser.py
│   ├── plot_area.py
│   ├── presets.py
│   ├── range_snapshot.py
│   ├── scatter.py
│   ├── semantic_family.py
│   ├── styles.py
│   ├── waterfall.py
│   └── oxml/
├── tests/
├── pyproject.toml
└── ISSUES.md
```

## 开发建议

- 新图族优先遵守 `create_* -> metadata -> parse_* -> restore_*` 这一闭环
- 如果只是报告级组合或页面编排，优先放到 `pptfi`，不要把 orchestration 逻辑下沉到这里
- 如果新增的是业务语义入口，优先考虑落在 `semantic_family.py` 或后续拆分出的 family 模块，而不是直接膨胀 `api.py`

## 规划

近期方向见 [ISSUES.md](./ISSUES.md)。

当前优先级大致是：

1. 继续打磨 combo / grouping / dual-axis 稳定性
2. 提升复合图卡与 overlay 的几何一致性
3. 继续沉淀 `semantic_family`，并在后续按 family 拆模块
4. 扩展更多金融报告高频图族，而不是盲目扩展图表种类

# pptchartengine

`pptchartengine` 是一个面向金融报告场景的 **可编辑 PowerPoint 图表引擎**。它专注于：

- 生成原生可编辑 `.pptx` 图表，而不是截图或图片嵌入
- 支持常见金融分析图族的程序化生成
- 支持从生成后的图表反向恢复语义配置，形成 round-trip 能力

这个仓库是底层图表内核，不负责整份报告编排、模板替换、数据连接器或 CLI 工作流；这些由上层仓库 `pptfi` 负责。

## 当前能力

### 1. Combo 图族

- `bar / line / area`
- `primary / secondary` 双轴
- `clustered / stacked / percent_stacked`
- 日期轴控制与预设
- 图表样式与布局配置

主入口：

- `create_combo_chart()`

### 2. Waterfall 图族

- 基于 editable stacked bridge 的瀑布桥图
- 支持正负贡献、总计 / 小计
- 支持 connector line 与 value labels
- 支持语义 round-trip

主入口：

- `create_waterfall_chart()`
- `prepare_waterfall_dataframe()`
- `parse_waterfall_chart()`
- `parse_waterfall_from_pptx()`

### 3. Scatter / Bubble 图族

- standalone scatter chart
- standalone bubble chart
- 支持从图表反向恢复 `x/y/size` 语义

主入口：

- `create_scatter_chart()`
- `create_bubble_chart()`
- `parse_scatter_chart()`
- `parse_scatter_from_pptx()`
- `parse_bubble_chart()`
- `parse_bubble_from_pptx()`

## 当前安全范围

### 稳定可用

- combo 图族中的柱、线、面积组合
- 双轴 financial time-series
- stacked / percent-stacked
- standalone waterfall
- standalone scatter
- standalone bubble
- 元数据增强的 round-trip 解析

### 暂未支持或暂不建议

- candlestick / OHLC
- sankey / mekko / tornado
- scatter / bubble 与 bar/line/area 混搭
- scatter 与 bubble 在同一个 `create_combo_chart()` 调用中混用

## 安装

```bash
pip install -e .
```

依赖见 [pyproject.toml](./pyproject.toml)。

## Quickstart

### Combo

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

### Waterfall

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

### Scatter

```python
import pandas as pd
from pptx import Presentation
from pptchartengine import create_scatter_chart

df = pd.DataFrame(
    {
        "波动率": [8.1, 9.2, 7.4],
        "收益率": [10.5, 12.0, 8.8],
    }
)

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

create_scatter_chart(
    slide=slide,
    df=df,
    x_col="波动率",
    y_col="收益率",
    series_name="风险收益分布",
)

prs.save("scatter-demo.pptx")
```

## Round-trip 设计

这是这个仓库最重要的设计原则之一：

- 生成端会把语义信息写进嵌入 workbook 的隐藏元数据 sheet
- 解析端优先读元数据，而不是只靠 XML 猜测
- 目标是恢复：
  - `categories_col`
  - `series key / name / type / axis / grouping`
  - waterfall 的 `value_col / measure_col / totals`
  - scatter / bubble 的 `x_col / y_col / size_col`

这让 “生成后再解析回来继续改” 成为可行路径。

## 测试

```bash
python -m pytest tests/test_package_contract.py
```

当前测试覆盖：

- 公开导出接口
- financial presets
- combo round-trip
- stacked / percent-stacked round-trip
- waterfall 语义 round-trip
- scatter / bubble round-trip

## 仓库结构

```text
pptchartengine/
├── src/pptchartengine/
│   ├── api.py
│   ├── builder.py
│   ├── cleaner.py
│   ├── date_axis.py
│   ├── layout.py
│   ├── parser.py
│   ├── presets.py
│   ├── scatter.py
│   ├── styles.py
│   ├── waterfall.py
│   └── oxml/
├── tests/
├── pyproject.toml
└── ISSUES.md
```

## 规划

近期方向见 [ISSUES.md](./ISSUES.md)。

当前优先级：

1. 继续打磨 combo / grouping 稳定性
2. 提升 waterfall 的报告级视觉质量
3. 扩展 scatter / bubble 的上层工作流支持
4. 下一重图族优先考虑 candlestick / OHLC

## Node/TS OOXML POC

仓库新增了独立目录 `node_renderer/`，用于验证 Node/TS 是否能复刻 Python 的 raw OOXML 路线（当前仅 `range_snapshot` family，POC 状态）。

详见：

- `docs/node_range_snapshot_poc_design.md`
- `node_renderer/README.md`

# node_renderer (POC)

Node OOXML renderer POC for `range_snapshot` family.

## Scope

- ✅ chart_family: `range_snapshot`
- ✅ orientation: `vertical`, `horizontal`
- ✅ `axis_break` semantic metadata + axis min/max injection
- ✅ editable native PPT chart output
- ✅ embedded workbook + hidden metadata
- ✅ minimal parse/inspect
- ❌ not a production-complete renderer

## Design alignment with Python

POC still follows Python route:

1. template bootstrap chart part + embedded workbook
2. direct chart XML rewrite (`ppt/charts/chart1.xml`)
3. direct embedded workbook rewrite (`ppt/embeddings/*.xlsx`)
4. hidden metadata sheet write (`_pptchartengine_meta`)
5. parse/inspect from metadata

## Demo

```bash
cd node_renderer
npm run demo
```

Will generate:

- `demo_output/range_snapshot_vertical_demo.pptx`
- `demo_output/range_snapshot_horizontal_demo.pptx`
- `demo_output/range_snapshot_axis_break_demo.pptx`

Template `templates/range_snapshot_template.pptx` is auto-generated at runtime and is intentionally git-ignored.

## Test

```bash
cd node_renderer
npm test
```

Tests are structural validation only (XML/workbook/metadata/parse). Opening/editing in local PowerPoint still required for full manual verification.

## Evidence

```bash
python scripts/inspect_range_snapshot.py --pptx demo_output/range_snapshot_axis_break_demo.pptx
```

Unzip + parse evidence is stored under `node_renderer/evidence/`.

PowerPoint real-machine screenshot/PDF/PNG export is not included in this environment due missing Microsoft PowerPoint / conversion tools.

# Evidence for range_snapshot Node POC

This folder stores structural evidence from generated demo PPTX files.

- `*.chart.xml.snippet.txt`: extracted `ppt/charts/chart1.xml` snippets
- `*.chart.rels.txt`: extracted `ppt/charts/_rels/chart1.xml.rels`
- `*.embedded.workbook.xml.txt`: extracted embedded workbook `xl/workbook.xml`
- `*.embedded.workbook.rels.txt`: extracted embedded workbook rels
- `*.embedded.sheet1.snippet.txt`: extracted workbook `Sheet1` data sheet
- `*.embedded.sheet2.metadata.txt`: extracted hidden metadata sheet (`_pptchartengine_meta`)
- `parse_*.json`: parse/inspect outputs for generated demos

Note: this environment does not have Microsoft PowerPoint or PDF/PNG conversion tooling, so only structural evidence is included here.

import argparse
import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET

C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
S_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _build_str_cache(parent, formula, values):
    str_ref = ET.SubElement(parent, f"{{{C_NS}}}strRef")
    ET.SubElement(str_ref, f"{{{C_NS}}}f").text = formula
    cache = ET.SubElement(str_ref, f"{{{C_NS}}}strCache")
    ET.SubElement(cache, f"{{{C_NS}}}ptCount", {"val": str(len(values))})
    for i, v in enumerate(values):
        pt = ET.SubElement(cache, f"{{{C_NS}}}pt", {"idx": str(i)})
        ET.SubElement(pt, f"{{{C_NS}}}v").text = str(v)


def _build_num_cache(parent, formula, values):
    num_ref = ET.SubElement(parent, f"{{{C_NS}}}numRef")
    ET.SubElement(num_ref, f"{{{C_NS}}}f").text = formula
    cache = ET.SubElement(num_ref, f"{{{C_NS}}}numCache")
    ET.SubElement(cache, f"{{{C_NS}}}formatCode").text = "General"
    ET.SubElement(cache, f"{{{C_NS}}}ptCount", {"val": str(len(values))})
    for i, v in enumerate(values):
        pt = ET.SubElement(cache, f"{{{C_NS}}}pt", {"idx": str(i)})
        ET.SubElement(pt, f"{{{C_NS}}}v").text = str(v)


def _replace_series_cache(ser, categories, values, col_letter):
    cat = ser.find(f"{{{C_NS}}}cat")
    cat.clear()
    _build_str_cache(cat, f"Sheet1!$A$2:$A${len(categories)+1}", categories)

    val = ser.find(f"{{{C_NS}}}val")
    val.clear()
    _build_num_cache(val, f"Sheet1!${col_letter}$2:${col_letter}${len(values)+1}", values)


def _update_chart(chart_xml, spec):
    ET.register_namespace("c", C_NS)
    root = ET.fromstring(chart_xml)
    root.find(f".//{{{C_NS}}}barDir").set("val", "bar" if spec["orientation"] == "horizontal" else "col")

    categories = [r["category"] for r in spec["rows"]]
    mins = [r["min"] for r in spec["rows"]]
    maxs = [r["max"] for r in spec["rows"]]

    series = root.findall(f".//{{{C_NS}}}barChart/{{{C_NS}}}ser")
    _replace_series_cache(series[0], categories, mins, "B")
    _replace_series_cache(series[1], categories, maxs, "C")

    axis_break = spec.get("axis_break")
    if axis_break and axis_break.get("enabled"):
        scaling = root.find(f".//{{{C_NS}}}valAx/{{{C_NS}}}scaling")
        scaling.clear()
        ET.SubElement(scaling, f"{{{C_NS}}}min", {"val": str(axis_break["min"])})
        ET.SubElement(scaling, f"{{{C_NS}}}max", {"val": str(axis_break["max"])})

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _col(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _set_cell_inline(row_elem, ref, text):
    c = ET.SubElement(row_elem, f"{{{S_NS}}}c", {"r": ref, "t": "inlineStr"})
    is_elem = ET.SubElement(c, f"{{{S_NS}}}is")
    ET.SubElement(is_elem, f"{{{S_NS}}}t").text = str(text)


def _set_cell_num(row_elem, ref, val):
    c = ET.SubElement(row_elem, f"{{{S_NS}}}c", {"r": ref})
    ET.SubElement(c, f"{{{S_NS}}}v").text = str(val)


def _build_sheet1(spec):
    ws = ET.Element(f"{{{S_NS}}}worksheet", {"xmlns:r": R_NS})
    row_count = len(spec["rows"]) + 1
    ET.SubElement(ws, f"{{{S_NS}}}dimension", {"ref": f"A1:E{row_count}"})
    sheet_views = ET.SubElement(ws, f"{{{S_NS}}}sheetViews")
    ET.SubElement(sheet_views, f"{{{S_NS}}}sheetView", {"tabSelected": "1", "workbookViewId": "0"})
    ET.SubElement(ws, f"{{{S_NS}}}sheetFormatPr", {"defaultRowHeight": "15"})
    sheet_data = ET.SubElement(ws, f"{{{S_NS}}}sheetData")

    header = ET.SubElement(sheet_data, f"{{{S_NS}}}row", {"r": "1", "spans": "1:5"})
    headers = [spec["categories_col"], spec["min_col"], spec["max_col"], spec["average_col"], spec["current_col"]]
    for i, h in enumerate(headers, start=1):
        _set_cell_inline(header, f"{_col(i)}1", h)

    for idx, row in enumerate(spec["rows"], start=2):
        r = ET.SubElement(sheet_data, f"{{{S_NS}}}row", {"r": str(idx), "spans": "1:5"})
        _set_cell_inline(r, f"A{idx}", row["category"])
        _set_cell_num(r, f"B{idx}", row["min"])
        _set_cell_num(r, f"C{idx}", row["max"])
        _set_cell_num(r, f"D{idx}", row["average"])
        _set_cell_num(r, f"E{idx}", row["current"])

    ET.SubElement(ws, f"{{{S_NS}}}pageMargins", {
        "left": "0.7", "right": "0.7", "top": "0.75", "bottom": "0.75", "header": "0.3", "footer": "0.3"
    })
    return ET.tostring(ws, encoding="utf-8", xml_declaration=True)


def _build_meta_sheet(spec):
    ws = ET.Element(f"{{{S_NS}}}worksheet")
    ET.SubElement(ws, f"{{{S_NS}}}dimension", {"ref": "A1:B10"})
    ET.SubElement(ws, f"{{{S_NS}}}sheetViews")
    ET.SubElement(ws, f"{{{S_NS}}}sheetFormatPr", {"defaultRowHeight": "15"})
    sheet_data = ET.SubElement(ws, f"{{{S_NS}}}sheetData")
    kv = [
        ("schema_version", "1"),
        ("chart_family", spec["chart_family"]),
        ("categories_col", spec["categories_col"]),
        ("min_col", spec["min_col"]),
        ("max_col", spec["max_col"]),
        ("average_col", spec["average_col"]),
        ("current_col", spec["current_col"]),
        ("orientation", spec["orientation"]),
        ("axis_break", json.dumps(spec.get("axis_break"))),
        ("rows_json", json.dumps(spec["rows"], ensure_ascii=False)),
    ]
    for i, (k, v) in enumerate(kv, start=1):
        row = ET.SubElement(sheet_data, f"{{{S_NS}}}row", {"r": str(i), "spans": "1:2"})
        _set_cell_inline(row, f"A{i}", k)
        _set_cell_inline(row, f"B{i}", v)
    return ET.tostring(ws, encoding="utf-8", xml_declaration=True)


def _update_xlsx(xlsx_bytes, spec):
    zin = zipfile.ZipFile(io := __import__('io').BytesIO(xlsx_bytes), "r")
    blobs = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    blobs["xl/worksheets/sheet1.xml"] = _build_sheet1(spec)
    blobs["xl/worksheets/sheet2.xml"] = _build_meta_sheet(spec)
    blobs.pop("xl/sharedStrings.xml", None)

    wb = ET.fromstring(blobs["xl/workbook.xml"])
    sheets = wb.find(f"{{{S_NS}}}sheets")
    existing = sheets.find(f"{{{S_NS}}}sheet[@name='_pptchartengine_meta']")
    if existing is None:
        ET.SubElement(sheets, f"{{{S_NS}}}sheet", {"name": "_pptchartengine_meta", "sheetId": "2", f"{{{R_NS}}}id": "rId5", "state": "hidden"})
    blobs["xl/workbook.xml"] = ET.tostring(wb, encoding="utf-8", xml_declaration=True)

    rels = ET.fromstring(blobs["xl/_rels/workbook.xml.rels"])
    if rels.find(f"{{{PR_NS}}}Relationship[@Id='rId5']") is None:
        ET.SubElement(rels, f"{{{PR_NS}}}Relationship", {
            "Id": "rId5",
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet",
            "Target": "worksheets/sheet2.xml",
        })
    blobs["xl/_rels/workbook.xml.rels"] = ET.tostring(rels, encoding="utf-8", xml_declaration=True)

    ct = ET.fromstring(blobs["[Content_Types].xml"])
    exists = any(el.attrib.get("PartName") == "/xl/worksheets/sheet2.xml" for el in ct.findall(f"{{{CT_NS}}}Override"))
    if not exists:
        ET.SubElement(ct, f"{{{CT_NS}}}Override", {
            "PartName": "/xl/worksheets/sheet2.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml",
        })
    blobs["[Content_Types].xml"] = ET.tostring(ct, encoding="utf-8", xml_declaration=True)

    out = __import__('io').BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in blobs.items():
            zout.writestr(name, data)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--spec-json", required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec_json)

    with zipfile.ZipFile(args.template, "r") as zin:
        blobs = {name: zin.read(name) for name in zin.namelist()}

    blobs["ppt/charts/chart1.xml"] = _update_chart(blobs["ppt/charts/chart1.xml"], spec)
    rels = blobs["ppt/charts/_rels/chart1.xml.rels"].decode("utf-8")
    m = re.search(r'Target="\.\./(embeddings/[^"]+\.xlsx)"', rels)
    workbook_name = "ppt/" + m.group(1)
    blobs[workbook_name] = _update_xlsx(blobs[workbook_name], spec)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in blobs.items():
            zout.writestr(name, data)


if __name__ == "__main__":
    main()

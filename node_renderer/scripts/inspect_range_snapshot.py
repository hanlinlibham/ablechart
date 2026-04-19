import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET

S_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _cell_text(c):
    t = c.attrib.get("t")
    if t == "inlineStr":
        t_elem = c.find(f"{{{S_NS}}}is/{{{S_NS}}}t")
        return t_elem.text if t_elem is not None else ""
    v = c.find(f"{{{S_NS}}}v")
    return v.text if v is not None else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pptx", required=True)
    args = parser.parse_args()

    with zipfile.ZipFile(args.pptx, "r") as z:
        rels = z.read("ppt/charts/_rels/chart1.xml.rels").decode("utf-8")
        m = re.search(r'Target="\.\./(embeddings/[^"]+\.xlsx)"', rels)
        wb_bytes = z.read("ppt/" + m.group(1))

    with zipfile.ZipFile(__import__('io').BytesIO(wb_bytes), "r") as xz:
        meta_xml = xz.read("xl/worksheets/sheet2.xml")

    root = ET.fromstring(meta_xml)
    meta = {}
    for row in root.findall(f".//{{{S_NS}}}row"):
        cells = row.findall(f"{{{S_NS}}}c")
        if len(cells) >= 2:
            meta[_cell_text(cells[0])] = _cell_text(cells[1])

    result = {
        "chart_family": meta.get("chart_family"),
        "categories_col": meta.get("categories_col"),
        "min_col": meta.get("min_col"),
        "max_col": meta.get("max_col"),
        "average_col": meta.get("average_col"),
        "current_col": meta.get("current_col"),
        "orientation": meta.get("orientation"),
        "axis_break": json.loads(meta.get("axis_break") or "null"),
        "rows": json.loads(meta.get("rows_json") or "[]"),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

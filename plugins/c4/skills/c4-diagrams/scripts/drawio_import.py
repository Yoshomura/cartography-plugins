#!/usr/bin/env python3
"""Extract C4 vertices and edges from a draw.io (.drawio / .xml) file as JSON.

Usage: python drawio_import.py diagram.drawio > model.json
Output: {"vertices": [{id, name, type, technology, description, parent, geometry}],
         "edges":    [{id, source, target, description, technology, stroke, width, dashed}]}
The parent field tells you which group (sub-domain) a container belongs to.
Edges whose source or target is null are legend samples: ignore them.
"""
import sys, json, re, html
import xml.etree.ElementTree as ET

def strip(s):
    s = html.unescape(s or "")
    s = re.sub(r"<br\s*/?>", " | ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()

def style(v, key):
    m = re.search(rf"(?:^|;){key}=([^;]+)", v.get("style", ""))
    return m.group(1) if m else None

def load(path):
    root = ET.parse(path).getroot()
    cells, wrapped = {}, set()
    for o in root.iter("object"):
        c = o.find("mxCell")
        if c is None: continue
        wrapped.add(id(c))
        a = dict(o.attrib); a.update(c.attrib)
        g = c.find("mxGeometry"); a["_geo"] = dict(g.attrib) if g is not None else {}
        cells[a["id"]] = a
    for c in root.iter("mxCell"):
        if id(c) in wrapped or c.get("id") in ("0", "1"): continue
        a = dict(c.attrib); g = c.find("mxGeometry"); a["_geo"] = dict(g.attrib) if g is not None else {}
        cells[a["id"]] = a
    def name(k):
        v = cells.get(k)
        if not v: return None
        return v.get("C4Name") or strip(v.get("label") or v.get("value")) or None
    verts = [{
        "id": k, "name": name(k), "type": v.get("C4Type") or None,
        "technology": v.get("C4Technology") or None, "description": strip(v.get("C4Description", "")) or None,
        "parent": name(v.get("parent")) if v.get("parent") != "1" else None,
        "fill": style(v, "fillColor"),
        "geometry": {kk: float(vv) for kk, vv in v["_geo"].items() if kk in ("x", "y", "width", "height")},
    } for k, v in cells.items() if v.get("vertex") == "1" and name(k)]
    edges = [{
        "id": k, "source": name(v.get("source")), "target": name(v.get("target")),
        "description": strip(v.get("C4Description", "")) or None, "technology": v.get("C4Technology") or None,
        "stroke": style(v, "strokeColor"), "width": style(v, "strokeWidth"), "dashed": "dashed=1" in v.get("style", ""),
    } for k, v in cells.items() if v.get("edge") == "1"]
    return {"vertices": verts, "edges": edges}

if __name__ == "__main__":
    json.dump(load(sys.argv[1]), sys.stdout, indent=2, ensure_ascii=False)

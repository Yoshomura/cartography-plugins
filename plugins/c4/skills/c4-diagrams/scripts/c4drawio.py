"""c4drawio: render a c4lib.Doc as an uncompressed draw.io file, same layout as the HTML.

Called by Doc.write_drawio(path). Every primitive the Doc recorded becomes a draw.io cell at the same
coordinates, with the styles of references/notation.md (section "draw.io"):
- cards and buses -> vertices carrying C4Type / C4Name / C4Technology / C4Description, so
  drawio_import.py reads the file back;
- a card inside a sub-domain band is a child of that band, a band inside the system boundary is a
  child of the boundary (drawio_import reports the sub-domain as `parent`);
- routes -> one edge each, waypoints kept, attached to the card its end touches (exit / entry pinned
  on the exact border point, so draw.io keeps the orthogonal path); an end on no card stays free;
- labels, titles, legend, footer -> text cells. Label heights are estimated from the text length,
  draw.io does not auto-size them on load.
"""
import html, math
from xml.sax.saxutils import quoteattr

LINE = "#707070"
PUBLISH = "#D55E00"    # bus lane, element to bus (publish / send)
SUBSCRIBE = "#0072B2"  # bus lane, bus to element (subscribe / receive)
FONT = "Segoe UI,Helvetica,Arial,sans-serif"  # draw.io passes it to CSS font-family
COND = "Arial Narrow,Arial,sans-serif"
FILL = {"person": "#08427B", "system": "#1168BD", "container": "#438DD5", "store": "#438DD5", "external": "#999999"}
CARD = ("rounded=1;absoluteArcSize=1;arcSize=32;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
        f"spacingLeft=14;spacingRight=14;fontFamily={FONT};fontSize=12;fontColor=#FFFFFF;strokeColor=none;shadow=1;")
STORE = ("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=12;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
         f"spacingLeft=14;spacingRight=14;fontFamily={FONT};fontSize=12;fontColor=#FFFFFF;fillColor=#438DD5;strokeColor=#2E6FAD;shadow=1;")
BOUNDARY = ("rounded=1;absoluteArcSize=1;arcSize=56;fillColor=none;dashed=1;fixDash=1;dashPattern=8 6;strokeColor=#444444;"
            "strokeWidth=2;container=1;collapsible=0;html=1;whiteSpace=wrap;align=left;verticalAlign=bottom;spacingLeft=16;"
            f"spacingBottom=10;fontFamily={FONT};fontSize=14;fontColor=#444444;")
SUBDOMAIN = ("rounded=1;absoluteArcSize=1;arcSize=40;fillColor=#E3F2E1;dashed=1;fixDash=1;dashPattern=8 6;strokeColor=#6DAE6D;"
             "strokeWidth=2;container=1;collapsible=0;html=1;whiteSpace=nowrap;align=left;verticalAlign=top;spacingLeft=14;"
             f"spacingTop=-12;labelBackgroundColor=#CDE8CB;fontFamily={FONT};fontSize=12;fontColor=#2E6B2E;")
PILL = ("text;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;rounded=1;absoluteArcSize=1;arcSize=20;"
        f"fillColor=#FFFFFF;strokeColor=#E5E7EB;fontFamily={FONT};fontSize=12;fontColor={LINE};spacing=2;spacingLeft=6;spacingRight=6;")
EDGE = (f"edgeStyle=none;rounded=1;html=1;strokeColor={LINE};strokeWidth=2.5;endFill=1;endSize=6;"
        "exitPerimeter=0;entryPerimeter=0;")
TEXT = "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacing=0;"


def text_width(s, size=12):
    """Rough rendered width of s in px (Segoe UI-like proportions)."""
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!()[]/ ":
            w += 0.28
        elif ch.isupper() or ch in "mwMW@%":
            w += 0.68
        else:
            w += 0.52
    return w * size


def text_lines(s, width, size=12):
    lines, cur = 1, 0.0
    space = text_width(" ", size)
    for word in s.split():
        ww = text_width(word, size)
        if cur and cur + space + ww > width:
            lines, cur = lines + 1, ww
        else:
            cur = cur + space + ww if cur else ww
    return lines


def badge(typ):
    return (f'<span style="font-family:{COND};font-size:11px;letter-spacing:1px;background:rgba(255,255,255,.2);'
            f'border-radius:999px;padding:1px 8px">[{html.escape(typ.upper())}]</span>')


class Writer:
    def __init__(self, doc):
        self.doc, self.cells, self.n = doc, [], 0
        self.frames = []   # (id, l, t, w, h, kind) of boundaries and sub-domains, for containment
        self.cards = []    # (id, l, t, w, h) of cards and buses, for edge attachment

    def nid(self):
        self.n += 1
        return f"c4-{self.n}"

    def vertex(self, l, t, w, h, style, label="", attrs=None, parent="1", origin=(0, 0)):
        i = self.nid()
        geo = f'<mxGeometry x="{l - origin[0]:g}" y="{t - origin[1]:g}" width="{w:g}" height="{h:g}" as="geometry"/>'
        cell = f'<mxCell style={quoteattr(style)} vertex="1" parent="{parent}">{geo}</mxCell>'
        if attrs is not None:
            a = "".join(f" {k}={quoteattr(v)}" for k, v in attrs.items() if v)
            self.cells.append(f'<object id="{i}" label={quoteattr(label)}{a}>{cell}</object>')
        else:
            self.cells.append(cell.replace("<mxCell ", f'<mxCell id="{i}" value={quoteattr(label)} ', 1))
        return i

    def container_of(self, l, t, w, h, kinds):
        best = None
        for fid, fl, ft, fw, fh, kind in self.frames:
            if kind in kinds and fl <= l and ft <= t and l + w <= fl + fw and t + h <= ft + fh:
                if best is None or fw * fh < best[3] * best[4]:
                    best = (fid, fl, ft, fw, fh)
        return ("1", (0, 0)) if best is None else (best[0], (best[1], best[2]))

    def attach(self, x, y):
        for cid, l, t, w, h in self.cards:
            if l - 3 <= x <= l + w + 3 and t - 3 <= y <= t + h + 3:
                on_x = abs(x - l) <= 3 or abs(x - (l + w)) <= 3
                on_y = abs(y - t) <= 3 or abs(y - (t + h)) <= 3
                if on_x or on_y:
                    fx = 0 if abs(x - l) <= 3 else 1 if abs(x - (l + w)) <= 3 else (x - l) / w
                    fy = 0 if abs(y - t) <= 3 else 1 if abs(y - (t + h)) <= 3 else (y - t) / h
                    return cid, round(min(max(fx, 0), 1), 4), round(min(max(fy, 0), 1), 4)
        # no card: an end on a sub-domain border attaches to the sub-domain (another sub-domain drawn
        # as one box in a sub-domain view)
        for cid, l, t, w, h, kind in self.frames:
            if kind != "subdomain" or not (l - 3 <= x <= l + w + 3 and t - 3 <= y <= t + h + 3):
                continue
            on_x = abs(x - l) <= 3 or abs(x - (l + w)) <= 3
            on_y = abs(y - t) <= 3 or abs(y - (t + h)) <= 3
            if on_x or on_y:
                fx = 0 if abs(x - l) <= 3 else 1 if abs(x - (l + w)) <= 3 else (x - l) / w
                fy = 0 if abs(y - t) <= 3 else 1 if abs(y - (t + h)) <= 3 else (y - t) / h
                return cid, round(min(max(fx, 0), 1), 4), round(min(max(fy, 0), 1), 4)
        return None

    # ------------------------------------------------------------------ primitives
    def boundary(self, l, t, w, h, name, typ):
        label = f'<b>{html.escape(name)}</b> <span style="font-family:{COND};font-size:11px;letter-spacing:1px">[{html.escape(typ.upper())}]</span>'
        i = self.vertex(l, t, w, h, BOUNDARY, label, {"C4Type": typ, "C4Name": name})
        self.frames.append((i, l, t, w, h, "boundary"))

    def subdomain(self, l, t, w, h, name):
        parent, origin = self.container_of(l, t, w, h, ("boundary",))
        label = f'<b>{html.escape(name)}</b> <span style="font-family:{COND};font-size:10px;letter-spacing:1px">[SUB-DOMAIN]</span>'
        i = self.vertex(l, t, w, h, SUBDOMAIN, label, {"C4Type": "Sub-domain", "C4Name": name}, parent, origin)
        self.frames.append((i, l, t, w, h, "subdomain"))

    def card(self, l, t, w, h, kind, name, typ, desc):
        parent, origin = self.container_of(l, t, w, h, ("subdomain", "boundary"))
        c4type, _, tech = (typ or "").partition(":")
        label = f'<b style="font-size:16px">{html.escape(name)}</b>' + (f"<br>{badge(typ)}" if typ else "") + (f"<br>{html.escape(desc)}" if desc else "")
        style = STORE if kind == "store" else CARD + f"fillColor={FILL[kind]};"
        attrs = {"C4Type": c4type.strip() or kind.title(), "C4Name": name, "C4Technology": tech.strip(), "C4Description": desc or ""}
        i = self.vertex(l, t, w, h, style, label, attrs, parent, origin)
        self.cards.append((i, l, t, w, h))

    def bus(self, l, t, w, h, name, typ, desc, vertical):
        parent, origin = self.container_of(l, t, w, h, ("subdomain", "boundary"))
        c4type, _, tech = typ.partition(":")
        label = f'<b style="font-size:16px">{html.escape(name)}</b> {badge(typ)} &middot; {html.escape(desc)}'
        style = CARD + "fillColor=#438DD5;" + ("horizontal=0;" if vertical else "")
        attrs = {"C4Type": c4type.strip(), "C4Name": name, "C4Technology": tech.strip(), "C4Description": desc}
        i = self.vertex(l, t, w, h, style, label, attrs, parent, origin)
        self.cards.append((i, l, t, w, h))

    def edge(self, pts, head, dashed, color=LINE):
        style = EDGE.replace(f"strokeColor={LINE};", f"strokeColor={color};") + ("endArrow=blockThin;" if head else "endArrow=none;")
        if dashed:
            style += "dashed=1;fixDash=1;dashPattern=6 6;"
        src, tgt = self.attach(*pts[0]), self.attach(*pts[-1])
        ends = ""
        if src:
            ends += f' source="{src[0]}"'; style += f"exitX={src[1]:g};exitY={src[2]:g};exitDx=0;exitDy=0;"
        if tgt:
            ends += f' target="{tgt[0]}"'; style += f"entryX={tgt[1]:g};entryY={tgt[2]:g};entryDx=0;entryDy=0;"
        way = "".join(f'<mxPoint x="{x:g}" y="{y:g}"/>' for x, y in pts[1:-1])
        geo = (f'<mxGeometry relative="1" as="geometry"><mxPoint x="{pts[0][0]:g}" y="{pts[0][1]:g}" as="sourcePoint"/>'
               f'<mxPoint x="{pts[-1][0]:g}" y="{pts[-1][1]:g}" as="targetPoint"/>' + (f'<Array as="points">{way}</Array>' if way else "") + "</mxGeometry>")
        self.cells.append(f'<mxCell id="{self.nid()}" style={quoteattr(style)} edge="1" parent="1"{ends}>{geo}</mxCell>')

    def label(self, l, t, w, text, border=None, dashed=False):
        """A newline is a line break; a label with bullets ("\n• name") is left-aligned. border /
        dashed: the outline takes the colour and the style of the line the label belongs to."""
        parts = text.split("\n")
        h = sum(text_lines(p, w) for p in parts) * 15 + 6
        style = PILL.replace("align=center;", "align=left;") if len(parts) > 1 else PILL
        if border:
            style = style.replace("strokeColor=#E5E7EB;", f"strokeColor={border};")
        if dashed:
            style += "dashed=1;dashPattern=4 3;"
        self.vertex(l - 6, t - 4, w + 12, h, style, "<br>".join(html.escape(p) for p in parts))

    def title(self, l, t, kicker, title, lead):
        self.vertex(l, t, 900, 18, TEXT + f"fontFamily={COND};fontStyle=1;fontSize=14;fontColor=#1168BD;", html.escape(kicker.upper()))
        self.vertex(l, t + 28, 1400, 40, TEXT + "fontFamily=Arial;fontStyle=1;fontSize=32;fontColor=#111827;", html.escape(title))
        self.vertex(l, t + 78, 760, text_lines(lead, 760, 15) * 20, TEXT + f"fontFamily={FONT};fontSize=15;fontColor=#374151;", html.escape(lead))

    def footer(self, text):
        w = 320
        self.vertex(self.doc.w - 64 - w, self.doc.hh - 48 - 16, w, 16, TEXT + f"align=right;fontFamily=Consolas,monospace;fontSize=12;fontColor=#6B7280;", html.escape(text))

    def legend(self, l, t, items):
        x, y, h = l + 16, t, 36
        parts = []
        parts.append(("text", x, "LEGEND", 60)); x += 60 + 24
        for kind, text in items:
            tw = text_width(text) * 1.1 + 12
            parts.append(("swatch", x, kind, 22)); x += 22 + 8
            parts.append(("text", x, text, tw)); x += tw + 24
        self.vertex(l, t, x - 24 + 16 - l, h, "rounded=1;arcSize=50;fillColor=#FFFFFF;strokeColor=#E5E7EB;html=1;")
        for p in parts:
            if p[0] == "text":
                bold = f"fontFamily={COND};fontStyle=1;fontSize=11;fontColor=#6B7280;" if p[2] == "LEGEND" else f"fontFamily={FONT};fontSize=12;fontColor=#374151;"
                self.vertex(p[1], y + 10, p[3], 16, TEXT + bold, html.escape(p[2]))
            elif p[2] in ("sync", "async", "publish", "subscribe"):
                color = {"publish": PUBLISH, "subscribe": SUBSCRIBE}.get(p[2], LINE)
                st = f"endArrow=none;html=1;strokeColor={color};strokeWidth=2.5;" + ("dashed=1;fixDash=1;dashPattern=6 6;" if p[2] != "sync" else "")
                self.cells.append(f'<mxCell id="{self.nid()}" style={quoteattr(st)} edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                                  f'<mxPoint x="{p[1]}" y="{y + 18}" as="sourcePoint"/><mxPoint x="{p[1] + 22}" y="{y + 18}" as="targetPoint"/></mxGeometry></mxCell>')
            elif p[2] == "boundary":
                self.vertex(p[1], y + 11, 22, 14, "rounded=1;arcSize=30;fillColor=none;dashed=1;strokeColor=#444444;strokeWidth=2;")
            elif p[2] == "subdomain":
                self.vertex(p[1], y + 11, 22, 14, "rounded=1;arcSize=30;fillColor=#E3F2E1;dashed=1;strokeColor=#6DAE6D;strokeWidth=2;")
            else:
                self.vertex(p[1], y + 11, 22, 14, f"rounded=1;arcSize=30;strokeColor=none;fillColor={FILL[p[2]]};")

    # ------------------------------------------------------------------ output
    def render(self):
        rec = self.doc.dio
        # z-order of the HTML: bands, arrows, cards, labels
        for kind in ("boundary", "subdomain"):
            for r in rec:
                if r[0] == kind: getattr(self, kind)(*r[1:])
        for r in rec:
            if r[0] in ("card", "bus"): getattr(self, r[0])(*r[1:])
        for r in rec:
            if r[0] == "edge": self.edge(*r[1:])
        for r in rec:
            if r[0] in ("label", "title", "legend", "footer"): getattr(self, r[0])(*r[1:])
        body = "\n        ".join(self.cells)
        return (f'<mxfile host="c4lib">\n  <diagram id="c4" name={quoteattr(self.doc.ttl)}>\n'
                f'    <mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" '
                f'pageWidth="{self.doc.w}" pageHeight="{self.doc.hh}" background="#FFFFFF" math="0" shadow="0">\n'
                f'      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n        {body}\n      </root>\n'
                f'    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


def render(doc):
    return Writer(doc).render()

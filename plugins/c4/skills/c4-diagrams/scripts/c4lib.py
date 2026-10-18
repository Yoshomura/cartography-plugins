"""c4lib: generate C4 diagrams (Level 1 / Level 2) as HTML and draw.io, in the notation of
references/notation.md.

Classic C4 palette (c4model.com / C4-PlantUML defaults), neutral chrome, green sub-domains,
orthogonal arrows, optional message buses. Two outputs, same layout:
  Doc.write(path)        -> self-contained HTML, system fonts, open in any browser
  Doc.write_drawio(path) -> uncompressed .drawio (scripts/c4drawio.py), editable in draw.io
Output folder: $C4_OUT, else <system temp>/c4-diagrams, never the current directory, so a run
from a repository root leaves no stray folder in the working tree.
"""
import os, tempfile
ROOT = os.environ.get("C4_OUT") or os.path.join(tempfile.gettempdir(), "c4-diagrams")

# chrome (titles, eyebrow, legend frame): neutral greys and the C4 system blue as accent
INK900, INK700, INK500, INK100 = "#111827", "#374151", "#6B7280", "#E5E7EB"
ACCENT, WHITE = "#1168BD", "#FFFFFF"
LINE = "#707070"
PUBLISH = "#D55E00"    # bus lane, element to bus (publish / send)
SUBSCRIBE = "#0072B2"  # bus lane, bus to element (subscribe / receive)
BODY = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
COND = "'Arial Narrow', Arial, sans-serif"
TITLE = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'Courier New', monospace"


class Doc:
    def __init__(self, title, w, h):
        self.ttl, self.w, self.hh = title, w, h
        self.bands, self.arrows, self.cards, self.labels = [], [], [], []
        self.k = 0
        self.dio, self._routing = [], False  # primitives replayed by write_drawio

    def _marker(self, color):
        self.k += 1
        mid = f"dc-arrow-head-filled-{self.k}"
        return mid, (f'<defs><marker id="{mid}" orient="auto" markerWidth="5" markerHeight="5" refX="2" refY="2" overflow="visible">'
                     f'<path d="M0 0.4 L4 2 L0 3.6 Z" fill="{color}" stroke="{color}" stroke-width="0.9" stroke-linejoin="round" style="fill: {color}; fill: context-stroke; stroke: context-stroke"/></marker></defs>')

    def _svg(self, left, top, w, h, path, defs, mid, dashed, color):
        dash = " stroke-dasharray: 6 6;" if dashed else ""
        me = f' marker-end="url(#{mid})"' if mid else ""
        return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; overflow: visible; fill: none; stroke: {color}; stroke-width: 2.5;{dash} stroke-linecap: round; stroke-linejoin: round">'
                f'{defs}<path d="{path}"{me}></path></svg>')

    def route(self, pts, head=True, dashed=False, color=LINE):
        """Orthogonal polyline through pts, head on the last point. One draw.io edge per route.
        A bus lane takes color=PUBLISH (element to bus) or color=SUBSCRIBE (bus to element)."""
        self.dio.append(("edge", list(pts), head, dashed, color))
        self._routing = True
        try:
            for i in range(len(pts) - 1):
                (x1, y1), (x2, y2) = pts[i], pts[i + 1]
                last = i == len(pts) - 2
                if y1 == y2: self.h(x1, x2, y1, head=head and last, dashed=dashed, color=color)
                elif x1 == x2: self.v(x1, y1, y2, head=head and last, dashed=dashed, color=color)
                else: raise ValueError(f"diagonal {pts[i]}->{pts[i+1]}")
        finally:
            self._routing = False

    def h(self, x1, x2, y, head=True, dashed=False, color=LINE):
        """Horizontal segment from x1 to x2 (tip at x2 when head)."""
        if not self._routing: self.dio.append(("edge", [(x1, y), (x2, y)], head, dashed))
        x, n = min(x1, x2), abs(x2 - x1)
        hh = 5 if head else 0
        mid, defs = self._marker(color) if head else (None, "")
        path = f"M 0 4 L {n-hh} 4" if x2 > x1 else f"M {n} 4 L {hh} 4"
        self.arrows.append(self._svg(x, y - 4, n, 8, path, defs, mid, dashed, color))

    def v(self, x, y1, y2, head=True, dashed=False, color=LINE):
        if not self._routing: self.dio.append(("edge", [(x, y1), (x, y2)], head, dashed))
        y, n = min(y1, y2), abs(y2 - y1)
        hh = 5 if head else 0
        mid, defs = self._marker(color) if head else (None, "")
        path = f"M 4 0 L 4 {n-hh}" if y2 > y1 else f"M 4 {n} L 4 {hh}"
        self.arrows.append(self._svg(x - 4, y, 8, n, path, defs, mid, dashed, color))

    def label(self, left, top, width, text, border=None, dashed=False):
        """Relationship label pill. border / dashed: the pill outline takes the colour and the style of
        the line it belongs to (sub-domain views); default: the light grey solid outline."""
        self.dio.append(("label", left, top, width, text, border, dashed))
        align = "left" if "\n" in text else "center"
        text = text.replace("\n", "<br>")
        outline = f"1px {'dashed' if dashed else 'solid'} {border or '#E5E7EB'}"
        self.labels.append(f'<div style="position: absolute; left: {left-6}px; top: {top-4}px; width: {width}px; box-sizing: content-box; padding: 2px 6px; text-align: {align}; background: {WHITE}; border: {outline}; border-radius: 10px; font-family: {BODY}; font-size: 12px; line-height: 15px; color: #707070">{text}</div>')

    def card(self, left, top, w, h, kind, name, typ, desc):
        self.dio.append(("card", left, top, w, h, kind, name, typ, desc))
        styles = {
            "person":    ("#08427B", WHITE, "none"),
            "system":    ("#1168BD", WHITE, "none"),
            "container": ("#438DD5", WHITE, "none"),
            "store":     ("#438DD5", WHITE, "none"),
            "external":  ("#999999", WHITE, "none"),
        }
        bg, fg, border = styles[kind]
        icon = ""
        if kind == "person":
            icon = (f'<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" style="flex: none; fill: none; stroke: {fg}; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round">'
                    '<circle cx="12" cy="8" r="4"></circle><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"></path></svg>')
        if kind == "store":
            icon = (f'<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" style="flex: none; fill: none; stroke: {fg}; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round">'
                    '<ellipse cx="12" cy="5" rx="8" ry="3"></ellipse><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"></path><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"></path></svg>')
        sub = "" if not typ else f'<br><span style="display: inline-block; margin: 3px 0 2px; padding: 1px 8px; border-radius: 999px; background: rgba(255,255,255,.2); font-family: {COND}; font-size: 11px; line-height: 14px; letter-spacing: .08em; text-transform: uppercase">[{typ}]</span>'
        d = f"<br>{desc}" if desc else ""
        self.cards.append(
            f'<div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; box-sizing: border-box; padding: 10px 14px; display: flex; flex-direction: column; gap: 6px; align-items: center; justify-content: center; text-align: center; '
            f'background: {bg}; color: {fg}; border: {border}; border-radius: 16px; box-shadow: 0 6px 16px rgba(17, 24, 39, .14), 0 1px 2px rgba(17, 24, 39, .08); font-family: {BODY}; font-size: 12px; line-height: 15px">'
            f'{icon}<span><b style="font-size: 16px; line-height: 20px">{name}</b>{sub}{d}</span></div>')

    def bus(self, left, top, w, h, name, typ, desc, vertical=False):
        """Message bus band (private: horizontal, inside the boundary; public: vertical, outside)."""
        self.dio.append(("bus", left, top, w, h, name, typ, desc, vertical))
        inner = (f'<span><b style="font-size: 16px; line-height: 20px">{name}</b> <span style="display: inline-block; padding: 1px 8px; border-radius: 999px; background: rgba(255,255,255,.2); font-family: {COND}; font-size: 11px; letter-spacing: .08em; text-transform: uppercase">[{typ}]</span> &middot; {desc}</span>')
        extra = "writing-mode: vertical-rl; transform: rotate(180deg); " if vertical else ""
        self.cards.append(f'<div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; box-sizing: border-box; padding: 0 20px; display: flex; align-items: center; justify-content: center; {extra}background: #438DD5; color: {WHITE}; border-radius: 16px; box-shadow: 0 6px 16px rgba(17, 24, 39, .14), 0 1px 2px rgba(17, 24, 39, .08); font-family: {BODY}; font-size: 12px; line-height: 15px">{inner}</div>')

    def boundary(self, left, top, w, h, name, typ):
        self.dio.append(("boundary", left, top, w, h, name, typ))
        self.bands.append(f'<div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; box-sizing: border-box; border: 2px dashed #444444; border-radius: 28px"></div>')
        self.labels.append(f'<div style="position: absolute; left: {left+16}px; top: {top+h-36}px; font-family: {BODY}; font-size: 14px; line-height: 20px; color: #444444"><b>{name}</b> <span style="font-family: {COND}; font-size: 11px; letter-spacing: .08em; text-transform: uppercase">[{typ}]</span></div>')

    def subdomain(self, left, top, w, h, name):
        self.dio.append(("subdomain", left, top, w, h, name))
        self.bands.append(f'<div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; box-sizing: border-box; background: #E3F2E1; border: 2px dashed #6DAE6D; border-radius: 20px"></div>')
        self.labels.append(f'<div style="position: absolute; left: {left+14}px; top: {top-10}px; padding: 2px 10px; border-radius: 999px; background: #CDE8CB; font-family: {BODY}; font-size: 12px; line-height: 16px; color: #2E6B2E"><b>{name}</b> <span style="font-family: {COND}; font-size: 10px; letter-spacing: .08em; text-transform: uppercase">[Sub-domain]</span></div>')

    def title(self, left, top, kicker, title, lead):
        self.dio.append(("title", left, top, kicker, title, lead))
        self.labels.append(f'<div style="position: absolute; left: {left}px; top: {top}px; font-family: {COND}; font-weight: 700; font-size: 14px; line-height: 16px; letter-spacing: .12em; text-transform: uppercase; color: {ACCENT}">{kicker}</div>')
        self.labels.append(f'<div style="position: absolute; left: {left}px; top: {top+28}px; font-family: {TITLE}; font-weight: 700; font-size: 32px; line-height: 38px; letter-spacing: -.01em; color: {INK900}">{title}</div>')
        self.labels.append(f'<div style="position: absolute; left: {left}px; top: {top+78}px; width: 760px; font-family: {BODY}; font-size: 15px; line-height: 20px; color: {INK700}">{lead}</div>')

    def legend(self, left, top, items):
        self.dio.append(("legend", left, top, list(items)))
        sw = []
        for kind, text in items:
            if kind == "boundary":
                box = f'<span style="display: inline-block; width: 22px; height: 14px; box-sizing: border-box; border: 2px dashed #444444; border-radius: 5px"></span>'
            elif kind == "subdomain":
                box = f'<span style="display: inline-block; width: 22px; height: 14px; box-sizing: border-box; background: #E3F2E1; border: 2px dashed #6DAE6D; border-radius: 5px"></span>'
            elif kind == "sync":
                box = f'<span style="display: inline-block; width: 22px; height: 0; border-top: 2.5px solid {LINE}; border-radius: 2px"></span>'
            elif kind == "async":
                box = f'<span style="display: inline-block; width: 22px; height: 0; border-top: 2.5px dashed {LINE}"></span>'
            elif kind in ("publish", "subscribe"):
                c = PUBLISH if kind == "publish" else SUBSCRIBE
                box = f'<span style="display: inline-block; width: 22px; height: 0; border-top: 2.5px dashed {c}"></span>'
            else:
                bg = {"person": "#08427B", "system": "#1168BD", "container": "#438DD5", "store": "#438DD5", "external": "#999999"}[kind]
                br = "none"
                box = f'<span style="display: inline-block; width: 22px; height: 14px; box-sizing: border-box; background: {bg}; border: {br}; border-radius: 5px"></span>'
            sw.append(f'<span style="display: inline-flex; align-items: center; gap: 8px">{box}{text}</span>')
        self.labels.append(f'<div style="position: absolute; left: {left}px; top: {top}px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px 24px; padding: 10px 16px; border: 1px solid {INK100}; border-radius: 999px; background: {WHITE}; font-family: {BODY}; font-size: 12px; line-height: 16px; color: {INK700}">'
                           f'<span style="font-family: {COND}; font-weight: 700; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: {INK500}">Legend</span>{"".join(sw)}</div>')

    def footer(self, text):
        self.dio.append(("footer", text))
        self.labels.append(f'<div style="position: absolute; right: 64px; bottom: 48px; font-family: {MONO}; font-size: 12px; line-height: 16px; letter-spacing: .04em; color: {INK500}">{text}</div>')

    def write(self, path):
        """Self-contained HTML page in ROOT."""
        body = f'<div style="position: relative; width: {self.w}px; height: {self.hh}px; background: {WHITE}; font-family: {BODY}; color: {INK900}">\n'
        body += "\n".join(self.bands + self.arrows + self.cards + self.labels)
        body += "\n</div>\n"
        html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{self.ttl}</title>'
                f'<style>body{{margin:0;background:#F3F4F6}}</style></head><body>{body}</body></html>')
        os.makedirs(ROOT, exist_ok=True)
        with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
            f.write(html)
        return os.path.join(ROOT, path)

    def write_drawio(self, path):
        """Same diagram as an uncompressed .drawio file in ROOT (see scripts/c4drawio.py)."""
        from c4drawio import render
        os.makedirs(ROOT, exist_ok=True)
        with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
            f.write(render(self))
        return os.path.join(ROOT, path)

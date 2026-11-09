"""Sub-domain view (C4 Level 2, one sub-domain in focus) from one JSON model.

    python subdomain_view.py all     models/<sd>.json     Mermaid view and draw.io
    python subdomain_view.py mermaid models/<sd>.json [--md <view.md>]
    python subdomain_view.py drawio  models/<sd>.json [--out <dir>] [--name <file stem>]

The model is the single source of both outputs. By default, from the current directory, the Mermaid
view is architecture/mermaid/c4-<sd>.md and the draw.io architecture/drawio/c4-<sd>.drawio, <sd>
being the model's file name; --mermaid-dir and --drawio-dir change the folders.

`mermaid` writes the ```mermaid block of the view: rows fitted (buses of a band on one row, bottom
sub-domains on one row) and relation labels moved off cards (mermaid_c4.cjs). An existing view keeps
everything but its block; a new view gets its reading rules, notes and open questions from the model.
`drawio` lays the view out (sub-domain view principle of the notation), routes every link
orthogonally around the cards, places the labels, and writes <name>.drawio with the c4-diagrams
library.

The design system is c4-diagrams/references/notation.md; this script holds no colour or style of its
own beyond what that library exports. The model format is in ../references/model.md.
"""
import argparse, heapq, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MERMAID_DIR = os.path.join("architecture", "mermaid")   # defaults, relative to the current directory
DRAWIO_DIR = os.path.join("architecture", "drawio")
C4LIB = os.path.normpath(os.path.join(HERE, "..", "..", "c4-diagrams", "scripts"))
sys.path.insert(0, C4LIB)
NODE_TOOL = os.path.join(HERE, "mermaid_c4.cjs")
from c4lib import GENERATED_WITH

GREEN = '$bgColor="rgba(109,174,109,0.15)", $fontColor="#2E6B2E", $borderColor="#6DAE6D"'
CSS_HEADER = ('---\nconfig:\n  themeCSS: "rect[stroke=\\"#6DAE6D\\"] { stroke-dasharray: 7 7; stroke-width: 1px; }"\n---\n')
BEND = 30   # router cost of a bend: high, so a link takes few long straight runs rather than zigzags
FOCUS = "__focus__"      # the band of the sub-domain in focus, as the source of the links to its stores
PUBLIC_TITLE = "PUBLIC BUS"
PRIVATE_TITLE = "PRIVATE BUS"
VERBS = {  # (direction, kind) -> verb phrase; direction "pub" = element to bus, "sub" = bus to element
    ("pub", "event"): "Publishes", ("pub", "command"): "Sends",
    ("sub", "event"): "Subscribes to", ("sub", "command"): "Receives",
    ("pub", "Redis pub/sub"): "Publishes", ("sub", "Redis pub/sub"): "Subscribes to",
}


# =====================================================================================  model
class Model:
    def __init__(self, path):
        m = json.load(open(path, encoding="utf-8"))
        self.raw = m
        self.slug = os.path.splitext(os.path.basename(path))[0]   # betting.json -> betting
        self.system = m["system"]     # the software system the sub-domain belongs to
        self.focus = m["focus"]
        self.date = m.get("date", "")
        self.containers = m["containers"]
        self.externals = m.get("externals", [])
        self.subdomains = m.get("subdomains", [])
        self.public = m.get("public_bus")
        self.private = m.get("private_buses", [])
        self.links = m.get("links", [])
        self.notes = m.get("notes", [])
        self.questions = m.get("open_questions", [])
        self.ids = {}
        for kind, items in (("container", self.containers), ("external", self.externals), ("subdomain", self.subdomains),
                            ("private", self.private), ("public", [self.public] if self.public else [])):
            for it in items:
                if it["id"] in self.ids:
                    raise SystemExit(f"duplicate id {it['id']}")
                self.ids[it["id"]] = kind
        for l in self.links:
            for end in (l["from"], l["to"]):
                if end not in self.ids:
                    raise SystemExit(f"link end {end} is not declared")
        # messages: one lane per (element, bus, direction), groups merged by kind
        lanes = {}
        for msg in m.get("messages", []):
            a, b = msg["from"], msg["to"]
            for end in (a, b):
                if end not in self.ids:
                    raise SystemExit(f"message end {end} is not declared")
            if self.ids[b] in ("public", "private"):
                elem, bus, direction = a, b, "pub"
            elif self.ids[a] in ("public", "private"):
                elem, bus, direction = b, a, "sub"
            else:
                raise SystemExit(f"message {a} -> {b} does not touch a bus")
            lane = lanes.setdefault((elem, bus, direction), {})
            for g in msg["groups"]:
                if g["kind"] == "Redis key":
                    # Redis is two things: a pub/sub bus (events on channels) and a distributed cache
                    # (keys). A key is a data access, never a message on a bus
                    raise SystemExit(f"{a} -> {b}: a Redis key ({', '.join(g['names'])}) is a cache access, not a "
                                     "message: model it as a link to the distributed cache store")
                lane.setdefault(g["kind"], [])
                lane[g["kind"]] += [n for n in g["names"] if n not in lane[g["kind"]]]
        self.lanes = [dict(elem=e, bus=b, dir=d, groups=g) for (e, b, d), g in lanes.items()]
        # where another sub-domain is drawn: on top when it talks through the public bus, at the
        # bottom when it talks through a private bus or by a direct link; both when both
        self.top_sd, self.bottom_sd = [], []
        for sd in self.subdomains:
            mine = [l for l in self.lanes if l["elem"] == sd["id"]]
            if any(self.ids[l["bus"]] == "public" for l in mine):
                self.top_sd.append(sd)
            if any(self.ids[l["bus"]] == "private" for l in mine) or any(sd["id"] in (k["from"], k["to"]) for k in self.links):
                self.bottom_sd.append(sd)

    def kind(self, ident):
        return self.ids[ident]

    def is_store(self, ident):
        return any(c["id"] == ident and c.get("kind") == "store" for c in self.containers)

    def is_service(self, ident):
        """A container of the band: neither a store nor a data sink (both drawn below the band)."""
        return self.kind(ident) == "container" and not any(
            c["id"] == ident and c.get("kind") in ("store", "datasink") for c in self.containers)

    def store_links(self, store):
        """Direct links between a service of the focus and one of its stores."""
        return [k for k in self.links if {k["from"], k["to"]} & {store}
                and any(self.is_service(e) for e in (k["from"], k["to"]))]

    def store_lines(self, store):
        """Label of the one link band -> store: the protocol once on top (one technology per store),
        then one bullet per service access."""
        name = {c["id"]: c["name"] for c in self.containers}
        links = self.store_links(store)
        protocols = list(dict.fromkeys(k["protocol"] for k in links))
        out = [f'Data access [{", ".join(protocols)}]:']
        for k in links:
            svc = k["from"] if self.is_service(k["from"]) else k["to"]
            out.append(f'• {name[svc]} : {k["label"]}')
        return out

    def name_of(self, ident):
        for items in (self.containers, self.externals, self.subdomains, self.private, [self.public] if self.public else []):
            for it in items:
                if it["id"] == ident:
                    return it["name"]
        return ident

    def bus_techno(self, bus_id):
        """Technology of a bus for the lane headers: the model's `techno`, else read from its `tech`."""
        bus = self.public if self.public and self.public["id"] == bus_id else next(b for b in self.private if b["id"] == bus_id)
        if bus.get("techno"):
            return bus["techno"]
        tech = bus.get("tech", "")
        return "SNS" if "SNS" in tech else "REDIS" if "Redis" in tech else tech

    def lane_label_lines(self, lane):
        """Header per kind with the bus scope and technology ("Publishes [PUBLIC event SNS]:",
        "Publishes [PRIVATE event SNS]:", "Publishes [event REDIS]:"), then one bullet per message."""
        techno = self.bus_techno(lane["bus"])
        scope = "PUBLIC " if self.kind(lane["bus"]) == "public" else "PRIVATE " if techno == "SNS" else ""
        shown = {"Redis pub/sub": "event"}
        who = self.name_of(lane["elem"])
        out = []
        for kind, names in lane["groups"].items():
            verb = VERBS.get((lane["dir"], kind), "Publishes" if lane["dir"] == "pub" else "Subscribes to")
            out.append(f"{who} {verb} [{scope}{shown.get(kind, kind)} {techno}]:")
            out += ["• " + n for n in names]
        return out

    def lane_mermaid(self, lane):
        groups = lane["groups"]
        if len(groups) == 1:
            (kind, names), = groups.items()
            return ", ".join(names), kind
        return "; ".join(f"{', '.join(n)} ({k})" for k, n in groups.items()), ", ".join(groups)


# =====================================================================================  Mermaid
def mermaid_code(M, n_per_row=4, offsets=()):
    alias = lambda sd_id, top: f"{sd_id}_pub" if top else sd_id
    L = [CSS_HEADER.rstrip("\n"), "C4Container", f"  %% {GENERATED_WITH}",
         f"  title {M.focus} sub-domain - containers and every link in or out" + (f", {M.date}" if M.date else ""), ""]
    for e in M.externals:
        L.append(f'  System_Ext({e["id"]}, "{e["name"]}", "{e.get("desc", "")}")')
    if M.top_sd:
        L += ["", f'  System_Boundary(sys_top, "{M.system}") {{']
        L += [f'    Container({alias(s["id"], True)}, "{s["name"]}", "Sub-domain", "{s.get("purpose", "")}")' for s in M.top_sd]
        L.append("  }")
    if M.public:
        p = M.public
        L += ["", f'  Boundary(core, "{PUBLIC_TITLE}", "Public bus") {{',
              f'    ContainerQueue_Ext({p["id"]}, "{p["name"]}", "{p.get("tech", "")}", "{p.get("desc", "")}")', "  }"]
    L += ["", f'  System_Boundary(sys, "{M.system}") {{', f'    Boundary(focus, "{M.focus}", "Sub-domain") {{']
    macro = {"container": "Container", "datasink": "Container", "store": "ContainerDb", "unexplored": "Container_Ext"}
    for c in M.containers:
        L.append(f'      {macro[c.get("kind", "container")]}({c["id"]}, "{c["name"]}", "{c.get("tech", "")}", "{c.get("desc", "")}")')
    L.append("    }")
    if M.private:
        L.append(f'    Boundary(buses, "{PRIVATE_TITLE}", "Private") {{')
        L += [f'      ContainerQueue({b["id"]}, "{b["name"]}", "{b.get("tech", "")}", "{b.get("desc", "")}")' for b in M.private]
        L.append("    }")
    if M.bottom_sd:
        L.append('    Boundary(others, " ", " ") {')
        L += [f'      Container({s["id"]}, "{s["name"]}", "Sub-domain", "{s.get("purpose", "")}")' for s in M.bottom_sd]
        L.append("    }")
    L.append("  }")

    def end(ident, bus_kind=None):
        if M.kind(ident) == "subdomain":
            return alias(ident, bus_kind == "public")
        return ident
    if M.links:
        L += ["", "  %% Direct links"]
        L += [f'  Rel({end(k["from"])}, {end(k["to"])}, "{k["label"]}", "{k["protocol"]}")' for k in M.links]
    for title, bus_kind in (("Public bus", "public"), ("Private buses", "private")):
        lanes = [l for l in M.lanes if M.kind(l["bus"]) == bus_kind]
        if not lanes:
            continue
        L += ["", f"  %% {title}"]
        for l in lanes:
            text, tech = M.lane_mermaid(l)
            e = end(l["elem"], bus_kind)
            a, b = (e, l["bus"]) if l["dir"] == "pub" else (l["bus"], e)
            L.append(f'  Rel({a}, {b}, "{text}", "{tech}")')
    L += ["", f"  UpdateElementStyle(focus, {GREEN})"]
    L += [f"  UpdateElementStyle({alias(s['id'], True)}, {GREEN})" for s in M.top_sd]
    L += [f"  UpdateElementStyle({s['id']}, {GREEN})" for s in M.bottom_sd]
    if M.bottom_sd:
        L.append('  UpdateElementStyle(others, $bgColor="transparent", $fontColor="transparent", $borderColor="transparent")')
    L += list(offsets)
    L.append(f'  UpdateLayoutConfig($c4ShapeInRow="{n_per_row}", $c4BoundaryInRow="1")')
    return "\n".join(L) + "\n"


def node(cmd, code, workdir):
    path = os.path.join(workdir, "_view.mmd")
    open(path, "w", encoding="utf-8").write(code)
    r = subprocess.run(["node", NODE_TOOL, cmd, path], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit(r.stderr.strip())
    return r.stdout


def rows_ok(M, geo):
    def name(s): return s["texts"][1] if s["texts"][0].startswith("<<") else s["texts"][0]
    shapes = geo["shapes"]
    by_name = {}
    for s in shapes:
        by_name.setdefault(name(s), []).append(s)
    buses = [by_name[b["name"]][0] for b in M.private if b["name"] in by_name]
    if len({b["y"] for b in buses}) > 1:
        return False
    sd = [s for s in shapes if "[Sub-domain]" in s["texts"]]
    if buses:
        bottom = [s for s in sd if s["y"] > buses[0]["y"]]
        top = [s for s in sd if s["y"] < buses[0]["y"]]
        return len({s["y"] for s in bottom}) <= 1 and len({s["y"] for s in top}) <= 1
    return len({s["y"] for s in sd}) <= 2


def build_mermaid(M, workdir):
    for n in (4, 5, 6, 7, 8, 3):
        code = mermaid_code(M, n)
        if rows_ok(M, json.loads(node("geometry", code, workdir))):
            break
    else:
        print("warning: no per-row value keeps the bus row and the sub-domain rows together", file=sys.stderr)
    offsets = [l for l in node("place", code, workdir).splitlines() if l.strip()]
    code = mermaid_code(M, n, offsets)
    report = node("overlaps", code, workdir).strip()
    print(f"mermaid: {n} shapes per row, {len(offsets)} labels moved, {report.splitlines()[0]}")
    for line in report.splitlines()[1:]:
        print("  " + line.strip())
    return code


def view_md(M, code):
    sds = ", ".join(s["name"] for s in M.subdomains) or "none"
    notes = "\n".join(f"- {n}" for n in M.notes) or "- None."
    qs = "\n".join(f"{i}. {q}" for i, q in enumerate(M.questions, 1)) or "None."
    return f"""# C4 Level 2 - {M.focus} (Mermaid)

Container view of the **{M.focus}** sub-domain of {M.system}: its containers and every link going in
or out of them, generated from its model by the `c4-subdomain-view` skill, in the notation of the
`c4-diagrams` skill.

## Reading rules

- **Top**: systems outside {M.system}, and other sub-domains that exchange with {M.focus} through the
  public bus; then the **PUBLIC BUS**.
- **Middle**: the {M.focus} sub-domain and its containers.
- **Bottom**: the **PRIVATE BUS**, then the other sub-domains reached through it or by a direct call.
- Another sub-domain ({sds}) is one green dashed box, never its containers; the boxes of one level
  share a row.
- A message is drawn in two parts carrying the same message names: producer → bus, then bus →
  consumer. Calls, data access and exports are drawn direct.
- The system boundary is drawn twice when sub-domains sit above the public bus: one system.

## Diagram

```mermaid
{code}```

## Notes

{notes}

## Open questions / next decision needed

{qs}
"""


def write_mermaid(M, args):
    import tempfile
    workdir = tempfile.mkdtemp(prefix="c4-subdomain-")      # scratch files of the Mermaid tooling
    code = build_mermaid(M, workdir)
    args.md = args.md or os.path.join(args.mermaid_dir, f"c4-{M.slug}.md")
    os.makedirs(os.path.dirname(args.md), exist_ok=True)
    if os.path.exists(args.md):
        md = open(args.md, encoding="utf-8").read()
        new, n = re.subn(r"```mermaid\n.*?```", lambda m: "```mermaid\n" + code + "```", md, count=1, flags=re.S)
        if not n:
            raise SystemExit(f"{args.md} has no mermaid block")
    else:
        new = view_md(M, code)
    open(args.md, "w", encoding="utf-8", newline="\n").write(new)
    print(args.md)


# =====================================================================================  draw.io layout
CW, CH, GAP, MARGIN = 240, 110, 80, 60  # every box on the 10 px routing grid
SDW = 280
BUS_H = 60
GRID = 10
LABEL_W = 280
LABEL_GAP = 20   # vertical space kept between two labels


def snap(v):
    return int(round(v / GRID) * GRID)


def label_size(lines, width=LABEL_W):
    from c4drawio import text_width, text_lines
    w = min(width, max(text_width(l) for l in lines) + 8)
    n = sum(text_lines(l, w) for l in lines)
    return int(w), n * 15 + 6


class Layout:
    """Places the boxes of a sub-domain view on a 10 px grid, top to bottom."""

    def __init__(self, M):
        self.M = M
        self.box = {}          # id or (id, "top") -> dict(l, t, w, h, kind, ...)
        self.frames = []       # (kind, l, t, w, h, name)

    def zone_height(self, lanes, minimum=80):
        """Height of the gap a set of lanes crosses: the labels of one element stack, the labels of
        different elements sit side by side."""
        per_elem = {}
        for l in lanes:
            per_elem[l["elem"]] = per_elem.get(l["elem"], 0) + label_size(self.M.lane_label_lines(l))[1] + 2 * LABEL_GAP
        return snap(max(list(per_elem.values()) + [minimum - 50]) + 50)

    def run(self):
        M = self.M
        linked = {k["from"] for k in M.links} | {k["to"] for k in M.links}
        # externals: on top when they only talk through the public bus (sub-domain view principle);
        # in a column right of the system when they have direct links, so a call never crosses a bus
        ext_top = [e for e in M.externals if e["id"] not in linked]
        ext_side = [e for e in M.externals if e["id"] in linked]
        # team convention: one database per domain and per technology. A store is drawn below the
        # band, not in it, and the accesses of the services to it become one link band -> store
        services = [c for c in M.containers if c.get("kind", "container") not in ("store", "datasink")]
        stores = [c for c in M.containers if c.get("kind", "container") == "store"]
        # a data sink exports one store to the data platform: drawn below its store, out of the band
        sinks = [c for c in M.containers if c.get("kind", "container") == "datasink"]
        n_focus = len(services)
        cols = min(4, max(1, n_focus))
        focus_w = cols * CW + (cols - 1) * GAP + 2 * 40
        bottom_w = len(M.bottom_sd) * (SDW + GAP) - GAP + 2 * 40 if M.bottom_sd else 0
        crossing = [k for k in M.links if self.crosses_bus(k)]
        self.corridor = 60 + 20 * len(crossing) if crossing else 0
        sys_l = MARGIN
        sys_w = snap(max(focus_w, bottom_w + self.corridor, 800) + 80)
        sys_r = sys_l + sys_w
        side_x = sys_r + GAP
        top_w = (len(M.top_sd) * (SDW + 40) + 40 + GAP if M.top_sd else 0) + len(ext_top) * (CW + GAP)
        W = snap(max(1400, top_w + 2 * MARGIN, (side_x + CW if ext_side else sys_r) + MARGIN))
        self.W = W
        # ---- top row: the system with the sub-domains reached through the public bus, then the externals
        y = 240
        x = MARGIN
        top_lanes = [l for l in M.lanes if M.kind(l["bus"]) == "public"
                     and (M.kind(l["elem"]) == "subdomain" or (M.kind(l["elem"]) == "external" and l["elem"] not in linked))]
        if M.top_sd or ext_top:
            if M.top_sd:
                bw = len(M.top_sd) * (SDW + 40) + 40
                self.frames.append(("boundary", x, y, bw, 230, M.system))
                for i, sd in enumerate(M.top_sd):
                    self.box[(sd["id"], "top")] = dict(l=x + 40 + i * (SDW + 40), t=y + 50, w=SDW, h=CH, kind="subdomain", name=sd["name"])
                x += bw + GAP
            for e in ext_top:
                self.box[e["id"]] = dict(l=x, t=y + 40, w=CW, h=CH, kind="external", name=e["name"], typ="External System", desc=e.get("desc", ""))
                x += CW + GAP
            y += 230
            y += self.zone_height(top_lanes)
        # ---- public bus, full width
        if M.public:
            self.box[M.public["id"]] = dict(l=MARGIN, t=y, w=W - 2 * MARGIN, h=BUS_H, kind="bus", name=PUBLIC_TITLE,
                                            typ="Container: " + M.public.get("tech", ""), desc=f'{M.public["name"]}, {M.public.get("desc", "")}')
            y += BUS_H
            focus_pub = [l for l in M.lanes if M.kind(l["bus"]) == "public" and M.kind(l["elem"]) in ("container", "external")
                         and (M.kind(l["elem"]) == "container" or l["elem"] in linked)]
            y += max(self.zone_height(focus_pub), 120)
        # ---- the system: the sub-domain in focus
        sys_t = y
        y += 50
        band_l = sys_l + 40
        rows = (n_focus + cols - 1) // cols
        ids = {c["id"] for c in services}
        inner = [k for k in M.links if k["from"] in ids and k["to"] in ids]
        row_gap = 200 if inner else 70
        band_h = 50 + rows * CH + (rows - 1) * row_gap + 50
        self.frames.append(("subdomain", band_l, y, focus_w, band_h, M.focus))
        self.box[FOCUS] = dict(l=band_l, t=y, w=focus_w, h=band_h, kind="band", name=M.focus)
        for i, c in enumerate(services):
            r, col = divmod(i, cols)
            kind = {"container": "container", "store": "store", "unexplored": "external"}[c.get("kind", "container")]
            self.box[c["id"]] = dict(l=band_l + 40 + col * (CW + GAP), t=y + 50 + r * (CH + row_gap), w=CW, h=CH, kind=kind,
                                     name=c["name"], typ="Container: " + c.get("tech", ""), desc=c.get("desc", ""))
        band_t = y
        y += band_h
        # ---- stores: a row below the band, right-aligned, with room for the list of accesses above it
        if stores:
            hs = [label_size(M.store_lines(s["id"]))[1] for s in stores]
            y += snap(max(hs + [60]) + 80)
            x = snap(band_l + focus_w - 40 - len(stores) * (CW + GAP) + GAP)
            for i, s in enumerate(stores):
                self.box[s["id"]] = dict(l=x + i * (CW + GAP), t=y, w=CW, h=CH, kind="store", name=s["name"],
                                         typ="Container: " + s.get("tech", ""), desc=s.get("desc", ""))
            y += CH
        # ---- data sinks: each one right below the store it exports
        sink_t = None
        if sinks:
            y += 120
            sink_t = y
            under = {}
            for s in sinks:
                store = next((k["to"] if k["from"] == s["id"] else k["from"] for k in M.links
                              if s["id"] in (k["from"], k["to"]) and M.is_store(k["to"] if k["from"] == s["id"] else k["from"])), None)
                base = self.box[store]["l"] if store in self.box else band_l + focus_w - 40 - CW
                n = under.get(base, 0)
                under[base] = n + 1
                self.box[s["id"]] = dict(l=base + n * (CW + GAP), t=y, w=CW, h=CH, kind="container", name=s["name"],
                                         typ="Container: " + s.get("tech", ""), desc=s.get("desc", ""))
            y += CH
        # ---- externals with direct links: a column right of the system, from the band down; the ones fed by
        # a data sink sit level with the sinks, close to them
        sink_ids = {s["id"] for s in sinks}
        fed = {k["to"] if k["from"] in sink_ids else k["from"] for k in M.links if sink_ids & {k["from"], k["to"]}}
        main = [e for e in ext_side if e["id"] not in fed]
        low = [e for e in ext_side if e["id"] in fed]
        t = band_t + 50
        for e in main:
            self.box[e["id"]] = dict(l=side_x, t=t, w=CW, h=CH, kind="external", name=e["name"],
                                     typ="External System", desc=e.get("desc", ""))
            t += CH + 90
        if low and sink_t is not None:
            t = max(t, sink_t)
        for e in low:
            self.box[e["id"]] = dict(l=side_x, t=t, w=CW, h=CH, kind="external", name=e["name"],
                                     typ="External System", desc=e.get("desc", ""))
            t += CH + 90
        side_bottom = t
        # ---- private buses, side by side, as wide as the system less the corridor of the calls crossing them
        if M.private:
            focus_priv = [l for l in M.lanes if M.kind(l["bus"]) == "private" and M.kind(l["elem"]) == "container"]
            y += max(self.zone_height(focus_priv), 140)
            n = len(M.private)
            span = sys_r - 40 - self.corridor - band_l
            bw = snap((span - (n - 1) * 40) / n)
            for i, b in enumerate(M.private):
                name = PRIVATE_TITLE if n == 1 else f"PRIVATE BUS · {b['name']}"
                desc = f'{b["name"]}, {b.get("desc", "")}' if n == 1 else b.get("desc", "")
                self.box[b["id"]] = dict(l=band_l + i * (bw + 40), t=y, w=bw, h=BUS_H, kind="bus", name=name,
                                         typ="Container: " + b.get("tech", ""), desc=desc)
            y += BUS_H
        # ---- bottom: the sub-domains reached through the private buses or by a direct link
        if M.bottom_sd:
            bottom_lanes = [l for l in M.lanes if M.kind(l["bus"]) == "private" and M.kind(l["elem"]) == "subdomain"]
            y += max(self.zone_height(bottom_lanes), 160)
            for i, sd in enumerate(M.bottom_sd):
                self.box[(sd["id"], "bottom")] = dict(l=band_l + i * (SDW + GAP), t=y, w=SDW, h=CH, kind="subdomain", name=sd["name"])
            y += CH
        y += 60
        self.frames.append(("boundary", sys_l, sys_t, sys_w, y - sys_t, M.system))
        y = max(y, side_bottom)
        self.H = y + 220
        self.legend_y = y + 50
        return self

    def crosses_bus(self, link):
        """A direct link between the focus and a sub-domain drawn below the private bus crosses it."""
        k = {self.M.kind(link["from"]), self.M.kind(link["to"])}
        return k == {"container", "subdomain"}

    def ref(self, ident, bus_kind=None):
        """Box of an element; a sub-domain resolves to its top copy for the public bus, else the bottom one."""
        if self.M.kind(ident) == "subdomain":
            return (ident, "top") if bus_kind == "public" else (ident, "bottom")
        return ident


# =====================================================================================  draw.io routing
class Router:
    """Orthogonal A* on a 10 px grid: cards are walls, bends and crossings cost, overlaps cost more."""

    def __init__(self, W, H, boxes):
        self.nx, self.ny = W // GRID + 1, H // GRID + 1
        self.block = bytearray(self.nx * self.ny)
        self.used = {}  # cell -> set of "h" / "v"
        for b in boxes:
            self.wall(b, 1)
        for gx in range(self.nx):          # title area and canvas edges are walls
            for gy in range(self.ny):
                if gy < 17 or gx < 3 or gx > self.nx - 4 or gy > self.ny - 4:
                    self.block[gy * self.nx + gx] = 1

    def cells(self, b, pad):
        x0, y0 = max(0, (b["l"] - pad) // GRID), max(0, (b["t"] - pad) // GRID)
        x1, y1 = min(self.nx - 1, (b["l"] + b["w"] + pad) // GRID), min(self.ny - 1, (b["t"] + b["h"] + pad) // GRID)
        for gx in range(x0, x1 + 1):
            for gy in range(y0, y1 + 1):
                yield gy * self.nx + gx

    def wall(self, b, v):
        for c in self.cells(b, 10):
            self.block[c] = v

    def route(self, start, goal, s_dir, g_dir):
        """start, goal: grid points just outside the source and target boxes; dirs: first and last move."""
        nx = self.nx
        sx, sy = start[0] // GRID, start[1] // GRID
        gx, gy = goal[0] // GRID, goal[1] // GRID
        moves = {"u": (0, -1), "d": (0, 1), "l": (-1, 0), "r": (1, 0)}
        h = lambda x, y: abs(x - gx) + abs(y - gy)
        opn = [(h(sx, sy), 0, sx, sy, s_dir)]
        best = {(sx, sy, s_dir): 0}
        prev = {}
        while opn:
            f, g, x, y, d = heapq.heappop(opn)
            if (x, y) == (gx, gy):
                if d != g_dir:
                    g += 6
                end = (x, y, d)
                break
            if g > best.get((x, y, d), 1e18):
                continue
            for nd, (dx, dy) in moves.items():
                if (dx, dy) == tuple(-v for v in moves[d]):
                    continue
                X, Y = x + dx, y + dy
                if not (0 <= X < nx and 0 <= Y < self.ny):
                    continue
                c = Y * nx + X
                if self.block[c] and (X, Y) != (gx, gy):
                    continue
                axis = "v" if dx == 0 else "h"
                used = self.used.get(c, ())
                step = 1 + (BEND if nd != d else 0) + (40 if axis in used else 0) + (12 if used and axis not in used else 0)
                ng = g + step
                if ng < best.get((X, Y, nd), 1e18):
                    best[(X, Y, nd)] = ng
                    prev[(X, Y, nd)] = (x, y, d)
                    heapq.heappush(opn, (ng + h(X, Y), ng, X, Y, nd))
        else:
            return None
        pts, k = [], end
        while k in prev or (k[0], k[1]) == (sx, sy):
            pts.append((k[0] * GRID, k[1] * GRID))
            if k not in prev:
                break
            k = prev[k]
        pts.reverse()
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            for X in range(min(x1, x2) // GRID, max(x1, x2) // GRID + 1):
                for Y in range(min(y1, y2) // GRID, max(y1, y2) // GRID + 1):
                    self.used.setdefault(Y * nx + X, set()).add("v" if x1 == x2 else "h")
        return pts


def simplify(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if len(out) >= 2 and (out[-2][0] == out[-1][0] == p[0] or out[-2][1] == out[-1][1] == p[1]):
            out[-1] = p
        else:
            out.append(p)
    return out


def ports(L, edges):
    """Port of each edge end: the side facing the other end, ends of one side spread along it.
    A bus end comes last and sits straight above or below its partner port, so a lane is a
    straight line whenever nothing stands in between."""
    def side_of(me, other):
        # a link leaves by the side facing its dominant direction, so a call to the right column
        # leaves sideways and runs straight; a lane to a bus or a band leaves by the top or the bottom
        if other["kind"] not in ("bus", "band") and me["kind"] not in ("bus", "band"):
            dx = (other["l"] + other["w"] / 2) - (me["l"] + me["w"] / 2)
            dy = (other["t"] + other["h"] / 2) - (me["t"] + me["h"] / 2)
            if abs(dx) > abs(dy) and (other["l"] >= me["l"] + me["w"] or other["l"] + other["w"] <= me["l"]):
                return "right" if dx > 0 else "left"
        if other["t"] >= me["t"] + me["h"]:
            return "bottom"
        if other["t"] + other["h"] <= me["t"]:
            return "top"
        return "right" if other["l"] > me["l"] else "left"

    def set_port(e, slot, me, side, x=None, y=None):
        if side == "top":
            e[slot] = ((x, me["t"]), (x, me["t"] - 20), "u")
        elif side == "bottom":
            e[slot] = ((x, me["t"] + me["h"]), (x, me["t"] + me["h"] + 20), "d")
        elif side == "left":
            e[slot] = ((me["l"], y), (me["l"] - 20, y), "l")
        else:
            e[slot] = ((me["l"] + me["w"], y), (me["l"] + me["w"] + 20, y), "r")

    sides = {}
    for i, e in enumerate(edges):
        a, b = L.box[e["a"]], L.box[e["b"]]
        for me, other, slot in ((a, b, "pa"), (b, a, "pb")):
            if me["kind"] in ("bus", "band"):
                continue
            side = side_of(me, other)
            sides.setdefault((id(me), side), []).append((i, slot, me, other, side))
    for items in sides.values():
        me, side = items[0][2], items[0][4]
        horizontal = side in ("top", "bottom")
        # lanes of one element to one bus sit side by side, publish left of subscribe
        items.sort(key=lambda it: ((it[3]["l"] + it[3]["w"] / 2) if horizontal else (it[3]["t"] + it[3]["h"] / 2),
                                   edges[it[0]].get("order", 0)))
        n = len(items)
        for k, (i, slot, _, other, _) in enumerate(items):
            if horizontal:
                set_port(edges[i], slot, me, side, x=snap(me["l"] + me["w"] * (k + 1) / (n + 1)))
            else:
                set_port(edges[i], slot, me, side, y=snap(me["t"] + me["h"] * (k + 1) / (n + 1)))
    for e in edges:
        for slot, partner in (("pa", "pb"), ("pb", "pa")):
            me = L.box[e["a" if slot == "pa" else "b"]]
            if me["kind"] not in ("bus", "band"):
                continue
            other = L.box[e["b" if slot == "pa" else "a"]]
            if partner not in e:          # bus to bus: not drawn in a sub-domain view
                continue
            px = e[partner][0][0]
            x = min(max(px, me["l"] + 20), me["l"] + me["w"] - 20)
            set_port(e, slot, me, side_of(me, other), x=x, y=snap(me["t"] + me["h"] / 2))


def place_labels(L, edges, routes):
    """Each label centred on a segment of its own route (the line runs through the middle of the
    pill), clear of cards, of other labels and of the other lines. A label goes beside its line only
    when no centred spot is free."""
    cards = [dict(x=b["l"] - 4, y=b["t"] - 4, w=b["w"] + 8, h=b["h"] + 8) for b in L.box.values() if b["kind"] != "band"]
    segs = [(i, sg) for i, r in enumerate(routes) if r for sg in zip(r, r[1:])]
    # the dashed edges of the boundaries and bands count as lines: a label should not sit on them
    for _, l, t, w, h, _ in L.frames:
        segs += [(-1, sg) for sg in (((l, t), (l + w, t)), ((l, t + h), (l + w, t + h)), ((l, t), (l, t + h)), ((l + w, t), (l + w, t + h)))]
    placed = []

    def inter(a, b):
        return max(0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])) * max(0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))

    def on_lines(box, own):
        n = 0
        for owner, ((x1, y1), (x2, y2)) in segs:
            if owner == own:
                continue
            if x1 == x2 and box["x"] < x1 < box["x"] + box["w"] and min(y1, y2) < box["y"] + box["h"] and max(y1, y2) > box["y"]:
                n += min(max(y1, y2), box["y"] + box["h"]) - max(min(y1, y2), box["y"])
            if y1 == y2 and box["y"] < y1 < box["y"] + box["h"] and min(x1, x2) < box["x"] + box["w"] and max(x1, x2) > box["x"]:
                n += min(max(x1, x2), box["x"] + box["w"]) - max(min(x1, x2), box["x"])
        return n

    def score(best, left, top, w, h, own, dist, beside):
        cand = dict(x=left - 6, y=top - 4, w=w + 12, h=h)
        if cand["x"] < 8 or cand["y"] < 160 or cand["x"] + cand["w"] > L.W - 8 or cand["y"] + cand["h"] > L.H - 8:
            return best
        cost = (sum(inter(cand, c) for c in cards) * 50 + sum(inter(cand, p) for p in placed) * 50
                + on_lines(cand, own) * 4 + dist + (3000 if beside else 0))
        return (cost, cand, left, top) if best is None or cost < best[0] else best

    order = sorted(range(len(edges)), key=lambda i: -label_size(edges[i]["lines"])[1])
    result = [None] * len(edges)
    for i in order:
        r = routes[i]
        if not r:
            continue
        w, h = label_size(edges[i]["lines"])
        best = None
        for (x1, y1), (x2, y2) in zip(r, r[1:]):
            if x1 == x2:
                lo, hi = min(y1, y2), max(y1, y2)
                for top in range(lo, max(lo, hi - h) + 1, 10):
                    dist = abs(top + h / 2 - (lo + hi) / 2)
                    best = score(best, x1 - w // 2, top, w, h, i, dist, False)
                    for left in (x1 + 14, x1 - 14 - w - 12):
                        best = score(best, left, top, w, h, i, dist, True)
            else:
                lo, hi = min(x1, x2), max(x1, x2)
                for left in range(lo, max(lo, hi - w) + 1, 10):
                    dist = abs(left + w / 2 - (lo + hi) / 2) + 40
                    best = score(best, left, y1 - h // 2 + 4, w, h, i, dist, False)
                    for top in (y1 + 12, y1 - 12 - h):
                        best = score(best, left, top, w, h, i, dist, True)
        if best:
            # keep the next labels LABEL_GAP away above and below: lists stay apart
            c = best[1]
            placed.append(dict(x=c["x"], y=c["y"] - LABEL_GAP, w=c["w"], h=c["h"] + 2 * LABEL_GAP))
            result[i] = (best[2], best[3], w, best[1])
    return result


def write_drawio(M, args):
    from c4lib import Doc, PUBLISH, SUBSCRIBE, LINE
    L = Layout(M).run()
    # ---- edges: lanes (one per element, bus and direction) and direct links
    edges = []
    for l in M.lanes:
        bus_kind = M.kind(l["bus"])
        elem = L.ref(l["elem"], bus_kind)
        a, b = (elem, l["bus"]) if l["dir"] == "pub" else (l["bus"], elem)
        edges.append(dict(a=a, b=b, lines=M.lane_label_lines(l), dashed=True,
                          color=PUBLISH if l["dir"] == "pub" else SUBSCRIBE,
                          order=0 if l["dir"] == "pub" else 1))
    to_store = set()
    for c in M.containers:
        if c.get("kind") == "store" and M.store_links(c["id"]):
            edges.append(dict(a=FOCUS, b=c["id"], lines=M.store_lines(c["id"]), dashed=False, color=None))
            to_store |= {id(k) for k in M.store_links(c["id"])}
    for k in M.links:
        if id(k) in to_store:
            continue
        edges.append(dict(a=L.ref(k["from"]), b=L.ref(k["to"]), lines=[f'{k["label"]} [{k["protocol"]}]'], dashed=False, color=None))
    ports(L, edges)
    router = Router(L.W, L.H, [b for b in L.box.values() if b["kind"] != "band"])
    routes = []
    for e in edges:
        (pa, sa, da), (pb, sb, db) = e["pa"], e["pb"]
        mid = router.route(sa, sb, da, {"u": "d", "d": "u", "l": "r", "r": "l"}[db])
        if mid is None:
            print(f"warning: no route for {e['a']} -> {e['b']}", file=sys.stderr)
            routes.append(None)
            continue
        # tip 1 px before the target edge
        tip = (pb[0] + {"u": 0, "d": 0, "l": 0, "r": 0}[db], pb[1])
        if db == "u": tip = (pb[0], pb[1] - 1)
        if db == "d": tip = (pb[0], pb[1] + 1)
        if db == "l": tip = (pb[0] - 1, pb[1])
        if db == "r": tip = (pb[0] + 1, pb[1])
        routes.append(simplify([pa] + mid + [tip]))
    labels = place_labels(L, edges, routes)
    # ---- draw
    d = Doc(f"Container diagram for {M.system} - {M.focus}", L.W, L.H)
    names = ", ".join(c["name"] for c in M.containers)
    as_of = f", as of {M.date}" if M.date else ""
    lead = f"{names} and every link in or out of the {M.focus} sub-domain{as_of}. The other sub-domains are drawn as one box each"
    lead += f"; {M.system} is drawn twice, above and below the public bus." if M.top_sd else "."
    d.title(64, 40, f"C4 · Level 2 · Containers · {M.system} · {M.focus} sub-domain", f"Container diagram for {M.system} - {M.focus}", lead)
    for kind, l, t, w, h, name in L.frames:
        (d.boundary(l, t, w, h, name, "Software System") if kind == "boundary" else d.subdomain(l, t, w, h, name))
    for b in L.box.values():
        if b["kind"] == "subdomain":
            d.subdomain(b["l"], b["t"], b["w"], b["h"], b["name"])
    for b in L.box.values():
        if b["kind"] == "bus":
            d.bus(b["l"], b["t"], b["w"], b["h"], b["name"], b["typ"], b["desc"])
        elif b["kind"] not in ("subdomain", "band"):
            d.card(b["l"], b["t"], b["w"], b["h"], b["kind"], b["name"], b["typ"], b["desc"])
    for e, r in zip(edges, routes):
        if r:
            kw = dict(dashed=e["dashed"])
            if e["color"]:
                kw["color"] = e["color"]
            d.route(r, **kw)
    for e, lab in zip(edges, labels):
        if lab:
            # the outline of a label takes the colour and the style of its line
            d.label(lab[0], lab[1], lab[2], "\n".join(e["lines"]), border=e["color"] or LINE, dashed=e["dashed"])
    present = {b["kind"] for b in L.box.values()}
    items = [(k, t) for k, t in (("container", "Container"), ("store", "Data store"), ("external", "External system"))
             if k in present or (k == "container" and "bus" in present)]
    items += [("boundary", "Software system boundary"), ("subdomain", "Sub-domain")]
    if M.links:
        items.append(("sync", "Direct call [HTTP / SQL]"))
    items += [("publish", "Published / sent to a bus"), ("subscribe", "Subscribed / received from a bus")]
    d.legend(64, L.legend_y, items)
    d.footer(f"C4 · L2 · {M.system} · {M.focus}" + (f" · {M.date[:4]}" if M.date else ""))
    # ---- report
    def hit(a, b):
        return min(a["x"] + a["w"], b["x"] + b["w"]) > max(a["x"], b["x"]) and min(a["y"] + a["h"], b["y"] + b["h"]) > max(a["y"], b["y"])
    boxes = [lab[3] for lab in labels if lab]
    cards = [dict(x=b["l"], y=b["t"], w=b["w"], h=b["h"]) for b in L.box.values() if b["kind"] != "band"]
    bad = sum(1 for i, a in enumerate(boxes) if any(hit(a, c) for c in cards) or any(hit(a, b) for b in boxes[i + 1:]))
    crossings = count_crossings(routes)
    bends = sum(len(r) - 2 for r in routes if r)
    print(f"drawio: {len(L.box)} boxes, {len(edges)} links, unrouted {routes.count(None)}, "
          f"labels over a card or another label {bad}, line crossings {crossings}, bends {bends}")
    stem = args.name or f"c4-{M.slug}"
    import c4lib
    c4lib.ROOT = args.out or args.drawio_dir
    print(d.write_drawio(f"{stem}.drawio"))


def count_crossings(routes):
    segs = [s for r in routes if r for s in zip(r, r[1:])]
    n = 0
    for i, ((ax1, ay1), (ax2, ay2)) in enumerate(segs):
        for (bx1, by1), (bx2, by2) in segs[i + 1:]:
            if ay1 == ay2 and bx1 == bx2 and min(ax1, ax2) < bx1 < max(ax1, ax2) and min(by1, by2) < ay1 < max(by1, by2):
                n += 1
            elif ax1 == ax2 and by1 == by2 and min(bx1, bx2) < ax1 < max(bx1, bx2) and min(ay1, ay2) < by1 < max(ay1, ay2):
                n += 1
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("format", choices=["all", "mermaid", "drawio"])
    ap.add_argument("model")
    ap.add_argument("--md")
    ap.add_argument("--out")
    ap.add_argument("--name")
    ap.add_argument("--mermaid-dir", default=MERMAID_DIR, help="folder of the Mermaid views (default %(default)s)")
    ap.add_argument("--drawio-dir", default=DRAWIO_DIR, help="folder of the draw.io files (default %(default)s)")
    a = ap.parse_args()
    model = Model(a.model)
    failed = False
    if a.format in ("all", "mermaid"):
        try:
            write_mermaid(model, a)
        except SystemExit as e:
            # the Mermaid tooling needs Node and Playwright; the draw.io does not, so `all` goes on
            if a.format == "mermaid":
                raise
            print(f"mermaid: not written ({e}); the draw.io is written anyway", file=sys.stderr)
            failed = True
    if a.format in ("all", "drawio"):
        write_drawio(model, a)
    sys.exit(1 if failed else 0)

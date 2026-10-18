# C4 notation

**Single source of the C4 design system.** Colours, shapes, wording and the bus rules below apply
to every C4 format: the HTML view (`scripts/c4lib.py`), draw.io (`scripts/c4drawio.py` and any
hand-written `.drawio`) and Mermaid. When the design system changes, it changes here first; then
`scripts/c4lib.py`, `scripts/c4drawio.py`, the generator of the `c4-subdomain-view` skill and the
sections "draw.io" and "Mermaid" below are aligned on it. No other file defines a C4 colour, shape
or wording rule.

Two kinds of Level 2 diagram follow it: the **complete view** of a system (every sub-domain with its
containers) and the **sub-domain view** (one sub-domain in focus, section "Sub-domain view").
The examples use an online shop with the Catalog, Ordering, Payment, Shipping and Customer
sub-domains.

## Element colours (classic C4, c4model.com / C4-PlantUML defaults)

| Element                     | Fill      | Text    | Notes                                                        |
|-----------------------------|-----------|---------|--------------------------------------------------------------|
| Person                      | `#08427B` | white   | head-and-shoulders icon above the name                       |
| Software system (in scope)  | `#1168BD` | white   | one per Level 1 diagram                                      |
| Container                   | `#438DD5` | white   | always `[Container: Technology]`                             |
| Data store / message broker | `#438DD5` | white   | same blue, cylinder icon; buses count here                   |
| External system or person   | `#999999` | white   | out of scope                                                 |
| Software system boundary    | none      | —       | 2 px dashed `#444444`, radius 28, label bottom-left          |
| Sub-domain (bounded context)| `#E3F2E1` | `#2E6B2E` | 2 px dashed `#6DAE6D`, radius 20, name tag on the top edge |
| Relationship (sync)         | —         | `#707070` | 2.5 px solid, round caps, soft head                        |
| Message published to a bus  | —         | `#D55E00` | 2.5 px dashed 6/6, head on the bus (publish / send)        |
| Message subscribed from a bus | —       | `#0072B2` | 2.5 px dashed 6/6, head on the element (subscribe / receive) |
| Message without a bus       | —         | `#707070` | 2.5 px dashed 6/6 (a webhook, an event between two systems in a Level 1) |
| Relationship label          | white pill, radius 10, 12/15 `#707070`; outline 1 px `#E5E7EB`, or in a sub-domain view the colour and the style of its line (section "Sub-domain view") |

The vermillion / blue pair is the Okabe-Ito pair, readable with colour blindness, and distinct from
the grey of the calls and the green of the sub-domains.

Chrome only (eyebrow, title, lead, legend frame, level stamp) uses neutral tokens: the C4 system
blue `#1168BD` for the eyebrow, greys `#111827` / `#374151` / `#6B7280` / `#E5E7EB` for the rest,
system fonts (Segoe UI, Helvetica, Arial), a condensed face for eyebrows and type badges (Arial
Narrow), a monospace face for the level stamp. No logo: the title names the system.

## Shapes

- Cards 240 × 110 (persons 240 × 130), radius 16, shadow `0 6px 16px rgba(17,24,39,.14), 0 1px 2px rgba(17,24,39,.08)`.
- Card content, centred: **Name** 16/20 bold · type badge pill `[Type: Technology]` condensed 11 uppercase, `rgba(255,255,255,.2)` background · one-line description 12/15.
- Column grid: 320 px pitch (240 card + 80 gap). Row pitch 180 (110 card + 70 gap) so one horizontal can run between rows.
- Arrows are orthogonal (horizontal/vertical segments only), never through a card. Tips stop 1 px before the target edge.

## Text rules

1. Every element shows Name, `[Type: Technology]`, one-line description. No technology on Level 1.
2. Every relationship reads `verb phrase [protocol]`: "Place, cancel and get orders [HTTPS]".
3. **Message labels** (draw.io and HTML): a header per message kind, then one message name per
   bullet, left-aligned. The header is the element name, the verb phrase, and in brackets the bus
   scope, the message kind and the bus technology:
   - "ordering-worker Publishes [PUBLIC event KAFKA]:" on the public bus,
   - "ordering-worker Sends [PRIVATE command SNS]:" on the private bus,
   - "ordering-api Subscribes to [event REDIS]:" on a Redis pub/sub;
   - then "• order_confirmed", "• order_cancelled". A label with both kinds repeats the pattern per
     kind. Verbs: Publishes / Subscribes to (event), Sends / Receives (command).
   Mermaid keeps one line per label: it has no line break in a `Rel` label.
4. **Data access labels** (draw.io and HTML, sub-domain view): the protocol once, then one access per
   service: "Data access [SQL]:" then "• ordering-api : Insert orders, read order history".
5. Titles: "System Context diagram for X", "Container diagram for X", "Component diagram for X (container)";
   a sub-domain view is "Container diagram for <system> - <sub-domain>".
6. Legend and a level stamp (`C4 · L2 · <system>`) on every diagram. The legend shows only the kinds
   the diagram uses, and both lane colours when it has bus lanes.
7. Up to ~20 elements per diagram. Group containers by sub-domain; a sub-domain past 6 containers gets its own Container diagram.
8. The domain's own vocabulary (its ubiquitous language), never generic words: "order line",
   "shipment", "refund", not "item", "object", "data".

## Message buses

Messaging is drawn as buses, not as coloured arrows between two containers:
- **Private bus** (inside the system boundary): horizontal band at the bottom. A Redis pub/sub that
  carries messages between sub-domains is drawn as a second private bus beside it.
- **Public bus** (shared with other systems): outside the boundary. In the complete view, a vertical
  band next to the external systems it connects, with a dashed collector line from the sub-domains;
  in a sub-domain view, a full-width horizontal band above the focus.
- **At most two lanes per element–bus pair, one per direction**: the publish lane (element → bus,
  head on the bus, publish or send) in vermillion `#D55E00`, the subscribe lane (bus → element, head
  on the element, subscribe or receive) in blue `#0072B2`. Each lane carries a message label (text
  rule 3). One head per arrow.
- **Redis is two things, drawn two ways**: its **pub/sub channels** carry events (`price_changed`) and
  are a bus; its **keys** (shopping carts, a leader election key) are a distributed cache and are a
  data store, reached by data access links, never by a bus lane. The same Redis instance can appear
  as both.
- A Redis pub/sub between two containers of the same sub-domain stays a data store card with its own arrows.

## draw.io

What `scripts/c4drawio.py` writes, and what a hand-written `.drawio` uses. The fastest path to a
draw.io C4 is a generator script: `Doc.write_drawio(path)` writes the same layout as the HTML, editable
in draw.io afterwards. Uncompressed XML, one `<object>` per element. A sub-domain view is generated by
the `c4-subdomain-view` skill, which writes the draw.io only.

- **Element attributes** on the `<object>`: `C4Type` (`Person`, `Software System`, `External System`,
  `Container`, `Sub-domain`), `C4Name`, `C4Technology`, `C4Description`. `scripts/drawio_import.py`
  reads them back.
- **Nesting**: a card inside a sub-domain is a child of the sub-domain cell, a sub-domain inside the
  system boundary is a child of the boundary (`container=1;collapsible=0` on both).
- **Attached edges**: an edge end on a card, a bus or a sub-domain border is attached to it
  (`source` / `target`), so moving the box in draw.io drags the edge.
- **Fonts**: `fontFamily=Segoe UI,Helvetica,Arial,sans-serif`; the condensed face is `Arial Narrow`,
  the monospace face `Consolas`.

| Element | Style (beyond `html=1;whiteSpace=wrap;fontFamily=…`) |
|---|---|
| Person, system, container, external, bus | `rounded=1;absoluteArcSize=1;arcSize=32;fillColor=<fill of the element table>;strokeColor=none;fontColor=#FFFFFF;shadow=1` — a vertical bus adds `horizontal=0` |
| Data store | `shape=cylinder3;boundedLbl=1;size=12;fillColor=#438DD5;strokeColor=#2E6FAD;fontColor=#FFFFFF;shadow=1` (the outline keeps the lid visible) |
| Software system boundary | `rounded=1;absoluteArcSize=1;arcSize=56;fillColor=none;dashed=1;fixDash=1;dashPattern=8 6;strokeColor=#444444;strokeWidth=2;verticalAlign=bottom;align=left` |
| Sub-domain | `rounded=1;absoluteArcSize=1;arcSize=40;fillColor=#E3F2E1;dashed=1;fixDash=1;dashPattern=8 6;strokeColor=#6DAE6D;strokeWidth=2;verticalAlign=top;align=left;spacingTop=-12;labelBackgroundColor=#CDE8CB;fontColor=#2E6B2E` |
| Relationship (sync) | `edgeStyle=none;rounded=1;strokeColor=#707070;strokeWidth=2.5;endArrow=blockThin;endFill=1;endSize=6` + waypoints; `exitX/exitY/entryX/entryY` pinned on the border point so the path stays orthogonal |
| Relationship (message) | same + `dashed=1;fixDash=1;dashPattern=6 6`; a bus lane takes `strokeColor=#D55E00` (publish) or `strokeColor=#0072B2` (subscribe) |
| Relationship label | separate `text` cell: `rounded=1;fillColor=#FFFFFF;strokeColor=#E5E7EB;fontColor=#707070;fontSize=12`, 8 px clear of lines; a multi-line label is `align=left`. In a sub-domain view: `strokeColor=<colour of its line>`, plus `dashed=1;dashPattern=4 3` on a bus lane, centred on its line |

Card label: `<b style="font-size:16px">Name</b><br>[TYPE: TECHNOLOGY]<br>description`.

## Mermaid

Mermaid's C4 syntax (`C4Context`, `C4Container`) is the format for **designing**: it is text, quick to
write while reverse engineering code or sketching, and it diffs. Its layout is automatic: lines go
diagonal, labels may overlap, and it has no dashed relationship. A diagram that must read well as a
presentation is drawn in draw.io or HTML with a generator script. Checked against Mermaid 11.4.1.

| Notation | Mermaid |
|---|---|
| Person | `Person(alias, "Name", "description")` |
| Software system in scope | `System(alias, "Name", "description")` (Level 1) or `System_Boundary(alias, "Name") { … }` (Level 2) |
| External system | `System_Ext(alias, "Name", "description")` |
| Container | `Container(alias, "Name", "Technology", "description")` |
| Data store | `ContainerDb(alias, "Name", "Technology", "description")` |
| Private bus | `ContainerQueue(privatebus, "Domain event bus", "message broker", "…")` inside the system boundary |
| Public bus | `ContainerQueue_Ext(publicbus, "Enterprise event bus", "message broker", "…")` outside it |
| Sub-domain | `Boundary(alias, "Name", "Sub-domain") { … }` + `UpdateElementStyle(alias, $bgColor="rgba(109,174,109,0.15)", $fontColor="#2E6B2E", $borderColor="#6DAE6D")`. Never an opaque `$bgColor`: Mermaid draws a boundary's rectangle over its children, so an opaque fill hides every container of the sub-domain; the 15 % green gives about `#E3F2E1` on white and leaves the cards visible. Mermaid C4 has no z-order parameter, and the declaration order does not change the drawing order |
| Relationship | `Rel(from, to, "verb phrase", "protocol")` — the protocol is the `[…]` of the label |
| Message | `Rel(container, bus, "x, y", "event")`, `Rel(bus, container, "x, y", "event")`; `command` the same way. The `event` / `command` technology replaces the dashed line |

Element colours are Mermaid's C4 defaults, which already are the classic palette of the element table.
Mermaid relationships stay grey: the publish / subscribe colours and the multi-line labels are not
carried by the Mermaid views.
Mermaid C4 wraps a row at the viewer's screen width (`screen.availWidth`), whatever `c4ShapeInRow`
says: the same source shows fewer boxes per row on a narrow screen. Two `Rel` between the same pair
are drawn on top of each other and one label disappears: merge them into one `Rel` whose label lists
every message, with `(event)` / `(command)` after each group when both kinds share the arrow.
Readability levers: `UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")` and
`UpdateRelStyle(from, to, $offsetX="…", $offsetY="…")` to move a label; `Rel_R` / `Rel_L` / `Rel_U` /
`Rel_D` have no effect on the layout in 11.4.1.

## Sub-domain view

One Container diagram per sub-domain: the sub-domain, everything in it, and every link going in or
out of its containers. Generated in draw.io and Mermaid from one JSON model per sub-domain, the
single source of both, by the `c4-subdomain-view` skill.

### Principles (every format)

- **Top**: systems outside the system in scope and other sub-domains that exchange with this one
  only through the public bus; then the **public bus**, full width.
- **Middle**: the band of the sub-domain in focus and its containers. It is the only sub-domain whose
  containers are drawn.
- **Bottom**: the **private buses** (the private bus, and a Redis pub/sub drawn as a bus) side by
  side, then the other sub-domains reached through them or by a direct link.
- **Another sub-domain is one green dashed box**, never its containers: every link of its containers
  lands on that box, and links between the same pair are merged. The boxes of one level (top or
  bottom) share a row. A sub-domain that exchanges through both sides is drawn twice (top and
  bottom) so no arrow crosses the band; the system boundary is then drawn twice too, above and below
  the public bus; the view says it is one sub-domain and one system.
- **A message is drawn in two parts carrying the same message names**: producer → bus, then bus →
  consumer, on the bus the code uses (private or public, never one then the other). A message with no
  producer or no consumer found keeps only its known part, and the view says so in its notes.
- **Direct links stay direct**: calls, data access, exports.
- Band names: the public bus band is **PUBLIC BUS**, the private bus band **PRIVATE BUS**.

### draw.io

- **Externals**: those that only talk through the public bus sit on top; those with direct links sit
  in a column right of the system, at the height of the focus band, so a call never crosses a bus
  (their bus lanes go up to the public bus, which spans the full width). Calls between the focus and
  a sub-domain below the private buses run in a corridor left free at the right end of the private
  buses.
- **Data stores**: convention, **one database per sub-domain and per technology**. A store of the
  sub-domain is drawn below its band (inside the system), not in it, and every access of its services
  to it becomes **one link band → store** with a data access label (text rule 4). The gap between the
  band and the private buses is sized for these lists.
- **Data sinks**: a data sink (a job that exports one store to a data platform) is drawn out of the
  band, right below the store it exports, with its own link to it; the externals it feeds sit level
  with it in the right column.
- **Lanes**: two lanes at most per element–bus pair, one per direction, coloured (section "Message
  buses"), with message labels (text rule 3).
- **Routing**: few long straight runs rather than zigzags. A call leaves its card by the side facing
  its dominant direction (sideways toward the right column), a lane by the top or the bottom toward
  its bus; a bend costs more than a detour of a few grid steps.
- **Labels**: a label is centred on its own line (the line runs through the middle of the pill), so a
  list reads with the lane it belongs to; it goes beside its line, 8 px clear, only when no centred
  spot is free of cards and other labels. Its outline takes the colour and the style of its line:
  dashed vermillion `#D55E00` (publish), dashed blue `#0072B2` (subscribe), solid grey `#707070`
  (direct link). Two labels keep 20 px of vertical space between them.

### Mermaid

- The public bus sits in a "PUBLIC BUS" `Boundary`, the private buses in a "PRIVATE BUS" `Boundary`,
  all stacked with `UpdateLayoutConfig($c4ShapeInRow="N", $c4BoundaryInRow="1")`. The data stores
  stay in the band, one `Rel` per access.
- **Top of the view**: the other sub-domains drawn above the public bus sit in a second
  `System_Boundary(sys_top, "<system>")`, declared before the public bus `Boundary`.
- **Another sub-domain**: `Container(alias, "Name", "Sub-domain", "purpose")` +
  `UpdateElementStyle(alias, $bgColor="rgba(109,174,109,0.15)", $fontColor="#2E6B2E", $borderColor="#6DAE6D")`.
  Boxes, not boundaries, because only shapes share a row: `c4BoundaryInRow` is global, so two
  boundaries cannot sit side by side without breaking the vertical stack. The dashed border comes
  from a `themeCSS` rule in the YAML header of the block (Mermaid drops it from an `%%{init}%%`
  directive); a renderer that ignores the header draws the border solid, still green:

  ```text
  ---
  config:
    themeCSS: "rect[stroke=\"#6DAE6D\"] { stroke-dasharray: 7 7; stroke-width: 1px; }"
  ---
  ```

- **Bottom of the view**: a shape declared directly in a boundary is drawn before its child
  boundaries, so the bottom boxes sit in an invisible `Boundary(others, " ", " ")`
  (`$bgColor`, `$fontColor` and `$borderColor` `"transparent"`) declared after the private bus band.
- **Row breaks**: Mermaid 11.4.1 starts a new row when a shape would be the `N+1`th of the row, or
  would end past the viewer's screen width (`screen.availWidth`), and does not reset its count between
  two sibling boundaries. `N` is therefore chosen per view, the smallest value from 4 up that keeps the
  buses of a band on one row and the bottom boxes on one row. A viewer with a narrower screen than
  1800 px may still see a row break.
- **Labels**: Mermaid draws a label with its left edge on the middle of its line, so labels overlap
  cards and each other. Each label that would overlap is moved with
  `UpdateRelStyle(from, to, $offsetX="…", $offsetY="…")` to a free spot along its line. The offsets
  are computed from the rendered geometry, never by hand, and are recomputed after any change to the
  elements or the relations.

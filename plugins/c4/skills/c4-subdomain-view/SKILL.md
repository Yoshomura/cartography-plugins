---
name: c4-subdomain-view
description: Generate the C4 Level 2 view of one sub-domain (a "sub-domain view", "focus view" or "C4 detail" of a bounded context) from one JSON model, as a Mermaid block (rows fitted, relation labels moved off the cards) and as a draw.io file (automatic layout, orthogonal routing, publish / subscribe colours, messages as bullets, stores and data sinks out of the band). Use when someone asks for the C4 of a sub-domain or bounded context, a focus or detail view, to regenerate or update a sub-domain view after a change, to add a message, a container or a link to one, or to produce its draw.io. Builds on c4-diagrams (design system and drawing library); for a complete system view or a Level 1, use c4-diagrams.
license: MIT
---

# C4 sub-domain view

One sub-domain in focus, every link in or out of it, from a single model: `models/<sd>.json`
(format: `references/model.md`), the single source of the view. One command writes both outputs:

```bash
python scripts/subdomain_view.py all models/<sd>.json
```

| Output | Written to (from the current directory) |
|---|---|
| Mermaid view | `architecture/mermaid/c4-<sd>.md`: its ```` ```mermaid ```` block is replaced (notes and open questions kept); a new view gets its reading rules, notes and open questions from the model |
| draw.io | `architecture/drawio/c4-<sd>.drawio` |

`--mermaid-dir` and `--drawio-dir` change the folders; `mermaid` or `drawio` instead of `all` writes
one output only. `<sd>` is the model's file name. No HTML view: the draw.io is the reference.
Never edit the Mermaid block or the generated draw.io of a sub-domain view by hand: change the
model, then run the command, so the two outputs never drift apart.

Example: `examples/ordering.json`, the Ordering sub-domain of an online shop.

The design system is the `c4-diagrams` skill's `references/notation.md` (section "Sub-domain view"
and the draw.io / Mermaid tables); the drawing library is its `scripts/c4lib.py`. This skill holds no
colour or style of its own: a change to the look goes there first.

## Requirements

- **draw.io output**: Python 3 standard library only. draw.io Desktop exports it to PNG for review.
- **Mermaid output**: Node.js and Playwright (`scripts/mermaid_c4.cjs` renders with Mermaid 11.4.1,
  loaded from `cdn.jsdelivr.net`, in a headless browser). `C4_PLAYWRIGHT_DIR` points to a folder
  whose `node_modules` holds Playwright; `C4_BROWSER` picks a Playwright channel (`msedge`,
  `chrome`), else Playwright's own Chromium, else the installed Edge or Chrome. Without them, `all`
  writes the draw.io and reports the Mermaid view as not written.

## Workflow

1. **Model.** Start from the existing model. For a sub-domain that exists only as a Mermaid view
   written in the same layout, bootstrap it: `python scripts/from_mermaid.py <view.md> >
   models/<sd>.json` (bootstrap only: rerun on an existing model, it would overwrite what the model
   holds beyond the Mermaid view, such as exact names, data sinks and cache accesses). For a new
   sub-domain, write the model from the code: name the source of every element and link. Never invent
   a message name: a compressed name list (`price, stock _changed`) stays one bullet until the exact
   names are found.
2. **Generate.** Run the `all` command. The Mermaid part picks the shapes per row that keep the
   buses of a band and each row of sub-domain boxes together, moves the relation labels off the
   cards, and reports the texts still drawn over each other (`overlaps 0` is the target).
3. **Review the draw.io.** Export and look at it:
   `draw.io -x -f png -s 1 -o render.png architecture/drawio/c4-<sd>.drawio`. The report gives
   `unrouted` (must be 0), `labels over a card or another label`, `line crossings` and `bends`. A busy
   sub-domain keeps crossings: the generated file is then a base to finish by hand in draw.io, and a
   hand-finished file is never regenerated over without asking.
4. **Deliver.** Nothing is published or committed without the human's go.

## What the generator encodes (sub-domain view rules)

- Top: other sub-domains that exchange through the public bus (inside a second system boundary) and
  externals that only talk through the public bus; then the public bus, full width.
- Middle: the focus band and its containers; externals with direct links sit in a column right of the
  system, so a call never crosses a bus.
- Below the band: one database per sub-domain and per technology; the accesses of the services to it
  become one link band → store, "Data access [protocol]:" then "• service : verb" per line. The model
  keeps each access as its own link; the generator merges them. A data sink (`"kind": "datasink"`)
  sits right below the store it exports; the externals it feeds sit level with it.
- Bottom: the private buses side by side, then the sub-domains reached through them or by a direct
  link; a corridor at the right of the private buses carries the calls to those sub-domains.
- Another sub-domain is one green dashed box, never its containers; drawn twice (top and bottom)
  when it uses both sides.
- At most two lanes per element–bus pair, one per direction: publish / send in vermillion, head on
  the bus; subscribe / receive in blue, head on the element; each lane lists its messages as bullets
  under the element name and the verb phrase, whose brackets give the bus scope, the kind and the bus
  technology ("ordering-worker Publishes [PUBLIC event KAFKA]:", "ordering-worker Sends [PRIVATE
  command SNS]:", "ordering-api Subscribes to [event REDIS]:"). Direct links are solid grey,
  labelled `verb phrase [protocol]`.
- Redis pub/sub channels are a bus; Redis keys are a distributed cache, a store reached by data
  access links ("Data access [Redis]:"), never a lane. The generator refuses a `Redis key` message.
- Every label is centred on its own line; it goes beside the line only when no centred spot is free.
  Its outline takes the colour and the style of its line, and two labels keep 20 px of vertical space.
- Routing: few long straight runs; a call leaves its card by the side facing its dominant direction.

## Mermaid limits (11.4.1)

Rows wrap at the viewer's screen width, the shapes-per-row counter is not reset between sibling
boundaries, `Rel_U/D/L/R` have no effect, and a label has no line break: these are why the generator
fits rows and offsets labels instead of trusting the layout. `C4_SCREEN` sets the screen width of the
render (1800 by default).

## Files

All paths below are relative to this skill's folder.

- `scripts/subdomain_view.py` - model to Mermaid view and to draw.io (layout, A* orthogonal router, label placer).
- `scripts/from_mermaid.py` - model from an existing Mermaid sub-domain view.
- `scripts/mermaid_c4.cjs` - `render`, `geometry`, `overlaps`, `place` on a Mermaid diagram.
- `references/model.md` - the model format.
- `examples/ordering.json` - example model.

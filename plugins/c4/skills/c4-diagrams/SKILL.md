---
name: c4-diagrams
description: Design, draw and convert C4 architecture diagrams (Level 1 System Context, Level 2 Containers) in one notation, in three formats - Mermaid (design, reverse engineering), draw.io (reference and presentation) or a self-contained HTML view - all from the single design system in references/notation.md. Use when someone asks for a C4 diagram, an architecture diagram, a container diagram or a system context, to reverse engineer an architecture from code, to add a container, a sub-domain or a link to a C4 diagram, or to convert a C4 diagram between draw.io, Mermaid and HTML, even if they do not say "C4". For the view of one sub-domain with every link in or out of it, use c4-subdomain-view.
license: MIT
---

# C4 diagrams

Business-agnostic and technology-agnostic: the notation names no domain, no product and no brand;
its examples use an online shop.

The design system (colours, shapes, wording, buses) lives in one file: `references/notation.md`.
Read it before drawing in any format. Never define a colour, shape or wording rule anywhere else;
when the design system changes, it changes there first, then in `scripts/c4lib.py` and
`scripts/c4drawio.py`, and in the generator of the `c4-subdomain-view` skill.

## Formats, and who chooses

| Format | Use it for | How |
|---|---|---|
| Mermaid (`C4Context`, `C4Container`) | **Design**: sketching, reverse engineering from code, a first version to discuss. Also a presentation when an automatic layout is acceptable | written by hand, section "Mermaid" of the notation |
| draw.io | **Reference and presentation**: the versioned diagram, a hand-arranged layout | generator script + `Doc.write_drawio`, or hand edit of an existing file |
| HTML | **Presentation view** derived from the same generator script, opened in any browser | `Doc.write` |

The `.drawio` is the reference; Mermaid and HTML are views of it or drafts toward it. A typical
path: design in Mermaid, have it validated, then lay it out with a generator script that writes the
draw.io (and the HTML when wanted).

**When the expected format is not stated, or the request fits more than one row, ask before
drawing**: which format, and for a presentation whether Mermaid's automatic layout is acceptable or
a draw.io layout is expected. Never pick by default.

## Workflow

1. **Collect the model**: elements (name, type, technology, one-line description), sub-domains,
   relationships (source, target, verb phrase, protocol, sync or message). From a draw.io file:
   `python scripts/drawio_import.py file.drawio > model.json`, then read the JSON (edges with a null
   source or target are legend samples, drop them). From code: name the source of every element and
   link; a missing fact is an open question, never a guess.
2. **Mermaid**: write the `.mmd` (or the ```` ```mermaid ```` block of a document) following the
   notation's Mermaid table. Model: `examples/context_level1.mmd`.
3. **draw.io and HTML**: write a generator script modelled on `examples/context_level1.py`. Lay out on
   the grid: 320 px column pitch, 180 px row pitch, 64 px margins; externals left and right of the
   boundary, sub-domain bands inside, private bus band at the bottom. Plan lanes (vertical gaps
   between columns) before writing arrows. Cards via `card(...)`, buses via `d.bus(...)`, links via
   `route([...points...])` (orthogonal only, a diagonal raises; `color=PUBLISH` or `color=SUBSCRIBE`
   on a bus lane), labels via `L(...)` (a newline is a line break, for bullet lists).
4. **Run it and check the geometry report**: `card-crossings` must be 0. Fix a card crossing by moving
   a lane into a column gap.
5. **Check the draw.io rendering**: export it to PNG with draw.io Desktop
   (`draw.io -x -f png -s 1 -o render.png file.drawio`) and look at it; label heights are estimated, a
   long label may need a wider box.
6. **Deliver**: set `C4_OUT` to the folder that must receive the files, run the script: it writes
   `<name>.html` and `<name>.drawio` there (without `C4_OUT`, into `<system temp>/c4-diagrams`, never
   the working tree). A file that must be versioned is copied where the human says.

## Rules that are easy to get wrong

- Classic C4 colours only for elements; neutral chrome. Do not invent a new colour for a new kind of box.
- Every arrow has a label `verb phrase [protocol]`. Labels are white pills, never on a card.
- Messaging never becomes a coloured arrow between two containers: it becomes a lane on the private or
  public bus, with the message names in the lane label. One head per arrow, at most two lanes per
  element–bus pair, one per direction, vermillion to the bus and blue from it.
- Redis pub/sub channels are a bus; Redis keys are a distributed cache, a data store.
- Containers that exist in several repositories (service + worker pairs) are separate cards; the
  sub-domain band groups them.
- Level 1 never shows technologies or sub-domains; Level 2 shows both.

## Changing a diagram

- **Generated diagram**: edit its generator script, never the HTML or the generated `.drawio`; rerun,
  confirm `card-crossings 0`. When a sub-domain passes six containers, split it into its own Level 2
  diagram ("Container diagram for <system> - <sub-domain>", see the `c4-subdomain-view` skill)
  instead of growing the band.
- **Existing hand-made `.drawio`**: edit it by hand, keeping every element and waypoint the request
  does not name. Regenerating a generator script over it would discard its hand layout: ask before.

## Files

All paths below are relative to this skill's folder.

- `references/notation.md` - the design system: colours, shapes, wording, buses, draw.io styles, Mermaid mapping, sub-domain view.
- `scripts/c4lib.py` - `Doc` class: `card`, `bus`, `route` (and raw `h`/`v` segments), `label`, `boundary`, `subdomain`, `title`, `legend`, `footer`, `write(path)`, `write_drawio(path)`.
- `scripts/c4drawio.py` - draw.io renderer behind `write_drawio`: same layout, C4 attributes, nesting, attached edges.
- `scripts/drawio_import.py` - draw.io to JSON model.
- `examples/context_level1.py` - Level 1 of an online shop; writes HTML and draw.io, with the geometry check.
- `examples/context_level1.mmd` - the same Level 1 in Mermaid.

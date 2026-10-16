---
name: cartography
description: The format of this repository's cartography artifacts - map.md, details/<USE-CASE>.md and refusals.md - with their templates and a validator. Cartography is reverse engineering of an existing system, from its code in any language or from a functionality observed or described, compared with a specification organized by feature, use case, scenario, rule and invariant. Use when writing, refreshing or reviewing any of those three files, and to check that a set of them still conforms.
license: MIT
---

# Cartography format

**Format version 2.0.0.** Business-agnostic and technology-agnostic: no domain term, no
language and no folder convention appears in this skill or in its templates.

This skill holds the **shape** of the three cartography artifacts. It does not hold the
judgment that fills them, which belongs to the cartographer agent. The two are separated
because they change at different rates: the shape is versionable and checkable, the judgment
is prose and moves rarely.

| File | What it answers |
|---|---|
| `docs/map.md` | Where is what, what enters, what leaves |
| `docs/details/<USE-CASE>.md` | What the implementation of one use case does, and the rules it applies |
| `docs/refusals.md` | What comes back when this deployable says no |

## Two sources, one format

Cartography is reverse engineering: it describes a system that already exists, from what can
be observed of it. The frontmatter key `source` says what was observed, and one set shares one
source.

| `source` | Observed | The implementation is |
|---|---|---|
| `code` (the value when the key is absent) | existing code, any language | the path of the **existing** file implementing the use case, never a file to create |
| `functionality` | a product studied from the outside, a user interface, network traffic, a specification, documentation | an implementation **name**, the title of the use case, unique in the set, never a path |

## Writing or refreshing one

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/cartography/references/format.md`. It is the
   specification: frontmatter keys, sections and their order, column meanings, the summary
   rules, the banned vocabulary, and what changes with the source.
2. **Copy the matching template from `${CLAUDE_PLUGIN_ROOT}/skills/cartography/references/`**,
   the one for the set's source, do not reproduce the shape from memory.
   Everything that is not a data row is then exact by construction.

   | Artifact | Source `code` | Source `functionality` |
   |---|---|---|
   | map | `map.code.template.md` | `map.functionality.template.md` |
   | detail entry | `detail-entry.code.template.md` | `detail-entry.functionality.template.md` |
   | refusals | `refusals.code.template.md` | `refusals.functionality.template.md` |
3. Fill the rows. Leave every heading, source line and blockquote untouched: the validator
   compares the blockquotes character for character, against the set of the file's source.
4. Run the validator before you finish.

## Checking a set

```
python "${CLAUDE_PLUGIN_ROOT}/skills/cartography/scripts/validate.py" docs
```

Run it from the repository whose `docs/` you are checking. The argument is that repository's
documentation folder.

Exit 0 when everything conforms, 1 otherwise. It reports missing or unexpected frontmatter
keys, an unknown `source` or one that differs from the map's, a frontmatter field that locates
another repository, a reworded blockquote or source line, sections renamed or out of order, a
malformed scenario counter, an implementation that is not a file path (source `code`) or that is a path or
a duplicate name (source `functionality`), a malformed anchor (source `functionality`), a
summary over 120 characters, an unknown refusal mechanism, a detail entry no map row links to,
and any banned vocabulary.

**It checks the form, never the content.** A conforming file can still be wrong about the
system: what these artifacts say is inferred, and stays outside any gate. Their shape is not
inferred, so a failing shape can block.

## The two rules behind the format

**Observation, never specification.** Every sentence of `What it does` must be refutable by
reading one precise place in the code, or by one precise observation of the functionality.
No purpose, no judgment, no completion. `What it answers` is where the specification lives.
`references/format.md` lists the banned vocabulary and the validator enforces it. The
judgment behind it belongs to the `cartographer` agent this plugin also ships.

**Nothing locating another repository.** No path into the specification, no commit
SHA of it. The use case identifier is the whole cross-repository coordinate, and it is the join key
for whoever holds both.

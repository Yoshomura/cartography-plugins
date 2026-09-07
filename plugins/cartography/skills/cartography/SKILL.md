---
name: cartography
description: The format of this repository's cartography artifacts - map.md, details/<SCENARIO>.md and refusals.md - with their templates and a validator. Use when writing, refreshing or reviewing any of those three files, and to check that a set of them still conforms.
license: MIT
---

# Cartography format

**Format version 1.0.0.** Business-agnostic: no domain term appears in this skill or in its
templates.

This skill holds the **shape** of the three cartography artifacts. It does not hold the
judgment that fills them, which belongs to the cartographer agent. The two are separated
because they change at different rates: the shape is versionable and checkable, the judgment
is prose and moves rarely.

| File | What it answers |
|---|---|
| `docs/map.md` | Where is what, what enters, what leaves |
| `docs/details/<SCENARIO>.md` | What one usecase does, and the rules it applies |
| `docs/refusals.md` | What comes back when this deployable says no |

## Writing or refreshing one

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/cartography/references/format.md`. It is the
   specification: frontmatter keys, sections and their order, column meanings, the summary
   rules, the banned vocabulary.
2. **Copy the matching template from `${CLAUDE_PLUGIN_ROOT}/skills/cartography/references/`**,
   do not reproduce the shape from memory.
   Everything that is not a data row is then exact by construction.
   - `map.template.md`
   - `detail-entry.template.md`
   - `refusals.template.md`
3. Fill the rows. Leave every heading, source line and blockquote untouched: the validator
   compares the blockquotes character for character.
4. Run the validator before you finish.

## Checking a set

```
python "${CLAUDE_PLUGIN_ROOT}/skills/cartography/scripts/validate.py" docs
```

Run it from the repository whose `docs/` you are checking. The argument is that repository's
documentation folder.

Exit 0 when everything conforms, 1 otherwise. It reports missing or unexpected frontmatter
keys, a frontmatter field that locates another repository, a reworded blockquote, sections
renamed or out of order, a malformed case counter, a summary over 120 characters, an unknown
refusal mechanism, a detail entry no map row links to, and any banned vocabulary.

**It checks the form, never the content.** A conforming file can still be wrong about the
code: what these artifacts say is inferred, and stays outside any gate. Their shape is not
inferred, so a failing shape can block.

## The two rules behind the format

**Observation, never specification.** Every sentence must be refutable by reading one precise
place in the code. No purpose, no judgment, no completion. `references/format.md` lists the
banned vocabulary and the validator enforces it. The judgment behind it belongs to the
`cartographer` agent this plugin also ships.

**Nothing locating another repository.** No path into the documentation repository, no commit
SHA of it. The scenario ID is the whole cross-repository coordinate, and it is the join key
for whoever holds both.

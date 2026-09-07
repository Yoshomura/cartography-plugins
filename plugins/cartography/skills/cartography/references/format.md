# Cartography format — specification

Format version **1.0.0**. Normative for the *shape* of the three artifacts, and only for the
shape. What they say is the cartographer's judgment; how they are laid out is this file.

Nothing here is business-specific. No domain term appears in this document or in the
templates beside it: that is what lets this skill be used as-is by another company, which is
the criterion the architecture directives set for a technical library.

---

## The three artifacts

| File | Kind | Read |
|---|---|---|
| `docs/map.md` | `map` | Whole. The index |
| `docs/details/<SCENARIO>.md` | `detail-entry` | One at a time |
| `docs/refusals.md` | `refusal-surface` | Whole |

---

## Header of every file

Two parts, and the split is the point: **YAML frontmatter for what a machine reads, one
visible blockquote for what a reader needs.**

### Frontmatter

Valid YAML, plain `key: value` lines only. No nesting, no list.

| Key | All files | Value |
|---|---|---|
| `kind` | yes | `map`, `detail-entry` or `refusal-surface` |
| `normative` | yes | always `false` |
| `generator` | yes | always `cartographer` |
| `base` | yes | commit SHA of **this** repository at the last pass. **Empty on a first pass** |
| `repository` | map, refusal-surface | this repository's name |
| `scenario` | detail-entry | the scenario ID, **may be empty** when the usecase answers none |
| `usecase` | detail-entry | path to the usecase file, from the repository root |

**Nothing locating another repository goes in the frontmatter.** No path into the
documentation repository, no commit SHA of it. A field this repository can neither resolve nor
verify rots without saying so. The scenario **ID** is the whole cross-repository coordinate,
and it is the join key whoever holds both repositories uses.

An unknown `base` is an **empty value**, never a sentence in parentheses: it must stay valid
YAML, because the next pass parses it to compute its delta. When it is empty, the body says
so in one line.

### The blockquote

One blockquote, immediately under the title, **copied from the template character for
character**. The validator compares it exactly.

It is repeated in every detail entry, so it stays at two or three lines: a paragraph repeated
two hundred times stops being read. It carries the **distinction** — the scenario says what
should happen, this file says what the code does — never the **procedure**: how a divergence
is settled is a rule, written once in the directives, not copied into every file.

---

## `map.md`

Sections, in this order, none omitted:

`## Usecases` · `## Inbound` · `## Outbound` · `## Anchors` · `## Unattached`

### Usecases

Four columns: `Scenario | Cases | Usecase | What it answers`.

- **Scenario** is a markdown link to `details/<ID>.md`. A usecase answering no scenario shows
  `?` and links to its detail entry all the same
- **Cases** is `declared/covered/tested`, three integers, no spaces around the slashes.
  Declared comes from the scenario table and tested from the tests' `DisplayName`: both exact.
  Covered is observed in the usecase, therefore inferred
- **Usecase** is a **file** path. Every other coordinate in these artifacts is a folder; the
  hexagon is the exception, because it has no per-usecase folder and `Application/` stops
  being an address once a deployable holds forty usecases
- **What it answers** is one sentence, **120 characters at most**, no subordinate clause

### The summary sentence

Four rules, and the last one is the test:

1. It says the **need**, not the mechanism
2. It is the compression of the detail entry's `What it answers`, which comes from the
   scenario. Same source, two lengths, so the two cannot drift
3. It carries no port, message or contract name: those are in Inbound and Outbound
4. **It must stay true when the implementation changes.** If it moves on every refactor, it
   was a summary of the code and it is wrong

### Inbound, Outbound

`Trigger | Nature | Usecases | Folder` and `What goes out | Nature | Usecases | Folder`.

**Indexed by the dependency, not by the usecase**, deliberately: a contract that changes must
be read on one line. This inverts the Usecases table on purpose.

### Anchors

`Folder | Tree SHA`, one row per folder any coordinate points at, so a reader arriving at a
coordinate can tell it is stale without a pass being run. `git rev-parse HEAD:<folder>`.

### Unattached

Folders holding code attached to no scenario, named one by one. Folders holding no
functionality — launch settings, composition root, project files — are **counted, never
listed**. That is what keeps the file bounded as the deployable grows.

---

## `details/<SCENARIO>.md`

One file per scenario ID, bearing that ID as its name. Nobody reads them all: the map says
which one to open.

Sections, in this order, none omitted:

`## What it answers` · `## What it does` · `## The rules it applies` · `## What it needs` ·
`## What it produces` · `## Observed divergences`

**The first two blocks are sourced separately and never merged.** Each opens on its source
line, copied exactly:

```
## What it answers
> Source: the scenario. Compressed, not inferred.

## What it does
> Source: the code. Observed, not interpreted.
```

That separation is what makes a divergence readable without leaving the file: it is the
difference between the two blocks.

`What it answers` is the only sentence in the file that speaks of a need, and it does not come
from the code. Where there is no scenario, it says so, holds only what the code shows, and is
marked `?`.

`The rules it applies` is the density the whole mechanism exists to expose. Columns
`# | Rule | Case`, one row per rule observed, in functional terms, with the case it answers or
an empty cell when it answers none. **An empty cell is a finding**: carry it down to
divergences.

`Observed divergences` is the product of the file. `None.` when there are none.

---

## `refusals.md`

Sections, in this order, none omitted:

`## Mechanisms` · `## Business refusals` · `## Adapter refusals` · `## Translation` ·
`## Divergences`

Indexed by the **refusal**, not by the exception. **Not every refusal raises an exception, and
that is the point of the file**: a refusal returned as an outcome, or decided silently, is
invisible everywhere else.

The `Mechanism` column takes one of exactly four values:

| Mechanism | What it means |
|---|---|
| Business exception | Raised in the hexagon, translated by an inbound adapter |
| Returned outcome | No exception: the treatment returns a state the adapter turns into a refusal |
| Silent no-op | No exception, no signal: the treatment decides not to act |
| Adapter | Never reaches the usecase: contract, routing, authorization |

Business refusals carry `Refusal | Mechanism | Exception | Code | Cases | Usecases |
Raised in | Caller sees`.

`Mechanism` and `Exception` are two different things and never share a column: the mechanism
says how the refusal becomes visible, the exception says which type carries it. A refusal
whose mechanism is not `Business exception` has no exception, by definition of the four
values, and that cell reads an em dash.

**The code is independent of the mechanism.** A code is what leaves the deployable on the
wire, in a response body and in a log, and that is the whole reason this file is allowed to
name one. A refusal returned as an outcome and turned into a status with a code by its
adapter carries a code and no exception. Only a refusal that emits nothing at all has
neither.

`Caller sees` is an HTTP status in an API, and an acknowledgement, a rejection or a dead
letter elsewhere.

**This is the one artifact allowed to name code**: exception types and error codes, and
nothing else. They are the published vocabulary of refusal, they leave the deployable on the
wire, and no normative document holds them. Everywhere else the ban is total.

---

## Vocabulary banned in every body

Checked mechanically by the validator, outside the boilerplate blockquotes.

| Banned | Why |
|---|---|
| `in order to`, `so that`, `because`, `to prevent` | Purpose and cause. The code does not carry its intention; writing it is inventing it |
| `correctly`, `properly`, `should`, `redundant`, `unnecessary` | Judgment. That is the human ruling, and it belongs in the specification |
| `presumably`, `seems intended`, `likely`, `probably` | Completion. Code silent on a point leaves the cartographer silent, or marking `?` |

The test behind all three, applied sentence by sentence: **a sentence must be refutable by
reading one precise place in the code.** If no coordinate makes it true, it is an
interpretation and it goes.

---

## What the validator does not check

It checks the **form**, never the **content**. That a file has valid frontmatter, its sections
in order and no banned word says nothing about whether the map is right.

The distinction matters because the directives forbid these artifacts from ever being a
blocking gate. That ban is about their **findings**, which are inferred and probabilistic. The
shape is neither: it can be checked, and a failing shape can block.

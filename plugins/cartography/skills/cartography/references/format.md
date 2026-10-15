# Cartography format — specification

Format version **1.1.0**. Normative for the *shape* of the three artifacts, and only for the
shape. What they say is the cartographer's judgment; how they are laid out is this file.

Nothing here is business-specific, and nothing here is technology-specific. No domain term,
no language, no framework and no folder convention appears in this document or in the
templates beside it: that is what lets this skill be used as-is by another company, on
another stack, which is the criterion the architecture directives set for a technical
library.

---

## Cartography is reverse engineering

Every cartography describes a system that already exists, from what can be observed of it. It
has two sources, and they are equal variants of the same work:

| `source` | What is read | The usecase is | Example |
|---|---|---|---|
| `code` | Existing code, in any language | the **path of the existing file** implementing it | `src/orders/place_order.py`, `app/Billing/CreateInvoice.kt` |
| `functionality` | A functionality observed or described, with no code to read: a product studied from the outside, a user interface, network traffic, a specification, documentation | a **usecase name**, unique in the set | `Sign in`, `Report an incident` |

The source is declared in the frontmatter of every file of a set, and the whole set shares one
source: the map declares it, the detail entries and the refusal surface follow. An absent
`source` reads `code`, which is what every artifact written before format 1.1.0 is.

**A usecase path points at existing code only.** It is never the path of a file to create, of
a target implementation, or of a file nobody has read. With no code to read, the source is
`functionality` and the usecase is a name: a path to a file that does not exist would be an
invention.

**A usecase name is unique.** With source `functionality` the name is the usecase's only
identity, so two usecases never share it: compared case-insensitively, backticks and
surrounding spaces trimmed, a name appears once in the map's Usecases table and once across
the detail entries' `usecase` keys. The name is chosen as part of the specification: short, in
the vocabulary of the need, a verb and its object (`Sign in`, `Report an incident`).

Any architecture fits. A hexagonal codebase, with its usecases in an application layer and its
adapters around them, is one example the vocabulary below borrows from (inbound, outbound,
adapter); it is not a requirement.

---

## The three artifacts

| File | Kind | Read |
|---|---|---|
| `docs/map.md` | `map` | Whole. The index |
| `docs/details/<SCENARIO>.md` | `detail-entry` | One at a time |
| `docs/refusals.md` | `refusal-surface` | Whole |

Each has one template per source in `references/`: `<artifact>.code.template.md` and
`<artifact>.functionality.template.md`.

---

## Header of every file

Two parts, and the split is the point: **YAML frontmatter for what a machine reads, one
visible blockquote for what a reader needs.**

### Frontmatter

Valid YAML, plain `key: value` lines only. No nesting, no list.

| Key | Files | Required | Value |
|---|---|---|---|
| `kind` | all | yes | `map`, `detail-entry` or `refusal-surface` |
| `normative` | all | yes | always `false` |
| `generator` | all | yes | always `cartographer` |
| `source` | all | no | `code` or `functionality`. **Absent reads `code`**. Same value in every file of a set |
| `base` | all | yes | commit SHA of **this** repository at the last pass. **Empty on a first pass** |
| `repository` | map, refusal-surface | yes | this repository's name |
| `scenario` | detail-entry | yes | the scenario ID, **may be empty** when the usecase answers none |
| `usecase` | detail-entry | yes | source `code`: path to the existing usecase file, from the repository root, any language. Source `functionality`: the usecase name, unique, no path, no extension |

**Nothing locating another repository goes in the frontmatter.** No path into the
documentation repository, no commit SHA of it. A field this repository can neither resolve nor
verify rots without saying so. The scenario **ID** is the whole cross-repository coordinate,
and it is the join key whoever holds both repositories uses.

An unknown `base` is an **empty value**, never a sentence in parentheses: it must stay valid
YAML, because the next pass parses it to compute its delta. When it is empty, the body says
so in one line.

### The blockquote

One blockquote, immediately under the title, **copied from the template of the file's source
character for character**. The validator compares it exactly, against the set of its source.

It is repeated in every detail entry, so it stays at two or three lines: a paragraph repeated
two hundred times stops being read. It carries the **distinction** — the scenario says what
should happen, this file says what the code or the functionality does — never the
**procedure**: how a divergence is settled is a rule, written once in the directives, not
copied into every file.

The exact texts:

| Kind | Source `code` | Source `functionality` |
|---|---|---|
| `map` | `> **Not normative, and inferred.** Where things are, never what they should be. ...` | identical |
| `detail-entry` | `... this file says` / `> what the code does. ...` | `... this file says` / `> what the functionality does, as observed or described. ...` |
| `refusal-surface` | `... its mechanism` / `> is decided in the code and only observed here. ...` | `... what the` / `> functionality shows when it refuses is only observed here. ...` |

The templates hold them in full, line breaks included; copy them from there.

---

## `map.md`

Sections, in this order, none omitted:

`## Usecases` · `## Inbound` · `## Outbound` · `## Anchors` · `## Unattached`

### Usecases

Four columns: `Scenario | Cases | Usecase | What it answers`.

- **Scenario** is a markdown link to `details/<ID>.md`. A usecase answering no scenario shows
  `?` and links to its detail entry all the same
- **Cases** is `declared/covered/tested`, three integers, no spaces around the slashes.
  Declared comes from the scenario table and tested from the test names or identifiers
  carrying the case ID, whatever the test framework (a display name, a test method name, a
  tag, a test title): both exact. Tested is `0` when no test exists, which is common with
  source `functionality`. Covered is observed in the usecase, therefore inferred
- **Usecase**, source `code`, is a **file** path to existing code, any language, with its
  extension. Every other coordinate in these artifacts is a folder; the usecase is the
  exception, because a usecase layer rarely has one folder per usecase, and a folder holding
  forty usecases stops being an address
- **Usecase**, source `functionality`, is the **usecase name**, unique in the set. Anything
  holding a `/` or ending on a file extension is refused
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

With source `code` the last column is the folder holding the entry point or the adapter. With
source `functionality` it is the **observed coordinate**: a screen, a URL path, a document
section, a module of a binary. It is never a folder to create.

### Anchors

`Folder | Tree SHA`, one row per coordinate any other cell points at, so a reader arriving at a
coordinate can tell it is stale without a pass being run.

- Source `code`: `git rev-parse HEAD:<folder>`
- Source `functionality`: there is no tree to hash. The cell reads `— observed YYYY-MM-DD`,
  an em dash followed by the date the coordinate was last observed. A coordinate held in this
  repository (a captured document, a recording) may carry its tree SHA instead

### Unattached

Coordinates holding behavior attached to no scenario, named one by one. Coordinates holding no
functionality — launch settings, composition root, project files, a static page — are
**counted, never listed**. That is what keeps the file bounded as the deployable grows.

---

## `details/<SCENARIO>.md`

One file per scenario ID, bearing that ID as its name. Nobody reads them all: the map says
which one to open.

Sections, in this order, none omitted:

`## What it answers` · `## What it does` · `## The rules it applies` · `## What it needs` ·
`## What it produces` · `## Observed divergences`

**The first two blocks are sourced separately and never merged.** Each opens on its source
line, copied exactly. Source `code`:

```
## What it answers
> Source: the scenario. Compressed, not inferred.

## What it does
> Source: the code. Observed, not interpreted.
```

Source `functionality`:

```
## What it answers
> Source: the scenario. Compressed, not inferred.

## What it does
> Source: the functionality. Observed, not interpreted.
```

That separation is what makes a divergence readable without leaving the file: it is the
difference between the two blocks.

`What it answers` is the specification: the only sentence in the file that speaks of a need,
and it comes neither from the code nor from the observed functionality. Where there is no
scenario, it says so, holds only what the code or the functionality shows, and is marked `?`.

`What it does` is observation, never specification, whatever the source: what the code does,
or what the functionality was seen or described doing (a screen, a request and its response,
a document section). Never what it is meant to do.

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
| Business exception | Raised by the business logic, translated by an inbound adapter |
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

**What cannot be observed is not recorded.** With source `functionality` an exception type is
usually invisible and a code often is: the `Exception` and `Code` cells read an em dash
whenever the functionality does not show them, whatever the mechanism. `Raised in` holds the
usecase name, and the Translation table's last column the observed coordinate.

`Caller sees` is an HTTP status in an API, a message on a screen, an acknowledgement, a
rejection or a dead letter elsewhere.

**This is the one artifact allowed to name code**: exception types and error codes, and
nothing else. They are the published vocabulary of refusal, they leave the deployable on the
wire, and no normative document holds them. Everywhere else the ban is total.

---

## Vocabulary banned in every body

Checked mechanically by the validator, outside the boilerplate blockquotes, whatever the
source.

| Banned | Why |
|---|---|
| `in order to`, `so that`, `because`, `to prevent` | Purpose and cause. Neither the code nor the observed functionality carries its intention; writing it is inventing it |
| `correctly`, `properly`, `should`, `redundant`, `unnecessary` | Judgment. That is the human ruling, and it belongs in the specification |
| `presumably`, `seems intended`, `likely`, `probably` | Completion. A source silent on a point leaves the cartographer silent, or marking `?` |

The test behind all three, applied sentence by sentence: **a sentence must be refutable by
reading one precise place in the code, or by one precise observation of the functionality.**
If no coordinate makes it true, it is an interpretation and it goes.

---

## What the validator checks per source

| Check | Source `code` | Source `functionality` |
|---|---|---|
| Blockquote and source lines | the `code` set, exactly | the `functionality` set, exactly |
| Usecase (map column, `usecase` key) | a file path with an extension, any language; existence not checked | a plain name: refused when it holds `/` or `\` or ends on a file extension; refused when it appears twice (case-insensitive) in the map or across the detail entries |
| Anchors | not checked | a tree SHA, or `— observed YYYY-MM-DD` |
| Refusals: `Exception`, `Code` | an em dash always accepted | same |
| `source` of every file | equal to the map's | equal to the map's |

## What the validator does not check

It checks the **form**, never the **content**. That a file has valid frontmatter, its sections
in order and no banned word says nothing about whether the map is right. It does not check that
a usecase path exists either: the path is observation, and observation is content.

The distinction matters because the directives forbid these artifacts from ever being a
blocking gate. That ban is about their **findings**, which are inferred and probabilistic. The
shape is neither: it can be checked, and a failing shape can block.

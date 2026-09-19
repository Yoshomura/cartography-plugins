---
name: workflow-feature-spec
description: >-
  Turn one raw idea (an inbox .md file, a meeting note, or text dictated in conversation) into a
  functional specification at docs/specs/spec-<topic>.md through a mandatory challenge, then
  interview, then write sequence, and run the second pass that amends an existing specification
  with what the first pass left out. Use when asked to specify or design a feature idea, to work
  through an idea inbox, to turn a note into a specification, to run a second reading of a
  specification, or when a conception session starts. Do NOT use for writing tickets, publishing
  to a wiki or a tracker, or summarizing meeting transcripts.
license: MIT
---

# Turn a raw idea into a functional specification

The deliverable is exactly one functional specification at `docs/specs/spec-<topic>.md`, built
from the template. The specification is written in English; the conversation happens in the
user's language.

The word is **specification**. "Spec" survives only inside identifiers this skill cannot rename
without breaking the projects that pin it: the agent names, this skill's name, and the default
paths below.

## Two passes

| Pass | Agent | Input | Output |
|---|---|---|---|
| **First pass** | `spec-writer` | the raw idea | a new specification, or an amended one when the idea changes something already specified |
| **Second pass** | `spec-second-pass` | the idea and the specification the first pass wrote | the same file, amended with what the first pass left out |

The first pass is the whole sequence below: mode selection, challenge, interview, write. The
second pass is a fresh reading by another model, with its own rules in
[Second pass](#second-pass). A project may run only the first pass; running the second one
without the first has no meaning.

## Where things live

The paths and the template below are this skill's defaults. A project may override any of them
in its own instructions (its `CLAUDE.md`); when it does, the project's declaration wins.

| Role | Default |
|---|---|
| Idea inbox | `docs/Features TODO/` (any `.md` file the user points at) |
| Specification | `docs/specs/spec-<topic>.md` |
| Archived idea | `docs/archives/<year>/<topic>/notes-before-spec-<topic>.md` |
| Template | `${CLAUDE_PLUGIN_ROOT}/skills/workflow-feature-spec/references/spec.template.md` |

A project that declares its own template replaces the shipped one entirely: its sections, its
order, its wording. The rules of this skill that name a section (Decisions log, Open questions,
Out of scope, Facts) then apply to the project's equivalent of that section, and the project's
template says which. A project that has no idea inbox skips the archive step: the idea came
from the conversation and there is nothing to move.

The specification states business behavior, never a solution design: no invented endpoints,
schemas, message contracts, or service internals. Established domain facts may be cited as
facts: existing services, the project's reference material (enums, glossaries, published
studies, documentation pages), and its cartography when it has one. A technical concern with no
established answer becomes an entry in the specification's Open questions, never an invented
answer; it is settled downstream, by whoever derives work from the specification.

## Scope guard — one idea at a time

An inbox file may mix several ideas. If the request spans more than one, have the user pick one
and park the others. Bundling two ideas into one specification is how scope creep starts before
anything is published.

## Phase 0 — Mode selection (mandatory, before anything else)

The first pass runs in one of two modes, chosen by the user at the very start:

- **interactive** — the challenge and the interview happen live, one question at a time
  (AskUserQuestion when available). This is the richest mode; use it whenever the user can
  answer in real time.
- **silent** — no interactive call before the specification file is complete. The challenge is
  conducted internally and its outcome is recorded in the Decisions log (alternatives
  considered, why the fixed inputs win or an open question remains). Every question the
  interview would have asked becomes a self-contained entry in the Open questions section:
  enough context to be answered asynchronously, plus options and a recommendation when one is
  defensible. The specification is written in one pass from the fixed inputs only. **Then, once
  the file is finished**, pose the collected open questions to the user in one interactive
  round (best effort): if the user is at the screen, integrate the answers immediately
  (Decisions log updated, answered entries removed from Open questions) and the specification
  can reach 100%; if the user does not answer or no channel is available, the specification
  stands as written and is resumed later from its Open questions.

The mode is never defaulted. If the invocation does not state it, ask for it as the very
first question and wait. In silent mode the hard rules do not relax: a gap is still an open
question, never an invented answer.

## Phase 1 — Challenge (mandatory, before any detail question)

Read the idea, the project's own instructions and its glossary when it has one, then present a
challenge covering, in order:

1. **Domain collisions**: which established domain facts (reference material, existing
   studies, published pages, the existing behavior the cartography describes) the idea touches
   or contradicts, and how. Name each source.
2. **Internal contradictions** within the idea itself.
3. **A simpler alternative** reaching the same business outcome, if one exists.
4. **Value**: what problem this solves, for whom, and what is lost if it is never built.

Do not soften the challenge. If the user drops the idea after it, stop; nothing is written. An
idea that has not been challenged must not be specified.

In silent mode the challenge still runs, internally: its outcome lands in the Decisions log,
and anything it cannot settle from the fixed inputs becomes an Open questions entry.

## Phase 2 — Interview (interactive mode) / Open questions conversion (silent mode)

In silent mode there is no interview: skip to Phase 3 and convert every question this phase
would have asked into an Open questions entry as defined in Phase 0.

In interactive mode: one question at a time, each with proposed options and a recommendation
when one is defensible. Continue until zero ambiguity remains on business rules, edge cases,
worked examples, and scope boundaries. Three hard rules:

- **Never fill a gap with a plausible assumption.** A gap is either a question to the user or
  an entry in the Open questions, never an invented rule presented as acquired.
- **Never settle an open reflection.** Present the options with a short recommendation and let
  the human choose.
- **Every decision lands in the Decisions log**, phrased as the user settled it.

Apply the project's naming conventions and glossary throughout when it declares them.

## Phase 3 — Write

Fill the template:

- One business rule = one sentence, numbered. No prose padding.
- Every non-trivial rule gets a worked example using values the user validated (in silent
  mode: plausible placeholder values, flagged as an Open questions entry for validation).
- Facts are separated from decided rules, each fact with its source.
- Fact labels are human-readable: write `**Fact 1**`, `**Fact 2**`… never the abbreviated
  form `**F1**`, in the Facts section and in every cross-reference (rules, decisions log,
  edge cases).
- A source that has a URL is cited as a clickable markdown hyperlink, `[Title](URL)`, never as
  a bare title plus an identifier. Use the URL the source was provided with; never invent one.
- Facts state the final consolidated truth, never a correction trail. When a fact turns out
  wrong or superseded, rewrite it in place so it reads as the current state on its own: no
  "amended", "obsolete", "supersedes Fact N" narration, no addendum facts pointing back at
  the fact they fix. The history of what changed and why belongs to the Decisions log only.
  Exception: an UNRESOLVED conflict between sources keeps both versions inside one fact
  (surface, don't resolve) until the human settles it.
- Out of scope lists what was explicitly excluded, so whatever is derived from the
  specification does not reinvent it.
- Status stays `draft`. It flips to `ready` only when Open questions is empty **and** the user
  explicitly confirms.

Then archive the source idea, when it came from an inbox file: create the archived idea file
containing the idea's text verbatim (no header, no decoration), and remove exactly that text
from its source inbox file with a surgical edit, never a full-file rewrite; this move is the
only allowed edit to that file. Inbox files are user-owned capture: never restructure,
translate, or clean up their content, even when it looks garbled. Committing is not this
skill's concern.

## Second pass

The second pass is another analyst reading the same idea, with the first pass's result as an
additional input and a context that did not take part in the interview. It exists because the
questions one reading asks are not the questions another one asks, and the human who validates
the specification is better served by both sets than by one.

**Input**: the specification, the idea it cites as its source, and everything the first pass
grounded itself in, plus what it did not read and should have. **Output**: the same file.

There is no mode selection and no interview. The Decisions log already carries what the user
settled; the second pass does not ask it again.

1. **Redo the challenge independently**, before reading the first pass's Decisions log in
   detail, then compare. A point the second pass raises and the first did not is a candidate
   addition; a point both raise confirms the first pass and is not written again.
2. **Redo the analysis section by section**: a rule without its boundary case, a fact without
   its source, an edge case table missing a row, a worked example that does not exercise the
   rule it cites, an exclusion a reader would expect in Out of scope, an alternative nobody
   considered.
3. **Amend**, under four rules that do not bend:
   - **Additions are marked.** Each one carries the marker `(second pass)` at the end of the
     line or the row, so the human sees at a glance what the second reading brought. A
     project template may declare another marker; the default is this one.
   - **A decision taken with the user is never reversed.** The Decisions log records what the
     human settled. If the second pass disagrees with one of those decisions, it writes an
     Open questions entry that exposes both readings, the options and a recommendation, and
     the human arbitrates. Rewriting the rule directly is forbidden even when the second pass
     is sure.
   - **What is factual may be corrected in place**: a fact without a source, a contradiction
     between two rules, a wording that leaves an ambiguity, a fact label written `F1`. Each
     correction is one Decisions log row that says what changed and why, attributed to the
     second pass.
   - **What was written correctly is not rewritten.** A second pass that rephrases the
     document in its own words hides its additions in noise.
4. **Leave the status at `draft`.** Only the human flips it.

The second pass may ask the user for a fact only they hold, in one round after its reading is
complete, never question by question while it reads. In the absence of an answer the question
stays open in the file.

## Checklist

First pass:

- [ ] Mode (interactive or silent) chosen by the user before anything else
- [ ] Silent mode: open questions posed to the user in one round after the specification file
      is complete; answers integrated, unanswered entries left in Open questions
- [ ] Exactly one idea in scope
- [ ] Challenge presented before the first detail question (silent mode: conducted internally,
      outcome in the Decisions log)
- [ ] Every decision in the Decisions log
- [ ] No invented solution design anywhere in the specification; domain facts cited with their
      source
- [ ] Fact labels written `Fact <n>`, never abbreviated `F<n>`
- [ ] Every source with a URL cited as a markdown hyperlink `[Title](URL)`
- [ ] Every fact reads as the final consolidated state on its own: no correction trail,
      no addendum facts; change history lives in the Decisions log only
- [ ] Each non-trivial rule has a user-validated worked example
- [ ] Open questions listed honestly, none silently resolved
- [ ] Project glossary, naming conventions and template applied when declared
- [ ] Source idea archived verbatim and removed from its source inbox file, nothing else
      touched; skipped when the idea came from the conversation
- [ ] Status left at `draft` unless the user explicitly said ready

Second pass:

- [ ] Challenge redone independently before reading the first pass's Decisions log in detail
- [ ] Every addition marked `(second pass)` or with the project's declared marker
- [ ] No decision taken with the user reversed; every disagreement is an Open questions entry
- [ ] Every in-place correction logged in the Decisions log, attributed to the second pass
- [ ] Nothing correct rewritten
- [ ] Status still `draft`

## Limits

Never jump to publication, even if asked "and now the wiki?" or "and now the tickets?". The
specification is the end of this workflow; what happens to it next (validation, distillation,
publication, ticket derivation) belongs to the host project and needs its explicit go. Never
publish anywhere, never create or transition a ticket, never flip the status yourself. Never
restructure, translate, or clean up an inbox file. Never write the specification in another
language than English.

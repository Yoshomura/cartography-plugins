---
name: workflow-feature-spec
description: >-
  Turn one raw idea (an inbox .md file, a meeting note, or text dictated in conversation) into a
  functional spec at docs/specs/spec-<topic>.md through a mandatory challenge, then interview,
  then write sequence. Use when asked to spec or design a feature idea, to work through an idea
  inbox, to turn a note into a spec, or when a conception session starts. Do NOT use for writing
  tickets, publishing to a wiki or a tracker, or summarizing meeting transcripts.
license: MIT
---

# Turn a raw idea into a functional spec

The deliverable is exactly one functional spec at `docs/specs/spec-<topic>.md`, built from
`${CLAUDE_PLUGIN_ROOT}/skills/workflow-feature-spec/references/spec.template.md`. The spec is
written in English; the conversation happens in the user's language.

## Where things live

The paths below are this skill's defaults. A project may override any of them in its own
instructions (its `CLAUDE.md`); when it does, the project's paths win.

| Role | Default path |
|---|---|
| Idea inbox | `docs/Features TODO/` (any `.md` file the user points at) |
| Spec | `docs/specs/spec-<topic>.md` |
| Archived idea | `docs/archives/<year>/<topic>/notes-before-spec-<topic>.md` |

The spec states business behavior, never a solution design: no invented endpoints, schemas,
message contracts, or service internals. Established domain facts may be cited as facts:
existing services, the project's reference material (enums, glossaries, published studies,
documentation pages). A technical concern with no established answer becomes an entry in the
spec's Open questions, never an invented answer; it is settled downstream, by whoever derives
work from the spec.

## Scope guard — one idea at a time

An inbox file may mix several ideas. If the request spans more than one, have the user pick one
and park the others. Bundling two ideas into one spec is how scope creep starts before anything
is published.

## Phase 0 — Mode selection (mandatory, before anything else)

The spec runs in one of two modes, chosen by the user at the very start:

- **interactive** — the challenge and the interview happen live, one question at a time
  (AskUserQuestion when available). This is the richest mode; use it whenever the user can
  answer in real time.
- **silent** — no interactive call before the spec file is complete. The challenge is conducted
  internally and its outcome is recorded in the spec's Decisions log (alternatives considered,
  why the fixed inputs win or an open question remains). Every question the interview would
  have asked becomes a self-contained entry in the spec's Open questions section: enough
  context to be answered asynchronously, plus options and a recommendation when one is
  defensible. The spec is written in one pass from the fixed inputs only. **Then, once the file
  is finished**, pose the collected open questions to the user in one interactive round (best
  effort): if the user is at the screen, integrate the answers immediately (Decisions log
  updated, answered entries removed from Open questions) and the spec can reach 100%; if the
  user does not answer or no channel is available, the spec stands as written and is resumed
  later from its Open questions.

The mode is never defaulted. If the invocation does not state it, ask for it as the very
first question and wait. In silent mode the hard rules do not relax: a gap is still an open
question, never an invented answer.

## Phase 1 — Challenge (mandatory, before any detail question)

Read the idea, the project's own instructions and its glossary when it has one, then present a
challenge covering, in order:

1. **Domain collisions**: which established domain facts (reference material, existing
   studies, published pages) the idea touches or contradicts, and how. Name each source.
2. **Internal contradictions** within the idea itself.
3. **A simpler alternative** reaching the same business outcome, if one exists.
4. **Value**: what problem this solves, for whom, and what is lost if it is never built.

Do not soften the challenge. If the user drops the idea after it, stop; nothing is written. An
idea that has not been challenged must not be specified.

In silent mode the challenge still runs, internally: its outcome lands in the spec's Decisions
log, and anything it cannot settle from the fixed inputs becomes an Open questions entry.

## Phase 2 — Interview (interactive mode) / Open questions conversion (silent mode)

In silent mode there is no interview: skip to Phase 3 and convert every question this phase
would have asked into an Open questions entry as defined in Phase 0.

In interactive mode: one question at a time, each with proposed options and a recommendation
when one is defensible. Continue until zero ambiguity remains on business rules, edge cases,
worked examples, and scope boundaries. Three hard rules:

- **Never fill a gap with a plausible assumption.** A gap is either a question to the user or
  an entry in the spec's Open questions, never an invented rule presented as acquired.
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
- Out of scope lists what was explicitly excluded, so whatever is derived from the spec does
  not reinvent it.
- Status stays `draft`. It flips to `ready` only when Open questions is empty **and** the user
  explicitly confirms.

Then archive the source idea, when it came from an inbox file: create the archived idea file
containing the idea's text verbatim (no header, no decoration), and remove exactly that text
from its source inbox file with a surgical edit, never a full-file rewrite; this move is the
only allowed edit to that file. Inbox files are user-owned capture: never restructure,
translate, or clean up their content, even when it looks garbled. Committing is not this
skill's concern.

## Checklist

- [ ] Mode (interactive or silent) chosen by the user before anything else
- [ ] Silent mode: open questions posed to the user in one round after the spec file is
      complete; answers integrated, unanswered entries left in Open questions
- [ ] Exactly one idea in scope
- [ ] Challenge presented before the first detail question (silent mode: conducted internally,
      outcome in the Decisions log)
- [ ] Every decision in the Decisions log
- [ ] No invented solution design anywhere in the spec; domain facts cited with their source
- [ ] Fact labels written `Fact <n>`, never abbreviated `F<n>`
- [ ] Every source with a URL cited as a markdown hyperlink `[Title](URL)`
- [ ] Every fact reads as the final consolidated state on its own: no correction trail,
      no addendum facts; change history lives in the Decisions log only
- [ ] Each non-trivial rule has a user-validated worked example
- [ ] Open questions listed honestly, none silently resolved
- [ ] Project glossary and naming conventions applied when declared
- [ ] Source idea archived verbatim and removed from its source inbox file, nothing else touched
- [ ] Status left at `draft` unless the user explicitly said ready

## Limits

Never jump to publication, even if asked "and now the wiki?" or "and now the tickets?". The spec
is the end of this workflow; what happens to it next (validation, distillation, publication,
ticket derivation) belongs to the host project and needs its explicit go. Never publish
anywhere, never create or transition a ticket, never flip the status yourself. Never
restructure, translate, or clean up an inbox file. Never write the spec in another language
than English.

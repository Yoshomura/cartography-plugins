---
name: workflow-feature-spec
description: >-
  Turn one raw idea (an inbox .md file, a meeting note, or text dictated in conversation) into a
  functional specification organized by feature and use case, at
  docs/specifications/<feature>/, through a mandatory challenge, then interview, then write
  sequence. Use when asked to spec or design a feature idea, to work through an idea inbox, to
  turn a note into a spec, or when a conception session starts. Do NOT use for writing tickets,
  publishing to a wiki or a tracker, or summarizing meeting transcripts.
license: MIT
---

# Turn a raw idea into a functional specification

The deliverable is exactly one feature: one feature file, plus one file per use case written or
changed in this pass, built from the two templates in
`${CLAUDE_PLUGIN_ROOT}/skills/workflow-feature-spec/references/`. The specification is written
in English; the conversation happens in the user's language.

## Vocabulary

Use these terms and no other, in the conversation as in the files:

| Term | Meaning | Identifier |
|---|---|---|
| **Feature** | A functionality | `SIGNIN` |
| **Use case** | One goal reached by one means. Two means of reaching the same goal are two use cases, never two scenarios of one use case | `SIGNIN-PASSKEY` |
| **Scenario** | One way a use case unfolds: nominal, variant or failure. It is a worked example | `SIGNIN-PASSKEY-SCENARIO-2` |
| **Rule** | A rule of one use case, written in that use case even when another use case states the same rule today | `SIGNIN-PASSKEY-RULE-1` |
| **Invariant** | A rule of the feature whose divergence between its use cases would be a defect: security, personal data, accessibility. Written once, in the feature | `SIGNIN-INVARIANT-1` |

Identifiers are upper case, in full words, fixed: renaming a title never changes an identifier,
and an identifier once written is never reused for something else. Every test of the project
starts with the identifier it covers.

## Where things live

The paths below are this skill's defaults. A project may override any of them in its own
instructions (its `CLAUDE.md` or `AGENTS.md`); when it does, the project's paths win.

| Role | Default path |
|---|---|
| Idea inbox | `docs/Features TODO/` (any `.md` file the user points at) |
| Feature | `docs/specifications/<feature>/<feature>.md`, from `feature.template.md` |
| Use case | `docs/specifications/<feature>/<use-case>.md`, from `use-case.template.md` |
| Index of the features | `docs/specifications/features.md`, one row per feature |
| Archived idea | `docs/archives/<year>/<feature>/notes-before-spec-<feature>.md` |

The feature file carries the name of its folder, so that every file name is unique in an editor
or a search. File and folder names are lower case, words joined by hyphens.

The spec states business behavior, never a solution design: no invented endpoints, schemas,
message contracts, or service internals. Established domain facts may be cited as facts:
existing services, the project's reference material (enums, glossaries, published studies,
documentation pages). A technical concern with no established answer becomes an entry in the
Open questions sections, never an invented answer; it is settled downstream, by whoever derives
work from the spec.

## Scope guard — one idea at a time

An inbox file may mix several ideas. If the request spans more than one, have the user pick one
and park the others. Bundling two ideas into one spec is how scope creep starts before anything
is published.

One idea is one feature: a new feature, or a change to an existing one (a use case added,
changed or removed). When the feature already exists under the specification folder, read it
first and change it in place: never create a second feature for the same functionality.

## Phase 0 — Mode selection (mandatory, before anything else)

The spec runs in one of two modes, chosen by the user at the very start:

- **interactive** — the challenge and the interview happen live, one question at a time
  (AskUserQuestion when available). This is the richest mode; use it whenever the user can
  answer in real time.
- **silent** — no interactive call before the specification files are complete. The challenge is conducted
  internally and its outcome is recorded in the feature's Decisions log (alternatives considered,
  why the fixed inputs win or an open question remains). Every question the interview would
  have asked becomes a self-contained entry in the Open questions sections: enough
  context to be answered asynchronously, plus options and a recommendation when one is
  defensible. The spec is written in one pass from the fixed inputs only. **Then, once the files
  are finished**, pose the collected open questions to the user in one interactive round (best
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

In silent mode the challenge still runs, internally: its outcome lands in the feature's Decisions
log, and anything it cannot settle from the fixed inputs becomes an Open questions entry.

## Phase 2 — Interview (interactive mode) / Open questions conversion (silent mode)

In silent mode there is no interview: skip to Phase 3 and convert every question this phase
would have asked into an Open questions entry as defined in Phase 0.

In interactive mode: one question at a time, each with proposed options and a recommendation
when one is defensible. Continue until zero ambiguity remains on the use cases (one per means
of reaching a goal), their rules, their scenarios (nominal, variants, failures, each with
validated values), the invariants of the feature, and scope boundaries. Three hard rules:

- **Never fill a gap with a plausible assumption.** A gap is either a question to the user or
  an entry in the Open questions sections, never an invented rule presented as acquired.
- **Never settle an open reflection.** Present the options with a short recommendation and let
  the human choose.
- **Every decision lands in the Decisions log**, phrased as the user settled it.

Apply the project's naming conventions and glossary throughout when it declares them.

## Phase 3 — Write

Fill the feature file from `feature.template.md` and one file per use case from
`use-case.template.md`, then add or update the feature's row in the index of the features:

- **Use cases**: one goal reached by one means per file. Two means of reaching the same goal are
  two use case files, never two scenarios of one.
- **Rules**: one sentence each, in the use case they belong to, with an identifier
  `<USE-CASE>-RULE-<n>`. A rule two use cases share today is written in both: it is not moved
  to the feature.
- **Invariants**: only a rule whose divergence between the use cases would be a defect
  (security, personal data, accessibility), written once in the feature file with an
  identifier `<FEATURE>-INVARIANT-<n>`. When in doubt, it is a rule of each use case, and the
  question goes to the user.
- **Scenarios**: every non-trivial rule is illustrated by a scenario using values the user
  validated (in silent mode: plausible placeholder values, flagged as an Open questions entry
  for validation). Nominal path first, then variants and failures. Edge cases are failure or
  variant scenarios, not a separate table.
- **Identifiers**: upper case, full words, never renamed, never reused, numbered in the order
  written. An existing identifier keeps its number when its text changes.
- No prose padding anywhere.
- Facts are separated from decided rules, each fact with its source.
- Fact labels are human-readable: write `**Fact 1**`, `**Fact 2**`… never the abbreviated
  form `**F1**`, in the Facts section and in every cross-reference (rules, decisions log,
  scenarios).
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
- Status stays `draft`, in the feature file and in every use case file of this pass. It flips
  to `ready` only when Open questions is empty in all of them **and** the user explicitly
  confirms.

Then archive the source idea, when it came from an inbox file: create the archived idea file
containing the idea's text verbatim (no header, no decoration), and remove exactly that text
from its source inbox file with a surgical edit, never a full-file rewrite; this move is the
only allowed edit to that file. Inbox files are user-owned capture: never restructure,
translate, or clean up their content, even when it looks garbled. Committing is not this
skill's concern.

## Checklist

- [ ] Mode (interactive or silent) chosen by the user before anything else
- [ ] Silent mode: open questions posed to the user in one round after the specification files are
      complete; answers integrated, unanswered entries left in Open questions
- [ ] Exactly one idea in scope, one feature written or changed
- [ ] One use case file per means of reaching a goal; rules in their use case; invariants
      only for divergences that would be a defect
- [ ] Every invariant, rule and scenario carries its fixed identifier in full words
- [ ] Feature row added or updated in the index of the features
- [ ] Challenge presented before the first detail question (silent mode: conducted internally,
      outcome in the Decisions log)
- [ ] Every decision in the Decisions log
- [ ] No invented solution design anywhere in the spec; domain facts cited with their source
- [ ] Fact labels written `Fact <n>`, never abbreviated `F<n>`
- [ ] Every source with a URL cited as a markdown hyperlink `[Title](URL)`
- [ ] Every fact reads as the final consolidated state on its own: no correction trail,
      no addendum facts; change history lives in the Decisions log only
- [ ] Each non-trivial rule is illustrated by a scenario with user-validated values
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

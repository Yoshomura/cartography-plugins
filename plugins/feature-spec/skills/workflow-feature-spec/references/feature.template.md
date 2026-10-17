# <Feature title>

- **Feature ID**: `<FEATURE>` <!-- Upper case, full words, fixed: never renamed once a test carries it. -->
- **Status**: draft <!-- draft | ready. Flips to ready only on explicit user confirmation, and only when Open questions is empty here and in every use case file of this pass. -->
- **Source**: `<archive path>/notes-before-spec-<feature>.md` — the original idea, archived verbatim
- **Date**: <YYYY-MM-DD>

## Goal

What hurts today, for whom (which user, which role, which team), and what this feature changes.
Three sentences maximum.

## Facts

Established domain facts the feature relies on, each with its source (a reference document, an
existing study, a published page, a user statement). No assumptions: an unproven statement is
an open question, not a fact. Label facts `**Fact 1**`, `**Fact 2**`… (never abbreviated `F1`),
and use the same form in every cross-reference.

- **Fact 1** — ...

## Invariants

Rules whose divergence between the use cases of this feature would be a defect: security,
personal data, accessibility. Written once, here, and never repeated in a use case. A business rule that
several use cases share today by coincidence is not an invariant: it is written in each use
case. `None.` when there is none.

### <FEATURE>-INVARIANT-1

<one sentence, functional vocabulary only>

## Use cases

One use case is one goal reached by one means. Two means of reaching the same goal are two use
cases, each in its own file.

| ID | Use case | Actor |
|---|---|---|
| `<FEATURE>-<MEANS>` | [<Use case title>](<use-case-file>.md) | <actor> |

## Decisions log

Every decision taken during the interview, phrased as the user settled it.

| Question | Decision |
| -------- | -------- |
| ...      | ...      |

## Out of scope

Explicitly excluded, so whatever is derived from this feature does not reinvent it.

- ...

## Open questions

Must be empty, here and in every use case file of this pass, before Status can become `ready`.
Inline gaps are marked `> OPEN QUESTION: <what is missing>` and collected here.

- ...

# Spec: <topic>

- **Status**: draft <!-- draft | ready. Flips to ready only on explicit user confirmation, and only when Open questions is empty. -->
- **Source**: `<archive path>/notes-before-spec-<topic>.md` — the original idea, archived verbatim
- **Date**: <YYYY-MM-DD>

## Problem

What hurts today, for whom (which user, which role, which team). Three sentences maximum.

## Facts

Established domain facts the spec relies on, each with its source (a reference document, an
existing study, a published page, a user statement). No assumptions in a spec: an unproven
statement is an open question, not a fact. Label facts `**Fact 1**`, `**Fact 2**`… (never
abbreviated `F1`), and use the same form in every cross-reference.

- **Fact 1** — ...

## Business rules

Numbered, one sentence each. Functional vocabulary only — no invented endpoints, schemas, or
message contracts.

1. ...

## Worked examples

At least one example per non-trivial rule, referencing rule numbers, using values the user
validated.

### Example 1 — <short name>

Given ..., then ... (rules 1, 3).

## Edge cases

| #   | Case | Expected behavior |
| --- | ---- | ----------------- |
| 1   | ...  | ...               |

## Decisions log

Every decision taken during the interview, phrased as the user settled it.

| Question | Decision |
| -------- | -------- |
| ...      | ...      |

## Out of scope

Explicitly excluded, so whatever is derived from this spec does not reinvent it.

- ...

## Open questions

Must be empty before Status can become `ready`. Inline gaps in the sections above are marked
`> OPEN QUESTION: <what is missing>` and collected here.

- ...

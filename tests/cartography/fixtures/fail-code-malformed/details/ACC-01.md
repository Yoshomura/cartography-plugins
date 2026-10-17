---
kind: detail-entry
normative: false
generator: cartographer
source: functionality
use-case: ACC-01
implementation: Sign in
base: 1a2b3c4d
---

# ACC-01 — Sample use case

> **Observation, not specification.** The use case says what should happen; this file says
> what the functionality does, as observed or described. Divergences are listed at the end,
> and settled in the specification, not here.

## What it answers
> Source: the use case. Compressed, not inferred.

A member gets access to the private area.

## What it does
> Source: the functionality. Observed, not interpreted.

The account is checked against the stored credentials, then a session opens.

## The rules it applies

| # | Business rule | Specified as |
|---|---|---|
| 1 | An unknown account is refused | ACC-01-SCENARIO-1 |

1 business rules observed. 1 scenarios declared in the use case, 1 covered here, 0 tested.

An empty cell in the Specified as column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| The account | What the user enters |

## What it produces

A session. Nothing leaves.

## Observed divergences

None.

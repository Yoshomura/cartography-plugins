---
kind: detail-entry
normative: false
generator: cartographer
source: functionality
scenario: ACC-01
usecase: Sign in
base: 1a2b3c4d
---

# ACC-01 — Sample scenario

> **Observation, not specification.** The scenario says what should happen; this file says
> what the functionality does, as observed or described. Divergences are listed at the end,
> and settled in the specification, not here.

## What it answers
> Source: the scenario. Compressed, not inferred.

A member gets access to the private area.

## What it does
> Source: the functionality. Observed, not interpreted.

The account is checked against the stored credentials, then a session opens.

## The rules it applies

| # | Rule | Case |
|---|---|---|
| 1 | An unknown account is refused | CASE-1 |

1 rules observed. 1 cases declared in the scenario, 1 covered here, 0 tested.

An empty cell in the Case column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| The account | What the user enters |

## What it produces

A session. Nothing leaves.

## Observed divergences

None.

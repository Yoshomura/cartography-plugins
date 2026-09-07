---
kind: detail-entry
normative: false
generator: cartographer
scenario: <SCENARIO, empty when the usecase answers none>
usecase: src/<Project>.Hexagon/Application/<Name>UseCase.cs
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# <SCENARIO> — <title of the scenario>

> **Observation, not specification.** The scenario says what should happen; this file says
> what the code does. Divergences are listed at the end, and settled in the specification,
> not here.

## What it answers
> Source: the scenario. Compressed, not inferred.

<the need, in the scenario's own terms. Where there is no scenario, say so, hold only what
the code shows, and mark it `?`.>

## What it does
> Source: the code. Observed, not interpreted.

<what happens, in functional terms. No purpose, no judgment, no completion, no class name,
no control flow. Every sentence refutable by reading one precise place in the code.>

## The rules it applies

| # | Rule | Case |
|---|---|---|
| 1 | <the rule, in functional terms> | <CASE-ID, or empty> |

<n> rules observed. <n> cases declared in the scenario, <n> covered here, <n> tested.

An empty cell in the Case column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| <what it reads, in business terms> | <own database, a named system, the runtime> |

## What it produces

<the outcome, and the messages emitted. Say plainly when nothing leaves.>

## Observed divergences

None.

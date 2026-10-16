---
kind: detail-entry
normative: false
generator: cartographer
source: code
use-case: <USE-CASE identifier from the specification, empty when the implementation answers none>
implementation: <path to the existing file implementing the use case, any language, from the repository root, never a file to create>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# <USE-CASE> — <title of the use case>

> **Observation, not specification.** The use case says what should happen; this file says
> what the code does. Divergences are listed at the end, and settled in the specification,
> not here.

## What it answers
> Source: the use case. Compressed, not inferred.

<the need, in the use case's own terms. Where there is no use case, say so, hold only what
the code shows, and mark it `?`.>

## What it does
> Source: the code. Observed, not interpreted.

<what happens, in functional terms. No purpose, no judgment, no completion, no type or
function name, no control flow. Every sentence refutable by reading one precise place in the
code.>

## The rules it applies

| # | Rule | Specified as |
|---|---|---|
| 1 | <the rule, in functional terms> | <scenario, rule or invariant identifier, or empty> |

<n> rules observed. <n> scenarios declared in the use case, <n> covered here, <n> tested.

An empty cell in the Specified as column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| <what it reads, in business terms> | <own database, a named system, the runtime> |

## What it produces

<the outcome, and the messages emitted. Say plainly when nothing leaves.>

## Observed divergences

None.

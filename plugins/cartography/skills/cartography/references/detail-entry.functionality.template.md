---
kind: detail-entry
normative: false
generator: cartographer
source: functionality
use-case: <USE-CASE identifier from the specification, empty when the implementation answers none>
implementation: <implementation name, unique across the map and the detail entries, no path and no extension>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# <USE-CASE> — <title of the use case>

> **Observation, not specification.** The use case says what should happen; this file says
> what the functionality does, as observed or described. Divergences are listed at the end,
> and settled in the specification, not here.

## What it answers
> Source: the use case. Compressed, not inferred.

<the need, in the use case's own terms. Where there is no use case, say so, hold only what
the functionality shows, and mark it `?`.>

## What it does
> Source: the functionality. Observed, not interpreted.

<what happens, in functional terms, as seen on the screen, on the wire or in a document. No
purpose, no judgment, no completion. Every sentence refutable by one precise observation: a
screen, a request, a response, a document section.>

## The rules it applies

| # | Business rule | Specified as |
|---|---|---|
| 1 | <the business rule, in functional terms> | <scenario, business rule or invariant identifier, or empty> |

<n> business rules observed. <n> scenarios declared in the use case, <n> covered here, <n> tested.

An empty cell in the Specified as column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| <what it reads, in business terms> | <what the user enters, a named system, a document> |

## What it produces

<the outcome, and what leaves: messages, documents, notifications. Say plainly when nothing
leaves.>

## Observed divergences

None.

---
kind: detail-entry
normative: false
generator: cartographer
source: functionality
scenario: <SCENARIO, empty when the usecase answers none>
usecase: <usecase name, unique across the map and the detail entries, no path and no extension>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# <SCENARIO> — <title of the scenario>

> **Observation, not specification.** The scenario says what should happen; this file says
> what the functionality does, as observed or described. Divergences are listed at the end,
> and settled in the specification, not here.

## What it answers
> Source: the scenario. Compressed, not inferred.

<the need, in the scenario's own terms. Where there is no scenario, say so, hold only what
the functionality shows, and mark it `?`.>

## What it does
> Source: the functionality. Observed, not interpreted.

<what happens, in functional terms, as seen on the screen, on the wire or in a document. No
purpose, no judgment, no completion. Every sentence refutable by one precise observation: a
screen, a request, a response, a document section.>

## The rules it applies

| # | Rule | Case |
|---|---|---|
| 1 | <the rule, in functional terms> | <CASE-ID, or empty> |

<n> rules observed. <n> cases declared in the scenario, <n> covered here, <n> tested.

An empty cell in the Case column is a finding: carry it down to divergences.

## What it needs

| Needs | From |
|---|---|
| <what it reads, in business terms> | <what the user enters, a named system, a document> |

## What it produces

<the outcome, and what leaves: messages, documents, notifications. Say plainly when nothing
leaves.>

## Observed divergences

None.

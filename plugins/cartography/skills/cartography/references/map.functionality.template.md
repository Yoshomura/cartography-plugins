---
kind: map
normative: false
generator: cartographer
source: functionality
repository: <repository>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# Map — <repository>

> **Not normative, and inferred.** Where things are, never what they should be. `?` marks an
> uncertain link, and nothing here is ever a blocking CI gate.

Behavior lives in `details/<USE-CASE>.md`, the refusal surface in `refusals.md`, code nowhere.

## Use cases

| Use case | Scenarios | Implementation | What it answers |
|---|---|---|---|
| [<USE-CASE>](details/<USE-CASE>.md) | 0/0/0 | <implementation name, unique across the map and the detail entries, no path and no extension> | <the need answered, one sentence, 120 characters at most> |

`Scenarios` reads declared / covered / tested. Declared comes from the use case and tested from
the test names or identifiers carrying the scenario identifier, `0` when no test exists: both
exact. Covered is observed in the functionality, therefore inferred. A disagreement is named in
the detail entry.

Use cases declared for this deployable and **not found**: none.
Implementations attached to **no use case**: none.
Untested scenarios: none.

## Inbound

What can trigger a treatment here, as observed.

| Trigger | Nature | Use cases | Where observed |
|---|---|---|---|
| <user action, request, message or schedule> | <UI, HTTP, Event, Command, Schedule> | <USE-CASE> | <observed coordinate: screen, URL path, document section, module> |

## Outbound

What leaves here, as observed: messages emitted, systems called, documents produced.

| What goes out | Nature | Use cases | Where observed |
|---|---|---|---|
| <contract, system, document or notification> | <Event, Command, External system, Document, Notification> | <USE-CASE> | <observed coordinate> |

Indexed by the dependency, not by the use case: a contract that changes is read on one line.

## Anchors

Observation date per coordinate, so a reader can tell on arrival how old an observation is
without a pass being run. A coordinate held in this repository may carry its tree SHA instead.

| Coordinate | Tree SHA |
|---|---|
| <observed coordinate> | — observed <YYYY-MM-DD> |

## Unattached

Observed coordinates carrying behavior attached to no use case. This is where an anomaly reads.

None.

Technical, no functionality: <n> coordinates.

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

Behavior lives in `details/<SCENARIO>.md`, the refusal surface in `refusals.md`, code nowhere.

## Usecases

| Scenario | Cases | Usecase | What it answers |
|---|---|---|---|
| [<SCENARIO>](details/<SCENARIO>.md) | 0/0/0 | <usecase name, unique across the map and the detail entries, no path and no extension> | <the need answered, one sentence, 120 characters at most> |

`Cases` reads declared / covered / tested. Declared comes from the scenario and tested from
the test names or identifiers carrying the case ID, `0` when no test exists: both exact.
Covered is observed in the functionality, therefore inferred. A disagreement is named in the
detail entry.

Scenarios declared for this deployable and **not found**: none.
Usecases attached to **no scenario**: none.
Untested cases: none.

## Inbound

What can trigger a treatment here, as observed.

| Trigger | Nature | Usecases | Where observed |
|---|---|---|---|
| <user action, request, message or schedule> | <UI, HTTP, Event, Command, Schedule> | <SCENARIO> | <observed coordinate: screen, URL path, document section, module> |

## Outbound

What leaves here, as observed: messages emitted, systems called, documents produced.

| What goes out | Nature | Usecases | Where observed |
|---|---|---|---|
| <contract, system, document or notification> | <Event, Command, External system, Document, Notification> | <SCENARIO> | <observed coordinate> |

Indexed by the dependency, not by the usecase: a contract that changes is read on one line.

## Anchors

Observation date per coordinate, so a reader can tell on arrival how old an observation is
without a pass being run. A coordinate held in this repository may carry its tree SHA instead.

| Coordinate | Tree SHA |
|---|---|
| <observed coordinate> | — observed <YYYY-MM-DD> |

## Unattached

Observed coordinates carrying behavior attached to no scenario. This is where an anomaly reads.

None.

Technical, no functionality: <n> coordinates.

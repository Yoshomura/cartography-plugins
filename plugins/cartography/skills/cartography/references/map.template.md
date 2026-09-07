---
kind: map
normative: false
generator: cartographer
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
| [<SCENARIO>](details/<SCENARIO>.md) | 0/0/0 | `src/<Project>.Hexagon/Application/<Name>UseCase.cs` | <the need answered, one sentence, 120 characters at most> |

`Cases` reads declared / covered / tested. Declared comes from the scenario and tested from
the tests' `DisplayName`: both exact. Covered is observed in the usecase, therefore inferred.
Three equal numbers is the normal case; a disagreement is named in the detail entry.

Scenarios declared for this deployable and **not found**: none.
Usecases attached to **no scenario**: none.
Untested cases: none.

## Inbound

What can trigger a treatment here.

| Trigger | Nature | Usecases | Folder |
|---|---|---|---|
| <route, message or schedule> | <HTTP, Event, Command, Schedule> | <SCENARIO> | `src/<Project>.Host/<EntryPoint>/` |

## Outbound

What leaves here: messages emitted, systems called, storage touched.

| What goes out | Nature | Usecases | Folder |
|---|---|---|---|
| <contract, system or table> | <Event, Command, Internal company API, Own storage> | <SCENARIO> | `src/<Project>.Infrastructure/<Port>/` |

Indexed by the dependency, not by the usecase: a contract that changes is read on one line.

## Anchors

Tree SHA per coordinate, so a reader can tell on arrival that a coordinate is stale without a
pass being run.

| Folder | Tree SHA |
|---|---|
| `src/<Project>.Hexagon/Application` | <sha> |

## Unattached

Folders carrying code attached to no scenario. This is where an anomaly reads.

None.

Technical, no functionality: <n> folders.

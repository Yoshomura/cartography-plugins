---
kind: map
normative: false
generator: cartographer
source: code
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
| [<USE-CASE>](details/<USE-CASE>.md) | 0/0/0 | `<path/to/existing implementation file, with its extension>` | <the need answered, one sentence, 120 characters at most> |

`Scenarios` reads declared / covered / tested. Declared comes from the use case and tested from
the test names or identifiers carrying the scenario identifier: both exact. Covered is observed
in the implementation, therefore inferred. Three equal numbers is the normal case; a
disagreement is named in the detail entry.

Use cases declared for this deployable and **not found**: none.
Implementations attached to **no use case**: none.
Untested scenarios: none.

## Inbound

What can trigger a treatment here.

| Trigger | Nature | Use cases | Folder |
|---|---|---|---|
| <route, message or schedule> | <HTTP, Event, Command, Schedule> | <USE-CASE> | `<inbound adapter folder>/` |

## Outbound

What leaves here: messages emitted, systems called, storage touched.

| What goes out | Nature | Use cases | Folder |
|---|---|---|---|
| <contract, system or table> | <Event, Command, Internal company API, Own storage> | <USE-CASE> | `<outbound adapter folder>/` |

Indexed by the dependency, not by the use case: a contract that changes is read on one line.

## Anchors

Tree SHA per coordinate, so a reader can tell on arrival that a coordinate is stale without a
pass being run.

| Folder | Tree SHA |
|---|---|
| `<implementation folder>` | <sha> |

## Unattached

Folders carrying code attached to no use case. This is where an anomaly reads.

None.

Technical, no functionality: <n> folders.

---

Generated with cartography 2.2.0 (https://github.com/Yoshomura/cartography-plugins)

---
kind: map
normative: false
generator: cartographer
source: functionality
repository: sample
base: 1a2b3c4d
---

# Map — sample

> **Not normative, and inferred.** Where things are, never what they should be. `?` marks an
> uncertain link, and nothing here is ever a blocking CI gate.

Behavior lives in `details/<USE-CASE>.md`, the refusal surface in `refusals.md`, code nowhere.

## Use cases

| Use case | Scenarios | Implementation | What it answers |
|---|---|---|---|
| [ACC-01](details/ACC-01.md) | 1/1/0 | Sign in | A member gets access to the private area |
| [ACC-02](details/ACC-02.md) | 2/2/0 | Report an incident | A resident reports an incident |

## Inbound

| Trigger | Nature | Use cases | Where observed |
|---|---|---|---|
| Sign-in form | UI | ACC-01 | Sign-in screen |

## Outbound

| What goes out | Nature | Use cases | Where observed |
|---|---|---|---|
| Confirmation mail | Notification | ACC-01 | Mailbox of the account |

## Anchors

| Coordinate | Tree SHA |
|---|---|
| Sign-in screen | — observed 2026-10-15 |
| Incident form | — observed 2026-10-14 |

## Unattached

None.

Technical, no functionality: 2 folders.

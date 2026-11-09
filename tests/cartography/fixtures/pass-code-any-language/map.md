---
kind: map
normative: false
generator: cartographer
source: code
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
| [ACC-01](details/ACC-01.md) | 1/1/0 | `src/account/sign-in.ts` | A member gets access to the private area |
| [ACC-02](details/ACC-02.md) | 1/1/1 | `app/incidents/report_incident.py` | A resident reports an incident |

## Inbound

| Trigger | Nature | Use cases | Folder |
|---|---|---|---|
| Sign-in form | UI | ACC-01 | Sign-in screen |

## Outbound

| What goes out | Nature | Use cases | Folder |
|---|---|---|---|
| Confirmation mail | Notification | ACC-01 | Mailbox of the account |

## Anchors

| Folder | Tree SHA |
|---|---|
| `src/account` | 9f8e7d6c |
| `app/incidents` | 8e7d6c5b |

## Unattached

None.

Technical, no functionality: 2 folders.

---

Generated with cartography 2.2.0 (https://github.com/Yoshomura/cartography-plugins)

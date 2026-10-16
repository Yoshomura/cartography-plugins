---
kind: refusal-surface
normative: false
generator: cartographer
source: functionality
repository: sample
base: 1a2b3c4d
---

# Refusals — sample

> **Observation, not specification.** The refusal is specified in the use case; what the
> functionality shows when it refuses is only observed here. Divergences are listed at the end.

## Mechanisms

| Mechanism | What it means |
|---|---|
| Business exception | Raised by the business logic, translated by an inbound adapter |
| Returned outcome | No exception: the treatment returns a state the adapter turns into a refusal |
| Silent no-op | No exception, no signal: the treatment decides not to act |
| Adapter | Never reaches the use case: contract, routing, authorization |

## Business refusals

| Refusal | Mechanism | Exception | Code | Specified as | Use cases | Raised in | Caller sees |
|---|---|---|---|---|---|---|---|
| Unknown account | Business exception | — | — | ACC-01-SCENARIO-1 | ACC-01 | Sign in | An error message |
| Empty form | Returned outcome | — | — | ACC-02-SCENARIO-1 | ACC-01 | Sign in | The form again |

## Adapter refusals

| Refusal | Scope | Caller sees |
|---|---|---|
| Not signed in | Every entry point | The sign-in screen |

## Translation

| Raised | Adapter | Caller sees | Folder |
|---|---|---|---|
| — | Sign-in form | An error message | Sign-in screen |

## Divergences

None.

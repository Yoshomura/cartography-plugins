---
kind: refusal-surface
normative: false
generator: cartographer
source: code
repository: sample
base: 1a2b3c4d
---

# Refusals — sample

> **Observation, not specification.** The refusal is specified in the scenario; its mechanism
> is decided in the code and only observed here. Divergences are listed at the end.

## Mechanisms

| Mechanism | What it means |
|---|---|
| Business exception | Raised by the business logic, translated by an inbound adapter |
| Returned outcome | No exception: the treatment returns a state the adapter turns into a refusal |
| Silent no-op | No exception, no signal: the treatment decides not to act |
| Adapter | Never reaches the usecase: contract, routing, authorization |

## Business refusals

| Refusal | Mechanism | Exception | Code | Cases | Usecases | Raised in | Caller sees |
|---|---|---|---|---|---|---|---|
| Unknown account | Business exception | UnknownAccountError | — | CASE-1 | ACC-01 | `src/account/sign-in.ts` | An error message |
| Empty form | Returned outcome | — | — | CASE-2 | ACC-01 | `src/account/sign-in.ts` | The form again |

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

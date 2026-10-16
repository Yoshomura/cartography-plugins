---
kind: refusal-surface
normative: false
generator: cartographer
source: functionality
repository: <repository>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# Refusals — <repository>

> **Observation, not specification.** The refusal is specified in the use case; what the
> functionality shows when it refuses is only observed here. Divergences are listed at the end.

Exceptions and error codes are recorded only where the functionality shows them; `—` marks
those it does not.

## Mechanisms

Not every refusal raises an exception. The mechanism is what makes the refusal visible, and
its absence is itself an observation.

| Mechanism | What it means |
|---|---|
| Business exception | Raised by the business logic, translated by an inbound adapter |
| Returned outcome | No exception: the treatment returns a state the adapter turns into a refusal |
| Silent no-op | No exception, no signal: the treatment decides not to act |
| Adapter | Never reaches the use case: contract, routing, authorization |

## Business refusals

| Refusal | Mechanism | Exception | Code | Specified as | Use cases | Raised in | Caller sees |
|---|---|---|---|---|---|---|---|
| <the refusal, in functional terms> | <one of the four mechanisms> | <type when observed, or —> | <CODE when observed, or —> | <scenario, rule or invariant identifier> | <USE-CASE> | <implementation name> | <message, status, rejection or nothing> |

## Adapter refusals

Before or outside the business logic. No identifier, no use case.

| Refusal | Scope | Caller sees |
|---|---|---|
| <the refusal> | <the entry point, or every entry point> | <what the caller gets> |

## Translation

| Raised | Adapter | Caller sees | Where observed |
|---|---|---|---|
| <exception type or code when observed, or —> | <entry point> | <what the caller gets> | <observed coordinate> |

## Divergences

None.

---
kind: refusal-surface
normative: false
generator: cartographer
repository: <repository>
base: <commit sha of this repository at the last pass, empty on a first pass>
---

# Refusals — <repository>

> **Observation, not specification.** The refusal is specified in the scenario; its mechanism
> is decided in the code and only observed here. Divergences are listed at the end.

Exceptions and error codes are defined in `src/<Project>.Hexagon/Domain/`.

## Mechanisms

Not every refusal raises an exception. The mechanism is what makes the refusal visible, and
its absence is itself an observation.

| Mechanism | What it means |
|---|---|
| Business exception | Raised in the hexagon, translated by an inbound adapter |
| Returned outcome | No exception: the treatment returns a state the adapter turns into a refusal |
| Silent no-op | No exception, no signal: the treatment decides not to act |
| Adapter | Never reaches the usecase: contract, routing, authorization |

## Business refusals

| Refusal | Mechanism | Exception | Code | Cases | Usecases | Raised in | Caller sees |
|---|---|---|---|---|---|---|---|
| <the refusal, in functional terms> | <one of the four mechanisms> | <type, or —> | <CODE, or —> | <CASE-ID> | <SCENARIO> | <usecase, or the folder that raises it> | <status, acknowledgement, rejection or dead letter> |

## Adapter refusals

Before or outside the hexagon. No case ID, no usecase.

| Refusal | Scope | Caller sees |
|---|---|---|
| <the refusal> | <the entry point, or every entry point> | <what the caller gets> |

## Translation

| Raised | Adapter | Caller sees | Folder |
|---|---|---|---|
| <exception type> | <entry point> | <what the caller gets> | `src/<Project>.Host/<EntryPoint>/` |

## Divergences

None.

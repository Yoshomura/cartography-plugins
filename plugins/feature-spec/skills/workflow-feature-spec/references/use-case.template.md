# <Use case title: a verb, its object and the means>

- **Use case ID**: `<FEATURE>-<MEANS>` <!-- Upper case, full words, fixed: never renamed once a test carries it. -->
- **Feature**: [<Feature title>](<feature>.md)
- **Actor**: <who reaches the goal>
- **Status**: draft <!-- draft | ready, as the feature file. -->

## Goal

The goal of the actor, and the means this use case reaches it by. One sentence.

The invariants of the feature apply: [<Feature title>](<feature>.md#invariants).

## Business rules

Numbered, one sentence each, functional vocabulary only: no invented endpoints, schemas or
message contracts. A business rule is written in this use case even when another use case
states the same business rule today, so that each can change alone. `None.` when there is none.

### <FEATURE>-<MEANS>-BUSINESS-RULE-1

<one sentence>

## Scenarios

One scenario per way the use case unfolds: the nominal path first, then each variant and each
failure. Each scenario is a worked example with values the user validated: a short title, one
sentence of 120 characters at most usable as the title of a ticket, then its Given / When /
Then, which says what the sentence says and nothing more.

### <FEATURE>-<MEANS>-SCENARIO-1: <short title>

<One sentence, 120 characters at most: the situation, the action and its outcome.>

```gherkin
Given <the situation before>
When <the action>
Then <the observable outcome>
```

## Open questions

Gaps of this use case, marked `> OPEN QUESTION: <what is missing>` where they occur and
collected here. Remove the section when it is empty.

- ...

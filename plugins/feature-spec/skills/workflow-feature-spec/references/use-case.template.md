# <Use case title: a verb, its object and the means>

- **Use case ID**: `<FEATURE>-<MEANS>` <!-- Upper case, full words, fixed: never renamed once a test carries it. -->
- **Feature**: [<Feature title>](<feature>.md)
- **Actor**: <who reaches the goal>
- **Status**: draft <!-- draft | ready, as the feature file. -->

## Goal

The goal of the actor, and the means this use case reaches it by. One sentence.

The invariants of the feature apply: [<Feature title>](<feature>.md#invariants).

## Rules

Numbered, one sentence each, functional vocabulary only: no invented endpoints, schemas or
message contracts. A rule is written in this use case even when another use case states the
same rule today, so that each can change alone. `None.` when there is none.

### <FEATURE>-<MEANS>-RULE-1

<one sentence>

## Scenarios

One scenario per way the use case unfolds: the nominal path first, then each variant and each
failure. Each scenario is a worked example with values the user validated, and points at the
rules it illustrates.

### <FEATURE>-<MEANS>-SCENARIO-1: <short name>

Given ..., when ..., then ... (<FEATURE>-<MEANS>-RULE-1).

## Open questions

Gaps of this use case, marked `> OPEN QUESTION: <what is missing>` where they occur and
collected here. Remove the section when it is empty.

- ...

# Sign in with an email code

- **Use case ID**: `LOGIN-EMAIL`
- **Feature**: [Sign in](sign-in.md)
- **Actor**: Person

## Goal

Open my private space with a code received by email.

## Business rules

None.

## Scenarios

### LOGIN-EMAIL-SCENARIO-1: Valid code

The person enters the code received by email: the session opens.

```gherkin
Given a code sent to the person
When the person enters it
Then the session opens
```

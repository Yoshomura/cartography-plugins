# Sign in with a passkey

- **Use case ID**: `SIGNIN-PASSKEY`
- **Feature**: [Sign in](sign-in.md)
- **Actor**: Person
- **Status**: draft

## Goal

Open my private space with a passkey.

## Business rules

### SIGNIN-PASSKEY-BUSINESS-RULE-1

A passkey is unlocked by face, fingerprint or device code.

## Scenarios

### SIGNIN-PASSKEY-SCENARIO-1: Passkey recognized

The person unlocks a passkey registered on their account: the session opens.

```gherkin
Given a passkey registered on the person's account
When the person unlocks it
Then the session opens
```

### SIGNIN-PASSKEY-SCENARIO-2: Unknown passkey

The person presents a passkey that no account holds: the sign-in is refused.

```gherkin
Given a passkey that no account holds
When the person presents it
Then the sign-in is refused
And no session opens
```

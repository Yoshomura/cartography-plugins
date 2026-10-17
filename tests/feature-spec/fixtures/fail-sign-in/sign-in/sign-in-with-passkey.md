# Sign in with a passkey

- **Use case ID**: `SIGNIN-PASSKEY`
- **Feature**: [Sign in](sign-in.md)
- **Actor**: Person

## Goal

Open my private space with a passkey.

## Business rules

### SIGNIN-PASSKEY-RULE-1

A passkey is unlocked by face, fingerprint or device code.

## Scenarios

### SIGNIN-PASSKEY-SCENARIO-1: Passkey recognized

The person unlocks a passkey registered on their account, on any of their devices, in any residence, at any time of day: the session opens.

```gherkin
Given a passkey registered on the person's account
Then the session opens
```

### SIGNIN-PASSKEY-SCENARIO-3: Unknown passkey

```gherkin
Given a passkey that no account holds
When the person presents it
Then the sign-in is refused
```

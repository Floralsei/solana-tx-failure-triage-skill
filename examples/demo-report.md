# Demo Triage Report

Input fixture: `examples/constraint-owner.log`

## Diagnosis

Primary cause: Anchor custom error or constraint failure
Confidence: Medium

## Evidence

- `Program log: AnchorError caused by account: vault_token_account.`
- `Program log: Error Code: ConstraintOwner. Error Number: 2004.`
- `Program log: Error Message: A token account owner was invalid.`
- `InstructionError: [1, { "Custom": 2004 }]`

## Why It Failed

The transaction reached instruction index 1 and the Anchor program rejected `vault_token_account` because its owner did not satisfy the expected account constraint. The raw custom error number is `2004`, and the program logs name the failing account, so the next debug step is account validation rather than retrying the same signed transaction.

## Fix

1. Check the IDL or source for the `vault_token_account` constraint on instruction 1.
2. Verify the token account owner, mint, PDA seeds, bump, and account order before building the transaction.
3. Create or pass the correct associated token account if the current account belongs to a different authority.

## Reproduction

```bash
python skill/scripts/triage_logs.py --input examples/constraint-owner.log --format markdown
```

## Safety Notes

This demo uses redacted local fixture data only. Do not paste private keys, seed phrases, bearer tokens, cookies, or unredacted RPC provider keys into triage logs.

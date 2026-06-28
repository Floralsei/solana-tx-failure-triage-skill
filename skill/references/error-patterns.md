# Solana Transaction Failure Patterns

Use this reference when logs or RPC errors are available. Treat matches as evidence, not proof; confirm with instruction index, program logs, and account context.

## Blockhash and Expiry

Signals:
- `Blockhash not found`
- `TransactionExpiredBlockheightExceededError`
- `block height exceeded`
- `This transaction has already been processed`

Likely cause:
- A serialized transaction was signed or broadcast after its recent blockhash expired.
- The client retried an old signed transaction instead of rebuilding and re-signing.

Fix:
- Fetch a fresh blockhash immediately before signing.
- Track `lastValidBlockHeight`.
- On expiry, rebuild the message and collect signatures again.
- Avoid caching signed transactions in queues unless using durable nonce intentionally.

## Compute Budget

Signals:
- `ComputationalBudgetExceeded`
- `Program failed to complete`
- `exceeded maximum number of instructions allowed`
- `consumed ... compute units`

Likely cause:
- The transaction path requires more compute than the default budget.
- A branch or CPI path is unexpectedly expensive.

Fix:
- Simulate with compute logs enabled.
- Add `ComputeBudgetProgram.setComputeUnitLimit`.
- Add `ComputeBudgetProgram.setComputeUnitPrice` during congestion when appropriate.
- Profile and optimize the program path instead of only raising the limit.

## Signer and Signature Problems

Signals:
- `Signature verification failed`
- `missing required signature`
- `unknown signer`
- `KeypairPubkeyMismatch`
- `Transaction signature verification failure`

Likely cause:
- Required signer meta is present but not signed.
- Fee payer differs from the signer used by the wallet.
- Partial signing overwritten existing signatures.
- Durable nonce authority or multisig path is wrong.

Fix:
- List every account meta marked signer and verify the signer set.
- Ensure fee payer signs.
- Preserve partial signatures when adding wallet signatures.
- Rebuild after blockhash refresh before re-signing.

## Account Ownership, PDA, and Initialization

Signals:
- `AccountNotInitialized`
- `InvalidAccountOwner`
- `Provided owner is not allowed`
- `AccountOwnedByWrongProgram`
- `ConstraintSeeds`
- `ConstraintOwner`
- `ConstraintAssociated`
- `ConstraintTokenAccount`

Likely cause:
- Wrong PDA seeds or bump.
- Account order does not match the program interface.
- ATA or program account was not created.
- Token account owner or mint differs from expected values.

Fix:
- Recompute PDA seeds and bump from source or IDL.
- Check account order against IDL/source.
- Create missing ATAs before the main instruction.
- Validate owner and mint before building the transaction.

## Anchor Custom Errors

Signals:
- `custom program error: 0x...`
- `AnchorError`
- `Error Code:`
- `Error Number:`

Likely cause:
- Program-specific invariant failed.
- Anchor constraints rejected one or more accounts.

Fix:
- Convert hex custom error to decimal when needed.
- Map the code through the program IDL or source.
- Use the failing instruction index and named account in Anchor logs.
- Report both decoded error and raw code.

## Funds, Rent, and Token Balances

Signals:
- `insufficient funds`
- `InsufficientFundsForRent`
- `Attempt to debit an account but found no record of a prior credit`
- `custom program error: 0x1` in token transfer contexts

Likely cause:
- Fee payer lacks SOL for fees or rent.
- Token source lacks the required SPL token balance.
- ATA creation rent was not budgeted.

Fix:
- Separate SOL fee/rent needs from token amount.
- Check token decimals and mint.
- Pre-create ATAs or include rent funding in the transaction.

## Slippage, Quotes, and Routing

Signals:
- `Slippage tolerance exceeded`
- `AmountOutBelowMinimum`
- `route expired`
- `quote expired`
- `market not found`

Likely cause:
- Quote or route was stale.
- Market moved beyond user-approved slippage.
- Token account, mint, or route account changed.

Fix:
- Refresh quote close to signing.
- Never raise slippage without explicit user approval.
- Validate token mints and ATAs before routing.
- Include min-out and quote timestamp in the report.

## Confirmation and RPC Inconsistency

Signals:
- `Transaction was not confirmed`
- `timeout`
- `signature not found`
- One RPC sees a signature while another does not.

Likely cause:
- Broadcast may have succeeded but confirmation polling used a lagging RPC.
- Transaction landed after client timeout.
- Preflight cluster or commitment differs from confirmation cluster.

Fix:
- Query `getSignatureStatuses` on multiple reliable RPCs.
- Record broadcast signature before retrying.
- Use consistent cluster and commitment.
- Avoid duplicate side effects by checking status before rebuilding.

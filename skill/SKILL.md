---
name: solana-tx-failure-triage
description: Diagnose failed Solana transactions from RPC errors, simulation logs, wallet/client exceptions, Anchor errors, program logs, or transaction signatures. Use when Codex needs to classify a Solana failure, explain likely root cause, propose fixes, prepare a developer-facing incident report, or turn raw Solana logs into actionable next steps.
---

# Solana Tx Failure Triage

## Overview

Diagnose failed Solana transactions by gathering evidence, classifying common failure patterns, and producing a concise remediation report. Prefer concrete logs and signatures over guesses, and separate confirmed facts from likely causes.

## Quick Start

1. Ask for or locate the transaction signature, cluster, RPC error JSON, simulation logs, wallet/client exception, relevant program IDs, and whether Anchor/IDLs are available.
2. If logs are available in a file, run:

```bash
python skill/scripts/triage_logs.py --input path/to/log.txt --format markdown
```

3. For detailed pattern rules, read `references/error-patterns.md`.
4. Return the diagnosis using the report format below.

## Evidence Checklist

- Transaction signature and cluster: mainnet-beta, devnet, testnet, localnet, or custom RPC.
- Full RPC error object, not only the top-level message.
- Simulation logs and `InstructionError` index.
- Program log lines around the failing instruction.
- Client code path that built the transaction, including signer and fee payer.
- IDL, known custom error map, or source link for Anchor programs when available.
- Wallet balance, token account addresses, recent blockhash handling, compute budget instructions, and priority fee settings.

## Triage Workflow

1. Preserve raw evidence. Redact private keys, seed phrases, API keys, bearer tokens, cookies, and personal data.
2. Identify the failing instruction. Use `InstructionError` index and nearby program logs.
3. Classify the primary failure pattern. Do not list every matching keyword as a root cause; pick the strongest pattern and note secondary signals.
4. Map the failure to the actor that can fix it: client builder, wallet/signing flow, program owner, RPC provider, keeper/automation, or user setup.
5. Propose the smallest safe fix first, then optional robustness improvements.
6. Include a reproduction path when enough information exists.

## Common Fix Directions

- Blockhash expired: rebuild the transaction with a fresh blockhash, re-sign, track `lastValidBlockHeight`, and avoid replaying old serialized transactions.
- Compute exceeded: add or raise `ComputeBudgetProgram.setComputeUnitLimit`, add priority fee when congestion is likely, and profile the program path before increasing blindly.
- Missing signer or signature failure: verify fee payer, required signer metas, durable nonce authority, PDA signer expectations, and wallet adapter partial-sign flows.
- Account owner or initialization mismatch: verify PDA seeds, bump, account owner, associated token account creation, rent exemption, and account ordering.
- Anchor constraint failure: decode Anchor custom errors, check IDL constraints, and inspect the account named by the failing constraint.
- Insufficient funds or token balance: include SOL rent/fee needs separately from SPL token balance.
- Slippage or route failure: refresh quotes, increase slippage only when user-approved, and guard against stale token accounts or mints.
- Confirmation timeout: distinguish broadcast success from finality delay; check signature status across RPCs before retrying.

## Report Format

Use this structure:

```markdown
## Diagnosis
Primary cause: <one sentence>
Confidence: High | Medium | Low

## Evidence
- <raw signal or log line, redacted>
- <instruction index / program id / error code>

## Why It Failed
<plain English explanation tied to Solana mechanics>

## Fix
1. <minimal fix>
2. <robustness improvement>

## Reproduction
<steps or "Not enough data; need ...">

## Safety Notes
<any secret redaction, scope, or mainnet caution>
```

## Resources

- `scripts/triage_logs.py`: deterministic keyword classifier for raw Solana logs.
- `references/error-patterns.md`: detailed failure pattern map and remediation notes.

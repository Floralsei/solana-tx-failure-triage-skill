# Superteam Earn Submission Draft

## Project

Solana Tx Failure Triage Skill

## Repository / PR

Replace this with the public GitHub repository URL after publishing:

`https://github.com/<your-handle>/solana-tx-failure-triage-skill`

## Short Description

Solana Tx Failure Triage is an AI skill that helps coding agents diagnose failed Solana transactions from RPC errors, simulation logs, Anchor errors, wallet/client exceptions, and program logs. It classifies likely root causes, preserves raw evidence, and generates a developer-facing remediation report.

## Problem Solved

Failed Solana transactions are hard to debug because the useful signal is split across RPC error JSON, simulation logs, Anchor custom errors, program logs, wallet adapter behavior, and confirmation status. Builders often waste time guessing whether a failure is caused by blockhash expiry, compute budget, missing signatures, account initialization, PDA mismatch, token balances, slippage, or RPC inconsistency.

This skill gives agents a structured triage workflow and a deterministic helper script so they can turn raw logs into actionable fixes.

## Why It Is Useful

- Helps Solana builders debug transactions faster.
- Gives agents a safe workflow for handling user-provided logs.
- Distinguishes confirmed evidence from likely causes.
- Produces consistent incident-style reports that engineering teams can act on.
- Includes a reusable classifier script and focused reference material.

## What Is Included

- `skill/SKILL.md`: concise triggerable workflow for Codex-compatible agents.
- `skill/references/error-patterns.md`: failure pattern map with fixes.
- `skill/scripts/triage_logs.py`: deterministic log classifier.
- `examples/`: sample logs for blockhash expiry, compute budget, and Anchor constraint failures.
- `README.md`: installation and usage instructions.
- `install.sh`: simple installer for Codex-compatible skill directories.
- `LICENSE`: MIT.

## Differentiation

Instead of being a broad "Solana audit" or "developer help" skill, this skill focuses on one recurring builder pain point: failed transaction triage. The narrow scope makes it easier for an AI agent to be reliable and for builders to use it in real workflows.

## Example Command

```bash
python skill/scripts/triage_logs.py --input examples/compute-budget.log --format markdown
```

## Example Output

```markdown
## Diagnosis
Primary cause: Compute budget exceeded
Confidence: High

## Evidence
- Program failed to complete: exceeded maximum number of instructions allowed

## Why It Failed
The transaction path used more compute than the configured or default budget.

## Fix
1. Simulate with logs, add an appropriate compute unit limit, consider priority fees, and profile expensive branches.
```

## Safety Notes

The skill instructs agents to redact private keys, seed phrases, API keys, bearer tokens, cookies, and personal data. It also encourages devnet/localnet or read-only evidence unless explicit authorization exists.

# Solana Tx Failure Triage Skill

An AI skill for diagnosing failed Solana transactions from RPC errors, simulation logs, wallet/client exceptions, Anchor errors, and raw program logs.

The goal is practical incident triage: identify the most likely root cause, explain it in Solana terms, and produce a fix plan that a builder can act on.

## Why This Exists

Solana transaction failures are often noisy:

- RPC errors hide the failing instruction behind nested JSON.
- Anchor custom errors need IDL/source mapping.
- Wallet adapters can overwrite partial signatures.
- Stale blockhashes, compute limits, missing ATAs, and RPC confirmation delays look similar to users.

This skill gives Codex/Claude-style coding agents a structured workflow for turning that mess into a concise developer report.

## Repository Structure

```text
skill/
  SKILL.md
  agents/openai.yaml
  references/error-patterns.md
  scripts/triage_logs.py
examples/
  blockhash-expired.log
  compute-budget.log
  constraint-owner.log
```

## Install

Copy the `skill/` folder into a Codex-compatible skill directory, or point your agent runtime at this repository and invoke:

```text
$solana-tx-failure-triage
```

The bundled script can be run directly:

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

## Fix
1. Simulate with logs, add an appropriate compute unit limit, consider priority fees, and profile expensive branches.
```

## Submission Fit

This skill is designed for Solana builders, wallet teams, DeFi integrators, keepers, and AI agents that need to understand why a transaction failed before retrying or changing code.

It is narrow on purpose: transaction failure triage is a recurring, high-friction workflow that benefits from deterministic classification plus agent reasoning.

## Safety

Never include private keys, seed phrases, bearer tokens, cookies, or unredacted API keys in logs. Use devnet/localnet or read-only evidence unless a project explicitly authorizes testing.

## License

MIT

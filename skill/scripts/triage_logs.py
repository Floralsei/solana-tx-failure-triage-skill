#!/usr/bin/env python3
"""Classify Solana transaction failure logs into likely causes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pattern:
    name: str
    severity: str
    confidence: str
    keywords: tuple[str, ...]
    explanation: str
    fix: str


PATTERNS: tuple[Pattern, ...] = (
    Pattern(
        name="Blockhash expired or stale signed transaction",
        severity="High",
        confidence="High",
        keywords=(
            "blockhash not found",
            "transactionexpiredblockheightexceedederror",
            "block height exceeded",
            "already been processed",
        ),
        explanation="The transaction likely used an expired recent blockhash or retried an old signed message.",
        fix="Fetch a fresh blockhash, rebuild the transaction message, re-sign, and track lastValidBlockHeight.",
    ),
    Pattern(
        name="Compute budget exceeded",
        severity="Medium",
        confidence="High",
        keywords=(
            "computationalbudgetexceeded",
            "program failed to complete",
            "exceeded maximum number of instructions",
            "compute units",
        ),
        explanation="The transaction path used more compute than the configured or default budget.",
        fix="Simulate with logs, add an appropriate compute unit limit, consider priority fees, and profile expensive branches.",
    ),
    Pattern(
        name="Missing signer or signature verification failure",
        severity="High",
        confidence="High",
        keywords=(
            "signature verification failed",
            "missing required signature",
            "unknown signer",
            "keypairpubkeymismatch",
            "transaction signature verification failure",
        ),
        explanation="A required signer did not sign, the fee payer/signers are mismatched, or partial signatures were overwritten.",
        fix="Verify all signer account metas, fee payer signature, durable nonce authority, and partial-signature preservation.",
    ),
    Pattern(
        name="Account owner, PDA, or initialization mismatch",
        severity="High",
        confidence="Medium",
        keywords=(
            "accountnotinitialized",
            "invalidaccountowner",
            "provided owner is not allowed",
            "accountownedbywrongprogram",
            "constraintseeds",
            "constraintowner",
            "constraintassociated",
            "constrainttokenaccount",
        ),
        explanation="An account does not match the program's expected owner, PDA seeds, mint, or initialization state.",
        fix="Recompute PDAs, verify account order against IDL/source, create missing ATAs/accounts, and validate owner/mint.",
    ),
    Pattern(
        name="Anchor custom error or constraint failure",
        severity="Medium",
        confidence="Medium",
        keywords=(
            "anchorerror",
            "error code:",
            "error number:",
            "custom program error",
            "constraint",
        ),
        explanation="The program returned a custom Anchor error or rejected one of the account constraints.",
        fix="Decode the custom error through the IDL/source, inspect the failing instruction index, and check named accounts.",
    ),
    Pattern(
        name="Insufficient SOL, rent, or SPL token balance",
        severity="Medium",
        confidence="High",
        keywords=(
            "insufficient funds",
            "insufficientfundsforrent",
            "attempt to debit an account",
            "custom program error: 0x1",
        ),
        explanation="The fee payer or token source likely lacks SOL for fees/rent or enough SPL token balance.",
        fix="Check SOL fee/rent separately from token balances, validate token decimals, and pre-create ATAs when needed.",
    ),
    Pattern(
        name="Slippage, stale quote, or route failure",
        severity="Medium",
        confidence="Medium",
        keywords=(
            "slippage tolerance exceeded",
            "amountoutbelowminimum",
            "route expired",
            "quote expired",
            "market not found",
        ),
        explanation="A quote or route was stale, market conditions moved, or route accounts/mints are invalid.",
        fix="Refresh the quote close to signing, keep min-out protection, and only change slippage with user approval.",
    ),
    Pattern(
        name="Confirmation timeout or RPC inconsistency",
        severity="Low",
        confidence="Medium",
        keywords=(
            "transaction was not confirmed",
            "signature not found",
            "timeout",
            "timed out",
        ),
        explanation="Broadcast status and confirmation status may differ across RPC nodes or commitments.",
        fix="Check getSignatureStatuses on reliable RPCs before retrying, record the signature, and keep cluster/commitment consistent.",
    ),
)


def read_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    return sys.stdin.read()


def matching_lines(text: str, keywords: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    hits: list[str] = []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for line in lines:
        low = line.lower()
        if any(keyword in low for keyword in lowered_keywords):
            cleaned = re.sub(r"\s+", " ", line).strip()
            if cleaned and cleaned not in hits:
                hits.append(cleaned)
    return hits[:8]


def classify(text: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    lowered = text.lower()
    for pattern in PATTERNS:
        score = sum(1 for keyword in pattern.keywords if keyword in lowered)
        if score:
            results.append(
                {
                    "name": pattern.name,
                    "severity": pattern.severity,
                    "confidence": pattern.confidence,
                    "score": score,
                    "evidence": matching_lines(text, pattern.keywords),
                    "explanation": pattern.explanation,
                    "fix": pattern.fix,
                }
            )
    return sorted(results, key=lambda item: (-int(item["score"]), str(item["name"])))


def as_markdown(results: list[dict[str, object]]) -> str:
    if not results:
        return (
            "## Diagnosis\n"
            "Primary cause: Unknown from supplied logs\n"
            "Confidence: Low\n\n"
            "## Next Evidence Needed\n"
            "- Full RPC error object\n"
            "- Simulation logs\n"
            "- InstructionError index\n"
            "- Program ID and IDL/source link\n"
        )

    primary = results[0]
    lines = [
        "## Diagnosis",
        f"Primary cause: {primary['name']}",
        f"Confidence: {primary['confidence']}",
        "",
        "## Evidence",
    ]
    for evidence in primary["evidence"]:
        lines.append(f"- {evidence}")
    lines.extend(
        [
            "",
            "## Why It Failed",
            str(primary["explanation"]),
            "",
            "## Fix",
            f"1. {primary['fix']}",
        ]
    )

    if len(results) > 1:
        lines.extend(["", "## Secondary Signals"])
        for item in results[1:4]:
            lines.append(f"- {item['name']} ({item['confidence']} confidence)")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Solana transaction failure logs.")
    parser.add_argument("--input", "-i", help="Path to a log/error text file. Reads stdin when omitted.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    text = read_text(args.input)
    results = classify(text)
    if args.format == "markdown":
        print(as_markdown(results))
    else:
        print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

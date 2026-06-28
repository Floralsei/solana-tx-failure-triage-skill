#!/usr/bin/env python3
"""Run local smoke tests for the Solana tx failure triage helper."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "scripts" / "triage_logs.py"

FIXTURES = (
    ("examples/blockhash-expired.log", "Blockhash expired or stale signed transaction"),
    ("examples/compute-budget.log", "Compute budget exceeded"),
    ("examples/constraint-owner.log", "Anchor custom error or constraint failure"),
)


def load_module():
    spec = importlib.util.spec_from_file_location("triage_logs", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_classifier_results() -> None:
    triage_logs = load_module()
    for fixture, expected_primary in FIXTURES:
        text = (ROOT / fixture).read_text(encoding="utf-8")
        results = triage_logs.classify(text)
        assert results, f"{fixture}: expected at least one classification"
        actual_primary = results[0]["name"]
        assert actual_primary == expected_primary, (
            f"{fixture}: expected primary {expected_primary!r}, got {actual_primary!r}"
        )


def assert_cli_formats() -> None:
    json_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(ROOT / FIXTURES[0][0]), "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    parsed = json.loads(json_run.stdout)
    assert parsed[0]["name"] == FIXTURES[0][1]

    markdown_run = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(ROOT / "examples/compute-budget.log"),
            "--format",
            "markdown",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Primary cause: Compute budget exceeded" in markdown_run.stdout
    assert "## Fix" in markdown_run.stdout


def main() -> int:
    assert_classifier_results()
    assert_cli_formats()
    print("Smoke tests passed: fixtures classified and CLI formats validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

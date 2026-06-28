#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-${CODEX_HOME:-$HOME/.codex}/skills/solana-tx-failure-triage}"
mkdir -p "$(dirname "$TARGET_DIR")"
if [ -e "$TARGET_DIR" ]; then
  echo "Target already exists: $TARGET_DIR" >&2
  echo "Choose another path or remove the existing directory yourself." >&2
  exit 1
fi
cp -R skill "$TARGET_DIR"
echo "Installed solana-tx-failure-triage to $TARGET_DIR"

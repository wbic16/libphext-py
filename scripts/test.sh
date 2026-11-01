#!/usr/bin/env bash
# test.sh — run the full pytest suite against THIS checkout.
#
# Route, in order:
#   1. uv installed  -> `uv sync` (creates/refreshes .venv and uv.lock),
#      then `uv run pytest`.
#   2. .venv exists  -> `.venv/bin/python -m pytest`.
#   3. neither       -> create .venv with python3 -m venv, install this
#      checkout editable with its dev extras (pytest), then run pytest.
#
# pyproject.toml sets pytest's pythonpath to ".", so every route tests
# the code in this checkout, never a `phext` installed elsewhere.
# The suite's exit code is this script's exit code.
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v uv >/dev/null 2>&1; then
  uv sync
  uv run pytest "$@"
elif [ -x .venv/bin/python ]; then
  .venv/bin/python -m pytest "$@"
else
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -e ".[dev]"
  .venv/bin/python -m pytest "$@"
fi

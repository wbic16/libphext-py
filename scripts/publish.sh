#!/usr/bin/env bash
# publish.sh — test, build, and (only on explicit confirmation) publish
# the release-dist/ artifacts to PyPI.
#
# Safety gate: without PUBLISH_CONFIRM=1 this script stops after
# printing the exact artifacts and version it WOULD publish. Nothing is
# uploaded. To publish for real:
#
#   UV_PUBLISH_TOKEN=<pypi-token> PUBLISH_CONFIRM=1 scripts/publish.sh
#
# Credentials come from the environment or your keyring — NEVER put a
# token in this script or commit one.
#   - uv route:      UV_PUBLISH_TOKEN (a PyPI API token for `phext`)
#   - twine route:   TWINE_USERNAME=__token__ and TWINE_PASSWORD=<token>
set -euo pipefail
cd "$(dirname "$0")/.."

scripts/test.sh
scripts/build.sh

version=$(grep -m1 '^version = ' pyproject.toml | grep -o '"[^"]*"' | tr -d '"')
echo
echo "Artifacts to publish (phext $version):"
ls -1 release-dist/
echo

if [ "${PUBLISH_CONFIRM:-}" != "1" ]; then
  echo "DRY RUN — nothing was uploaded."
  echo "To publish these artifacts to PyPI, re-run with PUBLISH_CONFIRM=1"
  echo "and your PyPI token in the environment (see the header of this script)."
  exit 0
fi

if command -v uv >/dev/null 2>&1; then
  uv publish release-dist/*
else
  if [ ! -x .venv/bin/python ]; then
    echo "ERROR: no uv and no .venv — run scripts/test.sh first to set up the environment." >&2
    exit 1
  fi
  if ! .venv/bin/python -c "import twine" >/dev/null 2>&1; then
    .venv/bin/pip install --quiet twine
  fi
  .venv/bin/python -m twine upload release-dist/*
fi
echo "Published phext $version to PyPI."

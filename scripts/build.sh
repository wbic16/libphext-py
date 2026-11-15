#!/usr/bin/env bash
# build.sh — build the sdist and wheel for the current version into a
# CLEAN release-dist/ directory.
#
# Why release-dist/ and not dist/: dist/ holds old builds that are
# checked into git, and publishing tools upload everything they are
# pointed at. Building into a freshly deleted release-dist/ guarantees
# only this version's artifacts can be published.
#
# The version is read from pyproject.toml and phext/__init__.py, and
# the build FAILS if the two disagree — set the version in both places
# before building (see readme.md, "Development").
set -euo pipefail
cd "$(dirname "$0")/.."

pyproject_version=$(grep -m1 '^version = ' pyproject.toml | grep -o '"[^"]*"' | tr -d '"')
init_version=$(grep -o '__version__ = "[^"]*"' phext/__init__.py | grep -o '"[^"]*"' | tr -d '"')
if [ "$pyproject_version" != "$init_version" ]; then
  echo "ERROR: version mismatch — pyproject.toml says '$pyproject_version' but phext/__init__.py says '$init_version'." >&2
  echo "Set the same version in both files, then re-run scripts/build.sh." >&2
  exit 1
fi
echo "Building phext $pyproject_version"

rm -rf release-dist
if command -v uv >/dev/null 2>&1; then
  uv build --out-dir release-dist
else
  # Fallback: python -m build (>= 0.10) inside .venv; create the venv
  # and install `build` + this checkout's dev tooling if needed.
  if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -e ".[dev]"
  fi
  if ! .venv/bin/python -c "import build" >/dev/null 2>&1; then
    .venv/bin/pip install --quiet build
  fi
  .venv/bin/python -m build --outdir release-dist
fi

echo "Artifacts in release-dist/:"
ls -1 release-dist/

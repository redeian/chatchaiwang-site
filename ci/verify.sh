#!/usr/bin/env bash
# One command that answers "is this commit shippable".
#
# Everything the factory needs, and everything a human needs before a push.
# It must pass on a fresh clone of main, on a machine with no Chrome, or the
# repository is not gradable and no amount of agent will help.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=${PYTHON:-python3}
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# build_cv.py rewrites assets/cv.pdf with a new timestamp on every run. That is
# not drift, so it is restored on every exit path, including a failing one: a
# failed check must not leave the tree dirty, or the next run starts by calling
# this repository's own dirt a finding.
trap 'git checkout -- assets/cv.pdf 2>/dev/null || true' EXIT

echo "== build =="
env -u PYTHONPATH "$PY" build.py >/dev/null

echo "== check =="
env -u PYTHONPATH "$PY" check.py

echo "== generated html is current =="
git diff --exit-code --quiet -- '*.html' || {
  echo "the committed html is not what build.py produces. run build.py and commit the result." >&2
  exit 1
}

echo "== behaviour tests =="
env -u PYTHONPATH "$PY" -m pytest -q tests/ "$@"

# build_cv.py rewrites assets/cv.pdf with a new timestamp on every run. That is
# not drift, so it is restored rather than reported.
git checkout -- assets/cv.pdf 2>/dev/null || true

echo "== ok =="

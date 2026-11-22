#!/usr/bin/env bash
# release.sh — build, gate, publish and verify chatchaiwang.com.
#
#   ./release.sh                      build and gate only (no network, no commit)
#   ./release.sh --publish "message"  build, gate, commit, push, wait, verify live
#   ./release.sh --verify             verify the live site against this build only
#
# Nothing is published unless check.py passes. Nothing is called done unless the
# live URLs answer 200 from the GitHub edge, not from a cached local resolver.

set -euo pipefail
cd "$(dirname "$0")"

PY="env -u PYTHONPATH /opt/homebrew/anaconda3/bin/python3"
REPO="redeian/chatchaiwang-site"
BRANCH="main"
HOST="www.chatchaiwang.com"
EDGE="185.199.108.153"          # any GitHub Pages A record
PATHS=(/ /th/ /publications.html /speaking.html /llms.txt /sitemap.xml /robots.txt /assets/publications.bib)

die() { printf '\n✗ %s\n' "$1" >&2; exit 1; }

build() {
  printf '› build\n'
  $PY build.py | tail -4
  printf '› gates\n'
  $PY check.py
}

# The local DNS cache still answers with the old builder after a domain move, so
# every live check pins the GitHub edge explicitly. See README "Verifying" .
verify_live() {
  printf '\n› live check against %s\n' "$EDGE"
  local bad=0
  for path in "${PATHS[@]}"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
      --resolve "$HOST:443:$EDGE" "https://$HOST$path")
    printf '  %-28s %s\n' "$path" "$code"
    [ "$code" = "200" ] || bad=1
  done
  [ "$bad" -eq 0 ] || die "the edge is not serving this build yet — wait a minute and run ./release.sh --verify"
  printf '\n✓ live and correct\n'
}

wait_for_pages() {
  local head_sha
  head_sha=$(git rev-parse HEAD)
  printf '\n› waiting for GitHub Pages to build %s\n' "${head_sha:0:7}"
  for _ in $(seq 1 60); do
    line=$(gh api "repos/$REPO/pages/builds/latest" --jq '.commit + " " + .status' 2>/dev/null || echo "")
    case "$line" in
      "$head_sha built") printf '  built\n'; return 0 ;;
      "$head_sha"*)      printf '  %s\n' "${line#* }" ;;
    esac
    sleep 5
  done
  printf '  still building — run ./release.sh --verify in a minute\n'
}

case "${1:-}" in
  --verify)
    verify_live
    ;;
  --publish)
    msg="${2:-}"
    [ -n "$msg" ] || die 'usage: ./release.sh --publish "commit message"'
    build
    git add -A
    if git diff --cached --quiet; then
      printf '\n· nothing changed since the last commit\n'
    else
      git -c user.name="Chatchai Wangwiwattana" -c user.email="chatchai_wan@utcc.ac.th" \
        commit -q -m "$msg"
      printf '\n› pushed %s\n' "$(git log -1 --format='%h %s' | cut -c1-72)"
      git push origin "$BRANCH" 2>&1 | tail -1
    fi
    wait_for_pages
    verify_live
    ;;
  ""|--dry)
    build
    printf '\n· dry run — nothing committed. Use ./release.sh --publish "message" to ship.\n'
    ;;
  *)
    die "unknown option $1"
    ;;
esac

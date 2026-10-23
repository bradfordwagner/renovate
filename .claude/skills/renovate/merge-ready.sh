#!/usr/bin/env bash
# Usage: merge-ready.sh <owner/repo> <pr-number>
# Exit 0 only when the PR is a Renovate PR that is safe to squash-merge. Otherwise print the reason and exit 1.
set -euo pipefail

repo=$1
pr=$2

json=$(gh pr view "$pr" -R "$repo" --json state,author,headRefName,mergeable,mergeStateStatus,statusCheckRollup)

fail() { echo "NOT READY $repo#$pr: $1" >&2; exit 1; }
field() { jq -r "$1" <<<"$json"; }

[ "$(field .state)" = OPEN ] || fail "state is $(field .state)"
[ "$(field .author.login)" = app/bradfordwagner-renovate ] || fail "author is $(field .author.login)"
case "$(field .headRefName)" in renovate/*) ;; *) fail "head is $(field .headRefName)" ;; esac
[ "$(field .mergeable)" = MERGEABLE ] || fail "mergeable is $(field .mergeable)"
[ "$(field .mergeStateStatus)" = CLEAN ] || fail "mergeStateStatus is $(field .mergeStateStatus)"
[ "$(field '.statusCheckRollup|length')" -gt 0 ] || fail "no checks reported yet"

bad=$(field '[.statusCheckRollup[]|select(.status!="COMPLETED" or .conclusion!="SUCCESS")|"\(.name):\(.status)/\(.conclusion)"]|join(", ")')
[ -z "$bad" ] || fail "checks not green: $bad"

echo "READY $repo#$pr"

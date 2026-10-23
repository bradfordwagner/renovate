#!/usr/bin/env bash
set -euo pipefail

repo=${1:?usage: merge-ready.sh <owner/repo> <pr-number>}
pr=${2:?usage: merge-ready.sh <owner/repo> <pr-number>}

fail() { echo "NOT READY $repo#$pr: $1" >&2; exit 1; }

case "$repo" in
  bradfordwagner/k8s-deployments|bradfordwagner/infra) fail "cluster-state repo; deploy-test first" ;;
esac

json=$(gh pr view "$pr" -R "$repo" --json state,author,headRefName,mergeable,mergeStateStatus,statusCheckRollup)
field() { jq -r "$1" <<<"$json"; }

[ "$(field .state)" = OPEN ] || fail "state is $(field .state)"
[ "$(field .author.login)" = app/bradfordwagner-renovate ] || fail "author is $(field .author.login)"
case "$(field .headRefName)" in renovate/*) ;; *) fail "head is $(field .headRefName)" ;; esac
[ "$(field .mergeable)" = MERGEABLE ] || fail "mergeable is $(field .mergeable)"
[ "$(field .mergeStateStatus)" = CLEAN ] || fail "mergeStateStatus is $(field .mergeStateStatus)"
[ "$(field '.statusCheckRollup|length')" -gt 0 ] || fail "no checks reported yet"

bad=$(field '[.statusCheckRollup[]
  | if .__typename == "StatusContext"
    then select(.state != "SUCCESS") | "\(.context):\(.state)"
    else select(.status != "COMPLETED" or ((.conclusion | IN("SUCCESS","SKIPPED","NEUTRAL")) | not)) | "\(.name):\(.status)/\(.conclusion)"
    end] | join(", ")')
[ -z "$bad" ] || fail "checks not green: $bad"

echo "READY $repo#$pr"

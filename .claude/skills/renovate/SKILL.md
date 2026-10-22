---
name: renovate
description: Triage the open Renovate PRs across every bradfordwagner repo — list them, read release notes, run each repo's own checks, recommend merge/hold/close, and act only on approval. Use for /renovate, "check my renovate PRs", "what dependency updates are waiting", or approving updates held on a Dependency Dashboard.
---

# Renovate PR triage

Renovate runs from `bradfordwagner/renovate` as the `bradfordwagner-renovate` GitHub App, once a day at 11:00 UTC,
for the repos in `config.js`. Every PR and Dependency Dashboard it creates is authored by the App and assigned to
`bradfordwagner`.

## 1. List

```sh
gh search prs --author app/bradfordwagner-renovate --owner bradfordwagner --state open \
  --json repository,number,title,labels,url
```

Search is indexed and can lag minutes behind a fresh run. If it comes back empty right after a run, ask each repo in
the allowlist directly:

```sh
gh api repos/bradfordwagner/renovate/contents/config.js -q .content | base64 -d \
  | grep -oE '"bradfordwagner/[^"]+"' | tr -d '"' \
  | while read -r r; do gh pr list -R "$r" --author app/bradfordwagner-renovate --json number,title,url; done
```

Also read each repo's open Dependency Dashboard issue (same author). Updates held behind `dependencyDashboardApproval`
(for example, k3s minors in `infra`) appear only there, never as PRs.

## 2. Triage each PR

- `gh pr view <n> -R <repo> --json body,files,labels,statusCheckRollup,mergeable`. The body carries the version
  range, the release notes, and any `prBodyNotes` the repo's `renovate.json` attaches. Those notes name coupled
  changes Renovate cannot make itself, such as a pin mirrored in another repo. Treat them as part of the change.
- Read the release notes for the whole range, not only the last version. Call out breaking changes, removed
  options, CRD changes and minimum-version bumps.
- Classify the update: patch, minor or major. Majors also carry the `major` label.
- Run the repo's own checks, as its `CLAUDE.md` describes them, against the PR branch in a temp worktree. If the repo
  has CI, its `statusCheckRollup` is the evidence. `infra` and `k8s-deployments` have no CI:
  - `k8s-deployments`: `helm lint` and `helm template` on each changed chart. For anything that changes what runs,
    deploy to the `local` pool cluster the session claimed (`task local_apply`, then `task local_status`). Never use
    `dev` or a remote cluster.
  - `infra`: a lookup-only Renovate dry run, plus whatever its `CLAUDE.md` names for the files touched.
- A check that could not run is a gap, not a pass. Say which check and why.

## 3. Report

One line per PR, ranked with majors and failures first: `repo#n`, update type, verdict (merge / hold / close), and
the one piece of evidence behind it. Then list any dashboard items waiting for approval.

## 4. Act only on explicit approval

- Merge: `gh pr merge <n> -R <repo> --squash`.
- Approve a held update: edit the dashboard issue body and tick its `- [ ] <!-- approve-branch=... -->` box. Renovate
  opens the PR on its next run.
- Rebase or retry a PR: tick its `- [ ] <!-- rebase-check -->` box in the PR body.
- Close: `gh pr close`. Renovate then ignores that version. A newer version opens a new PR.
- Start a run early: `gh workflow run renovate.yaml -R bradfordwagner/renovate`.

Never push commits to a `renovate/*` branch. Renovate stops updating a branch someone else has modified. If a PR
needs a manual fix, close it and make the change in a normal branch.

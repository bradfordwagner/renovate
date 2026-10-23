# renovate

Runs Renovate for every repo listed in `config.js`, once a day at 11:00 UTC, and holds the preset those repos
extend (`default.json`).

## How it works

`.github/workflows/renovate.yaml` mints a token for the Renovate GitHub App and runs Renovate with `config.js`.
PRs are therefore authored by the App's bot user, not by a person, so GitHub notifies the assignee and repo
watchers. A PR authored with your own token never notifies you.

The App is installed on all of the account's repos, but Renovate only processes the repos in `repositories`.

This repo is public, so its Actions minutes are free. Its run logs are public too, and they name the dependencies,
branches and PRs of every repo processed.

Each run also sets `delete_branch_on_merge` on every repo in `repositories` (separate job; needs the App's Administration
permission set to read and write).

Start a run early with `gh workflow run renovate.yaml -R bradfordwagner/renovate`.

## Opting a repo in

1. Add `bradfordwagner/<repo>` to `repositories` in `config.js`.
2. On the next run, a repo with no Renovate config gets an onboarding PR that extends this preset. Merge it.

A repo that already has `renovate.json` needs this in it instead:

```json
{
  "extends": ["github>bradfordwagner/renovate"]
}
```

Keep repo-specific rules (groups, custom managers, versioning) in the repo's own `renovate.json`. Put only what
every repo should share in `default.json`.

A `postUpgradeTasks` command only runs if it matches `allowedCommands` in `config.js`.

## Setup

- Variable `RENOVATE_APP_CLIENT_ID`: the App's Client ID.
- Secret `RENOVATE_APP_PRIVATE_KEY`: a private key generated on the App's settings page.

App repository permissions: Checks, Commit statuses, Contents, Issues, Pull requests and Workflows set to read and
write. Administration set to read and write. Dependabot alerts and Metadata set to read-only. No webhook.

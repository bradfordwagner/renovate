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

The App is [bradfordwagner-renovate](https://github.com/settings/apps/bradfordwagner-renovate), installed on all
repositories. This repo needs:

- Variable `RENOVATE_APP_CLIENT_ID`: the App's Client ID.
- Secret `RENOVATE_APP_PRIVATE_KEY`: a private key generated on the App's settings page.

## Rotating the private key

1. On the [App's settings page](https://github.com/settings/apps/bradfordwagner-renovate), under *Private keys*,
   click *Generate a private key*.
2. Upload it, then delete the local copy:

   ```sh
   gh secret set RENOVATE_APP_PRIVATE_KEY -R bradfordwagner/renovate < ~/Downloads/bradfordwagner-renovate.*.private-key.pem
   rm ~/Downloads/bradfordwagner-renovate.*.private-key.pem
   ```

3. Run `gh workflow run renovate.yaml -R bradfordwagner/renovate` and check that it passes.
4. Delete the old key on the settings page. GitHub keeps every key valid until it is deleted.

App repository permissions: Checks, Commit statuses, Contents, Issues, Pull requests and Workflows set to read and
write. Dependabot alerts and Metadata set to read-only. No webhook.

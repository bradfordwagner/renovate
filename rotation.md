# Rotating the private key

1. On the [App's settings page](https://github.com/settings/apps/bradfordwagner-renovate), under *Private keys*,
   click *Generate a private key*.
2. Upload it, then delete the local copy:

   ```sh
   gh secret set RENOVATE_APP_PRIVATE_KEY -R bradfordwagner/renovate < ~/Downloads/bradfordwagner-renovate.*.private-key.pem
   rm ~/Downloads/bradfordwagner-renovate.*.private-key.pem
   ```

3. Run `gh workflow run renovate.yaml -R bradfordwagner/renovate` and check that it passes.
4. Delete the old key on the settings page. GitHub keeps every key valid until it is deleted.

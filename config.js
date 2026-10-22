module.exports = {
  platform: "github",
  repositories: [
    "bradfordwagner/renovate",
    "bradfordwagner/infra",
    "bradfordwagner/k8s-deployments",
    "bradfordwagner/devtainer",
    "bradfordwagner/vault-plugin-keycloak-secrets",
    "bradfordwagner/vault-plugin-manager",
  ],
  onboardingConfig: {
    $schema: "https://docs.renovatebot.com/renovate-schema.json",
    extends: ["github>bradfordwagner/renovate"],
  },
  allowedCommands: [
    "^node \\.github/renovate/gateway-api-from-istio\\.mjs \\d+\\.\\d+\\.\\d+$",
  ],
};

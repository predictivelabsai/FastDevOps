---
name: coolify-cicd
description: Inspect, plan, configure, deploy, verify, troubleshoot, or change the canonical domain of a Fast* repository through the FastDevOps Coolify control plane. Use for requests such as `/skill coolify-cicd FastFunnel`, adding or cutting over a FastSME service domain, redeploying after DNS changes, checking whether a GitHub commit is live, configuring a GitHub App or manual webhook, or preparing a GCP Pulumi fallback.
---

# Operate FastSME CI/CD

Accept a repository or service name and normalize it through
`config/services.yaml`; never guess a Coolify UUID.

1. Read repository-local `AGENTS.md`, Dockerfile, compose file, environment
   sample, branch/upstream state, exposed port, bind address, and health route.
2. Run `python cli.py validate` and `python cli.py doctor <service>`.
3. Inspect Coolify read-only before changes with `status` and `env`. Never print
   environment values or API responses that may contain secrets.
4. Ensure the declared canonical hostname is controlled by the operator, DNS
   resolves to the VPS, TLS validates, the container binds `0.0.0.0`, and a
   cheap health route exists. Prefer `fastsme.com` subdomains, but preserve a
   deliberately selected standalone product domain.
5. Prefer one automatic trigger: Coolify GitHub App webhook on `main`. Use a
   GitHub Action/manual webhook only when the App is unavailable.
6. Before a mutation, identify the exact repo, branch, commit, application,
   domain, and expected impact. Require explicit authorization.
7. After an authorized deploy, verify the GitHub delivery, matching Coolify
   deployment/commit, terminal success, health route, TLS, and canonical URL.
8. For GCP, run `pulumi preview` first and report creates, updates,
   replacements, and deletes. Never run `up` or `destroy` without explicit
   authorization.

Treat `COOLIFY_API_TOKEN`, `XAI_API_KEY`, GitHub secrets, passwords, and Pulumi
secrets as values that may only live in secret stores or ignored local
environment files.

## Canonical domain cutover

1. Resolve the new hostname from its authoritative nameservers and confirm it
   points to the intended Coolify server before attaching it.
2. Search the service repository and `config/services.yaml` for the old host.
   Update the canonical domain plus runtime public URL, CORS origin, email links,
   and OAuth callback as applicable. Keep exactly one domain unless aliases were
   explicitly requested.
3. Add the new Google OAuth callback before removing the old callback. Preserve
   all unrelated callbacks and never rotate the shared client secret for a
   domain change.
4. Run `validate`, reconcile with `provision <service> --yes`, and read back the
   application's domain. Then run `env <service> --sync --yes` so runtime URLs
   match the route.
5. Redeploy the exact pushed commit. Verify the GitHub delivery, webhook-origin
   Coolify deployment, health, TLS, login redirect, static assets, and important
   application routes on the new hostname.
6. Confirm the former hostname is absent from the Coolify application and no
   longer routes to it. Do not delete DNS records or OAuth callbacks unless the
   user explicitly requests those separate destructive changes.

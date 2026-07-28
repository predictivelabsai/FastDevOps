---
name: coolify-cicd
description: Inspect, plan, configure, deploy, verify, or troubleshoot a Fast* repository through the FastDevOps Coolify control plane. Use for requests such as `/skill coolify-cicd FastFunnel`, adding a FastSME service/domain, checking whether a GitHub commit is live, configuring a GitHub App or manual webhook, or preparing a GCP Pulumi fallback.
---

# Operate FastSME CI/CD

Accept a repository or service name and normalize it through
`config/services.yaml`; never guess a Coolify UUID.

1. Read repository-local `AGENTS.md`, Dockerfile, compose file, environment
   sample, branch/upstream state, exposed port, bind address, and health route.
2. Run `python cli.py validate` and `python cli.py doctor <service>`.
3. Inspect Coolify read-only before changes with `status` and `env`. Never print
   environment values or API responses that may contain secrets.
4. Ensure the canonical hostname is under `fastsme.com`, DNS resolves to the
   VPS, TLS validates, the container binds `0.0.0.0`, and a cheap health route
   exists.
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

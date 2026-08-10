# FastDevOps operational skills

Invoke the repository skill as:

```text
/skill coolify-cicd FastFunnel
```

The installed skill source is
[`skills/coolify-cicd/SKILL.md`](skills/coolify-cicd/SKILL.md).

Configure or repair a Google OAuth callback with authenticated `gcloud`
context, safe browser handoff, and a non-secret live verification probe:

```text
/skill gcloud-oauth-sso FastAccounts
```

The versioned workflow and audit helper live in
[`skills/gcloud-oauth-sso/`](skills/gcloud-oauth-sso/).

Create or refresh a product landing page and its Google SSO entry point with:

```text
/skill fastsme-landing FastCRM
```

The fleet-wide source, product palettes, callback contract, and idempotent sync
tool live in [`skills/fastsme-landing/`](skills/fastsme-landing/). Streamlit
products are explicitly deferred until they are migrated.

The same landing workflow owns each product's public `/developers` surface.
After API or landing changes, validate the committed OpenAPI snapshots and
navigation contract with:

```bash
python scripts/validate_fastapi_fleet.py
python scripts/validate_seo_fleet.py
```

## FastFunnel rollout

1. Verify the trusted certificate for `coolify.fastsme.com`.
2. Generate `COOLIFY_API_TOKEN`; keep it in a local ignored `.env` and CI
   secret store.
3. In Coolify, create project `FastSME` and install a GitHub App on
   `predictivelabsai` with access to the public Fast repositories.
4. Create application `fastfunnel` from `predictivelabsai/fastfunnel`, branch
   `main`, Dockerfile `/Dockerfile`, port `5005`.
5. Attach `https://funnel.fastsme.com`, health path `/healthz`, and persistent
   storage at `/app/data`.
6. Set the runtime variables declared in `config/services.yaml`; set
   `XAI_API_KEY` only when supplied.
7. Add the IONOS A record for `funnel.fastsme.com` to `191.218.164.166`.
8. Deploy, then verify the exact Git commit, health endpoint, TLS, static
   assets, console errors, and one browser flow.

## Fleet rollout

Inventory all Fast* repos, then onboard them in waves:

- Wave 1: repos with Dockerfiles and standalone SQLite/local state.
- Wave 2: repos with external databases, queues, or multiple containers.
- Wave 3: repos missing Dockerfiles or owned outside `predictivelabsai`.

Each service gets a unique `<slug>.fastsme.com`, health route, volume/database
decision, environment-name manifest, resource limits, and rollback smoke test.
Do not copy one shared secret into services that do not consume it.

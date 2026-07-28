# FastDevOps

Deployment orchestration for the public `predictivelabsai/Fast*` repositories.
Coolify is the primary runtime; a config-driven Pulumi program keeps a GCP
Cloud Run migration path available.

## Service fleet

The catalog in `config/services.yaml` defines the 19 FastSME applications.
`data/fast-domains.csv` is the DNS/source inventory used to audit that catalog.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.sample .env
```

Create a Coolify API token at **Keys & Tokens → API Tokens**, then expose it
only in the shell:

```bash
export COOLIFY_API_TOKEN=...
python cli.py doctor
python cli.py status fastfunnel
python cli.py env fastfunnel
python cli.py env fastfunnel --sync
python cli.py provision --yes
python cli.py deploy --yes
```

The CLI loads `COOLIFY_API_TOKEN` and an optional `COOLIFY_BASE_URL` from the
ignored local `.env`. The CLI defaults to read-only operations. Deployment and environment writes
require an explicit command and confirmation; `--yes` is intended for CI.
Provisioning is idempotent: existing applications are reconciled, missing
applications and declared persistent volumes are created, and FastFunnel's
hand-tuned configuration is preserved.

## CI/CD model

Preferred:

```text
push main → Coolify GitHub App webhook → Dockerfile build → health check → route
```

The FastDevOps CLI is the control plane for inventory, status, manual deploys,
and environment synchronization. GitHub Actions can call it with
`COOLIFY_API_TOKEN` when a GitHub App cannot be installed, but using both
automatic mechanisms for one service should be avoided.

## GCP preview

The same `config/services.yaml` drives Pulumi Cloud Run resources:

```bash
pip install -e ".[gcp]"
pulumi preview --cwd infra/gcp --stack production
```

Pulumi state, service-account JSON, `.env`, and secret values must never be
committed.

## Adding services

Add a service to `config/services.yaml`, then run:

```bash
python cli.py validate
python cli.py doctor <service>
```

See [SKILLS.md](SKILLS.md) for the rollout runbook.

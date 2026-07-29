# FastSME shared-core architecture analysis

## Executive recommendation

Create a small, dependency-light Python distribution named `fastsme-core`.
Extract authentication and framework adapters first, then UI primitives and AI
transport. Keep product schemas, domain services, seed data, workflows, prompts,
and most views inside each application.

Do not combine all 18 applications into one package or framework. FastFund and
FastPPM are substantially larger platforms with graph, document, and analytics
dependencies; forcing those dependencies into every product would make the thin
apps slower to build and harder to evolve.

The target dependency direction is:

```text
Fast* product
  ├── product domain, schema, views, tools, prompts
  └── fastsme-core
        ├── auth + transactional email
        ├── Google OIDC
        ├── FastHTML/FastAPI adapters
        ├── UI primitives and design tokens
        ├── AI provider/streaming contracts
        └── operational health/config helpers
```

## Portfolio findings

The audit covered the 18 migrated repositories and excluded FastInsure while it
remains a Streamlit application.

| Measure | Finding |
|---|---:|
| Python files | 405 |
| Approximate Python lines | 77,745 |
| Repositories using FastHTML | 18/18 |
| Repositories using SQLite | 18/18 |
| Repositories with PostgreSQL-capable code | 7/18 |
| Repositories with SSE/streaming code | 15/18 |
| Repositories with xAI integration | 15/18 |
| Repositories with Postmark integration/config | 18/18 |
| Repositories with a shared Coolify launcher | 18/18 |
| Thin apps following the shared `web_app.py` pattern | 13 |

The 13-app FastHTML cohort is FastClinic, FastCRM, FastDocs, FastDrive,
FastERP, FastESM, FastHelpdesk, FastHRM, FastInsights, FastMail, FastMeet,
FastSheets, and FastSlides.

Within that cohort:

- `account_auth.py` is byte-identical across all 13 repositories.
- `google_auth.py` is byte-identical across all 13 repositories.
- `scripts/coolify.py` is byte-identical across all 13 repositories.
- Pairwise source similarity averages approximately 56% for `web_app.py`, 54%
  for `web/layout.py`, and 35% for `web/ai.py`.
- Database schemas are product-specific: `db.py` similarity averages only 16%.

These numbers point to a clear boundary: extract platform mechanics, but leave
the domain and persistence models local.

## Proposed package structure

```text
fastsme-core/
  pyproject.toml
  src/fastsme/
    auth/
      models.py
      passwords.py
      tokens.py
      store.py
      service.py
      google.py
      postmark.py
      protocols.py
      adapters/
        fasthtml.py
        fastapi.py
    ui/
      auth_modal.py
      shell.py
      tokens.py
      assets/
        core.css
        auth.js
    ai/
      config.py
      providers.py
      streaming.py
      messages.py
      tools.py
    ops/
      config.py
      health.py
      logging.py
  tests/
```

Publish one base distribution with optional extras:

```toml
fastsme-core
fastsme-core[auth]
fastsme-core[ai]
fastsme-core[charts]
fastsme-core[all]
```

The default install should remain lightweight. `auth` can depend on FastHTML
and its session stack. `ai` can add the OpenAI-compatible client and optional
LangGraph adapter. Heavy packages such as pandas, Playwright, Neo4j, office
document parsers, and plotting libraries must remain product dependencies.

## 1. Authentication is the first extraction

The new account implementation is already the strongest package candidate:
the same module is present in every app, with framework/session callbacks
providing the application-specific bridge.

Extract:

- scrypt password hashing and constant-time verification;
- account persistence and migrations;
- email verification;
- expiring, single-use password-reset tokens;
- rate limiting and enumeration-safe responses;
- Google identity linking;
- Postmark delivery;
- CarHero-style modal;
- FastHTML and FastAPI route adapters.

Define an application adapter rather than importing product database modules:

```python
class IdentityAdapter(Protocol):
    def establish_session(self, session: MutableMapping, identity: Identity) -> None: ...
    def disable_identity(self, email: str) -> bool: ...
```

The thin apps can use `EmailSessionAdapter("user")`. FastClinic uses
`EmailSessionAdapter("user_email")`. FastCMS, FastFund, FastLMS, and FastPPM
provide small adapters that provision or resolve their own user records.

### Important identity decision

The present rollout gives every application an independent account database.
It standardizes behavior but is not cross-application SSO: a password
registered in FastCRM does not automatically exist in FastDocs.

If the business goal is one FastSME account across all products, the next step
should be a central OpenID Connect identity service or a managed identity
provider—not a shared SQLite file mounted into 18 containers. Each product
would become an OIDC relying party, while Google and email/password live in one
identity plane.

Recommended progression:

1. Package the current local account service to eliminate source duplication.
2. Stabilize its `IdentityAdapter` contract.
3. Replace its local store with a central OIDC issuer when cross-product SSO is
   required.

## 2. UI primitives, not whole product layouts

Extract:

- authentication modal and JavaScript controller;
- palette/design-token dataclass;
- navigation, button, card, empty-state, and status components;
- responsive three-pane grid primitives;
- shared accessibility behavior;
- shared favicon and metadata helpers.

Keep each product's navigation model, page composition, branded palette,
feature copy, dashboards, and domain views local.

An appropriate API is declarative:

```python
theme = ProductTheme(
    name="FastCRM",
    accent="#2563eb",
    tint="#eff6ff",
)
```

The package should output components and CSS variables. It should not own a
single global stylesheet that prevents product-level design changes.

## 3. AI provider and streaming contracts

The 12 thin apps have different domain tools but repeat provider setup,
OpenAI-compatible xAI configuration, SSE framing, message normalization,
fallback behavior, and error handling.

Extract:

- provider configuration (`xai`, OpenAI, Anthropic, Google);
- model availability checks;
- OpenAI-compatible client construction;
- normalized chat messages and tool results;
- SSE event encoding and heartbeat/error events;
- bounded timeouts, retry policy, and telemetry hooks;
- graceful no-key fallback contract.

Keep:

- system prompts;
- domain tools and permissions;
- retrieval queries;
- product-specific response rendering;
- approval and mutation policies.

The package should not expose a generic “agent that can do everything.” It
should provide transport and lifecycle mechanics while every product remains
responsible for its tool boundaries.

## 4. Data and migrations

Do not extract product tables or generic CRUD repositories. The low similarity
between database modules confirms that the schemas represent real product
boundaries.

Extract only:

- SQLite connection pragmas and transaction context managers;
- schema-version table and migration runner;
- JSON serialization helpers;
- pagination and safe query utilities;
- test fixtures for temporary SQLite databases.

Use a `Storage` protocol only where a product genuinely supports multiple
backends, as FastFund already does. Avoid imposing its graph/relational
abstraction on the thin apps.

## 5. Operational helpers

The per-repository `scripts/coolify.py` launchers should eventually become a
console entry point:

```bash
fastsme deploy
fastsme env --sync
fastsme status
```

The inventory, domains, opaque Coolify UUIDs, and environment declarations
must remain in FastDevOps `config/services.yaml`. The package should locate and
invoke that control plane; it must not carry a second service catalog.

Useful application-side helpers:

- `/healthz` response and dependency checks;
- structured logging and request IDs;
- environment validation with secret-name-only diagnostics;
- build/release metadata display;
- secure session defaults.

## Packaging and release model

Create `predictivelabsai/fastsme-core` as a public repository using `src/`
layout, typed public APIs, and semantic versioning.

Recommended release controls:

1. Unit tests on Python 3.11–3.13.
2. Contract tests for FastHTML and FastAPI adapters.
3. A compatibility matrix containing at least one thin app plus FastCMS,
   FastLMS, FastFund, and FastPPM.
4. PyPI Trusted Publishing through GitHub OIDC; no long-lived PyPI token.
5. Conventional commits or explicit release PRs with generated changelogs.
6. Dependabot/Renovate PRs in the 18 consumers.
7. Pin compatible ranges such as `fastsme-core>=0.1,<0.2` until the API reaches
   1.0.

Do not install the package directly from a moving Git branch in production.
Every Coolify build should resolve an immutable PyPI version or commit-tagged
artifact.

## Migration plan

### Phase 0 — contract tests

- Freeze current auth behavior in shared tests.
- Add modal/accessibility and email-provider tests.
- Add adapter tests for the five custom applications.
- Record current production smoke tests in FastDevOps.

### Phase 1 — `fastsme-core[auth]`

- Publish account service, Google OIDC, Postmark, modal, and route adapters.
- Migrate FastCRM first as the reference thin app.
- Migrate FastClinic and FastESM to validate alternate session keys/redirects.
- Migrate the remaining thin apps.
- Migrate FastCMS, FastLMS, FastFund, and FastPPM using explicit identity
  adapters.
- Remove copied modules only after every consumer pins the released package.

### Phase 2 — UI foundation

- Extract tokens and small shell primitives.
- Migrate two visually different products first to prove theming remains local.
- Add screenshot/Playwright regression tests.

### Phase 3 — AI and streaming

- Extract provider configuration and SSE contracts.
- Migrate one read-only app first.
- Preserve every product's tool authorization and fallback behavior.

### Phase 4 — operations

- Replace copied Coolify launchers with a `fastsme` console command.
- Standardize health, release metadata, and logging.

### Phase 5 — central identity, if desired

- Select an OIDC issuer architecture.
- Migrate existing local identities with verified ownership.
- Use one FastSME session/identity plane while preserving per-product roles.

## What must remain outside `fastsme-core`

- Product database schemas and seed data.
- Frappe-derived domain models.
- Patient, HR, finance, document, mail, meeting, spreadsheet, and presentation
  business logic.
- FastFund/PPM graph, ingestion, document, and portfolio engines.
- Product prompts, agents, tools, and approval rules.
- Product-specific navigation and landing-page copy.
- Coolify service IDs, domains, and secrets.

## Near-term quality priorities

Only FastFunnel, FastERP, FastFund, and FastPPM currently contain identifiable
automated test modules. Before a large shared-core migration, add at least:

- anonymous landing and modal smoke tests for every app;
- registration, verification, login, forgot/reset, Google-link, and logout
  contract tests;
- authenticated root-route tests;
- database migration tests;
- one read-only domain workflow per product;
- production callback and email-delivery probes in FastDevOps.

The core package will reduce duplication, but it will also increase the blast
radius of a bad release. Consumer contract tests and staged rollouts are
therefore prerequisites, not follow-up work.

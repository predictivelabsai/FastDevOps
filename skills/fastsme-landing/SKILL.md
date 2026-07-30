---
name: fastsme-landing
description: Create, update, audit, and verify FastSME product landing pages and their Google SSO entry points. Use for Fast* public homepages, portfolio catalogue cards, app-specific light colour schemes, top-right Sign In controls, Google OAuth callback configuration, and fleet-wide landing-page consistency.
---

# FastSME landing pages

Read `README.md`, `SKILLS.md`, and `config/services.yaml` before changing the
fleet. Read the target repository's `AGENTS.md` or `CLAUDE.md` when present.

## Workflow

1. Run `python skills/fastsme-landing/scripts/sync_fasthtml_landings.py --check`
   to identify drift in the shared FastHTML cohort.
2. Treat `references/portfolio.yaml` as the content and colour source of truth.
   Match the accent to the target application's internal CSS, not to another
   product.
3. Keep the public surface white, typographically quiet, and specific about
   actual product capabilities. Use one primary action and a top-right Sign In.
4. Keep the authenticated product at its existing route. At `/`, show the
   landing only to anonymous visitors when the app already uses `/` internally.
5. Use `/auth/google` and `/auth/google/callback` for new OAuth integrations.
   Preserve state validation, request only `openid email profile`, verify the
   returned email, and never put client secrets in source or browser code.
6. Add only variable names/placeholders to committed samples:
   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`,
   `GOOGLE_ALLOWED_DOMAINS`, and `GOOGLE_ALLOWED_EMAILS`.
7. Run the target repository's compile/tests, then visually check desktop and
   mobile widths with Playwright. Exercise Sign In through the Google account
   chooser without completing a production login unless authorised.
8. For changes to the `fastsme-landing` repository, commit and push the
   validated task changes by default unless the user explicitly requests
   local-only work, no commit, or no push. Before committing, run
   `git diff --check`, inspect the staged paths for secrets and unrelated
   changes, use a descriptive commit message, push the current tracking
   branch, and verify the remote branch resolves to the new commit. Do not
   apply this default to other Fast* repositories.

Run the sync script without `--check` only when the user explicitly authorises
changes across the Fast* repositories. The script is idempotent and refuses
unknown source shapes.

For portfolio wording, app-specific palettes, feature lists, domains, and
repository mappings, read `references/portfolio.yaml`.

## Release gates

- No secrets, absolute developer paths, or demo passwords in diffs.
- Anonymous `/` renders the branded landing; an authenticated `/` retains the
  current app behavior.
- Sign In is keyboard reachable and remains visible at mobile widths.
- OAuth-disabled deployments show a useful configuration error and retain
  existing password login where one exists.
- Callback URIs exactly match the deployed HTTPS domains.
- Commit and deploy each repository independently; verify the deployed commit,
  TLS, health endpoint, landing page, and callback redirect.

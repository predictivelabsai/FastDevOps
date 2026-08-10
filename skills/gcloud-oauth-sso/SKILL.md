---
name: gcloud-oauth-sso
description: Configure, audit, repair, and verify Google OAuth/OpenID Connect SSO for FastSME and other web applications using Google Auth Platform, local ignored environment files, and Coolify runtime variables. Use for Google callback URI changes, redirect_uri_mismatch errors, shared web OAuth clients, Google Sign In enablement, or repeatable GCP OAuth onboarding.
---

# Configure Google Cloud OAuth SSO

## Establish the contract

1. Read the target repository instructions and auth implementation.
2. Confirm the app uses authorization-code OIDC, a random session-bound `state`, and only
   `openid email profile` unless the user requests more scopes.
3. Prefer `/auth/google` and `/auth/google/callback`. Resolve the exact production HTTPS
   callback before changing Google Cloud.
4. Reuse the established fleet OAuth web client when its consent screen and audience match.
   Do not create a client merely because a callback is absent.

## Handle credentials safely

- Use an existing authenticated `gcloud` account or browser profile first.
- Never print, screenshot, commit, or place client secrets or account passwords in shell
  arguments. Pause for human 2-step verification.
- Inspect environment variable names and equality checks without displaying values.
- Keep the target env file mode `0600`. Refuse tracked or unignored env files.

## Update Google Auth Platform

1. Run `scripts/audit_oauth_callback.py --env-file APP/.env --project PROJECT` to read the
   active `gcloud` account/project and probe the configured callback without exposing the
   client secret. Do not change the active account or project implicitly.
2. Read the system `playwright` skill, then open
   `https://console.cloud.google.com/auth/clients?project=PROJECT` in visible Playwright Chrome.
3. If Google needs authentication, enter the password only through a hidden interactive prompt.
   Stop for human 2-step verification; never pass credentials in a command or save browser state
   under the repository.
4. Open the existing web client whose full client ID matches `GOOGLE_CLIENT_ID` from the trusted
   env. Treat the display name only as a navigation hint.
5. Dismiss the Google cookie notice if it blocks controls. Record all existing redirect values,
   click the **Add URI** control under **Authorized redirect URIs** (not the JavaScript-origins
   control), fill the new empty row, and save. Never edit or remove existing rows.
6. Saving may return to the clients list. Reopen the same client, read every redirect value back,
   and require both that the new callback is present and that all recorded values remain present.
7. Rerun `scripts/audit_oauth_callback.py`; require `redirect_uri_mismatch=false`. Google can take
   several minutes to propagate changes.
8. Do not use `gcloud iap oauth-clients`; it is retired and does not manage generic OAuth web
   clients. Use `gcloud` for authenticated account/project discovery and the Google Auth Platform
   UI for this mutation.

## Sync and release

1. Preserve unfamiliar Coolify variables. Sync only `GOOGLE_CLIENT_ID`,
   `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` plus explicitly requested allowlists.
2. Use the FastDevOps service catalogue and `python cli.py env SERVICE --sync --yes` when the
   service is registered. Otherwise resolve the exact Coolify application and update only the
   named variables through the existing provider.
3. Restart or redeploy apps that read OAuth variables at process import.
4. Verify `/auth/google` redirects to Google with the exact callback, scopes, and nonempty state.
   Complete one authorized sign-in when permitted, then verify the callback establishes an
   application session.
5. Confirm health, TLS, deployed commit, and that local password auth still works when present.

## Failure boundaries

- Stop for human Google 2-step verification, consent publication, or an account/project choice.
- On `redirect_uri_mismatch`, compare decoded redirect URIs byte-for-byte and allow a few
  minutes for Google configuration propagation.
- Never rotate an existing client secret merely to add a callback.
- Never replace the fleet callback list with a single app callback.
- Delete temporary browser profiles after verification because they contain authenticated Google
  cookies.

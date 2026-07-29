# FastSME API contract

The 18 migrated FastSME products expose a same-process FastAPI integration
surface. FastInsure remains outside this contract while it is a Streamlit
application.

## Public routes

Every product serves:

| Route | Purpose |
|---|---|
| `/developers` | Branded developer documentation |
| `/api/` | API discovery document |
| `/api/v1/health` | API health and write-enabled state |
| `/api/v1/<resource>` | Paginated resource collection |
| `/api/v1/<resource>/<id>` | Individual resource |
| `/api/docs` | Swagger UI |
| `/api/redoc` | ReDoc |
| `/api/openapi.json` | Runtime OpenAPI 3 schema |
| `/swagger.json` | Stable compatibility schema |

Each repository also commits `swagger.json` at its root. CI should regenerate
the runtime schema and fail when it differs from that snapshot.

## Access model

Reads are public and use the product's existing synthetic/demo database.
Mutation routes are implemented only for selected integration-safe workflows.
They are disabled unless `FASTSME_API_TOKEN` is configured in the deployment.

When enabled, clients send:

```http
Authorization: Bearer <token>
```

No shared token is committed or configured by FastDevOps. Production token
creation, rotation, per-client token records, scopes, and audit trails are a
future security phase. Until that phase is authorised, production writes
return `503 writes_disabled`.

Browser CORS permits public read methods only. Server-side clients can use
token-authenticated writes after the deployment has explicitly enabled them.

## Compatibility conventions

- APIs are versioned under `/api/v1`.
- JSON is the request and response representation.
- Collection endpoints use `limit` and `offset`.
- SQLite-backed products derive response schemas from their real tables.
- Product storage abstractions remain authoritative where present.
- Product policies remain authoritative: for example, FastFunnel content
  writes enter its audited review workflow rather than directly publishing.
- OpenAPI operation IDs are stable and product resource names are plural.
- New breaking behavior requires a new URL version.

## Release gates

Before a fleet release:

1. Run `python skills/fastsme-landing/scripts/sync_fasthtml_landings.py --check`.
2. Run `python scripts/validate_fastapi_fleet.py`.
3. Run each repository's compile and test commands.
4. Confirm unauthenticated reads return real demo data.
5. Confirm writes return `503` while no token is configured.
6. Compare committed `swagger.json` with the runtime schema.
7. Check `/developers` at desktop and mobile widths.
8. Deploy repositories independently and verify the exact pushed commit.


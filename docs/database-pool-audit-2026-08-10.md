# Fast* database connection-pool audit — 2026-08-10

## Contract

The reference is `dev/plai/alpatrade/engine/db/pool.py`. A network database
runtime must have one thread-safe pool per process/database URL, bounded pool
and overflow sizes, checkout validation/pre-ping, a short checkout timeout,
connection recycling, an identifiable PostgreSQL `application_name`, and a
shutdown/reset disposal path. SQLite-only runtimes do not need a network
connection pool.

Fleet-safe defaults used by this change are 0–3 retained psycopg connections,
or a SQLAlchemy pool of 3 plus at most 2 temporary overflow connections, with a
10-second checkout timeout and 1,800-second recycle interval.

## Sweep result

| Repository | Database path | Result |
| --- | --- | --- |
| FastAccounts | PostgreSQL or SQLite | Added strict per-URL psycopg singleton, bounds, checkout validation, lifecycle disposal, tests |
| FastBI | SQLite / external connector catalogue | No PostgreSQL runtime pool |
| FastBooking | Dedicated PostgreSQL | Existing module singleton; added bounds, pre-ping, recycle, application name, lifespan disposal, tests |
| FastCMS | SQLite / file-backed | No PostgreSQL runtime pool |
| FastCRM | SQLite / file-backed | No PostgreSQL runtime pool |
| FastCal | PostgreSQL | Existing module singleton; bounded settings are already present in an active unrelated worktree change |
| FastCity | SQLite / file-backed | No PostgreSQL runtime pool |
| FastClinic | SQLite runtime | Dormant, unused SQLAlchemy helper is not installed or imported by the application; no PostgreSQL runtime pool |
| FastDataGov | Shared PostgreSQL | Replaced race-prone cached factory with strict singleton; added bounds, checkout validation, lifecycle disposal, tests |
| FastDevOps | Deployment control plane | No application database |
| FastDocs | SQLite / file-backed | No PostgreSQL runtime pool |
| FastDrive | SQLite / file-backed | No PostgreSQL runtime pool |
| FastERP | Shared PostgreSQL | Added per-settings class singleton, bounded validated pool, lifecycle disposal, tests |
| FastESM | SQLite / file-backed | No PostgreSQL runtime pool |
| FastFPA | SQLite / file-backed | No PostgreSQL runtime pool |
| FastFund | SQLite today; PostgreSQL-capable | Added one shared per-URL SQLAlchemy engine across tax, family-office, and text-to-SQL paths, bounds and disposal, tests |
| FastFunnel | PostgreSQL-capable or SQLite | Added strict per-URL psycopg singleton, bounds, checkout validation, lifecycle disposal, tests |
| FastGTM | SQLite / file-backed | No PostgreSQL runtime pool |
| FastGrants | SQLite / file-backed | No PostgreSQL runtime pool |
| FastHRM | SQLite runtime | PostgreSQL engine reference exists only under vendored reference documentation |
| FastHealthData | SQLite / file-backed | No PostgreSQL runtime pool |
| FastHelpdesk | SQLite / file-backed | No PostgreSQL runtime pool |
| FastInsure | SQLite / file-backed | No PostgreSQL runtime pool |
| FastLCA | SQLite / file-backed | No PostgreSQL runtime pool |
| FastLMS | Dedicated PostgreSQL | Replaced race-prone cached factory with strict per-URL singleton, bounds, pre-ping, lifecycle disposal, tests |
| FastMSR | SQLite / file-backed | No PostgreSQL runtime pool |
| FastMail | SQLite / file-backed | No PostgreSQL runtime pool |
| FastMeet | SQLite / file-backed | No PostgreSQL runtime pool |
| FastOffice | SQLite / file-backed | No PostgreSQL runtime pool |
| FastPE | PostgreSQL | Added strict psycopg singleton; removed the second retained SQLAlchemy pool by using an unpooled singleton facade; tests |
| FastPPM | SQLite today; PostgreSQL-capable | Added strict per-URL SQLAlchemy singleton, bounds, pre-ping, disposal, tests |
| FastSSO | SQLite / file-backed | No PostgreSQL runtime pool |
| FastSheets | SQLite / file-backed | No PostgreSQL runtime pool |
| FastSlides | SQLite / file-backed | No PostgreSQL runtime pool |
| FastSocial | Dedicated PostgreSQL | Replaced race-prone cached factory with strict per-URL singleton; added bounds, pre-ping, application name, lifecycle disposal, tests |
| FastSurvey | SQLite / file-backed | No PostgreSQL runtime pool |
| FastVC | Shared PostgreSQL | Added strict psycopg singleton; removed the second retained SQLAlchemy pool by using an unpooled singleton facade; tests |
| FastWiki | SQLite / file-backed | No PostgreSQL runtime pool |

## Production incident finding

`fastaccounts.org` is returning 503 because the shared PostgreSQL server at the
configured external host rejects new non-superuser sessions with all connection
slots exhausted. At audit time the Coolify host accounted for five established
sessions across FastERP, FastDataGov, and FastVC, so most exhaustion originates
outside this Coolify host. The pool changes reduce this fleet's retained demand,
but database-owner access is still required if external clients continue to
consume all slots.

## Deployment set

FastDevOps-managed services changed by this sweep: `fastaccounts`,
`fastbooking`, `fastdatagov`, `fasterp`, `fastfund`, `fastfunnel`, `fastlms`,
`fastppm`, `fastsocial`, and `fastvc`. FastPE has no FastDevOps service registration, so its
code can be published but cannot be deployed through this catalogue until an
application/domain mapping is added.

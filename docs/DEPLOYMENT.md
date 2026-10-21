# Deployment

## Live services

- Application: https://campus-find-g19.onrender.com
- Standalone page: https://campus-find-g19-project.onrender.com
- Source: private repository, main branch
- Render web service: srv-davk9lbncjis73en5us0, Docker Free, Singapore
- Render static site: srv-davkmvvavr4c73cds0eg, publish directory website
- Manual deployment only; auto-deploy is off

## Persistent inventory

The staff inventory uses Neon PostgreSQL in Singapore (Free plan), project
campus-find-g19. Items, compressed JPEG photos, account hashes, session hashes and
audit events are stored in SQL, independently of Render's filesystem.
Set Render DATABASE_URL to the Neon connection string, retaining TLS settings.
Never put it into render.yaml, Git, screenshots or the public project page.

Free Render local files are ephemeral. Staff writes are deliberately refused
when RENDER is set and the database is SQLite. SQLite remains supported locally
with its file on persistent storage. The old live SQLite catalogue contained only
the 30 fictional seed records; no staff records required transfer.

Database startup creates missing tables and upgrades the original items table
with place and created_at columns. Existing descriptions are preserved. Seeding
is recorded once in app_meta: collection does not cause seed records to reappear.
SEED_DEMO_DATA=false starts an empty database on first initialization; changing
it later does not add or delete records.

Photos accept JPEG/PNG/WebP up to 5 MB and 16 million pixels. They are re-encoded,
metadata is stripped, and the stored JPEG is limited to 400 KB. Free database
storage is finite; monitor Neon usage before adding large inventories. No paid
plan or additional storage subscription was selected.

Collection deletes the active item and its photo in one transaction, retaining
only item ID, action, staff account ID and time in an audit table. Provider
backups may still contain historical versions until their retention expires.
Configure appropriate backups and periodically test restoration before using
this course project as an operational service.

## Deployment procedure

1. Run tests with a dedicated TEST_DATABASE_URL for PostgreSQL integration.
2. Push to the personal private repository.
3. In Render, save DATABASE_URL as a secret environment variable.
4. Deploy the latest reviewed commit to the application and static site.
5. Verify student search and place filters.
6. Sign in as staff; add a clearly synthetic item/photo, verify it through a
   separate student session, reconnect/restart, and confirm collection.
7. Confirm the item and photo no longer appear and do not return after startup.

The static site serves website/index.html. All CSS and the running screenshot
are embedded; the file also works offline. The repository-link placeholder must
be replaced before assessment.

## Staff and optional AI/SSO

See STAFF_AND_SIGNIN.md for provisioning and the pending Microsoft registration.
There are no default committed passwords. Local generated staff credentials are
stored in ignored storage/staff-access.txt for the owner.

Qwen Flash is configured with the sponsored Bailian token-plan endpoint and server-side
LLM_API_KEY, LLM_BASE_URL, LLM_MODEL and LLM_PROVIDER settings. See QWEN_SETUP.md.
Thinking is disabled and JSON output is validated against SQL catalogue records.
Staff passwords and photos are never included in model requests. The 19 October
2026 synthetic evaluation is recorded in EVALUATION.md; it is a development set.

## Local containers

`docker compose up --build -d` uses SQLite on a named volume.
For PostgreSQL, set POSTGRES_PASSWORD in ignored .env, then run:
`docker compose -f compose.postgres.yaml up --build -d`.

The local Docker daemon was unavailable during initial verification; CI and
Render validate container builds. Never run integration tests against the live
inventory. Use a dedicated test database.

## Verified release, 19 October 2026

Application commit: `d1d1e62`. The navigation contains Search, Catalogue and Staff.
GitHub Actions run 39200828663 passed the Python/PostgreSQL suite and Docker build.
Render deployment `dep-dbapvt49v7es739g5m40` succeeded in 46.9 seconds.

A live Qwen search returned LF-001 with source-verified evidence.
PostgreSQL persistence and collection removal were verified during the inventory
release; ongoing evaluation and backup restoration checks are described in
EVALUATION.md. No test suite should target the live database.

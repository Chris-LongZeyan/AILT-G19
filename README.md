# Campus Find

**Live demo:** https://campus-find-g19.onrender.com

**Private source:** https://github.com/Chris-LongZeyan/AILT-G19

A browser-based lost-and-found matching demonstration for AILT9019 Group 19.
Describe a fictional item, search a real SQL catalogue, and inspect up to three
possible matches with their original descriptions.

The green-and-white UI draws its accent colour (#8EC63F) from the
[public HKU Portal](https://hkuportal.hku.hk/) inspected on 2 October 2026.
This is an independent course project, not an official university service.

## Run on Windows

Requires Python 3.13. From PowerShell:

```powershell
cd D:\GitHub_Repositories\AILT-G19
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1
```

Open http://localhost:8501. If that port is occupied, append
`--server.port=18501` and open http://localhost:18501.
On this development machine the preview uses port **18501**.

Alternatively run `powershell -ExecutionPolicy Bypass -File scripts/run.ps1`.
This bypass applies only to that invocation and does not change system policy.
The launcher installs dependencies when creating a new virtual environment.

## Run on macOS or Linux

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1
```

## First search

Choose **Keyword search**, enter **black insulated bottle with a silver lid**,
and click **Search items**. LF-001 should be the first possible match. Its original
description mentions a silver screw lid and a crescent sticker. Other baseline
results may conflict with the query: this mode only counts shared words.

Use **Browse catalogue** to inspect all 30 fictional records or filter by category.
Choose **AI matching** to see its configuration status. An absent key produces a
clear message, not fabricated AI results. Switching modes never silently performs
a fallback request.

## Database

SQLite is the default: `storage/items.db` is created and seeded automatically.
SQLAlchemy executes real SQL queries; JSON is only the versioned seed source.
The database has an `items` table with a primary-key ID, type, colour, JSON feature
list and original description. A type index supports category filtering.
No search-history or user-profile tables exist.

To use PostgreSQL, create a database and set `DATABASE_URL` in a local `.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
```

Percent-encode special characters in credentials. The provider's connection string
may use `postgres://` or `postgresql://`; the app normalises either to psycopg.
For a local Compose network, use its supplied connection URL without external TLS.

```powershell
.\.venv\Scripts\python.exe -m lostfound.database
```

Seeding inserts missing IDs without overwriting existing rows. Seed edits do not
overwrite records in an existing database. For an intentional dataset revision,
use a new database path or apply reviewed SQL updates and record the new hash.
Schema v1 is initialised with SQLAlchemy metadata; future schema changes require
explicit versioned migrations. See [architecture](docs/ARCHITECTURE.md).

## Add the LLM key later

Copy `.env.example` to `.env` and set:

```dotenv
LLM_API_KEY=your-server-side-key
LLM_BASE_URL=https://your-provider.example/v1
LLM_MODEL=your-provider-model-id
LLM_PROVIDER=your-provider-display-name
```

The example hostname is a placeholder. Select a provider supporting the
Chat Completions-compatible JSON protocol (`/chat/completions`,
`response_format: json_object`, `max_tokens`, and `temperature`).
The adapter is provider-neutral; support for a specific provider/model must be
verified with a real key. Native protocols that differ need another adapter.

Restart the app after configuration. The app never asks visitors for API keys.
On Render, set these as server environment variables. Do not put keys in code,
screenshots, browser forms inside this app, or Git. `.env` and Streamlit secrets
are ignored, but this implementation reads environment variables and `.env`,
not `.streamlit/secrets.toml`.

AI mode sends only the fictional query and the selected catalogue records.
The provider's retention policy applies. The app does not persist queries, though
Streamlit holds form values and the last result in the current browser session.
Close the session to discard them. The app does not add query logging.
Use synthetic input only; English boundary checks are safeguards, not a universal
personal-data detector.

A process-wide request cap defaults to 10 AI requests per minute; there is no
automatic retry. Set provider-side spending limits before sharing a keyed demo.
The cap resets on restart and is per process, not a distributed quota.

## Tests and evaluation

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m evaluation.run --mode keyword
```

If Windows denies access to its shared pytest temp folder:

```powershell
$env:TEMP = Join-Path (Get-Location) 'storage\test-temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP
.\.venv\Scripts\python.exe -m pytest -q
```

A PostgreSQL integration test runs when `TEST_DATABASE_URL` points to a dedicated
test database. Do not point it to production. The checked-in CI workflow starts
PostgreSQL and builds Docker on each push. The first CI run passed all 45 tests, including PostgreSQL,
and successfully built the Docker image.

After configuring the model:

```powershell
.\.venv\Scripts\python.exe -m evaluation.run --mode ai --output evaluation/results/ai.json
```

This makes billable model requests and paces them to the configured rate limit.
Reports include timestamp, provider/model, prompt hash and dataset hash.
The 20-query answer key is a draft pending independent team review. Do not tune
against the final set; use separate practice queries and record any changes.
See [evaluation status](docs/EVALUATION.md) for measured baseline results and
pending manual checks. Do not report mocked model tests as real AI accuracy.

## Deploy

- [Render Free instructions](docs/DEPLOYMENT.md): `render.yaml` selects a free web
  service with SQLite reconstructed from the fixed seed after restarts.
- Local Docker with persistent SQLite: `docker compose up --build -d`.
- Local Docker with PostgreSQL: add a long random **alphanumeric**
  `POSTGRES_PASSWORD` to `.env`, then
  `docker compose -f compose.postgres.yaml up --build -d`.

Docker Desktop/Engine must be running. Open http://localhost:8501.
Use `docker compose down` to stop; do not add `-v` unless you intend to delete data.
The local Compose services bind only to loopback and the database is not published.

## Scope and remaining team work

Implemented: UI, SQLite/PostgreSQL repository, seeded fictional catalogue, category
filter, keyword baseline, provider adapter, strict ID/evidence validation, defensive
error handling, evaluation runner, tests and deployment configuration.

Pending: real provider selection/key, live AI evaluation, human review of the
synthetic records and answer key, and two-classmate usability checks. PostgreSQL integration and Docker builds
passed in CI; the Render Free deployment is live.

Photos, OCR, accounts, item posting, real campus data and ownership decisions are
outside the proposal's scope. SQLite/PostgreSQL and deployment were added at the
team's explicit request. AI assistance was used for code, UI, synthetic records and
draft evaluation cases; team members must inspect and understand the deliverables.

Publication is authorised only to the new private repository Chris-LongZeyan/AILT-G19. The original team repository jason-0712/AILT-G19 is not modified.

The local remote named private points to your new repository and is the default
push destination. The original origin remote is preserved for team reference.

# Deployment

## Render Free with SQLite

This is the selected no-charge demo configuration. Free plans and quotas should be
confirmed in Render at deployment time. As checked on 2 October 2026, free web
services sleep after 15 minutes idle and lose local filesystem changes on restart.
The catalogue automatically rebuilds its 30 synthetic records. The app deliberately
does not accept item submissions or store searches.

Free Render PostgreSQL expires after 30 days, so it is not the default for this
semester-long demo. PostgreSQL remains supported through DATABASE_URL.
Source: https://render.com/docs/free

### Source requirement

Render builds from a connected Git repository or pulls a published container
image; it does not upload this local folder directly. The original team remote is
`git@github.com:jason-0712/AILT-G19.git`. The user authorised publishing to a new private repository: Chris-LongZeyan/AILT-G19. Use that repository for Render; keep the original team remote untouched.

The connected Render account has access to the newly created private repository
Chris-LongZeyan/AILT-G19. The original team repository was not modified.

### Verified deployment

- Live URL: https://campus-find-g19.onrender.com
- Render service: campus-find-g19, srv-davk9lbncjis73en5us0
- Deployed application commit: 072f3b0
- First deployment: 2 October 2026, about 13:46 Asia/Shanghai
- Plan: Free ($0 selected), Singapore, Docker, SQLite
- Auto-deploy: Off
- No LLM key or paid database configured
- CI: all 45 tests and Docker build passed

Future app changes require a manual deploy from Render after pushing reviewed
code. Documentation-only updates do not need redeploying the application.

### Service settings

| Setting | Value |
|---|---|
| Service type | Web Service |
| Name | campus-find-g19 |
| Runtime | Docker |
| Instance plan | Free |
| Region | Singapore, if available |
| Health check | /_stcore/health |
| Auto deploy | Off |
| DATABASE_URL | sqlite:///storage/items.db |
| LLM_REQUESTS_PER_MINUTE | 10 |

`render.yaml` encodes these settings for the Blueprint flow.
Do not select a paid database, disk or service. Review any billing screen rather
than accepting an upgrade. Do not add payment information just for this demo.

The Docker entrypoint reads Render's PORT variable and binds to 0.0.0.0.
Do not disable CORS or XSRF protections. Render terminates HTTPS and supports the
WebSocket connection Streamlit needs.

### After deployment

1. Wait for the successful build and healthy service.
2. Open its generated HTTPS address.
3. Confirm 30 fictional records appear in Browse catalogue.
4. Search the supplied black-bottle query in Keyword mode and verify LF-001.
5. Verify AI mode explains the missing key, without fabricated matches.
6. Try a blank query and an ownership request.
7. Restart the service and repeat the catalogue and query checks.

A green deployment health check alone is not proof that the application works.
Record the actual URL and deployment date after these checks pass.

## LLM activation

Add LLM_API_KEY, LLM_BASE_URL, LLM_MODEL and LLM_PROVIDER in Render's environment
settings after the team selects a compatible provider. Leave them absent until
then. Restart and perform one synthetic query, then run the evaluation from a
controlled local environment. Provider charges are separate from free hosting.
Review retention and set a provider spending limit.

## Local Docker

Start Docker Desktop, then:

```powershell
docker compose up --build -d
docker compose logs --tail 50 app
```

For PostgreSQL, set POSTGRES_PASSWORD to a long random alphanumeric string in
the ignored .env file, then:

```powershell
docker compose -f compose.postgres.yaml up --build -d
```

Using alphanumeric passwords here avoids URL-interpolation ambiguity in Compose;
external connection strings must percent-encode any special characters.

Both variants expose only http://localhost:8501. Compose named volumes preserve
the database. Stop using the same compose file with `down`, without `-v`.
Take database backups before deleting volumes or applying schema changes.

Docker builds passed in GitHub CI and Render. The local Docker daemon did not
respond during verification, so local Compose startup remains unverified. The
PostgreSQL adapter passed its integration test in GitHub CI.

## Alternative PostgreSQL host

Set DATABASE_URL to a managed PostgreSQL connection string and follow its TLS
instructions, normally sslmode=require. There is no requirement to open a paid
account for local SQLite. To test the PostgreSQL adapter, run pytest with
TEST_DATABASE_URL pointing to a separate test database. Never expose a database
password in frontend code or commit it.

## Standalone project overview

A separate Render Static Site serves `website/index.html`:
`https://campus-find-g19-project.onrender.com`.

Use the same private source repository and main branch. Set the publish directory
to `website`, leave the build command empty, and turn auto-deploy off. This is
a static site, not another paid web-service instance. The self-contained HTML
also works when opened directly from disk. Update the placeholder repository
link before assessment; the private source repository remains unchanged in
visibility.

The Streamlit About tab links to this distinct project page. Static HTML is
hosted separately because Streamlit's built-in static serving sends HTML as
plain text rather than rendering it.

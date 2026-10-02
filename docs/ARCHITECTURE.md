# Architecture

Streamlit provides public Search/Catalogue tabs and an authenticated Staff tab.
Python service functions enforce staff authorization on every mutation;
hiding UI controls is not the authorization boundary.

SQLAlchemy targets SQLite locally or PostgreSQL for durable hosting.
Tables: items, item_photos, accounts, staff_sessions, inventory_audit, app_meta.
The original schema is migrated in place. The one-time seed marker prevents
deleted demonstration items from being recreated at startup.

Students submit description + optional category/place. The application queries
available items, runs keyword/AI matching and validates model output against
those records. Place names and abbreviations are searchable text. Exact filters
are applied before matching. Result display rechecks current availability.
An already open screen is a snapshot; refresh/search again to see changes.

Staff sign in using a separate app password (PBKDF2 hash) or an approved
Microsoft OIDC identity when configured. A random session token is kept only
in server-side Streamlit session state; only its hash and expiry are in SQL.
Roles are provisioned administratively. Mutations and audit queries fail closed
for missing, expired, disabled or non-staff sessions.

Record creation validates text/place/photo and commits the item, optional photo
and audit event atomically. Images are decoded, resized and re-encoded as JPEG.
Collection requires an explicit UI confirmation, deletes the active record and
photo atomically, and retains only a minimal audit entry. Concurrent/double
collection fails without a second audit event.

The app uses UUID-derived identifiers that fit the legacy item ID column.
Parameterized SQL is used throughout. Item text is escaped before HTML display.
Student users cannot upload files or supply SQL/roles. No passwords or photos
are sent to the LLM.

Limitations: Streamlit browser sessions are not a full enterprise access
management system; OIDC needs HKU approval and live validation. The dataset and
retrieval evaluation are small, and human collection verification stays outside
the app. Free service quotas and backup retention must be monitored.

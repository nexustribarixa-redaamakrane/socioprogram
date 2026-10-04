# Socioprogram

Socioprogram is a server-rendered Flask application for developer posts,
comments, user profiles, and moderation. The application factory is
`create_app()` in `app.py`; the data models are SQLAlchemy models in
`models/`, and the route groups are Flask blueprints in `routes/`.

## Implemented application areas

- Local accounts with password login, registration, TOTP two-factor
  authentication/recovery codes, and optional Google, GitHub, and Reddit OAuth
  when credentials are configured.
- Project, snippet, discussion, showcase, and other post records, with tags,
  comments, stars, bookmarks, reposts, and user follows.
- Profile editing, notifications, live search, reports, moderation rules,
  bans, and moderator/admin routes.
- Image uploads are restricted to PNG/JPEG/GIF/WebP and capped at 5 MiB by
  `config.py`. Post HTML is cleaned with an allowlist in `routes/posts.py`.
- The default feed query orders stored posts by pin status and then
  `created_at`; it does not rank by engagement.

The feed route queries local database records. `services/aggregator.py`
contains helper functions for public Reddit and GitHub feeds, but the default
feed route does not call those functions or automatically import their
results.

## Run locally

Requirements: Python 3 and pip. Dependency versions are pinned in
`requirements.txt`; the repository does not declare a Python minimum version.
SQLite is the configured database.

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Set a private random `SECRET_KEY` in `.env` before using real accounts. The
code contains a development fallback value and must not rely on it in a
deployment. OAuth client IDs/secrets are optional; the corresponding buttons
are enabled only when configured. With the example environment file, the
application listens on `127.0.0.1:5000`.

For a WSGI server, `wsgi.py` exports `application`. `app.py` also starts
Waitress when run directly and the dependency is installed.

## Database and deployment status

The app creates missing tables with `db.create_all()` and has a small SQLite
column-addition helper in `migrate_db()`. There is no Alembic migration
history. The first registered user is assigned the `admin` role.

There is no application test suite in the repository. The current
`.github/workflows/lint.yml` and `deploy.yml` run Node/npm commands and
reference `package.json`/`dist`; this Flask checkout has no Node package
manifest. Those workflows do not lint or deploy the Python WSGI application.
Treat deployment as unconfigured until a Python-capable host workflow is
provided.

## Source layout

- `app.py`, `config.py`, `wsgi.py` — Flask factory, settings, and WSGI entry.
- `models/` — users/OAuth links, posts/tags, comments, social relations,
  notifications, reports, moderation records, and SQLAlchemy setup.
- `routes/` — page and JSON endpoints grouped by feature.
- `services/` — authentication helpers and external-feed fetch functions.
- `templates/`, `static/` — server-rendered pages and static assets/uploads.
- `requirements.txt`, `.env.example` — pinned dependencies and environment
  variable names.

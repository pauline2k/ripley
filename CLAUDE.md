# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Ripley Is

Ripley is a Flask + Vue 3 application that supports UC Berkeley's Canvas LMS instance. It provisions course sites, manages enrollments, handles mailing lists, and provides grade export/roster tools for instructors. It integrates with Canvas API, CalNet (UC Berkeley LDAP directory), a read-only institutional data warehouse called Data Loch, Redis/RQ for background jobs, AWS S3, and Mailgun for email.

## Commands

### Python tests and linting

```bash
# Run all tests and linters in parallel (recommended before committing)
tox -p

# Run the full test suite
tox -e test

# Run a single test file
tox -e test -- tests/test_api/test_canvas_site_controller.py

# Run a single test function
pytest tests/test_api/test_canvas_site_controller.py::test_function_name

# Python linting
tox -e lint-py

# Lint specific files (useful for scripts/)
tox -e lint-py -- scripts/my_script.py
```

### Frontend

```bash
npm run lint-vue          # Lint Vue/TypeScript
npm run lint-vue-fix      # Auto-fix linting errors
npm run build-vue         # Production build (output: dist/)
npm run serve-vue         # Dev server
```

### Database

```bash
export FLASK_APP=application.py
flask initdb              # Initialize/reset the schema
```

### Background worker

```bash
python scripts/start_rq_worker.py
```

## Architecture

### Backend layers

- **`ripley/api/`** — Flask REST controllers (`*_controller.py`). Each controller file handles one domain (auth, canvas site, mailing lists, jobs, etc.). `util.py` holds shared helpers; `errors.py` + `error_handlers.py` define the error model.
- **`ripley/models/`** — SQLAlchemy 2.x ORM models for the `nostromo` PostgreSQL database (users, jobs, job history, mailing lists, Canvas sync state). `development_db.py` handles schema initialization.
- **`ripley/externals/`** — Thin adapters over external services: `canvas.py` (canvasapi wrapper), `data_loch.py` (read-only warehouse queries), `calnet.py` (LDAP), `mailgun.py`, `b_connected.py` (SMTP), `s3.py`, `redis.py`.
- **`ripley/lib/`** — Business logic shared across API and jobs: course/term utilities, Canvas provisioning helpers, mailing list logic, grade export.
- **`ripley/jobs/`** — RQ background workers. Each `*_job.py` extends `base_job.py`. `background_job_manager.py` schedules and runs them. Jobs cover enrollment sync, course provisioning, mailing list updates, etc.
- **`ripley/factory.py`** — App factory: creates the Flask app, initializes SQLAlchemy, Redis, and the RQ queue.
- **`ripley/routes.py`** — Registers all blueprints, error handlers, and CAS/LTI auth setup.

### Frontend layers

- **`src/views/`** — Page-level Vue 3 components (one per feature: course site creation, roster, grade export, mailing lists, admin screens).
- **`src/components/`** — Reusable components shared across views.
- **`src/stores/`** — Pinia stores for shared state.
- **`src/api/`** — TypeScript API client functions that call the Flask REST endpoints.
- **`src/router.ts`** — Vue Router configuration.

### Configuration

- **`config/default.py`** — All config keys with defaults. Every environment inherits from this.
- **`config/development.py`** / **`config/test.py`** — Environment-specific overrides.
- Tests use `nostromo_test` (app DB) and `ripley_loch_test` (Data Loch), a fake Redis (fakeredis), and Moto for AWS mocking. Real external HTTP calls are blocked via `requests-mock` in `tests/conftest.py`.

### Auth

The app supports three auth mechanisms: CAS (standard web login), LTI 1.3 (launched from within Canvas), and a local dev/test bypass. `flask-login` manages sessions. LTI config uses `config/lti_rsa.pub`.

### Databases

- **`nostromo`** — Primary application PostgreSQL database (owner role: `ripley`).
- **Data Loch** — Separate read-only PostgreSQL data warehouse accessed via `ripley/externals/data_loch.py`. Contains institutional enrollment, CalNet, and term data.

## Python style

Ruff is configured in `ruff.toml` targeting Python 3.11 with line length 150. Run `tox -e lint-py` before committing Python changes.

# Track: Web Backend

**Stack:** FastAPI · Pydantic · SQLAlchemy 2.x · Alembic · PostgreSQL · pytest + httpx · Docker
**Alternative:** if you prefer a batteries-included framework, use Django and Django REST Framework for milestones 2–6.

## Milestone 1: HTTP & the web, from first principles
- **Learn:** HTTP methods, status codes, headers, JSON, REST conventions. Use `http.server` from the stdlib.
- **Build:** a key-value store over HTTP with **only the standard library** (`GET/PUT/DELETE /keys/{k}`).
- **Done when:** you can drive it with `curl`, it returns correct status codes (200/201/204/404/405), and you can explain what a framework would do for you.

## Milestone 2: First FastAPI app
- **Learn:** path and query params, request bodies with Pydantic models, response models, dependency injection, automatic OpenAPI docs. ([docs](https://fastapi.tiangolo.com/tutorial/))
- **Build:** a CRUD "Notes" API stored in memory.
- **Done when:** `/docs` lists every endpoint, invalid input returns 422, and there are `pytest` tests using `TestClient` for each endpoint.

## Milestone 3: Databases
- **Learn:** SQL basics (SELECT/JOIN/GROUP BY/indexes), SQLAlchemy 2.x ORM (`Mapped`, `select()`), sessions, transactions, Alembic migrations.
- **Build:** move Notes into SQLite, then PostgreSQL (run it in Docker). Add users and tags (many-to-many).
- **Done when:** the schema is created through Alembic migrations, tests use an isolated test database, and you've avoided N+1 queries (check with SQL echo).

## Milestone 4: Auth & security
- **Learn:** password hashing (argon2/bcrypt), JWT versus session cookies, OAuth2 password flow, CORS, the OWASP Top 10.
- **Build:** registration and login, with each user seeing only their own notes.
- **Done when:** a test proves that user A cannot read user B's note (expect 404/403), no plaintext passwords are stored anywhere, and secrets come from environment variables.

## Milestone 5: Production concerns
- **Learn:** async endpoints and when they help, background tasks, pagination, rate limiting, structured logging, settings with `pydantic-settings`, health checks.
- **Build:** add pagination, filtering, a `/health` endpoint, and JSON logs with request IDs.
- **Done when:** a load test (`locust` or `hey`) runs without errors, and you can name your slowest endpoint and explain why it's slow.

## Milestone 6: Ship it
- **Learn:** Dockerfiles (multi-stage, non-root), docker compose, CI (GitHub Actions), deploying to a PaaS (Fly.io, Render or Railway).
- **Done when:** a public URL serves your API, CI runs lint, type checks and tests on every push, and a merge to main deploys automatically.

## Capstone
A complete API for a domain you care about, such as a habit tracker, a book club or an expense splitter: auth, at least 3 related resources, migrations, a test suite with 85% or more coverage, Docker, CI/CD, deployed, and a README with an architecture diagram.

## Key reading
- FastAPI docs (tutorial and advanced guide)
- *Architecture Patterns with Python* (Percival & Gregory), free at cosmicpython.com
- SQLAlchemy 2.0 Unified Tutorial

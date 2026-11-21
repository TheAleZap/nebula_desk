# Decision records

Format: **Context · Decision · Alternatives · Consequences.**

---

## ADR-1 — Two services: Conversation API and Intelligence API
*Author: Viktoriia Stepanenko*

**Context.** The assignment requires exactly two services, each with its own container and database, talking over HTTP. Nebula Desk has two very different kinds of work: managing the inbox (contacts, conversations, messages, agents) and analysing messages with AI.

**Decision.** Split along that line. The **Conversation API** (FastAPI) owns all inbox data and full CRUD. The **Intelligence API** (FastAPI) classifies messages (intent, sentiment, priority), suggests replies and stores the analyses. The one cross-service call is server-side: `POST /conversations/{id}/analyze` on the Conversation API calls `POST /analyze` on the Intelligence API with a 3-second timeout. The UI (React, static) calls both services from the browser. Inside each service we use a simple layered structure: routes → (pure logic modules) → SQLAlchemy models. **Language and framework:** Python 3.12 with FastAPI in both services: request validation with Pydantic, and the OpenAPI docs at /docs come for free. **Frontend:** React 18 built with Vite into static files on Azure Static Web Apps; the two service URLs are read from a config.js that the pipeline writes at deploy time, so the same build runs locally and on Azure.

**Alternatives.** (a) Split by entity (contacts service vs conversations service): many cross-service joins, no clear benefit. (b) Let the UI call the Intelligence API and save results itself: no server-side flow, and the UI would hold business logic.

**Consequences.** The AI part has different failure and cost characteristics (external LLM, rate limits), so isolating it means the inbox keeps working when AI is down: the analyze flow returns a clear 503 message after the timeout. The price is one network hop and no transaction across the seam.

---

## ADR-2 — Storage: one serverless Azure SQL database per service, Alembic migrations
*Author: Viktoriia Stepanenko*

**Context.** Each service needs its own database (SQL Server: Azure SQL serverless in Azure, a SQL Server container locally) and a schema defined by versioned migrations applied at start-up.

**Decision.** SQLAlchemy 2 with the `pymssql` driver; schema defined by **Alembic** migrations in `services/<name>/migrations/versions/`, applied automatically at start-up and recorded in `schema_migrations`, so each runs once. Migration `0002` adds the AI labels to `conversations` without losing rows (column defaults backfill existing data). **Data model** (diagram in `docs/data-model.md`): contacts, conversations (with status, assigned agent and the AI labels), messages and seeded agents in the Conversation database; analyses in the Intelligence database. There is **no foreign key across the seam**: `analyses.message_id` is a plain integer. Each service connects with its own contained database user that can only reach its own database.

**Alternatives.** Hand-written numbered SQL files with our own runner (more code to own and test); recreating tables on start-up (loses data, not allowed).

**Consequences.** Migrations are portable Python, so tests run them on SQLite and CI runs them again on real SQL Server via `docker compose`. Forward-only: a bad migration is fixed with a new migration; recovery from a broken one uses Azure SQL point-in-time restore.

---

## ADR-3 — Deployment and pipeline: Container Apps, GHCR, OIDC, Static Web Apps
*Author: Alejandro Zapata*

_To be written by Alejandro._

---

## ADR-4 — The AI feature: rules first, optional LLM, cache and rate limit
*Author: Alex Garcia*

_To be written by Alex._

---

## ADR-5 — Monitoring: one JSON log line per request, Log Analytics workbook, one SLO
*Author: Kohana Rakipi*

_To be written by Kohana._

---

## ADR-6 — Scope and team workflow
*Author: Alesia Dako*

_To be written by Alesia._

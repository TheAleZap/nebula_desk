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

**Context.** The stack is fixed (containers, Azure SQL serverless, GitHub Actions, GHCR, Container Apps, Static Web Apps) in the group's resource group `rg-sdd-3a-g6`, with nothing changed manually after the initial setup.

**Decision.** `infra/setup.sh` (Azure CLI, run once) creates the SQL server and two serverless databases (15-min auto-pause, 2 GB), the Container Apps environment, two Container Apps (min 0, max 1 replica) and the Static Web App, and registers GitHub's OIDC token on the identity `sdd-3a-g6-github`. **CI** (every PR and branch push): lint, format check, tests with >=70% coverage per service, UI build, image builds, and the full compose stack on SQL Server including a cross-service and a partial-failure check. **CD** (merge to `main`): runs CI, pushes images tagged with the commit SHA to GHCR, updates both Container Apps, waits until `/health` returns 200 **with that SHA** (up to ~10 min to allow for database resume), builds the UI with a generated `config.js` holding the service URLs, deploys it to the Static Web App, and smoke-tests the live URL.

**Alternatives.** Bicep/Terraform IaC (credited, but slower for us to learn this week); Azure Container Registry (fixed monthly cost); a service-principal secret (an Azure password stored in GitHub, which OIDC avoids).

**Consequences.** No Azure password exists anywhere. Scale-to-zero means the first request after idle can take ~1 minute (cold start + database resume); the UI retries and shows a "starting up" message. Migrations run at start-up with max 1 replica, so they never run twice in parallel. Giving the identity its Contributor role needs a subscription owner, so our first deploy waited on that permission; everything that did not need Azure went ahead in the meantime.

---

## ADR-4 — The AI feature: rules first, optional LLM, cache and rate limit
*Author: Alex Garcia*

**Context.** The feature beyond CRUD is classifying messages and suggesting replies. An LLM costs money, needs a secret, and can be slow or down.

**Decision.** The core is a **deterministic rule-based classifier** (keywords for intent, word lists for sentiment, rules for priority, templates for replies). An **optional LLM** (OpenAI-compatible API) only rewrites the suggested reply, and only if `LLM_API_KEY` is configured. Cost is kept low with three controls: results are **cached** in the database by a hash of the text, calls are **rate-limited** (10/minute), and each call has a **4-second timeout**. Any LLM failure falls back to the rule-based reply.

**Alternatives.** LLM for everything (cost, non-deterministic tests, single point of failure); a trained ML model (no time, no data).

**Consequences.** The feature works with no key and no cost, tests are deterministic, and there are two levels of degradation: LLM down → rule-based reply; Intelligence API down → the inbox keeps working with an "analysis unavailable" message.

---

## ADR-5 — Monitoring: one JSON log line per request, Log Analytics workbook, one SLO
*Author: Kohana Rakipi*

_To be written by Kohana._

---

## ADR-6 — Scope and team workflow
*Author: Alesia Dako*

_To be written by Alesia._

# AI usage

One row per significant AI-assisted piece of work (code, workflows, Dockerfiles, IaC, docs).
Add your row **in the same pull request** as the work.

| Date | Who | Tool | What it produced | Used as-is / Modified / Rejected | What changed (if modified) | In my own words, how this works |
|---|---|---|---|---|---|---|
| 2026-11-18 | Alesia Dako | Claude | Definition of Done and Sprint 0 document draft | Modified | Created the Definition of Done and Sprint 0 documents, then checked them against our team's project requirements and actual Sprint 0 outcomes. | The Definition of Done explains the conditions that must be met before a task is considered complete, including a reviewed PR, successful CI and deployment. The Sprint 0 document records what our team planned, completed and carried forward to the next sprint. |
| 2026-11-19 | Viktoriia Stepanenko | Claude | Conversation API skeleton (FastAPI app, DB retry, Alembic migration 0001, Dockerfile) | Used as-is | No code changes. I created the files from the team plan and ran the CI checks on my laptop with Python 3.12: ruff format and ruff check passed, and pytest passed 4 tests with 88% coverage. I created the virtual environment with python3.12 because my Mac's default python3 is 3.14. | When the service starts, it waits for the database and retries with growing pauses, because Azure SQL can be paused. Then it applies the Alembic migration that creates the tables and the 3 demo agents; it runs only once because applied migrations are saved in schema_migrations. GET /health answers 200 if the database responds and 503 if not, every request writes one JSON log line, and the Docker image runs as a non-root user. |

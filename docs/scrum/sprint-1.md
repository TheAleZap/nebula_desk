# Sprint 1 (11–18 Nov 2026)

**Product Owner:** Alex Garcia
**Scrum Master:** Alesia Dako
**Developers:** everyone

## Sprint Goal
Build the core backend services, database migrations, local Docker Compose stack, CI pipeline, and deploy the initial version of Nebula Desk to Azure.

## Items selected
- Definition of Done and Sprint 0/1 Scrum documentation
- `conversation-api` service with SQLAlchemy models, Alembic migrations, and tests
- `intelligence-api` service with rule-based classifier, caching, and tests
- Local `docker-compose.yml` stack with SQL Server 2022 and `db-init`
- GitHub Actions CI workflow (`ci.yml`)
- Azure one-time infrastructure setup (`infra/setup.sh`) and first CD deploy (`cd.yml`)

## Done
- Definition of Done (`docs/scrum/definition-of-done.md`) and Sprint 0 notes added
- `conversation-api` and `intelligence-api` implemented with Alembic `0001_init.py` migrations and pytest suites
- Local Docker Compose stack configured for SQL Server 2022, both APIs, and the UI
- CI workflow (`ci.yml`) configured for linting, formatting, coverage, Docker builds, and full compose stack verification
- Azure resource group, Container Apps, SQL Server databases, and Static Web App provisioned once Azure access arrived on 18 Nov

## Not done
- **First deploy to Azure (`cd.yml`)**: Azure subscription access only arrived on 18 Nov (the last day of Sprint 1), so the CD workflow and live Azure deployment are carried over as the first priority of Sprint 2.
- **React UI (`frontend`)**: Core inbox, conversation, and contacts screens rolled into early Sprint 2.

## Sprint Review feedback
- Core backend endpoints, migration setup, and local Compose environment work cleanly together.
- Priority for the start of Sprint 2 is finishing the React UI and completing the carried-over Azure CD deployment before adding extra features.

## Retrospective agreements
- Keep PRs small, focused, and strictly sequenced in the group chat so reviewers are never blocked.
- Verify CI checks and remove all template markers before requesting review.

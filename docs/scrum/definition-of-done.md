# Definition of Done

An item is **Done** only when **all** of these are true:

1. **Merged to `main` through a pull request** reviewed and approved by another team member (no direct pushes: `main` is protected).
2. **CI is green** on that pull request: lint, format check, tests with coverage ≥ 70%, UI build, image builds, compose stack on SQL Server.
3. **Deployed**: the CD run for the merge commit succeeded and `/health` on both services returns `200` with that commit's SHA.
4. **Acceptance criteria met** on the live URL (checked by the Product Owner of the sprint).
5. **Tests**: new behaviour has at least one automated test.
6. **No secrets** in the code, the history or the logs.
7. **Docs updated** when the change affects them (README, `docs/decisions.md`, `docs/data-model.md`, OpenAPI).
8. **AI use logged**: one row in `AI_USAGE.md` for any significant AI-assisted work in the change.
9. The GitHub Project card is moved to **Done**.

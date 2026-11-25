# Sprint 2 — 19 to 24 November 2026

**Product Owner:** Kohana Rakipi  ·  **Scrum Master:** Alex Garcia  ·  **Developers:** everyone

## Sprint Goal
First deploy to Azure by the pipeline (carried over from Sprint 1), then the MVP complete: inbox, AI classification and suggested replies, metrics, monitoring with an SLO, and full documentation.

## Items selected
- US-1 to US-6 (carried over from Sprint 1)
- US-7 to US-12

## Impediment: Azure permission for the pipeline (19 to 24 Nov)
The CD pipeline signs in to Azure as the identity `sdd-3a-g6-github`, which needs the Contributor role on `rg-sdd-3a-g6`. Our own role cannot grant roles, so we asked for it on 19 and 20 Nov; it was granted on 24 Nov. Until then we kept building, reviewing and approving everything that did not need Azure, and on purpose held the merges that did: the CD workflow (#24), migration 0002 (#25, which must run on a database that already holds data), and the two PRs that depend on it (#29, #31). On 24 Nov we merged them in that order and the first deploy ran.

## Done
Accepted by the Product Owner on the live URL (https://thankful-river-0e059a403.6.azurestaticapps.net):
- **US-1** Skeleton deployed by the pipeline: #16, #17, #18, #19, #20, #24 (first deploy 24 Nov)
- **US-2** Manage contacts: #21, #22
- **US-3** Inbox with filters and search: #21, #22
- **US-4** Read and reply to a conversation: #21, #22
- **US-5** Change status, assign and delete: #21, #22
- **US-6** Simulate incoming messages: #21, #22, #28, #42 (no copies of open conversations)
- **US-7** AI classification: #17, #25, #29 (migration 0002 evidence on Azure: #38)
- **US-8** AI suggested reply: #17, #25, #29
- **US-9** Support metrics page: #25, #29, #43 (conversations by priority, added on 25 Nov after the first acceptance check found it missing)
- **US-10** Partial failure handled: #25, #31
- **US-11** Monitoring dashboard and SLO: #30, #36, #37, #44
- **US-12** Documentation complete: #23, #26, #32, #33, #34, #35, #36, #38, #39, #40 and this file

## Not done
- None of the selected items.
- US-13 (knowledge base) and US-14 (automatic AI replies) stay in the Product Backlog: they were stretch goals and were not selected for this sprint.

## Sprint Review (25 Nov) — feedback
The review in class was cancelled; we held it as an internal team call on 25 Nov.

## Retrospective agreements
- **Raise blockers the day they appear.** Communicate blockers as soon as they arise, clearly explaining their impact on the sprint and what is needed from the team to resolve them, and keep working on independent tasks while waiting for external dependencies. (Trigger: the Azure role for the pipeline took from 19 to 24 Nov.)
- **Small, assigned tasks and a live board.** Break work down into smaller, clearly assigned tasks and keep the GitHub Project updated, so everyone knows what is being worked on, what is blocked and what is ready for review.
- **Check acceptance criteria on the deployed app before calling a story done.** Strengthen cross-review and acceptance testing before considering a user story complete: verify every acceptance criterion on the live application and address feedback before the final review. (Trigger: US-9 was missing "by priority" and was only caught at PO acceptance.)

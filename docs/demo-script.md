# Sprint Review demo script

Order of the live demo, so whoever presents can follow along and everyone knows the backup for each step.

Live URL: https://thankful-river-0e059a403.6.azurestaticapps.net

## 5 minutes before

1. Open the live URL and both `/health` links from the README so the containers and databases wake up. They scale to zero, so the first request can take about a minute.
2. Have the backup screenshots open in another tab.

## The demo

| # | On screen | What to say | Backup if it's slow |
|---|---|---|---|
| 1 | Inbox with the conversations, their priority and intent | This is the inbox. Messages from WhatsApp, chat and email all show up here, each with a priority and an intent. If it says unknown, we just haven't analyzed that one yet. | Screenshot of the inbox |
| 2 | Click "Simulate incoming message", a new conversation shows up | Let's pretend a customer writes in. I click Simulate and the new message appears at the top. If you get a note saying AI analysis is unavailable, that's okay, the message still comes in and we analyze it in the next step. | Screenshot after Simulate |
| 3 | Open it, click "Analyze & suggest reply" to get intent, sentiment, priority and a suggested reply | I open it and click Analyze. It works out the intent, sentiment and priority and writes a draft reply. Under the draft it says whether the reply came from the model or from our rules. | Screenshot of the AI panel |
| 4 | Click "Use suggestion", then "Send reply" | If the draft is fine, the agent clicks Use suggestion, edits it if needed and sends it. Nothing goes to the customer until someone clicks Send. | n/a |
| 5 | Metrics page | Last thing in the app is Metrics. At the top you see how many conversations are open, pending or resolved, and below that how many messages the AI analyzed and what it tagged them as. | Screenshot of Metrics |
| 6 | Partial failure, shown with the CI run of the reliability check (we never stop a service on Azure by hand) | We also check what happens when the AI service is down. We don't turn anything off on Azure for that. There's a reliability check in CI, and this is the run where it passed. | Screenshot of the green CI steps |

## After the demo

Alejandro merges the live-change PR and shows the CI and CD runs in the Actions tab. Kohana shows the dashboard and the SLO.

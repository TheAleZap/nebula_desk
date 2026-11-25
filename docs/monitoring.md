# Monitoring

Both services write **one JSON line per request** to stdout, for example:

```json
{"service": "conversation-api", "method": "GET", "path": "/conversations", "status": 200, "duration_ms": 41.3}
```

Container Apps forwards stdout to the Log Analytics workspace of the environment
`sdd-3a-g6-env`. Open it in the portal: resource group `rg-sdd-3a-g6` → the Log Analytics
workspace → **Logs**. Every query starts from the same base:

```kusto
let requests = ContainerAppConsoleLogs_CL
    | where ContainerAppName_s startswith "sdd-3a-g6-"
    | where Log_s startswith "{" and Log_s has "duration_ms"
    | extend r = parse_json(Log_s)
    | project TimeGenerated, service = tostring(r.service), method = tostring(r.method),
              path = tostring(r.path), status = toint(r.status), duration_ms = todouble(r.duration_ms);
```

## 1. Request count (per service, 5-minute bins)

```kusto
let requests = ContainerAppConsoleLogs_CL
    | where ContainerAppName_s startswith "sdd-3a-g6-"
    | where Log_s startswith "{" and Log_s has "duration_ms"
    | extend r = parse_json(Log_s)
    | project TimeGenerated, service = tostring(r.service), method = tostring(r.method),
              path = tostring(r.path), status = toint(r.status), duration_ms = todouble(r.duration_ms);
requests
| where TimeGenerated > ago(24h)
| summarize requests = count() by service, bin(TimeGenerated, 5m)
| render timechart
```

## 2. Error rate (% of responses with status ≥ 500)

```kusto
let requests = ContainerAppConsoleLogs_CL
    | where ContainerAppName_s startswith "sdd-3a-g6-"
    | where Log_s startswith "{" and Log_s has "duration_ms"
    | extend r = parse_json(Log_s)
    | project TimeGenerated, service = tostring(r.service), method = tostring(r.method),
              path = tostring(r.path), status = toint(r.status), duration_ms = todouble(r.duration_ms);
requests
| where TimeGenerated > ago(24h)
| summarize total = count(), errors = countif(status >= 500) by service, bin(TimeGenerated, 15m)
| extend error_rate_pct = round(100.0 * errors / total, 2)
| project TimeGenerated, service, error_rate_pct
| render timechart
```

## 3. Response time (p50 / p95 / p99, ms)

```kusto
let requests = ContainerAppConsoleLogs_CL
    | where ContainerAppName_s startswith "sdd-3a-g6-"
    | where Log_s startswith "{" and Log_s has "duration_ms"
    | extend r = parse_json(Log_s)
    | project TimeGenerated, service = tostring(r.service), method = tostring(r.method),
              path = tostring(r.path), status = toint(r.status), duration_ms = todouble(r.duration_ms);
requests
| where TimeGenerated > ago(24h)
| summarize percentiles(duration_ms, 50, 95, 99) by service, bin(TimeGenerated, 15m)
| render timechart
```

## 4. SLO

**Objective:** 99% of `GET /conversations` requests succeed (status < 500) **and** take under 500 ms, measured over 7 days.

```kusto
let requests = ContainerAppConsoleLogs_CL
    | where ContainerAppName_s startswith "sdd-3a-g6-"
    | where Log_s startswith "{" and Log_s has "duration_ms"
    | extend r = parse_json(Log_s)
    | project TimeGenerated, service = tostring(r.service), method = tostring(r.method),
              path = tostring(r.path), status = toint(r.status), duration_ms = todouble(r.duration_ms);
requests
| where TimeGenerated > ago(7d)
| where service == "conversation-api" and method == "GET" and path == "/conversations"
| summarize total = count(), good = countif(status < 500 and duration_ms < 500)
| extend sli_pct = round(100.0 * good / total, 2), slo_target_pct = 99.0
| extend slo_met = sli_pct >= slo_target_pct,
         failed_requests_allowed = round(total * (100 - slo_target_pct) / 100, 2),
         error_budget_left_pct = round(100.0 * (sli_pct - slo_target_pct) / (100 - slo_target_pct), 1)
```

**Why this SLO:** the inbox list is the page agents open all day; if it is slow or failing, nothing else matters.
**Limitation:** `duration_ms` is measured inside the service, so the time Azure spends starting a container from zero is not included.

## Dashboard

The four queries are saved as an **Azure Workbook** named `sdd-3a-g6 Nebula Desk monitoring`
in `rg-sdd-3a-g6`; its JSON is exported to `monitoring/workbook.json`.

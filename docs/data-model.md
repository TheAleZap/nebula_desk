# Data Model

Nebula Desk uses **two separate SQL Server databases**, one per service, with no cross-database foreign keys:

1. **Conversation API database** (`sdd-3a-g6-conversation-db`), owned by `services/conversation-api`
2. **Intelligence API database** (`sdd-3a-g6-intelligence-db`), owned by `services/intelligence-api`

Alembic migrations live under `migrations/versions/` in each service and run automatically, once, at start-up; applied migrations are recorded in each database's `schema_migrations` table. Applied migrations are never modified; schema changes require a new revision.

**The seam.** `analyses.message_id` in the Intelligence database is a plain integer that refers to `messages.id` in the Conversation database. Integrity across the seam is deliberately not enforced: an analysis is a cache entry, so losing the link loses nothing important.

---

## Conversation API (`services/conversation-api`)

Defined by `0001_init.py` (all tables) and `0002_ai_labels.py` (the three AI label columns on `conversations`):

```mermaid
erDiagram
    AGENTS {
        int id PK
        nvarchar name "max 100"
        varchar email "max 200"
    }

    CONTACTS {
        int id PK
        nvarchar name "max 100"
        varchar email "max 200"
        datetime created_at
    }

    CONVERSATIONS {
        int id PK
        int contact_id FK
        nvarchar subject "max 200"
        varchar channel "chat | email | whatsapp"
        varchar status "open | pending | resolved"
        int assigned_agent_id FK "nullable"
        datetime created_at
        datetime updated_at
        datetime first_response_at "nullable"
        varchar intent "added by 0002, default unknown"
        varchar sentiment "added by 0002, default neutral"
        varchar priority "added by 0002, default normal"
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        varchar sender "customer | agent"
        nvarchar body "max 4000"
        bit from_suggestion
        datetime created_at
    }

    CONTACTS ||--o{ CONVERSATIONS : "has"
    AGENTS |o--o{ CONVERSATIONS : "assigned to"
    CONVERSATIONS ||--o{ MESSAGES : "contains"
```

| Migration | Change |
|---|---|
| `0001_init` | Creates `agents`, `contacts`, `conversations` and `messages` |
| `0002_ai_labels` | Adds `intent`, `sentiment` and `priority` to `conversations`, each with a server default, so rows that already exist keep their data and get a value |

---

## Intelligence API (`services/intelligence-api`)

Defined by `0001_init.py`:

```mermaid
erDiagram
    ANALYSES {
        int id PK
        int message_id "plain ID of a Conversation API message (no FK)"
        varchar text_hash "SHA-256 of the text, cache key"
        varchar intent
        varchar sentiment
        varchar priority
        nvarchar suggested_reply "max 2000"
        varchar source "rules | llm"
        datetime created_at
    }
```

| Migration | Change |
|---|---|
| `0001_init` | Creates `analyses` with an index on `text_hash` |

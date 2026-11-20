# Data Model

Nebula Desk uses **two separate SQL Server databases**—one per service, with no cross-database foreign keys:

1. **Conversation API database** (`sdd-3a-g6-conversation-db`) — owned by `services/conversation-api`
2. **Intelligence API database** (`sdd-3a-g6-intelligence-db`) — owned by `services/intelligence-api`

Alembic migrations live under `migrations/versions/` in each service and run automatically on startup. Applied migrations are never modified; schema changes require a new revision.

---

## Conversation API (`services/conversation-api`)

Defined in `services/conversation-api/migrations/versions/0001_init.py`:

```mermaid
erDiagram
    AGENTS {
        int id PK
        nvarchar(100) name
        varchar(200) email
    }

    CONTACTS {
        int id PK
        nvarchar(100) name
        varchar(200) email
        datetime created_at
    }

    CONVERSATIONS {
        int id PK
        int contact_id FK
        nvarchar(200) subject
        varchar(20) channel
        varchar(20) status
        int assigned_agent_id FK "nullable"
        datetime created_at
        datetime updated_at
        datetime first_response_at "nullable"
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        varchar(20) sender
        nvarchar(4000) body
        bit from_suggestion
        datetime created_at
    }

    CONTACTS ||--o{ CONVERSATIONS : "has"
    AGENTS ||--o{ CONVERSATIONS : "assigned to"
    CONVERSATIONS ||--|{ MESSAGES : "contains"
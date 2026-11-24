"""Nebula Desk - Conversation API. Owns the inbox: contacts, conversations, messages, agents."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config
from app.db import db_is_healthy, run_migrations, wait_for_db
from app.logging_mw import configure_logging, log_requests
from app.routes import agents, contacts, conversations, metrics

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if config.RUN_MIGRATIONS:
        wait_for_db()
        run_migrations()
    yield


app = FastAPI(title="Nebula Desk - Conversation API", version=config.APP_VERSION, lifespan=lifespan)

# Added first = inner layer: logs every request. CORS is added last = outer layer.
app.middleware("http")(log_requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health", tags=["health"])
def health():
    if db_is_healthy():
        return {"status": "ok", "db": "ok", "version": config.APP_VERSION}
    return JSONResponse(
        status_code=503, content={"status": "error", "db": "down", "version": config.APP_VERSION}
    )


app.include_router(contacts.router)
app.include_router(conversations.router)
app.include_router(agents.router)
app.include_router(metrics.router)

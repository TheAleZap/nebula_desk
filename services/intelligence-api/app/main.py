"""Nebula Desk - Intelligence API. Classifies messages and suggests replies."""

import hashlib
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import classifier, config, llm
from app.db import db_is_healthy, get_session, run_migrations, wait_for_db
from app.logging_mw import configure_logging, log_requests
from app.models import Analysis

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if config.RUN_MIGRATIONS:
        wait_for_db()
        run_migrations()
    yield


app = FastAPI(
    title="Nebula Desk - Intelligence API",
    version=config.APP_VERSION,
    lifespan=lifespan,
)
app.middleware("http")(log_requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class AnalyzeIn(BaseModel):
    message_id: int
    text: str = Field(min_length=1, max_length=5000)


class AnalysisOut(BaseModel):
    message_id: int
    intent: str
    sentiment: str
    priority: str
    suggested_reply: str
    source: str
    cached: bool


def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


@app.get("/health", tags=["health"])
def health():
    if db_is_healthy():
        return {"status": "ok", "db": "ok", "version": config.APP_VERSION}
    return JSONResponse(
        status_code=503,
        content={"status": "error", "db": "down", "version": config.APP_VERSION},
    )


@app.post("/analyze", response_model=AnalysisOut, tags=["analysis"])
def analyze(body: AnalyzeIn, session: Session = Depends(get_session)):
    text_hash = _hash(body.text)
    cached = session.scalars(
        select(Analysis).where(Analysis.text_hash == text_hash).order_by(Analysis.id.desc())
    ).first()
    if cached is not None:  # same text seen before: no new work, no LLM cost
        return {**_out(cached), "message_id": body.message_id, "cached": True}

    result = classifier.analyze(body.text)
    source = "rules"
    better = llm.rewrite_reply(body.text, result["intent"], result["suggested_reply"])
    if better:
        result["suggested_reply"], source = better, "llm"

    analysis = Analysis(message_id=body.message_id, text_hash=text_hash, source=source, **result)
    session.add(analysis)
    session.commit()
    return {**_out(analysis), "cached": False}


def _out(a: Analysis) -> dict:
    return {
        "message_id": a.message_id,
        "intent": a.intent,
        "sentiment": a.sentiment,
        "priority": a.priority,
        "suggested_reply": a.suggested_reply,
        "source": a.source,
    }


@app.get("/analyses", tags=["analysis"])
def recent_analyses(limit: int = 20, session: Session = Depends(get_session)):
    limit = max(1, min(limit, 100))
    rows = session.scalars(select(Analysis).order_by(Analysis.id.desc()).limit(limit)).all()
    return [{**_out(a), "id": a.id, "created_at": a.created_at} for a in rows]


@app.get("/stats", tags=["analysis"])
def stats(session: Session = Depends(get_session)):
    rows = session.execute(select(Analysis.intent, Analysis.sentiment, Analysis.source)).all()
    return {
        "total_analyses": len(rows),
        "by_intent": dict(Counter(r.intent for r in rows)),
        "by_sentiment": dict(Counter(r.sentiment for r in rows)),
        "by_source": dict(Counter(r.source for r in rows)),
        "llm_enabled": llm.is_enabled(),
    }

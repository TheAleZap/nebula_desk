"""One JSON log line per request on stdout: method, path, status, duration."""

import json
import logging
import sys
import time

from fastapi import Request

SERVICE = "intelligence-api"
logger = logging.getLogger("request")


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout, force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # keep log volume low


async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        logger.info(
            json.dumps(
                {
                    "service": SERVICE,
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                }
            )
        )

"""
backend/middleware/logging.py — Request-logging middleware

Tilføjer:
  - Correlation ID (X-Correlation-ID header, genereres hvis fraværende)
  - Struktureret log pr. request: metode, path, status, ms, bruger-ID
  - FASE 2: Videresend til Azure Application Insights via OpenTelemetry

Tilføj til main.py:
    from backend.middleware.logging import RequestLoggingMiddleware
    app.add_middleware(RequestLoggingMiddleware)
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sos.api")

# Paths der ikke logges (sundhedstjek, favicon, osv.)
_SILENT_PATHS = {"/health", "/favicon.ico", "/robots.txt"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Struktureret access-log + correlation ID for alle API-requests.

    Tilføjer headers til response:
      X-Correlation-ID  — unik request-ID (videresendes fra klient hvis til stede)
      X-Response-Time   — behandlingstid i ms
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ── Correlation ID ────────────────────────────────────────────────────
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        # Gør tilgængeligt i request state (brug i routers: request.state.correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        status_code = 500

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            logger.error(
                "Ubehandlet undtagelse",
                extra={
                    "correlation_id": correlation_id,
                    "method":         request.method,
                    "path":           request.url.path,
                    "error":          str(exc),
                },
                exc_info=True,
            )
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            path = request.url.path

            if path not in _SILENT_PATHS:
                # Hent bruger-ID fra request state (sættes af get_current_user dep)
                user_id = getattr(request.state, "user_id", None)

                log_method = logger.warning if status_code >= 400 else logger.info
                log_method(
                    "%s %s %d %sms",
                    request.method,
                    path,
                    status_code,
                    elapsed_ms,
                    extra={
                        "correlation_id": correlation_id,
                        "method":         request.method,
                        "path":           path,
                        "status":         status_code,
                        "ms":             elapsed_ms,
                        "user_id":        str(user_id) if user_id else None,
                        "query":          str(request.url.query) or None,
                    },
                )

        # ── Response headers ──────────────────────────────────────────────────
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Response-Time"]  = f"{elapsed_ms}ms"
        return response


def configure_logging(level: str = "INFO") -> None:
    """
    Konfigurér root logger.
    Kald fra main.py ved opstart:
        from backend.middleware.logging import configure_logging
        configure_logging(level=settings.LOG_LEVEL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Dæmp støjende tredjeparts-loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

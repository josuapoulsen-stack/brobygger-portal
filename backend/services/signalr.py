"""
backend/services/signalr.py — Azure SignalR real-time beskeder

Broadcaster events til forbundne klienter via SignalR REST API.
Frontend abonnerer med @microsoft/signalr npm-pakken.

Brug i routere:
    from ..services.signalr import broadcast_ny_besked, broadcast_ny_aftale
    await broadcast_ny_besked(thread_id, message_dict)

Dokumentation:
    https://learn.microsoft.com/azure/azure-signalr/signalr-reference-data-plane-rest-api
"""

import httpx
import hmac
import hashlib
import base64
import time
import logging
from typing import Any
from ..config import settings

log = logging.getLogger(__name__)

# ── SignalR REST API ───────────────────────────────────────────────────────────

def _parse_connection_string(conn_str: str) -> tuple[str, str]:
    """Udtræk endpoint og accessKey fra connection string."""
    parts = dict(p.split("=", 1) for p in conn_str.split(";") if "=" in p)
    endpoint  = parts.get("Endpoint", "").rstrip("/")
    access_key = parts.get("AccessKey", "")
    return endpoint, access_key


def _generate_jwt(endpoint: str, access_key: str, audience: str) -> str:
    """Generer simpelt JWT til SignalR REST API (HS256)."""
    now = int(time.time())
    header  = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=")
    payload = base64.urlsafe_b64encode(
        f'{{"aud":"{audience}","iat":{now},"exp":{now + 300}}}'.encode()
    ).rstrip(b"=")
    sig_input = header + b"." + payload
    sig = base64.urlsafe_b64encode(
        hmac.new(access_key.encode(), sig_input, hashlib.sha256).digest()
    ).rstrip(b"=")
    return f"{sig_input.decode()}.{sig.decode()}"


async def _broadcast(hub: str, method: str, args: list[Any]) -> None:
    """Send broadcast til alle klienter i en hub."""
    if not settings.SIGNALR_CONNECTION_STRING:
        log.debug("SignalR ikke konfigureret — springer %s over", method)
        return

    endpoint, access_key = _parse_connection_string(settings.SIGNALR_CONNECTION_STRING)
    url = f"{endpoint}/api/v1/hubs/{hub}"
    audience = url
    token = _generate_jwt(endpoint, access_key, audience)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json={"target": method, "arguments": args},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=5,
        )
    if resp.status_code not in (200, 202):
        log.warning("SignalR broadcast fejlede (%s): %s", method, resp.status_code)


async def _send_to_user(hub: str, user_id: str, method: str, args: list[Any]) -> None:
    """Send til én specifik bruger (via Entra ID oid)."""
    if not settings.SIGNALR_CONNECTION_STRING:
        return

    endpoint, access_key = _parse_connection_string(settings.SIGNALR_CONNECTION_STRING)
    url = f"{endpoint}/api/v1/hubs/{hub}/users/{user_id}"
    audience = f"{endpoint}/api/v1/hubs/{hub}"
    token = _generate_jwt(endpoint, access_key, audience)

    async with httpx.AsyncClient() as client:
        await client.post(
            url,
            json={"target": method, "arguments": args},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=5,
        )


# ── Events ────────────────────────────────────────────────────────────────────

HUB = "brobygger"

async def broadcast_ny_besked(thread_id: str, message: dict) -> None:
    """Broadcast ny besked til alle abonnenter på tråd-ID."""
    await _broadcast(HUB, "nyBesked", [thread_id, message])


async def broadcast_ny_aftale(brobygger_azure_oid: str, aftale: dict) -> None:
    """Send ny aftale-event direkte til én brobygger."""
    await _send_to_user(HUB, brobygger_azure_oid, "nyAftale", [aftale])


async def broadcast_notifikation(bruger_azure_oid: str, notif: dict) -> None:
    """Send in-app notifikation til én bruger."""
    await _send_to_user(HUB, bruger_azure_oid, "nyNotifikation", [notif])

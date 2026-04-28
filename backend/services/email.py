"""
backend/services/email.py — Email via Microsoft Graph (Exchange Online)

SoS bruger Microsoft 365 → vi sender email via Graph API med app-credentials.
Kræver: App Registration med Mail.Send-tilladelse i Entra ID.

Brug:
    await send_magic_link(to="maja@example.com", navn="Maja", link="https://...")
    await send_aftale_bekraeftelse(to="maja@example.com", aftale=aftale_obj)
"""

import httpx
import logging
from typing import Optional
from ..config import settings

log = logging.getLogger(__name__)

GRAPH_URL = "https://graph.microsoft.com/v1.0"
FROM_ADDRESS = "no-reply@socialsundhed.dk"   # Opret denne postkasse i M365

# ── Auth: hent Graph-token med client credentials ─────────────────────────────

async def _get_graph_token() -> str:
    """
    Hent access token til Microsoft Graph via client_credentials flow.

    Kræver:
    - AZURE_CLIENT_ID (app registration)
    - AZURE_TENANT_ID
    - AZURE_CLIENT_SECRET (tilføj til .env.example og Key Vault)
    - Graph API-tilladelse: Mail.Send (application permission)
    """
    url = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data={
            "grant_type":    "client_credentials",
            "client_id":     settings.AZURE_CLIENT_ID,
            "client_secret": settings.AZURE_CLIENT_SECRET,   # TODO: tilføj til config
            "scope":         "https://graph.microsoft.com/.default",
        })
        resp.raise_for_status()
        return resp.json()["access_token"]


async def _send_mail(to: str, subject: str, html_body: str) -> None:
    """Lavniveau: send én email via Graph API."""
    token = await _get_graph_token()
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"address": to}}],
        },
        "saveToSentItems": False,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/users/{FROM_ADDRESS}/sendMail",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code != 202:
            log.error("Email-fejl til %s: %s %s", to, resp.status_code, resp.text)
            resp.raise_for_status()
    log.info("Email sendt til %s: %s", to, subject)


# ── Høj-niveau email-funktioner ───────────────────────────────────────────────

async def send_magic_link(
    to: str,
    navn: str,
    link: str,
    besked: Optional[str] = None,
    expires_hours: int = 48,
) -> None:
    """Send invitation med magic link til ny brobygger."""
    personlig = f"<p><em>{besked}</em></p>" if besked else ""
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #4A7C59;">Invitation til SoS Brobygger Portal</h2>
      <p>Hej {navn},</p>
      <p>Du er inviteret som frivillig brobygger hos Støt op om en Mentalig Sundhed (SoS).</p>
      {personlig}
      <p>Klik på knappen nedenfor for at oprette din adgang:</p>
      <a href="{link}" style="
        display: inline-block;
        padding: 14px 28px;
        background: #4A7C59;
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-size: 16px;
        margin: 16px 0;
      ">Acceptér invitation</a>
      <p style="color: #666; font-size: 14px;">
        Linket er gyldigt i {expires_hours} timer.<br>
        Hvis du ikke har bedt om denne invitation, kan du se bort fra denne email.
      </p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
      <p style="color: #999; font-size: 12px;">
        Støt op om en Mentalig Sundhed · <a href="https://sos.dk">sos.dk</a>
      </p>
    </div>
    """
    await _send_mail(to, "Invitation til SoS Brobygger Portal", html)


async def send_aftale_bekraeftelse(
    to: str,
    navn: str,
    dato: str,
    sted: Optional[str],
    app_link: str,
) -> None:
    """Send bekræftelse på ny aftale til brobygger."""
    sted_linje = f"<p>📍 <strong>Sted:</strong> {sted}</p>" if sted else ""
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #4A7C59;">Ny aftale oprettet</h2>
      <p>Hej {navn},</p>
      <p>Der er oprettet en ny aftale til dig:</p>
      <div style="background: #F0F7F2; padding: 16px; border-radius: 8px; margin: 16px 0;">
        <p>📅 <strong>Tidspunkt:</strong> {dato}</p>
        {sted_linje}
      </div>
      <a href="{app_link}" style="
        display: inline-block; padding: 12px 24px;
        background: #4A7C59; color: white;
        text-decoration: none; border-radius: 8px;
      ">Se i appen</a>
    </div>
    """
    await _send_mail(to, f"Ny aftale: {dato}", html)


async def send_paamindelse(to: str, navn: str, dato: str, app_link: str) -> None:
    """Send påmindelse dagen før aftale."""
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #4A7C59;">Påmindelse: Aftale i morgen</h2>
      <p>Hej {navn},</p>
      <p>Husk din aftale i morgen: <strong>{dato}</strong></p>
      <a href="{app_link}" style="
        display: inline-block; padding: 12px 24px;
        background: #4A7C59; color: white;
        text-decoration: none; border-radius: 8px;
      ">Se detaljer</a>
    </div>
    """
    await _send_mail(to, "Påmindelse: Aftale i morgen", html)

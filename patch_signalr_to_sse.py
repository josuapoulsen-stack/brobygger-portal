import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ok, fail = [], []
def patch(path, old, new, label):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    if old in c:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c.replace(old, new, 1))
        ok.append(label)
    else:
        fail.append(label)

PLAN = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\IMPLEMENTERINGSPLAN.md'
ROAD = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\ROADMAP.md'
REQ  = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\backend\requirements.txt'

# 1) Hovedbeslutningen — sektion 3.2
patch(PLAN,
"""### 3.2 SignalR (realtids-beskeder)
- FASE 1 brugte `BroadcastChannel` (samme browser)
- FASE 2: Azure SignalR → beskeder synkroniseres på tværs af enheder i realtid
- Hent connection string fra Azure Portal → gem i Key Vault""",
"""### 3.2 Realtids-beskeder — SSE i egen backend (Azure SignalR UDGÅR)
**Beslutning (juni 2026):** Vi bruger **Server-Sent Events (SSE) i vores egen FastAPI-backend** i stedet for Azure SignalR.

- **Mønster:** beskeder gemmes i PostgreSQL (kilde) → SSE pusher "ny besked"-event til åbne klienter → klienten henter siden-sidst ved (gen)forbindelse. Afsendelse via almindelig autentificeret POST.
- **Web Push** (3.1) håndterer notifikationer når appen er lukket — SSE betyder kun noget mens appen er åben.
- **Begrundelse:** ved vores skala (~50 medarbejdere samtidigt, 50–500 beskeder/dag) giver SignalR ingen mærkbar UX-gevinst for slutbrugeren, men koster ~$580/år og tilføjer en ekstra komponent der behandler beskeddata. SSE er $0 oveni App Service, holder data i egen backend (GDPR-rent), er ren HTTPS, og browserens `EventSource` genforbinder automatisk.
- **Forbehold:** valider Entra ID-token ved forbindelse + autorisér hvilke tråde brugeren må følge; send keepalive ~hvert 30. sek. (Azure idle-timeout ~230 sek.); kører vi nogensinde på **flere App Service-instanser**, tilføj **Postgres `LISTEN/NOTIFY`** (eller Redis) som backplane.
- **Oprydning ved FASE 2-build:** fjern `azure-signalr` (requirements), `Microsoft.SignalRService/signalR` (`infra/main.bicep`) og `SIGNALR_CONNECTION_STRING` (`backend/config.py`).""",
"1: IMPLEMENTERINGSPLAN 3.2")

# 2) Free-tier-liste
patch(PLAN,
"- ✅ Azure SignalR Free tier (**gratis** op til 20 enheder)",
"- ~~Azure SignalR~~ → **udgår**: SSE i egen backend (se 3.2) — $0, ingen ekstra tjeneste",
"2: free-tier-note")

# 3) /beskeder-endpoint
patch(PLAN,
"- `/beskeder` — tråde + SignalR-broadcast",
"- `/beskeder` — tråde + SSE-broadcast (egen backend)",
"3: beskeder-endpoint")

# 4) Omkostningstabel
patch(PLAN,
"| SignalR Free tier | Gratis |",
"| Realtid (SSE i egen backend) | Gratis — SignalR udgår |",
"4: omkostningstabel")

# 5) Tidslinje
patch(PLAN,
"Uge 4–5   Push-notifikationer · SignalR realtid · Magic link emails",
"Uge 4–5   Push-notifikationer · SSE realtid (egen backend) · Magic link emails",
"5: tidslinje")

# 6) ROADMAP mock-beskeder
patch(ROAD,
"- [ ] **Mock-beskeder og notifikationer** — `SoS_NOTIFICATIONS`, `SoS_MESSAGES` er statiske; erstattes af WebSocket eller polling.",
"- [ ] **Mock-beskeder og notifikationer** — `SoS_NOTIFICATIONS`, `SoS_MESSAGES` er statiske; erstattes af **SSE i egen backend + DB-bakkede beskeder** (Azure SignalR udgår; se IMPLEMENTERINGSPLAN 3.2).",
"6: ROADMAP")

# 7) requirements.txt — markér azure-signalr som udgået
patch(REQ,
"""# ── Real-time (SignalR) ────────────────────────────────────────────────────────
azure-signalr==1.1.0""",
"""# ── Real-time ──────────────────────────────────────────────────────────────────
# UDGÅET: Azure SignalR erstattet af SSE i egen FastAPI-backend (se IMPLEMENTERINGSPLAN.md 3.2)
# azure-signalr==1.1.0
# SSE kræver ingen ekstra pakke (FastAPI StreamingResponse / sse-starlette hvis ønsket).""",
"7: requirements azure-signalr")

with open(PLAN, 'r', encoding='utf-8') as f:
    pass

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

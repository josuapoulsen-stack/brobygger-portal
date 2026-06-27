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

R = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal'
REQ  = R + r'\backend\requirements.txt'
PLAN = R + r'\IMPLEMENTERINGSPLAN.md'
CHK  = R + r'\SECURITY_CHECKLIST.md'

# 1) requirements: aiosmtplib udgår
patch(REQ,
"""# ── Email (magic links + notifikationer via Exchange Online) ─────────────────
aiosmtplib==3.0.1""",
"""# ── Email (magic links + notifikationer) ─────────────────────────────────────
# UDGÅET: vi sender via Microsoft Graph (Mail.Send) — se backend/services/email.py
# (genbruger Entra ID-app, ingen mailboks-password; Microsoft udfaser SMTP basic-auth).
# aiosmtplib==3.0.1""",
"1: requirements aiosmtplib")

# 2) plan 3.3: note om at SMTP udgår
patch(PLAN,
"""- Aftaleberkræftelse til borger (via koordinator)
- Kræver Graph API-tilladelse i Entra-app-registreringen""",
"""- Aftaleberkræftelse til borger (via koordinator)
- Kræver Graph API-tilladelse (`Mail.Send`) i Entra-app-registreringen
- **`aiosmtplib`/SMTP udgår:** vi sender via Graph (mere sikkert — ingen mailboks-password; Microsoft udfaser SMTP basic-auth). Allerede påbegyndt i `backend/services/email.py`.""",
"2: plan 3.3 SMTP-note")

# 3) plan 3.2: HTTP/2-note på forbehold
patch(PLAN,
"kører vi nogensinde på **flere App Service-instanser**, tilføj **Postgres `LISTEN/NOTIFY`** (eller Redis) som backplane.",
"kører vi nogensinde på **flere App Service-instanser**, tilføj **Postgres `LISTEN/NOTIFY`** (eller Redis) som backplane; aktivér **HTTP/2** på den host der serverer SSE (App Service-indstilling) — fjerner browserens \"6 forbindelser pr. host\"-grænse.",
"3: plan 3.2 HTTP/2-note")

# 4) checklist: Google Fonts self-hosted ✅
patch(CHK,
"- [x] SRI-hashes (`integrity=` sha384) på alle 3 CDN-scripts + `crossorigin=anonymous` — verificeret i preview",
"- [x] SRI-hashes (`integrity=` sha384) på alle 3 CDN-scripts + `crossorigin=anonymous` — verificeret i preview\n- [x] Self-hostede fonts — Google Fonts CDN fjernet (9 woff2 i `fonts/`); CSP strammet (Google-domæner ude). GDPR: ingen bruger-IP til Google (juni 2026)",
"4: checklist fonts")

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

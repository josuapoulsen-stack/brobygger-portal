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
PLAN = R + r'\IMPLEMENTERINGSPLAN.md'
CHK  = R + r'\SECURITY_CHECKLIST.md'

# 1) Teknisk tjekliste: udvid audit-rækken
patch(PLAN,
"| Audit-log verificeret (INSERT/UPDATE/DELETE logges) | ⬜ |",
"""| Audit-log: mutationer logges (INSERT/UPDATE/DELETE via DB-trigger) | ⬜ |
| Audit-log: følsomme LÆSNINGER + udtræk logges eksplicit i API'et (helbredsvisning, GDPR-indsigtsrapport, kreditor-eksport) — kun aktør/handling/mål-id/tid, ALDRIG indhold | ⬜ |
| audit_log er append-only (ingen UPDATE/DELETE — heller ikke for admin) | ⬜ |
| Retention-/sletningspolitik for audit_log (er selv persondata) defineret + i art. 30 | ⬜ |""",
"1: teknisk audit-rækker")

# 2) GDPR-tjekliste: per-person adgangshistorik
patch(PLAN,
"| Ret til indsigt-endpoint implementeret (`GET /mig/data`) | ⬜ |",
"""| Ret til indsigt-endpoint implementeret (`GET /mig/data`) | ⬜ |
| Per-person adgangshistorik ("hvem har set mine data") kan udtrækkes fra audit-loggen | ⬜ |""",
"2: GDPR adgangshistorik")

# 3) SECURITY_CHECKLIST: udvid audit-punktet
patch(CHK,
"- [ ] Audit-trail / logning af al adgang til Art. 9-helbredsdata",
"""- [ ] **Revisionsspor (server-side, append-only)** — den endelige version (prototypens `sos_audit_log` i localStorage er kun demo af intentionen):
  - [ ] Mutationer logges via DB-trigger (`audit_changes`, migration 003) på borger-tabeller
  - [ ] **Følsomme læsninger + udtræk logges eksplicit i API'et** (helbredsvisning, GDPR-indsigtsrapport, kreditor-eksport) — aktør + handling + mål-id + tid/IP, ALDRIG selve indholdet
  - [ ] `audit_log` gøres append-only (ingen UPDATE/DELETE — heller ikke admin)
  - [ ] Retention-/sletningspolitik for audit-loggen (den er også persondata) — med i art. 30
  - [ ] Per-person adgangshistorik i admin-UI ("hvem har set mine data")""",
"3: SECURITY_CHECKLIST audit")

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# 1) Mobil viewingHq default → org-bredt for admin/landssekretariat
sub('  const [viewingHq, setViewingHq] = useState("Aarhus");',
    '  const [viewingHq, setViewingHq] = useState(activeRole === "admin" || activeRole === "landssekretariat" ? "Alle hovedsæder" : "Aarhus");',
    "1: mobil default")

# 2) AdminSettings-kald: canAllHq
sub("""      content = <AdminSettings
        currentHq={viewingHq}
        ownHq="Aarhus"
        isAdmin={activeRole === "admin"}
        canRapport={_canRapport}""",
    """      content = <AdminSettings
        currentHq={viewingHq}
        ownHq="Aarhus"
        isAdmin={activeRole === "admin"}
        canRapport={_canRapport}
        canAllHq={activeRole === "admin" || activeRole === "landssekretariat"}""",
    "2: AdminSettings-kald")

# 3) AdminMobile-kald: canAllHq
sub("""      content = <AdminMobile
        user={user}
        viewingHq={viewingHq}
        ownHq="Aarhus"
        isAdmin={activeRole === "admin"}""",
    """      content = <AdminMobile
        user={user}
        viewingHq={viewingHq}
        ownHq="Aarhus"
        isAdmin={activeRole === "admin"}
        canAllHq={activeRole === "admin" || activeRole === "landssekretariat"}""",
    "3: AdminMobile-kald")

# 4) AdminMobile-signatur
sub("const AdminMobile = ({ user, viewingHq, ownHq, isAdmin, onOpenSettings, onOpenIntake, onOpenMatching, onOpenMessages, onOpenDesktop }) => {",
    "const AdminMobile = ({ user, viewingHq, ownHq, isAdmin, canAllHq = false, onOpenSettings, onOpenIntake, onOpenMatching, onOpenMessages, onOpenDesktop }) => {",
    "4: AdminMobile-signatur")

# 5) AdminSettings-signatur
sub("const AdminSettings = ({ currentHq, ownHq, onPick, onClose, isAdmin, canRapport = false }) => {",
    "const AdminSettings = ({ currentHq, ownHq, onPick, onClose, isAdmin, canRapport = false, canAllHq = false }) => {",
    "5: AdminSettings-signatur")

# 6) Header-label: korrekt for landssekretariat
sub("              {isAdmin ? 'ADMIN — SOCIAL SUNDHED' : `RAADGIVER — ${viewingHq.toUpperCase()}`}",
    "              {isAdmin ? 'ADMIN — SOCIAL SUNDHED' : canAllHq ? `LANDSSEKRETARIAT — ${viewingHq.toUpperCase()}` : `RAADGIVER — ${viewingHq.toUpperCase()}`}",
    "6: header-label")

# 7) Tæller: håndter 'Alle hovedsæder'
sub("                    .filter(m => (m.status === 'afventer' || m.status === 'venter') && m.hq === viewingHq).length;",
    "                    .filter(m => (m.status === 'afventer' || m.status === 'venter') && (viewingHq === 'Alle hovedsæder' || m.hq === viewingHq)).length;",
    "7: tæller-fix")

# 8) Hovedsæde-vælger: 'Alle hovedsæder'-mulighed når canAllHq
sub("          {SoS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {",
    """          {canAllHq && (() => {
            const sel = picked === 'Alle hovedsæder';
            return (
              <button onClick={() => setPicked('Alle hovedsæder')} style={{
                display: 'flex', alignItems: 'center', gap: 12, width: '100%',
                padding: 14, marginBottom: 6, textAlign: 'left', background: '#fff',
                border: `2px solid ${sel ? SoS.accent : SoS.lineSoft}`,
                borderRadius: SoS.r.md, cursor: 'pointer',
              }}>
                <div style={{ width: 12, height: 12, borderRadius: 6, background: SoS.accent }}/>
                <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>Alle hovedsæder</span>
                {sel && <Icon name="check" size={16} color={SoS.accent}/>}
              </button>
            );
          })()}
          {SoS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {""",
    "8: alle-hovedsæder-vælger")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

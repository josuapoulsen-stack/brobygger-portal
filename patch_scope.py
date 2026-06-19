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

# A) Brobygger seed: hq + afdeling
BB = [('bb-1','Aarhus','Aarhus C'), ('bb-2','Aarhus','Risskov'), ('bb-3','Aarhus','Brabrand'),
      ('bb-4','Aarhus','Aarhus C'), ('bb-5','Aarhus','Trøjborg'), ('bb-6','Midt','Randers'),
      ('bb-7','Aarhus','Aarhus C'), ('bb-8','Aarhus','Risskov'), ('bb-9','Hovedstaden','København'),
      ('bb-10','Midt','Viborg')]
for bid, hq, afd in BB:
    sub(f"id: '{bid}',", f"id: '{bid}', hq: '{hq}', afdeling: '{afd}',", f"A: hq/afdeling {bid}")

# B) DesktopView signatur + ownAfdeling + onlyMine state
sub(
    "const DesktopView = ({ user, ownHq, isAdmin, canRapport = false, canUserMgmt = false, onClose }) => {",
    "const DesktopView = ({ user, ownHq, ownAfdeling, isAdmin, canRapport = false, canUserMgmt = false, onClose }) => {",
    "B1: DesktopView signatur")
sub(
    "  const [viewingHq, setViewingHq] = React.useState(canRapport ? 'Alle hovedsæder' : ownHq);",
    "  const [viewingHq, setViewingHq] = React.useState(canRapport ? 'Alle hovedsæder' : ownHq);\n  const [onlyMine, setOnlyMine] = React.useState(false);",
    "B2: onlyMine state")

# C) Topbar-toggle "Kun min afdeling" (kun plain rådgiver)
sub(
    "                {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}\n"
    "              </select>\n"
    "              {canRapport && (",
    "                {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}\n"
    "              </select>\n"
    "              {!canRapport && ownAfdeling && (\n"
    "                <button onClick={() => setOnlyMine(v => !v)} title={'Vis kun ' + ownAfdeling}\n"
    "                  style={{ padding: '7px 12px', borderRadius: SoS.r.sm,\n"
    "                    background: onlyMine ? SoS.accent : SoS.surface,\n"
    "                    color: onlyMine ? '#fff' : SoS.inkSoft,\n"
    "                    border: `1px solid ${onlyMine ? SoS.accent : SoS.line}`,\n"
    "                    fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',\n"
    "                    display: 'flex', alignItems: 'center', gap: 6 }}>\n"
    "                  <span style={{ width: 8, height: 8, borderRadius: 4,\n"
    "                    background: onlyMine ? '#fff' : SoS.line }}/>\n"
    "                  Kun {ownAfdeling}\n"
    "                </button>\n"
    "              )}\n"
    "              {canRapport && (",
    "C: topbar-toggle")

# D) DesktopView render: scope-props til lister
sub(
    "{section === 'brobyggere' && <DesktopBrobyggere initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)}/>}",
    "{section === 'brobyggere' && <DesktopBrobyggere initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)} scopeHq={viewingHq} scopeAfd={onlyMine ? ownAfdeling : null}/>}",
    "D1: scope til DesktopBrobyggere")
sub(
    "{section === 'mennesker' && <DesktopMennesker initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)}/>}",
    "{section === 'mennesker' && <DesktopMennesker initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)} scopeHq={viewingHq} scopeAfd={onlyMine ? ownAfdeling : null}/>}",
    "D2: scope til DesktopMennesker")

# E) AppWithTweaks: ownAfdeling på DesktopView-kald
sub(
    '<DesktopView user={user} ownHq="Aarhus" isAdmin={tweaks.role === "admin"}',
    '<DesktopView user={user} ownHq="Aarhus" ownAfdeling="Aarhus C" isAdmin={tweaks.role === "admin"}',
    "E: ownAfdeling i AppWithTweaks")

# F) DesktopBrobyggere: signatur + rows scope-filter
sub(
    "const DesktopBrobyggere = ({ initialTarget, onTargetConsumed }) => {",
    "const DesktopBrobyggere = ({ initialTarget, onTargetConsumed, scopeHq, scopeAfd }) => {",
    "F1: DesktopBrobyggere signatur")
sub(
    "  const rows = SoS_BROBYGGERE\n"
    "    .filter(b => filter === 'alle' || b.status === filter)\n"
    "    .filter(b => !search || b.name.toLowerCase().includes(search.toLowerCase()));",
    "  const rows = SoS_BROBYGGERE\n"
    "    .filter(b => filter === 'alle' || b.status === filter)\n"
    "    .filter(b => !scopeHq || scopeHq === 'Alle hovedsæder' || b.hq === scopeHq)\n"
    "    .filter(b => !scopeAfd || b.afdeling === scopeAfd)\n"
    "    .filter(b => !search || b.name.toLowerCase().includes(search.toLowerCase()));",
    "F2: DesktopBrobyggere rows scope")

# G) DesktopMennesker: signatur + filter-scope
sub(
    "const DesktopMennesker = ({ initialTarget, onTargetConsumed }) => {",
    "const DesktopMennesker = ({ initialTarget, onTargetConsumed, scopeHq, scopeAfd }) => {",
    "G1: DesktopMennesker signatur")
sub(
    "    if (hqFilter !== 'alle' && m.hq !== hqFilter) return false;",
    "    if (scopeHq && scopeHq !== 'Alle hovedsæder' && m.hq !== scopeHq) return false;\n"
    "    if (scopeAfd && m.afdeling !== scopeAfd) return false;\n"
    "    if (hqFilter !== 'alle' && m.hq !== hqFilter) return false;",
    "G2: DesktopMennesker filter-scope")

# H) Skjul HQ-chips når rådgiver er scope-låst til ét hovedsæde
sub(
    "      {/* HQ-filter */}\n      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>",
    "      {/* HQ-filter (skjult når scope-låst til ét hovedsæde) */}\n      {(!scopeHq || scopeHq === 'Alle hovedsæder') && (\n      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>",
    "H1: åbn HQ-chip-wrap")
sub(
    "            cursor: 'pointer' }}>{hq}</button>\n        ))}\n      </div>\n\n      {hqFilter !== 'alle' && SoS_REFS.afdelinger.filter(a => a.hovedsaede === hqFilter).length > 0 && (",
    "            cursor: 'pointer' }}>{hq}</button>\n        ))}\n      </div>\n      )}\n\n      {hqFilter !== 'alle' && SoS_REFS.afdelinger.filter(a => a.hovedsaede === hqFilter).length > 0 && (",
    "H2: luk HQ-chip-wrap")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

with open(P, 'rb') as f:
    b = f.read()
needle = b".join('" + bytes([0x0a]) + b"');"
if needle in b:
    b = b.replace(needle, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(P, 'wb') as f:
        f.write(b)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f"\nOK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"\nFAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

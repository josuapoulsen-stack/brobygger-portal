import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

ok = []
fail = []

def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1)
        ok.append(label)
    else:
        fail.append(label)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 2a: TAB_TITLES — tilføj 'beskeder' entry
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  const TAB_TITLES = {\n    oversigt:   'God morgen, ' + user.firstName,\n    kalender:   'Kalender',\n    mennesker:  'Mennesker',\n    brobyggere: 'Brobyggere',\n    matching:   'Matching',\n  };",
    "  const TAB_TITLES = {\n    oversigt:   'God morgen, ' + user.firstName,\n    kalender:   'Kalender',\n    mennesker:  'Mennesker',\n    brobyggere: 'Brobyggere',\n    matching:   'Matching',\n    beskeder:   'Beskeder',\n  };",
    "Item 2a: TAB_TITLES + beskeder"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 2b: AdminMobileTabBar — betingede tabs pr. rolle
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "const AdminMobileTabBar = ({ active, onChange, isAdmin }) => {\n  const tabs = [\n    { id: 'oversigt',   label: 'Oversigt',   icon: 'home'     },\n    { id: 'kalender',   label: 'Kalender',   icon: 'calendar' },\n    { id: 'mennesker',  label: 'Mennesker',  icon: 'heart'    },\n    { id: 'brobyggere', label: 'Brobyggere', icon: 'users'    },\n    { id: 'matching',   label: 'Matching',   icon: 'match'    },\n  ];",
    "const AdminMobileTabBar = ({ active, onChange, isAdmin }) => {\n  const tabs = isAdmin ? [\n    { id: 'oversigt',   label: 'Oversigt',   icon: 'home'     },\n    { id: 'kalender',   label: 'Kalender',   icon: 'calendar' },\n    { id: 'mennesker',  label: 'Mennesker',  icon: 'heart'    },\n    { id: 'brobyggere', label: 'Brobyggere', icon: 'users'    },\n    { id: 'matching',   label: 'Matching',   icon: 'match'    },\n  ] : [\n    { id: 'oversigt', label: 'Oversigt', icon: 'home'     },\n    { id: 'kalender', label: 'Kalender', icon: 'calendar' },\n    { id: 'beskeder', label: 'Beskeder', icon: 'chat'     },\n  ];",
    "Item 2b: AdminMobileTabBar betingede tabs"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 5a: IntakeFlow — tilføj hqOverride state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  const [behovUrgency, setBehovUrgency] = React.useState('');\n  const canFinish = consent;",
    "  const [behovUrgency, setBehovUrgency] = React.useState('');\n  const [hqOverride, setHqOverride] = React.useState(viewingHq || 'Aarhus');\n  const canFinish = consent;",
    "Item 5a: IntakeFlow hqOverride state"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 5b: IntakeFlow handleFinish — brug hqOverride
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "      hq:           viewingHq || 'Aarhus',",
    "      hq:           hqOverride || viewingHq || 'Aarhus',",
    "Item 5b: IntakeFlow hq = hqOverride"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 5c: IntakeFlow step 1 — vis HQ-vælger
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,\n              marginBottom: 20, lineHeight: 1.5 }}>\n              Fornavn, alder og telefon er påkrævet. Øvrige oplysninger er frivillige.\n            </div>\n            {[\n              { key: 'firstName', label: 'Fornavn',   placeholder: 'f.eks. Erik',  required: true },",
    "            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,\n              marginBottom: 20, lineHeight: 1.5 }}>\n              Fornavn, alder og telefon er påkrævet. Øvrige oplysninger er frivillige.\n            </div>\n            <div style={{ marginBottom: 18 }}>\n              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n                color: SoS.ink, marginBottom: 8 }}>\n                Tilknyt til hovedsæde <span style={{ color: SoS.orange }}>*</span>\n              </div>\n              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>\n                {SoS_HOVEDSAEDER.map(h => (\n                  <button key={h} onClick={() => setHqOverride(h)} style={{\n                    padding: '8px 14px', borderRadius: SoS.r.sm, cursor: 'pointer',\n                    fontFamily: SoS.sans, fontSize: 13, fontWeight: hqOverride === h ? 600 : 400,\n                    background: hqOverride === h ? SoS.orange : '#fff',\n                    color: hqOverride === h ? '#fff' : SoS.ink,\n                    border: `1.5px solid ${hqOverride === h ? SoS.orange : SoS.line}`,\n                  }}>{h}</button>\n                ))}\n              </div>\n            </div>\n            {[\n              { key: 'firstName', label: 'Fornavn',   placeholder: 'f.eks. Erik',  required: true },",
    "Item 5c: IntakeFlow HQ-vælger i trin 1"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 4: DesktopDashboard — SROI-estimat KPI + dynamisk grid
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)',\n      gap: 10, marginBottom: 14 }}>\n      {(() => {\n        const aktive = SoS_BROBYGGERE ? SoS_BROBYGGERE.filter(b => b.status === 'aktiv').length : 0;\n        const afventer = Object.values(SoS_MENNESKER || {}).filter(m => m.status === 'afventer' || m.status === 'venter').length;\n        const konfirmerede = (SoS_APPOINTMENTS_BUSY || []).filter(a => a.status === 'confirmed').length;\n        const pendende = (SoS_APPOINTMENTS_BUSY || []).filter(a => a.status === 'pending').length;\n        return [\n          { l: 'Aktive brobyggere', v: String(aktive), d: aktive > 0 ? 'aktive' : '—', c: SoS.accent },\n          { l: 'Afventer match', v: String(afventer), d: afventer > 0 ? 'ikke matchet' : 'alle matchet', c: SoS.amber },\n          { l: 'Bekæftede aftaler', v: String(konfirmerede), d: 'registrerede', c: SoS.green },\n          { l: 'Afventer bekæftelse', v: String(pendende), d: 'pending', c: SoS.inkMuted },\n          { l: 'Registrerede mennesker', v: String(Object.keys(SoS_MENNESKER || {}).length), d: 'i alt', c: SoS.sky },\n        ];\n      })().map((k, i) => (",
    "    <div style={{ display: 'grid', gridTemplateColumns: canRapport ? 'repeat(6, 1fr)' : 'repeat(5, 1fr)',\n      gap: 10, marginBottom: 14 }}>\n      {(() => {\n        const aktive = SoS_BROBYGGERE ? SoS_BROBYGGERE.filter(b => b.status === 'aktiv').length : 0;\n        const afventer = Object.values(SoS_MENNESKER || {}).filter(m => m.status === 'afventer' || m.status === 'venter').length;\n        const konfirmerede = (SoS_APPOINTMENTS_BUSY || []).filter(a => a.status === 'confirmed').length;\n        const pendende = (SoS_APPOINTMENTS_BUSY || []).filter(a => a.status === 'pending').length;\n        const afsluttede = Object.values(SoS_MENNESKER || {}).filter(m => m.status === 'afsluttet');\n        const sroiEst = afsluttede.length * 47000;\n        const kpis = [\n          { l: 'Aktive brobyggere', v: String(aktive), d: aktive > 0 ? 'aktive' : '—', c: SoS.accent },\n          { l: 'Afventer match', v: String(afventer), d: afventer > 0 ? 'ikke matchet' : 'alle matchet', c: SoS.amber },\n          { l: 'Bekæftede aftaler', v: String(konfirmerede), d: 'registrerede', c: SoS.green },\n          { l: 'Afventer bekæftelse', v: String(pendende), d: 'pending', c: SoS.inkMuted },\n          { l: 'Registrerede mennesker', v: String(Object.keys(SoS_MENNESKER || {}).length), d: 'i alt', c: SoS.sky },\n        ];\n        if (canRapport) kpis.push({ l: 'SROI-estimat', v: (sroiEst/1000).toFixed(0) + 'k', d: 'kr. samfundsværdi', c: SoS.sage });\n        return kpis;\n      })().map((k, i) => (",
    "Item 4: DesktopDashboard SROI KPI + dynamisk grid"
)

# ═══════════════════════════════════════════════════════════════════════════
# ITEM 6: DesktopDashboard — "Afventer match"-callout med Tilknyt-knap
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "    {/* Opfølgning afventer */}\n    {(() => {\n      const TODAY_S = new Date().toISOString().slice(0, 10);",
    "    {/* Afventer match */}\n    {(() => {\n      const afventerListe = Object.values(window.SoS_MENNESKER || {})\n        .filter(m => m.status === 'afventer' || m.status === 'venter')\n        .slice(0, 10);\n      const [expanded, setExpanded] = React.useState(false);\n      const [tilknytMenneske, setTilknytMenneske] = React.useState(null);\n      if (afventerListe.length === 0) return null;\n      return (\n        <>\n          <DSCard style={{ marginBottom: 14, padding: 0, overflow: 'hidden' }}>\n            <button onClick={() => setExpanded(v => !v)} style={{\n              display: 'flex', alignItems: 'center', gap: 12,\n              width: '100%', padding: '14px 18px', background: 'none',\n              border: 'none', cursor: 'pointer', textAlign: 'left' }}>\n              <div style={{ width: 32, height: 32, borderRadius: 0,\n                background: SoS.orange + '20', display: 'flex',\n                alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>\n                <Icon name=\"match\" size={15} color={SoS.orange}/>\n              </div>\n              <div style={{ flex: 1 }}>\n                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: SoS.ink }}>\n                  {afventerListe.length} {afventerListe.length === 1 ? 'person afventer' : 'personer afventer'} match\n                </div>\n                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>\n                  Tilknyt en brobygger direkte herfra\n                </div>\n              </div>\n              <Icon name={expanded ? 'chevronD' : 'chevron'} size={14} color={SoS.inkMuted}/>\n            </button>\n            {expanded && (\n              <div style={{ borderTop: `1px solid ${SoS.line}` }}>\n                {afventerListe.map((m, i) => (\n                  <div key={m.id} style={{\n                    padding: '12px 18px',\n                    borderBottom: i < afventerListe.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',\n                    display: 'flex', alignItems: 'center', gap: 12 }}>\n                    <div style={{ width: 34, height: 34, borderRadius: 17,\n                      background: SoS.orange + '20', display: 'flex',\n                      alignItems: 'center', justifyContent: 'center', flexShrink: 0,\n                      fontFamily: SoS.mono, fontSize: 11, fontWeight: 700, color: SoS.orange }}>\n                      {(m.firstName[0] || '') + (m.lastName ? m.lastName[0] : '')}\n                    </div>\n                    <div style={{ flex: 1 }}>\n                      <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>\n                        {m.firstName} {m.lastName}\n                        <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 400, color: SoS.inkMuted, marginLeft: 6 }}>{m.age} år</span>\n                      </div>\n                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>\n                        {m.hq} · {m.needs && m.needs.length > 0 ? m.needs.slice(0,2).join(', ') : 'Ingen behov angivet'}\n                      </div>\n                    </div>\n                    <button onClick={() => setTilknytMenneske(m)} style={{\n                      padding: '7px 14px', background: SoS.ink, color: '#fff',\n                      border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',\n                      fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n                      whiteSpace: 'nowrap' }}>\n                      Tilknyt\n                    </button>\n                  </div>\n                ))}\n              </div>\n            )}\n          </DSCard>\n          {tilknytMenneske && (\n            <TilknytBrobyggerModal\n              menneske={tilknytMenneske}\n              onClose={() => setTilknytMenneske(null)}\n              onSaved={() => setTilknytMenneske(null)}\n            />\n          )}\n        </>\n      );\n    })()}\n\n    {/* Opfølgning afventer */}\n    {(() => {\n      const TODAY_S = new Date().toISOString().slice(0, 10);",
    "Item 6: 'Afventer match'-callout i DesktopDashboard"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ─────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

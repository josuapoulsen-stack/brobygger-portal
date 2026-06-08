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

# ══════════════════════════════════════════════════════════════════
# 1. TilknytBrobyggerModal: handleMatch sender notif til brobygger
# ══════════════════════════════════════════════════════════════════
sub(
    "  const handleMatch = () => {\n"
    "    if (!valgt) return;\n"
    "    const updated = { ...(window.SoS_MENNESKER || {}) };\n"
    "    updated[m.id] = { ...updated[m.id], brobyggerId: valgt, status: 'aktiv',\n"
    "      matchedAt: new Date().toISOString().slice(0, 10), matchAnmodning: null };\n"
    "    window.SoS_MENNESKER = updated;\n"
    "    window.SoS_STORE?.save('mennesker', updated);\n"
    "    onSaved?.({ brobyggerId: valgt });\n"
    "    onClose();\n"
    "  };",
    "  const handleMatch = () => {\n"
    "    if (!valgt) return;\n"
    "    const updated = { ...(window.SoS_MENNESKER || {}) };\n"
    "    updated[m.id] = { ...updated[m.id], brobyggerId: valgt, status: 'aktiv',\n"
    "      matchedAt: new Date().toISOString().slice(0, 10), matchAnmodning: null };\n"
    "    window.SoS_MENNESKER = updated;\n"
    "    window.SoS_STORE?.save('mennesker', updated);\n"
    "    const _nk = 'sos_notifikationer';\n"
    "    const _ns = JSON.parse(localStorage.getItem(_nk) || '[]');\n"
    "    _ns.push({ id: 'n-' + Date.now(), type: 'nyt-match', read: false,\n"
    "      createdAt: new Date().toISOString(),\n"
    "      text: `Nyt match: ${m.firstName} ${m.lastName} er tilknyttet dig`,\n"
    "      brobyggerId: valgt, menneskeId: m.id });\n"
    "    localStorage.setItem(_nk, JSON.stringify(_ns));\n"
    "    onSaved?.({ brobyggerId: valgt });\n"
    "    onClose();\n"
    "  };",
    "1: handleMatch notifikation til brobygger"
)

# ══════════════════════════════════════════════════════════════════
# 2. HomeScreen: matchVersion state + accept/decline handlers
# ══════════════════════════════════════════════════════════════════
sub(
    "  const [logTarget, setLogTarget] = React.useState(null);\n"
    "  const [apptVersion, setApptVersion] = React.useState(0);",
    "  const [logTarget,    setLogTarget]    = React.useState(null);\n"
    "  const [apptVersion,  setApptVersion]  = React.useState(0);\n"
    "  const [matchVersion, setMatchVersion] = React.useState(0);\n"
    "\n"
    "  const acceptMatch = (person) => {\n"
    "    if (!brobyggerId) return;\n"
    "    const upd = { ...(window.SoS_MENNESKER || {}) };\n"
    "    upd[person.id] = { ...upd[person.id], brobyggerId,\n"
    "      status: 'aktiv',\n"
    "      matchedAt: new Date().toISOString().slice(0, 10),\n"
    "      matchAnmodning: null };\n"
    "    window.SoS_MENNESKER = upd;\n"
    "    window.SoS_STORE?.save('mennesker', upd);\n"
    "    const ns = JSON.parse(localStorage.getItem('sos_notifikationer') || '[]')\n"
    "      .map(n => n.brobyggerId === brobyggerId && n.type === 'match-anmodning'\n"
    "        ? { ...n, status: 'accepteret', read: true } : n);\n"
    "    localStorage.setItem('sos_notifikationer', JSON.stringify(ns));\n"
    "    window.dispatchEvent(new Event('sos-mennesker-updated'));\n"
    "    setMatchVersion(v => v + 1);\n"
    "  };\n"
    "\n"
    "  const declineMatch = (person) => {\n"
    "    const upd = { ...(window.SoS_MENNESKER || {}) };\n"
    "    upd[person.id] = { ...upd[person.id], matchAnmodning: null };\n"
    "    window.SoS_MENNESKER = upd;\n"
    "    window.SoS_STORE?.save('mennesker', upd);\n"
    "    const ns = JSON.parse(localStorage.getItem('sos_notifikationer') || '[]')\n"
    "      .map(n => n.brobyggerId === brobyggerId && n.type === 'match-anmodning'\n"
    "        ? { ...n, status: 'afvist', read: true } : n);\n"
    "    localStorage.setItem('sos_notifikationer', JSON.stringify(ns));\n"
    "    setMatchVersion(v => v + 1);\n"
    "  };",
    "2: HomeScreen matchVersion + accept/decline"
)

# ══════════════════════════════════════════════════════════════════
# 3. HomeScreen: vis forespørgsler + direkte match-notifikationer
#    indsættes efter rådighedsplan-banneret, FØR TopBar
# ══════════════════════════════════════════════════════════════════
FORESP_SECTION = (
    "      {/* Afventende forespørgsler og nye matches */}\n"
    "      {brobyggerId && (() => {\n"
    "        const pending = Object.values(window.SoS_MENNESKER || {})\n"
    "          .filter(p => p.matchAnmodning?.brobyggerId === brobyggerId\n"
    "            && p.matchAnmodning?.status === 'afventer');\n"
    "        const nyeMatches = JSON.parse(localStorage.getItem('sos_notifikationer') || '[]')\n"
    "          .filter(n => n.brobyggerId === brobyggerId\n"
    "            && n.type === 'nyt-match' && !n.read);\n"
    "        if (pending.length === 0 && nyeMatches.length === 0) return null;\n"
    "        return (\n"
    "          <div style={{ margin: '12px 20px 0' }}>\n"
    "            {nyeMatches.map(n => {\n"
    "              const mp = (window.SoS_MENNESKER || {})[n.menneskeId];\n"
    "              return (\n"
    "                <div key={n.id} style={{ padding: '12px 14px',\n"
    "                  background: SoS.sage + '15',\n"
    "                  border: `1px solid ${SoS.sage}40`,\n"
    "                  borderRadius: SoS.r.md, marginBottom: 8,\n"
    "                  display: 'flex', alignItems: 'center', gap: 12 }}>\n"
    "                  <div style={{ width: 8, height: 8, borderRadius: 4,\n"
    "                    background: SoS.sage, flexShrink: 0 }}/>\n"
    "                  <div style={{ flex: 1 }}>\n"
    "                    <div style={{ fontFamily: SoS.sans, fontSize: 13,\n"
    "                      fontWeight: 700, color: SoS.ink }}>Nyt match!</div>\n"
    "                    <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                      color: SoS.inkMuted, marginTop: 2 }}>{n.text}</div>\n"
    "                  </div>\n"
    "                  <button onClick={() => {\n"
    "                    const ns = JSON.parse(localStorage.getItem('sos_notifikationer') || '[]')\n"
    "                      .map(x => x.id === n.id ? { ...x, read: true } : x);\n"
    "                    localStorage.setItem('sos_notifikationer', JSON.stringify(ns));\n"
    "                    setMatchVersion(v => v + 1);\n"
    "                  }} style={{ background: 'none', border: 'none',\n"
    "                    cursor: 'pointer', fontFamily: SoS.sans,\n"
    "                    fontSize: 11, color: SoS.inkMuted }}>OK</button>\n"
    "                </div>\n"
    "              );\n"
    "            })}\n"
    "            {pending.map(p => {\n"
    "              const t = SoS_TYPER[p.type] || {};\n"
    "              return (\n"
    "                <div key={p.id} style={{ padding: '14px',\n"
    "                  background: SoS.orange + '10',\n"
    "                  border: `1px solid ${SoS.orange}40`,\n"
    "                  borderRadius: SoS.r.md, marginBottom: 8 }}>\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 13,\n"
    "                    fontWeight: 700, color: SoS.ink, marginBottom: 4 }}>\n"
    "                    Foresp\xf8rgsel om brobygning\n"
    "                  </div>\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                    color: SoS.inkMuted, marginBottom: 12 }}>\n"
    "                    {p.firstName} {p.lastName}, {p.age} \xe5r\n"
    "                    {t.short ? ` \xb7 ${t.short}` : ''}\n"
    "                    {p.hq ? ` \xb7 ${p.hq}` : ''}\n"
    "                  </div>\n"
    "                  <div style={{ display: 'flex', gap: 8 }}>\n"
    "                    <button onClick={() => acceptMatch(p)} style={{\n"
    "                      flex: 2, padding: '10px 0',\n"
    "                      background: SoS.sage, color: '#fff', border: 'none',\n"
    "                      borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                      fontFamily: SoS.sans, fontSize: 14, fontWeight: 700 }}>\n"
    "                      Accepter\n"
    "                    </button>\n"
    "                    <button onClick={() => declineMatch(p)} style={{\n"
    "                      flex: 1, padding: '10px 0',\n"
    "                      background: 'none',\n"
    "                      border: `1px solid ${SoS.line}`,\n"
    "                      borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                      fontFamily: SoS.sans, fontSize: 14,\n"
    "                      color: SoS.inkMuted }}>Afvis</button>\n"
    "                  </div>\n"
    "                </div>\n"
    "              );\n"
    "            })}\n"
    "          </div>\n"
    "        );\n"
    "      })()}\n"
)

sub(
    "      <TopBar\n"
    "        subtitle={greet}\n"
    "        title={<span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>",
    FORESP_SECTION +
    "      <TopBar\n"
    "        subtitle={greet}\n"
    "        title={<span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>",
    "3: HomeScreen forespørgsler + nye matches"
)

# Gør bell-badge dynamisk
sub(
    "            <Icon name=\"bell\" size={22} color={SoS.ink} />\n"
    "            <div style={{ position: 'absolute', top: 10, right: 10, width: 8, height: 8,\n"
    "              borderRadius: 4, background: SoS.rose, border: '2px solid #fff' }} />",
    "            <Icon name=\"bell\" size={22} color={SoS.ink} />\n"
    "            {(() => {\n"
    "              const pf = Object.values(window.SoS_MENNESKER || {})\n"
    "                .filter(p => p.matchAnmodning?.brobyggerId === brobyggerId\n"
    "                  && p.matchAnmodning?.status === 'afventer').length;\n"
    "              const nm = JSON.parse(localStorage.getItem('sos_notifikationer') || '[]')\n"
    "                .filter(n => n.brobyggerId === brobyggerId && !n.read).length;\n"
    "              const cnt = pf + nm;\n"
    "              if (cnt === 0) return null;\n"
    "              return (\n"
    "                <div style={{ position: 'absolute', top: 8, right: 8,\n"
    "                  minWidth: 16, height: 16, borderRadius: 8,\n"
    "                  background: SoS.rose, border: '2px solid #fff',\n"
    "                  display: 'flex', alignItems: 'center', justifyContent: 'center',\n"
    "                  fontFamily: SoS.sans, fontSize: 9, fontWeight: 700, color: '#fff',\n"
    "                  padding: '0 3px' }}>\n"
    "                  {cnt > 9 ? '9+' : cnt}\n"
    "                </div>\n"
    "              );\n"
    "            })()}",
    "3b: HomeScreen bell badge dynamisk"
)

# ══════════════════════════════════════════════════════════════════
# 4. CalendarScreen saveRaadig: tjek venteliste efter gem
# ══════════════════════════════════════════════════════════════════
sub(
    "  const saveRaadig = (newEntries) => {\n"
    "    const prev = JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]');\n"
    "    const updated = [...prev, ...newEntries];\n"
    "    localStorage.setItem('sos_raadighedsplan', JSON.stringify(updated));\n"
    "    setRaadighedsplan(updated);\n"
    "    setAddedCount(newEntries.length);\n"
    "    setAddShiftDone(true);\n"
    "  };",
    "  const saveRaadig = (newEntries) => {\n"
    "    const prev = JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]');\n"
    "    const updated = [...prev, ...newEntries];\n"
    "    localStorage.setItem('sos_raadighedsplan', JSON.stringify(updated));\n"
    "    setRaadighedsplan(updated);\n"
    "    setAddedCount(newEntries.length);\n"
    "    setAddShiftDone(true);\n"
    "    // Tjek venteliste\n"
    "    const vl = JSON.parse(localStorage.getItem('sos_venteliste') || '[]');\n"
    "    const newDates = newEntries.map(e => e.dato);\n"
    "    const matches = vl.filter(v => {\n"
    "      const p = (window.SoS_MENNESKER || {})[v.menneskeId];\n"
    "      return p && p.appointmentDato && newDates.includes(p.appointmentDato);\n"
    "    });\n"
    "    if (matches.length > 0 && brobyggerId) {\n"
    "      const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === brobyggerId);\n"
    "      const existing = JSON.parse(\n"
    "        localStorage.getItem('sos_venteliste_matches') || '[]');\n"
    "      matches.forEach(v => {\n"
    "        const p = (window.SoS_MENNESKER || {})[v.menneskeId];\n"
    "        if (!existing.some(e =>\n"
    "            e.menneskeId === v.menneskeId && e.brobyggerId === brobyggerId)) {\n"
    "          existing.push({\n"
    "            id: 'vm-' + Date.now() + '-' + v.menneskeId,\n"
    "            brobyggerId,\n"
    "            brobyggerNavn: bb?.name || 'Ukendt brobygger',\n"
    "            menneskeId: v.menneskeId,\n"
    "            menneskeNavn: p ? p.firstName + ' ' + p.lastName : '?',\n"
    "            dato: p.appointmentDato,\n"
    "            sted: p.appointmentSted || null,\n"
    "            createdAt: new Date().toISOString(),\n"
    "            read: false,\n"
    "          });\n"
    "        }\n"
    "      });\n"
    "      localStorage.setItem(\n"
    "        'sos_venteliste_matches', JSON.stringify(existing));\n"
    "    }\n"
    "  };",
    "4: CalendarScreen saveRaadig venteliste-check"
)

# ══════════════════════════════════════════════════════════════════
# 5. DesktopDashboard: venteliste matches i Dagsorden
# ══════════════════════════════════════════════════════════════════
sub(
    "  const urgentCount = opfPending.length\n"
    "    + afventerListe.filter(m => daysWaiting(m) >= 3).length;\n"
    "  const harDagsorden = opfPending.length > 0 || afventerListe.length > 0;",
    "  const venteMatches = (() => {\n"
    "    try {\n"
    "      return JSON.parse(\n"
    "        localStorage.getItem('sos_venteliste_matches') || '[]')\n"
    "        .filter(v => !v.read);\n"
    "    } catch { return []; }\n"
    "  })();\n"
    "  const urgentCount = opfPending.length\n"
    "    + afventerListe.filter(m => daysWaiting(m) >= 3).length\n"
    "    + venteMatches.length;\n"
    "  const harDagsorden = opfPending.length > 0\n"
    "    || afventerListe.length > 0 || venteMatches.length > 0;",
    "5a: DesktopDashboard venteMatches state"
)

# Indsæt venteliste-rækker i dagsorden INDEN afventer-liste
sub(
    "          {/* Afventer match */}\n"
    "          {afventerListe.slice(0, 5).map((m, i) => {",
    "          {/* Venteliste matches */}\n"
    "          {venteMatches.map((v, i) => (\n"
    "            <div key={v.id} style={{ padding: '12px 18px',\n"
    "              borderBottom: `1px solid ${SoS.lineSoft}`,\n"
    "              display: 'flex', alignItems: 'center', gap: 12 }}>\n"
    "              <div style={{ width: 3, alignSelf: 'stretch',\n"
    "                background: SoS.sage, flexShrink: 0, borderRadius: 2 }}/>\n"
    "              <div style={{ flex: 1, minWidth: 0 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 13,\n"
    "                  fontWeight: 600, color: SoS.ink }}>\n"
    "                  {v.menneskeNavn}\n"
    "                  <span style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                    fontWeight: 400, color: SoS.inkMuted, marginLeft: 6 }}>\n"
    "                    p\xe5 venteliste\n"
    "                  </span>\n"
    "                </div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                  color: SoS.inkMuted, marginTop: 2 }}>\n"
    "                  {v.brobyggerNavn} er ledig\n"
    "                  {' '}{new Date(v.dato).toLocaleDateString('da-DK',\n"
    "                    { weekday: 'short', day: 'numeric', month: 'short' })}\n"
    "                  {v.sted ? ` \xb7 ${v.sted}` : ''}\n"
    "                </div>\n"
    "              </div>\n"
    "              <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>\n"
    "                <button onClick={() => setTilknytMenneske(\n"
    "                  (window.SoS_MENNESKER || {})[v.menneskeId])} style={{\n"
    "                  padding: '6px 12px', background: SoS.sage, color: '#fff',\n"
    "                  border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                  fontFamily: SoS.sans, fontSize: 11, fontWeight: 700 }}>\n"
    "                  Match nu\n"
    "                </button>\n"
    "                <button onClick={() => {\n"
    "                  const all = JSON.parse(\n"
    "                    localStorage.getItem('sos_venteliste_matches') || '[]')\n"
    "                    .map(x => x.id === v.id ? { ...x, read: true } : x);\n"
    "                  localStorage.setItem(\n"
    "                    'sos_venteliste_matches', JSON.stringify(all));\n"
    "                  setOpfVersion(n => n + 1);\n"
    "                }} style={{ padding: '6px 10px', background: SoS.surfaceAlt,\n"
    "                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "                  cursor: 'pointer', fontFamily: SoS.sans,\n"
    "                  fontSize: 11, color: SoS.inkMuted }}>Luk</button>\n"
    "              </div>\n"
    "            </div>\n"
    "          ))}\n"
    "\n"
    "          {/* Afventer match */}\n"
    "          {afventerListe.slice(0, 5).map((m, i) => {",
    "5b: DesktopDashboard venteliste rækker i Dagsorden"
)

# ══════════════════════════════════════════════════════════════════
# 6. AppWithTweaks: send _bbId til MessagesList
# ══════════════════════════════════════════════════════════════════
sub(
    "              : <MessagesList\n"
    "                  onOpen={(id) => setMsgOpenId(id)}\n"
    "                  onCompose={() => setMsgCompose(true)}\n"
    "                  role={activeRole}\n"
    "                  ownHq={viewingHq}\n"
    "                  onNavigate={navigate}",
    "              : <MessagesList\n"
    "                  onOpen={(id) => setMsgOpenId(id)}\n"
    "                  onCompose={() => setMsgCompose(true)}\n"
    "                  role={activeRole}\n"
    "                  ownHq={viewingHq}\n"
    "                  brobyggerId={_bbId}\n"
    "                  onNavigate={navigate}",
    "6: AppWithTweaks _bbId til MessagesList"
)

# ══════════════════════════════════════════════════════════════════
# 7. MessagesList: brug faktisk brobyggerId som fra-felt
# ══════════════════════════════════════════════════════════════════
sub(
    "const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose, onNavigate }) => {",
    "const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose, onNavigate, brobyggerId }) => {",
    "7a: MessagesList brobyggerId prop"
)

sub(
    "    const nm = { id: 'msg-' + Date.now(), fra: 'brobygger', til: 'admin',\n"
    "      tekst: t, sendt: new Date().toISOString(), laest: false };",
    "    const nm = { id: 'msg-' + Date.now(),\n"
    "      fra: (role === 'brobygger' && brobyggerId) ? brobyggerId : role,\n"
    "      til: 'admin',\n"
    "      tekst: t, sendt: new Date().toISOString(), laest: false };",
    "7b: MessagesList brug brobyggerId som fra"
)

# ─── Write ───────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print('CRLF-fix: rettet')
else:
    print('CRLF-check: OK')

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  OK {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  FAIL {x}')
print('\nFil skrevet.')

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
# VERSION — HTML titel + sidebar badge
# ══════════════════════════════════════════════════════════════════
sub(
    '<title>Brobygger portal — SoS</title>',
    '<title>Brobygger Portal — SoS v1.0</title>',
    "Version: HTML titel"
)

sub(
    "                {canUserMgmt ? 'Admin' : canRapport ? 'Leder' : ownHq}\n              </div>\n            </div>\n      ",
    "                {canUserMgmt ? 'Admin' : canRapport ? 'Leder' : ownHq}\n              </div>\n            </div>\n            <div style={{ padding: '6px 12px 10px', display: 'flex', justifyContent: 'flex-end' }}>\n              <span style={{ fontFamily: SoS.mono, fontSize: 8.5, color: SoS.inkMuted,\n                letterSpacing: 0.5 }}>v1.0</span>\n            </div>\n      ",
    "Version: sidebar badge"
)

# ══════════════════════════════════════════════════════════════════
# C1+C2 — TilknytBrobyggerModal: bredere, person-kontekst,
#          tilgængeligheds-chips, venteliste
# ══════════════════════════════════════════════════════════════════

# Gør dialogen bredere og tilføj person-kontekst strip
sub(
    "      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 440,\n"
    "        padding: 28, boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>",
    "      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 620,\n"
    "        boxShadow: '0 8px 40px rgba(0,0,0,0.18)', overflow: 'hidden' }}>\n"
    "        {/* Person-kontekst strip */}\n"
    "        {(() => {\n"
    "          const t = SoS_TYPER[m.type] || {};\n"
    "          const days = m.createdAt\n"
    "            ? Math.floor((new Date() - new Date(m.createdAt)) / (1000*60*60*24))\n"
    "            : 0;\n"
    "          return (\n"
    "            <div style={{ padding: '14px 20px', background: SoS.ink,\n"
    "              display: 'flex', alignItems: 'center', gap: 14 }}>\n"
    "              <div style={{ flex: 1 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700,\n"
    "                  color: '#fff' }}>\n"
    "                  {m.firstName} {m.lastName}\n"
    "                  {m.behovUrgency === 'snarest' && (\n"
    "                    <span style={{ marginLeft: 8, color: SoS.rose, fontSize: 11 }}>Haster</span>\n"
    "                  )}\n"
    "                </div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                  color: 'rgba(255,255,255,0.6)', marginTop: 3 }}>\n"
    "                  {m.age} \xe5r \xb7 {m.hq}\n"
    "                  {days > 0 && ` \xb7 Ventet ${days} dage`}\n"
    "                </div>\n"
    "              </div>\n"
    "              {t.color && (\n"
    "                <div style={{ padding: '4px 10px', borderRadius: SoS.r.sm,\n"
    "                  background: t.soft, color: t.color,\n"
    "                  fontFamily: SoS.sans, fontSize: 11, fontWeight: 700 }}>\n"
    "                  {t.short}\n"
    "                </div>\n"
    "              )}\n"
    "            </div>\n"
    "          );\n"
    "        })()}\n"
    "        <div style={{ padding: 24 }}>",
    "C1: person-kontekst strip i TilknytBrobyggerModal"
)

# Luk den nye inner div og tilføj venteliste-knap
sub(
    "        {/* Action-knapper */}\n"
    "        <div style={{ display: 'flex', gap: 10 }}>\n"
    "          <button onClick={onClose}\n"
    "            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,\n"
    "              background: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer' }}>\n"
    "            Annuller\n"
    "          </button>\n"
    "          {mode === 'ledig' ? (\n"
    "            <button onClick={handleMatch} disabled={!valgt}\n"
    "              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "                background: valgt ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>\n"
    "              Match med brobygger\n"
    "            </button>\n"
    "          ) : (\n"
    "            <button onClick={handleForesporg} disabled={!valgt}\n"
    "              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "                background: valgt ? '#D97706' : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>\n"
    "              Send foresp\xf8rgsel\n"
    "            </button>\n"
    "          )}\n"
    "        </div>\n"
    "      </div>\n"
    "    </div>",
    "        {/* Action-knapper */}\n"
    "        <div style={{ display: 'flex', gap: 10 }}>\n"
    "          <button onClick={onClose}\n"
    "            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,\n"
    "              background: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer' }}>\n"
    "            Annuller\n"
    "          </button>\n"
    "          {mode === 'ledig' ? (\n"
    "            <button onClick={handleMatch} disabled={!valgt}\n"
    "              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "                background: valgt ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>\n"
    "              Match med brobygger\n"
    "            </button>\n"
    "          ) : (\n"
    "            <button onClick={handleForesporg} disabled={!valgt}\n"
    "              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "                background: valgt ? '#D97706' : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>\n"
    "              Send foresp\xf8rgsel\n"
    "            </button>\n"
    "          )}\n"
    "        </div>\n"
    "        {ledige.length === 0 && (\n"
    "          <button onClick={() => {\n"
    "            const vl = JSON.parse(localStorage.getItem('sos_venteliste') || '[]');\n"
    "            const exists = vl.some(v => v.menneskeId === m.id);\n"
    "            if (!exists) {\n"
    "              vl.push({ id: 'vl-' + Date.now(), menneskeId: m.id,\n"
    "                navn: m.firstName + ' ' + m.lastName,\n"
    "                dato: new Date().toISOString().slice(0,10) });\n"
    "              localStorage.setItem('sos_venteliste', JSON.stringify(vl));\n"
    "            }\n"
    "            onClose();\n"
    "          }} style={{ width: '100%', marginTop: 8, padding: '9px 0',\n"
    "            background: 'none', border: `1px dashed ${SoS.amber}`,\n"
    "            borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "            fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n"
    "            color: SoS.amber }}>\n"
    "            S\xe6t p\xe5 venteliste — f\xe5r besked n\xe5r en brobygger er ledig\n"
    "          </button>\n"
    "        )}\n"
    "        </div>\n"
    "      </div>\n"
    "    </div>",
    "C3: venteliste-knap i TilknytBrobyggerModal"
)

# Brobygger-kortene: tilføj tilgængeligheds-chips (C2)
sub(
    "                  {myAppts.length} aktive aftaler\n"
    "                    {mode === 'ledig' && ` \xb7 ${b.openShifts} ledig${b.openShifts !== 1 ? 'e' : ''} tid${b.openShifts !== 1 ? 'er' : ''}`}\n"
    "                  </div>",
    "                  {myAppts.length} aktive aftaler\n"
    "                    {mode === 'ledig' && ` \xb7 ${b.openShifts} ledig${b.openShifts !== 1 ? 'e' : ''}`}\n"
    "                  </div>\n"
    "                  {mode === 'ledig' && b.openShifts > 0 && (\n"
    "                    <div style={{ display: 'flex', gap: 4, marginTop: 4, flexWrap: 'wrap' }}>\n"
    "                      {['Man\xe2\x80\x93ons', 'Hverdage', 'Fleksibelt'][b.openShifts > 2 ? 2 : b.openShifts - 1]\n"
    "                        .split('\xb7').map((slot, si) => (\n"
    "                        <span key={si} style={{ padding: '2px 7px',\n"
    "                          background: SoS.green + '18', color: SoS.green,\n"
    "                          borderRadius: SoS.r.sm,\n"
    "                          fontFamily: SoS.mono, fontSize: 9, fontWeight: 700 }}>\n"
    "                          {['Man\xe2\x80\x93ons', 'Hverdage', 'Fleksibelt'][b.openShifts > 2 ? 2 : b.openShifts - 1]}\n"
    "                        </span>\n"
    "                      ))}\n"
    "                    </div>\n"
    "                  )}",
    "C2: tilgængeligheds-chips i brobygger-kort"
)

# ══════════════════════════════════════════════════════════════════
# D1 — Beskeder-tab i DesktopMenneskeDetailPanel
# ══════════════════════════════════════════════════════════════════

# Tilføj 'Beskeder' som 5. tab
sub(
    "  const TABS        = ['Oversigt', 'Tidslinje', 'Aftaler', 'Detaljer'];",
    "  const TABS        = ['Oversigt', 'Tidslinje', 'Aftaler', 'Detaljer', 'Beskeder'];\n"
    "  const [beskedTekst, setBeskedTekst] = React.useState('');\n"
    "  const [beskedAlle,  setBeskedAlle]  = React.useState(() => {\n"
    "    try { return JSON.parse(localStorage.getItem('sos_beskeder') || '[]'); }\n"
    "    catch { return []; }\n"
    "  });\n"
    "  const tilknyttetBB = (window.SoS_BROBYGGERE || []).find(b => b.id === m.brobyggerId);\n"
    "  const bbTrad = beskedAlle\n"
    "    .filter(msg => msg.fra === (m.brobyggerId || '') || msg.til === (m.brobyggerId || ''))\n"
    "    .sort((a, b) => a.sendt.localeCompare(b.sendt));\n"
    "  const sendBeskedFraForloeb = () => {\n"
    "    if (!beskedTekst.trim() || !m.brobyggerId) return;\n"
    "    const newMsg = { id: 'msg-' + Date.now(), fra: 'admin', til: m.brobyggerId,\n"
    "      tekst: beskedTekst.trim(), sendt: new Date().toISOString(), laest: false };\n"
    "    const updated = [...beskedAlle, newMsg];\n"
    "    setBeskedAlle(updated);\n"
    "    localStorage.setItem('sos_beskeder', JSON.stringify(updated));\n"
    "    setBeskedTekst('');\n"
    "  };",
    "D1: Beskeder tab state i DesktopMenneskeDetailPanel"
)

# Tilføj beskeder tab-badge og tab-indhold
sub(
    "            {tab === 'Aftaler' && mennAppts.length > 0 && (\n"
    "              <span style={{ marginLeft: 5, background: SoS.lineSoft, borderRadius: 8,\n"
    "                padding: '1px 5px', fontSize: 10, color: SoS.inkMuted }}>\n"
    "                {mennAppts.length}\n"
    "              </span>\n"
    "            )}",
    "            {tab === 'Aftaler' && mennAppts.length > 0 && (\n"
    "              <span style={{ marginLeft: 5, background: SoS.lineSoft, borderRadius: 8,\n"
    "                padding: '1px 5px', fontSize: 10, color: SoS.inkMuted }}>\n"
    "                {mennAppts.length}\n"
    "              </span>\n"
    "            )}\n"
    "            {tab === 'Beskeder' && bbTrad.filter(msg => !msg.laest && msg.fra !== 'admin').length > 0 && (\n"
    "              <span style={{ marginLeft: 5, minWidth: 14, height: 14, borderRadius: 7,\n"
    "                background: SoS.accent, display: 'inline-flex', alignItems: 'center',\n"
    "                justifyContent: 'center', fontSize: 9, fontWeight: 700, color: '#fff',\n"
    "                padding: '0 3px' }}>\n"
    "                {bbTrad.filter(msg => !msg.laest && msg.fra !== 'admin').length}\n"
    "              </span>\n"
    "            )}",
    "D1: Beskeder tab-badge"
)

# Tilføj beskeder tab indhold (activeTab === 4) inden den afsluttende </div>
sub(
    "      </div>\n"
    "      {addOpen && <AddKontaktFlow",
    "        {/* ── BESKEDER ── */}\n"
    "        {activeTab === 4 && (\n"
    "          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>\n"
    "            {!tilknyttetBB ? (\n"
    "              <div style={{ padding: '30px 0', textAlign: 'center',\n"
    "                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>\n"
    "                Ingen brobygger tilknyttet endnu \xb7 Tilknyt en brobygger for at se beskeder\n"
    "              </div>\n"
    "            ) : (\n"
    "              <>\n"
    "                <div style={{ padding: '8px 0 12px',\n"
    "                  fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>\n"
    "                  Beskeder med {tilknyttetBB.name}\n"
    "                </div>\n"
    "                <div style={{ display: 'flex', flexDirection: 'column', gap: 8,\n"
    "                  minHeight: 120, maxHeight: 320, overflowY: 'auto',\n"
    "                  padding: '12px 0', marginBottom: 12 }}>\n"
    "                  {bbTrad.length === 0 && (\n"
    "                    <div style={{ textAlign: 'center', padding: '24px 0',\n"
    "                      fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>\n"
    "                      Ingen beskeder endnu \xb7 Send den f\xf8rste herunder\n"
    "                    </div>\n"
    "                  )}\n"
    "                  {bbTrad.map(msg => {\n"
    "                    const erAdmin = msg.fra === 'admin';\n"
    "                    return (\n"
    "                      <div key={msg.id}\n"
    "                        style={{ display: 'flex',\n"
    "                          justifyContent: erAdmin ? 'flex-end' : 'flex-start' }}>\n"
    "                        <div style={{ maxWidth: '78%' }}>\n"
    "                          <div style={{ padding: '8px 12px', lineHeight: 1.5,\n"
    "                            fontFamily: SoS.sans, fontSize: 12,\n"
    "                            background: erAdmin ? SoS.accent : '#fff',\n"
    "                            color: erAdmin ? '#fff' : SoS.ink,\n"
    "                            border: erAdmin ? 'none' : `1px solid ${SoS.line}`,\n"
    "                            borderRadius: erAdmin\n"
    "                              ? `${SoS.r.md}px ${SoS.r.md}px 4px ${SoS.r.md}px`\n"
    "                              : `${SoS.r.md}px ${SoS.r.md}px ${SoS.r.md}px 4px` }}>\n"
    "                            {msg.tekst}\n"
    "                          </div>\n"
    "                          <div style={{ fontFamily: SoS.sans, fontSize: 9,\n"
    "                            color: SoS.inkMuted, marginTop: 3,\n"
    "                            textAlign: erAdmin ? 'right' : 'left' }}>\n"
    "                            {new Date(msg.sendt).toLocaleDateString('da-DK',\n"
    "                              { day: 'numeric', month: 'short' })}\n"
    "                          </div>\n"
    "                        </div>\n"
    "                      </div>\n"
    "                    );\n"
    "                  })}\n"
    "                </div>\n"
    "                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>\n"
    "                  <textarea value={beskedTekst}\n"
    "                    onChange={e => setBeskedTekst(e.target.value)}\n"
    "                    onKeyDown={e => {\n"
    "                      if (e.key === 'Enter' && !e.shiftKey) {\n"
    "                        e.preventDefault(); sendBeskedFraForloeb();\n"
    "                      }\n"
    "                    }}\n"
    "                    placeholder={`Skriv til ${tilknyttetBB.name.split(' ')[0]}…`}\n"
    "                    rows={2}\n"
    "                    style={{ flex: 1, padding: '8px 12px',\n"
    "                      border: `1px solid ${SoS.line}`,\n"
    "                      borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 12,\n"
    "                      color: SoS.ink, outline: 'none', resize: 'none',\n"
    "                      lineHeight: 1.45 }}/>\n"
    "                  <button onClick={sendBeskedFraForloeb}\n"
    "                    disabled={!beskedTekst.trim()}\n"
    "                    style={{ padding: '9px 14px', borderRadius: SoS.r.sm,\n"
    "                      border: 'none',\n"
    "                      background: beskedTekst.trim() ? SoS.accent : SoS.lineSoft,\n"
    "                      color: beskedTekst.trim() ? '#fff' : SoS.inkMuted,\n"
    "                      cursor: beskedTekst.trim() ? 'pointer' : 'default',\n"
    "                      fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,\n"
    "                      alignSelf: 'flex-end' }}>\n"
    "                    Send\n"
    "                  </button>\n"
    "                </div>\n"
    "              </>\n"
    "            )}\n"
    "          </div>\n"
    "        )}\n"
    "\n"
    "      </div>\n"
    "      {addOpen && <AddKontaktFlow",
    "D1: Beskeder tab indhold i DesktopMenneskeDetailPanel"
)

# D2 — Forløbslog: tilføj opkald-log i Tidslinje (index 1)
# Find eksisterende Tidslinje indhold
sub(
    "        {activeTab === 1 && (\n"
    "          <MenneskeTimelineInline m={m}/>",
    "        {activeTab === 1 && (\n"
    "          <>\n"
    "            <MenneskeTimelineInline m={m}/>\n"
    "            {(() => {\n"
    "              const logs = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]')\n"
    "                .filter(l => l.navn &&\n"
    "                  (l.navn.toLowerCase().includes(m.firstName?.toLowerCase() || '') ||\n"
    "                   l.navn.toLowerCase().includes(m.lastName?.toLowerCase() || '')));\n"
    "              if (logs.length === 0) return null;\n"
    "              return (\n"
    "                <div style={{ marginTop: 14 }}>\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,\n"
    "                    color: SoS.inkMuted, letterSpacing: 0.9,\n"
    "                    textTransform: 'uppercase', marginBottom: 8 }}>Loggede opkald</div>\n"
    "                  {logs.map((l, i) => (\n"
    "                    <div key={l.id} style={{ display: 'flex', gap: 10,\n"
    "                      padding: '8px 0',\n"
    "                      borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>\n"
    "                      <div style={{ fontFamily: SoS.mono, fontSize: 10,\n"
    "                        color: SoS.inkMuted, flexShrink: 0, width: 70 }}>\n"
    "                        {l.dato} {l.tid}\n"
    "                      </div>\n"
    "                      <div style={{ flex: 1 }}>\n"
    "                        <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                          fontWeight: 600, color: SoS.ink }}>{l.navn}</div>\n"
    "                        <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                          color: SoS.inkSoft, marginTop: 2 }}>{l.note}</div>\n"
    "                      </div>\n"
    "                    </div>\n"
    "                  ))}\n"
    "                </div>\n"
    "              );\n"
    "            })()}\n"
    "          </>",
    "D2: Opkald-log i Tidslinje-tab"
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
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

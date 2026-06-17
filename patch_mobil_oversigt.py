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

# ── 1) Opfølgnings-state i AdminMobile (efter TYPE_C) ──
sub(
    "  const TYPE_C = { sundhed: SoS.sundhed, forening: SoS.forening, social: SoS.social };",
    "  const TYPE_C = { sundhed: SoS.sundhed, forening: SoS.forening, social: SoS.social };\n"
    "  const TODAY_S = new Date().toISOString().slice(0, 10);\n"
    "  const [opfVersion, setOpfVersion] = React.useState(0);\n"
    "  const opfPending = (window.SoS_APPOINTMENTS_BUSY || [])\n"
    "    .filter(a => a.date < TODAY_S && a.brobyggerLog && !a.raadgiverOpfoelgning)\n"
    "    .sort((a, b) => a.date.localeCompare(b.date));\n"
    "  const setOpfoelgning = (apptId, val) => {\n"
    "    const list = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>\n"
    "      a.id === apptId ? { ...a, raadgiverOpfoelgning: val } : a);\n"
    "    window.SoS_APPOINTMENTS_BUSY = list;\n"
    "    if (window.SoS_STORE) window.SoS_STORE.save('appointments', list);\n"
    "    setOpfVersion(v => v + 1);\n"
    "  };",
    "1: opfølgnings-state i AdminMobile")

# ── 2) Erstat match-prompt med Dagsorden-kort (opfølgninger) ──
OLD = """            {/* Hurtige handlinger */}
            {isAdmin && pendingMatches > 0 && (
              <button onClick={onOpenMatching} style={{
                margin: '12px 22px 0', width: 'calc(100% - 44px)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '13px 16px', background: SoS.ink, border: 'none',
                borderRadius: SoS.r.sm, cursor: 'pointer',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="7.5" cy="7.5" r="3"/>
                    <circle cx="16.5" cy="7.5" r="3"/>
                    <path d="M2.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5"/>
                    <path d="M11.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5"/>
                  </svg>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: '#fff' }}>
                    {pendingMatches} {pendingMatches === 1 ? 'menneske venter' : 'mennesker venter'} på match
                  </span>
                </div>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke={SoS.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </button>
            )}"""

NEW = """            {/* Dagsorden — opfølgninger (ring & notér; ideelt på telefon) */}
            {opfPending.length > 0 && (
              <div style={{ margin: '12px 22px 0', border: `1px solid ${SoS.line}`,
                background: SoS.surface }}>
                <div style={{ padding: '9px 14px', display: 'flex', alignItems: 'center',
                  gap: 8, background: SoS.ink }}>
                  <span style={{ fontFamily: SoS.mono, fontSize: 10, fontWeight: 700,
                    color: '#fff', textTransform: 'uppercase', letterSpacing: 0.8 }}>DAGSORDEN</span>
                  <span style={{ marginLeft: 'auto', fontFamily: SoS.mono, fontSize: 9.5,
                    color: 'rgba(255,255,255,0.7)' }}>{opfPending.length} afventer opfølgning</span>
                </div>
                {opfPending.slice(0, 5).map((a, i) => {
                  const mn = SoS_MENNESKER[a.menneskeId];
                  const bb = SoS_BROBYGGERE.find(b => b.id === a.brobyggerId);
                  const log = a.brobyggerLog || {};
                  const UD = { gennemfoert: 'Gennemført', afbud: 'Afbud', 'ikke-modt': 'Mødte ikke op' };
                  const UC = { gennemfoert: SoS.green, afbud: SoS.amber, 'ikke-modt': SoS.rose };
                  return (
                    <div key={a.id} style={{ padding: '10px 14px',
                      borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                        {mn ? (mn.firstName + ' ' + mn.lastName) : '—'}
                        {log.udfald && (
                          <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700,
                            color: UC[log.udfald] || SoS.inkMuted, marginLeft: 6,
                            textTransform: 'uppercase' }}>{UD[log.udfald] || log.udfald}</span>
                        )}
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
                        {a.date}{bb ? (' · ' + bb.name.split(' ')[0]) : ''}{log.note ? (' · "' + log.note + '"') : ''}
                      </div>
                      <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                        <button onClick={() => setOpfoelgning(a.id, 'fulgt-op')} style={{
                          flex: 1, padding: '8px 0', background: SoS.ink, color: '#fff',
                          border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
                          fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>Ring &amp; notér</button>
                        <button onClick={() => setOpfoelgning(a.id, 'ikke-noedvendigt')} style={{
                          padding: '8px 12px', background: 'none', color: SoS.inkMuted,
                          border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
                          fontFamily: SoS.sans, fontSize: 12 }}>Ikke nødv.</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}"""

sub(OLD, NEW, "2: match-knap → dagsorden (opfølgninger)")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

# CRLF-fix
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

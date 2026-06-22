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

# 1) matchOpen-state + assignBB
sub(
    "  const [bbDetaljeId, setBbDetaljeId] = React.useState(null);",
    "  const [bbDetaljeId, setBbDetaljeId] = React.useState(null);\n  const [matchOpen, setMatchOpen] = React.useState(null);",
    "1: matchOpen state")
sub(
    "  const deleteAppt = (id) => {\n"
    "    const newList = appointments.filter(a => a.id !== id);\n"
    "    window.SoS_APPOINTMENTS_BUSY = newList;\n"
    "    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);\n"
    "    setAppts(newList);\n"
    "    setSelectedAppt(null);\n"
    "    setApptModal(null);\n"
    "  };",
    "  const deleteAppt = (id) => {\n"
    "    const newList = appointments.filter(a => a.id !== id);\n"
    "    window.SoS_APPOINTMENTS_BUSY = newList;\n"
    "    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);\n"
    "    setAppts(newList);\n"
    "    setSelectedAppt(null);\n"
    "    setApptModal(null);\n"
    "  };\n"
    "  const assignBB = (apptId, bbId) => {\n"
    "    const newList = appointments.map(a => a.id === apptId ? { ...a, brobyggerId: bbId } : a);\n"
    "    window.SoS_APPOINTMENTS_BUSY = newList;\n"
    "    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);\n"
    "    setAppts(newList);\n"
    "  };",
    "2: assignBB")

# 3) View-knap "Bekræft"
sub(
    "            { k: 'liste',    l: 'Liste'    },\n"
    "            { k: 'vagtplan', l: 'Vagtplan' },",
    "            { k: 'liste',    l: 'Liste'    },\n"
    "            { k: 'bekraeft', l: 'Bekræft'  },\n"
    "            { k: 'vagtplan', l: 'Vagtplan' },",
    "3: view-knap Bekræft")

# 4) Bekræft-visning (tre sektioner) — indsættes før månedsvisningen
BLOK = """      {view === 'bekraeft' && (() => {
        const inWeek = filteredWeekAppts.slice().sort((a, b) => (a.date + a.start).localeCompare(b.date + b.start));
        const ikke = inWeek.filter(a => a.status !== 'confirmed' && a.status !== 'gennemfoert' && ['aflyst','afslaaet','brudt'].indexOf(a.status) < 0);
        const bekr = inWeek.filter(a => a.status === 'confirmed');
        const raadig = (() => { try { return JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]'); } catch (e) { return []; } })();
        const ledigePaa = (ds) => aktiveBb.map(b => ({
          b,
          optaget: appointments.some(a => a.brobyggerId === b.id && a.date === ds && a.status === 'confirmed'),
        })).filter(x => raadig.some(r => r.brobyggerId === x.b.id && r.dato === ds));
        const emptyStyle = { textAlign: 'center', padding: '16px 0', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted };
        const linkBtn = { background: SoS.accent + '12', border: `1px solid ${SoS.accent}44`, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.accent, padding: '5px 10px', borderRadius: SoS.r.sm };
        const H = (txt, n, color) => (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '20px 0 10px' }}>
            <div style={{ width: 9, height: 9, borderRadius: 5, background: color }}/>
            <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>{txt}</div>
            <div style={{ fontFamily: SoS.mono, fontSize: 11, color: SoS.inkMuted }}>{n}</div>
          </div>
        );
        return (
          <div>
            {H('Ikke bekræftede aftaler', ikke.length, SoS.amber)}
            {ikke.length === 0 && <div style={emptyStyle}>Ingen ubekræftede aftaler i perioden</div>}
            {ikke.map(a => (
              <div key={a.id} style={{ marginBottom: 6 }}>
                {renderRow(a)}
                <div style={{ marginTop: -2, marginBottom: 8 }}>
                  <button onClick={() => setMatchOpen(matchOpen === a.id ? null : a.id)} style={linkBtn}>
                    {matchOpen === a.id ? 'Skjul ledige brobyggere' : 'Vis ledige brobyggere d. ' + a.date}
                  </button>
                  {matchOpen === a.id && (() => {
                    const cand = ledigePaa(a.date);
                    return (
                      <div style={{ background: SoS.surface, border: `1px solid ${SoS.line}`,
                        borderRadius: SoS.r.sm, padding: '10px 12px', marginTop: 6 }}>
                        {cand.length === 0 && (
                          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
                            Ingen brobyggere har meldt sig ledige denne dag — tjek BB-vagtplan nederst eller forespørg en optaget.
                          </div>
                        )}
                        {cand.map(({ b, optaget }, ci) => (
                          <div key={b.id} style={{ display: 'flex', alignItems: 'center', gap: 10,
                            padding: '7px 0', borderTop: ci > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                            <div style={{ width: 28, height: 28, borderRadius: 14, background: b.bg,
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontFamily: SoS.mono, fontSize: 10, fontWeight: 700, color: '#fff', flexShrink: 0 }}>{b.avatar}</div>
                            <div style={{ flex: 1 }}>
                              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{b.name}</div>
                              <div style={{ fontFamily: SoS.sans, fontSize: 10,
                                color: optaget ? SoS.amber : SoS.green }}>
                                {optaget ? 'Ledig — men har en aftale denne dag' : 'Ledig denne dag'}
                              </div>
                            </div>
                            <button onClick={() => { assignBB(a.id, b.id); setMatchOpen(null); }} style={{
                              padding: '5px 14px', background: a.brobyggerId === b.id ? SoS.green : SoS.ink,
                              color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
                              fontFamily: SoS.sans, fontSize: 12, fontWeight: 600 }}>
                              {a.brobyggerId === b.id ? 'Valgt ✓' : 'Vælg'}
                            </button>
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              </div>
            ))}

            {H('Bekræftede aftaler', bekr.length, SoS.green)}
            {bekr.length === 0 && <div style={emptyStyle}>Ingen bekræftede aftaler i perioden</div>}
            {bekr.map(renderRow)}

            {H('BB-vagtplan', aktiveBb.length + ' brobyggere', SoS.accent)}
            {renderVagtplan()}
          </div>
        );
      })()}

      {view === 'maaned' && (() => {"""

sub("      {view === 'maaned' && (() => {", BLOK, "4: bekræft-visning")

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

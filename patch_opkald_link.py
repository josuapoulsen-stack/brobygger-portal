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

# 1) State + søgeresultater + canSave
sub(
"""const OpkaldLog = ({ onClose }) => {
  const [navn, setNavn] = React.useState('');
  const [tlf,  setTlf]  = React.useState('');
  const [note, setNote] = React.useState('');
  const [saved, setSaved] = React.useState(false);""",
"""const OpkaldLog = ({ onClose }) => {
  const [query, setQuery] = React.useState('');
  const [valgt, setValgt] = React.useState(null);
  const [tlf,  setTlf]  = React.useState('');
  const [note, setNote] = React.useState('');
  const [saved, setSaved] = React.useState(false);
  const lbl = { fontFamily: SoS.sans, fontSize: 11, fontWeight: 600, color: SoS.inkSoft, marginBottom: 5 };

  const resultater = query.trim().length >= 2 ? (() => {
    const ql = query.toLowerCase();
    const qd = query.replace(/\\s/g, '');
    const mns = Object.values(window.SoS_MENNESKER || {}).filter(m =>
      ((m.firstName || '') + ' ' + (m.lastName || '')).toLowerCase().includes(ql) ||
      (m.mobil || '').replace(/\\s/g, '').includes(qd)
    ).slice(0, 5).map(m => ({ kind: 'menneske', id: m.id, navn: ((m.firstName || '') + ' ' + (m.lastName || '')).trim(), tlf: m.mobil || '' }));
    const bbs = (window.SoS_BROBYGGERE || []).filter(b => (b.name || '').toLowerCase().includes(ql))
      .slice(0, 5).map(b => ({ kind: 'brobygger', id: b.id, navn: b.name || '', tlf: b.mobil || b.phone || '' }));
    return [...mns, ...bbs];
  })() : [];

  const canSave = !!valgt && !!note.trim();""",
"1: state + søg")

# 2) handleSave med tilknytning
sub(
"""  const handleSave = () => {
    if (!note.trim()) return;
    const entry = {
      id: 'log-' + Date.now(),
      navn: navn.trim() || 'Ukendt',
      tlf: tlf.trim(),
      note: note.trim(),
      dato: new Date().toISOString().slice(0, 10),
      tid: new Date().toTimeString().slice(0, 5),
    };
    const prev = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]');
    localStorage.setItem('sos_opkald_log', JSON.stringify([entry, ...prev]));
    setSaved(true);
    setTimeout(onClose, 1000);
  };""",
"""  const handleSave = () => {
    if (!canSave) return;
    const entry = {
      id: 'log-' + Date.now(),
      kind: valgt.kind,
      menneskeId:  valgt.kind === 'menneske'  ? valgt.id : null,
      brobyggerId: valgt.kind === 'brobygger' ? valgt.id : null,
      navn: valgt.navn,
      tlf: tlf.trim(),
      note: note.trim(),
      dato: new Date().toISOString().slice(0, 10),
      tid: new Date().toTimeString().slice(0, 5),
    };
    const prev = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]');
    localStorage.setItem('sos_opkald_log', JSON.stringify([entry, ...prev]));
    setSaved(true);
    setTimeout(onClose, 1000);
  };""",
"2: handleSave")

# 3) Navn/tlf-grid → påkrævet søg-og-vælg + telefon
sub(
"""          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>Navn (valgfrit)</div>
              <input value={navn} onChange={e => setNavn(e.target.value)}
                placeholder="f.eks. Erik Hansen" autoFocus
                style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                  borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                  color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
            </div>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>Telefon (valgfrit)</div>
              <input value={tlf} onChange={e => setTlf(e.target.value)}
                placeholder="12 34 56 78" type="tel"
                style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                  borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                  color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
            </div>
          </div>""",
"""          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Tilknyt menneske eller brobygger <span style={{ color: SoS.orange }}>*</span></div>
            {valgt ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 12px',
                border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, background: SoS.surface }}>
                <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 3,
                  background: valgt.kind === 'brobygger' ? SoS.sky + '22' : SoS.orange + '22',
                  color: valgt.kind === 'brobygger' ? SoS.sky : SoS.orange }}>
                  {valgt.kind === 'brobygger' ? 'BROBYGGER' : 'MENNESKE'}
                </span>
                <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{valgt.navn || '—'}</span>
                <button onClick={() => { setValgt(null); setQuery(''); }} style={{ background: 'none', border: 'none',
                  cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>Skift</button>
              </div>
            ) : (
              <div style={{ position: 'relative' }}>
                <input value={query} onChange={e => setQuery(e.target.value)} autoFocus
                  placeholder="Søg navn eller telefon…"
                  style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                    borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
                {resultater.length > 0 && (
                  <div style={{ border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, marginTop: 4, overflow: 'hidden' }}>
                    {resultater.map((r, i) => (
                      <button key={r.kind + r.id} onClick={() => { setValgt(r); setTlf(r.tlf || ''); setQuery(''); }}
                        style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', textAlign: 'left',
                          padding: '8px 12px', border: 'none', borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none',
                          background: '#fff', cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                        <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 3,
                          background: r.kind === 'brobygger' ? SoS.sky + '22' : SoS.orange + '22',
                          color: r.kind === 'brobygger' ? SoS.sky : SoS.orange }}>{r.kind === 'brobygger' ? 'BB' : 'M'}</span>
                        <span style={{ flex: 1 }}>{r.navn}</span>
                        {r.tlf && <span style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted }}>{r.tlf}</span>}
                      </button>
                    ))}
                  </div>
                )}
                {query.trim().length >= 2 && resultater.length === 0 && (
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginTop: 6 }}>
                    Ingen match. Et opkald skal kobles til et menneske eller en brobygger — opret personen via "Ny aftale" først.
                  </div>
                )}
              </div>
            )}
          </div>
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Telefon</div>
            <input value={tlf} onChange={e => setTlf(e.target.value)} placeholder="12 34 56 78" type="tel"
              style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
          </div>""",
"3: søg-og-vælg UI")

# 4) Gem-knap → canSave
sub(
"""          <button onClick={handleSave} disabled={!note.trim()} style={{
            width: '100%', padding: '11px 0',
            background: saved ? SoS.green : note.trim() ? SoS.ink : SoS.lineSoft,
            color: note.trim() ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.sm,
            cursor: note.trim() ? 'pointer' : 'default',
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 700,
            transition: 'background 0.2s' }}>
            {saved ? '✓ Gemt' : 'Gem log'}
          </button>""",
"""          <button onClick={handleSave} disabled={!canSave} style={{
            width: '100%', padding: '11px 0',
            background: saved ? SoS.green : canSave ? SoS.ink : SoS.lineSoft,
            color: canSave ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.sm,
            cursor: canSave ? 'pointer' : 'default',
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 700,
            transition: 'background 0.2s' }}>
            {saved ? '✓ Gemt' : 'Gem log'}
          </button>""",
"4: gem-knap")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

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

# 1) SoS_hqMatch: understøt multi-select (komma-liste) for afløser-mode
sub("""window.SoS_hqMatch = function (hq, scope) {
  if (!scope || scope === 'Alle hovedsæder') return true;
  if (hq === scope) return true;
  var z = (SoS_REFS.zoner || {})[scope];
  return !!(z && z.indexOf(hq) >= 0);
};""",
"""window.SoS_hqMatch = function (hq, scope) {
  if (!scope || scope === 'Alle hovedsæder') return true;
  if (hq === scope) return true;
  if (typeof scope === 'string' && scope.indexOf(',') >= 0) return scope.split(',').map(function (s) { return s.trim(); }).indexOf(hq) >= 0;
  var z = (SoS_REFS.zoner || {})[scope];
  return !!(z && z.indexOf(hq) >= 0);
};""",
"1: hqMatch multi")

# 2) Afløser-state i DesktopView
sub("  const [viewingHq, setViewingHq] = React.useState(canAllHq ? 'Alle hovedsæder' : ownHq);",
    "  const [viewingHq, setViewingHq] = React.useState(canAllHq ? 'Alle hovedsæder' : ownHq);\n"
    "  const [coverHqs, setCoverHqs] = React.useState([]);\n"
    "  const [coverPickerOpen, setCoverPickerOpen] = React.useState(false);\n"
    "  const [coverPick, setCoverPick] = React.useState([]);",
    "2: afløser-state")

# 3) Erstat hq-dropdown med afløser-faner / dropdown + afløser-knap
sub("""              <select value={viewingHq} onChange={e => setViewingHq(e.target.value)} style={{
                padding: '7px 12px', borderRadius: SoS.r.sm,
                background: SoS.surface, border: `1px solid ${SoS.line}`,
                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink,
                cursor: 'pointer',
              }}>
                {canAllHq && <option value="Alle hovedsæder">Alle hovedsæder</option>}
                {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}
              </select>""",
"""              {coverHqs.length > 0 ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
                  <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, color: '#fff',
                    background: SoS.accent, padding: '3px 7px', borderRadius: 4, letterSpacing: 0.5 }}>AFLØSER</span>
                  {[{ k: '__alle__', l: 'Alle valgte (' + coverHqs.length + ')', v: coverHqs.join(', ') }].concat(coverHqs.map(h => ({ k: h, l: h, v: h }))).map(t => {
                    const on = viewingHq === t.v;
                    return (
                      <button key={t.k} onClick={() => setViewingHq(t.v)} style={{
                        padding: '6px 11px', borderRadius: SoS.r.sm, cursor: 'pointer',
                        border: `1px solid ${on ? SoS.accent : SoS.line}`,
                        background: on ? SoS.accent : SoS.surface, color: on ? '#fff' : SoS.inkSoft,
                        fontFamily: SoS.sans, fontSize: 12, fontWeight: on ? 700 : 500 }}>{t.l}</button>
                    );
                  })}
                  <button onClick={() => { setCoverHqs([]); setViewingHq(canAllHq ? 'Alle hovedsæder' : ownHq); }} style={{
                    padding: '6px 10px', borderRadius: SoS.r.sm, cursor: 'pointer', border: `1px solid ${SoS.line}`,
                    background: 'none', color: SoS.inkMuted, fontFamily: SoS.sans, fontSize: 12 }}>Afslut</button>
                </div>
              ) : (
                <React.Fragment>
                  <select value={viewingHq} onChange={e => setViewingHq(e.target.value)} style={{
                    padding: '7px 12px', borderRadius: SoS.r.sm,
                    background: SoS.surface, border: `1px solid ${SoS.line}`,
                    fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink,
                    cursor: 'pointer',
                  }}>
                    {canAllHq && <option value="Alle hovedsæder">Alle hovedsæder</option>}
                    {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}
                  </select>
                  <div style={{ position: 'relative' }}>
                    <button onClick={() => { setCoverPick(SoS_HOVEDSAEDER.indexOf(viewingHq) >= 0 ? [viewingHq] : []); setCoverPickerOpen(o => !o); }} style={{
                      padding: '7px 12px', borderRadius: SoS.r.sm, background: SoS.surface,
                      border: `1px solid ${SoS.line}`, cursor: 'pointer', fontFamily: SoS.sans,
                      fontSize: 12, fontWeight: 600, color: SoS.ink, display: 'flex', alignItems: 'center', gap: 5 }}>
                      Afløser
                    </button>
                    {coverPickerOpen && (
                      <div style={{ position: 'absolute', top: '112%', right: 0, zIndex: 50,
                        background: '#fff', border: `1px solid ${SoS.line}`, borderRadius: SoS.r.md,
                        boxShadow: '0 10px 30px rgba(0,0,0,0.15)', padding: 12, width: 244 }}>
                        <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700, color: SoS.ink, marginBottom: 2 }}>Afløser — vælg hovedsæder</div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 10 }}>Dæk flere hovedsæder og skift mellem dem med faner. Nulstilles når du afslutter.</div>
                        <div style={{ maxHeight: 220, overflowY: 'auto', marginBottom: 10 }}>
                          {SoS_HOVEDSAEDER.map(h => {
                            const on = coverPick.indexOf(h) >= 0;
                            return (
                              <button key={h} onClick={() => setCoverPick(p => on ? p.filter(x => x !== h) : [...p, h])} style={{
                                display: 'flex', alignItems: 'center', gap: 8, width: '100%', textAlign: 'left',
                                padding: '7px 8px', border: 'none', background: on ? SoS.accent + '12' : 'none',
                                borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                                <span style={{ width: 16, height: 16, borderRadius: 4, flexShrink: 0,
                                  border: `1.5px solid ${on ? SoS.accent : SoS.line}`, background: on ? SoS.accent : '#fff',
                                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  {on && <Icon name="check" size={11} color="#fff" weight={3}/>}
                                </span>
                                {h}
                              </button>
                            );
                          })}
                        </div>
                        <button onClick={() => { if (coverPick.length) { setCoverHqs(coverPick); setViewingHq(coverPick.join(', ')); } setCoverPickerOpen(false); }}
                          disabled={!coverPick.length} style={{ width: '100%', padding: '9px 0',
                          background: coverPick.length ? SoS.ink : SoS.lineSoft, color: coverPick.length ? '#fff' : SoS.inkMuted,
                          border: 'none', borderRadius: SoS.r.sm, cursor: coverPick.length ? 'pointer' : 'default',
                          fontFamily: SoS.sans, fontSize: 13, fontWeight: 700 }}>
                          Aktivér afløser ({coverPick.length})
                        </button>
                      </div>
                    )}
                  </div>
                </React.Fragment>
              )}""",
    "3: afløser-faner UI")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

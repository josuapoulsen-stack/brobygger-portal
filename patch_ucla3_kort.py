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

# Fælles kort-JSX (mobil bruger lg-radius; desktop bruger sh())
MOB_CARD = """        {/* Ensomhedsmåling (UCLA-3) */}
        {(() => {
          const u = m.ucla3;
          const latest = u && u.opfoelgninger && u.opfoelgninger.length ? u.opfoelgninger[u.opfoelgninger.length - 1] : null;
          const btn = (txt, kind) => (
            <button onClick={() => setUclaOpen(kind)} style={{ marginTop: 10, padding: '8px 14px',
              background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>{txt}</button>
          );
          return (
            <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16, border: `1px solid ${SoS.lineSoft}` }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
                letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>Ensomhedsmåling (UCLA-3)</div>
              {u && u.optedOut ? (
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Mennesket har fravalgt at svare — bliver ikke spurgt igen.</div>
              ) : !u || !u.baseline ? (
                <div><div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Ingen baseline registreret endnu.</div>{btn('Registrér baseline', 'baseline')}</div>
              ) : (
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                    Baseline: <strong>{u.baseline.sum}</strong> <span style={{ color: SoS.inkMuted }}>({u.baseline.dato})</span>
                    {latest && <> · Seneste: <strong>{latest.sum}</strong> <span style={{ color: SoS.inkMuted }}>({latest.dato})</span></>}
                  </div>
                  {btn('Registrér opfølgning', 'opfoelgning')}
                </div>
              )}
            </div>
          );
        })()}
        {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={() => setRefreshKey(k => k + 1)} />}

        {/* Behov */}"""

DSK_CARD = """                  {stats.antalFolgeskaber} følgeskaber registreret
                </div>
              </div>
            </div>

            {/* Ensomhedsmåling (UCLA-3) */}
            {(() => {
              const u = m.ucla3;
              const latest = u && u.opfoelgninger && u.opfoelgninger.length ? u.opfoelgninger[u.opfoelgninger.length - 1] : null;
              const btn = (txt, kind) => (
                <button onClick={() => setUclaOpen(kind)} style={{ marginTop: 8, padding: '7px 14px',
                  background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>{txt}</button>
              );
              return (
                <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px', border: `1px solid ${SoS.lineSoft}` }}>
                  {sh('Ensomhedsmåling (UCLA-3)')}
                  {u && u.optedOut ? (
                    <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Mennesket har fravalgt at svare — bliver ikke spurgt igen.</div>
                  ) : !u || !u.baseline ? (
                    <div><div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Ingen baseline registreret endnu.</div>{btn('Registrér baseline', 'baseline')}</div>
                  ) : (
                    <div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                        Baseline: <strong>{u.baseline.sum}</strong> <span style={{ color: SoS.inkMuted }}>({u.baseline.dato})</span>
                        {latest && <> · Seneste: <strong>{latest.sum}</strong> <span style={{ color: SoS.inkMuted }}>({latest.dato})</span></>}
                      </div>
                      {btn('Registrér opfølgning', 'opfoelgning')}
                    </div>
                  )}
                </div>
              );
            })()}
            {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={handleSaved} />}

            {/* Behov */}"""

# 3a) Mobil state
sub(
"""  const [tilknytOpen, setTilknytOpen] = React.useState(false);
  const stats       = React.useMemo(() => calcMenneskeStats(m.id), [m.id, refreshKey]);""",
"""  const [tilknytOpen, setTilknytOpen] = React.useState(false);
  const [uclaOpen,    setUclaOpen]    = React.useState(null);
  const stats       = React.useMemo(() => calcMenneskeStats(m.id), [m.id, refreshKey]);""",
"3a: mobil state")

# 3b) Mobil kort
sub(
"""      {activeTab === 0 && (
      <div style={{ padding: '0 16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>

        {/* Behov */}""",
"""      {activeTab === 0 && (
      <div style={{ padding: '0 16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>

""" + MOB_CARD,
"3b: mobil kort")

# 3c) Desktop state
sub(
"""  const [tilknytOpen, setTilknytOpen] = React.useState(false);
  const [localKey,    setLocalKey]    = React.useState(0);""",
"""  const [tilknytOpen, setTilknytOpen] = React.useState(false);
  const [uclaOpen,    setUclaOpen]    = React.useState(null);
  const [localKey,    setLocalKey]    = React.useState(0);""",
"3c: desktop state")

# 3d) Desktop kort
sub(
"""                  {stats.antalFolgeskaber} følgeskaber registreret
                </div>
              </div>
            </div>

            {/* Behov */}""",
DSK_CARD,
"3d: desktop kort")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

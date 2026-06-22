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

# Widget 1 — desktop oversigt
sub(
"""        <DSCard title="Effekt · UCLA-3" subtitle="Selv-rapporteret ensomhed">
          <div style={{ fontFamily: SoS.mono, fontSize: 30, fontWeight: 700,
            color: SoS.ink, letterSpacing: -1 }}>
            −3.3{' '}
            <span style={{ fontSize: 14, color: SoS.inkSoft }}>point gnsn.</span>
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11,
            color: SoS.inkSoft, marginTop: 4 }}>
            Baseret på 62 besvarelser · 3 mdr efter start
          </div>
          <div style={{ display: 'flex', gap: 14, marginTop: 16, alignItems: 'center' }}>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.rose }}>6.4</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 10,
                color: SoS.inkMuted }}>Før start</div>
            </div>
            <svg width="40" height="20" viewBox="0 0 40 20">
              <path d="M4 16 Q20 2 36 10" stroke={SoS.sage} strokeWidth="2"
                fill="none" strokeLinecap="round"/>
              <path d="M32 7 L36 10 L32 13" stroke={SoS.sage} strokeWidth="2"
                fill="none" strokeLinecap="round"/>
            </svg>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.sage }}>3.1</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 10,
                color: SoS.inkMuted }}>Efter 3 mdr</div>
            </div>
          </div>
          <div style={{ marginTop: 14, padding: 10,
            background: SoS.green + '10', borderLeft: `2px solid ${SoS.green}`,
            fontFamily: SoS.sans, fontSize: 11,
            color: SoS.green, lineHeight: 1.5 }}>
            87% rapporterer mindre ensomhed efter 3 måneder.
          </div>
        </DSCard>""",
"""        <DSCard title="Effekt · UCLA-3" subtitle="Selv-rapporteret ensomhed">
          {(() => {
            const _u = window.SoS_ucla3Stats ? window.SoS_ucla3Stats((typeof viewingHq !== 'undefined') ? viewingHq : null) : { hasData: false };
            if (!_u.hasData) return (
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, lineHeight: 1.5 }}>
                Ingen opfølgningsdata endnu. Registrér baseline + opfølgning på menneskene for at se effekt her.
                {_u.nBaseline > 0 && <div style={{ marginTop: 6, fontFamily: SoS.mono, fontSize: 11 }}>{_u.nBaseline} baseline · {_u.optedOut} fravalgt</div>}
              </div>
            );
            return (
              <>
                <div style={{ fontFamily: SoS.mono, fontSize: 30, fontWeight: 700, color: SoS.ink, letterSpacing: -1 }}>
                  {(_u.delta > 0 ? '+' : '−') + Math.abs(_u.delta).toFixed(1)}{' '}
                  <span style={{ fontSize: 14, color: SoS.inkSoft }}>point gnsn.</span>
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 4 }}>
                  Baseret på {_u.nFollow} opfølgninger · svarprocent {_u.svarprocent}%
                </div>
                <div style={{ display: 'flex', gap: 14, marginTop: 16, alignItems: 'center' }}>
                  <div style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.rose }}>{_u.baselineAvg.toFixed(1)}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted }}>Før start</div>
                  </div>
                  <svg width="40" height="20" viewBox="0 0 40 20">
                    <path d="M4 16 Q20 2 36 10" stroke={SoS.sage} strokeWidth="2" fill="none" strokeLinecap="round"/>
                    <path d="M32 7 L36 10 L32 13" stroke={SoS.sage} strokeWidth="2" fill="none" strokeLinecap="round"/>
                  </svg>
                  <div style={{ flex: 1, textAlign: 'center' }}>
                    <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.sage }}>{_u.latestAvg.toFixed(1)}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted }}>Efter opfølgning</div>
                  </div>
                </div>
                <div style={{ marginTop: 14, padding: 10, background: SoS.green + '10', borderLeft: `2px solid ${SoS.green}`,
                  fontFamily: SoS.sans, fontSize: 11, color: SoS.green, lineHeight: 1.5 }}>
                  {_u.pctImproved}% rapporterer mindre ensomhed ved opfølgning.
                </div>
              </>
            );
          })()}
        </DSCard>""",
"1: widget desktop-oversigt")

# Widget 2 — rapport "over tid"
sub(
"""      <DSCard title="Effekt · UCLA-3 over tid">
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 160 }}>
          {[6.4, 6.1, 5.6, 5.1, 4.6, 4.2, 3.8, 3.5, 3.3, 3.2, 3.1, 3.1].map((v, i) => (
            <div key={i} style={{ flex: 1, display: 'flex',
              flexDirection: 'column', alignItems: 'center', gap: 6 }}>
              <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', width: '100%' }}>
                <div style={{ width: '100%', height: `${(v/7) * 100}%`,
                  background: `linear-gradient(180deg, ${SoS.sage}, ${SoS.sageSoft})`,
                  borderRadius: '3px 3px 0 0' }}/>
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 9, color: SoS.inkMuted }}>{i}m</div>
            </div>
          ))}
        </div>
      </DSCard>""",
"""      <DSCard title="Effekt · UCLA-3">
        {(() => {
          const _u = window.SoS_ucla3Stats ? window.SoS_ucla3Stats(viewingHq) : { hasData: false };
          if (!_u.hasData) return (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, lineHeight: 1.5 }}>
              Ingen opfølgningsdata endnu. Registrér baseline + opfølgning på menneskene{_u.nBaseline > 0 ? ' (' + _u.nBaseline + ' baseline, ' + _u.optedOut + ' fravalgt)' : ''}.
            </div>
          );
          const bars = [['Baseline', _u.baselineAvg, SoS.rose], ['Opfølgning', _u.latestAvg, SoS.sage]];
          return (
            <div>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 24, height: 140 }}>
                {bars.map(([l, v, col]) => (
                  <div key={l} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                    <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', width: '55%' }}>
                      <div style={{ width: '100%', height: `${(v / 9) * 100}%`, background: col, borderRadius: '4px 4px 0 0' }}/>
                    </div>
                    <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 600, color: SoS.ink }}>{v.toFixed(1)}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>{l}</div>
                  </div>
                ))}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 10, lineHeight: 1.5 }}>
                {_u.nFollow} mennesker med opfølgning · {_u.pctImproved}% forbedret · svarprocent {_u.svarprocent}% · {_u.optedOut} fravalgt. Lavere score = mindre ensomhed (skala 3–9).
              </div>
            </div>
          );
        })()}
      </DSCard>""",
"2: widget rapport")

# Widget 3 — mobil effekt
sub(
"""        <div style={{ padding: '16px 14px' }}>
          <div style={{ fontFamily: SoS.mono, fontSize: 26, fontWeight: 700,
            color: SoS.ink, letterSpacing: -1, lineHeight: 1, marginBottom: 6 }}>
            87%
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
            color: SoS.ink, marginBottom: 8 }}>
            føler sig mindre ensomme efter 3 måneder
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
            Baseret på 62 besvarelser (UCLA-3). Snit før: 6.4 · efter: 3.1.
          </div>
        </div>""",
"""        <div style={{ padding: '16px 14px' }}>
          {(() => {
            const _u = window.SoS_ucla3Stats ? window.SoS_ucla3Stats(null) : { hasData: false };
            if (!_u.hasData) return (
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.5 }}>
                Ingen opfølgningsdata endnu — registrér baseline + opfølgning på menneskene.
              </div>
            );
            return (
              <>
                <div style={{ fontFamily: SoS.mono, fontSize: 26, fontWeight: 700, color: SoS.ink, letterSpacing: -1, lineHeight: 1, marginBottom: 6 }}>{_u.pctImproved}%</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink, marginBottom: 8 }}>føler sig mindre ensomme ved opfølgning</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>Baseret på {_u.nFollow} opfølgninger (UCLA-3). Snit før: {_u.baselineAvg.toFixed(1)} · efter: {_u.latestAvg.toFixed(1)}.</div>
              </>
            );
          })()}
        </div>""",
"3: widget mobil")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

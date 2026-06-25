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

# 1) Datalag: henvendelser pr. menneske + seed + helper
sub(
"""      opfoelgninger: s.opf != null ? [{ ...mk(s.opf, '2026-06-15'), label: '3 mdr' }] : [],
    };
  });
})();
""",
"""      opfoelgninger: s.opf != null ? [{ ...mk(s.opf, '2026-06-15'), label: '3 mdr' }] : [],
    };
  });
})();

// ── Henvendelser (hvem tog kontakt — kan være flere pr. forløb) ──────────────
const _KILDE_TIL_HENVENDER = { selv: 'Personen selv', kommune: 'Kommune', hospital: 'Hospital', region: 'Region', 'paarørende': 'Pårørende', paaroerende: 'Pårørende', laege: 'Almen praksis', org: 'Anden NGO', andet: 'Andet', ukendt: 'Andet' };
(function () {
  Object.values(window.SoS_MENNESKER || {}).forEach(m => {
    if (m.henvendelser && m.henvendelser.length) return;
    m.henvendelser = [{ id: 'h-' + m.id + '-1', type: _KILDE_TIL_HENVENDER[m.kilde] || 'Andet', navn: '', dato: m.startedAt || '2026-01-01', note: 'Førstegangshenvendelse' }];
  });
  const tilfoej = (id, e) => { const m = (window.SoS_MENNESKER || {})[id]; if (m && m.henvendelser && !m.henvendelser.some(h => h.id === e.id)) m.henvendelser.push(e); };
  tilfoej('b-2', { id: 'h-b-2-2', type: 'Personen selv', navn: '', dato: '2026-03-02', note: 'Ringede selv ind ifm. ny brobygning' });
  tilfoej('b-5', { id: 'h-b-5-2', type: 'Pårørende', navn: 'Datter', dato: '2026-04-10', note: 'Datter henvendte sig om følgeskab' });
})();
window.SoS_henvendelseStats = function (viewingHq) {
  const mns = Object.values(window.SoS_MENNESKER || {}).filter(m => window.SoS_hqMatch(m.hq, viewingHq));
  const withH = mns.filter(m => m.henvendelser && m.henvendelser.length);
  const foerste = {}, alle = {};
  let selvFoerste = 0, total = 0;
  withH.forEach(m => {
    const sorted = m.henvendelser.slice().sort((a, b) => (a.dato || '').localeCompare(b.dato || ''));
    const f = sorted[0];
    foerste[f.type] = (foerste[f.type] || 0) + 1;
    if (f.type === 'Personen selv') selvFoerste++;
    m.henvendelser.forEach(h => { alle[h.type] = (alle[h.type] || 0) + 1; total++; });
  });
  return {
    antalForloeb: withH.length, foerste, alle, total, selvFoerste,
    lavtaerskelPct: withH.length ? Math.round(selvFoerste / withH.length * 100) : 0,
    snitPerForloeb: withH.length ? (total / withH.length) : 0,
  };
};
""",
"1: henvendelse-datalag")

# 2) Rapport: Førstegangshenvendelse-kort (lavtærskel-indikator)
sub(
"""            </DSCard>
          </div>

          {/* Årsagskoder + køn */}""",
"""            </DSCard>
          </div>

          {(() => {
            const _h = window.SoS_henvendelseStats ? window.SoS_henvendelseStats(viewingHq) : null;
            if (!_h || _h.antalForloeb === 0) return null;
            const ents = Object.entries(_h.foerste).sort((a, b) => b[1] - a[1]);
            return (
              <DSCard title="Førstegangshenvendelse" subtitle={_h.antalForloeb + ' forløb · hvem tog først kontakt'}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
                  <div style={{ fontFamily: SoS.mono, fontSize: 30, fontWeight: 700, color: SoS.sage, letterSpacing: -1 }}>{_h.lavtaerskelPct}%</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>henvender sig selv først</div>
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 14, lineHeight: 1.5 }}>
                  Høj andel selv-henvendelser indikerer et lavtærskel-program — let for det enkelte menneske selv at tage kontakt. Gns. {_h.snitPerForloeb.toFixed(1)} henvendelser pr. forløb.
                </div>
                {ents.map(([t, v]) => {
                  const pct = Math.round(v / _h.antalForloeb * 100);
                  const isSelv = t === 'Personen selv';
                  return (
                    <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <div style={{ width: 130, fontFamily: SoS.sans, fontSize: 11, color: SoS.ink, fontWeight: isSelv ? 700 : 400 }}>{t}</div>
                      <div style={{ flex: 1, height: 6, background: SoS.lineSoft, borderRadius: 3, overflow: 'hidden' }}>
                        <div style={{ width: pct + '%', height: '100%', background: isSelv ? SoS.sage : SoS.sky, borderRadius: 3 }}/>
                      </div>
                      <div style={{ width: 52, textAlign: 'right', fontFamily: SoS.mono, fontSize: 11, fontWeight: 600, color: SoS.inkMuted }}>{v} · {pct}%</div>
                    </div>
                  );
                })}
              </DSCard>
            );
          })()}

          {/* Årsagskoder + køn */}""",
"2: førstegangshenvender-kort")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

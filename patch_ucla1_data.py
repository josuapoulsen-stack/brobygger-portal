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

sub(
"""  window.SoS_STORE = { save, load, clear, hydrate };
  hydrate();
})();
""",
"""  window.SoS_STORE = { save, load, clear, hydrate };
  hydrate();
})();

// ── UCLA-3 (ensomhedsmåling) ────────────────────────────────────────────────
// Måles KUN på mennesket (borgeren) — aldrig medarbejdere/brobyggere.
// Rådgiver taster under samtalen. Mennesket kan fravælge; fravalgt baseline = vises aldrig igen.
const UCLA3_SPM = [
  'Hvor ofte føler du, at du mangler nogen at være sammen med?',
  'Hvor ofte føler du dig udenfor?',
  'Hvor ofte føler du dig isoleret fra andre?',
];
const UCLA3_SVAR = [
  { v: 1, l: 'Næsten aldrig' },
  { v: 2, l: 'En gang imellem' },
  { v: 3, l: 'Ofte' },
];
window.SoS_ucla3Stats = function (viewingHq) {
  const sc = !!(viewingHq && viewingHq !== 'Alle hovedsæder');
  const mns = Object.values(window.SoS_MENNESKER || {}).filter(m => !sc || m.hq === viewingHq);
  const avg = arr => arr.length ? arr.reduce((s, x) => s + x, 0) / arr.length : 0;
  const latest = u => (u && u.opfoelgninger && u.opfoelgninger.length) ? u.opfoelgninger[u.opfoelgninger.length - 1] : null;
  const withBaseline = mns.filter(m => m.ucla3 && m.ucla3.baseline);
  const withFollow = withBaseline.filter(m => latest(m.ucla3));
  const optedOut = mns.filter(m => m.ucla3 && m.ucla3.optedOut).length;
  const baselineAvg = avg(withFollow.map(m => m.ucla3.baseline.sum));
  const latestAvg = avg(withFollow.map(m => latest(m.ucla3).sum));
  const improved = withFollow.filter(m => latest(m.ucla3).sum < m.ucla3.baseline.sum).length;
  return {
    eligible: mns.length,
    nBaseline: withBaseline.length,
    nFollow: withFollow.length,
    optedOut,
    baselineAvg, latestAvg,
    delta: latestAvg - baselineAvg,
    pctImproved: withFollow.length ? Math.round(improved / withFollow.length * 100) : 0,
    svarprocent: mns.length ? Math.round(withBaseline.length / mns.length * 100) : 0,
    hasData: withFollow.length > 0,
  };
};
// Demo-data, så Effekt-widgets viser ægte beregnede tal (idempotent — rører ikke eksisterende)
(function () {
  const seed = {
    'b-1': { baseline: 7, opf: 4 }, 'b-2': { baseline: 8, opf: 5 },
    'b-4': { baseline: 6, opf: 5 }, 'b-5': { baseline: 9, opf: 6 },
    'b-6': { baseline: 7 }, 'b-3': { optOut: true },
  };
  Object.keys(seed).forEach(id => {
    const m = (window.SoS_MENNESKER || {})[id]; if (!m || m.ucla3) return;
    const s = seed[id];
    if (s.optOut) { m.ucla3 = { optedOut: true, baseline: null, opfoelgninger: [] }; return; }
    const mk = (sum, dato) => ({ q1: 0, q2: 0, q3: 0, sum, dato });
    m.ucla3 = {
      optedOut: false,
      baseline: mk(s.baseline, '2026-03-15'),
      opfoelgninger: s.opf != null ? [{ ...mk(s.opf, '2026-06-15'), label: '3 mdr' }] : [],
    };
  });
})();
""",
"1: UCLA-3 datalag")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

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

# A) Beregn mine ledige dage + sæt til hurtig opslag
sub(
"""  myRaadig.forEach(r => {
    (shiftsByDate[r.dato] ||= []).push(
      { id: r.id, date: r.dato, start: 'Ledig', end: '', _raadig: true });
  });""",
"""  myRaadig.forEach(r => {
    (shiftsByDate[r.dato] ||= []).push(
      { id: r.id, date: r.dato, start: 'Ledig', end: '', _raadig: true });
  });
  const raadigSet = new Set(myRaadig.map(r => r.dato));
  const _todayIso = new Date().toISOString().slice(0, 10);
  const mineLedigeDatoer = Array.from(raadigSet).filter(dd => dd >= _todayIso).sort();
  const fmtRaadigChip = (iso) => {
    const dt = new Date(iso);
    const dag = ['søn', 'man', 'tir', 'ons', 'tor', 'fre', 'lør'][dt.getDay()];
    const mnd = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'][dt.getMonth()];
    return dag + '. ' + dt.getDate() + '. ' + mnd;
  };""",
"A: beregning")

# B) Grøn baggrund på rådige dage i gittet
sub(
"              background: isSel ? SoS.orange : 'transparent',",
"              background: isSel ? SoS.orange : (raadigSet.has(iso) ? SoS.sageSoft + '66' : 'transparent'),",
"B: celle-baggrund")

# C) "Mine ledige dage"-liste efter legenden
sub(
"""          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Rådighed</div>
        </div>
      </div>

      {/* Selected day details */}""",
"""          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Rådighed</div>
        </div>
      </div>

      {/* Mine ledige dage — hurtigt overblik */}
      {mineLedigeDatoer.length > 0 && (
        <div style={{ padding: '0 20px 16px' }}>
          <SectionHead title={'Mine ledige dage · ' + mineLedigeDatoer.length} />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {mineLedigeDatoer.map(dd => (
              <button key={dd} onClick={() => { setSelected(dd); setMonth(new Date(dd.slice(0, 7) + '-01')); }} style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '7px 12px',
                background: SoS.sageSoft + '66', border: `1px solid ${SoS.sage}55`, borderRadius: 999,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12.5, fontWeight: 600, color: SoS.ink }}>
                <span style={{ width: 7, height: 7, borderRadius: 4, background: SoS.sage, flexShrink: 0 }}/>
                {fmtRaadigChip(dd)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Selected day details */}""",
"C: mine-ledige-dage liste")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

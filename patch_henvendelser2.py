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

# 1) HenvendelserKort-komponent før UCLA3Modal
COMP = """const HenvendelserKort = ({ menneske, onSaved }) => {
  const TYPER = (window.SoS_REFS && SoS_REFS.henvendere) || ['Personen selv', 'Kommune', 'Region', 'Pårørende', 'Almen praksis', 'Hospital', 'Tandlæge', 'Anden NGO', 'Andet'];
  const [addOpen, setAddOpen] = React.useState(false);
  const [type, setType] = React.useState(TYPER[0]);
  const [navn, setNavn] = React.useState('');
  const [dato, setDato] = React.useState(new Date().toISOString().slice(0, 10));
  const [, force] = React.useReducer(x => x + 1, 0);
  const liste = (menneske.henvendelser || []).slice().sort((a, b) => (a.dato || '').localeCompare(b.dato || ''));
  const inp = { width: '100%', padding: '8px 10px', border: '1px solid ' + SoS.line, borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none', boxSizing: 'border-box', background: '#fff' };
  const gem = () => {
    const m = (window.SoS_MENNESKER || {})[menneske.id]; if (!m) return;
    const arr = (m.henvendelser || []).slice();
    arr.push({ id: 'h-' + menneske.id + '-' + Date.now(), type, navn: navn.trim(), dato, note: '' });
    m.henvendelser = arr;
    if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER);
    setAddOpen(false); setNavn(''); force(); if (onSaved) onSaved();
  };
  return (
    <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px', border: '1px solid ' + SoS.lineSoft }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
        <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, color: SoS.inkMuted, letterSpacing: 0.9, textTransform: 'uppercase' }}>Henvendelser ({liste.length})</div>
        {!addOpen && <button onClick={() => setAddOpen(true)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.accent }}>+ Tilføj</button>}
      </div>
      {liste.length === 0 && !addOpen && <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>Ingen henvendelser registreret.</div>}
      {liste.map((h, i) => (
        <div key={h.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 0', borderTop: i > 0 ? '1px solid ' + SoS.lineSoft : 'none' }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
              {h.type}{h.navn ? ' · ' + h.navn : ''}
              {i === 0 && <span style={{ marginLeft: 8, fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, color: SoS.sage, background: SoS.sageSoft, padding: '2px 6px', borderRadius: 3 }}>FØRSTE</span>}
            </div>
            <div style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted, marginTop: 1 }}>{h.dato}{h.note ? ' · ' + h.note : ''}</div>
          </div>
        </div>
      ))}
      {addOpen && (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid ' + SoS.lineSoft }}>
          <select value={type} onChange={e => setType(e.target.value)} style={{ ...inp, marginBottom: 8 }}>
            {TYPER.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <input value={navn} onChange={e => setNavn(e.target.value)} placeholder="Navn (valgfrit — fx pårørende/instans)" style={{ ...inp, marginBottom: 8 }}/>
          <input type="date" value={dato} onChange={e => setDato(e.target.value)} style={{ ...inp, marginBottom: 10 }}/>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={gem} style={{ flex: 1, padding: '9px 0', background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13, fontWeight: 700 }}>Tilføj henvendelse</button>
            <button onClick={() => setAddOpen(false)} style={{ padding: '9px 14px', background: 'none', border: '1px solid ' + SoS.line, borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Annuller</button>
          </div>
        </div>
      )}
    </div>
  );
};

const UCLA3Modal = ({ menneske, kind, onClose, onSaved }) => {"""

sub("const UCLA3Modal = ({ menneske, kind, onClose, onSaved }) => {", COMP, "1: HenvendelserKort komponent")

# 2) Render i mobil menneske-detalje (efter UCLA-modal)
sub(
"        {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={() => setRefreshKey(k => k + 1)} />}",
"        {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={() => setRefreshKey(k => k + 1)} />}\n"
"        <HenvendelserKort menneske={m} onSaved={() => setRefreshKey(k => k + 1)} />",
"2: mobil render")

# 3) Render i desktop menneske-detalje (efter UCLA-modal)
sub(
"            {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={handleSaved} />}",
"            {uclaOpen && <UCLA3Modal menneske={m} kind={uclaOpen} onClose={() => setUclaOpen(null)} onSaved={handleSaved} />}\n"
"            <HenvendelserKort menneske={m} onSaved={handleSaved} />",
"3: desktop render")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

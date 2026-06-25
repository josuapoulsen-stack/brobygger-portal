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

# 1) Edit/slet-state + handlers efter gem()
sub(
"""    setAddOpen(false); setNavn(''); force(); if (onSaved) onSaved();
  };
  return (
    <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px', border: '1px solid ' + SoS.lineSoft }}>""",
"""    setAddOpen(false); setNavn(''); force(); if (onSaved) onSaved();
  };
  const [editId, setEditId] = React.useState(null);
  const [eType, setEType] = React.useState('');
  const [eNavn, setENavn] = React.useState('');
  const [eDato, setEDato] = React.useState('');
  const startEdit = (h) => { setAddOpen(false); setEditId(h.id); setEType(h.type); setENavn(h.navn || ''); setEDato(h.dato || ''); };
  const gemEdit = () => {
    const m = (window.SoS_MENNESKER || {})[menneske.id]; if (!m) return;
    m.henvendelser = (m.henvendelser || []).map(x => x.id === editId ? { ...x, type: eType, navn: eNavn.trim(), dato: eDato } : x);
    if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER);
    setEditId(null); force(); if (onSaved) onSaved();
  };
  const slet = (id) => {
    if (!window.confirm('Slet denne henvendelse?')) return;
    const m = (window.SoS_MENNESKER || {})[menneske.id]; if (!m) return;
    m.henvendelser = (m.henvendelser || []).filter(x => x.id !== id);
    if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER);
    setEditId(null); force(); if (onSaved) onSaved();
  };
  return (
    <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px', border: '1px solid ' + SoS.lineSoft }}>""",
"1: edit/slet state+handlers")

# 2) Erstat række-map med edit-mode + Rediger/Slet
sub(
"""      {liste.map((h, i) => (
        <div key={h.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 0', borderTop: i > 0 ? '1px solid ' + SoS.lineSoft : 'none' }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
              {h.type}{h.navn ? ' · ' + h.navn : ''}
              {i === 0 && <span style={{ marginLeft: 8, fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, color: SoS.sage, background: SoS.sageSoft, padding: '2px 6px', borderRadius: 3 }}>FØRSTE</span>}
            </div>
            <div style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted, marginTop: 1 }}>{h.dato}{h.note ? ' · ' + h.note : ''}</div>
          </div>
        </div>
      ))}""",
"""      {liste.map((h, i) => {
        if (editId === h.id) return (
          <div key={h.id} style={{ padding: '8px 0', borderTop: i > 0 ? '1px solid ' + SoS.lineSoft : 'none' }}>
            <select value={eType} onChange={e => setEType(e.target.value)} style={{ ...inp, marginBottom: 6 }}>
              {TYPER.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <input value={eNavn} onChange={e => setENavn(e.target.value)} placeholder="Navn (valgfrit)" style={{ ...inp, marginBottom: 6 }}/>
            <input type="date" value={eDato} onChange={e => setEDato(e.target.value)} style={{ ...inp, marginBottom: 8 }}/>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={gemEdit} style={{ flex: 1, padding: '8px 0', background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>Gem</button>
              <button onClick={() => setEditId(null)} style={{ padding: '8px 12px', background: 'none', border: '1px solid ' + SoS.line, borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Annuller</button>
            </div>
          </div>
        );
        return (
          <div key={h.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 0', borderTop: i > 0 ? '1px solid ' + SoS.lineSoft : 'none' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                {h.type}{h.navn ? ' · ' + h.navn : ''}
                {i === 0 && <span style={{ marginLeft: 8, fontFamily: SoS.mono, fontSize: 9, fontWeight: 700, color: SoS.sage, background: SoS.sageSoft, padding: '2px 6px', borderRadius: 3 }}>FØRSTE</span>}
              </div>
              <div style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted, marginTop: 1 }}>{h.dato}{h.note ? ' · ' + h.note : ''}</div>
            </div>
            <button onClick={() => startEdit(h)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, padding: '2px 4px' }}>Rediger</button>
            <button onClick={() => slet(h.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: SoS.sans, fontSize: 11, color: SoS.rose, padding: '2px 4px' }}>Slet</button>
          </div>
        );
      })}""",
"2: række-map edit/slet")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

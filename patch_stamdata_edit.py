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

# ── 1) SoS_REFS-builder: tilføj farver-map + anvend på SoS_TYPER ──
sub(
"""const SoS_REFS = (() => {
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem('sos_refs') || '{}'); } catch (e) { stored = {}; }
  const merged = {};
  Object.keys(SoS_REFS_SEED).forEach(k => {
    merged[k] = Array.isArray(stored[k]) ? stored[k] : SoS_REFS_SEED[k].slice();
  });
  return merged;
})();
const saveRefs = () => { try { localStorage.setItem('sos_refs', JSON.stringify(SoS_REFS)); } catch (e) {} };
window.SoS_REFS = SoS_REFS;
window.SoS_saveRefs = saveRefs;""",
"""const SoS_REFS = (() => {
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem('sos_refs') || '{}'); } catch (e) { stored = {}; }
  const merged = {};
  Object.keys(SoS_REFS_SEED).forEach(k => {
    merged[k] = Array.isArray(stored[k]) ? stored[k] : SoS_REFS_SEED[k].slice();
  });
  merged.farver = (stored.farver && typeof stored.farver === 'object') ? stored.farver : {};
  [['Social', 'social'], ['Forening', 'forening'], ['Sundhed', 'sundhed']].forEach(([n, key]) => {
    const fk = 'brobygningstyper|' + n;
    if (!merged.farver[fk] && SoS_TYPER[key]) merged.farver[fk] = SoS_TYPER[key].color;
  });
  return merged;
})();
const saveRefs = () => { try { localStorage.setItem('sos_refs', JSON.stringify(SoS_REFS)); } catch (e) {} };
window.SoS_REFS = SoS_REFS;
window.SoS_saveRefs = saveRefs;
// Anvend gemte indsatstype-farver på SoS_TYPER, så de slår igennem i hele systemet
try {
  [['Social', 'social'], ['Forening', 'forening'], ['Sundhed', 'sundhed']].forEach(([n, key]) => {
    const cc = SoS_REFS.farver['brobygningstyper|' + n];
    if (cc && SoS_TYPER[key]) SoS_TYPER[key].color = cc;
  });
} catch (e) {}""",
"1: builder farver")

# ── 2) State i DesktopStamdata ──
sub(
"  const [, force]       = React.useReducer(x => x + 1, 0);",
"  const [, force]       = React.useReducer(x => x + 1, 0);\n"
"  const [editIdx, setEditIdx] = React.useState(-1);\n"
"  const [editVal, setEditVal] = React.useState('');",
"2: state")

# ── 3) Hjælpere efter slet ──
sub(
"  const slet = (i) => { liste.splice(i, 1); gem(); };",
"""  const slet = (i) => { liste.splice(i, 1); gem(); };

  const brugFelter = {
    brobygningstyper: ['brobygningstype'], aftaletyper: ['aftaletype'], henvendere: ['henvender'],
    modtagere: ['modtagerType'], samarbejdspartnere: ['samarbejdspartner'], finansieringskilder: ['finansiering'],
    aflystAf: ['aflystAf'], aflysningsaarsager: ['aflysningsAarsag'], transportplaner: ['transportplan'],
  };
  const _appts = () => window.SoS_APPOINTMENTS_BUSY || [];
  const _mns   = () => window.SoS_MENNESKER || {};
  const taelBrug = (k, val) => {
    let n = 0;
    (brugFelter[k] || []).forEach(f => _appts().forEach(a => { if (a[f] === val) n++; }));
    if (k === 'afdelinger') {
      Object.values(_mns()).forEach(m => { if (m.afdeling === val) n++; });
      _appts().forEach(a => { if (a.afdeling === val) n++; });
    }
    if (k === 'hovedsaeder') {
      Object.values(_mns()).forEach(m => { if (m.hq === val) n++; });
      (SoS_REFS.afdelinger || []).forEach(a => { if (a.hovedsaede === val) n++; });
    }
    return n;
  };
  const cascade = (k, oldV, newV) => {
    const felter = brugFelter[k] || [];
    if (felter.length) {
      _appts().forEach(a => felter.forEach(f => { if (a[f] === oldV) a[f] = newV; }));
      if (window.SoS_STORE) window.SoS_STORE.save('appointments', _appts());
    }
    if (k === 'afdelinger' || k === 'hovedsaeder') {
      const field = k === 'afdelinger' ? 'afdeling' : 'hq';
      const mns = _mns(); Object.values(mns).forEach(m => { if (m[field] === oldV) m[field] = newV; });
      if (window.SoS_STORE) window.SoS_STORE.save('mennesker', mns);
      if (k === 'afdelinger') { _appts().forEach(a => { if (a.afdeling === oldV) a.afdeling = newV; }); if (window.SoS_STORE) window.SoS_STORE.save('appointments', _appts()); }
      if (k === 'hovedsaeder') { (SoS_REFS.afdelinger || []).forEach(a => { if (a.hovedsaede === oldV) a.hovedsaede = newV; }); }
    }
  };
  const farveKey = (navn) => kat + '|' + navn;
  const farveOf  = (navn) => SoS_REFS.farver ? (SoS_REFS.farver[farveKey(navn)] || null) : null;
  const _typeKey = { 'Social': 'social', 'Forening': 'forening', 'Sundhed': 'sundhed' };
  const saetFarve = (navn, cc) => {
    if (!SoS_REFS.farver) SoS_REFS.farver = {};
    SoS_REFS.farver[farveKey(navn)] = cc;
    if (kat === 'brobygningstyper' && _typeKey[navn] && SoS_TYPER[_typeKey[navn]]) SoS_TYPER[_typeKey[navn]].color = cc;
    gem();
  };
  const startEdit = (i, navn) => { setEditIdx(i); setEditVal(navn); };
  const gemEdit = (i) => {
    const nyV = editVal.trim(); if (!nyV) return;
    const gammel = meta.obj ? liste[i].navn : liste[i];
    if (nyV !== gammel) {
      if (liste.some((it, j) => j !== i && (meta.obj ? it.navn : it) === nyV)) { setEditIdx(-1); setEditVal(''); return; }
      if (SoS_REFS.farver && SoS_REFS.farver[kat + '|' + gammel] != null) {
        SoS_REFS.farver[kat + '|' + nyV] = SoS_REFS.farver[kat + '|' + gammel];
        delete SoS_REFS.farver[kat + '|' + gammel];
      }
      if (meta.obj) liste[i] = { ...liste[i], navn: nyV }; else liste[i] = nyV;
      cascade(kat, gammel, nyV);
    }
    setEditIdx(-1); setEditVal(''); gem();
  };""",
"3: hjælpere")

# ── 4) Beskrivelsestekst ──
sub(
"            Tilføj, eller slet poster. Ændringer gemmes med det samme og bruges i hele systemet.",
"            Tilføj, omdøb, giv farve eller slet poster. Ændringer gemmes med det samme og bruges i hele systemet.",
"4: beskrivelse")

# ── 5) Liste-rækker: farve + brugt-badge + redigér + advarsel ──
sub(
"""          {liste.map((item, i) => {
            const navn = meta.obj ? item.navn : item;
            const sub2 = meta.obj ? item.hovedsaede : null;
            return (
              <div key={i} style={{ padding: '10px 18px', display: 'flex', alignItems: 'center', gap: 10,
                borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                <div style={{ flex: 1 }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>{navn}</span>
                  {sub2 && <span style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted,
                    marginLeft: 8 }}>{sub2}</span>}
                </div>
                <button onClick={() => slet(i)} style={{ padding: '5px 10px', background: 'none',
                  border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12, color: SoS.rose }}>Slet</button>
              </div>
            );
          })}""",
"""          {liste.map((item, i) => {
            const navn = meta.obj ? item.navn : item;
            const sub2 = meta.obj ? item.hovedsaede : null;
            const erRedigering = editIdx === i;
            const brug = taelBrug(kat, navn);
            const aendret = editVal.trim() && editVal.trim() !== navn;
            const farve = farveOf(navn);
            return (
              <div key={i} style={{ padding: '10px 18px',
                borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <label title="Skift farve" style={{ position: 'relative', width: 22, height: 22, flexShrink: 0,
                    borderRadius: 6, cursor: 'pointer', border: `1px solid ${SoS.line}`,
                    background: farve || '#E9E4DC', display: 'inline-block' }}>
                    <input type="color" value={farve || '#888888'}
                      onChange={e => saetFarve(navn, e.target.value)}
                      style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%', height: '100%' }}/>
                  </label>
                  {erRedigering ? (
                    <input autoFocus value={editVal} onChange={e => setEditVal(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') gemEdit(i); if (e.key === 'Escape') { setEditIdx(-1); setEditVal(''); } }}
                      style={{ flex: 1, padding: '7px 10px', border: `1px solid ${SoS.accent}`,
                        borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none' }}/>
                  ) : (
                    <div style={{ flex: 1 }}>
                      <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>{navn}</span>
                      {sub2 && <span style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted, marginLeft: 8 }}>{sub2}</span>}
                      {brug > 0 && <span style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted, marginLeft: 8 }}>· brugt {brug}×</span>}
                    </div>
                  )}
                  {erRedigering ? (
                    <React.Fragment>
                      <button onClick={() => gemEdit(i)} style={{ padding: '5px 12px',
                        background: (aendret && brug > 0) ? SoS.orange : SoS.ink, color: '#fff', border: 'none',
                        borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>
                        {(aendret && brug > 0) ? 'Gem alligevel' : 'Gem'}
                      </button>
                      <button onClick={() => { setEditIdx(-1); setEditVal(''); }} style={{ padding: '5px 10px',
                        background: 'none', border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                        cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Annuller</button>
                    </React.Fragment>
                  ) : (
                    <React.Fragment>
                      <button onClick={() => startEdit(i, navn)} style={{ padding: '5px 10px', background: 'none',
                        border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
                        fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Rediger</button>
                      <button onClick={() => slet(i)} style={{ padding: '5px 10px', background: 'none',
                        border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm, cursor: 'pointer',
                        fontFamily: SoS.sans, fontSize: 12, color: SoS.rose }}>Slet</button>
                    </React.Fragment>
                  )}
                </div>
                {erRedigering && aendret && brug > 0 && (
                  <div style={{ marginTop: 8, marginLeft: 32, padding: '8px 10px',
                    background: SoS.orange + '14', border: `1px solid ${SoS.orange}44`,
                    borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 11.5, color: '#9A4A12', lineHeight: 1.45 }}>
                    ⚠ Ændrer {brug} allerede noteret{brug === 1 ? '' : 'e'} registrering{brug === 1 ? '' : 'er'}. Gør det kun, hvis posten stadig giver mening bagefter — ellers mister de gamle data deres betydning.
                  </div>
                )}
              </div>
            );
          })}""",
"5: liste-rækker")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

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

# 1) State + typer + filtreret søgning
sub(
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
"""const OpkaldLog = ({ onClose }) => {
  const OPKALD_TYPER = [
    { id: 'samtale_menneske',  label: 'Samtale med menneske',     kind: 'menneske',  farve: SoS.orange },
    { id: 'samtale_brobygger', label: 'Samtale med brobygger',    kind: 'brobygger', farve: SoS.sky },
    { id: 'ringeopgave',       label: 'Ringeopgave for menneske', kind: 'menneske',  farve: SoS.sage },
  ];
  const RINGE_UNDER = [
    { id: 'bestil_tid',       label: 'Bestiller tid' },
    { id: 'forny_recept',     label: 'Fornyer recept' },
    { id: 'kontakt_forening', label: 'Kontakt til forening' },
    { id: 'andet',            label: 'Andet' },
  ];
  const [type, setType]   = React.useState('samtale_menneske');
  const [underType, setUnderType] = React.useState('bestil_tid');
  const [query, setQuery] = React.useState('');
  const [valgt, setValgt] = React.useState(null);
  const [tlf,  setTlf]  = React.useState('');
  const [note, setNote] = React.useState('');
  const [saved, setSaved] = React.useState(false);
  const lbl = { fontFamily: SoS.sans, fontSize: 11, fontWeight: 600, color: SoS.inkSoft, marginBottom: 5 };

  const typeMeta = OPKALD_TYPER.find(t => t.id === type) || OPKALD_TYPER[0];
  const kraevetKind = typeMeta.kind;
  const erRinge = type === 'ringeopgave';
  const linkLabel = erRinge ? 'For hvilket menneske?' : (kraevetKind === 'brobygger' ? 'Hvilken brobygger?' : 'Hvilket menneske?');

  const vaelgType = (id) => {
    const ny = OPKALD_TYPER.find(t => t.id === id);
    if (valgt && ny && valgt.kind !== ny.kind) { setValgt(null); setQuery(''); }
    setType(id);
  };

  const resultater = query.trim().length >= 2 ? (() => {
    const ql = query.toLowerCase();
    const qd = query.replace(/\\s/g, '');
    if (kraevetKind === 'brobygger') {
      return (window.SoS_BROBYGGERE || []).filter(b => (b.name || '').toLowerCase().includes(ql))
        .slice(0, 8).map(b => ({ kind: 'brobygger', id: b.id, navn: b.name || '', tlf: b.mobil || b.phone || '' }));
    }
    return Object.values(window.SoS_MENNESKER || {}).filter(m =>
      ((m.firstName || '') + ' ' + (m.lastName || '')).toLowerCase().includes(ql) ||
      (m.mobil || '').replace(/\\s/g, '').includes(qd)
    ).slice(0, 8).map(m => ({ kind: 'menneske', id: m.id, navn: ((m.firstName || '') + ' ' + (m.lastName || '')).trim(), tlf: m.mobil || '' }));
  })() : [];

  const canSave = !!valgt && !!note.trim();""",
"1: state + typer")

# 2) handleSave: gem type + underType
sub(
"""      id: 'log-' + Date.now(),
      kind: valgt.kind,""",
"""      id: 'log-' + Date.now(),
      type,
      underType: erRinge ? underType : null,
      kind: valgt.kind,""",
"2: handleSave type")

# 3) Indsæt type-vælger + undertype før link-blokken
sub(
"""        <div style={{ padding: '18px 20px' }}>
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Tilknyt menneske eller brobygger <span style={{ color: SoS.orange }}>*</span></div>""",
"""        <div style={{ padding: '18px 20px' }}>
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Type opkald</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {OPKALD_TYPER.map(t => (
                <button key={t.id} onClick={() => vaelgType(t.id)} style={{
                  display: 'flex', alignItems: 'center', gap: 8, padding: '9px 12px', textAlign: 'left',
                  border: `1.5px solid ${type === t.id ? t.farve : SoS.line}`, borderRadius: SoS.r.sm,
                  background: type === t.id ? t.farve + '12' : '#fff', cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: type === t.id ? 700 : 500,
                  color: type === t.id ? SoS.ink : SoS.inkSoft }}>
                  <span style={{ width: 9, height: 9, borderRadius: 5, background: t.farve, flexShrink: 0 }}/>
                  {t.label}
                </button>
              ))}
            </div>
          </div>
          {erRinge && (
            <div style={{ marginBottom: 12 }}>
              <div style={lbl}>Hvad drejer ringeopgaven sig om?</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {RINGE_UNDER.map(u => (
                  <button key={u.id} onClick={() => setUnderType(u.id)} style={{
                    padding: '6px 11px', border: `1.5px solid ${underType === u.id ? SoS.ink : SoS.line}`,
                    borderRadius: SoS.r.sm, background: underType === u.id ? SoS.ink : '#fff',
                    color: underType === u.id ? '#fff' : SoS.ink, cursor: 'pointer',
                    fontFamily: SoS.sans, fontSize: 12, fontWeight: underType === u.id ? 700 : 400 }}>{u.label}</button>
                ))}
              </div>
            </div>
          )}
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>{linkLabel} <span style={{ color: SoS.orange }}>*</span></div>""",
"3: type-vælger UI")

# 4) Søge-placeholder kontekstuel
sub(
'                  placeholder="Søg navn eller telefon…"',
"                  placeholder={kraevetKind === 'brobygger' ? 'Søg brobygger…' : 'Søg menneske (navn eller telefon)…'}",
"4: placeholder")

# 5) Ingen-match-tekst kontekstuel
sub(
'                    Ingen match. Et opkald skal kobles til et menneske eller en brobygger — opret personen via "Ny aftale" først.',
"                    Ingen match. {kraevetKind === 'brobygger' ? 'Tjek brobyggerens navn.' : 'Opret mennesket via \\\"Ny aftale\\\" først.'} Et opkald skal altid kobles til en person.",
"5: ingen-match")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

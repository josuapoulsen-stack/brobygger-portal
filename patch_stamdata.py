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

COMP = r'''const STAMDATA_KATEGORIER = [
  { key: 'hovedsaeder',         label: 'Hovedsæder' },
  { key: 'afdelinger',          label: 'Afdelinger', obj: true },
  { key: 'brobygningstyper',    label: 'Brobygningstyper' },
  { key: 'aftaletyper',         label: 'Aftaletyper' },
  { key: 'henvendere',          label: 'Henvisningstyper' },
  { key: 'modtagere',           label: 'Modtagere' },
  { key: 'transportplaner',     label: 'Transportplaner' },
  { key: 'aflysningsaarsager',  label: 'Aflysningsårsager' },
  { key: 'aflystAf',            label: 'Aflyst af' },
  { key: 'samarbejdspartnere',  label: 'Samarbejdspartnere / henvisere' },
  { key: 'finansieringskilder', label: 'Finansiering / projekter' },
];

const DesktopStamdata = () => {
  const [kat, setKat]   = React.useState('hovedsaeder');
  const [ny, setNy]     = React.useState('');
  const [nyHs, setNyHs] = React.useState(SoS_REFS.hovedsaeder[0] || '');
  const [, force]       = React.useReducer(x => x + 1, 0);
  const meta  = STAMDATA_KATEGORIER.find(k => k.key === kat);
  const liste = SoS_REFS[kat] || [];
  const gem   = () => { if (window.SoS_saveRefs) window.SoS_saveRefs(); force(); };
  const tilfoej = () => {
    const v = ny.trim(); if (!v) return;
    if (meta.obj) { liste.push({ navn: v, hovedsaede: nyHs }); }
    else { if (liste.indexOf(v) >= 0) return; liste.push(v); }
    setNy(''); gem();
  };
  const slet = (i) => { liste.splice(i, 1); gem(); };

  return (
    <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
      {/* Kategori-liste */}
      <div style={{ width: 230, flexShrink: 0, border: `1px solid ${SoS.line}`,
        background: SoS.surface, borderRadius: 0 }}>
        {STAMDATA_KATEGORIER.map(k => {
          const on = kat === k.key;
          const n = (SoS_REFS[k.key] || []).length;
          return (
            <button key={k.key} onClick={() => setKat(k.key)} style={{
              display: 'flex', alignItems: 'center', width: '100%', gap: 8,
              padding: '10px 14px', border: 'none', cursor: 'pointer', textAlign: 'left',
              borderLeft: `3px solid ${on ? SoS.accent : 'transparent'}`,
              background: on ? '#fff' : 'transparent',
              fontFamily: SoS.sans, fontSize: 13, fontWeight: on ? 700 : 500,
              color: on ? SoS.ink : SoS.inkSoft }}>
              <span style={{ flex: 1 }}>{k.label}</span>
              <span style={{ fontFamily: SoS.mono, fontSize: 10, color: SoS.inkMuted }}>{n}</span>
            </button>
          );
        })}
      </div>

      {/* Indhold */}
      <div style={{ flex: 1, border: `1px solid ${SoS.line}`, background: '#fff', borderRadius: 0 }}>
        <div style={{ padding: '14px 18px', borderBottom: `1px solid ${SoS.line}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>{meta.label}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginTop: 2 }}>
            Tilføj, eller slet poster. Ændringer gemmes med det samme og bruges i hele systemet.
          </div>
        </div>

        {/* Tilføj-række */}
        <div style={{ padding: '12px 18px', borderBottom: `1px solid ${SoS.lineSoft}`,
          display: 'flex', gap: 8, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <input value={ny} onChange={e => setNy(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') tilfoej(); }}
            placeholder={meta.obj ? 'Afdelingens navn…' : 'Ny post…'}
            style={{ flex: 1, minWidth: 180, padding: '9px 12px', border: `1px solid ${SoS.line}`,
              borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none' }}/>
          {meta.obj && (
            <select value={nyHs} onChange={e => setNyHs(e.target.value)}
              style={{ padding: '9px 12px', border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, background: '#fff' }}>
              {SoS_REFS.hovedsaeder.map(h => <option key={h} value={h}>{h}</option>)}
            </select>
          )}
          <button onClick={tilfoej} disabled={!ny.trim()} style={{
            padding: '9px 16px', background: ny.trim() ? SoS.ink : SoS.lineSoft,
            color: ny.trim() ? '#fff' : SoS.inkMuted, border: 'none', borderRadius: SoS.r.sm,
            cursor: ny.trim() ? 'pointer' : 'default', fontFamily: SoS.sans, fontSize: 13, fontWeight: 700 }}>
            + Tilføj
          </button>
        </div>

        {/* Liste */}
        <div>
          {liste.length === 0 && (
            <div style={{ padding: '24px 18px', textAlign: 'center', fontFamily: SoS.sans,
              fontSize: 13, color: SoS.inkMuted }}>Ingen poster endnu — tilføj den første ovenfor.</div>
          )}
          {liste.map((item, i) => {
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
          })}
        </div>
      </div>
    </div>
  );
};

'''

# 1) Indsæt komponent før DesktopBrugerstyring
sub("const DesktopBrugerstyring = () => {",
    COMP + "const DesktopBrugerstyring = () => {",
    "1: DesktopStamdata komponent")

# 2) Nav-punkt (admin)
sub(
    ".concat(canUserMgmt ? [{ k: 'brugerstyring', l: 'Brugerstyring', i: 'shield' }] : []).map(n => (",
    ".concat(canUserMgmt ? [{ k: 'stamdata', l: 'Stamdata', i: 'note' }, { k: 'brugerstyring', l: 'Brugerstyring', i: 'shield' }] : []).map(n => (",
    "2: nav-punkt Stamdata")

# 3) Sidetitel
sub(
    "rapport: 'Rapport & eksport', brugerstyring: 'Brugerstyring' }[section]}",
    "rapport: 'Rapport & eksport', stamdata: 'Stamdata', brugerstyring: 'Brugerstyring' }[section]}",
    "3: sidetitel Stamdata")

# 4) Section render
sub(
    "{section === 'brugerstyring' && canUserMgmt && <DesktopBrugerstyring/>}",
    "{section === 'stamdata' && canUserMgmt && <DesktopStamdata/>}\n          {section === 'brugerstyring' && canUserMgmt && <DesktopBrugerstyring/>}",
    "4: render DesktopStamdata")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

with open(P, 'rb') as f:
    b = f.read()
needle = b".join('" + bytes([0x0a]) + b"');"
if needle in b:
    b = b.replace(needle, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(P, 'wb') as f:
        f.write(b)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f"\nOK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"\nFAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

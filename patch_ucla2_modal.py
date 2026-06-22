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

MODAL = """const UCLA3Modal = ({ menneske, kind, onClose, onSaved }) => {
  const [svar, setSvar] = React.useState([0, 0, 0]);
  const sum = svar.reduce((s, v) => s + v, 0);
  const komplet = svar.every(v => v > 0);
  const erBaseline = kind === 'baseline';

  const persist = (ucla3) => {
    const mm = (window.SoS_MENNESKER || {})[menneske.id];
    if (mm) { mm.ucla3 = ucla3; if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER); }
    if (onSaved) onSaved();
    onClose();
  };
  const eks = () => menneske.ucla3 || { optedOut: false, baseline: null, opfoelgninger: [] };
  const gem = () => {
    if (!komplet) return;
    const post = { q1: svar[0], q2: svar[1], q3: svar[2], sum, dato: new Date().toISOString().slice(0, 10) };
    const e = eks();
    if (erBaseline) persist({ ...e, optedOut: false, baseline: post });
    else persist({ ...e, opfoelgninger: [...(e.opfoelgninger || []), { ...post, label: 'Opfølgning' }] });
  };
  const fravalg = () => persist({ ...eks(), optedOut: true });

  const overlay = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 600,
    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 };
  const box = { background: '#fff', width: '100%', maxWidth: 480, maxHeight: '90vh',
    display: 'flex', flexDirection: 'column', borderRadius: SoS.r.lg, overflow: 'hidden',
    boxShadow: '0 20px 60px rgba(0,0,0,0.25)' };

  return (
    <div style={overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={box}>
        <div style={{ padding: '15px 20px', borderBottom: `1px solid ${SoS.line}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>
            Ensomhedsmåling (UCLA-3) · {erBaseline ? 'Baseline' : 'Opfølgning'}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginTop: 2 }}>
            {(menneske.firstName || '') + ' ' + (menneske.lastName || '')} · spørg mennesket og notér svarene
          </div>
        </div>
        <div style={{ overflowY: 'auto', padding: '16px 20px', flex: 1 }}>
          {UCLA3_SPM.map((spm, qi) => (
            <div key={qi} style={{ marginBottom: 16 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink, marginBottom: 7 }}>
                {qi + 1}. {spm}
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {UCLA3_SVAR.map(o => {
                  const on = svar[qi] === o.v;
                  return (
                    <button key={o.v} onClick={() => setSvar(s => s.map((x, j) => j === qi ? o.v : x))} style={{
                      flex: 1, padding: '9px 4px', borderRadius: SoS.r.sm, cursor: 'pointer',
                      border: `1.5px solid ${on ? SoS.accent : SoS.line}`,
                      background: on ? SoS.accent : '#fff', color: on ? '#fff' : SoS.inkSoft,
                      fontFamily: SoS.sans, fontSize: 12, fontWeight: on ? 700 : 400 }}>
                      {o.l}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px',
            background: SoS.surface, borderRadius: SoS.r.sm }}>
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Samlet score (3–9):</span>
            <span style={{ fontFamily: SoS.mono, fontSize: 18, fontWeight: 700,
              color: komplet ? SoS.ink : SoS.inkMuted }}>{komplet ? sum : '—'}</span>
            {komplet && <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
              {sum <= 4 ? 'lav ensomhed' : sum <= 6 ? 'moderat' : 'høj ensomhed'}</span>}
          </div>
        </div>
        <div style={{ padding: '14px 20px', borderTop: `1px solid ${SoS.line}`, display: 'flex', gap: 8, alignItems: 'center' }}>
          <button onClick={fravalg} style={{ padding: '11px 12px', background: 'none',
            border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
            Ønsker ikke at svare
          </button>
          <button onClick={onClose} style={{ marginLeft: 'auto', padding: '11px 14px', background: SoS.surface,
            border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Annuller</button>
          <button onClick={gem} disabled={!komplet} style={{ padding: '11px 18px',
            background: komplet ? SoS.ink : SoS.lineSoft, color: komplet ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.sm, cursor: komplet ? 'pointer' : 'default',
            fontFamily: SoS.sans, fontSize: 13, fontWeight: 700 }}>Gem måling</button>
        </div>
      </div>
    </div>
  );
};

const MenneskeDetailPanel = ({ menneske: m, onClose }) => {"""

sub("const MenneskeDetailPanel = ({ menneske: m, onClose }) => {", MODAL, "2: UCLA3Modal")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

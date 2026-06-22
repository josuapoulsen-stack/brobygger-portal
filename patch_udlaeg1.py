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

# 1) UdlaegKort-komponent før HomeScreen
COMP = """const UdlaegKort = ({ brobyggerId, user }) => {
  const loadKonti = () => { try { return JSON.parse(localStorage.getItem('sos_udlaeg_konti') || '[]'); } catch (e) { return []; } };
  const eksist = loadKonti().find(x => x.brobyggerId === brobyggerId) || null;
  const [open, setOpen]       = React.useState(false);
  const [navn, setNavn]       = React.useState((eksist && eksist.navn) || (user && user.name) || '');
  const [email, setEmail]     = React.useState((eksist && eksist.email) || (user && user.email) || '');
  const [regnr, setRegnr]     = React.useState((eksist && eksist.regnr) || '');
  const [kontonr, setKontonr] = React.useState((eksist && eksist.kontonr) || '');
  const [saved, setSaved]     = React.useState(false);
  const [indsendt, setIndsendt] = React.useState(!!eksist);

  const regOk   = /^\\d{4}$/.test(regnr.trim());
  const kontoOk = /^\\d{6,10}$/.test(kontonr.replace(/\\s/g, ''));
  const canSave = !!navn.trim() && regOk && kontoOk;
  const maskeret = kontonr ? ('•••• ' + kontonr.replace(/\\s/g, '').slice(-4)) : '';

  const gem = () => {
    if (!canSave) return;
    const list = loadKonti().filter(x => x.brobyggerId !== brobyggerId);
    list.push({
      brobyggerId: brobyggerId || 'bb-selv',
      navn: navn.trim(), email: email.trim(),
      regnr: regnr.trim(), kontonr: kontonr.replace(/\\s/g, ''),
      year: new Date().getFullYear(), submittedAt: new Date().toISOString().slice(0, 10),
    });
    localStorage.setItem('sos_udlaeg_konti', JSON.stringify(list));
    setSaved(true); setIndsendt(true);
    setTimeout(() => { setSaved(false); setOpen(false); }, 1200);
  };

  const inp = { width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
    borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, outline: 'none', boxSizing: 'border-box' };
  const lbl = { fontFamily: SoS.sans, fontSize: 11, fontWeight: 600, color: SoS.inkSoft, marginBottom: 5 };

  return (
    <div style={{ padding: '0 20px 8px' }}>
      <div style={{ background: '#fff', border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.md, overflow: 'hidden' }}>
        <button onClick={() => setOpen(o => !o)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12,
          padding: '11px 14px', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0, background: SoS.sageSoft,
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="chart" size={18} color={SoS.sage}/>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>Udlæg & bankoplysninger</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: indsendt ? SoS.sage : SoS.inkMuted, marginTop: 1 }}>
              {indsendt ? ('✓ Indsendt · reg. ' + (eksist ? eksist.regnr : regnr) + ' · konto ' + maskeret) : 'Tilføj reg.nr + kontonr til udbetaling'}
            </div>
          </div>
          <Icon name={open ? 'chevronU' : 'chevronD'} size={16} color={SoS.inkMuted}/>
        </button>
        {open && (
          <div style={{ padding: '4px 14px 16px', borderTop: `1px solid ${SoS.lineSoft}` }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5, margin: '10px 0 14px' }}>
              Selve udlæg og kvitteringer håndteres i <strong>Acubiz</strong>. Her registrerer du blot dine bankoplysninger, så økonomi kan oprette dig til udbetaling.
            </div>
            <div style={{ marginBottom: 10 }}>
              <div style={lbl}>Navn</div>
              <input value={navn} onChange={e => setNavn(e.target.value)} style={inp} placeholder="Dit fulde navn"/>
            </div>
            <div style={{ marginBottom: 10 }}>
              <div style={lbl}>E-mail</div>
              <input value={email} onChange={e => setEmail(e.target.value)} type="email" style={inp} placeholder="dig@mail.dk"/>
            </div>
            <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
              <div style={{ width: 110 }}>
                <div style={lbl}>Reg.nr</div>
                <input value={regnr} onChange={e => setRegnr(e.target.value.replace(/\\D/g, '').slice(0, 4))}
                  inputMode="numeric" style={{ ...inp, borderColor: regnr && !regOk ? SoS.rose : SoS.line }} placeholder="0000"/>
              </div>
              <div style={{ flex: 1 }}>
                <div style={lbl}>Kontonummer</div>
                <input value={kontonr} onChange={e => setKontonr(e.target.value.replace(/\\D/g, '').slice(0, 10))}
                  inputMode="numeric" style={{ ...inp, borderColor: kontonr && !kontoOk ? SoS.rose : SoS.line }} placeholder="1234567890"/>
              </div>
            </div>
            <button onClick={gem} disabled={!canSave} style={{ width: '100%', padding: '11px 0',
              background: saved ? SoS.green : canSave ? SoS.ink : SoS.lineSoft,
              color: canSave ? '#fff' : SoS.inkMuted, border: 'none', borderRadius: SoS.r.sm,
              cursor: canSave ? 'pointer' : 'default', fontFamily: SoS.sans, fontSize: 14, fontWeight: 700 }}>
              {saved ? '✓ Gemt og sendt til økonomi' : indsendt ? 'Opdater bankoplysninger' : 'Gem bankoplysninger'}
            </button>
            <div style={{ fontFamily: SoS.sans, fontSize: 10.5, color: SoS.inkMuted, marginTop: 8, lineHeight: 1.45 }}>
              Sendes kun til økonomi til oprettelse som kreditor — vises ikke for andre brobyggere.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const HomeScreen = ({ user, appointments, onOpenAppt, onNavigate, variant = 'busy', brobyggerId }) => {"""

sub("const HomeScreen = ({ user, appointments, onOpenAppt, onNavigate, variant = 'busy', brobyggerId }) => {", COMP, "1: UdlaegKort komponent")

# 2) Render efter Acubiz-blokken
sub(
"""          </div>
        );
      })()}

      {/* Uregistrerede aftaler */}""",
"""          </div>
        );
      })()}

      <UdlaegKort brobyggerId={brobyggerId} user={user} />

      {/* Uregistrerede aftaler */}""",
"2: render UdlaegKort")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

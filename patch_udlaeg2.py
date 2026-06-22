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

CARD = """      </DSCard>

      {/* Udlæg · kreditor-eksport */}
      <DSCard style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600, color: SoS.inkMuted,
          letterSpacing: 1, textTransform: 'uppercase', marginBottom: 14 }}>Udlæg · kreditor-eksport til e-conomic</div>
        {(() => {
          const list = (() => { try { return JSON.parse(localStorage.getItem('sos_udlaeg_konti') || '[]'); } catch (e) { return []; } })();
          const iaar = new Date().getFullYear();
          const iaarGrp = iaar - 2020;
          if (!list.length) return (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
              Ingen brobyggere har indsendt bankoplysninger endnu. Når de gør (via startsiden), kan de eksporteres her.
            </div>
          );
          const download = () => {
            const sorted = [...list].sort((a, b) => ((a.year || iaar) - (b.year || iaar)) || (a.submittedAt || '').localeCompare(b.submittedAt || ''));
            const seq = {};
            const rows = sorted.map(x => {
              const year = x.year || iaar;
              const gruppe = year - 2020;
              seq[year] = (seq[year] || 0) + 1;
              const kreditornr = String(gruppe) + String(seq[year]).padStart(3, '0');
              return [kreditornr, x.navn || '', gruppe, 'DKK', 'Netto 8 dage', 'Danmark', x.email || '', x.regnr || '', x.kontonr || ''];
            });
            const head = ['Kreditornummer', 'Navn', 'Kreditorgruppe', 'Valuta', 'Betalingsbetingelse', 'Land', 'E-mail', 'Bankregistreringsnummer', 'Bankkontonummer'];
            const esc = v => '\"' + String(v == null ? '' : v).replace(/\"/g, '\"\"') + '\"';
            const csv = '\\ufeff' + [head.map(esc).join(';')].concat(rows.map(r => r.map(esc).join(';'))).join('\\r\\n');
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'kreditorer-economic-' + new Date().toISOString().slice(0, 10) + '.csv';
            a.click();
          };
          return (
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginBottom: 12, lineHeight: 1.5 }}>
                {list.length} brobygger{list.length === 1 ? '' : 'e'} har indsendt bankoplysninger. Eksporten tildeler automatisk <strong>kreditornummer</strong> og <strong>kreditorgruppe</strong> (i år = gruppe {iaarGrp}, så hvert års kreditorer kan slettes samlet) samt valuta, betalingsbetingelse, land og e-mail — klar til import i e-conomic.
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 14 }}>
                <thead>
                  <tr>
                    {['Navn', 'Reg.', 'Konto', 'E-mail', 'Gruppe'].map((h, i) => (
                      <th key={i} style={{ textAlign: 'left', fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                        color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase', padding: '0 8px 8px',
                        borderBottom: `1px solid ${SoS.line}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {list.map((x, i) => (
                    <tr key={i}>
                      <td style={{ padding: '8px', borderBottom: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{x.navn}</td>
                      <td style={{ padding: '8px', borderBottom: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.mono, fontSize: 12, color: SoS.inkSoft }}>{x.regnr}</td>
                      <td style={{ padding: '8px', borderBottom: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.mono, fontSize: 12, color: SoS.inkSoft }}>{x.kontonr}</td>
                      <td style={{ padding: '8px', borderBottom: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>{x.email || '—'}</td>
                      <td style={{ padding: '8px', borderBottom: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.mono, fontSize: 12, color: SoS.inkSoft }}>{(x.year || iaar) - 2020}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button onClick={download} style={{ padding: '10px 18px', background: SoS.ink, color: '#fff',
                border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13, fontWeight: 700 }}>
                Download CSV til e-conomic
              </button>
            </div>
          );
        })()}
      </DSCard>

    </div>
  );
};
const OpkaldLog = ({ onClose }) => {"""

sub(
"""      </DSCard>

    </div>
  );
};
const OpkaldLog = ({ onClose }) => {""",
CARD,
"kreditor-eksport-kort")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

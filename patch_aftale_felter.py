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

# 1) Form-state: nye strukturerede felter
sub(
    "    aktivitetsTid: initial.aktivitetsTid || '',\n  });",
    "    aktivitetsTid: initial.aktivitetsTid || '',\n"
    "    aftaletype:        initial.aftaletype        || '',\n"
    "    brobygningstype:   initial.brobygningstype   || '',\n"
    "    henvender:         initial.henvender         || '',\n"
    "    modtagerType:      initial.modtagerType      || '',\n"
    "    samarbejdspartner: initial.samarbejdspartner || '',\n"
    "    finansiering:      initial.finansiering      || '',\n"
    "    afdeling:          initial.afdeling          || '',\n"
    "    aflystAf:          initial.aflystAf          || '',\n"
    "    aflysningsAarsag:  initial.aflysningsAarsag  || '',\n"
    "  });",
    "1: form-state felter")

# 2) Klassificerings-sektion i formularen (før Brobygger-note)
KLASS = r'''          {/* Klassificering — struktureret data (fra stamdata) */}
          <div style={{ borderTop: `1px solid ${SoS.lineSoft}`, paddingTop: 14 }}>
            <div style={{ ...labelStyle, marginBottom: 10 }}>Klassificering</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div>
                <div style={labelStyle}>Aftaletype</div>
                <select value={form.aftaletype} onChange={upd('aftaletype')} style={inputStyle}>
                  <option value="">Vælg…</option>
                  {(SoS_REFS.aftaletyper || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Brobygningstype</div>
                <select value={form.brobygningstype} onChange={upd('brobygningstype')} style={inputStyle}>
                  <option value="">Vælg…</option>
                  {(SoS_REFS.brobygningstyper || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Henvender</div>
                <select value={form.henvender} onChange={upd('henvender')} style={inputStyle}>
                  <option value="">Vælg…</option>
                  {(SoS_REFS.henvendere || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Modtager</div>
                <select value={form.modtagerType} onChange={upd('modtagerType')} style={inputStyle}>
                  <option value="">Vælg…</option>
                  {(SoS_REFS.modtagere || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Samarbejdspartner</div>
                <select value={form.samarbejdspartner} onChange={upd('samarbejdspartner')} style={inputStyle}>
                  <option value="">Ingen</option>
                  {(SoS_REFS.samarbejdspartnere || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Finansiering / projekt</div>
                <select value={form.finansiering} onChange={upd('finansiering')} style={inputStyle}>
                  <option value="">Ingen</option>
                  {(SoS_REFS.finansieringskilder || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Afdeling</div>
                <select value={form.afdeling} onChange={upd('afdeling')} style={inputStyle}>
                  <option value="">Vælg…</option>
                  {(SoS_REFS.afdelinger || []).map((a, i) => {
                    const navn = a && a.navn ? a.navn : a;
                    return <option key={i} value={navn}>{navn}</option>;
                  })}
                </select>
              </div>
            </div>
            {/* Aflysning (kun relevant hvis aflyst) */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 10 }}>
              <div>
                <div style={labelStyle}>Aflyst af (hvis aflyst)</div>
                <select value={form.aflystAf} onChange={upd('aflystAf')} style={inputStyle}>
                  <option value="">—</option>
                  {(SoS_REFS.aflystAf || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <div style={labelStyle}>Aflysningsårsag</div>
                <select value={form.aflysningsAarsag} onChange={upd('aflysningsAarsag')} style={inputStyle}>
                  <option value="">—</option>
                  {(SoS_REFS.aflysningsaarsager || []).map(x => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Brobygger-note */}'''

sub("          {/* Brobygger-note */}", KLASS, "2: klassificerings-sektion")

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

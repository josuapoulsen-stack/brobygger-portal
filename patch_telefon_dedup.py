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

# 1) Telefon-normalisering (kanonisk DK-form: sidste 8 cifre)
sub("window.SoS_isZone = function (scope) { return !!(SoS_REFS.zoner && SoS_REFS.zoner[scope]); };",
    "window.SoS_isZone = function (scope) { return !!(SoS_REFS.zoner && SoS_REFS.zoner[scope]); };\n"
    "// Telefon-normalisering: kanonisk form til genkendelse på tværs af forløb (DK = sidste 8 cifre, fjerner +45/0045/0)\n"
    "window.SoS_normPhone = function (s) { var d = String(s == null ? '' : s).replace(/\\D/g, ''); return d.length > 8 ? d.slice(-8) : d; };",
    "1: normPhone helper")

# 2) phoneMatches i NyAftaleFlow
sub("""  const canSaveNy = form.firstName.trim() && form.age.trim()
    && phoneDigits.length === 8 && type && kilde && consent;""",
"""  const canSaveNy = form.firstName.trim() && form.age.trim()
    && phoneDigits.length === 8 && type && kilde && consent;

  // Telefon-dedup: telefonnummer er den sikreste genkendelse (navne varierer)
  const _normPhone = (s) => window.SoS_normPhone ? window.SoS_normPhone(s) : String(s || '').replace(/\\D/g, '').slice(-8);
  const phoneMatches = phoneDigits.length >= 8
    ? Object.values(window.SoS_MENNESKER || {}).filter(m => m.mobil && _normPhone(m.mobil) === _normPhone(form.phone))
    : [];""",
"2: phoneMatches")

# 3) Dedup-banner efter telefon-feltet i 'ny'-formen
sub("""                style={{ ...inp, borderColor: form.phone && phoneDigits.length !== 8
                  ? SoS.rose : SoS.line }}/>
            </div>
          </div>
""",
"""                style={{ ...inp, borderColor: form.phone && phoneDigits.length !== 8
                  ? SoS.rose : SoS.line }}/>
            </div>
          </div>

          {phoneMatches.length > 0 && (
            <div style={{ marginBottom: 14, padding: '10px 12px', background: SoS.orange + '14',
              border: `1px solid ${SoS.orange}55`, borderRadius: SoS.r.sm }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12.5, fontWeight: 700, color: '#9A4A12', marginBottom: 4 }}>
                ⚠ Findes måske allerede — samme telefonnummer
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginBottom: 8, lineHeight: 1.45 }}>
                Nummeret matcher {phoneMatches.length === 1 ? 'et eksisterende menneske' : phoneMatches.length + ' eksisterende mennesker'}. Telefonnummer er vores sikreste genkendelse — tjek om det er samme person (de kan have brugt et andet navn).
              </div>
              {phoneMatches.slice(0, 3).map(m => (
                <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0',
                  borderTop: `1px solid ${SoS.orange}22` }}>
                  <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                    {((m.firstName || '') + ' ' + (m.lastName || '')).trim() || 'Uden navn'}
                    <span style={{ color: SoS.inkMuted }}> · {m.age || '?'} år · {m.hq || '?'}{m.status ? ' · ' + m.status : ''}</span>
                  </div>
                  <button onClick={() => { setSelectedPerson(m); setQuery(((m.firstName || '') + ' ' + (m.lastName || '')).trim()); setMode('eksisterende'); }}
                    style={{ padding: '5px 12px', background: SoS.ink, color: '#fff', border: 'none',
                      borderRadius: SoS.r.sm, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                    Samme person
                  </button>
                </div>
              ))}
            </div>
          )}
""",
"3: dedup-banner")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

ok = []
fail = []

def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1)
        ok.append(label)
    else:
        fail.append(label)

# ══════════════════════════════════════════════════════════════════
# D1 fix — indsæt Beskeder tab inden Actions strip
# ══════════════════════════════════════════════════════════════════
BESKEDER_TAB = '''        {/* ══ BESKEDER ══ */}
        {activeTab === 4 && (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {!tilknyttetBB ? (
              <div style={{ padding: '30px 0', textAlign: 'center',
                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen brobygger tilknyttet &middot; Tilknyt en brobygger for at sende beskeder
              </div>
            ) : (
              <>
                <div style={{ padding: '6px 0 10px', fontFamily: SoS.sans,
                  fontSize: 12, color: SoS.inkMuted }}>
                  Beskeder med {tilknyttetBB.name}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8,
                  minHeight: 80, maxHeight: 260, overflowY: 'auto',
                  padding: '8px 0', marginBottom: 10 }}>
                  {bbTrad.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px 0',
                      fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
                      Ingen beskeder endnu
                    </div>
                  ) : bbTrad.map(msg => {
                    const erAdmin = msg.fra === 'admin';
                    return (
                      <div key={msg.id} style={{ display: 'flex',
                        justifyContent: erAdmin ? 'flex-end' : 'flex-start' }}>
                        <div style={{ maxWidth: '78%' }}>
                          <div style={{ padding: '8px 12px', lineHeight: 1.5,
                            fontFamily: SoS.sans, fontSize: 12,
                            background: erAdmin ? SoS.accent : '#fff',
                            color: erAdmin ? '#fff' : SoS.ink,
                            border: erAdmin ? 'none' : `1px solid ${SoS.line}`,
                            borderRadius: SoS.r.md,
                            boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
                            {msg.tekst}
                          </div>
                          <div style={{ fontFamily: SoS.sans, fontSize: 9,
                            color: SoS.inkMuted, marginTop: 3,
                            textAlign: erAdmin ? 'right' : 'left' }}>
                            {new Date(msg.sendt).toLocaleDateString('da-DK',
                              { day: 'numeric', month: 'short' })}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
                  <textarea value={beskedTekst}
                    onChange={e => setBeskedTekst(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault(); sendBeskedFraForloeb();
                      }
                    }}
                    placeholder={"Skriv til " + tilknyttetBB.name.split(' ')[0] + "..."}
                    rows={2}
                    style={{ flex: 1, padding: '8px 12px',
                      border: `1px solid ${SoS.line}`,
                      borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 12,
                      color: SoS.ink, outline: 'none', resize: 'none',
                      lineHeight: 1.45 }}/>
                  <button onClick={sendBeskedFraForloeb}
                    disabled={!beskedTekst.trim()}
                    style={{ padding: '9px 14px', borderRadius: SoS.r.sm, border: 'none',
                      background: beskedTekst.trim() ? SoS.accent : SoS.lineSoft,
                      color: beskedTekst.trim() ? '#fff' : SoS.inkMuted,
                      cursor: beskedTekst.trim() ? 'pointer' : 'default',
                      fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>
                    Send
                  </button>
                </div>
              </>
            )}
          </div>
        )}

'''

sub(
    "          </div>\n        )}\n\n      </div>\n\n      {/* ── Actions strip",
    "          </div>\n        )}\n\n" + BESKEDER_TAB + "      </div>\n\n      {/* ── Actions strip",
    "D1: Beskeder tab indhold"
)

# ══════════════════════════════════════════════════════════════════
# D2 fix — tilf\xf8j opkald-log i Tidslinje-tab
# ══════════════════════════════════════════════════════════════════
OPKALD_LOG_SECTION = '''          {(() => {
            const logs = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]')
              .filter(l => l.navn && l.navn !== 'Ukendt' && (
                l.navn.toLowerCase().includes((m.firstName || '').toLowerCase()) ||
                l.navn.toLowerCase().includes((m.lastName || '').toLowerCase())));
            if (logs.length === 0) return null;
            return (
              <div style={{ marginTop: 14 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.9,
                  textTransform: 'uppercase', marginBottom: 8 }}>Loggede opkald</div>
                {logs.map((l, i) => (
                  <div key={l.id} style={{ display: 'flex', gap: 10,
                    padding: '8px 0',
                    borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                    <div style={{ fontFamily: SoS.mono, fontSize: 10,
                      color: SoS.inkMuted, flexShrink: 0, width: 74 }}>
                      {l.dato}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 12,
                        fontWeight: 600, color: SoS.ink }}>{l.navn}</div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11,
                        color: SoS.inkSoft, marginTop: 2, lineHeight: 1.4 }}>{l.note}</div>
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
'''

sub(
    "        {activeTab === 1 && (\n"
    "        <div style={{ padding: '16px 16px 24px' }}>\n"
    "          <MenneskeTimelineInline m={m} />\n"
    "        </div>\n"
    "      )}",
    "        {activeTab === 1 && (\n"
    "        <div style={{ padding: '16px 16px 24px' }}>\n"
    "          <MenneskeTimelineInline m={m} />\n"
    + OPKALD_LOG_SECTION +
    "        </div>\n"
    "      )}",
    "D2: opkald-log i Tidslinje-tab"
)

# ─── Write ───────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print('CRLF-fix: rettet')
else:
    print('CRLF-check: OK')

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  OK {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  FAIL {x}')
print('\nFil skrevet.')

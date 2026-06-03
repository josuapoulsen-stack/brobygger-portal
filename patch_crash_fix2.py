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

# ═══════════════════════════════════════════════════════════════════════════
# FIX 1: DesktopKalender — luk <> fragment inden );
#         bb-detaljepanelet sidder korrekt i fragmentet, men </> mangler
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "      })()}\n  );\n};\n\nconst DesktopRapport",
    "      })()}\n    </>\n  );\n};\n\nconst DesktopRapport",
    "DesktopKalender: luk JSX-fragment med </>"
)

# ═══════════════════════════════════════════════════════════════════════════
# FIX 2a: ProfileScreen — tilføj _profBb + bbStatus + toggleBbStatus
#          på komponent-niveau (Rules of Hooks)
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  const toggleNotif = (k) => setNotifToggles(p => ({ ...p, [k]: !p[k] }));",
    """  const toggleNotif = (k) => setNotifToggles(p => ({ ...p, [k]: !p[k] }));
  const _profBb = user.role === 'brobygger'
    ? (window.SoS_BROBYGGERE || []).find(b =>
        b.name === user.name || b.id === user.id ||
        b.name?.toLowerCase().includes(user.name?.split(' ')[0]?.toLowerCase())
      )
    : null;
  const [bbStatus, setBbStatus] = React.useState(_profBb?.status || 'aktiv');
  const toggleBbStatus = () => {
    const next = bbStatus === 'aktiv' ? 'pause' : 'aktiv';
    setBbStatus(next);
    if (_profBb && window.SoS_BROBYGGERE) {
      const idx = window.SoS_BROBYGGERE.findIndex(b => b.id === _profBb.id);
      if (idx >= 0) window.SoS_BROBYGGERE[idx].status = next;
    }
  };""",
    "ProfileScreen: _profBb + bbStatus + toggleBbStatus pa komponent-niveau"
)

# ═══════════════════════════════════════════════════════════════════════════
# FIX 2b: ProfileScreen — erstat IIFE med direkte conditional render
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """      {/* Brobygger-statuskort */}
      {user.role === 'brobygger' && (() => {
        const bb = (window.SoS_BROBYGGERE || []).find(b =>
          b.name === user.name || b.id === user.id || b.name?.toLowerCase().includes(user.name?.split(' ')[0]?.toLowerCase())
        );
        const [bbStatus, setBbStatus] = React.useState(bb?.status || 'aktiv');
        const toggleStatus = () => {
          const next = bbStatus === 'aktiv' ? 'pause' : 'aktiv';
          setBbStatus(next);
          if (bb && window.SoS_BROBYGGERE) {
            const idx = window.SoS_BROBYGGERE.findIndex(b => b.id === bb.id);
            if (idx >= 0) window.SoS_BROBYGGERE[idx].status = next;
          }
        };
        return (
          <div style={{ background: '#fff', borderRadius: SoS.r.lg,
            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>
            <div style={{ padding: '14px 16px', borderBottom: `1px solid ${SoS.lineSoft}`,
              display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                  Min status
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                  {bbStatus === 'aktiv' ? '🟢 Aktiv — tager imod nye aftaler' : '⏸️ Pause — modtager ikke nye aftaler'}
                </div>
              </div>
              <button onClick={toggleStatus} style={{
                width: 48, height: 28, borderRadius: 14,
                background: bbStatus === 'aktiv' ? SoS.sage : SoS.lineSoft,
                border: 'none', cursor: 'pointer', position: 'relative', flexShrink: 0,
              }}>
                <div style={{
                  width: 20, height: 20, borderRadius: 10, background: '#fff',
                  position: 'absolute', top: 4,
                  left: bbStatus === 'aktiv' ? 24 : 4,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                }}/>
              </button>
            </div>
            <div style={{ padding: '12px 16px', display: 'flex', gap: 24 }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                  {bb?.openShifts ?? 0}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Åbne vagter</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                  {(window.SoS_APPOINTMENTS_BUSY || []).filter(a => a.brobyggerId === bb?.id && a.status === 'confirmed').length}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Aktive aftaler</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                  {bb?.hq || '—'}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>HQ</div>
              </div>
            </div>
          </div>
        );
      })()}""",
    """      {/* Brobygger-statuskort */}
      {_profBb && (
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>
          <div style={{ padding: '14px 16px', borderBottom: `1px solid ${SoS.lineSoft}`,
            display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                Min status
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                {bbStatus === 'aktiv' ? '🟢 Aktiv — tager imod nye aftaler' : '⏸️ Pause — modtager ikke nye aftaler'}
              </div>
            </div>
            <button onClick={toggleBbStatus} style={{
              width: 48, height: 28, borderRadius: 14,
              background: bbStatus === 'aktiv' ? SoS.sage : SoS.lineSoft,
              border: 'none', cursor: 'pointer', position: 'relative', flexShrink: 0,
            }}>
              <div style={{
                width: 20, height: 20, borderRadius: 10, background: '#fff',
                position: 'absolute', top: 4,
                left: bbStatus === 'aktiv' ? 24 : 4,
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}/>
            </button>
          </div>
          <div style={{ padding: '12px 16px', display: 'flex', gap: 24 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                {_profBb?.openShifts ?? 0}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Åbne vagter</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                {(window.SoS_APPOINTMENTS_BUSY || []).filter(a => a.brobyggerId === _profBb?.id && a.status === 'confirmed').length}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Aktive aftaler</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 600, color: SoS.ink }}>
                {_profBb?.hq || '—'}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>HQ</div>
            </div>
          </div>
        </div>
      )}""",
    "ProfileScreen: erstat IIFE med direkte conditional render"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ─────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

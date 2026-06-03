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
# 1a. MessagesList — tilføj bbTekst state + sendBbBesked funktion
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [sosBesk,   setSosBesk]   = React.useState(() => JSON.parse(localStorage.getItem('sos_beskeder')      || '[]'));

  const handleAcceptMatch""",
    """  const [sosBesk,   setSosBesk]   = React.useState(() => JSON.parse(localStorage.getItem('sos_beskeder')      || '[]'));
  const [bbTekst,   setBbTekst]   = React.useState('');

  const sendBbBesked = () => {
    const t = bbTekst.trim();
    if (!t) return;
    const nm = { id: 'msg-' + Date.now(), fra: 'brobygger', til: 'admin',
      tekst: t, sendt: new Date().toISOString(), laest: false };
    const updated = [...sosBesk, nm];
    setSosBesk(updated);
    localStorage.setItem('sos_beskeder', JSON.stringify(updated));
    setBbTekst('');
  };

  const handleAcceptMatch""",
    "MessagesList: bbTekst state + sendBbBesked"
)

# ═══════════════════════════════════════════════════════════════════════════
# 1b. MessagesList — dispatch sos-mennesker-updated efter accept/decline
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
  };
  const handleDeclineMatch = (n) => {""",
    """    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
    window.dispatchEvent(new Event('sos-mennesker-updated'));
  };
  const handleDeclineMatch = (n) => {""",
    "handleAcceptMatch: dispatch sos-mennesker-updated event"
)

sub(
    """    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
  };

  const NOTIF_ICON""",
    """    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
    window.dispatchEvent(new Event('sos-mennesker-updated'));
  };

  const NOTIF_ICON""",
    "handleDeclineMatch: dispatch sos-mennesker-updated event"
)

# ═══════════════════════════════════════════════════════════════════════════
# 1c. MessagesList — tilføj brobygger svar-input over visibleThreads.map
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """      ))}\n      {role !== 'brobygger' && visibleThreads.map(t => (""",
    """      ))}
      {role === 'brobygger' && (
        <div style={{ display: 'flex', gap: 8, paddingTop: 12, marginTop: 4,
          borderTop: `1px solid ${SoS.lineSoft}` }}>
          <input
            value={bbTekst}
            onChange={e => setBbTekst(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendBbBesked(); } }}
            placeholder="Skriv til Social Sundhed…"
            style={{
              flex: 1, fontFamily: SoS.sans, fontSize: 13,
              border: `1px solid ${SoS.line}`, borderRadius: SoS.r.md,
              padding: '10px 12px', outline: 'none',
              background: '#fff', color: SoS.ink,
            }}
          />
          <button
            onClick={sendBbBesked}
            disabled={!bbTekst.trim()}
            style={{
              width: 42, height: 42, borderRadius: 21, flexShrink: 0,
              background: bbTekst.trim() ? SoS.orange : SoS.lineSoft,
              border: 'none', cursor: bbTekst.trim() ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
            <Icon name="send" size={17} color="#fff"/>
          </button>
        </div>
      )}
      {role !== 'brobygger' && visibleThreads.map(t => (""",
    "MessagesList: brobygger svar-input under beskeder-tab"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. AppWithTweaks — unreadCount inkluderer sos_notifikationer
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const unreadCount = SoS_NOTIFICATIONS.filter(n => n.unread).length;""",
    """  const unreadCount = SoS_NOTIFICATIONS.filter(n => n.unread).length
    + JSON.parse(localStorage.getItem('sos_notifikationer') || '[]').filter(n => !n.read && !n.status).length;""",
    "unreadCount: inkluder sos_notifikationer ulæste"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. ProfileScreen — brobygger-statuskort efter avatar
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """        </div>\n      </div>\n\n      <div style={{ background: '#fff', borderRadius: SoS.r.lg,\n        border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>\n        {[\n          { icon: 'user',""",
    """        </div>
      </div>

      {/* Brobygger-statuskort */}
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
      })()}

      <div style={{ background: '#fff', borderRadius: SoS.r.lg,
        border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>
        {[
          { icon: 'user',""",
    "ProfileScreen: brobygger-statuskort"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. DesktopKalender renderRow — ↻-mærkat på gentagende aftaler
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """          <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{a.activity}</div>""",
    """          <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink,
            display: 'flex', alignItems: 'center', gap: 5 }}>
            {a.activity}
            {a.aftaleForm === 'gentagende' && (
              <span title="Gentagende aftale" style={{ fontSize: 11, color: SoS.orange,
                fontFamily: SoS.mono, fontWeight: 700 }}>↻</span>
            )}
          </div>""",
    "renderRow: ↻-mærkat på gentagende aftaler"
)

# ═══════════════════════════════════════════════════════════════════════════
# 5a. DesktopMennesker — lyt på sos-mennesker-updated event
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  }, [initialTarget]);

  const alle = Object.values(SoS_MENNESKER);""",
    """  }, [initialTarget]);

  // Live-opdatering når brobygger accepterer/afviser via mobil
  React.useEffect(() => {
    const refresh = () => {
      setRefreshKey(k => k + 1);
      setSelected(prev => prev ? (window.SoS_MENNESKER?.[prev.id] || prev) : null);
    };
    window.addEventListener('sos-mennesker-updated', refresh);
    return () => window.removeEventListener('sos-mennesker-updated', refresh);
  }, []);

  const alle = Object.values(window.SoS_MENNESKER || SoS_MENNESKER);""",
    "DesktopMennesker: live refresh via sos-mennesker-updated event"
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
    print("CRLF-fix: .join('\\n') rettet")
else:
    print("CRLF-check: OK")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

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
# 1. Tilføj 'chat' og 'send' ikoner til Icon-komponenten
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "    more: <><circle cx=\"5\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/><circle cx=\"12\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/><circle cx=\"19\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/></>",
    "    more: <><circle cx=\"5\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/><circle cx=\"12\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/><circle cx=\"19\" cy=\"12\" r=\"1.5\" fill={color} stroke=\"none\"/></>,\n    chat: <><path d=\"M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-5 4V6a2 2 0 0 1 2-2z\"/></>,\n    send: <><path d=\"M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z\"/>",
    "Icon: tilføj chat + send ikoner"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. Desktop nav — tilføj Beskeder menupunkt
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "              { k: 'mennesker',    l: 'Mennesker',          i: 'heart'    },\n              ].concat(isAdmin",
    "              { k: 'mennesker',    l: 'Mennesker',          i: 'heart'    },\n              { k: 'beskeder',    l: 'Beskeder',           i: 'chat'    },\n              ].concat(isAdmin",
    "Desktop nav: Beskeder menupunkt"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Desktop header-titel map — tilføj 'beskeder'
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "{ dashboard: 'Dashboard', brobygninger: 'Brobygninger',\n                   brobyggere: 'Brobyggere', mennesker: 'Mennesker',\n                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport' }[section]",
    "{ dashboard: 'Dashboard', brobygninger: 'Brobygninger',\n                   brobyggere: 'Brobyggere', mennesker: 'Mennesker', beskeder: 'Beskeder',\n                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport' }[section]",
    "Desktop titel-map: beskeder"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. Desktop section-renderer — tilføj DesktopBeskeder
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "          {section === 'rapport' && <DesktopRapport/>}",
    "          {section === 'beskeder' && <DesktopBeskeder/>}\n          {section === 'rapport' && <DesktopRapport/>}",
    "Desktop: DesktopBeskeder renderer"
)

# ═══════════════════════════════════════════════════════════════════════════
# 5. DesktopBeskeder komponent — indsæt før DesktopView
# ═══════════════════════════════════════════════════════════════════════════
BESKEDER_COMPONENT = r"""
DesktopBeskeder = () => {
  const brobyggere = (window.SoS_BROBYGGERE || []).filter(b => ['aktiv', 'ny'].includes(b.status));
  const [valgtBB, setValgtBB] = React.useState(brobyggere[0]?.id || '');
  const [tekst,   setTekst]   = React.useState('');
  const [alle,    setAlle]    = React.useState(() => {
    try { return JSON.parse(localStorage.getItem('sos_beskeder') || '[]'); } catch { return []; }
  });
  const bottomRef = React.useRef(null);

  React.useEffect(() => {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
  }, [valgtBB, alle.length]);

  const gemBeskeder = (updated) => {
    setAlle(updated);
    localStorage.setItem('sos_beskeder', JSON.stringify(updated));
  };

  const sendBesked = () => {
    const t = tekst.trim();
    if (!t || !valgtBB) return;
    gemBeskeder([...alle, {
      id:    'msg-' + Date.now(),
      fra:   'admin',
      til:   valgtBB,
      tekst: t,
      sendt: new Date().toISOString(),
      laest: false,
    }]);
    setTekst('');
  };

  const trad = alle
    .filter(m => m.fra === valgtBB || m.til === valgtBB)
    .sort((a, b) => a.sendt.localeCompare(b.sendt));

  const sidsteBesked = bbId => {
    const msgs = alle.filter(m => m.fra === bbId || m.til === bbId);
    return msgs.sort((a, b) => b.sendt.localeCompare(a.sendt))[0] || null;
  };

  const ulaestCount = bbId =>
    alle.filter(m => m.til === 'admin' && m.fra === bbId && !m.laest).length;

  const formatTid = iso => {
    const d = new Date(iso);
    const today = new Date();
    if (d.toDateString() === today.toDateString())
      return d.toLocaleTimeString('da-DK', { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString('da-DK', { day: 'numeric', month: 'short' });
  };

  const bb = brobyggere.find(b => b.id === valgtBB);

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>

      {/* ── Sidebar: brobygger-liste ─────────────────────────────────── */}
      <div style={{ width: 260, borderRight: `1px solid ${SoS.line}`,
        display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
        <div style={{ padding: '16px 16px 12px', borderBottom: `1px solid ${SoS.line}` }}>
          <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 700,
            letterSpacing: 1, color: SoS.inkMuted }}>BROBYGGERE</div>
        </div>
        <div style={{ overflowY: 'auto', flex: 1 }}>
          {brobyggere.map(b => {
            const sidst  = sidsteBesked(b.id);
            const ulast  = ulaestCount(b.id);
            const valgt  = valgtBB === b.id;
            return (
              <button key={b.id} onClick={() => setValgtBB(b.id)}
                style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%',
                  padding: '12px 16px', border: 'none', cursor: 'pointer', textAlign: 'left',
                  borderBottom: `1px solid ${SoS.lineSoft}`,
                  background: valgt ? SoS.accent + '14' : 'transparent' }}>
                <div style={{ width: 36, height: 36, borderRadius: 18, background: b.bg || SoS.accent,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 700, color: '#fff', flexShrink: 0,
                  outline: valgt ? `2px solid ${SoS.accent}` : 'none', outlineOffset: 1 }}>
                  {b.avatar}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    color: valgt ? SoS.accent : SoS.ink }}>{b.name}</div>
                  {sidst ? (
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: 2 }}>
                      {sidst.fra === 'admin' ? 'Dig: ' : ''}{sidst.tekst.slice(0, 38)}
                    </div>
                  ) : (
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 2 }}>
                      Ingen beskeder endnu
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 3 }}>
                  {sidst && (
                    <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted }}>
                      {formatTid(sidst.sendt)}
                    </div>
                  )}
                  {ulast > 0 && (
                    <div style={{ minWidth: 18, height: 18, borderRadius: 9, background: SoS.accent,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 5px',
                      fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, color: '#fff' }}>
                      {ulast}
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Besked-tråd ──────────────────────────────────────────────── */}
      {valgtBB && bb ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {/* Header */}
          <div style={{ padding: '12px 20px', borderBottom: `1px solid ${SoS.line}`,
            display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 32, height: 32, borderRadius: 16, background: bb.bg || SoS.accent,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: '#fff' }}>
              {bb.avatar}
            </div>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, color: SoS.ink }}>
                {bb.name}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                {bb.email || ''}{bb.mobil ? ` · ${bb.mobil}` : ''}
              </div>
            </div>
          </div>

          {/* Beskeder */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px',
            display: 'flex', flexDirection: 'column', gap: 10,
            background: SoS.creamDeep || '#F8F5F0' }}>
            {trad.length === 0 && (
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <div style={{ fontSize: 36, marginBottom: 12 }}>💬</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkMuted }}>
                  Ingen beskeder til {bb.name.split(' ')[0]} endnu.<br/>Skriv den første!
                </div>
              </div>
            )}
            {trad.map(msg => {
              const erAdmin = msg.fra === 'admin';
              return (
                <div key={msg.id}
                  style={{ display: 'flex', justifyContent: erAdmin ? 'flex-end' : 'flex-start' }}>
                  <div style={{ maxWidth: '72%' }}>
                    <div style={{
                      padding: '10px 14px', lineHeight: 1.5,
                      fontFamily: SoS.sans, fontSize: 13,
                      background: erAdmin ? SoS.accent : '#fff',
                      color: erAdmin ? '#fff' : SoS.ink,
                      border: erAdmin ? 'none' : `1px solid ${SoS.line}`,
                      borderRadius: erAdmin
                        ? `${SoS.r.md} ${SoS.r.md} 4px ${SoS.r.md}`
                        : `${SoS.r.md} ${SoS.r.md} ${SoS.r.md} 4px`,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                    }}>
                      {msg.tekst}
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted,
                      marginTop: 4, textAlign: erAdmin ? 'right' : 'left' }}>
                      {formatTid(msg.sendt)}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef}/>
          </div>

          {/* Input */}
          <div style={{ padding: '12px 20px', borderTop: `1px solid ${SoS.line}`,
            display: 'flex', gap: 10, alignItems: 'flex-end',
            background: SoS.paper }}>
            <textarea
              value={tekst}
              onChange={e => setTekst(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendBesked(); }
              }}
              placeholder={`Skriv til ${bb.name.split(' ')[0]}… (Enter for at sende)`}
              rows={2}
              style={{ flex: 1, padding: '10px 14px', border: `1px solid ${SoS.line}`,
                borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 13,
                color: SoS.ink, outline: 'none', resize: 'none', lineHeight: 1.45,
                background: SoS.surface }}
            />
            <button onClick={sendBesked} disabled={!tekst.trim()}
              style={{ padding: '10px 18px', borderRadius: SoS.r.md, border: 'none',
                background: tekst.trim() ? SoS.accent : SoS.lineSoft,
                color: tekst.trim() ? '#fff' : SoS.inkMuted,
                fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                cursor: tekst.trim() ? 'pointer' : 'default',
                display: 'flex', alignItems: 'center', gap: 6, alignSelf: 'flex-end' }}>
              <Icon name="send" size={14} color={tekst.trim() ? '#fff' : SoS.inkMuted} weight={2}/>
              Send
            </button>
          </div>
        </div>
      ) : (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column', gap: 12 }}>
          <Icon name="chat" size={48} color={SoS.lineSoft} weight={1.5}/>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkMuted }}>
            Vælg en brobygger for at se beskeder
          </div>
        </div>
      )}
    </div>
  );
};

"""

sub(
    "DesktopView = ({ user, ownHq, isAdmin, onClose }) => {",
    BESKEDER_COMPONENT + "DesktopView = ({ user, ownHq, isAdmin, onClose }) => {",
    "DesktopBeskeder: komponent"
)

# ═══════════════════════════════════════════════════════════════════════════
# 6. DesktopApptModal — tilføj nye form-felter til state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "    brobyggerNote: initial.brobyggerNote || '',\n  });",
    "    brobyggerNote:  initial.brobyggerNote  || '',\n    aftaleForm:    initial.aftaleForm    || 'enkelt',\n    gentagelse:    initial.gentagelse    || '',\n    fremmoedeType: initial.fremmoedeType || '',\n    aktivitetsTid: initial.aktivitetsTid || '',\n  });",
    "DesktopApptModal: nye form-felter i state"
)

# ═══════════════════════════════════════════════════════════════════════════
# 7. DesktopApptModal — tilføj nye felter i UI (efter Mødested, før Status)
# ═══════════════════════════════════════════════════════════════════════════
sub(
    r"""          <div>
            <div style={labelStyle}>Mødested</div>
            <input type="text" value={form.location} onChange={upd('location')}
              placeholder="Adresse eller beskrivelse" style={inputStyle}/>
          </div>

          {/* Status */}""",
    r"""          <div>
            <div style={labelStyle}>Mødested</div>
            <input type="text" value={form.location} onChange={upd('location')}
              placeholder="Adresse eller beskrivelse" style={inputStyle}/>
          </div>

          {/* Fremmøde */}
          <div>
            <div style={labelStyle}>Fremmøde</div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {[
                { v: 'hjemme',    l: '🏠 Følges fra hjemmet' },
                { v: 'sted',      l: '📍 Mødes på stedet' },
                { v: 'brobygger', l: '🤝 Mødes hos brobygger' },
              ].map(o => (
                <button key={o.v}
                  onClick={() => setForm(f => ({ ...f, fremmoedeType: f.fremmoedeType === o.v ? '' : o.v }))}
                  style={{ padding: '6px 12px', border: `1.5px solid ${form.fremmoedeType === o.v ? SoS.accent : SoS.line}`,
                    borderRadius: 0, background: form.fremmoedeType === o.v ? SoS.accent + '14' : SoS.surface,
                    fontFamily: SoS.sans, fontSize: 12, cursor: 'pointer',
                    color: form.fremmoedeType === o.v ? SoS.accent : SoS.inkSoft,
                    fontWeight: form.fremmoedeType === o.v ? 600 : 400 }}>
                  {o.l}
                </button>
              ))}
            </div>
          </div>

          {/* Tidspunkt for aktiviteten */}
          <div>
            <div style={labelStyle}>Tidspunkt for aktiviteten</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <input type="time" value={form.aktivitetsTid} onChange={upd('aktivitetsTid')}
                style={{ ...inputStyle, width: 'auto' }}/>
              {form.aktivitetsTid && (
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                  F.eks. kl. {form.aktivitetsTid} hos lægen — brobygger ankommer tidligere
                </div>
              )}
            </div>
            {!form.aktivitetsTid && (
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 4 }}>
                Selve aftaletidspunktet (f.eks. lægetid kl. 14:30). Brobyggers ankomst sættes i Start/Slut.
              </div>
            )}
          </div>

          {/* Aftaleform: enkelt / gentagende */}
          <div>
            <div style={labelStyle}>Aftaleform</div>
            <div style={{ display: 'flex', border: `1px solid ${SoS.line}`, borderRadius: 0, overflow: 'hidden' }}>
              {[
                { v: 'enkelt',     l: 'Enkelt aftale' },
                { v: 'gentagende', l: '↻ Gentagende' },
              ].map((o, i) => (
                <button key={o.v}
                  onClick={() => setForm(f => ({ ...f, aftaleForm: o.v, gentagelse: '' }))}
                  style={{ flex: 1, padding: '8px 0', border: 'none',
                    borderLeft: i > 0 ? `1px solid ${SoS.line}` : 'none',
                    cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                    background: form.aftaleForm === o.v ? SoS.ink : SoS.surface,
                    color: form.aftaleForm === o.v ? '#fff' : SoS.inkSoft }}>
                  {o.l}
                </button>
              ))}
            </div>
            {form.aftaleForm === 'gentagende' && (
              <div style={{ marginTop: 8, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {[
                  { v: 'ugentligt',  l: 'Ugentligt' },
                  { v: 'hver14dag',  l: 'Hver 14. dag' },
                  { v: 'maanedligt', l: 'Månedligt' },
                  { v: 'variabelt',  l: 'Variabelt' },
                ].map(o => (
                  <button key={o.v}
                    onClick={() => setForm(f => ({ ...f, gentagelse: o.v }))}
                    style={{ padding: '5px 12px',
                      border: `1.5px solid ${form.gentagelse === o.v ? SoS.ink : SoS.line}`,
                      borderRadius: 0, cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12,
                      background: form.gentagelse === o.v ? SoS.ink : SoS.surface,
                      color: form.gentagelse === o.v ? '#fff' : SoS.inkSoft,
                      fontWeight: form.gentagelse === o.v ? 600 : 400 }}>
                    {o.l}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Status */}""",
    "DesktopApptModal: fremmøde + aktivitetstid + enkelt/gentagende UI"
)

# ═══════════════════════════════════════════════════════════════════════════
# 8. Mobil TabBar — fjern 'historik', hold kun hjem/kalender/notif/profil
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const tabs = [
    { id: 'hjem', label: 'Hjem', icon: 'home' },
    { id: 'kalender', label: 'Kalender', icon: 'calendar' },
    { id: 'historik', label: 'Historik', icon: 'clock' },
    { id: 'notif', label: 'Beskeder', icon: 'bell' },
    { id: 'profil', label: 'Profil', icon: 'user' },
  ];""",
    """  const tabs = [
    { id: 'hjem',    label: 'Hjem',      icon: 'home'     },
    { id: 'kalender',label: 'Kalender',  icon: 'calendar' },
    { id: 'notif',   label: 'Beskeder',  icon: 'chat'     },
    { id: 'profil',  label: 'Profil',    icon: 'user'     },
  ];""",
    "Mobil TabBar: fjern historik, brug chat-ikon til beskeder"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'OK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

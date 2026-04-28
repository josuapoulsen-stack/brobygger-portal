# -*- coding: utf-8 -*-
"""
patch_messaging.py
Komplet omskrivning af besked-systemet:
  1. SoS_THREADS  — tilføjer koordinator-tråde (fromBrobygger) + urgent-eksempel
  2. ComposeMessage — ny komponent: send til én / alle aktive / alle / alle HQ'er
     - Hurtige skabeloner, live modtager-tæller, urgent-flag, brobygger-picker
  3. MessagesList  — role-aware: viser komponer-knap for rådgiver/admin
  4. MessageThread — role-aware: read-only fællesbeskeder, korrekt placeholder
  5. App           — tilføjer msgCompose-state + sender role til besked-screens
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ============================================================
# 1. Udvid SoS_THREADS med koordinator-view tråde
# ============================================================
OLD_THREADS_END = """  { id: 't-4', withName: 'Ahmad Karimi', withRole: 'Menneske \u00b7 Ahmad (34)', avatar: 'AK', bg: '#7FA089',
    last: '[Via koordinator] Kan vi flytte til torsdag?', time: '21. apr', unread: 0, proxied: true },
];"""

NEW_THREADS_END = """  { id: 't-4', withName: 'Ahmad Karimi', withRole: 'Menneske \u00b7 Ahmad (34)', avatar: 'AK', bg: '#7FA089',
    last: '[Via koordinator] Kan vi flytte til torsdag?', time: '21. apr', unread: 0, proxied: true },
  // Koordinator-view: tråde MED brobyggere (fromBrobygger: true)
  { id: 't-5', withName: 'Katrine Lund', withRole: 'Brobygger \u00b7 aktiv', avatar: 'KL', bg: '#7FA089',
    last: 'Tak for info om næste aftale!', time: 'tirs.', unread: 2, fromBrobygger: true },
  { id: 't-6', withName: 'Thomas Birk', withRole: 'Brobygger \u00b7 på pause til 1. maj', avatar: 'TB', bg: '#999',
    last: 'Melder mig klar igen 1. maj', time: 'man.', unread: 0, fromBrobygger: true, paused: true },
  { id: 't-7', withName: 'Signe Olsen', withRole: 'Brobygger \u00b7 aktiv', avatar: 'SO', bg: '#6B8CAE',
    last: 'Kan vi tale om Ahmad i morgen?', time: 'søn.', unread: 1, fromBrobygger: true },
  { id: 't-8', withName: 'Omar Hassan', withRole: 'Brobygger \u00b7 aktiv', avatar: 'OH', bg: '#B8501E',
    last: 'Aftalen er bekræftet \u2014 glæder mig!', time: '22. apr', unread: 0, fromBrobygger: true },
  // Urgent-eksempel (koordinator modtager vigtig besked fra brobygger)
  { id: 't-9', withName: 'Lise Nygaard', withRole: 'Brobygger \u00b7 aktiv', avatar: 'LN', bg: '#D64545',
    last: 'VIGTIGT: Borger indlagt i dag', time: '09:14', unread: 1, fromBrobygger: true, urgent: true },
];"""

cnt = html.count(OLD_THREADS_END)
html = html.replace(OLD_THREADS_END, NEW_THREADS_END, 1)
results.append(('SoS_THREADS udvidet', cnt, 1))

# ============================================================
# 2. Erstat hele MessagesList + MessageThread blokken
#    med ComposeMessage + opdaterede versioner
# ============================================================

OLD_MSG_BLOCK = """const MessagesList = ({ onOpen, onBack }) => (
  <div style={{ position: 'absolute', inset: 0, background: SoS.cream, overflowY: 'auto', paddingBottom: 90 }}>
    <TopBar title="Beskeder" subtitle="Din koordinator" bg={SoS.cream}
      trailing={<button style={{
        width: 40, height: 40, borderRadius: 20, background: '#fff',
        border: 'none', boxShadow: SoS.shadow.sm, cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}><Icon name="search" size={20} color={SoS.ink}/></button>}/>

    <div style={{ padding: '8px 12px' }}>
      {SoS_THREADS.map(t => (
        <button key={t.id} onClick={() => onOpen(t.id)} style={{
          display: 'flex', gap: 12, width: '100%', padding: 14,
          background: t.unread ? '#fff' : 'transparent',
          border: 'none', borderRadius: SoS.r.lg, cursor: 'pointer', textAlign: 'left',
          marginBottom: 4, boxShadow: t.unread ? SoS.shadow.sm : 'none',
          alignItems: 'center',
        }}>
          <div style={{ position: 'relative' }}>
            <Avatar initials={t.avatar} bg={t.bg} size={48}/>
            {t.online && <div style={{
              position: 'absolute', bottom: 0, right: 0, width: 12, height: 12,
              borderRadius: 6, background: SoS.sage, border: '2px solid #fff',
            }}/>}
            {t.official && <div style={{
              position: 'absolute', bottom: -2, right: -2, width: 18, height: 18,
              borderRadius: 9, background: SoS.orange, border: '2px solid #fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}><Icon name="shield" size={10} color="#fff" weight={2.5}/></div>}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: t.unread ? 700 : 600,
                color: SoS.ink }}>{t.withName}</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11,
                color: t.unread ? SoS.orange : SoS.inkMuted, fontWeight: t.unread ? 600 : 400 }}>
                {t.time}
              </div>
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
              {t.withRole}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginTop: 4, gap: 8 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13,
                color: t.unread ? SoS.ink : SoS.inkSoft,
                fontWeight: t.unread ? 500 : 400,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>{t.proxied && '\u21b3 '}{t.last}</div>
              {t.unread > 0 && <div style={{
                minWidth: 20, height: 20, borderRadius: 10, background: SoS.orange,
                color: '#fff', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                padding: '0 6px',
              }}>{t.unread}</div>}
            </div>
          </div>
        </button>
      ))}
    </div>

    {/* Info footnote */}
    <div style={{ margin: '16px 20px', padding: 14, background: SoS.creamDeep,
      borderRadius: SoS.r.md, display: 'flex', gap: 10 }}>
      <Icon name="lock" size={16} color={SoS.orangeDeep}/>
      <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
        color: SoS.orangeDeep, lineHeight: 1.5 }}>
        Al kommunikation går gennem din koordinator. Direkte kontakt til mennesker sker altid via koordinatoren for at beskytte begge parter.
      </div>
    </div>
  </div>
);

const MessageThread = ({ threadId, onBack }) => {
  const thread = SoS_THREADS.find(t => t.id === threadId) || SoS_THREADS[0];
  const [draft, setDraft] = React.useState('');
  const [sent, setSent] = React.useState(false);

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 12px', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none',
          padding: 4, cursor: 'pointer' }}>
          <Icon name="chevronL" size={22} color={SoS.ink}/>
        </button>
        <Avatar initials={thread.avatar} bg={thread.bg} size={40}/>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
            {thread.withName}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
            {thread.online ? '\u25cf Online' : thread.withRole}
          </div>
        </div>
        <button style={{ background: 'none', border: 'none', padding: 4, cursor: 'pointer' }}>
          <Icon name="phone" size={20} color={SoS.orange}/>
        </button>
      </div>

      {/* Date separator */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 8px' }}>
        <div style={{ textAlign: 'center', margin: '8px 0 16px' }}>
          <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
            background: SoS.creamDeep, padding: '4px 10px', borderRadius: 999 }}>
            I dag
          </span>
        </div>

        {SoS_MESSAGES.map(m => {
          const mine = m.from === 'me';
          return (
            <div key={m.id} style={{
              display: 'flex', justifyContent: mine ? 'flex-end' : 'flex-start',
              marginBottom: 6,
            }}>
              <div style={{
                maxWidth: '78%',
                padding: '10px 14px',
                borderRadius: mine
                  ? `${SoS.r.lg}px ${SoS.r.lg}px 6px ${SoS.r.lg}px`
                  : `${SoS.r.lg}px ${SoS.r.lg}px ${SoS.r.lg}px 6px`,
                background: mine ? SoS.orange : '#fff',
                color: mine ? '#fff' : SoS.ink,
                fontFamily: SoS.sans, fontSize: 14, lineHeight: 1.4,
                boxShadow: mine ? 'none' : SoS.shadow.sm,
              }}>
                {m.text}
                <div style={{ fontSize: 10, marginTop: 4,
                  opacity: mine ? 0.7 : 0.5, fontWeight: 400 }}>
                  {m.time}{mine && ' \u00b7 L\u00e6st'}
                </div>
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        <div style={{ display: 'flex', gap: 4, padding: '8px 14px', alignItems: 'center' }}>
          <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
            animation: 'typing 1.4s infinite', animationDelay: '0s' }}/>
          <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
            animation: 'typing 1.4s infinite', animationDelay: '0.2s' }}/>
          <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
            animation: 'typing 1.4s infinite', animationDelay: '0.4s' }}/>
          <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginLeft: 4 }}>
            Linda skriver...
          </span>
        </div>
        <style>{\`@keyframes typing {
          0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
          30% { opacity: 1; transform: translateY(-3px); }
        }\`}</style>
      </div>

      {/* Composer */}
      <div style={{ padding: '12px 16px 30px', background: '#fff',
        borderTop: `1px solid ${SoS.line}`,
        display: 'flex', gap: 8, alignItems: 'flex-end' }}>
        <button style={{ width: 38, height: 38, borderRadius: 19,
          background: SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Icon name="plus" size={20} color={SoS.ink}/>
        </button>
        <div style={{ flex: 1, background: SoS.creamDeep, borderRadius: 22,
          padding: '10px 14px', minHeight: 38 }}>
          <textarea value={draft} onChange={e => setDraft(e.target.value)}
            placeholder="Skriv til Linda..." rows={1}
            style={{ width: '100%', background: 'transparent', border: 'none',
              outline: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
              resize: 'none' }}/>
        </div>
        <button onClick={() => { if (draft.trim()) { setSent(true); setDraft(''); setTimeout(() => setSent(false), 2000); } }}
          style={{ width: 38, height: 38, borderRadius: 19,
          background: draft ? SoS.orange : SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          transition: 'background 0.2s' }}>
          <Icon name={sent ? 'check' : 'chevron'} size={18} color={draft || sent ? '#fff' : SoS.inkMuted} weight={2.5}/>
        </button>
      </div>
    </div>
  );
};

window.MessagesList = MessagesList;"""

NEW_MSG_BLOCK = """// ── ComposeMessage ─────────────────────────────────────────────────────────
// Send til én / alle aktive / alle / alle HQ'er
const ComposeMessage = ({ role, ownHq, onClose }) => {
  const isAdmin = role === 'admin';
  const [scope,      setScope]      = React.useState('aktive');
  const [pickingBb,  setPickingBb]  = React.useState(false);
  const [selectedBb, setSelectedBb] = React.useState(null);
  const [bbSearch,   setBbSearch]   = React.useState('');
  const [templateId, setTemplateId] = React.useState(null);
  const [body,       setBody]       = React.useState('');
  const [urgent,     setUrgent]     = React.useState(false);
  const [sent,       setSent]       = React.useState(false);

  const SCOPES = [
    { id: 'een',     label: 'Én brobygger',  sub: 'Vælg nedenfor' },
    { id: 'aktive',  label: 'Alle aktive',   sub: 'Ekskl. pause' },
    { id: 'alle',    label: 'Inkl. pause',   sub: 'Alle i ' + ownHq },
    ...(isAdmin ? [{ id: 'alle-hq', label: 'Alle HQ\u2019er', sub: 'Tværgående fællesbesked' }] : []),
  ];

  const TEMPLATES = [
    { id: 'noter',  emoji: '📋', label: 'Husk at notere',
      text: 'Husk at udfylde en registrering efter din næste aftale. Det tager 2 minutter og er vigtigt for vores dokumentation og SROI-rapport.' },
    { id: 'afbud',  emoji: '📞', label: 'Meld afbud i tid',
      text: 'Husk altid at melde afbud til din koordinator senest 24 timer før en planlagt aftale, så vi kan underrette borgeren i god tid.' },
    { id: 'info',   emoji: '📅', label: 'Infomøde',
      text: 'Vi holder infomøde for brobyggere snart. Dato og program følger — sæt allerede et kryds i kalenderen og del gerne med nogen, der kunne være interesserede!' },
    { id: 'ros',    emoji: '⭐', label: 'Tak og ros',
      text: 'Tak for din fantastiske indsats som brobygger. Det arbejde du gør gør en reel forskel for de mennesker, du møder. Vi sætter stor pris på dig!' },
    { id: 'husk',   emoji: '🔔', label: 'Husk arrangement',
      text: 'Husk vores fælles arrangement. Vi håber du kan deltage — meld tilbage til din koordinator om du kommer.' },
  ];

  const allBbs = window.SoS_BROBYGGERE || [];
  const activeBbs = allBbs.filter(b => b.status === 'aktiv');
  const recipientCount = scope === 'een' ? (selectedBb ? 1 : 0)
    : scope === 'aktive' ? activeBbs.length
    : scope === 'alle'   ? allBbs.length
    : 412;

  const canSend = body.trim().length > 2 && (scope !== 'een' || selectedBb);

  const handleSend = () => setSent(true);

  const filteredBbs = allBbs.filter(b =>
    !bbSearch || b.name.toLowerCase().includes(bbSearch.toLowerCase())
  );

  // ── Brobygger-picker ──
  if (pickingBb) return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      overflowY: 'auto', zIndex: 220, display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '54px 16px 12px', background: '#fff', position: 'sticky',
        top: 0, zIndex: 10, borderBottom: `1px solid ${SoS.lineSoft}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={() => setPickingBb(false)} style={{ width: 36, height: 36,
          borderRadius: 18, background: SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="chevronL" size={18} color={SoS.ink} weight={2.2}/>
        </button>
        <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink }}>
          Vælg brobygger
        </div>
      </div>
      <div style={{ padding: '10px 12px 6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8,
          background: '#fff', borderRadius: SoS.r.md, padding: '10px 14px',
          border: `1px solid ${SoS.lineSoft}` }}>
          <Icon name="search" size={14} color={SoS.inkMuted}/>
          <input value={bbSearch} onChange={e => setBbSearch(e.target.value)}
            placeholder="Søg brobygger..." style={{ flex: 1, background: 'transparent',
              border: 'none', outline: 'none', fontFamily: SoS.sans, fontSize: 14 }}/>
        </div>
      </div>
      <div style={{ padding: '0 12px 32px' }}>
        {filteredBbs.map(b => {
          const STATUS_C = { aktiv: SoS.sage, pause: '#E8A43E', afventer: SoS.orange, afsluttet: '#999' };
          const STATUS_L = { aktiv: 'Aktiv', pause: 'På pause', afventer: 'Afventer', afsluttet: 'Afsluttet' };
          const sel = selectedBb?.id === b.id;
          return (
            <button key={b.id} onClick={() => { setSelectedBb(b); setPickingBb(false); setBbSearch(''); }}
              style={{ display: 'flex', gap: 12, width: '100%', padding: '12px 10px',
                background: sel ? SoS.orange + '12' : 'transparent',
                border: `2px solid ${sel ? SoS.orange : 'transparent'}`,
                borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',
                alignItems: 'center', marginBottom: 2 }}>
              <Avatar initials={b.avatar} bg={b.bg} size={40}/>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
                  color: sel ? SoS.orange : SoS.ink }}>{b.name}</div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center', marginTop: 2 }}>
                  <div style={{ width: 6, height: 6, borderRadius: 3,
                    background: STATUS_C[b.status] || '#999' }}/>
                  <span style={{ fontFamily: SoS.sans, fontSize: 12,
                    color: STATUS_C[b.status] || SoS.inkSoft }}>
                    {STATUS_L[b.status] || b.status}
                  </span>
                </div>
              </div>
              {sel && <Icon name="check" size={18} color={SoS.orange} weight={2.5}/>}
            </button>
          );
        })}
      </div>
    </div>
  );

  // ── Succes-skærm ──
  if (sent) return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, zIndex: 210,
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: 32 }}>
      <div style={{ width: 80, height: 80, borderRadius: 40, background: SoS.sage,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24 }}>
        <Icon name="check" size={36} color="#fff" weight={2.5}/>
      </div>
      <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500, color: SoS.ink,
        textAlign: 'center', marginBottom: 8 }}>Besked sendt</div>
      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        textAlign: 'center', lineHeight: 1.6, marginBottom: 8, maxWidth: 280 }}>
        {scope === 'een'
          ? `Beskeden er sendt til ${selectedBb?.name}.`
          : `Beskeden er sendt til ${recipientCount} brobyggere.`}
      </div>
      {urgent && (
        <div style={{ background: '#D64545' + '18', borderRadius: SoS.r.md,
          padding: '8px 14px', marginBottom: 20 }}>
          <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
            color: '#D64545' }}>⚑ Markeret som vigtig</span>
        </div>
      )}
      <Button full onClick={onClose}>Luk</Button>
    </div>
  );

  // ── Compose-skærm ──
  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      overflowY: 'auto', zIndex: 210 }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 14px', background: '#fff', position: 'sticky',
        top: 0, zIndex: 10, borderBottom: `1px solid ${SoS.lineSoft}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onClose} style={{ width: 36, height: 36, borderRadius: 18,
          background: SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="chevronL" size={18} color={SoS.ink} weight={2.2}/>
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkSoft, letterSpacing: 0.4, textTransform: 'uppercase' }}>
            {isAdmin ? 'Admin besked' : 'Ny besked'}
          </div>
          <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink }}>
            Skriv til brobyggere
          </div>
        </div>
      </div>

      <div style={{ padding: '14px 16px 48px', display: 'flex', flexDirection: 'column', gap: 12 }}>

        {/* Modtager-scope */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 12 }}>Modtager *</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 12 }}>
            {SCOPES.map(s => {
              const sel = scope === s.id;
              return (
                <button key={s.id} onClick={() => setScope(s.id)} style={{
                  padding: '12px 14px', borderRadius: SoS.r.md, textAlign: 'left',
                  background: sel ? SoS.orange + '14' : SoS.creamDeep,
                  border: `2px solid ${sel ? SoS.orange : 'transparent'}`,
                  cursor: 'pointer', transition: 'all 0.15s',
                }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13,
                    fontWeight: sel ? 700 : 500, color: sel ? SoS.orange : SoS.ink }}>
                    {s.label}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11,
                    color: SoS.inkSoft, marginTop: 2 }}>{s.sub}</div>
                </button>
              );
            })}
          </div>

          {/* Brobygger-picker trigger */}
          {scope === 'een' && (
            <button onClick={() => setPickingBb(true)} style={{
              display: 'flex', alignItems: 'center', gap: 12, width: '100%',
              padding: '12px 14px', borderRadius: SoS.r.md,
              background: selectedBb ? SoS.sage + '12' : SoS.creamDeep,
              border: `2px solid ${selectedBb ? SoS.sage : SoS.lineSoft}`,
              cursor: 'pointer' }}>
              {selectedBb
                ? <><Avatar initials={selectedBb.avatar} bg={selectedBb.bg} size={32}/>
                    <div style={{ flex: 1, textAlign: 'left' }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
                        color: SoS.ink }}>{selectedBb.name}</div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11,
                        color: SoS.inkSoft }}>{selectedBb.withRole || 'Brobygger'}</div>
                    </div>
                    <Icon name="chevronR" size={16} color={SoS.inkMuted}/></>
                : <><div style={{ flex: 1, textAlign: 'left', fontFamily: SoS.sans,
                    fontSize: 14, color: SoS.inkSoft }}>Vælg brobygger...</div>
                    <Icon name="chevronR" size={16} color={SoS.inkMuted}/></>}
            </button>
          )}

          {/* Modtager-tæller */}
          {scope !== 'een' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10,
              padding: '8px 12px', background: SoS.creamDeep, borderRadius: SoS.r.md }}>
              <Icon name="users" size={14} color={SoS.orange}/>
              <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                Sendes til <strong style={{ color: SoS.orange }}>{recipientCount}</strong> brobyggere
                {scope === 'aktive' ? ' (aktive)' : scope === 'alle-hq' ? ' på tværs af alle HQ\u2019er' : ''}
              </span>
            </div>
          )}
        </div>

        {/* Skabeloner */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
            Hurtige skabeloner
          </div>
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
            {TEMPLATES.map(t => (
              <button key={t.id} onClick={() => { setTemplateId(t.id); setBody(t.text); }}
                style={{ flexShrink: 0, padding: '8px 12px', borderRadius: 999,
                  background: templateId === t.id ? SoS.orange : SoS.creamDeep,
                  color: templateId === t.id ? '#fff' : SoS.ink,
                  border: `1.5px solid ${templateId === t.id ? SoS.orange : SoS.lineSoft}`,
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                  transition: 'all 0.15s', whiteSpace: 'nowrap' }}>
                {t.emoji} {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Besked-felt */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            marginBottom: 10 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
              letterSpacing: 0.8, textTransform: 'uppercase' }}>Besked *</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: body.length > 400 ? SoS.orange : SoS.inkMuted }}>
              {body.length} tegn
            </div>
          </div>
          <textarea value={body} onChange={e => { setBody(e.target.value); setTemplateId(null); }}
            placeholder="Skriv din besked her..."
            style={{ width: '100%', minHeight: 110, padding: '10px 0',
              border: 'none', outline: 'none', fontFamily: SoS.sans, fontSize: 14,
              color: SoS.ink, background: 'transparent', resize: 'vertical',
              lineHeight: 1.5, boxSizing: 'border-box' }}/>
        </div>

        {/* Urgent toggle */}
        <button onClick={() => setUrgent(!urgent)} style={{
          display: 'flex', alignItems: 'center', gap: 14, background: '#fff',
          borderRadius: SoS.r.lg, padding: '14px 16px', width: '100%',
          border: `1px solid ${urgent ? '#D64545' : SoS.lineSoft}`,
          cursor: 'pointer', textAlign: 'left', transition: 'border-color 0.2s' }}>
          <div style={{ width: 42, height: 24, borderRadius: 12, position: 'relative',
            background: urgent ? '#D64545' : SoS.lineSoft, transition: 'background 0.2s', flexShrink: 0 }}>
            <div style={{ position: 'absolute', top: 2,
              left: urgent ? 20 : 2, width: 20, height: 20, borderRadius: 10,
              background: '#fff', transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }}/>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
              color: urgent ? '#D64545' : SoS.ink }}>
              ⚑ Markér som vigtig
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
              Brobyggerne ser et rødt flag i deres indbakke
            </div>
          </div>
        </button>

        {/* Forhåndsvisning-note */}
        {canSend && (
          <div style={{ display: 'flex', gap: 10, padding: '10px 14px',
            background: SoS.sageSoft, borderRadius: SoS.r.md, alignItems: 'flex-start' }}>
            <Icon name="bell" size={14} color={SoS.sage} style={{ marginTop: 2 }}/>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.sage, lineHeight: 1.5 }}>
              {scope === 'een'
                ? `${selectedBb?.name} modtager en notifikation og kan se beskeden i sin indbakke.`
                : `${recipientCount} brobyggere modtager hver en notifikation. Fællesbeskeder kan ikke besvares direkte.`}
            </div>
          </div>
        )}

        <Button full
          style={{ opacity: canSend ? 1 : 0.4, cursor: canSend ? 'pointer' : 'default', marginTop: 4 }}
          onClick={canSend ? handleSend : undefined}>
          {scope === 'een'
            ? (selectedBb ? `Send til ${selectedBb.name}` : 'Vælg modtager')
            : `Send til ${recipientCount} brobyggere`}
        </Button>
      </div>
    </div>
  );
};

// ── MessagesList ─────────────────────────────────────────────────────────
// role-aware: koordinator og admin ser brobygger-tråde + komponer-knap
const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose }) => {
  const isBrobygger = role === 'brobygger';
  const isAdmin     = role === 'admin';

  // Brobygger ser kun koordinator-tråde; koordinator/admin ser brobygger-tråde
  const threads = SoS_THREADS.filter(t =>
    isBrobygger ? !t.fromBrobygger : t.fromBrobygger || t.official
  );

  const ThreadRow = ({ t }) => (
    <button key={t.id} onClick={() => onOpen(t.id)} style={{
      display: 'flex', gap: 12, width: '100%', padding: 14,
      background: (t.unread || t.urgent) ? '#fff' : 'transparent',
      border: `1.5px solid ${t.urgent ? '#D64545' : 'transparent'}`,
      borderRadius: SoS.r.lg, cursor: 'pointer', textAlign: 'left',
      marginBottom: 4, boxShadow: t.unread ? SoS.shadow.sm : 'none',
      alignItems: 'center',
    }}>
      <div style={{ position: 'relative' }}>
        <Avatar initials={t.avatar} bg={t.paused ? '#BBB' : t.bg} size={48}/>
        {t.online && <div style={{
          position: 'absolute', bottom: 0, right: 0, width: 12, height: 12,
          borderRadius: 6, background: SoS.sage, border: '2px solid #fff',
        }}/>}
        {t.official && <div style={{
          position: 'absolute', bottom: -2, right: -2, width: 18, height: 18,
          borderRadius: 9, background: SoS.orange, border: '2px solid #fff',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}><Icon name="shield" size={10} color="#fff" weight={2.5}/></div>}
        {t.urgent && <div style={{
          position: 'absolute', bottom: -2, right: -2, width: 18, height: 18,
          borderRadius: 9, background: '#D64545', border: '2px solid #fff',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: SoS.sans, fontSize: 11, color: '#fff', fontWeight: 700,
        }}>!</div>}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: t.unread ? 700 : 600,
            color: t.urgent ? '#D64545' : SoS.ink }}>{t.withName}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11,
            color: t.urgent ? '#D64545' : (t.unread ? SoS.orange : SoS.inkMuted),
            fontWeight: (t.unread || t.urgent) ? 600 : 400 }}>{t.time}</div>
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
          {t.withRole}
          {t.paused && <span style={{ marginLeft: 6, color: '#E8A43E', fontWeight: 600 }}>· Pause</span>}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginTop: 4, gap: 8 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 13,
            color: t.urgent ? '#D64545' : (t.unread ? SoS.ink : SoS.inkSoft),
            fontWeight: (t.unread || t.urgent) ? 500 : 400,
            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
          }}>{t.proxied && '\u21b3 '}{t.urgent ? '\u26a0\ufe0f ' : ''}{t.last}</div>
          {t.unread > 0 && <div style={{
            minWidth: 20, height: 20, borderRadius: 10,
            background: t.urgent ? '#D64545' : SoS.orange,
            color: '#fff', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 6px',
          }}>{t.unread}</div>}
        </div>
      </div>
    </button>
  );

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, overflowY: 'auto', paddingBottom: 90 }}>
      <TopBar
        title="Beskeder"
        subtitle={isBrobygger ? 'Din koordinator' : (isAdmin ? 'Alle brobyggere' : 'Dine brobyggere')}
        bg={SoS.cream}
        trailing={
          <div style={{ display: 'flex', gap: 8 }}>
            {!isBrobygger && onCompose && (
              <button onClick={onCompose} style={{
                height: 40, padding: '0 14px', borderRadius: 20,
                background: SoS.orange, color: '#fff', border: 'none',
                display: 'flex', alignItems: 'center', gap: 6,
                fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                boxShadow: SoS.shadow.glow, cursor: 'pointer',
              }}>
                <Icon name="plus" size={16} color="#fff" weight={2.5}/>
                Ny besked
              </button>
            )}
            <button style={{
              width: 40, height: 40, borderRadius: 20, background: '#fff',
              border: 'none', boxShadow: SoS.shadow.sm, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}><Icon name="search" size={20} color={SoS.ink}/></button>
          </div>
        }/>

      <div style={{ padding: '8px 12px' }}>
        {threads.map(t => <ThreadRow key={t.id} t={t}/>)}
        {threads.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px 20px',
            fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft }}>
            Ingen beskeder endnu
          </div>
        )}
      </div>

      {/* Fodnote */}
      <div style={{ margin: '16px 20px', padding: 14, background: SoS.creamDeep,
        borderRadius: SoS.r.md, display: 'flex', gap: 10 }}>
        <Icon name="lock" size={16} color={SoS.orangeDeep}/>
        <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
          color: SoS.orangeDeep, lineHeight: 1.5 }}>
          {isBrobygger
            ? 'Al kommunikation går gennem din koordinator. Direkte kontakt til mennesker sker altid via koordinatoren for at beskytte begge parter.'
            : 'Fællesbeskeder kan ikke besvares af modtagerne. Brug individuelle tråde til dialog.'}
        </div>
      </div>
    </div>
  );
};

// ── MessageThread ─────────────────────────────────────────────────────────
// role-aware: read-only fællesbeskeder; dynamisk placeholder
const MessageThread = ({ threadId, onBack, role }) => {
  const thread    = SoS_THREADS.find(t => t.id === threadId) || SoS_THREADS[0];
  const [draft, setDraft] = React.useState('');
  const [sent,  setSent]  = React.useState(false);
  const isReadOnly = thread.official; // Fællesbeskeder kan ikke besvares

  const placeholder = thread.fromBrobygger
    ? `Svar til ${thread.withName}...`
    : `Skriv til ${thread.withName}...`;

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 12px', background: '#fff',
        borderBottom: `1px solid ${thread.urgent ? '#D64545' : SoS.line}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none',
          padding: 4, cursor: 'pointer' }}>
          <Icon name="chevronL" size={22} color={SoS.ink}/>
        </button>
        <Avatar initials={thread.avatar} bg={thread.paused ? '#BBB' : thread.bg} size={40}/>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
              color: thread.urgent ? '#D64545' : SoS.ink }}>
              {thread.withName}
            </div>
            {thread.urgent && (
              <span style={{ background: '#D64545', color: '#fff', fontFamily: SoS.sans,
                fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 999 }}>
                VIGTIG
              </span>
            )}
            {thread.official && (
              <span style={{ background: SoS.orange + '20', color: SoS.orange,
                fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                padding: '2px 7px', borderRadius: 999 }}>
                FÆLLESBESKED
              </span>
            )}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
            {thread.online ? '\u25cf Online' : thread.withRole}
            {thread.paused && ' \u00b7 På pause'}
          </div>
        </div>
        {!isReadOnly && (
          <button style={{ background: 'none', border: 'none', padding: 4, cursor: 'pointer' }}>
            <Icon name="phone" size={20} color={SoS.orange}/>
          </button>
        )}
      </div>

      {/* Beskeder */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 8px' }}>
        <div style={{ textAlign: 'center', margin: '8px 0 16px' }}>
          <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
            background: SoS.creamDeep, padding: '4px 10px', borderRadius: 999 }}>
            I dag
          </span>
        </div>

        {isReadOnly ? (
          // Fællesbesked — read-only visning
          <div style={{ margin: '0 auto', maxWidth: '88%' }}>
            <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: '14px 16px',
              boxShadow: SoS.shadow.sm, border: `1px solid ${SoS.lineSoft}` }}>
              <div style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
                <Avatar initials={thread.avatar} bg={thread.bg} size={32}/>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: SoS.ink }}>
                    {thread.withName}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                    {thread.withRole}
                  </div>
                </div>
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink, lineHeight: 1.6 }}>
                {thread.last}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 10 }}>
                {thread.time} \u00b7 L\u00e6st
              </div>
            </div>
            <div style={{ textAlign: 'center', marginTop: 16, fontFamily: SoS.sans,
              fontSize: 12, color: SoS.inkSoft }}>
              Fællesbeskeder kan ikke besvares
            </div>
          </div>
        ) : (
          SoS_MESSAGES.map(m => {
            const mine = m.from === 'me';
            return (
              <div key={m.id} style={{
                display: 'flex', justifyContent: mine ? 'flex-end' : 'flex-start',
                marginBottom: 6,
              }}>
                <div style={{
                  maxWidth: '78%', padding: '10px 14px',
                  borderRadius: mine
                    ? `${SoS.r.lg}px ${SoS.r.lg}px 6px ${SoS.r.lg}px`
                    : `${SoS.r.lg}px ${SoS.r.lg}px ${SoS.r.lg}px 6px`,
                  background: mine ? SoS.orange : '#fff',
                  color: mine ? '#fff' : SoS.ink,
                  fontFamily: SoS.sans, fontSize: 14, lineHeight: 1.4,
                  boxShadow: mine ? 'none' : SoS.shadow.sm,
                }}>
                  {m.text}
                  <div style={{ fontSize: 10, marginTop: 4,
                    opacity: mine ? 0.7 : 0.5, fontWeight: 400 }}>
                    {m.time}{mine && ' \u00b7 L\u00e6st'}
                  </div>
                </div>
              </div>
            );
          })
        )}

        {!isReadOnly && (
          <div style={{ display: 'flex', gap: 4, padding: '8px 14px', alignItems: 'center' }}>
            <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
              animation: 'typing 1.4s infinite', animationDelay: '0s' }}/>
            <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
              animation: 'typing 1.4s infinite', animationDelay: '0.2s' }}/>
            <div style={{ width: 6, height: 6, borderRadius: 3, background: SoS.inkMuted,
              animation: 'typing 1.4s infinite', animationDelay: '0.4s' }}/>
            <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginLeft: 4 }}>
              {thread.withName.split(' ')[0]} skriver...
            </span>
          </div>
        )}
        <style>{\`@keyframes typing {
          0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
          30% { opacity: 1; transform: translateY(-3px); }
        }\`}</style>
      </div>

      {/* Composer (kun ikke read-only) */}
      {!isReadOnly && (
        <div style={{ padding: '12px 16px 30px', background: '#fff',
          borderTop: `1px solid ${SoS.line}`,
          display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <div style={{ flex: 1, background: SoS.creamDeep, borderRadius: 22,
            padding: '10px 14px', minHeight: 38 }}>
            <textarea value={draft} onChange={e => setDraft(e.target.value)}
              placeholder={placeholder} rows={1}
              style={{ width: '100%', background: 'transparent', border: 'none',
                outline: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                resize: 'none' }}/>
          </div>
          <button onClick={() => { if (draft.trim()) { setSent(true); setDraft(''); setTimeout(() => setSent(false), 2000); } }}
            style={{ width: 38, height: 38, borderRadius: 19,
            background: draft ? SoS.orange : SoS.creamDeep, border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            transition: 'background 0.2s' }}>
            <Icon name={sent ? 'check' : 'chevron'} size={18}
              color={draft || sent ? '#fff' : SoS.inkMuted} weight={2.5}/>
          </button>
        </div>
      )}
    </div>
  );
};

window.MessagesList = MessagesList;"""

cnt = html.count(OLD_MSG_BLOCK)
html = html.replace(OLD_MSG_BLOCK, NEW_MSG_BLOCK, 1)
results.append(('ComposeMessage + MessagesList + MessageThread erstattet', cnt, 1))

# ============================================================
# 3. App: tilføj msgCompose-state
# ============================================================
OLD_APP_STATE = '  const [msgOpenId, setMsgOpenId] = useState(null);'
NEW_APP_STATE = """  const [msgOpenId,   setMsgOpenId]   = useState(null);
  const [msgCompose,  setMsgCompose]  = useState(false);"""

cnt = html.count(OLD_APP_STATE)
html = html.replace(OLD_APP_STATE, NEW_APP_STATE, 1)
results.append(('App: msgCompose state', cnt, 1))

# ============================================================
# 4. App: opdater notif-screen render med role + compose
# ============================================================
OLD_NOTIF_RENDER = """          {screen === "notif" && (
            msgOpenId
              ? <MessageThread threadId={msgOpenId} onBack={() => setMsgOpenId(null)} />
              : <MessagesList onOpen={(id) => setMsgOpenId(id)} />
          )}"""

NEW_NOTIF_RENDER = """          {screen === "notif" && (
            msgCompose
              ? <ComposeMessage
                  role={tweaks.role}
                  ownHq={viewingHq}
                  onClose={() => setMsgCompose(false)}
                />
              : msgOpenId
              ? <MessageThread
                  threadId={msgOpenId}
                  role={tweaks.role}
                  onBack={() => setMsgOpenId(null)}
                />
              : <MessagesList
                  onOpen={(id) => setMsgOpenId(id)}
                  onCompose={() => setMsgCompose(true)}
                  role={tweaks.role}
                  ownHq={viewingHq}
                />
          )}"""

cnt = html.count(OLD_NOTIF_RENDER)
html = html.replace(OLD_NOTIF_RENDER, NEW_NOTIF_RENDER, 1)
results.append(('App: notif-screen render opdateret', cnt, 1))

# ============================================================
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 and after == 1 else f'[WARN] before={before} after={after}'
    print(f'{status} {label}')

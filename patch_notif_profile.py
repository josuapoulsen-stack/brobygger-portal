# -*- coding: utf-8 -*-
"""
patch_notif_profile.py
1. MessagesList: tilføj faner Notifikationer | Beskeder
   - Notifikationer viser SoS_NOTIFICATIONS (nye aftaler, påmindelser, systembesked)
   - Beskeder viser nuværende tråd-liste
2. ProfileScreen: erstat "kommer snart" med rigtige undersider
   - Notifikationer: push-toggles
   - Personlige oplysninger: navn/telefon/email/start
   - Præferencer, Privatliv, Sprog: informative (ikke bare toast)
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ─────────────────────────────────────────────────────────────────────
# 1. MessagesList — fane-baseret notif + beskeder
# ─────────────────────────────────────────────────────────────────────
OLD_ML = """const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose }) => (
  <div style={{ position: 'absolute', inset: 0, background: SoS.cream, overflowY: 'auto', paddingBottom: 90 }}>
    <div style={{ padding: '54px 16px 10px', background: '#fff',
      borderBottom: `1px solid ${SoS.line}`,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500, color: SoS.ink }}>Beskeder</div>
      <div style={{ display: 'flex', gap: 8 }}>
        {role && role !== 'brobygger' && onCompose && (
          <button onClick={onCompose} style={{
            width: 40, height: 40, borderRadius: 20, background: SoS.orange, border: 'none',
            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: SoS.shadow.glow,
          }}><Icon name="plus" size={20} color="#fff" weight={2.5}/></button>
        )}
        <button style={{ width: 40, height: 40, borderRadius: 20, background: '#fff',
          border: 'none', boxShadow: SoS.shadow.sm, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}><Icon name="search" size={20} color={SoS.ink}/></button>
      </div>
    </div>

    <div style={{ padding: '8px 12px' }}>
      {SoS_THREADS.map(t => ("""

NEW_ML = """const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose }) => {
  const [tab, setTab] = React.useState('notifikationer');
  const NOTIF_ICON  = { match: 'match', reminder: 'clock', message: 'bell' };
  const NOTIF_COLOR = { match: SoS.orange, reminder: SoS.sage, message: SoS.sky };
  const unread = SoS_NOTIFICATIONS.filter(n => n.unread).length;

  return (
  <div style={{ position: 'absolute', inset: 0, background: SoS.cream, display: 'flex', flexDirection: 'column' }}>
    {/* Header */}
    <div style={{ padding: '54px 16px 0', background: '#fff',
      borderBottom: `1px solid ${SoS.line}`, flexShrink: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500, color: SoS.ink }}>Beskeder</div>
        <div style={{ display: 'flex', gap: 8 }}>
          {role && role !== 'brobygger' && onCompose && (
            <button onClick={onCompose} style={{
              width: 40, height: 40, borderRadius: 20, background: SoS.orange, border: 'none',
              cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: SoS.shadow.glow,
            }}><Icon name="plus" size={20} color="#fff" weight={2.5}/></button>
          )}
        </div>
      </div>
      {/* Fane-vælger */}
      <div style={{ display: 'flex', gap: 0, marginBottom: 0 }}>
        {[
          { id: 'notifikationer', label: 'Notifikationer', badge: unread },
          { id: 'beskeder',       label: 'Beskeder',       badge: SoS_THREADS.filter(t => t.unread > 0).length },
        ].map(f => (
          <button key={f.id} onClick={() => setTab(f.id)} style={{
            flex: 1, padding: '10px 0 12px', background: 'none', border: 'none',
            borderBottom: `2.5px solid ${tab === f.id ? SoS.orange : 'transparent'}`,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: tab === f.id ? 700 : 400,
            color: tab === f.id ? SoS.orange : SoS.inkSoft,
            cursor: 'pointer', position: 'relative',
          }}>
            {f.label}
            {f.badge > 0 && (
              <span style={{ marginLeft: 6, background: SoS.orange, color: '#fff',
                fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                borderRadius: 999, padding: '1px 6px' }}>{f.badge}</span>
            )}
          </button>
        ))}
      </div>
    </div>

    {/* Indhold */}
    <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 90 }}>

    {/* ── NOTIFIKATIONER ── */}
    {tab === 'notifikationer' && (
      <div style={{ padding: '8px 16px 16px' }}>
        {SoS_NOTIFICATIONS.length === 0 && (
          <div style={{ padding: 32, textAlign: 'center', fontFamily: SoS.sans,
            fontSize: 13, color: SoS.inkMuted }}>Ingen notifikationer</div>
        )}
        {SoS_NOTIFICATIONS.map(n => (
          <div key={n.id} style={{
            display: 'flex', gap: 12, padding: '14px 16px', marginBottom: 8,
            background: n.unread ? '#fff' : 'transparent',
            borderRadius: SoS.r.lg,
            boxShadow: n.unread ? SoS.shadow.sm : 'none',
            border: `1px solid ${n.unread ? SoS.lineSoft : 'transparent'}`,
            alignItems: 'flex-start',
          }}>
            <div style={{ width: 40, height: 40, borderRadius: 20, flexShrink: 0,
              background: (NOTIF_COLOR[n.type] || SoS.orange) + '18',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name={NOTIF_ICON[n.type] || 'bell'} size={20}
                color={NOTIF_COLOR[n.type] || SoS.orange}/>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between',
                alignItems: 'baseline', marginBottom: 2 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14,
                  fontWeight: n.unread ? 700 : 500, color: SoS.ink }}>
                  {n.title}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11,
                  color: SoS.inkMuted, flexShrink: 0, marginLeft: 8 }}>{n.time}</div>
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
                lineHeight: 1.4 }}>{n.body}</div>
              {n.type === 'match' && n.unread && (
                <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                  <button style={{ flex: 1, padding: '8px 0', background: SoS.orange,
                    color: '#fff', border: 'none', borderRadius: SoS.r.sm,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                    Se aftale
                  </button>
                  <button style={{ flex: 1, padding: '8px 0', background: SoS.creamDeep,
                    color: SoS.ink, border: 'none', borderRadius: SoS.r.sm,
                    fontFamily: SoS.sans, fontSize: 13, cursor: 'pointer' }}>
                    Afvis
                  </button>
                </div>
              )}
            </div>
            {n.unread && <div style={{ width: 8, height: 8, borderRadius: 4,
              background: SoS.orange, flexShrink: 0, marginTop: 6 }}/>}
          </div>
        ))}
      </div>
    )}

    {/* ── BESKEDER ── */}
    {tab === 'beskeder' && (
    <div style={{ padding: '8px 12px' }}>
      {SoS_THREADS.map(t => ("""

cnt = html.count(OLD_ML)
html = html.replace(OLD_ML, NEW_ML, 1)
results.append(('MessagesList: notif+besked faner', cnt, 1))

# Also need to close the new JSX structure — the old component ends with );\n
# We need to close the new tab div and the outer div
OLD_ML_END = """    <div style={{ margin: '8px 20px 16px', padding: 14, background: SoS.creamDeep,
      borderRadius: SoS.r.md, display: 'flex', gap: 10 }}>
      <Icon name="lock" size={16} color={SoS.orangeDeep}/>
      <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
        color: SoS.orangeDeep, lineHeight: 1.5 }}>
        Al kommunikation til borgere sker via koordinator.
      </div>
    </div>
  </div>
);"""

NEW_ML_END = """    </div>
    )}

    </div>{/* end scrollable */}

    {/* Lås-note kun for beskeder */}
    {tab === 'beskeder' && (
      <div style={{ margin: '0 16px 16px', padding: 14, background: SoS.creamDeep,
        borderRadius: SoS.r.md, display: 'flex', gap: 10, flexShrink: 0 }}>
        <Icon name="lock" size={16} color={SoS.orangeDeep}/>
        <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
          color: SoS.orangeDeep, lineHeight: 1.5 }}>
          Al kommunikation til borgere sker via koordinator.
        </div>
      </div>
    )}
  </div>
  );
};"""

cnt = html.count(OLD_ML_END)
html = html.replace(OLD_ML_END, NEW_ML_END, 1)
results.append(('MessagesList: luk ny struktur', cnt, 1))

# ─────────────────────────────────────────────────────────────────────
# 2. ProfileScreen — funktionelle undersider
# ─────────────────────────────────────────────────────────────────────
OLD_PROFILE = """const ProfileScreen = ({ user, onSwitchRole }) => {
  const [toast, setToast] = React.useState(null);
  const showToast = (label) => { setToast(label); setTimeout(() => setToast(null), 2000); };
  return (
  <>
    <TopBar title="Profil" />
    <div style={{ padding: '0 20px 20px' }}>
      <div style={{ display: 'flex', gap: 16, alignItems: 'center',
        padding: 20, background: '#fff', borderRadius: SoS.r.xl,
        border: `1px solid ${SoS.lineSoft}`, marginBottom: 20 }}>
        <Avatar initials={user.avatar} bg={user.avatarBg} size={64} />
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
            color: SoS.ink, marginBottom: 2 }}>{user.name}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
            {user.role === 'brobygger' ? 'Brobygger' : 'Ansat'} · {user.hovedsaede}
          </div>
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: SoS.r.lg,
        border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>
        {[
          { icon: 'user', label: 'Personlige oplysninger' },
          { icon: 'heart', label: 'Mine præferencer' },
          { icon: 'shield', label: 'Privatliv & sikkerhed' },
          { icon: 'bell', label: 'Notifikationer' },
          { icon: 'language', label: 'Sprog' },
        ].map((row, i, arr) => (
          <div key={i} onClick={() => showToast(row.label)} style={{
            display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px',
            borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
            cursor: 'pointer',
          }}>
            <Icon name={row.icon} size={20} color={SoS.orange} />
            <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14,
              fontWeight: 500, color: SoS.ink }}>{row.label}</div>
            <Icon name="chevron" size={16} color={SoS.inkMuted} />
          </div>
        ))}
      </div>

      <Button full variant="secondary" onClick={onSwitchRole}>
        Skift til ansat-visning
      </Button>
    </div>
    {toast && (
      <div style={{ position: 'fixed', bottom: 90, left: '50%', transform: 'translateX(-50%)',
        background: SoS.ink, color: '#fff', padding: '12px 20px', borderRadius: 999,
        fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, zIndex: 999,
        boxShadow: '0 4px 20px rgba(0,0,0,0.2)', whiteSpace: 'nowrap' }}>
        {toast} — kommer snart
      </div>
    )}
  </>
  );
};"""

NEW_PROFILE = """const ProfileScreen = ({ user, onSwitchRole }) => {
  const [subPage, setSubPage] = React.useState(null);
  const [notifToggles, setNotifToggles] = React.useState({
    nyeAftaler: true, pamindelser: true, beskeder: true, systemOpdateringer: false,
  });
  const toggleNotif = (k) => setNotifToggles(p => ({ ...p, [k]: !p[k] }));

  const SubToggle = ({ label, sublabel, on, onToggle }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14,
      padding: '14px 16px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>{label}</div>
        {sublabel && <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>{sublabel}</div>}
      </div>
      <button onClick={onToggle} style={{
        width: 48, height: 28, borderRadius: 14,
        background: on ? SoS.sage : SoS.lineSoft,
        border: 'none', cursor: 'pointer', position: 'relative', flexShrink: 0,
        transition: 'background 0.2s',
      }}>
        <div style={{
          width: 20, height: 20, borderRadius: 10, background: '#fff',
          position: 'absolute', top: 4, left: on ? 24 : 4,
          transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
        }}/>
      </button>
    </div>
  );

  const BackHeader = ({ title }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4,
      padding: '54px 16px 12px', background: '#fff',
      borderBottom: `1px solid ${SoS.line}` }}>
      <button onClick={() => setSubPage(null)} style={{
        background: 'none', border: 'none', padding: 4, cursor: 'pointer',
      }}><Icon name="chevronL" size={22} color={SoS.ink}/></button>
      <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500,
        color: SoS.ink, marginLeft: 4 }}>{title}</div>
    </div>
  );

  // ── Notifikationer-underside
  if (subPage === 'notif') return (
    <>
      <BackHeader title="Notifikationer"/>
      <div style={{ padding: '0 0 20px' }}>
        <div style={{ padding: '14px 16px', fontFamily: SoS.sans, fontSize: 12,
          color: SoS.inkSoft, lineHeight: 1.5 }}>
          Vælg hvilke notifikationer du vil modtage på din telefon.
        </div>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', margin: '0 20px 20px' }}>
          <SubToggle label="Nye aftaleforslag"
            sublabel="Når koordinatoren foreslår en ny brobygning"
            on={notifToggles.nyeAftaler} onToggle={() => toggleNotif('nyeAftaler')}/>
          <SubToggle label="Påmindelser"
            sublabel="Dagen før og morgenen for en aftale"
            on={notifToggles.pamindelser} onToggle={() => toggleNotif('pamindelser')}/>
          <SubToggle label="Nye beskeder"
            sublabel="Fra koordinator eller SoS"
            on={notifToggles.beskeder} onToggle={() => toggleNotif('beskeder')}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14,
            padding: '14px 16px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>Systemopdateringer</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>Portal-nyheder og vedligeholdelse</div>
            </div>
            <button onClick={() => toggleNotif('systemOpdateringer')} style={{
              width: 48, height: 28, borderRadius: 14,
              background: notifToggles.systemOpdateringer ? SoS.sage : SoS.lineSoft,
              border: 'none', cursor: 'pointer', position: 'relative', flexShrink: 0,
              transition: 'background 0.2s',
            }}>
              <div style={{
                width: 20, height: 20, borderRadius: 10, background: '#fff',
                position: 'absolute', top: 4,
                left: notifToggles.systemOpdateringer ? 24 : 4,
                transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
              }}/>
            </button>
          </div>
        </div>
        <div style={{ padding: '0 20px', fontFamily: SoS.sans, fontSize: 12,
          color: SoS.inkSoft, lineHeight: 1.5 }}>
          Push-notifikationer kræver at du har accepteret tilladelse i din telefon.
          Notifikationer sendes aldrig om natten (kl. 22–07).
        </div>
      </div>
    </>
  );

  // ── Personlige oplysninger-underside
  if (subPage === 'personlig') return (
    <>
      <BackHeader title="Personlige oplysninger"/>
      <div style={{ padding: '16px 20px 20px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
          {[
            { label: 'Navn', value: user.name },
            { label: 'Rolle', value: 'Brobygger' },
            { label: 'Hovedsæde', value: user.hovedsaede || 'Aarhus' },
            { label: 'Startdato', value: 'Oktober 2024' },
            { label: 'Email', value: 'maja.holmberg@socialsundhed.org' },
            { label: 'Telefon', value: '+45 23 45 67 89' },
          ].map((row, i, arr) => (
            <div key={i} style={{ padding: '13px 16px',
              borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 13,
                color: SoS.inkSoft }}>{row.label}</span>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500,
                color: SoS.ink }}>{row.value}</span>
            </div>
          ))}
        </div>
        <div style={{ padding: '12px 14px', background: SoS.creamDeep, borderRadius: SoS.r.md,
          fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
          For at ændre dine oplysninger skal du kontakte din koordinator.
        </div>
      </div>
    </>
  );

  // ── Privatliv & sikkerhed
  if (subPage === 'privatliv') return (
    <>
      <BackHeader title="Privatliv & sikkerhed"/>
      <div style={{ padding: '16px 20px 20px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
          {[
            { label: 'Databehandlingsaftale', value: 'Underskrevet' },
            { label: 'GDPR-samtykke', value: 'Accepteret' },
            { label: 'Kryptering', value: 'TLS 1.3 · SSL' },
            { label: 'Sidst logget ind', value: 'I dag, 08:42' },
          ].map((row, i, arr) => (
            <div key={i} style={{ padding: '13px 16px',
              borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{row.label}</span>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.sage }}>{row.value}</span>
            </div>
          ))}
        </div>
        <div style={{ padding: '12px 14px', background: '#FFF8F0',
          border: `1px solid ${SoS.orange}30`,
          borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 12,
          color: SoS.inkSoft, lineHeight: 1.5 }}>
          Dine persondata opbevares sikkert og behandles i henhold til GDPR.
          Kun koordinatorer i dit primære hovedsæde har adgang til dine oplysninger.
        </div>
      </div>
    </>
  );

  // ── Præferencer
  if (subPage === 'praeferencer') return (
    <>
      <BackHeader title="Mine præferencer"/>
      <div style={{ padding: '16px 20px 20px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
          {[
            { label: 'Brobygningstyper', value: 'Sundhed, Social' },
            { label: 'Max. aktive mennesker', value: '3' },
            { label: 'Transport', value: 'Bil, Cykel' },
            { label: 'Sprog', value: 'Dansk' },
          ].map((row, i, arr) => (
            <div key={i} style={{ padding: '13px 16px',
              borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{row.label}</span>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>{row.value}</span>
            </div>
          ))}
        </div>
        <div style={{ padding: '12px 14px', background: SoS.creamDeep,
          borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 12,
          color: SoS.inkSoft, lineHeight: 1.5 }}>
          Kontakt din koordinator for at opdatere dine præferencer.
        </div>
      </div>
    </>
  );

  // ── Hoved-profil
  return (
  <>
    <TopBar title="Profil" />
    <div style={{ padding: '0 20px 100px' }}>
      <div style={{ display: 'flex', gap: 16, alignItems: 'center',
        padding: 20, background: '#fff', borderRadius: SoS.r.xl,
        border: `1px solid ${SoS.lineSoft}`, marginBottom: 20 }}>
        <Avatar initials={user.avatar} bg={user.avatarBg} size={64} />
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
            color: SoS.ink, marginBottom: 2 }}>{user.name}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
            {user.role === 'brobygger' ? 'Brobygger' : 'Ansat'} · {user.hovedsaede || 'Aarhus'}
          </div>
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: SoS.r.lg,
        border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 20 }}>
        {[
          { icon: 'user',     label: 'Personlige oplysninger', key: 'personlig' },
          { icon: 'heart',    label: 'Mine præferencer',       key: 'praeferencer' },
          { icon: 'shield',   label: 'Privatliv & sikkerhed',  key: 'privatliv' },
          { icon: 'bell',     label: 'Notifikationer',         key: 'notif' },
        ].map((row, i, arr) => (
          <div key={i} onClick={() => setSubPage(row.key)} style={{
            display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px',
            borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
            cursor: 'pointer',
          }}>
            <Icon name={row.icon} size={20} color={SoS.orange} />
            <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14,
              fontWeight: 500, color: SoS.ink }}>{row.label}</div>
            <Icon name="chevron" size={16} color={SoS.inkMuted} />
          </div>
        ))}
      </div>

      <Button full variant="secondary" onClick={onSwitchRole}>
        Skift til ansat-visning
      </Button>
    </div>
  </>
  );
};"""

cnt = html.count(OLD_PROFILE)
html = html.replace(OLD_PROFILE, NEW_PROFILE, 1)
results.append(('ProfileScreen: undersider', cnt, 1))

# ─────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

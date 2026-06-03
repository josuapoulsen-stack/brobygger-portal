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
# 1. Mobil appts — filtrer til brobygger bb-1 (Maja Holmberg)
# ═══════════════════════════════════════════════════════════════════════════
sub(
    'const appts = (activeRole === "brobygger" && !isBusy) ? SoS_APPOINTMENTS_EMPTY : SoS_APPOINTMENTS_BUSY;',
    """const _bbId = activeRole === 'brobygger'
    ? (SoS_BROBYGGERE.find(b => b.id === 'bb-1') || SoS_BROBYGGERE[0])?.id
    : null;
  const appts = (activeRole === 'brobygger' && !isBusy)
    ? SoS_APPOINTMENTS_EMPTY
    : (activeRole === 'brobygger'
        ? SoS_APPOINTMENTS_BUSY.filter(a => a.brobyggerId === _bbId)
        : SoS_APPOINTMENTS_BUSY);""",
    "Mobil: filtrer appts til brobyggerens egne aftaler"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2a. AppointmentDetailScreen — tilføj showLog state + aflysAarsag state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [showCancel, setShowCancel] = React.useState(false);
  const [cancelled, setCancelled] = React.useState(false);""",
    """  const [showCancel, setShowCancel] = React.useState(false);
  const [cancelled, setCancelled] = React.useState(false);
  const [showLog, setShowLog] = React.useState(false);
  const [aflysAarsag, setAflysAarsag] = React.useState(null);""",
    "AppointmentDetailScreen: showLog + aflysAarsag state"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2b. AppointmentDetailScreen — Registrér-knap åbner BrobyggerLogModal
#     Tilføj også Registrér-knap for fortidige aftaler
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """        {isToday(appt.date) ? (
          <Button full onClick={onComplete}
            icon={<Icon name="check" size={18} color="#fff" weight={2.5} />}>
            Registrér efter aftale
          </Button>
        ) : (
          <>
            <Button full variant="secondary"
              onClick={() => alert(`Ring ${menneske.contact.name}: ${menneske.contact.phone}`)}
              icon={<Icon name="phone" size={16} color={SoS.ink} weight={2} />}>
              Ring koordinator: {menneske.contact.phone}
            </Button>
            <Button full variant="ghost"
              onClick={() => se""",
    """        {(isToday(appt.date) || appt.date < new Date().toISOString().slice(0,10)) && !appt.brobyggerLog && (
          <Button full onClick={() => setShowLog(true)}
            icon={<Icon name="check" size={18} color="#fff" weight={2.5} />}>
            {isToday(appt.date) ? 'Registrér efter aftale' : 'Registrér kontakt'}
          </Button>
        )}
        {!isToday(appt.date) && appt.date >= new Date().toISOString().slice(0,10) && (
          <>
            <Button full variant="secondary"
              onClick={() => alert(`Ring ${menneske.contact.name}: ${menneske.contact.phone}`)}
              icon={<Icon name="phone" size={16} color={SoS.ink} weight={2} />}>
              Ring koordinator: {menneske.contact.phone}
            </Button>
            <Button full variant="ghost"
              onClick={() => se""",
    "AppointmentDetailScreen: Registrér knap for fortid + i dag"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2c. AppointmentDetailScreen — vis BrobyggerLogModal
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """      {cancelled && (""",
    """      {showLog && (
        <BrobyggerLogModal
          aftale={appt}
          onClose={() => setShowLog(false)}
          onSave={(log) => {
            const updAppts = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>
              a.id === appt.id ? { ...a, brobyggerLog: log } : a
            );
            window.SoS_APPOINTMENTS_BUSY = updAppts;
            window.SoS_STORE?.save('appointments', updAppts);
            setShowLog(false);
            onComplete?.();
          }}
        />
      )}
      {cancelled && (""",
    "AppointmentDetailScreen: vis BrobyggerLogModal"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2d. AppointmentDetailScreen — tilføj årsag-vælger i aflys-modal
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """            <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
              lineHeight: 1.5, marginBottom: 24 }}>
              Din koordinator bliver informeret. Aftalen fjernes fra din kalender.
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Button full variant="secondary" onClick={() => setShowCancel(false)}>
                Behold aftale
              </Button>
              <Button full onClick={() => { setCancelled(true); setShowCancel(false); }}
                style={{ background: SoS.rose, color: '#fff' }}>
                Bekræft aflysning
              </Button>
            </div>""",
    """            <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
              lineHeight: 1.5, marginBottom: 16 }}>
              Din koordinator bliver informeret. Aftalen fjernes fra din kalender.
            </div>
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                color: SoS.ink, marginBottom: 8 }}>Årsag til aflysning</div>
              {[
                { id: 'mennesket',  label: 'Aflyst af mennesket' },
                { id: 'brobygger',  label: 'Aflyst af mig (brobygger)' },
                { id: 'sygdom',     label: 'Sygdom / nødsituation' },
                { id: 'koordinator',label: 'Aftalt med koordinator' },
                { id: 'andet',      label: 'Andet' },
              ].map(a => (
                <button key={a.id} onClick={() => setAflysAarsag(a.id)} style={{
                  display: 'block', width: '100%', textAlign: 'left',
                  padding: '10px 14px', marginBottom: 6,
                  background: aflysAarsag === a.id ? SoS.rose + '18' : SoS.cream,
                  border: `1px solid ${aflysAarsag === a.id ? SoS.rose : SoS.line}`,
                  borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 13,
                  color: aflysAarsag === a.id ? SoS.rose : SoS.ink,
                  fontWeight: aflysAarsag === a.id ? 600 : 400,
                }}>
                  {a.label}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Button full variant="secondary" onClick={() => { setShowCancel(false); setAflysAarsag(null); }}>
                Behold aftale
              </Button>
              <Button full onClick={() => { setCancelled(true); setShowCancel(false); }}
                disabled={!aflysAarsag}
                style={{ background: aflysAarsag ? SoS.rose : SoS.lineSoft,
                  color: '#fff', opacity: aflysAarsag ? 1 : 0.6 }}>
                Bekræft aflysning
              </Button>
            </div>""",
    "AppointmentDetailScreen: aflys-årsag vælger"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. IntakeFlow — tilføj sprog-felt (state + UI + save)
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [kpType,      setKpType]      = React.useState(null);
  const [kpNavn,      setKpNavn]      = React.useState('');
  const [kpTlf,       setKpTlf]       = React.useState('');
  const [behovUrgency, setBehovUrgency] = React.useState('');""",
    """  const [kpType,      setKpType]      = React.useState(null);
  const [kpNavn,      setKpNavn]      = React.useState('');
  const [kpTlf,       setKpTlf]       = React.useState('');
  const [sprog,       setSprog]       = React.useState('Dansk');
  const [behovUrgency, setBehovUrgency] = React.useState('');""",
    "IntakeFlow: sprog state"
)

sub(
    "address:      '', meetPoint: '', language: 'Dansk',",
    "address:      '', meetPoint: '', language: sprog || 'Dansk',",
    "IntakeFlow: brug sprog state i newPerson"
)

sub(
    """            {/* Kontaktperson */}
            <div style={{ marginBottom: 6 }}>""",
    """            {/* Sprog */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink, marginBottom: 8 }}>
                Primært sprog <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, fontWeight: 400 }}>— valgfri</span>
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {['Dansk','Arabisk','Somalisk','Tyrkisk','Farsi','Polsk','Urdu','Andet'].map(s => (
                  <button key={s} onClick={() => setSprog(sprog === s ? 'Dansk' : s)} style={{
                    padding: '7px 14px', borderRadius: SoS.r.md, cursor: 'pointer',
                    fontFamily: SoS.sans, fontSize: 13,
                    background: sprog === s ? SoS.orange : SoS.cream,
                    color: sprog === s ? '#fff' : SoS.ink,
                    border: `1px solid ${sprog === s ? SoS.orange : SoS.line}`,
                    fontWeight: sprog === s ? 600 : 400,
                  }}>{s}</button>
                ))}
              </div>
            </div>

            {/* Kontaktperson */}
            <div style={{ marginBottom: 6 }}>""",
    "IntakeFlow: sprog chip-vælger i basisinfo step"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. DesktopKalender — tilføj bbDetaljeId state + klikbar bb-avatar
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [udfaldsModal, setUdfaldsModal] = React.useState(null);

  const saveAppt""",
    """  const [udfaldsModal, setUdfaldsModal] = React.useState(null);
  const [bbDetaljeId, setBbDetaljeId] = React.useState(null);

  const saveAppt""",
    "DesktopKalender: bbDetaljeId state"
)

sub(
    """        {bb && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ width: 28, height: 28, borderRadius: 0, background: bb.bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 3px', fontFamily: SoS.mono, fontSize: 10,
              fontWeight: 700, color: '#fff' }}>{bb.avatar}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 9, color: SoS.inkMuted }}>{bb.name.split(' ')[0]}</div>
          </div>
        )}""",
    """        {bb && (
          <div title={bb.name} onClick={e => { e.stopPropagation(); setBbDetaljeId(bb.id); }}
            style={{ textAlign: 'center', cursor: 'pointer' }}>
            <div style={{ width: 28, height: 28, borderRadius: 14, background: bb.bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 3px', fontFamily: SoS.mono, fontSize: 10,
              fontWeight: 700, color: '#fff',
              boxShadow: '0 0 0 2px ' + bb.bg + '44' }}>{bb.avatar}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 9, color: SoS.inkMuted }}>{bb.name.split(' ')[0]}</div>
          </div>
        )}""",
    "DesktopKalender: bb-avatar klikbar"
)

sub(
    """  );\n};\n\nconst DesktopRapport = () => {""",
    """      {/* ── Brobygger-detaljepanel ── */}
      {bbDetaljeId && (() => {
        const bbD = SoS_BROBYGGERE.find(b => b.id === bbDetaljeId);
        if (!bbD) return null;
        const bbAppts = (window.SoS_APPOINTMENTS_BUSY || []).filter(a => a.brobyggerId === bbD.id);
        const bekr = bbAppts.filter(a => a.status === 'confirmed').length;
        const afholdt = bbAppts.filter(a => a.date < '2026-04-26' && a.brobyggerLog).length;
        return (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
            zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            onClick={() => setBbDetaljeId(null)}>
            <div style={{ background: '#fff', borderRadius: SoS.r.xl, width: 400,
              maxHeight: '80vh', overflow: 'auto', boxShadow: SoS.shadow.lg }}
              onClick={e => e.stopPropagation()}>
              {/* Header */}
              <div style={{ background: `linear-gradient(135deg, ${bbD.bg}22, ${bbD.bg}44)`,
                padding: '28px 28px 20px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 12 }}>
                  <div style={{ width: 60, height: 60, borderRadius: 30, background: bbD.bg,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: SoS.mono, fontSize: 20, fontWeight: 700, color: '#fff' }}>
                    {bbD.avatar}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink }}>{bbD.name}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                      {bbD.status === 'aktiv' ? '🟢 Aktiv' : bbD.status === 'pause' ? '⏸️ Pause' : bbD.status}
                      {bbD.pauseUntil && ` · pause til ${bbD.pauseUntil}`}
                    </div>
                  </div>
                  <button onClick={() => setBbDetaljeId(null)} style={{
                    width: 32, height: 32, borderRadius: 16, background: SoS.creamDeep,
                    border: 'none', cursor: 'pointer', display: 'flex',
                    alignItems: 'center', justifyContent: 'center' }}>
                    <Icon name="x" size={16} color={SoS.inkMuted}/>
                  </button>
                </div>
                <div style={{ display: 'flex', gap: 20 }}>
                  {[
                    { label: 'Aktive',    val: bbD.active },
                    { label: 'Bekræftede',val: bekr },
                    { label: 'Afholdt',   val: afholdt },
                    { label: 'Åbne vagter',val: bbD.openShifts },
                  ].map((s,i) => (
                    <div key={i} style={{ textAlign: 'center' }}>
                      <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 600, color: SoS.ink }}>{s.val}</div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkSoft }}>{s.label}</div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Kontaktinfo */}
              <div style={{ padding: '16px 28px' }}>
                {[
                  { icon: 'phone', label: bbD.mobil || '—' },
                  { icon: 'mail',  label: bbD.email || '—' },
                  { icon: 'calendar', label: `Startdato: ${bbD.startDate || '—'}` },
                  { icon: 'clock', label: `Sidst aktiv: ${bbD.lastActive || '—'}` },
                ].map((r,i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10,
                    paddingBottom: 10, marginBottom: 10,
                    borderBottom: i < 3 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                    <Icon name={r.icon} size={16} color={SoS.inkMuted}/>
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>{r.label}</span>
                  </div>
                ))}
              </div>
              {/* Kommende aftaler */}
              {bekr > 0 && (
                <div style={{ padding: '0 28px 24px' }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                    color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase',
                    marginBottom: 8 }}>Kommende aftaler ({bekr})</div>
                  {bbAppts.filter(a => a.status === 'confirmed' && a.date >= '2026-04-26').slice(0,4).map((a,i) => {
                    const m = SoS_MENNESKER[a.menneskeId];
                    return (
                      <div key={i} style={{ display: 'flex', gap: 10, padding: '8px 0',
                        borderBottom: `1px solid ${SoS.lineSoft}` }}>
                        <div style={{ fontFamily: SoS.mono, fontSize: 12, color: SoS.inkMuted, minWidth: 60 }}>
                          {a.date.slice(5)} {a.start}
                        </div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.ink }}>
                          {a.activity}{m ? ` · ${m.firstName}` : ''}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        );
      })()}
  );\n};\n\nconst DesktopRapport = () => {""",
    "DesktopKalender: brobygger-detaljepanel modal"
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

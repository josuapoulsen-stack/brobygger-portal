"""
patch_matching_flow.py
Rewrites MatchingFlow:
  - 4 steps: Menneske -> Tidspunkt -> Brobygger -> Bekraft
  - Match on TIME not just person
  - No notification to menneske (radgiver rings instead)
  - Brobygger still gets notification
  - Done screen shows "Ring og bekraft" task with contact info
  - Pushes task to window.PENDING_RING_TASKS

Also adds "Ring og bekraft" pending tasks section to AdminOverview,
and fixes the dead-end ActionCard for "aftale-noter".
"""
import sys

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────
# 1. REWRITE MatchingFlow
# ─────────────────────────────────────────────────────────
OLD_MF_START = 'const MatchingFlow = ({ onClose }) => {'
OLD_MF_END   = 'const OnboardingWizard'

if OLD_MF_START not in html or OLD_MF_END not in html:
    sys.exit('ERROR: MatchingFlow anchors not found')

i1 = html.index(OLD_MF_START)
i2 = html.index(OLD_MF_END)

NEW_MF = r"""const MatchingFlow = ({ onClose }) => {
  const [step, setStep] = React.useState(0);
  const [done, setDone] = React.useState(false);
  const [menneskeId, setMenneskeId] = React.useState(null);
  const [brobyggerId, setBrobyggerId] = React.useState(null);

  // Step 1 state
  const [aftaleDato, setAftaleDato] = React.useState('2026-05-05');
  const [aftaleStart, setAftaleStart] = React.useState(null);
  const [aftaleDuration, setAftaleDuration] = React.useState(null);
  const [aftaleType, setAftaleType] = React.useState(null);
  const [aftaleSted, setAftaleSted] = React.useState('');

  const menneske = menneskeId ? SS_MENNESKER[menneskeId] : null;
  const type = menneske ? SS_TYPER[menneske.type] : null;
  const brobygger = brobyggerId ? SS_BROBYGGERE.find(b => b.id === brobyggerId) : null;

  const steps = ['Menneske', 'Tidspunkt', 'Brobygger', 'Bekraft'];

  const SLOTS = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00'];
  const DURATIONS = [
    { label: '30 min', v: 30 },
    { label: '1 time', v: 60 },
    { label: '1\u00bd time', v: 90 },
    { label: '2 timer', v: 120 },
  ];
  const AKTIVITETER = [
    { id: 'laege',    label: 'L\u00e6gebes\u00f8g',  icon: 'shield' },
    { id: 'hospital', label: 'Hospital',    icon: 'shield' },
    { id: 'indkob',   label: 'Indkob',     icon: 'search' },
    { id: 'tur',      label: 'G\u00e5tur',      icon: 'match'  },
    { id: 'forening', label: 'Forening',    icon: 'sparkle'},
    { id: 'andet',    label: 'Andet',       icon: 'heart'  },
  ];

  const canNext = (
    (step === 0 && menneskeId) ||
    (step === 1 && aftaleDato && aftaleStart && aftaleDuration && aftaleType) ||
    (step === 2 && brobyggerId) ||
    step === 3
  );

  const fmtDato = (d) => d ? new Date(d).toLocaleDateString('da-DK', { weekday: 'long', day: 'numeric', month: 'long' }) : '';

  const handleSend = () => {
    if (!window.PENDING_RING_TASKS) window.PENDING_RING_TASKS = [];
    window.PENDING_RING_TASKS.unshift({
      id: Date.now(),
      menneskeFirstName: menneske.firstName,
      menneskeLastInitial: menneske.lastName[0],
      menneskeContact: menneske.contact,
      brobyggerFirstName: brobygger.name.split(' ')[0],
      dato: aftaleDato,
      start: aftaleStart,
      duration: aftaleDuration,
      done: false,
    });
    setDone(true);
  };

  if (done) return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: 32 }}>
      <div style={{ width: 72, height: 72, borderRadius: 36, background: SoS.sageSoft,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
        <Icon name="check" size={32} color={SoS.sage} weight={2.5}/>
      </div>
      <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,
        color: SoS.ink, textAlign: 'center', marginBottom: 8 }}>
        Matching oprettet!
      </div>
      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        textAlign: 'center', lineHeight: 1.6, marginBottom: 24 }}>
        {brobygger.name.split(' ')[0]} modtager en besked om aftalen.
      </div>

      {/* Ring og bekraft task card */}
      <div style={{ width: '100%', background: '#fff', borderRadius: SoS.r.xl,
        padding: 20, border: `2px solid ${SoS.orange}33`, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
          <div style={{ width: 38, height: 38, borderRadius: 19,
            background: SoS.orange + '22', display: 'flex',
            alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="phone" size={18} color={SoS.orange}/>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: SoS.ink }}>
              Din opgave
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
              Skal gores snarest
            </div>
          </div>
          <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
            color: SoS.orange, background: SoS.orange + '18',
            padding: '3px 8px', borderRadius: 999 }}>Ventende</span>
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
          lineHeight: 1.6, marginBottom: 14 }}>
          Ring <strong>{menneske.firstName} {menneske.lastName[0]}.</strong> og bekraft aftalen med{' '}
          {brobygger.name.split(' ')[0]} — {fmtDato(aftaleDato)} kl. {aftaleStart}.
        </div>
        <div style={{ background: SoS.creamDeep, borderRadius: SoS.r.md,
          padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Icon name="phone" size={14} color={SoS.inkSoft}/>
          <div>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
              {menneske.contact.name}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, color: SoS.ink }}>
              {menneske.contact.phone}
            </div>
          </div>
        </div>
      </div>

      <Button full onClick={onClose}>Luk og ga til oversigt</Button>
    </div>
  );

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '54px 20px 12px', background: '#fff', borderBottom: `1px solid ${SoS.line}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.inkSoft }}>Afbryd</button>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 1, textTransform: 'uppercase' }}>
            Ny matching \u00b7 {step + 1}/{steps.length}
          </div>
          <div style={{ width: 60 }}/>
        </div>
        <StepDots step={step} total={steps.length}/>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>

        {/* ── Step 0: Valg menneske ── */}
        {step === 0 && (
          <>
            <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2 }}>Valg menneske</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 16 }}>
              Mennesker der venter pa match.
            </div>
            {Object.values(SS_MENNESKER).map(b => {
              const t = SS_TYPER[b.type];
              const sel = menneskeId === b.id;
              return (
                <button key={b.id} onClick={() => setMenneskeId(b.id)} style={{
                  display: 'flex', gap: 12, width: '100%', padding: 14,
                  marginBottom: 8, textAlign: 'left',
                  background: sel ? t.soft : '#fff',
                  border: `2px solid ${sel ? t.color : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, cursor: 'pointer',
                }}>
                  <Avatar initials={b.initials} bg={t.color} size={44}/>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                      {b.firstName} {b.lastName[0]}. ({b.age})
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                      {b.needs.slice(0,2).join(' \u00b7 ')}
                    </div>
                    <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                      <Pill bg={t.soft} color={t.color}>{t.short}</Pill>
                      <Pill bg={SoS.creamDeep} color={SoS.inkSoft}>{b.language.split(',')[0]}</Pill>
                    </div>
                  </div>
                </button>
              );
            })}
          </>
        )}

        {/* ── Step 1: Angiv tidspunkt ── */}
        {step === 1 && menneske && (
          <>
            <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
              color: SoS.ink, marginBottom: 4, letterSpacing: -0.2 }}>Angiv tidspunkt</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20, lineHeight: 1.5 }}>
              Hvornr har {menneske.firstName} brug for hjlp?
            </div>

            {/* Dato */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>Dato</div>
              <input type="date" value={aftaleDato} onChange={e => setAftaleDato(e.target.value)}
                style={{ width: '100%', padding: '12px 14px', fontFamily: SoS.sans, fontSize: 14,
                  color: SoS.ink, background: '#fff', border: `1.5px solid ${SoS.lineSoft}`,
                  borderRadius: SoS.r.md, outline: 'none', boxSizing: 'border-box' }}/>
            </div>

            {/* Starttidspunkt */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>Starttidspunkt</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {SLOTS.map(s => (
                  <button key={s} onClick={() => setAftaleStart(s)} style={{
                    padding: '8px 12px', borderRadius: SoS.r.md, cursor: 'pointer',
                    background: aftaleStart === s ? SoS.orange : '#fff',
                    color: aftaleStart === s ? '#fff' : SoS.ink,
                    border: `1.5px solid ${aftaleStart === s ? SoS.orange : SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                  }}>{s}</button>
                ))}
              </div>
            </div>

            {/* Varighed */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>Varighed</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {DURATIONS.map(d => (
                  <button key={d.v} onClick={() => setAftaleDuration(d.v)} style={{
                    padding: '8px 14px', borderRadius: SoS.r.md, cursor: 'pointer', flex: 1, minWidth: 80,
                    background: aftaleDuration === d.v ? SoS.orange : '#fff',
                    color: aftaleDuration === d.v ? '#fff' : SoS.ink,
                    border: `1.5px solid ${aftaleDuration === d.v ? SoS.orange : SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                  }}>{d.label}</button>
                ))}
              </div>
            </div>

            {/* Type aktivitet */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>Type aktivitet</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {AKTIVITETER.map(a => (
                  <button key={a.id} onClick={() => setAftaleType(a.id)} style={{
                    padding: '12px 14px', borderRadius: SoS.r.md, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', gap: 8, textAlign: 'left',
                    background: aftaleType === a.id ? SoS.orange + '18' : '#fff',
                    border: `1.5px solid ${aftaleType === a.id ? SoS.orange : SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink,
                  }}>
                    <Icon name={a.icon} size={16} color={aftaleType === a.id ? SoS.orange : SoS.inkMuted}/>
                    {a.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sted (valgfrit) */}
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
                Sted <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>
              </div>
              <input placeholder="Fx klinik, adresse eller m\u00f8dested"
                value={aftaleSted} onChange={e => setAftaleSted(e.target.value)}
                style={{ width: '100%', padding: '12px 14px', fontFamily: SoS.sans, fontSize: 14,
                  color: SoS.ink, background: '#fff', border: `1.5px solid ${SoS.lineSoft}`,
                  borderRadius: SoS.r.md, outline: 'none', boxSizing: 'border-box' }}/>
            </div>
          </>
        )}

        {/* ── Step 2: Valg brobygger ── */}
        {step === 2 && menneske && (() => {
          const available = SS_BROBYGGERE
            .filter(b => b.status === 'aktiv' || b.status === 'ny')
            .slice()
            .sort((a, b) => b.openShifts - a.openShifts);
          return (
            <>
              <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
                color: SoS.ink, marginBottom: 4, letterSpacing: -0.2 }}>Valg brobygger</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
                marginBottom: 16, lineHeight: 1.5 }}>
                Sorteret efter ledige vagter. Aftalen er{' '}
                {new Date(aftaleDato).toLocaleDateString('da-DK', { weekday: 'long', day: 'numeric', month: 'long' })}{' '}
                kl. {aftaleStart}.
              </div>
              {available.map(b => {
                const sel = brobyggerId === b.id;
                const hasShift = b.openShifts > 0;
                return (
                  <button key={b.id} onClick={() => setBrobyggerId(b.id)} style={{
                    display: 'flex', gap: 12, alignItems: 'center', width: '100%',
                    padding: 14, marginBottom: 8, textAlign: 'left', background: '#fff',
                    border: `2px solid ${sel ? SoS.orange : SoS.lineSoft}`,
                    borderRadius: SoS.r.md, cursor: 'pointer',
                    boxShadow: sel ? SoS.shadow.md : 'none',
                    opacity: !hasShift && !sel ? 0.55 : 1,
                  }}>
                    <Avatar initials={b.avatar} bg={b.bg} size={44}/>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                          {b.name}
                        </span>
                        {hasShift ? (
                          <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                            color: SoS.sage, background: SoS.sageSoft,
                            padding: '2px 7px', borderRadius: 999 }}>
                            {b.openShifts} ledige vagter
                          </span>
                        ) : (
                          <span style={{ fontFamily: SoS.sans, fontSize: 10,
                            color: SoS.inkMuted, background: SoS.lineSoft + '88',
                            padding: '2px 7px', borderRadius: 999 }}>
                            Ingen vagter
                          </span>
                        )}
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                        {b.active} aktive forl\u00f8b \u00b7 {b.thisMonth} aftaler denne mned
                      </div>
                    </div>
                    {sel && (
                      <div style={{ width: 24, height: 24, borderRadius: 12,
                        background: SoS.orange, display: 'flex',
                        alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <Icon name="check" size={14} color="#fff" weight={2.5}/>
                      </div>
                    )}
                  </button>
                );
              })}
            </>
          );
        })()}

        {/* ── Step 3: Bekraft ── */}
        {step === 3 && menneske && brobygger && (
          <>
            <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
              color: SoS.ink, marginBottom: 20, letterSpacing: -0.2 }}>Bekraft matching</div>

            <div style={{ background: '#fff', borderRadius: SoS.r.xl, padding: 24,
              border: `1px solid ${SoS.lineSoft}`, marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <Avatar initials={menneske.initials} bg={type.color} size={56}/>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    color: SoS.ink, marginTop: 8 }}>{menneske.firstName}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Menneske</div>
                </div>
                <Icon name="match" size={28} color={SoS.orange}/>
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <Avatar initials={brobygger.avatar} bg={brobygger.bg} size={56}/>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    color: SoS.ink, marginTop: 8 }}>{brobygger.name.split(' ')[0]}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Brobygger</div>
                </div>
              </div>

              <div style={{ paddingTop: 18, borderTop: `1px solid ${SoS.lineSoft}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Tidspunkt</span>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                    {new Date(aftaleDato).toLocaleDateString('da-DK', { day: 'numeric', month: 'short' })} kl. {aftaleStart}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Varighed</span>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                    {DURATIONS.find(d => d.v === aftaleDuration)?.label}
                  </span>
                </div>
                {aftaleSted ? (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Sted</span>
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{aftaleSted}</span>
                  </div>
                ) : null}
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Mennesketype</span>
                  <Pill bg={type.soft} color={type.color}>{type.label}</Pill>
                </div>
              </div>
            </div>

            {/* Brobygger fa besked */}
            <div style={{ padding: 14, background: SoS.sageSoft, borderRadius: SoS.r.md,
              display: 'flex', gap: 10, marginBottom: 10 }}>
              <Icon name="sparkle" size={18} color={SoS.sage}/>
              <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 12,
                color: SoS.sage, lineHeight: 1.5, fontWeight: 600 }}>
                {brobygger.name.split(' ')[0]} modtager en besked om aftalen.
              </div>
            </div>

            {/* Din opgave */}
            <div style={{ padding: 14, background: SoS.orange + '12', borderRadius: SoS.r.md,
              display: 'flex', gap: 10, border: `1px solid ${SoS.orange}30` }}>
              <Icon name="phone" size={18} color={SoS.orange}/>
              <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 12,
                color: SoS.orangeDeep, lineHeight: 1.6 }}>
                <strong>Din opgave:</strong> Ring {menneske.firstName} og bekraft aftalen.
                En pgmindelse vises i din oversigt, indtil du krydser den af.
              </div>
            </div>
          </>
        )}

      </div>

      {/* Footer */}
      <div style={{ padding: '16px 20px 34px', background: '#fff',
        borderTop: `1px solid ${SoS.line}`, display: 'flex', gap: 10 }}>
        {step > 0 && <Button variant="secondary" onClick={() => setStep(step - 1)}>Tilbage</Button>}
        <Button full onClick={() => step === 3 ? handleSend() : setStep(step + 1)}
          style={{ flex: 1, opacity: canNext ? 1 : 0.4, pointerEvents: canNext ? 'auto' : 'none' }}>
          {step === 3 ? 'Opret matching' : 'Fortsat'}
        </Button>
      </div>
    </div>
  );
};

"""

html = html[:i1] + NEW_MF + html[i2:]
print('[OK] MatchingFlow rewritten (4 steps + ring task)')

# ─────────────────────────────────────────────────────────
# 2. ADD "Ring og bekraft"-PENDING TASKS to AdminOverview
# ─────────────────────────────────────────────────────────
# Insert a pending tasks section right after the period selector div in AdminOverview

PERIOD_SELECTOR_END = (
    "        {['I dag', 'Uge', 'M\u00e5ned', 'Kvartal', '\u00c5r', 'Alt'].map((p, i) => (\n"
    "          <button key={p} style={{\n"
    "            padding: '8px 14px', borderRadius: 999, flexShrink: 0,\n"
    "            background: i === 2 ? SoS.ink : '#fff',\n"
    "            color: i === 2 ? '#fff' : SoS.ink,\n"
    "            border: i === 2 ? 'none' : `1px solid ${SoS.line}`,\n"
    "            fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',\n"
    "          }}>{p}</button>\n"
    "        ))}\n"
    "      </div>"
)

RING_TASKS_SECTION = (
    "        {['I dag', 'Uge', 'M\u00e5ned', 'Kvartal', '\u00c5r', 'Alt'].map((p, i) => (\n"
    "          <button key={p} style={{\n"
    "            padding: '8px 14px', borderRadius: 999, flexShrink: 0,\n"
    "            background: i === 2 ? SoS.ink : '#fff',\n"
    "            color: i === 2 ? '#fff' : SoS.ink,\n"
    "            border: i === 2 ? 'none' : `1px solid ${SoS.line}`,\n"
    "            fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',\n"
    "          }}>{p}</button>\n"
    "        ))}\n"
    "      </div>\n"
    "\n"
    "      {/* Ring og bekraft — ventende opgaver */}\n"
    "      {(() => {\n"
    "        const tasks = (window.PENDING_RING_TASKS || []).filter(t => !t.done);\n"
    "        if (tasks.length === 0) return null;\n"
    "        return (\n"
    "          <div style={{ margin: '0 20px 16px', padding: 16,\n"
    "            background: SoS.orange + '10', borderRadius: SoS.r.lg,\n"
    "            border: `1.5px solid ${SoS.orange}33` }}>\n"
    "            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>\n"
    "              <Icon name='phone' size={16} color={SoS.orange}/>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,\n"
    "                color: SoS.orange, textTransform: 'uppercase', letterSpacing: 0.8 }}>\n"
    "                Ring og bekraft — {tasks.length} ventende\n"
    "              </div>\n"
    "            </div>\n"
    "            {tasks.map(t => (\n"
    "              <RingTaskCard key={t.id} task={t}\n"
    "                onDone={() => { t.done = true; }}/>\n"
    "            ))}\n"
    "          </div>\n"
    "        );\n"
    "      })()}\n"
)

if PERIOD_SELECTOR_END not in html:
    sys.exit('ERROR: period selector anchor not found in AdminOverview')

html = html.replace(PERIOD_SELECTOR_END, RING_TASKS_SECTION, 1)
print('[OK] Ring og bekraft section added to AdminOverview')

# ─────────────────────────────────────────────────────────
# 3. ADD RingTaskCard component before AdminOverview
# ─────────────────────────────────────────────────────────
BEFORE_OVERVIEW = '// Overview — the data analyst\'s dashboard\nconst AdminOverview'

if BEFORE_OVERVIEW not in html:
    sys.exit('ERROR: AdminOverview anchor not found')

RING_TASK_CARD = (
    "const RingTaskCard = ({ task: t, onDone }) => {\n"
    "  const [checked, setChecked] = React.useState(false);\n"
    "  const fmtDato = (d) => d ? new Date(d).toLocaleDateString('da-DK',\n"
    "    { weekday: 'short', day: 'numeric', month: 'short' }) : '';\n"
    "  const handleCheck = () => {\n"
    "    setChecked(true);\n"
    "    setTimeout(onDone, 600);\n"
    "  };\n"
    "  return (\n"
    "    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0',\n"
    "      borderTop: `1px solid ${SoS.orange}22`,\n"
    "      opacity: checked ? 0.4 : 1, transition: 'opacity 0.4s' }}>\n"
    "      <button onClick={handleCheck} style={{ width: 24, height: 24, borderRadius: 12,\n"
    "        flexShrink: 0, border: `2px solid ${checked ? SoS.sage : SoS.orange}`,\n"
    "        background: checked ? SoS.sage : 'transparent', cursor: 'pointer',\n"
    "        display: 'flex', alignItems: 'center', justifyContent: 'center' }}>\n"
    "        {checked && <Icon name='check' size={12} color='#fff' weight={2.5}/>}\n"
    "      </button>\n"
    "      <div style={{ flex: 1, minWidth: 0 }}>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n"
    "          color: SoS.ink, marginBottom: 2 }}>\n"
    "          Ring {t.menneskeFirstName} {t.menneskeLastInitial}.\n"
    "        </div>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>\n"
    "          Aftale med {t.brobyggerFirstName} \u00b7 {fmtDato(t.dato)} kl. {t.start}\n"
    "        </div>\n"
    "      </div>\n"
    "      <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,\n"
    "        color: SoS.ink }}>{t.menneskeContact?.phone}</div>\n"
    "    </div>\n"
    "  );\n"
    "};\n"
    "\n"
    "// Overview — the data analyst's dashboard\n"
    "const AdminOverview"
)

html = html.replace(BEFORE_OVERVIEW, RING_TASK_CARD, 1)
print('[OK] RingTaskCard component added')

# ─────────────────────────────────────────────────────────
# 4. FIX dead-end "aftale-noter" ActionCard — add onClick
# ─────────────────────────────────────────────────────────
OLD_NOTER_CARD = (
    '              <ActionCard color={SoS.sage} bg={SoS.sageSoft} icon="bell"\n'
    '                title="3 aftale-noter modtaget i dag"\n'
    '                subtitle="Nye registreringer fra brobyggere"/>'
)

NEW_NOTER_CARD = (
    '              <ActionCard color={SoS.sage} bg={SoS.sageSoft} icon="bell"\n'
    '                title="3 aftale-noter modtaget i dag"\n'
    '                subtitle="Nye registreringer fra brobyggere"\n'
    '                onClick={() => setAktivTab(\'notater\')}/>'
)

if OLD_NOTER_CARD not in html:
    # Try without trailing />
    OLD_NOTER_CARD2 = (
        '              <ActionCard color={SoS.sage} bg={SoS.sageSoft} icon="bell"\n'
        '                title="3 aftale-noter modtaget i dag"\n'
        '                subtitle="Nye registreringer fra brobyggere" />'
    )
    if OLD_NOTER_CARD2 in html:
        html = html.replace(OLD_NOTER_CARD2, NEW_NOTER_CARD, 1)
        print('[OK] aftale-noter ActionCard onClick added (variant 2)')
    else:
        print('[WARN] aftale-noter ActionCard not found — skipping')
else:
    html = html.replace(OLD_NOTER_CARD, NEW_NOTER_CARD, 1)
    print('[OK] aftale-noter ActionCard onClick added')

# ─────────────────────────────────────────────────────────
# 5. Save
# ─────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Saved ({len(html.encode("utf-8")):,} bytes)')

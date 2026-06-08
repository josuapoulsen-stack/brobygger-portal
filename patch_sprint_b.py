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
# 1. Indsæt OpkaldLog + NyAftaleFlow før DesktopView
# ══════════════════════════════════════════════════════════════════
NEW_COMPONENTS = r'''
const OpkaldLog = ({ onClose }) => {
  const [navn, setNavn] = React.useState('');
  const [tlf,  setTlf]  = React.useState('');
  const [note, setNote] = React.useState('');
  const [saved, setSaved] = React.useState(false);

  const handleSave = () => {
    if (!note.trim()) return;
    const entry = {
      id: 'log-' + Date.now(),
      navn: navn.trim() || 'Ukendt',
      tlf: tlf.trim(),
      note: note.trim(),
      dato: new Date().toISOString().slice(0, 10),
      tid: new Date().toTimeString().slice(0, 5),
    };
    const prev = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]');
    localStorage.setItem('sos_opkald_log', JSON.stringify([entry, ...prev]));
    setSaved(true);
    setTimeout(onClose, 1000);
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
      zIndex: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      onClick={onClose}>
      <div style={{ width: 420, background: '#fff', borderRadius: SoS.r.lg,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)', overflow: 'hidden' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ padding: '15px 20px', borderBottom: `1px solid ${SoS.line}`,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>
            Log opkald
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <Icon name="close" size={16} color={SoS.inkMuted}/>
          </button>
        </div>
        <div style={{ padding: '18px 20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>Navn (valgfrit)</div>
              <input value={navn} onChange={e => setNavn(e.target.value)}
                placeholder="f.eks. Erik Hansen" autoFocus
                style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                  borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                  color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
            </div>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>Telefon (valgfrit)</div>
              <input value={tlf} onChange={e => setTlf(e.target.value)}
                placeholder="12 34 56 78" type="tel"
                style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                  borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                  color: SoS.ink, outline: 'none', boxSizing: 'border-box' }}/>
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
              color: SoS.inkSoft, marginBottom: 5 }}>
              Note <span style={{ color: SoS.orange }}>*</span>
            </div>
            <textarea value={note} onChange={e => setNote(e.target.value)}
              placeholder="Hvad handlede opkaldet om?" rows={3}
              style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                color: SoS.ink, outline: 'none', resize: 'none',
                lineHeight: 1.5, boxSizing: 'border-box' }}/>
          </div>
          <button onClick={handleSave} disabled={!note.trim()} style={{
            width: '100%', padding: '11px 0',
            background: saved ? SoS.green : note.trim() ? SoS.ink : SoS.lineSoft,
            color: note.trim() ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.sm,
            cursor: note.trim() ? 'pointer' : 'default',
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 700,
            transition: 'background 0.2s' }}>
            {saved ? '✓ Gemt' : 'Gem log'}
          </button>
        </div>
      </div>
    </div>
  );
};

const NyAftaleFlow = ({ onClose, viewingHq }) => {
  const [mode,           setMode]           = React.useState(null);
  const [saved,          setSaved]          = React.useState(null);
  const [form,           setForm]           = React.useState({ firstName: '', lastName: '', age: '', phone: '' });
  const [type,           setType]           = React.useState(null);
  const [kilde,          setKilde]          = React.useState(null);
  const [note,           setNote]           = React.useState('');
  const [consent,        setConsent]        = React.useState(false);
  const [hqOverride,     setHqOverride]     = React.useState(viewingHq || 'Aarhus');
  const [query,          setQuery]          = React.useState('');
  const [selectedPerson, setSelectedPerson] = React.useState(null);
  const [showContact,    setShowContact]    = React.useState(false);
  const [kpRolle,        setKpRolle]        = React.useState(null);
  const [kpNavn,         setKpNavn]         = React.useState('');
  const [kpTlf,          setKpTlf]          = React.useState('');

  const phoneDigits = form.phone.replace(/\D/g, '');
  const canSaveNy = form.firstName.trim() && form.age.trim()
    && phoneDigits.length === 8 && type && kilde && consent;

  const searchResults = query.length >= 2
    ? Object.values(window.SoS_MENNESKER || {}).filter(m => {
        const q = query.toLowerCase();
        return `${m.firstName || ''} ${m.lastName || ''}`.toLowerCase().includes(q)
          || (m.mobil || '').replace(/\s/g, '').includes(query.replace(/\s/g, ''));
      }).slice(0, 6)
    : [];

  const handleSaveNy = () => {
    const id = 'b-' + Date.now();
    const person = {
      id,
      firstName:    form.firstName.trim(),
      lastName:     form.lastName.trim(),
      age:          parseInt(form.age) || 0,
      mobil:        form.phone.trim(),
      type:         type || 'social',
      status:       'afventer',
      kilde,
      notes:        note.trim()
        ? [{ id: 'n-' + Date.now(), tekst: note.trim(), dato: new Date().toISOString().slice(0,10) }]
        : [],
      hq:           hqOverride || viewingHq || 'Aarhus',
      registeredAt: new Date().toISOString(),
      createdAt:    new Date().toISOString().slice(0, 10),
      initials:     (form.firstName.trim()[0] || '') + (form.lastName.trim()[0] || ''),
      consentAt:    new Date().toISOString(),
      brobyggerId:  null,
    };
    window.SoS_MENNESKER = { ...(window.SoS_MENNESKER || {}), [id]: person };
    if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER);
    setSaved(person);
  };

  const handleSaveEksisterende = () => {
    if (!selectedPerson) return;
    if (kpRolle && kpNavn.trim()) {
      const updated = { ...selectedPerson,
        kontaktpersoner: [
          ...(selectedPerson.kontaktpersoner || []),
          { id: 'kp-' + Date.now(), rolle: kpRolle, navn: kpNavn.trim(), tlf: kpTlf.trim() },
        ],
      };
      window.SoS_MENNESKER = { ...(window.SoS_MENNESKER || {}), [selectedPerson.id]: updated };
      if (window.SoS_STORE) window.SoS_STORE.save('mennesker', window.SoS_MENNESKER);
    }
    setSaved(selectedPerson);
  };

  const inp = {
    width: '100%', padding: '10px 12px', border: `1px solid ${SoS.line}`,
    borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
    color: SoS.ink, outline: 'none', boxSizing: 'border-box', background: '#fff',
  };

  const overlay = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
    zIndex: 500, display: 'flex', alignItems: 'center',
    justifyContent: 'center', padding: 20 };

  // Success
  if (saved) return (
    <div style={overlay}>
      <div style={{ width: 420, background: '#fff', borderRadius: SoS.r.lg,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)', padding: '36px 28px', textAlign: 'center' }}>
        <div style={{ width: 56, height: 56, borderRadius: 28, background: SoS.green + '18',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px' }}>
          <Icon name="check" size={24} color={SoS.green} weight={2.5}/>
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
          color: SoS.ink, marginBottom: 6 }}>
          {saved.firstName} er gemt
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
          marginBottom: 24, lineHeight: 1.5 }}>
          {mode === 'ny'
            ? 'Personen afventer nu match med en brobygger.'
            : 'Oplysningerne er opdateret.'}
        </div>
        <button onClick={onClose} style={{ width: '100%', padding: '12px 0',
          background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm,
          fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, cursor: 'pointer' }}>
          Luk
        </button>
      </div>
    </div>
  );

  // Mode selector
  if (!mode) return (
    <div style={overlay} onClick={onClose}>
      <div style={{ width: 440, background: '#fff', borderRadius: SoS.r.lg,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)', overflow: 'hidden' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ padding: '18px 20px', borderBottom: `1px solid ${SoS.line}`,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink }}>
            Ny aftale
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <Icon name="close" size={16} color={SoS.inkMuted}/>
          </button>
        </div>
        <div style={{ padding: '20px 20px 24px', display: 'flex', gap: 10 }}>
          {[
            { id: 'ny', emoji: '👤', title: 'Ny person',
              sub: 'Registrér stamdata og samtykke' },
            { id: 'eksisterende', emoji: '🔍', title: 'Eksisterende person',
              sub: 'Find og opdatér kontakter' },
          ].map(opt => (
            <button key={opt.id} onClick={() => setMode(opt.id)} style={{
              flex: 1, padding: '20px 16px', border: `2px solid ${SoS.line}`,
              borderRadius: SoS.r.md, background: '#fff', cursor: 'pointer', textAlign: 'left',
              transition: 'border-color 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = SoS.accent}
              onMouseLeave={e => e.currentTarget.style.borderColor = SoS.line}>
              <div style={{ fontSize: 26, marginBottom: 10 }}>{opt.emoji}</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, color: SoS.ink }}>
                {opt.title}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 4 }}>
                {opt.sub}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  // Ny person
  if (mode === 'ny') return (
    <div style={overlay} onClick={onClose}>
      <div style={{ width: '100%', maxWidth: 580, background: '#fff',
        borderRadius: SoS.r.lg, boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
        maxHeight: '90vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ padding: '15px 20px', borderBottom: `1px solid ${SoS.line}`,
          display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <button onClick={() => setMode(null)} style={{ background: 'none', border: 'none',
            cursor: 'pointer', display: 'flex' }}>
            <Icon name="chevronL" size={20} color={SoS.ink}/>
          </button>
          <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>
            Ny person
          </div>
          <button onClick={onClose} style={{ marginLeft: 'auto', background: 'none',
            border: 'none', cursor: 'pointer' }}>
            <Icon name="close" size={16} color={SoS.inkMuted}/>
          </button>
        </div>
        <div style={{ overflowY: 'auto', padding: '18px 20px 8px', flex: 1 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 10, marginBottom: 12 }}>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>
                Fornavn <span style={{ color: SoS.orange }}>*</span>
              </div>
              <input value={form.firstName}
                onChange={e => setForm(f => ({ ...f, firstName: e.target.value }))}
                placeholder="f.eks. Erik" autoFocus style={inp}/>
            </div>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>Efternavn</div>
              <input value={form.lastName}
                onChange={e => setForm(f => ({ ...f, lastName: e.target.value }))}
                placeholder="Valgfrit" style={inp}/>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10, marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>
                Alder <span style={{ color: SoS.orange }}>*</span>
              </div>
              <input value={form.age}
                onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                placeholder="72" type="number" min="0" max="120" style={inp}/>
            </div>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, marginBottom: 5 }}>
                Telefon <span style={{ color: SoS.orange }}>*</span>
              </div>
              <input value={form.phone}
                onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                placeholder="12 34 56 78" type="tel"
                style={{ ...inp, borderColor: form.phone && phoneDigits.length !== 8
                  ? SoS.rose : SoS.line }}/>
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
              color: SoS.inkSoft, marginBottom: 7 }}>Tilknyt til</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {SoS_HOVEDSAEDER.map(h => (
                <button key={h} onClick={() => setHqOverride(h)} style={{
                  padding: '6px 12px', borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12,
                  fontWeight: hqOverride === h ? 700 : 400,
                  background: hqOverride === h ? SoS.ink : SoS.surface,
                  color: hqOverride === h ? '#fff' : SoS.ink,
                  border: `1px solid ${hqOverride === h ? SoS.ink : SoS.line}` }}>
                  {h}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
              color: SoS.inkSoft, marginBottom: 7 }}>
              Indsats <span style={{ color: SoS.orange }}>*</span>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              {[
                { id: 'social',   l: 'Social',   c: SoS.social   },
                { id: 'forening', l: 'Forening',  c: SoS.forening },
                { id: 'sundhed',  l: 'Sundhed',   c: SoS.sundhed  },
              ].map(t => (
                <button key={t.id} onClick={() => setType(t.id)} style={{
                  flex: 1, padding: '10px 0',
                  border: `2px solid ${type === t.id ? t.c : SoS.line}`,
                  borderRadius: SoS.r.sm, cursor: 'pointer', textAlign: 'center',
                  background: type === t.id ? t.c + '15' : '#fff',
                  fontFamily: SoS.sans, fontSize: 13,
                  fontWeight: type === t.id ? 700 : 500,
                  color: type === t.id ? t.c : SoS.ink }}>
                  {t.l}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
              color: SoS.inkSoft, marginBottom: 7 }}>
              Kilde <span style={{ color: SoS.orange }}>*</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {[
                { id: 'kommune',    l: 'Sagsbehandler'  },
                { id: 'hospital',   l: 'Hospital'       },
                { id: 'paarørende', l: 'P\xe5r\xf8rende' },
                { id: 'selv',       l: 'Selvhenvendelse' },
                { id: 'laege',      l: 'L\xe6ge/klinik'  },
                { id: 'org',        l: 'Organisation'   },
                { id: 'andet',      l: 'Andet'          },
              ].map(k => (
                <button key={k.id} onClick={() => setKilde(k.id)} style={{
                  padding: '7px 13px', borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12,
                  fontWeight: kilde === k.id ? 700 : 400,
                  background: kilde === k.id ? SoS.ink : SoS.surface,
                  color: kilde === k.id ? '#fff' : SoS.ink,
                  border: `1px solid ${kilde === k.id ? SoS.ink : SoS.line}` }}>
                  {k.l}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
              color: SoS.inkSoft, marginBottom: 5 }}>Note (valgfrit)</div>
            <textarea value={note} onChange={e => setNote(e.target.value)}
              placeholder="Relevant baggrundsinformation..." rows={2}
              style={{ width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
                borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                color: SoS.ink, outline: 'none', resize: 'none',
                lineHeight: 1.5, boxSizing: 'border-box' }}/>
          </div>

          <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10,
            cursor: 'pointer', marginBottom: 4,
            padding: '12px 14px',
            background: consent ? SoS.green + '08' : SoS.surface,
            border: `1px solid ${consent ? SoS.green + '40' : SoS.line}`,
            borderRadius: SoS.r.sm }}>
            <input type="checkbox" checked={consent}
              onChange={e => setConsent(e.target.checked)}
              style={{ marginTop: 2, flexShrink: 0 }}/>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.ink, lineHeight: 1.6 }}>
              Personen har givet samtykke til registrering og videregivelse af oplysninger
              til en brobygger i forbindelse med brobygningsforl\xf8bet.
            </div>
          </label>
        </div>
        <div style={{ padding: '12px 20px', borderTop: `1px solid ${SoS.line}`, flexShrink: 0 }}>
          <button onClick={handleSaveNy} disabled={!canSaveNy} style={{
            width: '100%', padding: '12px 0',
            background: canSaveNy ? SoS.ink : SoS.lineSoft,
            color: canSaveNy ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.sm,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 700,
            cursor: canSaveNy ? 'pointer' : 'default' }}>
            Gem og afvent match →
          </button>
        </div>
      </div>
    </div>
  );

  // Eksisterende person
  return (
    <div style={overlay} onClick={onClose}>
      <div style={{ width: '100%', maxWidth: 520, background: '#fff',
        borderRadius: SoS.r.lg, boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
        maxHeight: '85vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ padding: '15px 20px', borderBottom: `1px solid ${SoS.line}`,
          display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <button onClick={() => { setMode(null); setSelectedPerson(null); setQuery(''); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}>
            <Icon name="chevronL" size={20} color={SoS.ink}/>
          </button>
          <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>
            Find person
          </div>
          <button onClick={onClose} style={{ marginLeft: 'auto', background: 'none',
            border: 'none', cursor: 'pointer' }}>
            <Icon name="close" size={16} color={SoS.inkMuted}/>
          </button>
        </div>

        <div style={{ overflowY: 'auto', padding: '16px 20px', flex: 1 }}>
          <input value={query}
            onChange={e => { setQuery(e.target.value); setSelectedPerson(null); }}
            placeholder="S\xf8g p\xe5 navn eller telefonnummer..." autoFocus
            style={{ width: '100%', padding: '10px 14px', marginBottom: 12,
              border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
              fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
              outline: 'none', boxSizing: 'border-box' }}/>

          {!selectedPerson && searchResults.map(m => {
            const t = SoS_TYPER[m.type] || {};
            return (
              <button key={m.id} onClick={() => setSelectedPerson(m)} style={{
                display: 'flex', alignItems: 'center', gap: 12, width: '100%',
                padding: '10px 12px', border: `1px solid ${SoS.line}`, marginBottom: 6,
                borderRadius: SoS.r.sm, background: '#fff',
                cursor: 'pointer', textAlign: 'left' }}
                onMouseEnter={e => e.currentTarget.style.background = SoS.surface}
                onMouseLeave={e => e.currentTarget.style.background = '#fff'}>
                <div style={{ width: 36, height: 36, borderRadius: 18, flexShrink: 0,
                  background: t.soft || SoS.accent + '20',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: SoS.mono, fontSize: 11, fontWeight: 700,
                  color: t.color || SoS.accent }}>
                  {(m.firstName[0] || '') + (m.lastName ? m.lastName[0] : '')}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    color: SoS.ink }}>
                    {m.firstName} {m.lastName}
                    <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 400,
                      color: SoS.inkMuted, marginLeft: 5 }}>{m.age} \xe5r</span>
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
                    {m.hq} \xb7 {m.mobil || 'Ingen tlf.'}
                  </div>
                </div>
                {t.color && <Pill bg={t.soft} color={t.color}>{t.short}</Pill>}
              </button>
            );
          })}
          {query.length >= 2 && !selectedPerson && searchResults.length === 0 && (
            <div style={{ padding: '20px 0', textAlign: 'center',
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
              Ingen match — pr\xf8v et andet s\xf8geord
            </div>
          )}

          {selectedPerson && (
            <>
              <div style={{ padding: '12px 14px', background: SoS.green + '08',
                border: `1px solid ${SoS.green}30`, borderRadius: SoS.r.sm,
                marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 700,
                    color: SoS.ink }}>
                    {selectedPerson.firstName} {selectedPerson.lastName}
                    <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 400,
                      color: SoS.inkMuted, marginLeft: 6 }}>
                      {selectedPerson.age} \xe5r \xb7 {selectedPerson.hq}
                    </span>
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkMuted, marginTop: 2 }}>
                    {selectedPerson.mobil || 'Ingen telefon'} \xb7 {selectedPerson.status}
                  </div>
                </div>
                <button onClick={() => setSelectedPerson(null)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                  <Icon name="close" size={14} color={SoS.inkMuted}/>
                </button>
              </div>

              <button onClick={() => setShowContact(v => !v)} style={{
                display: 'flex', alignItems: 'center', gap: 8,
                background: 'none', border: 'none', cursor: 'pointer', padding: '4px 0',
                fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.accent,
                marginBottom: showContact ? 10 : 0 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke={SoS.accent} strokeWidth="2.5"
                  strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Tilf\xf8j kontakt (sagsbehandler, familie m.fl.)
              </button>

              {showContact && (
                <div style={{ padding: 14, background: SoS.surface,
                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                    color: SoS.inkSoft, marginBottom: 8 }}>Rolle</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
                    {['Sagsbehandler', 'Familie', 'P\xe5r\xf8rende', 'Andet'].map(r => (
                      <button key={r} onClick={() => setKpRolle(r)} style={{
                        padding: '6px 12px', borderRadius: SoS.r.sm, cursor: 'pointer',
                        fontFamily: SoS.sans, fontSize: 12,
                        fontWeight: kpRolle === r ? 700 : 400,
                        background: kpRolle === r ? SoS.ink : '#fff',
                        color: kpRolle === r ? '#fff' : SoS.ink,
                        border: `1px solid ${kpRolle === r ? SoS.ink : SoS.line}` }}>
                        {r}
                      </button>
                    ))}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                    <input value={kpNavn} onChange={e => setKpNavn(e.target.value)}
                      placeholder="Navn"
                      style={{ padding: '9px 12px', border: `1px solid ${SoS.line}`,
                        borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                        color: SoS.ink, outline: 'none' }}/>
                    <input value={kpTlf} onChange={e => setKpTlf(e.target.value)}
                      placeholder="Telefon" type="tel"
                      style={{ padding: '9px 12px', border: `1px solid ${SoS.line}`,
                        borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                        color: SoS.ink, outline: 'none' }}/>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {selectedPerson && (
          <div style={{ padding: '12px 20px', borderTop: `1px solid ${SoS.line}`, flexShrink: 0 }}>
            <button onClick={handleSaveEksisterende} style={{
              width: '100%', padding: '12px 0', background: SoS.ink, color: '#fff',
              border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 14, fontWeight: 700 }}>
              Gem →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

'''

sub(
    '\n\nconst DesktopView = ({ user',
    NEW_COMPONENTS + '\n\nconst DesktopView = ({ user',
    "B1: Indsæt OpkaldLog + NyAftaleFlow"
)

# ══════════════════════════════════════════════════════════════════
# 2. DesktopView — tilføj showNyAftale + showOpkaldLog state
# ══════════════════════════════════════════════════════════════════
sub(
    "  const handleSearchNav = (sec, result) => {",
    "  const [showNyAftale,  setShowNyAftale]  = React.useState(false);\n"
    "  const [showOpkaldLog, setShowOpkaldLog] = React.useState(false);\n"
    "\n"
    "  const handleSearchNav = (sec, result) => {",
    "B2: showNyAftale + showOpkaldLog state"
)

# ══════════════════════════════════════════════════════════════════
# 3. Udvid keyboard handler med N, L, F genvejer
# ══════════════════════════════════════════════════════════════════
sub(
    "      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {\n"
    "        e.preventDefault();\n"
    "        setShowSearch(v => !v);\n"
    "      }\n"
    "    };",
    "      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {\n"
    "        e.preventDefault();\n"
    "        setShowSearch(v => !v);\n"
    "      }\n"
    "      const tag = document.activeElement?.tagName;\n"
    "      const isTyping = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';\n"
    "      if (!isTyping && !e.metaKey && !e.ctrlKey && !e.altKey) {\n"
    "        if (e.key === 'n' || e.key === 'N') { e.preventDefault(); setShowNyAftale(true); }\n"
    "        if (e.key === 'l' || e.key === 'L') { e.preventDefault(); setShowOpkaldLog(true); }\n"
    "        if (e.key === 'f' || e.key === 'F') { e.preventDefault(); setShowSearch(true); }\n"
    "      }\n"
    "    };",
    "B3: keyboard shortcuts N/L/F"
)

# ══════════════════════════════════════════════════════════════════
# 4. Topbar — tilføj Ny aftale + Log opkald knapper
# ══════════════════════════════════════════════════════════════════
sub(
    "              <select value={viewingHq} onChange={e => setViewingHq(e.target.value)} style={{\n"
    "                padding: '7px 12px', borderRadius: SoS.r.sm,\n"
    "                background: SoS.surface, border: `1px solid ${SoS.line}`,\n"
    "                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink,\n"
    "                cursor: 'pointer',\n"
    "              }}>",
    "              <button onClick={() => setShowNyAftale(true)} style={{\n"
    "                padding: '7px 14px', background: SoS.ink, color: '#fff',\n"
    "                border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,\n"
    "                display: 'flex', alignItems: 'center', gap: 6 }}>\n"
    "                <svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                  stroke=\"#fff\" strokeWidth=\"2.5\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                  <line x1=\"12\" y1=\"5\" x2=\"12\" y2=\"19\"/>\n"
    "                  <line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"/>\n"
    "                </svg>\n"
    "                Ny aftale\n"
    "                <span style={{ fontFamily: SoS.mono, fontSize: 9,\n"
    "                  opacity: 0.55, marginLeft: 1 }}>N</span>\n"
    "              </button>\n"
    "              <button onClick={() => setShowOpkaldLog(true)} style={{\n"
    "                padding: '7px 12px', background: SoS.surface,\n"
    "                border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12,\n"
    "                fontWeight: 600, color: SoS.ink,\n"
    "                display: 'flex', alignItems: 'center', gap: 5 }}>\n"
    "                Log opkald\n"
    "                <span style={{ fontFamily: SoS.mono, fontSize: 9,\n"
    "                  opacity: 0.4, marginLeft: 1 }}>L</span>\n"
    "              </button>\n"
    "              <select value={viewingHq} onChange={e => setViewingHq(e.target.value)} style={{\n"
    "                padding: '7px 12px', borderRadius: SoS.r.sm,\n"
    "                background: SoS.surface, border: `1px solid ${SoS.line}`,\n"
    "                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink,\n"
    "                cursor: 'pointer',\n"
    "              }}>",
    "B4: Ny aftale + Log opkald knapper i topbar"
)

# ══════════════════════════════════════════════════════════════════
# 5. Render modaler i DesktopView
# ══════════════════════════════════════════════════════════════════
sub(
    "{showSearch && (\n            <DesktopGlobalSearch\n              onClose={() => setShowSearch(false)}\n              onNavigate={handleSearchNav}\n            />\n          )}",
    "{showNyAftale && (\n            <NyAftaleFlow\n              viewingHq={viewingHq}\n              onClose={() => setShowNyAftale(false)}\n            />\n          )}\n          {showOpkaldLog && (\n            <OpkaldLog onClose={() => setShowOpkaldLog(false)}/>\n          )}\n          {showSearch && (\n            <DesktopGlobalSearch\n              onClose={() => setShowSearch(false)}\n              onNavigate={handleSearchNav}\n            />\n          )}",
    "B5: Render NyAftaleFlow + OpkaldLog modaler"
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
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

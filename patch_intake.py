path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

# ── 1. Insert IntakeFlow script block before closing </body> ──────────────────
intake_script = r"""
<script type="text/babel">
// ═══════════════════════════════════════════════════════════════════════
// INTAKE FLOW — Registrer nyt menneske
// ═══════════════════════════════════════════════════════════════════════

const INTAKE_KILDER = [
  { id: 'selv',       label: 'Egen henvendelse',    icon: 'user',     desc: 'Personen tog selv kontakt' },
  { id: 'kommune',    label: 'Kommunal henvisning', icon: 'building', desc: 'Fra sagsbehandler eller jobcenter' },
  { id: 'hospital',   label: 'Hospitalsudslusning', icon: 'shield',   desc: 'Via sygehus eller sundhedsvæsen' },
  { id: 'paarørende', label: 'Familie / pårørende', icon: 'heart',    desc: 'Henvendelse fra nærtstående' },
  { id: 'org',        label: 'Anden organisation',  icon: 'star',     desc: 'NGO, frivilligcenter e.l.' },
];

const INTAKE_BEHOV = [
  'Selskab og samtale',
  'Gåture / frisk luft',
  'Hjælp til lægebesøg',
  'Transport og ledsagelse',
  'Foreningsliv og fællesskab',
  'Sproglig støtte',
  'Kulturelle aktiviteter',
  'Let motion',
  'Indkøb og ærinder',
  'Andet',
];

const FieldLabel = ({ children, note }) => (
  <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
    color: SS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase',
    marginBottom: 8 }}>
    {children}
    {note && <span style={{ fontWeight: 400, textTransform: 'none',
      letterSpacing: 0, color: SS.inkMuted }}> ({note})</span>}
  </div>
);

const IntakeFlow = ({ onClose }) => {
  const [step, setStep] = React.useState(0);
  const [kilde, setKilde] = React.useState(null);
  const [form, setForm] = React.useState({ firstName: '', lastName: '', age: '', phone: '' });
  const [type, setType] = React.useState(null);
  const [selectedBehov, setSelectedBehov] = React.useState([]);
  const [udfordringer, setUdfordringer] = React.useState('');
  const [note, setNote] = React.useState('');
  const [consent, setConsent] = React.useState(false);
  const [done, setDone] = React.useState(false);

  const STEPS = ['Kilde', 'Basisinfo', 'Behov', 'Samtykke'];
  const canNext0 = !!kilde;
  const canNext1 = form.firstName.trim().length > 0 && form.age.trim().length > 0;
  const canNext2 = !!type && selectedBehov.length > 0;
  const canFinish = consent;

  const toggleBehov = (b) =>
    setSelectedBehov(prev => prev.includes(b) ? prev.filter(x => x !== b) : [...prev, b]);

  const inputStyle = {
    width: '100%', padding: '12px 14px',
    fontFamily: SS.sans, fontSize: 15, color: SS.ink,
    background: '#fff', border: `1.5px solid ${SS.lineSoft}`,
    borderRadius: SS.r.md, outline: 'none',
    boxSizing: 'border-box',
  };

  if (done) {
    return (
      <div style={{
        position: 'fixed', inset: 0, background: SS.cream,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: 32, zIndex: 300,
      }}>
        <div style={{
          width: 72, height: 72, borderRadius: 36,
          background: SS.sage, display: 'flex',
          alignItems: 'center', justifyContent: 'center', marginBottom: 24,
        }}>
          <Icon name="check" size={32} color="#fff" weight={2.5}/>
        </div>
        <div style={{ fontFamily: SS.font, fontSize: 28, fontWeight: 500,
          color: SS.ink, textAlign: 'center', letterSpacing: -0.3, marginBottom: 8 }}>
          {form.firstName} er registreret
        </div>
        <div style={{ fontFamily: SS.sans, fontSize: 14, color: SS.inkSoft,
          textAlign: 'center', lineHeight: 1.6, maxWidth: 280, marginBottom: 32 }}>
          Oplysningerne er gemt. Du kan nu starte et match, eller vende tilbage til oversigten.
        </div>
        <button onClick={onClose} style={{
          width: '100%', maxWidth: 280, padding: '15px 0',
          background: SS.orange, color: '#fff', border: 'none',
          borderRadius: SS.r.md, fontFamily: SS.sans, fontSize: 15,
          fontWeight: 600, cursor: 'pointer', marginBottom: 12,
        }}>
          Start matching
        </button>
        <button onClick={onClose} style={{
          width: '100%', maxWidth: 280, padding: '13px 0',
          background: 'transparent', color: SS.inkSoft,
          border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
          fontFamily: SS.sans, fontSize: 14, cursor: 'pointer',
        }}>
          Tilbage til oversigt
        </button>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: SS.cream,
      display: 'flex', flexDirection: 'column', zIndex: 300,
    }}>
      {/* Header */}
      <div style={{
        background: '#fff', padding: '54px 20px 16px',
        borderBottom: `1px solid ${SS.lineSoft}`, flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <button onClick={onClose} style={{
            width: 36, height: 36, borderRadius: 18, border: 'none',
            background: SS.creamDeep, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Icon name="close" size={16} color={SS.ink}/>
          </button>
          <div style={{ fontFamily: SS.font, fontSize: 20, fontWeight: 500,
            color: SS.ink, letterSpacing: -0.2 }}>
            Registrer menneske
          </div>
        </div>
        {/* Step bar */}
        <div style={{ display: 'flex', gap: 6 }}>
          {STEPS.map((s, i) => (
            <div key={s} style={{
              flex: i === step ? 2 : 1, height: 4, borderRadius: 2,
              background: i < step ? SS.sage : i === step ? SS.orange : SS.lineSoft,
              transition: 'all 0.3s',
            }}/>
          ))}
        </div>
        <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted,
          marginTop: 6, letterSpacing: 0.3 }}>
          Trin {step + 1} af {STEPS.length} — {STEPS[step]}
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 20px 120px' }}>

        {/* ── STEP 0: Kilde ── */}
        {step === 0 && (
          <>
            <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
              color: SS.ink, marginBottom: 6, letterSpacing: -0.2 }}>
              Hvordan kom personen i kontakt?
            </div>
            <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
              marginBottom: 20, lineHeight: 1.5 }}>
              Vi bruger dette til at forstå hvilke kanaler der virker bedst.
            </div>
            {INTAKE_KILDER.map(k => {
              const sel = kilde === k.id;
              return (
                <button key={k.id} onClick={() => setKilde(k.id)} style={{
                  display: 'flex', alignItems: 'center', gap: 14, width: '100%',
                  padding: '14px 16px', marginBottom: 8, textAlign: 'left',
                  background: sel ? SS.orange + '12' : '#fff',
                  border: `2px solid ${sel ? SS.orange : SS.lineSoft}`,
                  borderRadius: SS.r.md, cursor: 'pointer',
                }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                    background: sel ? SS.orange : SS.creamDeep,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon name={k.icon} size={18} color={sel ? '#fff' : SS.inkSoft}/>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 600,
                      color: SS.ink }}>{k.label}</div>
                    <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
                      marginTop: 2 }}>{k.desc}</div>
                  </div>
                  {sel && <Icon name="check" size={16} color={SS.orange}/>}
                </button>
              );
            })}
          </>
        )}

        {/* ── STEP 1: Basisinfo ── */}
        {step === 1 && (
          <>
            <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
              color: SS.ink, marginBottom: 6, letterSpacing: -0.2 }}>
              Basisoplysninger
            </div>
            <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
              marginBottom: 20, lineHeight: 1.5 }}>
              Kun fornavn og alder er påkrævet. Øvrige oplysninger er frivillige.
            </div>
            {[
              { key: 'firstName', label: 'Fornavn',   placeholder: 'f.eks. Erik',  required: true },
              { key: 'lastName',  label: 'Efternavn', placeholder: 'Valgfrit' },
              { key: 'age',       label: 'Alder',     placeholder: 'f.eks. 72',    required: true, type: 'number' },
              { key: 'phone',     label: 'Telefon',   placeholder: 'Valgfrit' },
            ].map(field => (
              <div key={field.key} style={{ marginBottom: 14 }}>
                <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                  color: SS.ink, marginBottom: 6 }}>
                  {field.label}
                  {field.required && <span style={{ color: SS.orange }}> *</span>}
                </div>
                <input
                  type={field.type || 'text'}
                  placeholder={field.placeholder}
                  value={form[field.key]}
                  onChange={e => setForm(f => ({ ...f, [field.key]: e.target.value }))}
                  style={inputStyle}
                />
              </div>
            ))}
          </>
        )}

        {/* ── STEP 2: Behov ── */}
        {step === 2 && (
          <>
            <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
              color: SS.ink, marginBottom: 6, letterSpacing: -0.2 }}>
              Behov og situation
            </div>
            <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
              marginBottom: 18, lineHeight: 1.5 }}>
              Vælg brobygningstype og beskriv de behov og udfordringer du kender til.
            </div>

            {/* Brobygningstype */}
            <FieldLabel>Brobygningstype</FieldLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 22 }}>
              {Object.values(SS_TYPER).map(t => {
                const sel = type === t.id;
                return (
                  <button key={t.id} onClick={() => setType(t.id)} style={{
                    display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
                    background: sel ? t.soft : '#fff',
                    border: `2px solid ${sel ? t.color : SS.lineSoft}`,
                    borderRadius: SS.r.md, cursor: 'pointer', textAlign: 'left',
                  }}>
                    <div style={{
                      width: 34, height: 34, borderRadius: 17, flexShrink: 0,
                      background: sel ? t.color : SS.creamDeep,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Icon name={t.icon} size={16} color={sel ? '#fff' : SS.inkSoft}/>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600,
                        color: SS.ink }}>{t.label}</div>
                      <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft,
                        marginTop: 2 }}>{t.desc}</div>
                    </div>
                    {sel && <Icon name="check" size={14} color={t.color}/>}
                  </button>
                );
              })}
            </div>

            {/* Specifikke behov */}
            <FieldLabel note="vælg alle der passer">Specifikke behov</FieldLabel>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 22 }}>
              {INTAKE_BEHOV.map(b => {
                const sel = selectedBehov.includes(b);
                return (
                  <button key={b} onClick={() => toggleBehov(b)} style={{
                    padding: '8px 14px',
                    fontFamily: SS.sans, fontSize: 13,
                    fontWeight: sel ? 600 : 400,
                    color: sel ? SS.orange : SS.inkSoft,
                    background: sel ? SS.orange + '15' : '#fff',
                    border: `1.5px solid ${sel ? SS.orange : SS.lineSoft}`,
                    borderRadius: 999, cursor: 'pointer',
                  }}>
                    {b}
                  </button>
                );
              })}
            </div>

            {/* Udfordringer og diagnoser — følsomt felt */}
            <div style={{
              background: '#FFF8F0', border: `1.5px solid ${SS.orange}30`,
              borderRadius: SS.r.md, padding: '12px 14px', marginBottom: 14,
            }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: 8 }}>
                <Icon name="shield" size={14} color={SS.orange} style={{ marginTop: 1 }}/>
                <div>
                  <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
                    color: SS.orange }}>
                    Følsomme oplysninger
                  </div>
                  <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft,
                    marginTop: 2, lineHeight: 1.4 }}>
                    Udfordringer og diagnoser er særligt beskyttet efter GDPR art. 9.
                    Skriv kun hvad der er nødvendigt for at finde den rette brobygger.
                    Kræver samtykke i næste trin.
                  </div>
                </div>
              </div>
              <textarea
                placeholder="F.eks. let demens, angst, mobilitetsvanskeligheder, depression, kronisk smerte..."
                value={udfordringer}
                onChange={e => setUdfordringer(e.target.value)}
                rows={3}
                style={{
                  width: '100%', padding: '10px 12px',
                  fontFamily: SS.sans, fontSize: 14, color: SS.ink,
                  background: '#fff',
                  border: `1.5px solid ${SS.orange}40`,
                  borderRadius: SS.r.sm, outline: 'none', resize: 'none',
                  boxSizing: 'border-box', lineHeight: 1.5,
                }}
              />
            </div>

            {/* Kontekstnote */}
            <FieldLabel note="valgfrit">Kontekstnote</FieldLabel>
            <textarea
              placeholder="Anden relevant kontekst om personen eller situationen..."
              value={note}
              onChange={e => setNote(e.target.value)}
              rows={2}
              style={{ ...inputStyle, resize: 'none', lineHeight: 1.5 }}
            />
          </>
        )}

        {/* ── STEP 3: Samtykke + opsummering ── */}
        {step === 3 && (
          <>
            <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
              color: SS.ink, marginBottom: 6, letterSpacing: -0.2 }}>
              Bekræft og gem
            </div>
            <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
              marginBottom: 16, lineHeight: 1.5 }}>
              Gennemgå oplysningerne inden du gemmer.
            </div>

            {/* Summary card */}
            <div style={{
              background: '#fff', borderRadius: SS.r.lg,
              border: `1px solid ${SS.lineSoft}`, marginBottom: 16, overflow: 'hidden',
            }}>
              {/* Person header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12,
                padding: '14px 16px', borderBottom: `1px solid ${SS.lineSoft}` }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 24, background: SS.orange,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                }}>
                  <span style={{ fontFamily: SS.sans, fontSize: 16,
                    fontWeight: 700, color: '#fff' }}>
                    {(form.firstName[0] || '?').toUpperCase()}{(form.lastName[0] || '').toUpperCase()}
                  </span>
                </div>
                <div>
                  <div style={{ fontFamily: SS.sans, fontSize: 16,
                    fontWeight: 600, color: SS.ink }}>
                    {form.firstName} {form.lastName}
                  </div>
                  <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft }}>
                    {form.age} år{form.phone ? ` · ${form.phone}` : ''}
                  </div>
                </div>
              </div>
              {/* Summary rows */}
              {[
                { label: 'Kilde', value: INTAKE_KILDER.find(k => k.id === kilde)?.label },
                { label: 'Type', value: SS_TYPER[type]?.label },
                { label: 'Behov', value: selectedBehov.join(', ') || '—' },
                ...(udfordringer ? [{ label: 'Udfordringer', value: udfordringer, sensitive: true }] : []),
                ...(note ? [{ label: 'Note', value: note }] : []),
              ].map(row => (
                <div key={row.label} style={{
                  display: 'flex', gap: 10,
                  padding: '10px 16px',
                  borderBottom: `1px solid ${SS.lineSoft}`,
                  background: row.sensitive ? '#FFF8F0' : 'transparent',
                }}>
                  <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                    color: row.sensitive ? SS.orange : SS.inkMuted,
                    minWidth: 100, paddingTop: 1 }}>
                    {row.label}
                    {row.sensitive && ' 🔒'}
                  </div>
                  <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.ink,
                    lineHeight: 1.5, flex: 1 }}>{row.value}</div>
                </div>
              ))}
              <div style={{ padding: '10px 16px' }}>
                <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted }}>
                  Registreret af dig · {new Date().toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' })}
                </div>
              </div>
            </div>

            {/* GDPR consent — særligt vigtigt ved følsomme data */}
            {udfordringer && (
              <div style={{
                background: '#FFF8F0', border: `1.5px solid ${SS.orange}40`,
                borderRadius: SS.r.md, padding: '12px 14px', marginBottom: 12,
              }}>
                <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
                  color: SS.orange, marginBottom: 4 }}>
                  OBS: Du har registreret følsomme helbredsoplysninger
                </div>
                <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
                  lineHeight: 1.5 }}>
                  GDPR art. 9 kræver eksplicit samtykke til behandling af helbredsoplysninger.
                  Sørg for at dette er dokumenteret — f.eks. via underskrevet samtykkeerklæring
                  eller journalnotat — inden du gemmer.
                </div>
              </div>
            )}

            <button
              onClick={() => setConsent(c => !c)}
              style={{
                display: 'flex', gap: 14, alignItems: 'flex-start', width: '100%',
                padding: '14px 16px',
                background: consent ? SS.sage + '15' : '#fff',
                border: `2px solid ${consent ? SS.sage : SS.lineSoft}`,
                borderRadius: SS.r.md, cursor: 'pointer', textAlign: 'left',
              }}>
              <div style={{
                width: 22, height: 22, borderRadius: 6, flexShrink: 0, marginTop: 1,
                background: consent ? SS.sage : '#fff',
                border: `2px solid ${consent ? SS.sage : SS.lineSoft}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {consent && <Icon name="check" size={12} color="#fff" weight={3}/>}
              </div>
              <div>
                <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600,
                  color: SS.ink, marginBottom: 4 }}>
                  Samtykke er indhentet og dokumenteret
                </div>
                <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
                  lineHeight: 1.5 }}>
                  Personen er informeret om formålet med registreringen, hvem der
                  har adgang til oplysningerne, og at de til enhver tid kan
                  trække samtykket tilbage.
                  {udfordringer && ' Særskilt samtykke til helbredsoplysninger er dokumenteret.'}
                </div>
              </div>
            </button>
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        padding: '12px 20px 34px',
        background: 'linear-gradient(to top, #fff 60%, transparent)',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', gap: 10 }}>
          {step > 0 && (
            <button onClick={() => setStep(s => s - 1)} style={{
              flex: 1, padding: '14px 0',
              background: '#fff', color: SS.ink,
              border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
              fontFamily: SS.sans, fontSize: 15, cursor: 'pointer',
            }}>
              Tilbage
            </button>
          )}
          {step < 3 ? (
            <button
              disabled={step === 0 ? !canNext0 : step === 1 ? !canNext1 : !canNext2}
              onClick={() => setStep(s => s + 1)}
              style={{
                flex: 2, padding: '14px 0',
                background: (step === 0 ? canNext0 : step === 1 ? canNext1 : canNext2)
                  ? SS.orange : SS.lineSoft,
                color: (step === 0 ? canNext0 : step === 1 ? canNext1 : canNext2)
                  ? '#fff' : SS.inkMuted,
                border: 'none', borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 15, fontWeight: 600,
                cursor: 'pointer', transition: 'background 0.2s',
              }}>
              Næste
            </button>
          ) : (
            <button
              disabled={!canFinish}
              onClick={() => setDone(true)}
              style={{
                flex: 2, padding: '14px 0',
                background: canFinish ? SS.sage : SS.lineSoft,
                color: canFinish ? '#fff' : SS.inkMuted,
                border: 'none', borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 15, fontWeight: 600,
                cursor: 'pointer', transition: 'background 0.2s',
              }}>
              Gem og opret
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
</script>
"""

if '</body>' in html:
    html = html.replace('</body>', intake_script + '\n</body>', 1)
    print("Inserted IntakeFlow script block")
else:
    print("ERROR: </body> not found")

# ── 2. Add 'intake' flow routing in app.jsx section ──────────────────────────
old_matching_route = """  } else if (tweaks.flow === "matching" && tweaks.role !== "brobygger") {
    content = <MatchingFlow onClose={() => setTweak("flow", "none")} />;
  } else if (tweaks.role === "admin" || tweaks.role === "raadgiver") {"""

new_matching_route = """  } else if (tweaks.flow === "matching" && tweaks.role !== "brobygger") {
    content = <MatchingFlow onClose={() => setTweak("flow", "none")} />;
  } else if (tweaks.flow === "intake" && tweaks.role !== "brobygger") {
    content = <IntakeFlow onClose={() => setTweak("flow", "none")} />;
  } else if (tweaks.role === "admin" || tweaks.role === "raadgiver") {"""

if old_matching_route in html:
    html = html.replace(old_matching_route, new_matching_route, 1)
    print("Added intake flow routing in app")
else:
    print("ERROR: matching route not found")

# ── 3. Add 'intake' to tweaks panel options ───────────────────────────────────
old_tweaks_flows = """                    { value: "matching", label: "Matching-flow" },
                    { value: "export", label: "SROI-rapport / eksport" },"""

new_tweaks_flows = """                    { value: "intake",   label: "Registrer menneske" },
                    { value: "matching", label: "Matching-flow" },
                    { value: "export",   label: "SROI-rapport / eksport" },"""

if old_tweaks_flows in html:
    html = html.replace(old_tweaks_flows, new_tweaks_flows, 1)
    print("Added 'intake' to tweaks panel")
else:
    print("ERROR: tweaks flows not found")

# ── 4. Add onOpenIntake prop to AdminMobile ───────────────────────────────────
old_admin_props = """AdminMobile = ({ user, viewingHq, ownHq, isAdmin, onOpenSettings, onOpenMatching, onOpenMessages, onOpenDesktop }) => {"""
new_admin_props = """AdminMobile = ({ user, viewingHq, ownHq, isAdmin, onOpenSettings, onOpenIntake, onOpenMatching, onOpenMessages, onOpenDesktop }) => {"""

if old_admin_props in html:
    html = html.replace(old_admin_props, new_admin_props, 1)
    print("Added onOpenIntake to AdminMobile props")
else:
    print("ERROR: AdminMobile props not found")

# ── 5. Add "Registrer nyt menneske" button after ActionCards ─────────────────
old_action_cards_end = """              <ActionCard color={SS.sage} bg={SS.sageSoft} icon="bell"
                title="3 aftale-noter modtaget i dag"
                subtitle="Nye registreringer fra brobyggere"/>
            </div>"""

new_action_cards_end = """              <ActionCard color={SS.sage} bg={SS.sageSoft} icon="bell"
                title="3 aftale-noter modtaget i dag"
                subtitle="Nye registreringer fra brobyggere"/>
            </div>
            <div style={{ padding: '8px 20px 0' }}>
              <button onClick={onOpenIntake} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                gap: 8, width: '100%', padding: '13px 0',
                background: SS.orange, color: '#fff', border: 'none',
                borderRadius: SS.r.md, fontFamily: SS.sans, fontSize: 14,
                fontWeight: 600, cursor: 'pointer',
              }}>
                <Icon name="user" size={16} color="#fff"/>
                Registrer nyt menneske
              </button>
            </div>"""

if old_action_cards_end in html:
    html = html.replace(old_action_cards_end, new_action_cards_end, 1)
    print("Added 'Registrer nyt menneske' CTA button")
else:
    print("ERROR: ActionCards end not found")

# ── 6. Wire onOpenIntake in app.jsx AdminMobile call ─────────────────────────
old_call = """        content = <AdminMobile
          user={user}
          viewingHq={viewingHq}
          ownHq="Aarhus"
          isAdmin={tweaks.role === "admin"}
          onOpenSettings={() => setSettingsOpen(true)}
          onOpenMatching={() => setTweak("flow", "matching")}
          onOpenMessages={(id) => setMsgOpenId(id)}
          onOpenDesktop={() => setDesktopMode(true)} />;"""

new_call = """        content = <AdminMobile
          user={user}
          viewingHq={viewingHq}
          ownHq="Aarhus"
          isAdmin={tweaks.role === "admin"}
          onOpenSettings={() => setSettingsOpen(true)}
          onOpenIntake={() => setTweak("flow", "intake")}
          onOpenMatching={() => setTweak("flow", "matching")}
          onOpenMessages={(id) => setMsgOpenId(id)}
          onOpenDesktop={() => setDesktopMode(true)} />;"""

if old_call in html:
    html = html.replace(old_call, new_call, 1)
    print("Wired onOpenIntake in app.jsx AdminMobile call")
else:
    print("ERROR: AdminMobile call not found")
    idx = html.find('onOpenMatching={() => setTweak("flow", "matching")}')
    print(f"  onOpenMatching idx: {idx}")
    if idx >= 0:
        print(repr(html[idx-300:idx+200]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDone. File: {len(html):,} bytes")

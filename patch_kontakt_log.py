"""
patch_kontakt_log.py
--------------------
Tilfoej KontaktLogFlow til rådgivere:
- Rådgiver-brobygning (rådgiver tog selv brobygningen)
- Telefonopkald
- Hjemmebesøg
Flowet vises som bottom sheet i AdminHome (overview-fanen).
Registreringen tæller med i historikken og statistikken.
"""
import sys

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────────────────────────────────────
# 1. Indsæt KontaktLogFlow FØR "const AdminHome = "
# ──────────────────────────────────────────────────────────────────────────────

ANCHOR = 'const AdminHome = ({ hovedsaede'

NEW_COMPONENT = r'''const KONTAKT_TYPER = [
  { id: 'brobygning', label: 'Brobygning',    icon: 'heart',  color: '#E87A3E',
    desc: 'Rådgiver tog selv brobygningen' },
  { id: 'telefon',    label: 'Telefonopkald', icon: 'phone',  color: '#6B8CAE',
    desc: 'Opkald til eller fra menneske' },
  { id: 'besog',      label: 'Hjemmebesøg',   icon: 'home',   color: '#7FA089',
    desc: 'Besøg hos menneske' },
];

const KontaktLogFlow = ({ onClose, onSave }) => {
  const [step,      setStep]      = React.useState(0);
  const [type,      setType]      = React.useState(null);
  const [menId,     setMenId]     = React.useState(null);
  const [dato,      setDato]      = React.useState('2026-04-26');
  const [varighed,  setVarighed]  = React.useState('30');
  const [note,      setNote]      = React.useState('');
  const [done,      setDone]      = React.useState(false);

  const valgtType = KONTAKT_TYPER.find(t => t.id === type);
  const valgtMen  = menId ? SS_MENNESKER[menId] : null;
  const menList   = Object.values(SS_MENNESKER).filter(m => m.status !== 'afsluttet');

  const registrer = () => {
    if (onSave) onSave({ type, menId, dato, varighed, note });
    setDone(true);
  };

  const sheetStyle = {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.48)',
    zIndex: 600, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end',
  };
  const panelStyle = {
    background: SoS.cream, borderRadius: '22px 22px 0 0',
    maxHeight: '92vh', overflowY: 'auto', paddingBottom: 44,
  };

  /* ── BEKRÆFTELSE ─────────────────────────────────────── */
  if (done) return (
    <div style={sheetStyle}>
      <div style={{ ...panelStyle, padding: '32px 24px 48px', textAlign: 'center' }}>
        <div style={{ width: 60, height: 60, borderRadius: 30,
          background: valgtType ? valgtType.color + '22' : SoS.sageSoft,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 18px' }}>
          <Icon name="check" size={26} color={valgtType ? valgtType.color : SoS.sage}/>
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
          color: SoS.ink, marginBottom: 8 }}>
          Kontakt registreret
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
          lineHeight: 1.6, marginBottom: 6 }}>
          <strong>{valgtType ? valgtType.label : ''}</strong>
          {valgtMen ? ' med ' + valgtMen.firstName + ' ' + valgtMen.lastName : ''}
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted,
          marginBottom: 28 }}>
          {dato} · {varighed} min
          {note ? ' · ' + note : ''}
        </div>
        <div style={{ background: '#fff', borderRadius: SoS.r.md,
          padding: '10px 14px', marginBottom: 24,
          border: '1px solid ' + SoS.lineSoft, textAlign: 'left' }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',
            marginBottom: 4 }}>Tæller med i statistik</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
            Kontakten er lagt til historikken og medregnes i SROI-beregning og rapporter.
          </div>
        </div>
        <button onClick={onClose} style={{
          width: '100%', padding: '14px 0', background: SoS.orange, color: '#fff',
          border: 'none', borderRadius: SoS.r.md, fontFamily: SoS.sans,
          fontSize: 15, fontWeight: 600, cursor: 'pointer' }}>Luk</button>
      </div>
    </div>
  );

  return (
    <div style={sheetStyle}>
      <div style={panelStyle}>
        {/* Handle + header */}
        <div style={{ display: 'flex', justifyContent: 'center', padding: '14px 0 0' }}>
          <div style={{ width: 38, height: 4, borderRadius: 2, background: SoS.lineSoft }}/>
        </div>
        <div style={{ display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', padding: '10px 20px 4px' }}>
          <div>
            <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink }}>
              Registrer kontakt
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
              {step === 0 ? 'Trin 1 — Kontakttype' :
               step === 1 ? 'Trin 2 — Vælg menneske' :
                            'Trin 3 — Detaljer'}
            </div>
          </div>
          <button onClick={onClose} style={{
            width: 32, height: 32, borderRadius: 16, background: SoS.creamDeep,
            border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="close" size={14} color={SoS.ink}/>
          </button>
        </div>

        <StepDots step={step} total={3}/>

        {/* ── TRIN 0: VÆLG TYPE ───────────────────────────── */}
        {step === 0 && (
          <div style={{ padding: '4px 20px 0' }}>
            {KONTAKT_TYPER.map(t => (
              <button key={t.id} onClick={() => { setType(t.id); setStep(1); }}
                style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 14,
                  padding: '16px 18px', marginBottom: 10,
                  background: '#fff', border: '1.5px solid ' + SoS.lineSoft,
                  borderRadius: SoS.r.lg, cursor: 'pointer', textAlign: 'left' }}>
                <div style={{ width: 46, height: 46, borderRadius: 12, flexShrink: 0,
                  background: t.color + '18',
                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name={t.icon} size={22} color={t.color}/>
                </div>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 600,
                    color: SoS.ink, marginBottom: 2 }}>{t.label}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkSoft }}>{t.desc}</div>
                </div>
                <Icon name="chevronR" size={16} color={SoS.inkMuted}
                  style={{ marginLeft: 'auto', flexShrink: 0 }}/>
              </button>
            ))}
          </div>
        )}

        {/* ── TRIN 1: VÆLG MENNESKE ──────────────────────── */}
        {step === 1 && (
          <div style={{ padding: '4px 20px 0' }}>
            {menList.map(m => {
              const t = SS_TYPER[m.type];
              return (
                <button key={m.id} onClick={() => { setMenId(m.id); setStep(2); }}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12,
                    padding: '13px 16px', marginBottom: 8,
                    background: '#fff', border: '1px solid ' + SoS.lineSoft,
                    borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left' }}>
                  <div style={{ width: 38, height: 38, borderRadius: 19, flexShrink: 0,
                    background: t ? t.soft : SoS.creamDeep,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,
                    color: t ? t.color : SoS.inkSoft }}>
                    {m.initials}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500,
                      color: SoS.ink }}>{m.firstName} {m.lastName}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11,
                      color: SoS.inkSoft, marginTop: 1 }}>
                      {t ? t.short : ''} · {m.age} år
                    </div>
                  </div>
                  <Icon name="chevronR" size={16} color={SoS.inkMuted}/>
                </button>
              );
            })}
            <button onClick={() => setStep(0)} style={{
              width: '100%', padding: '12px 0', marginTop: 4,
              background: 'transparent', border: 'none', cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
              ← Tilbage
            </button>
          </div>
        )}

        {/* ── TRIN 2: DETALJER ────────────────────────────── */}
        {step === 2 && (
          <div style={{ padding: '4px 20px 0' }}>
            {/* Opsummering */}
            {valgtType && valgtMen && (
              <div style={{ display: 'flex', gap: 10, alignItems: 'center',
                background: '#fff', borderRadius: SoS.r.md,
                padding: '12px 14px', marginBottom: 18,
                border: '1px solid ' + SoS.lineSoft }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0,
                  background: valgtType.color + '18',
                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name={valgtType.icon} size={18} color={valgtType.color}/>
                </div>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    color: SoS.ink }}>{valgtType.label}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkSoft }}>{valgtMen.firstName} {valgtMen.lastName}</div>
                </div>
              </div>
            )}

            {/* Dato */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase',
                marginBottom: 6 }}>Dato</div>
              <input type="date" value={dato} onChange={e => setDato(e.target.value)}
                style={{ width: '100%', padding: '12px 13px', fontFamily: SoS.sans,
                  fontSize: 14, color: SoS.ink, background: '#fff',
                  border: '1.5px solid ' + SoS.lineSoft, borderRadius: SoS.r.md,
                  outline: 'none', boxSizing: 'border-box' }}/>
            </div>

            {/* Varighed */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase',
                marginBottom: 6 }}>Varighed</div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {['15', '30', '45', '60', '90', '120'].map(v => (
                  <button key={v} onClick={() => setVarighed(v)} style={{
                    padding: '9px 16px', borderRadius: 999, cursor: 'pointer',
                    background: varighed === v ? SoS.orange : '#fff',
                    color: varighed === v ? '#fff' : SoS.ink,
                    border: varighed === v ? 'none' : '1px solid ' + SoS.lineSoft,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 500 }}>
                    {v} min
                  </button>
                ))}
              </div>
            </div>

            {/* Note */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase',
                marginBottom: 6 }}>Note <span style={{ fontWeight: 400, textTransform: 'none' }}>(valgfri)</span></div>
              <textarea value={note} onChange={e => setNote(e.target.value)}
                placeholder="Kort beskrivelse af kontakten..."
                rows={3}
                style={{ width: '100%', padding: '11px 13px', fontFamily: SoS.sans,
                  fontSize: 14, color: SoS.ink, background: '#fff',
                  border: '1.5px solid ' + SoS.lineSoft, borderRadius: SoS.r.md,
                  outline: 'none', boxSizing: 'border-box', resize: 'none',
                  lineHeight: 1.5 }}/>
            </div>

            <button onClick={registrer} style={{
              width: '100%', padding: '14px 0', marginBottom: 10,
              background: SoS.orange, color: '#fff', border: 'none',
              borderRadius: SoS.r.md, fontFamily: SoS.sans,
              fontSize: 15, fontWeight: 600, cursor: 'pointer' }}>
              Registrer kontakt
            </button>
            <button onClick={() => setStep(1)} style={{
              width: '100%', padding: '12px 0',
              background: 'transparent', border: 'none', cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
              ← Tilbage
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

''' + ANCHOR

if ANCHOR not in html:
    sys.exit('ERROR: AdminHome anchor ikke fundet')
html = html.replace(ANCHOR, NEW_COMPONENT, 1)
print('[OK] KontaktLogFlow komponent indsat')

# ──────────────────────────────────────────────────────────────────────────────
# 2. Tilfoej state til AdminHome + åbn-knap i overview + render flow
# ──────────────────────────────────────────────────────────────────────────────

# 2a. Tilfoej state-variabel
OLD_STATE = "  const titles = {"
NEW_STATE = (
  "  const [kontaktLog, setKontaktLog] = React.useState(false);\n"
  "  const titles = {"
)
if OLD_STATE not in html:
    sys.exit('ERROR: titles-anchor i AdminHome ikke fundet')
html = html.replace(OLD_STATE, NEW_STATE, 1)
print('[OK] kontaktLog state tilfoejt til AdminHome')

# 2b. Tilfoej "Registrer kontakt"-knap i overview (efter desktop-banner, foer AdminOverview)
OLD_OVERVIEW = "        {tab === 'overview' && <AdminOverview"
NEW_OVERVIEW = (
  "        {tab === 'overview' && (\n"
  "          <div style={{ padding: '0 20px 14px' }}>\n"
  "            <button onClick={() => setKontaktLog(true)} style={{\n"
  "              width: '100%', padding: '14px 0',\n"
  "              background: SoS.orange, color: '#fff', border: 'none',\n"
  "              borderRadius: SoS.r.md, fontFamily: SoS.sans,\n"
  "              fontSize: 15, fontWeight: 600, cursor: 'pointer',\n"
  "              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>\n"
  "              <Icon name=\"heart\" size={18} color=\"#fff\" weight={2}/>\n"
  "              Registrer kontakt\n"
  "            </button>\n"
  "          </div>\n"
  "        )}\n"
  "        {tab === 'overview' && <AdminOverview"
)
if OLD_OVERVIEW not in html:
    sys.exit('ERROR: AdminOverview-anchor ikke fundet')
html = html.replace(OLD_OVERVIEW, NEW_OVERVIEW, 1)
print('[OK] "Registrer kontakt"-knap tilfoejt i overview-fanen')

# 2c. Render KontaktLogFlow og indsaet det foer AdminTabBar
OLD_TABBAR = "      <AdminTabBar active={tab} onChange={setTab} />"
NEW_TABBAR = (
  "      {kontaktLog && (\n"
  "        <KontaktLogFlow\n"
  "          onClose={() => setKontaktLog(false)}\n"
  "          onSave={() => setKontaktLog(false)}\n"
  "        />\n"
  "      )}\n"
  "      <AdminTabBar active={tab} onChange={setTab} />"
)
if OLD_TABBAR not in html:
    sys.exit('ERROR: AdminTabBar-anchor ikke fundet')
html = html.replace(OLD_TABBAR, NEW_TABBAR, 1)
print('[OK] KontaktLogFlow render tilfoejt i AdminHome')

# ──────────────────────────────────────────────────────────────────────────────
# Gem
# ──────────────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] Gemt ({len(html.encode("utf-8")):,} bytes)')

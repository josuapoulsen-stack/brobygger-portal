# -*- coding: utf-8 -*-
"""
patch_kontakt_model.py
Implementerer komplet kontakt/aftale-model med indsatsniveauer og SROI-data:

  1. SoS_KONTAKTER — event-log for kontakter pr. menneske (mock-data)
  2. calcMenneskeStats + AddKontaktFlow — beregningslogik + UI-komponent
  3. MenneskeDetailPanel — indsatsniveau-banner, beregnede stats, "Tilfoej"-knap,
     seneste kontakter-liste
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ===========================================================================
# 1. Injicér SoS_KONTAKTER mock-data
# ===========================================================================
ANCHOR_KONTAKTER = 'window.SoS_MENNESKER     = SoS_MENNESKER;\n'

KONTAKTER_BLOCK = r"""window.SoS_MENNESKER     = SoS_MENNESKER;

// \u2500\u2500 Kontakt-h\u00e6ndelser (event log per menneske) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
// type-enum: telefonisk | mode-brobygger | folge-primaer | folge-sekundaer | andet
// status:    gennemfoert | aflyst | udeblev
const SoS_KONTAKTER = [
  // Karl Bredvig (b-1) \u2014 fler-aftaleforl\u00f8b: 3 gennemf\u00f8rte f\u00f8lgeskaber
  { id: 'k-1',  menneskeId: 'b-1', type: 'telefonisk',      dato: '2026-01-10', status: 'gennemfoert', note: 'F\u00f8rste kontakt oprettet, Karl er interesseret.' },
  { id: 'k-2',  menneskeId: 'b-1', type: 'mode-brobygger',  dato: '2026-01-22', status: 'gennemfoert', note: 'Hjemsbes\u00f8g, afklaret behov og \u00f8nsker.' },
  { id: 'k-3',  menneskeId: 'b-1', type: 'folge-primaer',   dato: '2026-02-07', status: 'gennemfoert', note: 'Ledsaget til praktiserende l\u00e6ge, Karl meget tilfreds.' },
  { id: 'k-4',  menneskeId: 'b-1', type: 'telefonisk',      dato: '2026-02-20', status: 'udeblev',     note: '' },
  { id: 'k-5',  menneskeId: 'b-1', type: 'folge-primaer',   dato: '2026-03-01', status: 'gennemfoert', note: 'Opf\u00f8lgning hos praktiserende l\u00e6ge, blodt\u00e6lling.' },
  { id: 'k-6',  menneskeId: 'b-1', type: 'folge-sekundaer', dato: '2026-03-18', status: 'gennemfoert', note: 'Kardiologisk ambulatorium, AUH Medicinsk afdeling.' },
  // Yaw Mensah (b-2) \u2014 personligt m\u00f8de: 1 m\u00f8de, 1 aflyst f\u00f8lgeskab
  { id: 'k-7',  menneskeId: 'b-2', type: 'telefonisk',      dato: '2026-02-14', status: 'gennemfoert', note: 'Afklaret behov, aftalt m\u00f8de.' },
  { id: 'k-8',  menneskeId: 'b-2', type: 'mode-brobygger',  dato: '2026-02-26', status: 'gennemfoert', note: 'Godt f\u00f8rste m\u00f8de, aftalte f\u00f8lgeskab til l\u00e6ge.' },
  { id: 'k-9',  menneskeId: 'b-2', type: 'folge-primaer',   dato: '2026-03-12', status: 'aflyst',      note: 'Yaw syg, aftalt ny tid.' },
  // Fatima Zahra (b-3) \u2014 f\u00f8lgeskab: 1 f\u00f8lgeskab gennemf\u00f8rt
  { id: 'k-10', menneskeId: 'b-3', type: 'telefonisk',      dato: '2026-03-03', status: 'gennemfoert', note: '' },
  { id: 'k-11', menneskeId: 'b-3', type: 'mode-brobygger',  dato: '2026-03-14', status: 'gennemfoert', note: 'M\u00f8de p\u00e5 Folkebiblioteket.' },
  { id: 'k-12', menneskeId: 'b-3', type: 'folge-sekundaer', dato: '2026-04-03', status: 'gennemfoert', note: 'F\u00f8lgeskab til AUH, Medicinsk afdeling.' },
  // Birger N\u00f8rgaard (b-4) \u2014 kontakt etableret: kun telefonisk
  { id: 'k-13', menneskeId: 'b-4', type: 'telefonisk',      dato: '2026-04-21', status: 'gennemfoert', note: 'Henvist via R\u00f8de Kors, god samtale.' },
];
window.SoS_KONTAKTER = SoS_KONTAKTER;
"""

cnt = html.count(ANCHOR_KONTAKTER)
html = html.replace(ANCHOR_KONTAKTER, KONTAKTER_BLOCK, 1)
results.append(('SoS_KONTAKTER mock-data injiceret', cnt, 1 if KONTAKTER_BLOCK in html else 0))

# ===========================================================================
# 2. Injicér helper-funktioner + AddKontaktFlow FØR MenneskeDetailPanel
# ===========================================================================
ANCHOR_MDP = 'const MenneskeDetailPanel = ({ menneske: m, onClose }) => {'

HELPERS_AND_FLOW = r"""// \u2500\u2500 Kontakt-beregningslogik \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
const KONTAKT_TYPE_META = {
  'telefonisk':      { label: 'Telefonisk kontakt',           shortLabel: 'Tlf.',     color: '#6B8CAE' },
  'mode-brobygger':  { label: 'M\u00f8de med brobygger',          shortLabel: 'M\u00f8de',    color: '#7FA089' },
  'folge-primaer':   { label: 'F\u00f8lgeskab \u2013 prim\u00e6r sundhed',  shortLabel: 'Prim\u00e6r',  color: '#E87A3E' },
  'folge-sekundaer': { label: 'F\u00f8lgeskab \u2013 sekund\u00e6r sundhed', shortLabel: 'Sekund\u00e6r', color: '#D64545' },
  'andet':           { label: 'Andet',                        shortLabel: 'Andet',    color: '#999'    },
};

const INDSATS_META = {
  ingen:   { label: 'Ingen kontakt endnu',    color: '#999',     rank: 0 },
  kontakt: { label: 'Kontakt etableret',      color: '#6B8CAE',  rank: 1 },
  mode:    { label: 'Personligt m\u00f8de',       color: '#7FA089',  rank: 2 },
  folge:   { label: 'F\u00f8lgeskab',             color: '#E87A3E',  rank: 3 },
  fler:    { label: 'Fler-aftaleforl\u00f8b',     color: '#D64545',  rank: 4 },
};

// Beregner n\u00f8gletal fra event-log (afledt, ingen redundante felter)
const calcMenneskeStats = (menneskeId) => {
  const all    = (window.SoS_KONTAKTER || []).filter(k => k.menneskeId === menneskeId);
  const done   = all.filter(k => k.status === 'gennemfoert');
  const mode   = done.filter(k => k.type === 'mode-brobygger');
  const folge  = done.filter(k => k.type === 'folge-primaer' || k.type === 'folge-sekundaer');
  const fPrim  = done.filter(k => k.type === 'folge-primaer');
  const fSek   = done.filter(k => k.type === 'folge-sekundaer');
  let niveau = 'ingen';
  if (done.length  >= 1) niveau = 'kontakt';
  if (mode.length  >= 1) niveau = 'mode';
  if (folge.length >= 1) niveau = 'folge';
  if (folge.length >= 2) niveau = 'fler';
  return {
    alle: all,
    antalKontakter:    all.length,
    antalGennemfoerte: done.length,
    antalFolgeskaber:  folge.length,
    antalFolgePrimaer: fPrim.length,
    antalFolgeSekundaer: fSek.length,
    antalMode:         mode.length,
    indsatsniveau:     niveau,
  };
};

// SROI-snapshot til rapport/eksport (alle mennesker)
window.calcSROISnapshot = () =>
  (window.SoS_MENNESKER || []).map(m => {
    const s = calcMenneskeStats(m.id);
    return {
      id: m.id, type: m.type, status: m.status,
      indsatsniveau:        s.indsatsniveau,
      antalKontakter:       s.antalKontakter,
      antalFolgeskaber:     s.antalFolgeskaber,
      antalFolgePrimaer:    s.antalFolgePrimaer,
      antalFolgeSekundaer:  s.antalFolgeSekundaer,
      flerAftaleforloeb:    s.indsatsniveau === 'fler',
      intensitet:           s.antalFolgeskaber >= 4 ? '4+' : s.antalFolgeskaber >= 2 ? '2\u20133' : s.antalFolgeskaber === 1 ? '1' : '0',
    };
  });

// AddKontaktFlow \u2014 tilf\u00f8j kontakt/aftale til et menneske
const AddKontaktFlow = ({ menneskeId, onClose, onSaved }) => {
  const [type,   setType]   = React.useState(null);
  const [dato,   setDato]   = React.useState('2026-04-27');
  const [status, setStatus] = React.useState(null);
  const [note,   setNote]   = React.useState('');
  const [done,   setDone]   = React.useState(false);
  const canSave = !!(type && dato && status);

  const handleSave = () => {
    const k = {
      id: 'k-' + Date.now(),
      menneskeId, type, dato, status,
      note: note.trim(),
      registreretDen: new Date().toISOString(),
    };
    window.SoS_KONTAKTER = [...(window.SoS_KONTAKTER || []), k];
    setDone(true);
  };

  const TYPE_OPTIONS = [
    { id: 'telefonisk',      label: 'Telefonisk kontakt' },
    { id: 'mode-brobygger',  label: 'M\u00f8de med brobygger' },
    { id: 'folge-primaer',   label: 'F\u00f8lgeskab \u2013 prim\u00e6r sundhed' },
    { id: 'folge-sekundaer', label: 'F\u00f8lgeskab \u2013 sekund\u00e6r sundhed' },
    { id: 'andet',           label: 'Andet' },
  ];
  const STATUS_OPTIONS = [
    { id: 'gennemfoert', label: 'Gennemf\u00f8rt', color: '#7FA089' },
    { id: 'aflyst',      label: 'Aflyst',       color: '#E87A3E' },
    { id: 'udeblev',     label: 'Udeblev',      color: '#D64545' },
  ];

  if (done) return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, zIndex: 200,
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: 32 }}>
      <div style={{ width: 72, height: 72, borderRadius: 36, background: SoS.sage,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>
        <Icon name="check" size={32} color="#fff" weight={2.5}/>
      </div>
      <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500, color: SoS.ink,
        textAlign: 'center', marginBottom: 8 }}>Kontakt registreret</div>
      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, textAlign: 'center',
        lineHeight: 1.6, marginBottom: 28, maxWidth: 280 }}>
        H\u00e6ndelsen er gemt og t\u00e6ller med i indsatsniveau og SROI-analyse.
      </div>
      <Button full onClick={() => { if (onSaved) onSaved(); onClose(); }}>Tilbage til forl\u00f8b</Button>
    </div>
  );

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, overflowY: 'auto', zIndex: 200 }}>
      {/* Mini-header */}
      <div style={{ padding: '54px 20px 14px', background: '#fff', position: 'sticky', top: 0, zIndex: 10,
        borderBottom: `1px solid ${SoS.lineSoft}`, display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onClose} style={{ width: 36, height: 36, borderRadius: 18,
          background: SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="chevronL" size={18} color={SoS.ink} weight={2.2}/>
        </button>
        <div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkSoft, letterSpacing: 0.4, textTransform: 'uppercase' }}>Ny registrering</div>
          <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink }}>
            Tilf\u00f8j kontakt/aftale
          </div>
        </div>
      </div>

      <div style={{ padding: '16px 16px 40px', display: 'flex', flexDirection: 'column', gap: 12 }}>

        {/* Type */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>Type *</div>
          {TYPE_OPTIONS.map(o => {
            const meta = KONTAKT_TYPE_META[o.id];
            const sel  = type === o.id;
            return (
              <button key={o.id} onClick={() => setType(o.id)} style={{
                display: 'flex', alignItems: 'center', width: '100%',
                padding: '11px 14px', marginBottom: 6, borderRadius: SoS.r.md,
                background: sel ? meta.color + '18' : SoS.creamDeep,
                border: `2px solid ${sel ? meta.color : 'transparent'}`,
                cursor: 'pointer', textAlign: 'left',
                fontFamily: SoS.sans, fontSize: 14,
                fontWeight: sel ? 700 : 400,
                color: sel ? meta.color : SoS.ink, transition: 'all 0.15s',
              }}>{o.label}</button>
            );
          })}
        </div>

        {/* Dato */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>Dato *</div>
          <input type="date" value={dato} onChange={e => setDato(e.target.value)} style={{
            width: '100%', padding: '11px 14px', border: `1px solid ${SoS.line}`,
            borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
            background: SoS.cream, boxSizing: 'border-box',
          }}/>
        </div>

        {/* Status */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>Status *</div>
          <div style={{ display: 'flex', gap: 8 }}>
            {STATUS_OPTIONS.map(o => {
              const sel = status === o.id;
              return (
                <button key={o.id} onClick={() => setStatus(o.id)} style={{
                  flex: 1, padding: '11px 0',
                  border: `2px solid ${sel ? o.color : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, background: sel ? o.color + '18' : '#fff',
                  cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13,
                  fontWeight: sel ? 700 : 400,
                  color: sel ? o.color : SoS.ink, transition: 'all 0.15s',
                }}>{o.label}</button>
              );
            })}
          </div>
        </div>

        {/* Note */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted,
            letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
            Faglig note (valgfri)
          </div>
          <textarea value={note} onChange={e => setNote(e.target.value)}
            placeholder="Kort faglig note om kontakten..."
            style={{ width: '100%', minHeight: 80, padding: '10px 12px',
              border: `1px solid ${SoS.line}`, borderRadius: SoS.r.md,
              fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
              background: SoS.cream, resize: 'vertical', boxSizing: 'border-box',
            }}/>
        </div>

        <Button full
          style={{ opacity: canSave ? 1 : 0.4, cursor: canSave ? 'pointer' : 'default' }}
          onClick={canSave ? handleSave : undefined}>
          Gem kontakt/aftale
        </Button>
        <button onClick={onClose} style={{ background: 'none', border: 'none',
          fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer', padding: 8 }}>
          Annuller
        </button>
      </div>
    </div>
  );
};

const MenneskeDetailPanel = ({ menneske: m, onClose }) => {"""

cnt = html.count(ANCHOR_MDP)
html = html.replace(ANCHOR_MDP, HELPERS_AND_FLOW, 1)
results.append(('Helper-funktioner + AddKontaktFlow injiceret', cnt, 1))

# ===========================================================================
# 3a. Tilfoej state til MenneskeDetailPanel (erstat de forste 2 linjer)
# ===========================================================================
OLD_MDP_START = """  const type = SoS_TYPER[m.type];
  return (
    <div style={{ background: SoS.cream, minHeight: '100%' }}>"""

NEW_MDP_START = """  const type = SoS_TYPER[m.type];
  const [addOpen, setAddOpen]       = React.useState(false);
  const [refreshKey, setRefreshKey] = React.useState(0);
  const stats       = React.useMemo(() => calcMenneskeStats(m.id), [m.id, refreshKey]);
  const niveauMeta  = INDSATS_META[stats.indsatsniveau];
  const recentKontakter = [...stats.alle]
    .sort((a, b) => b.dato.localeCompare(a.dato))
    .slice(0, 4);

  if (addOpen) return (
    <AddKontaktFlow
      menneskeId={m.id}
      onClose={() => setAddOpen(false)}
      onSaved={() => setRefreshKey(k => k + 1)}
    />
  );

  return (
    <div style={{ background: SoS.cream, minHeight: '100%' }}>"""

cnt = html.count(OLD_MDP_START)
html = html.replace(OLD_MDP_START, NEW_MDP_START, 1)
results.append(('MenneskeDetailPanel: state tilfojet', cnt, html.count(NEW_MDP_START)))

# ===========================================================================
# 3b. Erstat stats-sektion med indsatsniveau-banner + beregnede stats
# ===========================================================================
OLD_STATS = """      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: 10, margin: '-16px 16px 16px', position: 'relative', zIndex: 1 }}>
        {[
          { v: m.completedCount, l: 'Aftaler' },
          { v: m.contactCount,   l: 'Kontakter' },
          { v: m.cancelledCount, l: 'Aflyst' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', borderRadius: SoS.r.lg,
            padding: 14, textAlign: 'center', boxShadow: SoS.shadow.md }}>
            <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
              color: SoS.orange }}>{s.v}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11,
              color: SoS.inkSoft, marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>"""

NEW_STATS = r"""      {/* Indsatsniveau-banner */}
      <div style={{ margin: '-16px 16px 0', position: 'relative', zIndex: 1 }}>
        <div style={{ background: niveauMeta.color, color: '#fff', borderRadius: 14,
          padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12,
          boxShadow: SoS.shadow.md }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 9, fontWeight: 700,
              opacity: 0.8, letterSpacing: 0.9, textTransform: 'uppercase' }}>Indsatsniveau</div>
            <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500, marginTop: 2 }}>
              {niveauMeta.label}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontFamily: SoS.font, fontSize: 30, fontWeight: 500, lineHeight: 1 }}>
              {stats.antalFolgeskaber}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 10, opacity: 0.85 }}>f\u00f8lgeskaber</div>
          </div>
        </div>
      </div>

      {/* Stats \u2014 beregnet fra events */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: 8, margin: '10px 16px 16px', position: 'relative', zIndex: 1 }}>
        {[
          { v: stats.antalKontakter,    l: 'Kontakter' },
          { v: stats.antalGennemfoerte, l: 'Gennemf\u00f8rt' },
          { v: stats.antalKontakter - stats.antalGennemfoerte, l: 'Ikke m\u00f8dt' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', borderRadius: SoS.r.lg,
            padding: 12, textAlign: 'center', boxShadow: SoS.shadow.sm }}>
            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,
              color: SoS.orange }}>{s.v}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 10,
              color: SoS.inkSoft, marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>"""

cnt = html.count(OLD_STATS)
html = html.replace(OLD_STATS, NEW_STATS, 1)
results.append(('MenneskeDetailPanel: stats-sektion opdateret', cnt, 1))

# ===========================================================================
# 3c. Tilfoej "Seneste kontakter" sektion + "Tilfoej"-knap
#     Indsaettes FØR <Button full onClick={onClose} variant="secondary">Luk</Button>
# ===========================================================================
OLD_LUK = '        <Button full onClick={onClose} variant="secondary">Luk</Button>\n      </div>\n    </div>\n  );\n};\n\nconst AdminMenneskerScreen'

NEW_BEFORE_LUK = r"""        {/* Seneste kontakter */}
        {recentKontakter.length > 0 && (
          <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
            border: `1px solid ${SoS.lineSoft}` }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
              Seneste kontakter
            </div>
            {recentKontakter.map((k, i) => {
              const meta   = KONTAKT_TYPE_META[k.type] || KONTAKT_TYPE_META['andet'];
              const sColor = k.status === 'gennemfoert' ? '#7FA089' : k.status === 'aflyst' ? '#E87A3E' : '#D64545';
              const sLabel = k.status === 'gennemfoert' ? 'Gennemf\u00f8rt' : k.status === 'aflyst' ? 'Aflyst' : 'Udeblev';
              return (
                <div key={k.id} style={{
                  paddingBottom: i < recentKontakter.length - 1 ? 10 : 0,
                  marginBottom: i < recentKontakter.length - 1 ? 10 : 0,
                  borderBottom: i < recentKontakter.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                    <div style={{ width: 8, height: 8, borderRadius: 4,
                      background: meta.color, marginTop: 5, flexShrink: 0 }}/>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                          color: SoS.ink }}>{meta.label}</div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11,
                          color: SoS.inkMuted }}>{k.dato}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                          color: sColor }}>{sLabel}</span>
                        {k.note ? (
                          <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                            maxWidth: 160 }}>
                            \u00b7 {k.note}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Tilfoej kontakt/aftale */}
        <Button full onClick={() => setAddOpen(true)}
          icon={<Icon name="plus" size={16} color="#fff" weight={2.5}/>}>
          Tilf\u00f8j kontakt/aftale
        </Button>

        <Button full onClick={onClose} variant="secondary">Luk</Button>
      </div>
    </div>
  );
};

const AdminMenneskerScreen"""

cnt = html.count(OLD_LUK)
html = html.replace(OLD_LUK, NEW_BEFORE_LUK, 1)
results.append(('MenneskeDetailPanel: kontakter + Tilfoej-knap', cnt, 1))

# ===========================================================================
# Gem fil
# ===========================================================================
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 and after == 1 else f'[WARN] before={before} after={after}'
    print(f'{status} {label}')

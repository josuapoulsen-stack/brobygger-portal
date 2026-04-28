"""
patch_sted_soeg.py

1. Adds SoS_STEDER dataset to mock-data block:
   - Danish hospitals with individual afsnit (department level)
   - Generic 'Lægepraksis, [by]' entries
   - 'Andet' category

2. Adds StedSoeg search component (exported to window):
   - Search by text -> filters navn + sygehus + by
   - Dropdown with grouped results (sygehus-afsnit / lægepraksis / andet)
   - Selecting closes dropdown; shows pill with clear-button
   - No freetext — only structured picks

3. Replaces the freetext sted input in MatchingFlow with StedSoeg:
   - aftaleSted state changed from string to object {id, navn, type, sygehus, by}
   - Confirmation step shows aftaleSted.navn
   - handleSend includes stedNavn + stedType for statistics
"""
import sys

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. ADD SoS_STEDER dataset — insert before window.SoS_BROBYGGERE export
# ─────────────────────────────────────────────────────────────────────────────
ANCHOR_DATA = 'window.SoS_BROBYGGERE  = SoS_BROBYGGERE;'
if ANCHOR_DATA not in html:
    sys.exit('ERROR: SoS_BROBYGGERE export anchor not found')

STEDER_DATA = r"""
// ── Stedregister ──────────────────────────────────────────────────────────
// type: 'sygehus-afsnit' | 'laegepraksis' | 'andet'
const SoS_STEDER = [
  // ── Aarhus Universitetshospital ─────────────────────────────────
  { id: 'auh-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-ort',    type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk afdeling',    sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-oje',    type: 'sygehus-afsnit', navn: 'Øjenafdeling',                 sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-onh',    type: 'sygehus-afsnit', navn: 'ØNH-afdeling',                 sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-neu',    type: 'sygehus-afsnit', navn: 'Neurologisk afdeling',          sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-onk',    type: 'sygehus-afsnit', navn: 'Onkologisk afdeling',           sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-ger',    type: 'sygehus-afsnit', navn: 'Geriatrisk afdeling',           sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-dial',   type: 'sygehus-afsnit', navn: 'Dialyseafdeling',               sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-reum',   type: 'sygehus-afsnit', navn: 'Reumatologisk afdeling',        sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-roent',  type: 'sygehus-afsnit', navn: 'Billeddiagnostisk afdeling',    sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                     sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  { id: 'auh-fys',    type: 'sygehus-afsnit', navn: 'Fysioterapeutisk afdeling',     sygehus: 'Aarhus Universitetshospital', by: 'Aarhus' },
  // ── Regionshospitalet Randers ────────────────────────────────────
  { id: 'ran-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Regionshospitalet Randers',   by: 'Randers' },
  { id: 'ran-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Regionshospitalet Randers',   by: 'Randers' },
  { id: 'ran-ort',    type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk afdeling',    sygehus: 'Regionshospitalet Randers',   by: 'Randers' },
  { id: 'ran-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                     sygehus: 'Regionshospitalet Randers',   by: 'Randers' },
  { id: 'ran-roent',  type: 'sygehus-afsnit', navn: 'Røntgen',                       sygehus: 'Regionshospitalet Randers',   by: 'Randers' },
  // ── Regionshospitalet Horsens ────────────────────────────────────
  { id: 'hor-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Regionshospitalet Horsens',   by: 'Horsens' },
  { id: 'hor-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Regionshospitalet Horsens',   by: 'Horsens' },
  { id: 'hor-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                     sygehus: 'Regionshospitalet Horsens',   by: 'Horsens' },
  // ── Rigshospitalet ───────────────────────────────────────────────
  { id: 'rh-neuro',   type: 'sygehus-afsnit', navn: 'Neurointensiv afdeling',       sygehus: 'Rigshospitalet',              by: 'København' },
  { id: 'rh-onk',     type: 'sygehus-afsnit', navn: 'Onkologisk klinik',             sygehus: 'Rigshospitalet',              by: 'København' },
  { id: 'rh-hjerte',  type: 'sygehus-afsnit', navn: 'Hjertekirurgisk klinik',        sygehus: 'Rigshospitalet',              by: 'København' },
  { id: 'rh-ort',     type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk klinik',       sygehus: 'Rigshospitalet',              by: 'København' },
  { id: 'rh-born',    type: 'sygehus-afsnit', navn: 'Børneafdelingen',               sygehus: 'Rigshospitalet',              by: 'København' },
  { id: 'rh-roent',   type: 'sygehus-afsnit', navn: 'Billeddiagnostik',              sygehus: 'Rigshospitalet',              by: 'København' },
  // ── Bispebjerg Hospital ──────────────────────────────────────────
  { id: 'bbh-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Bispebjerg Hospital',         by: 'København' },
  { id: 'bbh-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Bispebjerg Hospital',         by: 'København' },
  { id: 'bbh-ger',    type: 'sygehus-afsnit', navn: 'Geriatrisk afdeling',          sygehus: 'Bispebjerg Hospital',         by: 'København' },
  { id: 'bbh-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                    sygehus: 'Bispebjerg Hospital',         by: 'København' },
  // ── Herlev Hospital ─────────────────────────────────────────────
  { id: 'hh-med',     type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Herlev Hospital',             by: 'Herlev' },
  { id: 'hh-onk',     type: 'sygehus-afsnit', navn: 'Onkologisk afdeling',          sygehus: 'Herlev Hospital',             by: 'Herlev' },
  { id: 'hh-kir',     type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Herlev Hospital',             by: 'Herlev' },
  { id: 'hh-gyn',     type: 'sygehus-afsnit', navn: 'Gynækologisk afdeling',        sygehus: 'Herlev Hospital',             by: 'Herlev' },
  // ── Odense Universitetshospital ──────────────────────────────────
  { id: 'ouh-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Odense Universitetshospital', by: 'Odense' },
  { id: 'ouh-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Odense Universitetshospital', by: 'Odense' },
  { id: 'ouh-neu',    type: 'sygehus-afsnit', navn: 'Neurologisk afdeling',          sygehus: 'Odense Universitetshospital', by: 'Odense' },
  { id: 'ouh-ort',    type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk afdeling',    sygehus: 'Odense Universitetshospital', by: 'Odense' },
  { id: 'ouh-ger',    type: 'sygehus-afsnit', navn: 'Geriatrisk afdeling',          sygehus: 'Odense Universitetshospital', by: 'Odense' },
  { id: 'ouh-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                    sygehus: 'Odense Universitetshospital', by: 'Odense' },
  // ── Aalborg Universitetshospital ─────────────────────────────────
  { id: 'aah-med',    type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',          sygehus: 'Aalborg Universitetshospital', by: 'Aalborg' },
  { id: 'aah-kir',    type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',           sygehus: 'Aalborg Universitetshospital', by: 'Aalborg' },
  { id: 'aah-neu',    type: 'sygehus-afsnit', navn: 'Neurologisk afdeling',          sygehus: 'Aalborg Universitetshospital', by: 'Aalborg' },
  { id: 'aah-ort',    type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk afdeling',    sygehus: 'Aalborg Universitetshospital', by: 'Aalborg' },
  { id: 'aah-skade',  type: 'sygehus-afsnit', navn: 'Skadestue',                    sygehus: 'Aalborg Universitetshospital', by: 'Aalborg' },
  // ── Sygehus Lillebælt ────────────────────────────────────────────
  { id: 'sl-vejle-med',   type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',      sygehus: 'Sygehus Lillebælt',           by: 'Vejle' },
  { id: 'sl-vejle-kir',   type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',       sygehus: 'Sygehus Lillebælt',           by: 'Vejle' },
  { id: 'sl-vejle-ort',   type: 'sygehus-afsnit', navn: 'Ortopædkirurgisk afdeling',sygehus: 'Sygehus Lillebælt',           by: 'Vejle' },
  { id: 'sl-kolding-med', type: 'sygehus-afsnit', navn: 'Medicinsk afdeling',      sygehus: 'Sygehus Lillebælt',           by: 'Kolding' },
  { id: 'sl-kolding-kir', type: 'sygehus-afsnit', navn: 'Kirurgisk afdeling',       sygehus: 'Sygehus Lillebælt',           by: 'Kolding' },
  { id: 'sl-kolding-skade',type:'sygehus-afsnit', navn: 'Skadestue',                sygehus: 'Sygehus Lillebælt',           by: 'Kolding' },
  // ── Lægepraksis (by-niveau) ──────────────────────────────────────
  { id: 'laege-aarhus',   type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Aarhus'    },
  { id: 'laege-kbh',      type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'København' },
  { id: 'laege-odense',   type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Odense'    },
  { id: 'laege-aalborg',  type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Aalborg'   },
  { id: 'laege-randers',  type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Randers'   },
  { id: 'laege-horsens',  type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Horsens'   },
  { id: 'laege-vejle',    type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Vejle'     },
  { id: 'laege-kolding',  type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Kolding'   },
  { id: 'laege-herlev',   type: 'laegepraksis',   navn: 'Lægepraksis',             sygehus: null, by: 'Herlev'    },
  // ── Andet ────────────────────────────────────────────────────────
  { id: 'andet',          type: 'andet',           navn: 'Andet sted',              sygehus: null, by: null        },
];
window.SoS_STEDER = SoS_STEDER;

"""

html = html.replace(ANCHOR_DATA, STEDER_DATA + ANCHOR_DATA, 1)
print('[OK] SoS_STEDER dataset added')

# ─────────────────────────────────────────────────────────────────────────────
# 2. ADD StedSoeg component — insert before MatchingFlow
# ─────────────────────────────────────────────────────────────────────────────
BEFORE_MF = 'const MatchingFlow = ({ onClose }) => {'
if BEFORE_MF not in html:
    sys.exit('ERROR: MatchingFlow anchor not found')

STED_SOEG_COMPONENT = r"""// ── StedSoeg ────────────────────────────────────────────────────────────────
// Structured location picker: søg på by eller sygehus → vælg afsnit
const StedSoeg = ({ value, onChange }) => {
  const [query, setQuery] = React.useState('');
  const [open,  setOpen]  = React.useState(false);
  const ref = React.useRef(null);

  // Close on outside click
  React.useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const TYPE_META = {
    'sygehus-afsnit': { label: 'Sygehus', color: SoS.sky,    bg: SoS.skySoft    },
    'laegepraksis':   { label: 'Læge',    color: SoS.sage,   bg: SoS.sageSoft   },
    'andet':          { label: 'Andet',   color: SoS.inkMuted, bg: SoS.creamDeep },
  };

  const q = query.toLowerCase().trim();
  const filtered = q.length < 1 ? [] : SoS_STEDER.filter(s => {
    const haystack = [s.navn, s.sygehus || '', s.by || ''].join(' ').toLowerCase();
    return q.split(' ').every(word => haystack.includes(word));
  }).slice(0, 18);

  // Group by sygehus for sygehus-afsnit, else flat
  const groups = [];
  const seenSygehus = {};
  filtered.forEach(s => {
    if (s.type === 'sygehus-afsnit') {
      const key = s.sygehus + '|' + s.by;
      if (!seenSygehus[key]) { seenSygehus[key] = { label: s.sygehus, by: s.by, items: [] }; groups.push(seenSygehus[key]); }
      seenSygehus[key].items.push(s);
    } else {
      groups.push({ label: null, by: null, items: [s] });
    }
  });

  const handleSelect = (s) => { onChange(s); setQuery(''); setOpen(false); };
  const handleClear  = () => { onChange(null); setQuery(''); };

  if (value) return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10,
      padding: '12px 14px', background: '#fff',
      border: `1.5px solid ${SoS.orange}`, borderRadius: SoS.r.md }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
          {value.navn}
        </div>
        {value.sygehus && (
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
            {value.sygehus} \u00b7 {value.by}
          </div>
        )}
        {!value.sygehus && value.by && (
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
            {value.by}
          </div>
        )}
      </div>
      <Pill bg={TYPE_META[value.type]?.bg} color={TYPE_META[value.type]?.color}>
        {TYPE_META[value.type]?.label}
      </Pill>
      <button onClick={handleClear} style={{ background: 'none', border: 'none',
        cursor: 'pointer', color: SoS.inkMuted, fontSize: 18, lineHeight: 1, padding: 2,
        display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        \u00d7
      </button>
    </div>
  );

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 14px',
        background: '#fff', border: `1.5px solid ${open ? SoS.orange : SoS.lineSoft}`,
        borderRadius: SoS.r.md, transition: 'border-color 0.15s' }}>
        <Icon name="search" size={14} color={SoS.inkMuted}/>
        <input
          autoComplete="off"
          placeholder="S\u00f8g by eller sygehus\u2026"
          value={query}
          onFocus={() => setOpen(true)}
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent',
            fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}
        />
        {query && (
          <button onClick={() => setQuery('')} style={{ background: 'none', border: 'none',
            cursor: 'pointer', color: SoS.inkMuted, fontSize: 16, lineHeight: 1, padding: 0 }}>
            \u00d7
          </button>
        )}
      </div>

      {open && query.length >= 1 && (
        <div style={{ position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0,
          background: '#fff', borderRadius: SoS.r.lg,
          boxShadow: '0 8px 32px rgba(0,0,0,0.14)', border: `1px solid ${SoS.lineSoft}`,
          zIndex: 999, maxHeight: 340, overflowY: 'auto' }}>

          {groups.length === 0 ? (
            <div style={{ padding: 16, fontFamily: SoS.sans, fontSize: 13,
              color: SoS.inkMuted, textAlign: 'center' }}>
              Ingen resultater \u2014 pr\u00f8v en anden s\u00f8gning
            </div>
          ) : groups.map((g, gi) => (
            <div key={gi}>
              {/* Sygehus group header */}
              {g.label && (
                <div style={{ padding: '10px 14px 4px',
                  fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',
                  borderTop: gi > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                  {g.label} \u00b7 {g.by}
                </div>
              )}
              {g.items.map(s => {
                const meta = TYPE_META[s.type] || TYPE_META.andet;
                return (
                  <button key={s.id}
                    onMouseDown={e => { e.preventDefault(); handleSelect(s); }}
                    style={{ display: 'flex', alignItems: 'center', gap: 12,
                      width: '100%', padding: '10px 14px', textAlign: 'left',
                      background: 'none', border: 'none', cursor: 'pointer' }}
                    onMouseEnter={e => e.currentTarget.style.background = SoS.cream}
                    onMouseLeave={e => e.currentTarget.style.background = 'none'}>
                    <div style={{ width: 8, height: 8, borderRadius: 4,
                      background: meta.color, flexShrink: 0 }}/>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 13,
                        fontWeight: s.type === 'laegepraksis' ? 500 : 600, color: SoS.ink }}>
                        {s.navn}
                        {s.type === 'laegepraksis' && s.by &&
                          <span style={{ fontWeight: 400, color: SoS.inkSoft }}>, {s.by}</span>}
                      </div>
                    </div>
                    <Pill bg={meta.bg} color={meta.color} style={{ flexShrink: 0 }}>
                      {meta.label}
                    </Pill>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
window.StedSoeg = StedSoeg;

"""

html = html.replace(BEFORE_MF, STED_SOEG_COMPONENT + BEFORE_MF, 1)
print('[OK] StedSoeg component added before MatchingFlow')

# ─────────────────────────────────────────────────────────────────────────────
# 3. In MatchingFlow: change aftaleSted state from string to object
# ─────────────────────────────────────────────────────────────────────────────
OLD_STED_STATE = "  const [aftaleSted, setAftaleSted] = React.useState('');"
NEW_STED_STATE = "  const [aftaleSted, setAftaleSted] = React.useState(null);"
if OLD_STED_STATE not in html:
    sys.exit('ERROR: aftaleSted state declaration not found')
html = html.replace(OLD_STED_STATE, NEW_STED_STATE, 1)
print('[OK] aftaleSted state changed to null (object)')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Replace the freetext sted input with StedSoeg
# ─────────────────────────────────────────────────────────────────────────────
OLD_STED_INPUT = (
    '            {/* Sted (valgfrit) */}\n'
    '            <div>\n'
    '              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n'
    '                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: \'uppercase\', marginBottom: 8 }}>\n'
    '                Sted <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>\n'
    '              </div>\n'
    '              <input placeholder="Fx klinik, adresse eller m\\u00f8dested"\n'
    '                value={aftaleSted} onChange={e => setAftaleSted(e.target.value)}\n'
    '                style={{ width: \'100%\', padding: \'12px 14px\', fontFamily: SoS.sans, fontSize: 14,\n'
    '                  color: SoS.ink, background: \'#fff\', border: `1.5px solid ${SoS.lineSoft}`,\n'
    '                  borderRadius: SoS.r.md, outline: \'none\', boxSizing: \'border-box\' }}/>\n'
    '            </div>\n'
)

NEW_STED_INPUT = (
    '            {/* Sted */}\n'
    '            <div>\n'
    '              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n'
    '                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: \'uppercase\', marginBottom: 8 }}>\n'
    '                Sted <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>\n'
    '              </div>\n'
    '              <StedSoeg value={aftaleSted} onChange={setAftaleSted}/>\n'
    '            </div>\n'
)

if OLD_STED_INPUT not in html:
    sys.exit('ERROR: old sted input block not found')
html = html.replace(OLD_STED_INPUT, NEW_STED_INPUT, 1)
print('[OK] Freetext sted input replaced with StedSoeg')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Fix confirmation step (step 3): aftaleSted.navn instead of string
# ─────────────────────────────────────────────────────────────────────────────
# The existing confirmation shows:
#   {aftaleSted ? (
#     <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
#       <span ...>Sted</span>
#       <span ...>{aftaleSted}</span>
#     </div>
#   ) : null}
OLD_STED_CONFIRM = (
    '                {aftaleSted ? (\n'
    '                  <div style={{ display: \'flex\', justifyContent: \'space-between\', marginBottom: 8 }}>\n'
    '                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Sted</span>\n'
    '                    <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{aftaleSted}</span>\n'
    '                  </div>\n'
    '                ) : null}'
)
NEW_STED_CONFIRM = (
    '                {aftaleSted ? (\n'
    '                  <div style={{ display: \'flex\', justifyContent: \'space-between\', marginBottom: 8 }}>\n'
    '                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Sted</span>\n'
    '                    <div style={{ textAlign: \'right\' }}>\n'
    '                      <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>{aftaleSted.navn}</div>\n'
    '                      {aftaleSted.sygehus && <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>{aftaleSted.sygehus}</div>}\n'
    '                    </div>\n'
    '                  </div>\n'
    '                ) : null}'
)
if OLD_STED_CONFIRM in html:
    html = html.replace(OLD_STED_CONFIRM, NEW_STED_CONFIRM, 1)
    print('[OK] Confirmation step updated to show aftaleSted.navn')
else:
    print('[WARN] Confirmation sted block not found — skipping')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Fix handleSend to include stedNavn + stedType
# ─────────────────────────────────────────────────────────────────────────────
OLD_SEND = (
    '    window.PENDING_RING_TASKS.unshift({\n'
    '      id: Date.now(),\n'
    '      menneskeFirstName: menneske.firstName,\n'
    '      menneskeLastInitial: menneske.lastName[0],\n'
    '      menneskeContact: menneske.contact,\n'
    '      brobyggerFirstName: brobygger.name.split(\' \')[0],\n'
    '      dato: aftaleDato,\n'
    '      start: aftaleStart,\n'
    '      duration: aftaleDuration,\n'
    '      done: false,\n'
    '    });'
)
NEW_SEND = (
    '    window.PENDING_RING_TASKS.unshift({\n'
    '      id: Date.now(),\n'
    '      menneskeFirstName: menneske.firstName,\n'
    '      menneskeLastInitial: menneske.lastName[0],\n'
    '      menneskeContact: menneske.contact,\n'
    '      brobyggerFirstName: brobygger.name.split(\' \')[0],\n'
    '      dato: aftaleDato,\n'
    '      start: aftaleStart,\n'
    '      duration: aftaleDuration,\n'
    '      stedNavn: aftaleSted?.navn || null,\n'
    '      stedType: aftaleSted?.type || null,\n'
    '      stedSygehus: aftaleSted?.sygehus || null,\n'
    '      done: false,\n'
    '    });'
)
if OLD_SEND in html:
    html = html.replace(OLD_SEND, NEW_SEND, 1)
    print('[OK] handleSend updated with stedNavn/stedType/stedSygehus')
else:
    print('[WARN] handleSend block not found — skipping')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Save
# ─────────────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Saved ({len(html.encode("utf-8")):,} bytes)')

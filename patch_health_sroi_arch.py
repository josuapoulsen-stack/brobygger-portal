# -*- coding: utf-8 -*-
"""
patch_health_sroi_arch.py
Implementerer alle tre arkitekturjusteringer:

1. Split health i to lag:
   - sroiMaalgruppe  (analytisk enum — neutral, stramt)
   - helbredsKategorier (fagligt flervalg)
   - health (fritekst, nu kaldet helbredsNote)
   Opdaterer: seed-data, IntakeFlow step 2, MenneskeDetailPanel

2. calcSROISnapshot -> aggregerede tæller kun (ingen per-borger objekter)

3. Admin-toggle: vis/skjul faglig helbreds-sektion (data-sekscionen)
   + window.SoS_SETTINGS global
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ─────────────────────────────────────────────────
# 0.  window.SoS_SETTINGS + SROI_MAALGRUPPE_OPTIONS
#     Indsæt lige efter window.MATCH_FRIST_TIMER
# ─────────────────────────────────────────────────
OLD0 = "window.MATCH_FRIST_TIMER = window.MATCH_FRIST_TIMER || 72;"
NEW0 = """window.MATCH_FRIST_TIMER = window.MATCH_FRIST_TIMER || 72;

// Global portal-indstillinger (kan overskrives fra AdminSettings)
window.SoS_SETTINGS = window.SoS_SETTINGS || {
  visHelbredsforhold: true,   // vis faglig helbreds-sektion i intake + profil
};

// SROI-målgruppe valgmuligheder (analytisk felt — bruges i SROI-rapportering)
window.SROI_MAALGRUPPE_OPTIONS = [
  { id: 'adhd',    label: 'ADHD / neurodiversitet' },
  { id: 'psykisk', label: 'Psykisk lidelse' },
  { id: 'alkohol', label: 'Alkohol- eller stofmisbrug' },
  { id: 'diabetes',label: 'Diabetes' },
  { id: 'kronisk', label: 'Anden kronisk sygdom' },
  { id: 'ingen',   label: 'Matcher ikke SROI-målgruppen' },
  { id: 'uoplyst', label: 'Ønsker ikke at oplyse' },
];

// Faglige helbreds-kategorier (flervalg)
window.HELBREDS_KATEGORIER = [
  { id: 'psykisk',  label: 'Psykisk' },
  { id: 'neuro',    label: 'Neurodiversitet' },
  { id: 'somatisk', label: 'Somatisk' },
  { id: 'afhaengighed', label: 'Afhængighed' },
  { id: 'andet',    label: 'Andet' },
];"""
cnt0 = html.count(OLD0)
html = html.replace(OLD0, NEW0, 1)
results.append(('SoS_SETTINGS + options', cnt0, 1))

# ─────────────────────────────────────────────────
# 1.  Seed-data: tilføj sroiMaalgruppe + helbredsKategorier
# ─────────────────────────────────────────────────

# b-1: Ingrid, social, mild demens + gangbesvær
OLD_B1 = "    health: 'Mild demens — hjælp gerne med at huske aftaler. Bruger stok ved længere gåture.',"
NEW_B1 = "    health: 'Mild demens — hjælp gerne med at huske aftaler. Bruger stok ved længere gåture.',\n    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk', 'somatisk'],"
cnt = html.count(OLD_B1)
html = html.replace(OLD_B1, NEW_B1, 1)
results.append(('seed b-1 helbred', cnt, 1))

# b-2: Ahmad, forening, ingen særlige
OLD_B2 = "    health: 'Ingen særlige forhold.',"
NEW_B2 = "    health: 'Ingen særlige forhold.',\n    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: [],"
cnt = html.count(OLD_B2)
html = html.replace(OLD_B2, NEW_B2, 1)
results.append(('seed b-2 helbred', cnt, 1))

# b-3: Birthe, social, gigt
OLD_B3 = "    health: 'Gigt i hænder — undgå håndtryk. Hører godt; ser dårligt.',"
NEW_B3 = "    health: 'Gigt i hænder — undgå håndtryk. Hører godt; ser dårligt.',\n    sroiMaalgruppe: 'kronisk',\n    helbredsKategorier: ['somatisk'],"
cnt = html.count(OLD_B3)
html = html.replace(OLD_B3, NEW_B3, 1)
results.append(('seed b-3 helbred', cnt, 1))

# b-4: Peter, sundhed, angstlidelse
OLD_B4 = "    health: 'Angstlidelse. Start gerne stille; undgå store forsamlinger.',"
NEW_B4 = "    health: 'Angstlidelse. Start gerne stille; undgå store forsamlinger.',\n    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk'],"
cnt = html.count(OLD_B4)
html = html.replace(OLD_B4, NEW_B4, 1)
results.append(('seed b-4 helbred', cnt, 1))

# b-5: Karen, sundhed, ingen kendte
OLD_B5 = "    health: 'Ingen kendte saerlige forhold.',"
NEW_B5 = "    health: 'Ingen kendte saerlige forhold.',\n    sroiMaalgruppe: 'uoplyst',\n    helbredsKategorier: [],"
cnt = html.count(OLD_B5)
html = html.replace(OLD_B5, NEW_B5, 1)
results.append(('seed b-5 helbred', cnt, 1))

# b-6: Mohammed, forening, ingen særlige
OLD_B6 = "    health: 'Ingen saerlige forhold.',"
NEW_B6 = "    health: 'Ingen saerlige forhold.',\n    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: [],"
cnt = html.count(OLD_B6)
html = html.replace(OLD_B6, NEW_B6, 1)
results.append(('seed b-6 helbred', cnt, 1))

# ─────────────────────────────────────────────────
# 2.  IntakeFlow: tilføj state-variabler
# ─────────────────────────────────────────────────
OLD_STATE = "  const [udfordringer, setUdfordringer] = React.useState('');\n  const [note, setNote] = React.useState('');"
NEW_STATE = "  const [udfordringer, setUdfordringer] = React.useState('');\n  const [sroiMaalgruppe, setSroiMaalgruppe] = React.useState('');\n  const [helbredsKategorier, setHelbredsKategorier] = React.useState([]);\n  const [note, setNote] = React.useState('');"
cnt = html.count(OLD_STATE)
html = html.replace(OLD_STATE, NEW_STATE, 1)
results.append(('IntakeFlow: state vars', cnt, 1))

# ─────────────────────────────────────────────────
# 3.  IntakeFlow step 2: erstat health-sektionen
# ─────────────────────────────────────────────────
OLD_HEALTH_UI = """            {/* Udfordringer og diagnoser — følsomt felt */}
            <div style={{
              background: '#FFF8F0', border: `1.5px solid ${SoS.orange}30`,
              borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 14,
            }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: 8 }}>
                <Icon name="shield" size={14} color={SoS.orange} style={{ marginTop: 1 }}/>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                    color: SoS.orange }}>
                    Følsomme oplysninger
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
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
                  fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,"""

# Find the end of this textarea block
start_idx = html.find(OLD_HEALTH_UI)
if start_idx != -1:
    # Find the closing </div> of the outer div after the textarea
    search_from = start_idx + len(OLD_HEALTH_UI)
    # Find the end of the health block: look for </div>\n            </div>
    close_tag = '              }}/>\n            </div>'
    close_idx = html.find(close_tag, search_from)
    if close_idx != -1:
        old_full = html[start_idx:close_idx + len(close_tag)]

        NEW_HEALTH_UI = """            {/* SROI-målgruppe — analytisk felt */}
            <div style={{
              background: SoS.creamDeep, borderRadius: SoS.r.md,
              padding: '12px 14px', marginBottom: 12,
            }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                color: SoS.ink, marginBottom: 6 }}>
                Matcher SROI-målgruppe?
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                marginBottom: 10, lineHeight: 1.4 }}>
                Bruges kun til aggregeret SROI-rapportering. Gemmes aldrig per borger i rapporter.
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(window.SROI_MAALGRUPPE_OPTIONS || []).map(opt => (
                  <label key={opt.id} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 12px', borderRadius: SoS.r.sm,
                    background: sroiMaalgruppe === opt.id ? SoS.orange + '15' : '#fff',
                    border: `1.5px solid ${sroiMaalgruppe === opt.id ? SoS.orange : SoS.lineSoft}`,
                    cursor: 'pointer',
                  }}>
                    <input
                      type="radio"
                      name="sroiMaalgruppe"
                      value={opt.id}
                      checked={sroiMaalgruppe === opt.id}
                      onChange={() => setSroiMaalgruppe(opt.id)}
                      style={{ accentColor: SoS.orange, width: 16, height: 16, flexShrink: 0 }}
                    />
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                      {opt.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Faglig helbreds-sektion — kun hvis aktiveret i admin */}
            {(window.SoS_SETTINGS || {}).visHelbredsforhold !== false && (
              <div style={{
                background: '#FFF8F0', border: `1.5px solid ${SoS.orange}30`,
                borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 14,
              }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: 10 }}>
                  <Icon name="shield" size={14} color={SoS.orange} style={{ marginTop: 1 }}/>
                  <div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                      color: SoS.orange }}>
                      Relevante helbredsforhold — fagligt brug
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                      marginTop: 2, lineHeight: 1.4 }}>
                      Frivilligt. GDPR art. 9. Bruges kun af brobygger til at støtte relationen
                      — ikke til diagnosticering eller individuel SROI-beregning.
                    </div>
                  </div>
                </div>

                {/* Kategori-flervalg */}
                <div style={{ marginBottom: 10 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                    color: SoS.inkSoft, marginBottom: 6, letterSpacing: 0.4,
                    textTransform: 'uppercase' }}>Overordnet kategori</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {(window.HELBREDS_KATEGORIER || []).map(kat => {
                      const on = helbredsKategorier.includes(kat.id);
                      return (
                        <button key={kat.id}
                          onClick={() => setHelbredsKategorier(prev =>
                            on ? prev.filter(k => k !== kat.id) : [...prev, kat.id]
                          )}
                          style={{
                            padding: '5px 12px', borderRadius: 999,
                            border: `1.5px solid ${on ? SoS.orange : SoS.lineSoft}`,
                            background: on ? SoS.orange + '15' : '#fff',
                            fontFamily: SoS.sans, fontSize: 12,
                            color: on ? SoS.orangeDeep : SoS.ink,
                            fontWeight: on ? 600 : 400,
                            cursor: 'pointer',
                          }}>
                          {kat.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Fritekst */}
                <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                  color: SoS.inkSoft, marginBottom: 6, letterSpacing: 0.4,
                  textTransform: 'uppercase' }}>Faglige noter til brobygger</div>
                <textarea
                  placeholder="F.eks. let demens, angst, mobilitetsvanskeligheder, kronisk smerte..."
                  value={udfordringer}
                  onChange={e => setUdfordringer(e.target.value)}
                  rows={3}
                  style={{
                    width: '100%', padding: '10px 12px',
                    fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                    border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm,
                    resize: 'vertical', background: '#fff', boxSizing: 'border-box',
                  }}
                />
              </div>
            )}"""

        html = html[:start_idx] + NEW_HEALTH_UI + html[close_idx + len(close_tag):]
        results.append(('IntakeFlow: health UI', 1, 1))
    else:
        results.append(('IntakeFlow: health UI — close_tag ikke fundet', 0, 0))
else:
    results.append(('IntakeFlow: health UI — start ikke fundet', 0, 0))

# ─────────────────────────────────────────────────
# 4.  MenneskeDetailPanel: opdater health-visning
# ─────────────────────────────────────────────────
OLD_DETAIL_HEALTH = """          {m.health && (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.5 }}>
              <span style={{ color: SoS.inkSoft }}>Helbred: </span>{m.health}
            </div>
          )}"""

NEW_DETAIL_HEALTH = """          {/* SROI-målgruppe pill */}
          {m.sroiMaalgruppe && m.sroiMaalgruppe !== 'ingen' && m.sroiMaalgruppe !== 'uoplyst' && (() => {
            const opt = (window.SROI_MAALGRUPPE_OPTIONS || []).find(o => o.id === m.sroiMaalgruppe);
            return opt ? (
              <div style={{ marginBottom: 4 }}>
                <Pill bg={SoS.creamDeep} color={SoS.inkSoft} style={{ fontSize: 11 }}>
                  SROI: {opt.label}
                </Pill>
              </div>
            ) : null;
          })()}
          {/* Helbredskategorier */}
          {m.helbredsKategorier && m.helbredsKategorier.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 6 }}>
              {m.helbredsKategorier.map(kid => {
                const kat = (window.HELBREDS_KATEGORIER || []).find(k => k.id === kid);
                return kat ? (
                  <Pill key={kid} bg={SoS.orange + '12'} color={SoS.orangeDeep}>{kat.label}</Pill>
                ) : null;
              })}
            </div>
          )}
          {/* Faglige helbredsnoter */}
          {m.health && (window.SoS_SETTINGS || {}).visHelbredsforhold !== false && (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.5 }}>
              <span style={{ color: SoS.inkSoft }}>Helbredsnoter: </span>{m.health}
            </div>
          )}"""

cnt = html.count(OLD_DETAIL_HEALTH)
html = html.replace(OLD_DETAIL_HEALTH, NEW_DETAIL_HEALTH, 1)
results.append(('MenneskeDetailPanel: health visning', cnt, 1))

# ─────────────────────────────────────────────────
# 5.  calcSROISnapshot — aggregeret, ingen per-borger
# ─────────────────────────────────────────────────
OLD_SNAPSHOT = """window.calcSROISnapshot = () =>
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
  });"""

NEW_SNAPSHOT = """// calcSROISnapshot returnerer KUN aggregerede tæller — aldrig per-borger objekter.
// Mental test: "Hvad er SROI-værdien for borger X?" → svaret er: "Den findes ikke."
window.calcSROISnapshot = () => {
  const mennesker = Object.values(window.SoS_MENNESKER || {});
  const result = {
    total: mennesker.length,
    byNiveau: { ingen: 0, kontakt: 0, mode: 0, folge: 0, fler: 0 },
    byMaalgruppe: {},
    byType: {},
    byIntensitet: { '0': 0, '1': 0, '2-3': 0, '4+': 0 },
  };
  mennesker.forEach(m => {
    const s = calcMenneskeStats(m.id);
    // Niveau
    result.byNiveau[s.indsatsniveau] = (result.byNiveau[s.indsatsniveau] || 0) + 1;
    // Type
    result.byType[m.type] = (result.byType[m.type] || 0) + 1;
    // SROI-målgruppe (analytisk)
    const mg = m.sroiMaalgruppe || 'uoplyst';
    result.byMaalgruppe[mg] = (result.byMaalgruppe[mg] || 0) + 1;
    // Intensitet
    const intKey = s.antalFolgeskaber >= 4 ? '4+' : s.antalFolgeskaber >= 2 ? '2-3' : s.antalFolgeskaber === 1 ? '1' : '0';
    result.byIntensitet[intKey] = (result.byIntensitet[intKey] || 0) + 1;
  });
  return result;
};"""

cnt = html.count(OLD_SNAPSHOT)
html = html.replace(OLD_SNAPSHOT, NEW_SNAPSHOT, 1)
results.append(('calcSROISnapshot: aggregeret', cnt, 1))

# ─────────────────────────────────────────────────
# 6.  Admin data-sektion: tilføj helbredsforhold-toggle
# ─────────────────────────────────────────────────
OLD_ADMIN_DATA_BTN = """          <button onClick={saveAndBack} style={{
            width: '100%', padding: '14px 0',
            background: saved ? SoS.sage : SoS.orange, color: '#fff',
            border: 'none', borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 15, fontWeight: 600, cursor: 'pointer',
          }}>{saved ? '✓ Gemt' : 'Gem indstillinger'}</button>
        </>)}"""

NEW_ADMIN_DATA_BTN = """          {/* Helbredsforhold-toggle */}
          <div style={{ background: '#fff', borderRadius: SoS.r.md,
            border: `1px solid ${SoS.lineSoft}`, padding: '14px 16px', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                  Vis faglig helbreds-sektion
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
                  marginTop: 3, lineHeight: 1.4 }}>
                  Kategorier og helbredsnoter i intake-flow og borger-profil.
                  Det analytiske SROI-felt vises altid.
                </div>
              </div>
              <button
                onClick={() => {
                  window.SoS_SETTINGS = window.SoS_SETTINGS || {};
                  window.SoS_SETTINGS.visHelbredsforhold = !(window.SoS_SETTINGS.visHelbredsforhold !== false);
                  setSaved(false);
                  setDataAccess(d => ({ ...d })); // force re-render
                }}
                style={{
                  width: 48, height: 28, borderRadius: 14,
                  background: (window.SoS_SETTINGS || {}).visHelbredsforhold !== false ? SoS.sage : SoS.lineSoft,
                  border: 'none', cursor: 'pointer', position: 'relative',
                  transition: 'background 0.2s', flexShrink: 0,
                }}>
                <div style={{
                  width: 20, height: 20, borderRadius: 10, background: '#fff',
                  position: 'absolute', top: 4,
                  left: (window.SoS_SETTINGS || {}).visHelbredsforhold !== false ? 24 : 4,
                  transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                }}/>
              </button>
            </div>
          </div>

          <button onClick={saveAndBack} style={{
            width: '100%', padding: '14px 0',
            background: saved ? SoS.sage : SoS.orange, color: '#fff',
            border: 'none', borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 15, fontWeight: 600, cursor: 'pointer',
          }}>{saved ? '✓ Gemt' : 'Gem indstillinger'}</button>
        </>)}"""

cnt = html.count(OLD_ADMIN_DATA_BTN)
html = html.replace(OLD_ADMIN_DATA_BTN, NEW_ADMIN_DATA_BTN, 1)
results.append(('Admin: helbredsforhold-toggle', cnt, 1))

# ─────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

#!/usr/bin/env python3
"""
Omnibus patch:
  1. Telefon påkrævet i intake trin 2
  2. Fjern SROI-sprog fra brugervendt UI
  3. HQ→kommuner mapping + StedSoeg lokal-sortering + Foretrukket mødested i trin 3
  4. Kilde-fordeling i Effekt & Dokumentation-skærmen
"""

import os
PATH = os.path.expanduser("~/Documents/Claude Code/brobygger-portal/Brobygger portal.html")

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
ok = 0
fail = 0

def p(old, new, label):
    global html, ok, fail
    if old not in html:
        print(f"  ✗ FEJL — ikke fundet: {label}")
        fail += 1
        return False
    html = html.replace(old, new, 1)
    print(f"  ✓ {label}")
    ok += 1
    return True

# ═══════════════════════════════════════════════════════════════════
# 1. TELEFON PÅKRÆVET
# ═══════════════════════════════════════════════════════════════════
print("\n── 1. Telefon påkrævet")

p(
    "  const canNext1 = form.firstName.trim().length > 0 && form.age.trim().length > 0;",
    "  const canNext1 = form.firstName.trim().length > 0 && form.age.trim().length > 0 && form.phone.trim().length > 0;",
    "canNext1: kræv phone"
)

p(
    "              Kun fornavn og alder er påkrævet. Øvrige oplysninger er frivillige.",
    "              Fornavn, alder og telefon er påkrævet. Øvrige oplysninger er frivillige.",
    "Sublabel: opdater obligatoriske felter"
)

p(
    "              { key: 'phone',     label: 'Telefon',   placeholder: 'Valgfrit' },",
    "              { key: 'phone',     label: 'Telefon',   placeholder: 'f.eks. +45 28 34 56 78', required: true },",
    "Phone: required + bedre placeholder"
)

# ═══════════════════════════════════════════════════════════════════
# 2. FJERN SROI-SPROG FRA BRUGERVENDT UI
# ═══════════════════════════════════════════════════════════════════
print("\n── 2. Fjern SROI-sprog fra brugervendt UI")

# Intake step 2: felt-overskrift
p(
    '            {/* SROI-målgruppe — analytisk felt */}',
    '            {/* Sundhedsudfordring — intern klassifikation */}',
    "Kommentar i intake step 2"
)
p(
    '                Matcher SROI-målgruppe?',
    '                Primær sundhedsudfordring',
    "Intake: overskrift uden SROI"
)
p(
    '                Bruges kun til aggregeret SROI-rapportering. Gemmes aldrig per borger i rapporter.',
    '                Bruges til at forstå personens udgangspunkt og understøtte den rette brobygning.',
    "Intake: sublabel uden SROI"
)

# Options
p(
    "  { id: 'ingen',   label: 'Matcher ikke SROI-målgruppen' },",
    "  { id: 'ingen',   label: 'Ingen af ovenstående' },",
    "Option 'ingen': neutral label"
)

# GDPR-tekst i helbreds-sektion
p(
    '                      — ikke til diagnosticering eller individuel SROI-beregning.',
    '                      — bruges udelukkende til at støtte relationen.',
    "GDPR-tekst: fjern SROI-reference"
)

# AdminSettings: helbreds-toggle note
p(
    '                  Kategorier og helbredsnoter i intake-flow og borger-profil.\n                  Det analytiske SROI-felt vises altid.',
    '                  Kategorier og helbredsnoter i intake-flow og borger-profil.',
    "AdminSettings toggle: fjern SROI-note"
)

# Menneske-kort: pill prefix
p(
    '                  SROI: {opt.label}',
    '                  {opt.label}',
    'Menneske-kort: fjern "SROI: " prefix på pill'
)

# Bekræftelsestekster
p(
    '        Kontakten tæller med i statistik og SROI-beregning.',
    '        Kontakten tæller med i statistik og dokumentation.',
    "Kontakt-bekræftelse: fjern SROI"
)
p(
    '            Kontakten er lagt til historikken og medregnes i SROI-beregning og rapporter.',
    '            Kontakten er lagt til historikken og medregnes i statistik og rapporter.',
    "Historik-bekræftelse: fjern SROI"
)
p(
    '            Hændelsen er gemt og tæller med i indsatsniveau og SROI-analyse.',
    '            Hændelsen er gemt og tæller med i indsatsniveau og dokumentation.',
    "Hændelse-bekræftelse: fjern SROI"
)

# Rådgiver-profil
p(
    '      Kontakt en admin for at ændre medarbejdere eller SROI-parametre.',
    '      Kontakt en admin for at ændre medarbejdere eller indstillinger.',
    "Rådgiver-profil: fjern SROI-parametre"
)

# Admin-mobil profil menu-item
p(
    "    { icon: 'users', label: 'Admin-indstillinger',    value: 'Medarbejdere, SROI m.m.',    action: onOpenSettings },",
    "    { icon: 'users', label: 'Admin-indstillinger',    value: 'Medarbejdere, indstillinger',  action: onOpenSettings },",
    "Admin-mobil profil: fjern SROI"
)

# AdminSettings menu-labels (admin-only — ingen problem med SROI der, det er internt)
p(
    "    { id: 'sroi',      icon: 'sparkle',  label: 'SROI-parametre',",
    "    { id: 'sroi',      icon: 'sparkle',  label: 'Effekt-parametre',",
    "AdminSettings menu: SROI-parametre → Effekt-parametre"
)
p(
    "    staff: 'Medarbejdere & roller', 'invite-bb': 'Inviter brobygger', sroi: 'SROI-parametre', 'match-frist': 'Matching-frist',",
    "    staff: 'Medarbejdere & roller', 'invite-bb': 'Inviter brobygger', sroi: 'Effekt-parametre', 'match-frist': 'Matching-frist',",
    "AdminSettings headers dict"
)
p(
    '              Disse værdier bruges til SROI-beregning i rapporter.\n              Baseret på Rambøll SROI-guide for civilsamfund.',
    "              Disse værdier afspejler den sociale effekt pr. brobygningstype.\n              Baseret på Rambøll's guide for civilsamfund.",
    "Effekt-sektion: fjern SROI fra brødtekst"
)
p(
    "              {sroiSaved ? '✓ Gemt' : 'Gem SROI-indstillinger'}",
    "              {sroiSaved ? '✓ Gemt' : 'Gem effekt-indstillinger'}",
    "Gem-knap i SROI-sektion"
)

# Desktop menu-tab
p(
    "      { k: 'sroi',         l: 'SROI & Effekt',      i: 'sparkle'  },",
    "      { k: 'sroi',         l: 'Effekt & Dokumentation', i: 'sparkle' },",
    "Desktop menu-tab"
)
p(
    "                   kalender: 'Kalender', sroi: 'SROI & Effekt', rapport: 'Rapport & eksport' }[section]}",
    "                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport' }[section]}",
    "Desktop sektion-header"
)

# DesktopSROI hero card
p(
    "          Social Return on Investment · Jan–apr 2026",
    "          Effekt & dokumentation · Jan–apr 2026",
    "DesktopSROI: hero card titel"
)

# ═══════════════════════════════════════════════════════════════════
# 3. HQ-KOMMUNER + STEDSOEG + INTAKE TRIN 3
# ═══════════════════════════════════════════════════════════════════
print("\n── 3. HQ-kommuner + StedSoeg + intake trin 3")

# 3a. Kommuner-mapping — indsæt efter SoS.hq closing brace
HQ_KOMMUNER = """
// HQ → Kommuner — bruges til lokal-sortering i StedSoeg
const SoS_HQ_KOMMUNER = {
  'Aarhus':      ['Aarhus'],
  'Kronjylland': ['Randers', 'Favrskov', 'Norddjurs', 'Syddjurs'],
  'Midt':        ['Viborg', 'Silkeborg', 'Ikast-Brande', 'Herning', 'Ringkøbing-Skjern'],
  'Nord':        ['Aalborg', 'Rebild', 'Vesthimmerlands', 'Jammerbugt', 'Thisted', 'Frederikshavn', 'Hjørring', 'Brønderslev', 'Mariagerfjord', 'Morsø'],
  'Syd':         ['Vejle', 'Kolding', 'Fredericia', 'Middelfart', 'Billund', 'Haderslev', 'Vejen'],
  'Sydvest':     ['Esbjerg', 'Fanø', 'Varde', 'Aabenraa', 'Sønderborg', 'Tønder'],
  'Fyn':         ['Odense', 'Kerteminde', 'Nordfyns', 'Faaborg-Midtfyn', 'Svendborg', 'Langeland', 'Ærø', 'Assens', 'Nyborg'],
  'Sjælland':    ['Næstved', 'Slagelse', 'Ringsted', 'Sorø', 'Faxe', 'Vordingborg', 'Guldborgsund', 'Lolland', 'Stevns', 'Køge', 'Greve', 'Roskilde', 'Holbæk', 'Kalundborg', 'Odsherred'],
  'Hovedstaden': ['København', 'Frederiksberg', 'Gentofte', 'Lyngby-Taarbæk', 'Rudersdal', 'Hørsholm', 'Helsingør', 'Frederikssund', 'Hillerød', 'Furesø', 'Allerød', 'Egedal', 'Gladsaxe', 'Herlev', 'Ballerup', 'Rødovre', 'Brøndby', 'Glostrup', 'Bornholm'],
};

"""

p(
    '  },\n\n  // Radii — rounded, soft',
    '  },\n' + HQ_KOMMUNER + '  // Radii — rounded, soft',
    "Tilføj SoS_HQ_KOMMUNER"
)

# 3b. StedSoeg: tilføj viewingHq prop
p(
    "const StedSoeg = ({ value, onChange }) => {",
    "const StedSoeg = ({ value, onChange, viewingHq }) => {",
    "StedSoeg: viewingHq prop"
)

# 3c. StedSoeg: lokal-sortering i filter
p(
    """  const q = query.toLowerCase().trim();
  const filtered = q.length < 1 ? [] : SoS_STEDER.filter(s => {
    const haystack = [s.navn, s.sygehus || '', s.by || ''].join(' ').toLowerCase();
    return q.split(' ').every(word => haystack.includes(word));
  }).slice(0, 18);""",
    """  const q = query.toLowerCase().trim();
  const localKommuner = viewingHq && window.SoS_HQ_KOMMUNER ? (window.SoS_HQ_KOMMUNER[viewingHq] || []) : [];
  const isLocal = s => localKommuner.length > 0 && localKommuner.some(k => (s.by || '').includes(k));
  const matched = q.length < 1 ? [] : SoS_STEDER.filter(s => {
    const haystack = [s.navn, s.sygehus || '', s.by || ''].join(' ').toLowerCase();
    return q.split(' ').every(word => haystack.includes(word));
  });
  const filtered = [...matched.filter(isLocal), ...matched.filter(s => !isLocal(s))].slice(0, 18);
  const hasLocalAndOther = filtered.some(isLocal) && filtered.some(s => !isLocal(s));""",
    "StedSoeg: lokal-sortering"
)

# 3d. StedSoeg: opdater groups-loop til at indsætte divider
p(
    """  // Group by sygehus for sygehus-afsnit, else flat
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
  });""",
    """  // Group by sygehus; sæt divider efter lokale resultater
  const groups = [];
  const seenSygehus = {};
  let dividerInserted = false;
  filtered.forEach(s => {
    const loc = isLocal(s);
    if (!loc && !dividerInserted && hasLocalAndOther) {
      groups.push({ _divider: true });
      dividerInserted = true;
    }
    if (s.type === 'sygehus-afsnit') {
      const key = s.sygehus + '|' + s.by;
      if (!seenSygehus[key]) { seenSygehus[key] = { label: s.sygehus, by: s.by, local: loc, items: [] }; groups.push(seenSygehus[key]); }
      seenSygehus[key].items.push(s);
    } else {
      groups.push({ label: null, by: null, local: loc, items: [s] });
    }
  });""",
    "StedSoeg: lokal divider i groups-loop"
)

# 3e. StedSoeg: render divider + Lokal badge i gruppe-header
p(
    """          {groups.length === 0 ? (
            <div style={{ padding: 16, fontFamily: SoS.sans, fontSize: 13,
              color: SoS.inkMuted, textAlign: 'center' }}>
              Ingen resultater — prøv en anden søgning
            </div>
          ) : groups.map((g, gi) => (
            <div key={gi}>
              {/* Sygehus group header */}
              {g.label && (
                <div style={{ padding: '10px 14px 4px',
                  fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',
                  borderTop: gi > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                  {g.label} · {g.by}
                </div>
              )}""",
    """          {groups.length === 0 ? (
            <div style={{ padding: 16, fontFamily: SoS.sans, fontSize: 13,
              color: SoS.inkMuted, textAlign: 'center' }}>
              Ingen resultater — prøv en anden søgning
            </div>
          ) : groups.map((g, gi) => (
            <div key={gi}>
              {/* Divider: lokale → øvrige */}
              {g._divider && (
                <div style={{ padding: '6px 14px', fontFamily: SoS.sans, fontSize: 10,
                  fontWeight: 700, color: SoS.inkMuted, letterSpacing: 0.8,
                  textTransform: 'uppercase', borderTop: `1px solid ${SoS.lineSoft}`,
                  background: SoS.creamDeep }}>
                  Øvrige steder
                </div>
              )}
              {/* Sygehus group header */}
              {!g._divider && g.label && (
                <div style={{ padding: '10px 14px 4px',
                  fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',
                  borderTop: gi > 0 ? `1px solid ${SoS.lineSoft}` : 'none',
                  display: 'flex', alignItems: 'center', gap: 6 }}>
                  {g.label} · {g.by}
                  {g.local && <span style={{ background: SoS.sage + '25', color: SoS.sage,
                    borderRadius: 4, padding: '1px 5px', fontSize: 9, fontWeight: 700,
                    letterSpacing: 0.4 }}>LOKAL</span>}
                </div>
              )}""",
    "StedSoeg: render divider + Lokal badge"
)

# 3f. StedSoeg: Lokal badge på enkelt-items (lægehuse osv.)
p(
    """                    <Pill bg={meta.bg} color={meta.color} style={{ flexShrink: 0 }}>
                      {meta.label}
                    </Pill>""",
    """                    {g.local && <span style={{ background: SoS.sage + '25', color: SoS.sage,
                      borderRadius: 4, padding: '2px 6px', fontFamily: SoS.sans, fontSize: 10,
                      fontWeight: 700, letterSpacing: 0.3, flexShrink: 0 }}>Lokal</span>}
                    <Pill bg={meta.bg} color={meta.color} style={{ flexShrink: 0 }}>
                      {meta.label}
                    </Pill>""",
    "StedSoeg: Lokal badge på enkelt-items"
)

# 3g. IntakeFlow: tilføj viewingHq prop + brobygSted state
p(
    "const IntakeFlow = ({ onClose }) => {",
    "const IntakeFlow = ({ onClose, viewingHq }) => {",
    "IntakeFlow: tilføj viewingHq prop"
)
p(
    "  const [brobygNote, setBrobygNote] = React.useState('');",
    "  const [brobygNote, setBrobygNote] = React.useState('');\n  const [brobygSted, setBrobygSted] = React.useState(null);",
    "IntakeFlow: brobygSted state"
)

# 3h. Intake trin 3: tilføj Foretrukket mødested efter Notat
p(
    """            {/* Notat */}
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
                Notat <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>
              </div>
              <textarea
                value={brobygNote}
                onChange={e => setBrobygNote(e.target.value)}
                rows={2}
                placeholder="F.eks. foretrækker formiddage..."
                style={{ ...inputStyle, resize: 'none', lineHeight: 1.5 }}
              />
            </div>
          </>
        )}""",
    """            {/* Notat */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
                Notat <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>
              </div>
              <textarea
                value={brobygNote}
                onChange={e => setBrobygNote(e.target.value)}
                rows={2}
                placeholder="F.eks. foretrækker formiddage..."
                style={{ ...inputStyle, resize: 'none', lineHeight: 1.5 }}
              />
            </div>

            {/* Foretrukket mødested */}
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
                Foretrukket mødested <span style={{ fontWeight: 400, color: SoS.inkMuted }}>(valgfrit)</span>
              </div>
              <StedSoeg value={brobygSted} onChange={setBrobygSted} viewingHq={viewingHq}/>
            </div>
          </>
        )}""",
    "Intake trin 3: StedSoeg felt"
)

# 3i. Prototype frame: send viewingHq til IntakeFlow
p(
    '    content = <IntakeFlow onClose={() => setTweak("flow", "none")} />;',
    '    content = <IntakeFlow onClose={() => setTweak("flow", "none")} viewingHq={viewingHq}/>;',
    "Prototype frame: send viewingHq til IntakeFlow"
)

# ═══════════════════════════════════════════════════════════════════
# 4. KILDE-FORDELING I EFFEKT & DOKUMENTATION + kilde på mennesker
# ═══════════════════════════════════════════════════════════════════
print("\n── 4. Kilde-fordeling i effekt-skærmen")

# 4a. Tilføj kilde-felt til eksisterende mennesker
p(
    "    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk', 'somatisk'],\n    notes: [\n      { date: '14. apr', from: 'Maja H.', text: 'Vi gik til Risskov strand.",
    "    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk', 'somatisk'],\n    kilde: 'hospital',\n    notes: [\n      { date: '14. apr', from: 'Maja H.', text: 'Vi gik til Risskov strand.",
    "b-1: kilde = hospital"
)
p(
    "    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: [],\n    notes: [\n      { date: '9. apr', from: 'Maja H.', text: 'Øvede tid hos tandlæge",
    "    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: [],\n    kilde: 'kommune',\n    notes: [\n      { date: '9. apr', from: 'Maja H.', text: 'Øvede tid hos tandlæge",
    "b-2: kilde = kommune"
)

# For b-3 through b-6, add after their sroiMaalgruppe lines
p(
    "    sroiMaalgruppe: 'kronisk',\n    helbredsKategorier: ['somatisk'],",
    "    sroiMaalgruppe: 'kronisk',\n    helbredsKategorier: ['somatisk'],\n    kilde: 'selv',",
    "b-3: kilde = selv"
)
p(
    "    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk'],",
    "    sroiMaalgruppe: 'psykisk',\n    helbredsKategorier: ['psykisk'],\n    kilde: 'paarørende',",
    "b-4: kilde = paarørende"
)
p(
    "    sroiMaalgruppe: 'uoplyst',\n    helbredsKategorier: [],",
    "    sroiMaalgruppe: 'uoplyst',\n    helbredsKategorier: [],\n    kilde: 'kommune',",
    "b-5: kilde = kommune"
)
p(
    "    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: ['neuro'],",
    "    sroiMaalgruppe: 'ingen',\n    helbredsKategorier: ['neuro'],\n    kilde: 'org',",
    "b-6: kilde = org"
)

# 4b. Tilføj kilde-fordeling DSCard i DesktopSROI, efter UCLA-3-sektionen
KILDE_CARD = """
      <DSCard title="Indgang · hvem henviser" style={{ marginTop: 10 }}>
        {(() => {
          const kildeStat = {};
          Object.values(SoS_MENNESKER).forEach(m => {
            const k = m.kilde || 'ukendt';
            kildeStat[k] = (kildeStat[k] || 0) + 1;
          });
          const total = Object.values(kildeStat).reduce((a, b) => a + b, 0);
          const KILDE_META = {
            selv:       { label: 'Egen henvendelse',    color: SoS.sage },
            kommune:    { label: 'Kommunal henvisning', color: SoS.sky },
            hospital:   { label: 'Hospitalsudslusning', color: SoS.orange },
            paarørende: { label: 'Familie / pårørende', color: '#8C6BAE' },
            org:        { label: 'Anden organisation',  color: '#7FA089' },
            ukendt:     { label: 'Ikke registreret',    color: SoS.inkMuted },
          };
          const sorted = Object.entries(kildeStat).sort((a, b) => b[1] - a[1]);
          return (
            <div>
              {sorted.map(([k, n]) => {
                const meta = KILDE_META[k] || KILDE_META.ukendt;
                const pct = Math.round(n / total * 100);
                return (
                  <div key={k} style={{ marginBottom: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between',
                      alignItems: 'center', marginBottom: 4 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                        <div style={{ width: 8, height: 8, borderRadius: 4, background: meta.color }}/>
                        <span style={{ fontFamily: SoS.sans, fontSize: 13,
                          color: SoS.ink, fontWeight: 500 }}>{meta.label}</span>
                      </div>
                      <span style={{ fontFamily: SoS.sans, fontSize: 12,
                        color: SoS.inkSoft }}>{n} pers. · {pct}%</span>
                    </div>
                    <div style={{ height: 6, borderRadius: 3, background: SoS.lineSoft }}>
                      <div style={{ height: '100%', borderRadius: 3,
                        background: meta.color, width: `${pct}%`,
                        transition: 'width 0.4s' }}/>
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })()}
      </DSCard>
"""

p(
    "      <DSCard title=\"Effekt · UCLA-3 over tid\">",
    KILDE_CARD + "      <DSCard title=\"Effekt · UCLA-3 over tid\">",
    "DesktopSROI: indsæt kilde-fordelings DSCard"
)

# ═══════════════════════════════════════════════════════════════════
# Gem
# ═══════════════════════════════════════════════════════════════════
print(f"\n  ✓ {ok} patches lykkedes | ✗ {fail} fejlede")
print(f"  Størrelse: {original_len:,} → {len(html):,} bytes (+{len(html)-original_len:+,})")

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✓ Gemt til disk.")

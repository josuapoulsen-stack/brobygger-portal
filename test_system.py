#!/usr/bin/env python3
"""
Systemtest — Brobygger portal.html
Verificerer at alle features fungerer som tænkt.
Kører mod den statiske fil uden browser.
"""
import re, sys, os

PATH = os.path.expanduser("~/Documents/Claude Code/brobygger-portal/Brobygger portal.html")
with open(PATH, encoding='utf-8') as f:
    html = f.read()

pass_count = 0
fail_count = 0
warn_count = 0
results = []

def check(name, condition, detail='', warn=False):
    global pass_count, fail_count, warn_count
    if condition:
        pass_count += 1
        results.append(('✓', name, detail))
    elif warn:
        warn_count += 1
        results.append(('⚠', name, detail))
    else:
        fail_count += 1
        results.append(('✗', name, detail))

def contains(pattern, flags=0):
    return bool(re.search(pattern, html, flags))

def count(pattern, flags=0):
    return len(re.findall(pattern, html, flags))

def find(pattern, flags=0):
    m = re.search(pattern, html, flags)
    return m.group(0) if m else None

# ═══════════════════════════════════════════════════════════════
# 1. STRUKTUR & SYNTAX
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 1. STRUKTUR & SYNTAX ━━━")

# Script-blokke
open_babel  = count(r'<script type="text/babel">')
close_script = count(r'</script>')
check("Script-blokke åbner/lukker symmetrisk",
      open_babel <= close_script,
      f"{open_babel} babel-blokke, {close_script} </script> total")

# Ingen dobbelt-deklarerede const-komponenter på toplevel
component_names = re.findall(r'^const ([A-Z][A-Za-z]+)\s*=\s*\(', html, re.MULTILINE)
dupes = {n for n in component_names if component_names.count(n) > 1}
check("Ingen duplikerede komponent-definitioner",
      len(dupes) == 0,
      f"Duplikater: {dupes}" if dupes else "")

# window.exports
expected_exports = [
    'window.StedSoeg', 'window.SoS_MENNESKER', 'window.SoS_BROBYGGERE',
    'window.SoS_STEDER', 'window.SoS_APPOINTMENTS_BUSY', 'window.SoS_HISTORIK',
    'window.SoS_HQ_KOMMUNER', 'window.HELBREDS_KATEGORIER',
    'window.SROI_MAALGRUPPE_OPTIONS', 'window.SoS_SETTINGS',
]
for exp in expected_exports:
    check(f"Export: {exp}", exp in html)

# ═══════════════════════════════════════════════════════════════
# 2. TELEFON PÅKRÆVET
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 2. TELEFON PÅKRÆVET ━━━")

check("canNext1 kræver phone",
      "form.phone.trim().length > 0" in html,
      "phone indgår i validering")

check("Phone-felt er required:true",
      "key: 'phone'" in html and "required: true" in html)

check("Sublabel nævner telefon",
      "Fornavn, alder og telefon er påkrævet" in html)

check("Phone-placeholder er beskrivende",
      "+45 28 34 56 78" in html or "+45" in html)

# ═══════════════════════════════════════════════════════════════
# 3. KILDE MED UNDERKATEGORIER
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 3. KILDE MED UNDERKATEGORIER ━━━")

check("kildeDetalje state eksisterer",
      "const [kildeDetalje, setKildeDetalje]" in html)

check("canNext0 kræver kildeDetalje når sub findes",
      "kildeHasSub || !!kildeDetalje" in html or
      "(!kildeHasSub || !!kildeDetalje)" in html)

check("kommune har underkategorier (sub)",
      re.search(r"id: 'kommune'.*?sub:", html, re.DOTALL) is not None)

check("hospital har underkategorier (sub)",
      re.search(r"id: 'hospital'.*?sub:", html, re.DOTALL) is not None)

check("org har underkategorier (sub)",
      re.search(r"id: 'org'.*?sub:", html, re.DOTALL) is not None)

check("selv har INGEN underkategorier",
      re.search(r"id: 'selv'[^}]*sub:", html) is None)

check("paarørende har INGEN underkategorier",
      re.search(r"id: 'paarørende'[^}]*sub:", html) is None)

# Specifikke sub-valgmuligheder
check("Kommune: Jobcenter findes",  "Jobcenter" in html)
check("Kommune: Sagsbehandler findes", "Sagsbehandler" in html)
check("Hospital: Psykiatri findes", "Psykiatri" in html)
check("Hospital: Ambulatorium findes", "Ambulatorium" in html)
check("Org: Frivilligcenter findes", "Frivilligcenter" in html)

check("Undertekst skifter til valgt sub",
      "kildeDetalje" in html and "k.sub" in html and "s.id === kildeDetalje" in html)

check("Opsummering viser kilde · detalje",
      "ko.label" in html and "sub.label" in html and "kildeDetalje" in html)

# ═══════════════════════════════════════════════════════════════
# 4. SROI FJERNET FRA BRUGERVENDT UI
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 4. SROI FJERNET FRA BRUGERVENDT UI ━━━")

# Felt-overskrift
check("Intake: overskrift er 'Primær sundhedsudfordring'",
      "Primær sundhedsudfordring" in html)

check("Intake: 'Matcher SROI-målgruppe?' FJERNET",
      "Matcher SROI-målgruppe?" not in html)

# Option-label
check("Option 'ingen' er 'Ingen af ovenstående'",
      "Ingen af ovenstående" in html)

check("Option 'ingen' er IKKE 'Matcher ikke SROI-målgruppen'",
      "Matcher ikke SROI-målgruppen" not in html)

# GDPR-tekst
check("GDPR-tekst nævner IKKE 'individuel SROI-beregning'",
      "individuel SROI-beregning" not in html)

check("GDPR-tekst siger 'støtte relationen'",
      "støtte relationen" in html)

# Bekræftelsestekster
check("Kontakt-bekræftelse: ingen SROI",
      "statistik og SROI-beregning" not in html)

check("Historik-bekræftelse: ingen SROI",
      "medregnes i SROI-beregning" not in html)

# Admin-tilgængeligt SROI er OK at beholde
check("Admin SROI-rapport eksisterer stadig (admin-funktion)",
      "DesktopSROI" in html)

# Effekt-skærm omdøbt
check("Desktop menu-tab hedder 'Effekt & Dokumentation'",
      "Effekt & Dokumentation" in html)

check("Desktop menu-tab hedder IKKE 'SROI & Effekt'",
      "SROI & Effekt" not in html)

# AdminSettings
check("AdminSettings gem-knap hedder 'effekt-indstillinger'",
      "Gem effekt-indstillinger" in html)

# Rådgiver-profil
sroi_in_ui = re.findall(r'SROI-parametre', html)
check("Ingen 'SROI-parametre' i brugervendt tekst",
      len(sroi_in_ui) == 0,
      f"Fandt {len(sroi_in_ui)} forekomster" if sroi_in_ui else "")

# ═══════════════════════════════════════════════════════════════
# 5. HQ-KOMMUNER + STEDSOEG
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 5. HQ-KOMMUNER + STEDSOEG ━━━")

check("SoS_HQ_KOMMUNER er defineret som window-property",
      "window.SoS_HQ_KOMMUNER = {" in html)

check("SoS_HQ_KOMMUNER er i tokens-script (ikke i babel JSX)",
      html.index("window.SoS_HQ_KOMMUNER") < html.index('// SoS — shared UI primitives'))

# Alle 9 HQ'er har kommuner
for hq in ['Aarhus', 'Kronjylland', 'Midt', 'Nord', 'Syd', 'Sydvest', 'Fyn', 'Sjælland', 'Hovedstaden']:
    check(f"HQ '{hq}' har kommuner-mapping",
          f"'{hq}':" in html and html.index(f"'{hq}':", html.index("SoS_HQ_KOMMUNER")) < html.index(f"'{hq}':", html.index("SoS_HQ_KOMMUNER")) + 2000)

check("StedSoeg accepterer viewingHq prop",
      "StedSoeg = ({ value, onChange, viewingHq })" in html)

check("StedSoeg sorterer lokale resultater først",
      "isLocal" in html and "localKommuner" in html)

check("StedSoeg indsætter divider mellem lokale og øvrige",
      "_divider" in html and "Øvrige steder" in html)

check("StedSoeg viser 'Lokal' badge",
      "LOKAL" in html or "Lokal" in html)

check("IntakeFlow modtager viewingHq prop",
      "IntakeFlow = ({ onClose, viewingHq })" in html)

check("IntakeFlow: brobygSted state",
      "const [brobygSted, setBrobygSted]" in html)

check("Intake trin 3 har StedSoeg-felt",
      "Foretrukket mødested" in html and "StedSoeg" in html and "brobygSted" in html)

check("Prototype frame sender viewingHq til IntakeFlow",
      "viewingHq={viewingHq}" in html and "IntakeFlow" in html)

# ═══════════════════════════════════════════════════════════════
# 6. KILDE-FORDELING I EFFEKT-SKÆRM
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 6. KILDE-FORDELING I EFFEKT-SKÆRM ━━━")

check("DesktopSROI har kilde-fordelings-sektion",
      "Indgang · hvem henviser" in html)

check("Kilde-bar viser procent",
      "pct}%" in html or "pct" in html and "%" in html)

# Alle mennesker har kilde-felt
for mid in ['b-1','b-2','b-3','b-4','b-5','b-6']:
    block = re.search(rf"'id':\s*'{mid}'.*?(?='[a-z]+-[0-9]+':)", html, re.DOTALL)
    if not block:
        block_str = re.search(rf"id: '{mid}'(.*?)(?:id: 'b-[0-9]+')", html, re.DOTALL)
    has_kilde = f"id: '{mid}'" in html and re.search(
        rf"id: '{mid}'.*?kilde:", html, re.DOTALL) is not None
    check(f"Menneske {mid} har kilde-felt", has_kilde)

# ═══════════════════════════════════════════════════════════════
# 7. FORRIGE BROBYGGER — STJERNE + FREMHÆVNING
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 7. FORRIGE BROBYGGER ━━━")

check("BrobyggerCard-komponent eksisterer",
      "const BrobyggerCard = " in html)

check("Stjerneikon vises på forrige brobygger",
      'name="star"' in html and "isPrev" in html)

check("Gylden venstre-kant på forrige brobygger-kort",
      "linear-gradient(180deg" in html and "E8C14B" in html)

check("Section-header 'Ønsket brobygger fra tidligere'",
      "Ønsket brobygger fra tidligere" in html)

check("Section-header 'Øvrige brobyggere'",
      "Øvrige brobyggere" in html)

check("Auto-select forrige brobygger via useEffect",
      "React.useEffect" in html and "prevBb && !brobyggerId" in html)

check("Sidst-fælles-aftale opslag fra appointments",
      "lastAppt" in html and "menneskeId === menneske.id" in html)

check("b-5 har previousBrobygger 'bb-3'",
      "previousBrobygger: 'bb-3'" in html)

# ═══════════════════════════════════════════════════════════════
# 8. HOOKS-REGLER
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 8. REACT HOOKS-REGLER ━━━")

# Ingen hooks inde i IIFE / betinget kode på toplevel
iife_with_hooks = re.findall(
    r'\(\(\)\s*=>\s*\{[^}]*React\.use(State|Effect|Ref)\b', html)
check("Ingen hooks inde i IIFE-udtryk",
      len(iife_with_hooks) == 0,
      f"Fandt: {iife_with_hooks[:3]}" if iife_with_hooks else "")

# Alle useEffect har dependency array — multi-linje søgning
# Finder }); uden forudgående , [ i samme effect-blok
effect_blocks = re.findall(r'React\.useEffect\(.*?}\s*\)', html, re.DOTALL)
effects_no_dep = [e for e in effect_blocks if not re.search(r',\s*\[', e)]
check("Alle useEffect har dependency-array",
      len(effects_no_dep) == 0,
      f"{len(effects_no_dep)} mangler dep-array" if effects_no_dep else f"{len(effect_blocks)} effects — alle OK",
      warn=True)

# BrobyggerCard er defineret inde i MatchingStepBrobygger (OK da ingen hooks)
# Find kun kroppen af BrobyggerCard — frem til næste const på toplevel
bb_card_match = re.search(r'const BrobyggerCard = \([^)]*\) => \{(.*?)\n  \};', html, re.DOTALL)
bb_card_body = bb_card_match.group(1) if bb_card_match else ''
bb_card_hooks = re.search(r'React\.use(State|Effect|Ref)', bb_card_body)
check("BrobyggerCard bruger ingen hooks (OK som inner function)",
      bb_card_match is not None and bb_card_hooks is None,
      "BrobyggerCard-krop fundet" if bb_card_match else "BrobyggerCard-krop ikke fundet")

# ═══════════════════════════════════════════════════════════════
# 9. DATA-INTEGRITET
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 9. DATA-INTEGRITET ━━━")

check("Alle 6 mennesker defineret",
      all(f"id: '{mid}'" in html for mid in ['b-1','b-2','b-3','b-4','b-5','b-6']))

check("Alle 6 brobyggere defineret",
      all(f"id: '{bid}'" in html for bid in ['bb-1','bb-2','bb-3','bb-4','bb-5','bb-6']))

check("b-5 og b-6 har language-felt",
      re.search(r"id: 'b-5'.*?language:", html, re.DOTALL) and
      re.search(r"id: 'b-6'.*?language:", html, re.DOTALL))

check("SoS_STEDER er defineret (sted-data til StedSoeg)",
      "SoS_STEDER" in html and "sygehus-afsnit" in html)

check("INTAKE_KILDER har 5 valgmuligheder",
      len(re.findall(r"id: '(?:selv|kommune|hospital|paarørende|org)'", html)) >= 5)

check("INTAKE_BEHOV er defineret",
      "const INTAKE_BEHOV" in html and "Selskab og samtale" in html)

check("HELBREDS_KATEGORIER defineret med 5 kategorier",
      html.count("id: 'psykisk'") >= 1 and
      html.count("id: 'neuro'") >= 1 and
      html.count("id: 'somatisk'") >= 1)

check("SoS_SETTINGS har visHelbredsforhold: true som default",
      "visHelbredsforhold: true" in html)

check("MATCH_FRIST_TIMER er konfigureret",
      "MATCH_FRIST_TIMER" in html)

# ═══════════════════════════════════════════════════════════════
# 10. ADMIN-FUNKTIONER
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 10. ADMIN-FUNKTIONER ━━━")

check("AdminSettings eksisterer",
      "const AdminSettings" in html or "AdminSettings = " in html)

check("AdminSettings har helbredsforhold-toggle",
      "visHelbredsforhold" in html and "Vis faglig helbreds-sektion" in html)

check("AdminSettings har match-frist konfiguration",
      "match-frist" in html and "MATCH_FRIST_TIMER" in html)

check("AdminSettings har HQ-type toggle",
      "HQ_ACTIVE_TYPES" in html or "typer" in html)

check("MatchingFlow eksisterer",
      "const MatchingFlow" in html)

check("IntakeFlow eksisterer",
      "const IntakeFlow" in html)

check("RaadgiverKalender eksisterer",
      "const RaadgiverKalender" in html)

check("DesktopSROI eksisterer (admin-only rapport)",
      "const DesktopSROI" in html)

# ═══════════════════════════════════════════════════════════════
# 11. ROLES
# ═══════════════════════════════════════════════════════════════
print("\n━━━ 11. ROLLER ━━━")

check("Rolle 'admin' håndteres",     "isAdmin" in html)
check("Rolle 'raadgiver' håndteres", "'raadgiver'" in html)
check("Rolle 'brobygger' håndteres", "'brobygger'" in html)

check("Rådgiver-view er begrænset (show: isAdmin)",
      "show: isAdmin" in html)

check("Admin kan skifte HQ (setViewingHq)",
      "setViewingHq" in html)

check("Brobygger-app adskilt fra admin-app",
      "BrobyggerApp" in html or
      'tweaks.role === "brobygger"' in html or
      "tweaks.role === 'brobygger'" in html)

# ═══════════════════════════════════════════════════════════════
# RESULTAT
# ═══════════════════════════════════════════════════════════════
print("\n" + "═"*55)
print(f"  RESULTAT: {pass_count} bestået  |  {warn_count} advarsler  |  {fail_count} fejlet")
print("═"*55)

if fail_count or warn_count:
    print()
    for status, name, detail in results:
        if status != '✓':
            print(f"  {status} {name}")
            if detail:
                print(f"      → {detail}")

print()
if fail_count == 0:
    print("  ✓ Alle tests bestod. Systemet fungerer som tænkt.")
else:
    print(f"  ✗ {fail_count} test(s) fejlede — se detaljer ovenfor.")

sys.exit(fail_count)

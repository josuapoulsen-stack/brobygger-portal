import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# 1) Flettefelter: tilføj transport (afhentning) + diagnose i resolver
sub(
    "    aktivitet:         appt.activity || '',\n"
    "    bb_fornavn:        bb ? (bb.name || '').split(' ')[0] : '',",
    "    aktivitet:         appt.activity || '',\n"
    "    transport:         appt.transportplan || (m && m.transportplan) || '',\n"
    "    diagnose:          m ? (m.health || '') : '',\n"
    "    bb_fornavn:        bb ? (bb.name || '').split(' ')[0] : '',",
    "1: resolver felter")

# 2) Flettefelt-liste: tilføj Afhentning/transport + Diagnose
sub(
    "  ['Dato','dato'],['Tid','tid'],['Sted','sted'],['Aktivitet','aktivitet'],['Brobygger','bb_fornavn'],",
    "  ['Dato','dato'],['Tid','tid'],['Sted','sted'],['Afhentning/transport','transport'],['Aktivitet','aktivitet'],['Diagnose ⚠','diagnose'],['Brobygger','bb_fornavn'],",
    "2: felt-liste")

# 3) Per-rådgiver: kun mine egne (+ ejerløse legacy) skabeloner
sub(
    "  const alle = [...SoS_BRIEFING_SEEDS, ...stored];",
    "  const me = window.SoS_AKTIV_BRUGER || (window.SoS_USER && window.SoS_USER.name) || 'mig';\n"
    "  const mineStored = stored.filter(t => !t.ejer || t.ejer === me);\n"
    "  const alle = [...SoS_BRIEFING_SEEDS, ...mineStored];",
    "3: filter mine")

# 4) Stempel ejer ved oprettelse af ny skabelon
sub(
    "    else persistStored([...stored, { id: 'skab-' + Date.now(), navn: redNavn.trim(), indsats: redIndsats, tekst: redTekst, erStandard: false }]);",
    "    else persistStored([...stored, { id: 'skab-' + Date.now(), navn: redNavn.trim(), indsats: redIndsats, tekst: redTekst, erStandard: false, ejer: me }]);",
    "4: stempel ejer")

# 5) Header: 'Mine skabeloner'
sub(
    "        {header('Skabeloner', () => setView('compose'))}",
    "        {header('Mine skabeloner', () => setView('compose'))}",
    "5: header mine")

# 6) Eksponér aktiv bruger globalt (så BriefingModal kan eje pr. rådgiver)
sub(
    "      : (isNew ? SoS.sky : SoS.orange),\n"
    "  };\n"
    "\n"
    "  useEffect(() => {\n"
    "    setScreen(\"hjem\");",
    "      : (isNew ? SoS.sky : SoS.orange),\n"
    "  };\n"
    "\n"
    "  useEffect(() => { try { window.SoS_AKTIV_BRUGER = user.name; } catch (e) {} }, [user.name]);\n"
    "\n"
    "  useEffect(() => {\n"
    "    setScreen(\"hjem\");",
    "6: aktiv bruger global")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

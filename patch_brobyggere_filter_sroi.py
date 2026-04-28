# -*- coding: utf-8 -*-
"""
patch_brobyggere_filter_sroi.py
1. AdminBrobyggereScreen: typeFilter prop — filtrerer brobyggere ud fra hvilke
   typer af mennesker de er matchet med.
2. AdminMobile: sender typeFilter ned til AdminBrobyggereScreen.
3. DesktopSROI: erstatter hardkodede tal (521/702/911) med live data fra
   calcSROISnapshot() + kobler SROI-beregning til det faktiske datagrundlag.
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. AdminBrobyggereScreen: accepter typeFilter prop + filtrer ──────────
OLD_BB_DEF = (
    "const AdminBrobyggereScreen = ({ hovedsaede, onOpenMatching }) => {\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
    "  const [search, setSearch] = React.useState('');\n"
    "  const filtered = SoS_BROBYGGERE.filter(b => (filter === 'alle' || b.status === filter) && (!search || b.name.toLowerCase().includes(search.toLowerCase())));"
)
NEW_BB_DEF = (
    "const AdminBrobyggereScreen = ({ hovedsaede, onOpenMatching, typeFilter: typeFProp }) => {\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
    "  const [search, setSearch] = React.useState('');\n"
    "  const filtered = SoS_BROBYGGERE.filter(b => {\n"
    "    const matchStatus = filter === 'alle' || b.status === filter;\n"
    "    const matchSearch = !search || b.name.toLowerCase().includes(search.toLowerCase());\n"
    "    const matchType = !typeFProp || typeFProp === 'alle' ||\n"
    "      Object.values(SoS_MENNESKER).some(m => m.matchedWith === b.id && m.type === typeFProp);\n"
    "    return matchStatus && matchSearch && matchType;\n"
    "  });"
)
cnt = html.count(OLD_BB_DEF)
html = html.replace(OLD_BB_DEF, NEW_BB_DEF, 1)
results.append(('AdminBrobyggereScreen: typeFilter prop + filter', cnt, 1))

# ── 2. AdminMobile: send typeFilter til AdminBrobyggereScreen ─────────────
OLD_BB_RENDER = "    <AdminBrobyggereScreen hovedsaede={viewingHq} onOpenMatching={onOpenMatching}/>"
NEW_BB_RENDER = "    <AdminBrobyggereScreen hovedsaede={viewingHq} onOpenMatching={onOpenMatching} typeFilter={typeFilter}/>"
cnt = html.count(OLD_BB_RENDER)
html = html.replace(OLD_BB_RENDER, NEW_BB_RENDER, 1)
results.append(('AdminMobile: typeFilter til AdminBrobyggereScreen', cnt, 1))

# ── 3. DesktopSROI: brug live calcSROISnapshot i stedet for 521/702/911 ──
OLD_SROI_CALC = (
    "const DesktopSROI = () => {\n"
    "  const rates = window.SROI_SETTINGS || { sundhed: 1840, forening: 1420, social: 1260, investment: 8400000 };\n"
    "  const sroi = 521 * rates.sundhed + 702 * rates.forening + 911 * rates.social;\n"
    "  const investment = rates.investment;"
)
NEW_SROI_CALC = (
    "const DesktopSROI = () => {\n"
    "  const rates = window.SROI_SETTINGS || { sundhed: 1840, forening: 1420, social: 1260, investment: 8400000 };\n"
    "  const snap = window.calcSROISnapshot ? window.calcSROISnapshot() : { byType: {} };\n"
    "  const sundhedCount  = snap.byType.sundhed  || 0;\n"
    "  const foreningCount = snap.byType.forening || 0;\n"
    "  const socialCount   = snap.byType.social   || 0;\n"
    "  const sroi = sundhedCount * rates.sundhed + foreningCount * rates.forening + socialCount * rates.social;\n"
    "  const investment = rates.investment;"
)
cnt = html.count(OLD_SROI_CALC)
html = html.replace(OLD_SROI_CALC, NEW_SROI_CALC, 1)
results.append(('DesktopSROI: live calcSROISnapshot', cnt, 1))

# ── 4. DesktopSROI: erstat hardkodede count-tal i type-rækker ────────────
OLD_SROI_ROWS = (
    "          { k: 'sundhed', count: 521, rate: 1840 },\n"
    "            { k: 'forening', count: 702, rate: 1420 },\n"
    "            { k: 'social', count: 911, rate: 1260 },"
)
NEW_SROI_ROWS = (
    "          { k: 'sundhed',  count: sundhedCount,  rate: rates.sundhed  },\n"
    "            { k: 'forening', count: foreningCount, rate: rates.forening },\n"
    "            { k: 'social',   count: socialCount,   rate: rates.social   },"
)
cnt = html.count(OLD_SROI_ROWS)
html = html.replace(OLD_SROI_ROWS, NEW_SROI_ROWS, 1)
results.append(('DesktopSROI: dynamiske type-tal', cnt, 1))

# ── 5. DesktopSROI type-rækker: "aftaler" -> "mennesker" (korrekt enhed) ─
OLD_SROI_UNIT = '                  {r.count} aftaler'
NEW_SROI_UNIT = '                  {r.count} mennesker'
cnt = html.count(OLD_SROI_UNIT)
html = html.replace(OLD_SROI_UNIT, NEW_SROI_UNIT, 1)
results.append(('DesktopSROI: enhed mennesker (ikke aftaler)', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

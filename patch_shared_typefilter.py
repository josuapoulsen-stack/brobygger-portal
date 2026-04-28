# -*- coding: utf-8 -*-
"""
patch_shared_typefilter.py
Gør typeFilter i AdminMobile til et delt filter der påvirker alle tabs:
  - Kalender (RaadgiverKalender bruger nu AdminMobiles typeFilter som prop)
  - Mennesker (AdminMenneskeListe filtrerer også på type)
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. RaadgiverKalender: accepter typeFilter som valgfri prop ────────────
OLD_RAA_SIG = "const RaadgiverKalender = ({ viewingHq }) => {"
NEW_RAA_SIG = "const RaadgiverKalender = ({ viewingHq, typeFilter: tfProp, setTypeFilter: setTfProp }) => {"
cnt = html.count(OLD_RAA_SIG)
html = html.replace(OLD_RAA_SIG, NEW_RAA_SIG, 1)
results.append(('RaadgiverKalender: prop-signatur', cnt, 1))

# ── 2. RaadgiverKalender: brug prop hvis givet, ellers lokal state ────────
OLD_RAA_STATE = (
    "  const [typeFilter, setTypeFilter] = React.useState('alle');\n"
    "  const weekDays = ['Man','Tir','Ons','Tor','Fre','L\u00f8r','S\u00f8n'];"
)
NEW_RAA_STATE = (
    "  const [_localTf, _setLocalTf] = React.useState('alle');\n"
    "  const typeFilter = tfProp !== undefined ? tfProp : _localTf;\n"
    "  const setTypeFilter = setTfProp || _setLocalTf;\n"
    "  const weekDays = ['Man','Tir','Ons','Tor','Fre','L\u00f8r','S\u00f8n'];"
)
cnt = html.count(OLD_RAA_STATE)
html = html.replace(OLD_RAA_STATE, NEW_RAA_STATE, 1)
results.append(('RaadgiverKalender: state → prop-fallback', cnt, 1))

# ── 3. AdminMobile: send typeFilter ned til RaadgiverKalender ─────────────
OLD_RAA_RENDER = "          <RaadgiverKalender viewingHq={viewingHq}/>"
NEW_RAA_RENDER = "          <RaadgiverKalender viewingHq={viewingHq} typeFilter={typeFilter} setTypeFilter={setTypeFilter}/>"
cnt = html.count(OLD_RAA_RENDER)
html = html.replace(OLD_RAA_RENDER, NEW_RAA_RENDER, 1)
results.append(('AdminMobile: typeFilter → RaadgiverKalender', cnt, 1))

# ── 4. AdminMenneskeListe: accepter typeFilter prop ───────────────────────
OLD_ML_DEF = (
    "const AdminMenneskeListe = ({ viewingHq, onOpenMatching }) => {\n"
    "  const [search, setSearch] = React.useState('');\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const alle = Object.values(SoS_MENNESKER);\n"
    "  const filtered = alle.filter(m => {\n"
    "    const matchSearch = !search || (m.firstName + ' ' + (m.lastName || '')).toLowerCase().includes(search.toLowerCase());\n"
    "    const matchFilter = filter === 'alle' || (filter === 'matchet' ? m.matchedWith : !m.matchedWith);\n"
    "    return matchSearch && matchFilter;\n"
    "  });"
)
NEW_ML_DEF = (
    "const AdminMenneskeListe = ({ viewingHq, onOpenMatching, typeFilter: typeFProp }) => {\n"
    "  const [search, setSearch] = React.useState('');\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const alle = Object.values(SoS_MENNESKER);\n"
    "  const filtered = alle.filter(m => {\n"
    "    const matchSearch = !search || (m.firstName + ' ' + (m.lastName || '')).toLowerCase().includes(search.toLowerCase());\n"
    "    const matchFilter = filter === 'alle' || (filter === 'matchet' ? m.matchedWith : !m.matchedWith);\n"
    "    const matchType = !typeFProp || typeFProp === 'alle' || m.type === typeFProp;\n"
    "    return matchSearch && matchFilter && matchType;\n"
    "  });"
)
cnt = html.count(OLD_ML_DEF)
html = html.replace(OLD_ML_DEF, NEW_ML_DEF, 1)
results.append(('AdminMenneskeListe: typeFilter prop', cnt, 1))

# ── 5. AdminMobile: send typeFilter ned til AdminMenneskeListe ────────────
OLD_ML_RENDER = "          <AdminMenneskeListe viewingHq={viewingHq} onOpenMatching={onOpenMatching}/>"
NEW_ML_RENDER = "          <AdminMenneskeListe viewingHq={viewingHq} onOpenMatching={onOpenMatching} typeFilter={typeFilter}/>"
cnt = html.count(OLD_ML_RENDER)
html = html.replace(OLD_ML_RENDER, NEW_ML_RENDER, 1)
results.append(('AdminMobile: typeFilter → AdminMenneskeListe', cnt, 1))

# ── 6. Vis aktiv-filter-chip øverst på kalender og mennesker tabs ─────────
# Indsæt en diskret "Filtrerer: Sundhed × Nulstil"-chip i RaadgiverKalender
# øverst, kun synlig når typeFilter !== 'alle' og styret af prop
OLD_KALENDER_HEADER = (
    "            <div style={{ padding: '16px 16px 12px', background: '#fff',\n"
    "              borderBottom: `1px solid ${SoS.lineSoft}` }}>"
)
NEW_KALENDER_HEADER = (
    "            {tfProp !== undefined && tfProp !== 'alle' && (() => {\n"
    "              const t = SoS_TYPER[tfProp];\n"
    "              return (\n"
    "                <div style={{ padding: '10px 16px', background: t.soft,\n"
    "                  borderBottom: `1px solid ${t.color}30`,\n"
    "                  display: 'flex', alignItems: 'center', gap: 8 }}>\n"
    "                  <Icon name={t.icon} size={13} color={t.color}/>\n"
    "                  <span style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                    color: t.color, fontWeight: 600 }}>\n"
    "                    Filtrerer: {t.label}\n"
    "                  </span>\n"
    "                  <button onClick={() => setTfProp('alle')} style={{\n"
    "                    marginLeft: 'auto', background: 'none', border: 'none',\n"
    "                    fontFamily: SoS.sans, fontSize: 11, color: t.color,\n"
    "                    cursor: 'pointer', padding: '2px 8px',\n"
    "                    borderRadius: 999, fontWeight: 600,\n"
    "                  }}>\u00d7 Nulstil</button>\n"
    "                </div>\n"
    "              );\n"
    "            })()}\n"
    "            <div style={{ padding: '16px 16px 12px', background: '#fff',\n"
    "              borderBottom: `1px solid ${SoS.lineSoft}` }}>"
)
cnt = html.count(OLD_KALENDER_HEADER)
html = html.replace(OLD_KALENDER_HEADER, NEW_KALENDER_HEADER, 1)
results.append(('RaadgiverKalender: aktiv-filter-chip', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

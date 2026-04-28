# -*- coding: utf-8 -*-
"""
patch_type_filter.py
Tilføjer prominent type-filter øverst på forsiden (arbejde-fane) i AdminMobile.
Filtrerer: Aftaler i dag + Match-frist-advarsler.
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. Tilføj typeFilter state til AdminMobile ────────────────────────
OLD_STATE = "  const [selectedAppt, setSelectedAppt] = React.useState(null);"
NEW_STATE = "  const [selectedAppt, setSelectedAppt] = React.useState(null);\n  const [typeFilter, setTypeFilter] = React.useState('alle');"
cnt = html.count(OLD_STATE)
html = html.replace(OLD_STATE, NEW_STATE, 1)
results.append(('AdminMobile: typeFilter state', cnt, 1))

# ── 2. Indsæt type-filter UI øverst i arbejde-fanen ─────────────────
OLD_ARBEJDE_TOP = """tab === 'arbejde' && (
          <>
            {/* Handlinger */}
            <div style={{ padding: '16px 20px 8px' }}>
              <SectionHead title="Skal handles på"/>
            </div>"""

NEW_ARBEJDE_TOP = """tab === 'arbejde' && (
          <>
            {/* Type-filter — prominent */}
            <div style={{ padding: '16px 16px 12px', background: '#fff',
              borderBottom: `1px solid ${SoS.lineSoft}` }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',
                marginBottom: 10 }}>Vis brobygningstype</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
                {[
                  { id: 'alle',    label: 'Alle',    color: SoS.ink,    soft: SoS.creamDeep, icon: null },
                  { id: 'sundhed', label: 'Sundhed', color: SoS_TYPER.sundhed.color, soft: SoS_TYPER.sundhed.soft, icon: 'sundhed' },
                  { id: 'forening',label: 'Forening',color: SoS_TYPER.forening.color,soft: SoS_TYPER.forening.soft,icon: 'forening' },
                  { id: 'social',  label: 'Social',  color: SoS_TYPER.social.color,  soft: SoS_TYPER.social.soft,  icon: 'social' },
                ].map(f => {
                  const sel = typeFilter === f.id;
                  return (
                    <button key={f.id} onClick={() => setTypeFilter(f.id)} style={{
                      display: 'flex', flexDirection: 'column', alignItems: 'center',
                      justifyContent: 'center', gap: 6,
                      padding: '12px 4px',
                      background: sel ? f.color : f.soft,
                      border: `2px solid ${sel ? f.color : 'transparent'}`,
                      borderRadius: SoS.r.md,
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                      boxShadow: sel ? SoS.shadow.sm : 'none',
                    }}>
                      {f.icon && (
                        <Icon name={f.icon === 'sundhed' ? 'heart' : f.icon === 'forening' ? 'users' : 'heart'}
                          size={18} color={sel ? '#fff' : f.color}/>
                      )}
                      {!f.icon && (
                        <div style={{ width: 18, height: 18, borderRadius: 9,
                          background: sel ? 'rgba(255,255,255,0.3)' : SoS.lineSoft,
                          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <div style={{ width: 6, height: 6, borderRadius: 3,
                            background: sel ? '#fff' : SoS.inkSoft }}/>
                        </div>
                      )}
                      <span style={{
                        fontFamily: SoS.sans, fontSize: 11, fontWeight: sel ? 700 : 500,
                        color: sel ? '#fff' : f.color,
                        letterSpacing: 0.2,
                      }}>{f.label}</span>
                    </button>
                  );
                })}
              </div>
              {typeFilter !== 'alle' && (() => {
                const t = SoS_TYPER[typeFilter];
                const count = Object.values(SoS_MENNESKER).filter(m =>
                  m.type === typeFilter && m.status === 'aktiv').length;
                return (
                  <div style={{ marginTop: 10, padding: '8px 12px',
                    background: t.soft, borderRadius: SoS.r.sm,
                    display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Icon name={t.icon} size={14} color={t.color}/>
                    <span style={{ fontFamily: SoS.sans, fontSize: 12,
                      color: t.color, fontWeight: 600 }}>
                      {count} aktive mennesker · {t.label}
                    </span>
                    <button onClick={() => setTypeFilter('alle')} style={{
                      marginLeft: 'auto', background: 'none', border: 'none',
                      fontFamily: SoS.sans, fontSize: 11, color: t.color,
                      cursor: 'pointer', padding: '2px 8px',
                      borderRadius: 999, fontWeight: 600,
                    }}>× Nulstil</button>
                  </div>
                );
              })()}
            </div>

            {/* Handlinger */}
            <div style={{ padding: '16px 20px 8px' }}>
              <SectionHead title="Skal handles på"/>
            </div>"""

cnt = html.count(OLD_ARBEJDE_TOP)
html = html.replace(OLD_ARBEJDE_TOP, NEW_ARBEJDE_TOP, 1)
results.append(('AdminMobile: type-filter UI', cnt, 1))

# ── 3. Filtrer todayAppts baseret på typeFilter ───────────────────────
# todayAppts er defineret som SoS_APPOINTMENTS_BUSY.slice(0, 3)
# Vi skal bruge typeFilter i render — erstat todayAppts.map med filtreret version

OLD_TODAY = "              {todayAppts.map(a => {\n                const menneske = SoS_MENNESKER[a.menneskeId];\n                const type = SoS_TYPER[menneske.type];"
NEW_TODAY = """              {todayAppts.filter(a => {
                const m = SoS_MENNESKER[a.menneskeId];
                return !m || typeFilter === 'alle' || m.type === typeFilter;
              }).map(a => {
                const menneske = SoS_MENNESKER[a.menneskeId];
                const type = SoS_TYPER[menneske.type];"""

cnt = html.count(OLD_TODAY)
html = html.replace(OLD_TODAY, NEW_TODAY, 1)
results.append(('AdminMobile: filtrer aftaler i dag', cnt, 1))

# ── 4. Filtrer match-frist-advarsler ─────────────────────────────────
OLD_OVERDUE = "              const overdueList = Object.values(SoS_MENNESKER).filter(m => {\n                if (m.matchedWith || !m.registeredAt) return false;\n                const hrs = (now - new Date(m.registeredAt)) / 3600000;\n                return hrs > frist;\n              });"
NEW_OVERDUE = """              const overdueList = Object.values(SoS_MENNESKER).filter(m => {
                if (m.matchedWith || !m.registeredAt) return false;
                if (typeFilter !== 'alle' && m.type !== typeFilter) return false;
                const hrs = (now - new Date(m.registeredAt)) / 3600000;
                return hrs > frist;
              });"""

cnt = html.count(OLD_OVERDUE)
html = html.replace(OLD_OVERDUE, NEW_OVERDUE, 1)
results.append(('AdminMobile: filtrer match-frist', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

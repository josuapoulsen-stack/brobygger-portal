# -*- coding: utf-8 -*-
"""
patch_desktop_mennesker_brobygninger.py
Erstatter de to stub-komponenter med fuldt implementerede versioner:
  - DesktopMennesker: søg, filtrer, tabel med alle mennesker + detail-panel
  - DesktopBrobygninger: type-statistik + aftaletabel med filter
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ─────────────────────────────────────────────────────────────────────
# 1. DesktopMennesker
# ─────────────────────────────────────────────────────────────────────
OLD_DM = """const DesktopMennesker = () => (
  <DSCard>
    <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
      Mennesker i systemet · 689 aktive · CRUD, opret, redigér, anonymisér
    </div>
    <div style={{ marginTop: 16, padding: 20, textAlign: 'center', background: SoS.cream,
      borderRadius: 10, fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
      Liste af mennesker med filter · type · hovedsæde · status
    </div>
  </DSCard>
);"""

NEW_DM = """const DesktopMennesker = () => {
  const [search,   setSearch]   = React.useState('');
  const [typeFilter, setTypeFilter] = React.useState('alle');
  const [statusFilter, setStatusFilter] = React.useState('alle');
  const [selected, setSelected] = React.useState(null);
  const [showIntake, setShowIntake] = React.useState(false);

  const alle = Object.values(SoS_MENNESKER);
  const filtered = alle.filter(m => {
    const navn = (m.firstName + ' ' + m.lastName).toLowerCase();
    if (search && !navn.includes(search.toLowerCase())) return false;
    if (typeFilter !== 'alle' && m.type !== typeFilter) return false;
    if (statusFilter !== 'alle' && m.status !== statusFilter) return false;
    return true;
  });

  const STATUS_FARVER = {
    aktiv:  { bg: '#E8F5E9', color: '#388E3C' },
    venter: { bg: '#FFF3E0', color: '#E87A3E' },
    pause:  { bg: '#F5F5F5', color: '#9E9E9E' },
    afsluttet: { bg: '#FCE4EC', color: '#C62828' },
  };

  if (showIntake) return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 300, overflowY: 'auto' }}>
      <IntakeFlow onClose={() => setShowIntake(false)} onDone={() => setShowIntake(false)}/>
    </div>
  );
  if (selected) return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 300, overflowY: 'auto',
      background: SoS.cream, padding: 24 }}>
      <MenneskeDetailPanel menneske={selected} onClose={() => setSelected(null)}/>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8,
          background: '#fff', borderRadius: 999, padding: '9px 16px',
          border: `1px solid ${SoS.lineSoft}` }}>
          <Icon name="search" size={16} color={SoS.inkMuted}/>
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Søg på navn…"
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent',
              fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}/>
        </div>
        <button onClick={() => setShowIntake(true)} style={{
          padding: '9px 18px', background: SoS.orange, color: '#fff',
          border: 'none', borderRadius: 999, fontFamily: SoS.sans,
          fontSize: 13, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap',
        }}>+ Opret menneske</button>
      </div>

      {/* Filtre */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {['alle', 'sundhed', 'forening', 'social'].map(f => {
          const t = SoS_TYPER[f];
          const sel = typeFilter === f;
          return (
            <button key={f} onClick={() => setTypeFilter(f)} style={{
              padding: '5px 14px', borderRadius: 999,
              background: sel ? (t ? t.color : SoS.ink) : '#fff',
              color: sel ? '#fff' : SoS.inkSoft,
              border: `1.5px solid ${sel ? (t ? t.color : SoS.ink) : SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400,
              cursor: 'pointer',
            }}>{f === 'alle' ? 'Alle typer' : t.label}</button>
          );
        })}
        <div style={{ width: 1, background: SoS.lineSoft, margin: '0 4px' }}/>
        {['alle', 'aktiv', 'venter', 'pause'].map(s => {
          const sel = statusFilter === s;
          const fc = STATUS_FARVER[s] || {};
          return (
            <button key={s} onClick={() => setStatusFilter(s)} style={{
              padding: '5px 14px', borderRadius: 999,
              background: sel ? (fc.color || SoS.ink) : '#fff',
              color: sel ? '#fff' : SoS.inkSoft,
              border: `1.5px solid ${sel ? (fc.color || SoS.ink) : SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400,
              cursor: 'pointer',
            }}>{s === 'alle' ? 'Alle statusser' : s.charAt(0).toUpperCase() + s.slice(1)}</button>
          );
        })}
      </div>

      {/* Tabel */}
      <DSCard style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: SoS.creamDeep, borderBottom: `2px solid ${SoS.line}` }}>
              {['Menneske', 'Type', 'Status', 'Indsatsniveau', 'Kontakter', 'Registreret'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left',
                  fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={6} style={{ padding: 24, textAlign: 'center',
                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen mennesker matcher søgningen
              </td></tr>
            )}
            {filtered.map((m, i) => {
              const t = SoS_TYPER[m.type];
              const stats = calcMenneskeStats(m.id);
              const nMeta = INDSATS_META[stats.indsatsniveau];
              const sf = STATUS_FARVER[m.status] || {};
              const dato = m.startedAt || m.registeredAt || '';
              return (
                <tr key={m.id}
                  onClick={() => setSelected(m)}
                  style={{ borderBottom: `1px solid ${SoS.lineSoft}`,
                    cursor: 'pointer', background: i % 2 === 0 ? '#fff' : SoS.cream + '60',
                    transition: 'background 0.1s' }}
                  onMouseEnter={e => e.currentTarget.style.background = SoS.creamDeep}
                  onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? '#fff' : SoS.cream + '60'}
                >
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <Avatar initials={m.initials} bg={t.color} size={34}/>
                      <div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                          color: SoS.ink }}>{m.firstName} {m.lastName}</div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                          {m.age} år · {(m.language || 'Dansk').split(',')[0]}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <Pill bg={t.soft} color={t.color}>{t.short}</Pill>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <Pill bg={sf.bg || SoS.creamDeep} color={sf.color || SoS.inkSoft}>
                      {m.status}
                    </Pill>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 4,
                        background: nMeta.color, flexShrink: 0 }}/>
                      <span style={{ fontFamily: SoS.sans, fontSize: 12, color: nMeta.color,
                        fontWeight: 600 }}>{nMeta.label}</span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', fontFamily: SoS.sans, fontSize: 13,
                    color: SoS.ink, textAlign: 'center' }}>
                    {stats.antalKontakter}
                  </td>
                  <td style={{ padding: '12px 14px', fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkSoft }}>
                    {dato ? new Date(dato).toLocaleDateString('da-DK',
                      { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ padding: '10px 14px', background: SoS.creamDeep,
          fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
          borderTop: `1px solid ${SoS.lineSoft}` }}>
          Viser {filtered.length} af {alle.length} mennesker
        </div>
      </DSCard>
    </div>
  );
};"""

cnt = html.count(OLD_DM)
html = html.replace(OLD_DM, NEW_DM, 1)
results.append(('DesktopMennesker', cnt, 1))

# ─────────────────────────────────────────────────────────────────────
# 2. DesktopBrobygninger
# ─────────────────────────────────────────────────────────────────────
OLD_DB = """const DesktopBrobygninger = () => (
  <DSCard>
    <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginBottom: 16 }}>
      847 brobygninger · Jan–apr 2026
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 10, marginBottom: 20 }}>
      {Object.values(SoS_TYPER).map(t => (
        <div key={t.id} style={{ padding: 16, background: t.soft, borderRadius: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <Icon name={t.icon} size={18} color={t.color}/>
            <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
              color: t.color, textTransform: 'uppercase', letterSpacing: 0.6 }}>{t.short}</span>
          </div>
          <div style={{ fontFamily: SoS.font, fontSize: 34, fontWeight: 500,
            color: t.color, letterSpacing: -0.8 }}>
            {t.id === 'sundhed' ? 213 : t.id === 'forening' ? 284 : 350}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 4 }}>
            {t.id === 'sundhed' ? '521' : t.id === 'forening' ? '702' : '911'} gennemførte aftaler
          </div>
        </div>
      ))}
    </div>
    <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, fontStyle: 'italic' }}>
      (Detaljeret drill-down visning — listeoversigt, filter, søgning, drilldown per brobygning)
    </div>
  </DSCard>
);"""

NEW_DB = """const DesktopBrobygninger = () => {
  const [statusFilter, setStatusFilter] = React.useState('alle');
  const [typeFilter,   setTypeFilter]   = React.useState('alle');

  const appts = SoS_APPOINTMENTS_BUSY || [];
  const filtered = appts.filter(a => {
    const m = SoS_MENNESKER[a.menneskeId];
    if (!m) return false;
    if (typeFilter !== 'alle' && m.type !== typeFilter) return false;
    if (statusFilter === 'confirmed' && a.status !== 'confirmed') return false;
    if (statusFilter === 'pending'   && a.status !== 'pending')   return false;
    return true;
  });

  const STATUS_LABEL = { confirmed: 'Bekræftet', pending: 'Afventer' };
  const STATUS_COLOR = { confirmed: '#388E3C', pending: '#E87A3E' };
  const STATUS_BG    = { confirmed: '#E8F5E9', pending: '#FFF3E0' };

  const typeCount = (tid) =>
    Object.values(SoS_MENNESKER).filter(m => m.type === tid && m.status === 'aktiv').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* Type-statistik */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {Object.values(SoS_TYPER).map(t => (
          <DSCard key={t.id} style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 18, background: t.soft,
                display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon name={t.icon} size={18} color={t.color}/>
              </div>
              <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                color: t.color, textTransform: 'uppercase', letterSpacing: 0.5 }}>{t.label}</span>
            </div>
            <div style={{ fontFamily: SoS.font, fontSize: 36, fontWeight: 500,
              color: t.color, letterSpacing: -1, lineHeight: 1 }}>
              {t.id === 'sundhed' ? 213 : t.id === 'forening' ? 284 : 350}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 6 }}>
              {t.id === 'sundhed' ? '521' : t.id === 'forening' ? '702' : '911'} gennemførte aftaler
            </div>
            <div style={{ marginTop: 8, paddingTop: 8, borderTop: `1px solid ${SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
              {typeCount(t.id)} aktive mennesker
            </div>
          </DSCard>
        ))}
      </div>

      {/* Filterlinje */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
          letterSpacing: 0.5, textTransform: 'uppercase', fontWeight: 700 }}>Type:</span>
        {['alle', 'sundhed', 'forening', 'social'].map(f => {
          const t = SoS_TYPER[f];
          const sel = typeFilter === f;
          return (
            <button key={f} onClick={() => setTypeFilter(f)} style={{
              padding: '4px 12px', borderRadius: 999,
              background: sel ? (t ? t.color : SoS.ink) : '#fff',
              color: sel ? '#fff' : SoS.inkSoft,
              border: `1.5px solid ${sel ? (t ? t.color : SoS.ink) : SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400, cursor: 'pointer',
            }}>{f === 'alle' ? 'Alle' : t.short}</button>
          );
        })}
        <div style={{ width: 1, background: SoS.lineSoft, margin: '0 4px', height: 18 }}/>
        <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
          letterSpacing: 0.5, textTransform: 'uppercase', fontWeight: 700 }}>Status:</span>
        {['alle', 'confirmed', 'pending'].map(s => {
          const sel = statusFilter === s;
          return (
            <button key={s} onClick={() => setStatusFilter(s)} style={{
              padding: '4px 12px', borderRadius: 999,
              background: sel ? (STATUS_COLOR[s] || SoS.ink) : '#fff',
              color: sel ? '#fff' : SoS.inkSoft,
              border: `1.5px solid ${sel ? (STATUS_COLOR[s] || SoS.ink) : SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400, cursor: 'pointer',
            }}>{s === 'alle' ? 'Alle' : STATUS_LABEL[s]}</button>
          );
        })}
      </div>

      {/* Aftaletabel */}
      <DSCard style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: SoS.creamDeep, borderBottom: `2px solid ${SoS.line}` }}>
              {['Dato', 'Menneske', 'Brobygger', 'Aktivitet', 'Sted', 'Status'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left',
                  fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                  color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={6} style={{ padding: 24, textAlign: 'center',
                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen aftaler matcher filteret
              </td></tr>
            )}
            {filtered.map((a, i) => {
              const m  = SoS_MENNESKER[a.menneskeId];
              const t  = m ? SoS_TYPER[m.type] : null;
              const bb = (SoS_BROBYGGERE || []).find(b => b.id === a.brobyggerId);
              const dato = new Date(a.date).toLocaleDateString('da-DK',
                { weekday: 'short', day: 'numeric', month: 'short' });
              return (
                <tr key={a.id} style={{
                  borderBottom: `1px solid ${SoS.lineSoft}`,
                  background: i % 2 === 0 ? '#fff' : SoS.cream + '60',
                }}>
                  <td style={{ padding: '11px 14px', fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkSoft, whiteSpace: 'nowrap' }}>
                    {dato}<br/>
                    <span style={{ color: SoS.inkMuted }}>{a.start}–{a.end}</span>
                  </td>
                  <td style={{ padding: '11px 14px' }}>
                    {m ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Avatar initials={m.initials} bg={t ? t.color : SoS.inkSoft} size={28}/>
                        <div>
                          <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                            color: SoS.ink }}>{m.firstName} {m.lastName[0]}.</div>
                          {t && <Pill bg={t.soft} color={t.color} style={{ fontSize: 10 }}>{t.short}</Pill>}
                        </div>
                      </div>
                    ) : '—'}
                  </td>
                  <td style={{ padding: '11px 14px' }}>
                    {bb ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Avatar initials={bb.avatar} bg={bb.bg} size={28}/>
                        <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                          {bb.name.split(' ')[0]}
                        </span>
                      </div>
                    ) : '—'}
                  </td>
                  <td style={{ padding: '11px 14px', fontFamily: SoS.sans, fontSize: 13,
                    color: SoS.ink }}>{a.activity}</td>
                  <td style={{ padding: '11px 14px', fontFamily: SoS.sans, fontSize: 12,
                    color: SoS.inkSoft }}>{a.location}</td>
                  <td style={{ padding: '11px 14px' }}>
                    <Pill bg={STATUS_BG[a.status] || SoS.creamDeep}
                      color={STATUS_COLOR[a.status] || SoS.inkSoft}>
                      {STATUS_LABEL[a.status] || a.status}
                    </Pill>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ padding: '10px 14px', background: SoS.creamDeep,
          fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
          borderTop: `1px solid ${SoS.lineSoft}` }}>
          Viser {filtered.length} af {appts.length} aftaler
        </div>
      </DSCard>
    </div>
  );
};"""

cnt = html.count(OLD_DB)
html = html.replace(OLD_DB, NEW_DB, 1)
results.append(('DesktopBrobygninger', cnt, 1))

# ─────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

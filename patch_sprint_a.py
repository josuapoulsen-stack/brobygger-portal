import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

ok = []
fail = []

def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1)
        ok.append(label)
    else:
        fail.append(label)

# ══════════════════════════════════════════════════════════════════
# A3a: Menu — ny rækkefølge, fjern brobygninger, omdøb dashboard
# ══════════════════════════════════════════════════════════════════
sub(
    "            {[\n"
    "              { k: 'dashboard',    l: 'Dashboard',          i: 'chart'    },\n"
    "              { k: 'kalender',     l: 'Kalender',           i: 'calendar' },\n"
    "              { k: 'brobygninger', l: 'Brobygninger',       i: 'match'    },\n"
    "              { k: 'brobyggere',   l: 'Brobyggere',         i: 'users'    },\n"
    "              { k: 'mennesker',    l: 'Mennesker',          i: 'heart'    },\n"
    "              { k: 'beskeder',    l: 'Beskeder',           i: 'chat'    },\n"
    "              ].concat(canRapport ? [{ k: 'rapport', l: 'Rapport & eksport', i: 'note' }] : [])",
    "            {[\n"
    "              { k: 'oversigt',   l: 'Oversigt',    i: 'chart'    },\n"
    "              { k: 'mennesker',  l: 'Mennesker',   i: 'heart'    },\n"
    "              { k: 'brobyggere', l: 'Brobyggere',  i: 'users'    },\n"
    "              { k: 'kalender',   l: 'Kalender',    i: 'calendar' },\n"
    "              { k: 'beskeder',   l: 'Beskeder',    i: 'chat'     },\n"
    "              ].concat(canRapport ? [{ k: 'rapport', l: 'Rapport & eksport', i: 'note' }] : [])",
    "A3a: menu ny raekkefølge"
)

# ══════════════════════════════════════════════════════════════════
# A3b: Sidetitel-map — oversigt erstatter dashboard
# ══════════════════════════════════════════════════════════════════
sub(
    "{ dashboard: 'Dashboard', brobygninger: 'Brobygninger',\n"
    "                   brobyggere: 'Brobyggere', mennesker: 'Mennesker', beskeder: 'Beskeder',\n"
    "                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport', brugerstyring: 'Brugerstyring' }[section]",
    "{ oversigt: 'Oversigt', brobygninger: 'Brobygninger',\n"
    "                   brobyggere: 'Brobyggere', mennesker: 'Mennesker', beskeder: 'Beskeder',\n"
    "                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport', brugerstyring: 'Brugerstyring' }[section]",
    "A3b: sidetitel oversigt"
)

# ══════════════════════════════════════════════════════════════════
# A3c: Section rendering — dashboard → oversigt
# ══════════════════════════════════════════════════════════════════
sub(
    "{section === 'dashboard' && <DesktopDashboard viewingHq={viewingHq} canRapport={canRapport}/>}",
    "{section === 'oversigt' && <DesktopDashboard viewingHq={viewingHq} canRapport={canRapport}/>}",
    "A3c: section rendering oversigt"
)

# ══════════════════════════════════════════════════════════════════
# A3d: Initial section state kalender → oversigt
# ══════════════════════════════════════════════════════════════════
sub(
    "const [section, setSection] = React.useState('kalender');\n  const [viewingHq, setViewingHq]",
    "const [section, setSection] = React.useState('oversigt');\n  const [viewingHq, setViewingHq]",
    "A3d: initial section oversigt"
)

# ══════════════════════════════════════════════════════════════════
# A1+A2+A4: DesktopDashboard — fuld omskrivning
#   - Dagsorden øverst (opfølgning + afventer match, altid synlig)
#   - KPI-strip nedenunder (4 tiles, 5 med SROI for leder)
#   - Grafer og tabel til sidst
#   - Proper function component med hooks på top-niveau
# ══════════════════════════════════════════════════════════════════
start_marker = 'const DesktopDashboard = ({ viewingHq, canRapport }) => ('
end_marker   = '\nconst DesktopBrobyggere = '

start_idx = c.find(start_marker)
end_idx   = c.find(end_marker)

if start_idx == -1 or end_idx == -1:
    fail.append('A1/A2/A4: DesktopDashboard – boundary ikke fundet')
else:
    new_dashboard = (
'''const DesktopDashboard = ({ viewingHq, canRapport }) => {
  const [opfVersion,      setOpfVersion]      = React.useState(0);
  const [tilknytMenneske, setTilknytMenneske] = React.useState(null);

  const TODAY_S = new Date().toISOString().slice(0, 10);

  const opfPending = (window.SoS_APPOINTMENTS_BUSY || [])
    .filter(a => a.date < TODAY_S && a.brobyggerLog && !a.raadgiverOpfoelgning)
    .sort((a, b) => a.date.localeCompare(b.date));

  const afventerListe = Object.values(window.SoS_MENNESKER || {})
    .filter(m => m.status === 'afventer' || m.status === 'venter');

  const daysWaiting = m => {
    const d = m.createdAt || m.registeredAt;
    if (!d) return 0;
    return Math.floor((new Date(TODAY_S) - new Date(d)) / (1000 * 60 * 60 * 24));
  };

  const setOpfoelgning = (apptId, val, trivsel) => {
    const newList = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>
      a.id === apptId ? { ...a, raadgiverOpfoelgning: val,
        brobyggerTrivsel: trivsel || a.brobyggerTrivsel || null } : a
    );
    window.SoS_APPOINTMENTS_BUSY = newList;
    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);
    setOpfVersion(v => v + 1);
  };

  const urgentCount = opfPending.length
    + afventerListe.filter(m => daysWaiting(m) >= 3).length;
  const harDagsorden = opfPending.length > 0 || afventerListe.length > 0;

  return (
    <>
      {/* ══ DAGSORDEN ══════════════════════════════════════════════ */}
      {harDagsorden && (
        <div style={{ marginBottom: 14, border: `1px solid ${SoS.line}`,
          background: SoS.surface, overflow: 'hidden' }}>
          {/* Header */}
          <div style={{ padding: '12px 18px', borderBottom: `1px solid ${SoS.line}`,
            display: 'flex', alignItems: 'center', gap: 10,
            background: urgentCount > 0 ? SoS.ink : SoS.surface }}>
            <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 700,
              color: urgentCount > 0 ? '#fff' : SoS.inkMuted,
              letterSpacing: 1, textTransform: 'uppercase' }}>DAGSORDEN</div>
            {urgentCount > 0 && (
              <div style={{ marginLeft: 'auto', padding: '2px 9px',
                background: 'rgba(255,255,255,0.15)', borderRadius: 2,
                fontFamily: SoS.mono, fontSize: 9, fontWeight: 700,
                color: '#fff', letterSpacing: 0.5 }}>
                {urgentCount} kr\xe6ver handling
              </div>
            )}
          </div>

          {/* Opf\xf8lgninger — \xe9n r\xe6kke per aftale */}
          {opfPending.map((a, i) => {
            const m  = (window.SoS_MENNESKER || {})[a.menneskeId];
            const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === a.brobyggerId);
            const log = a.brobyggerLog || {};
            const UDFALD_LABEL = {
              gennemfoert: 'Gennemf\xf8rt', afbud: 'Afbud', 'ikke-modt': 'M\xf8dte ikke op' };
            const UDFALD_COLOR = {
              gennemfoert: SoS.green, afbud: SoS.amber, 'ikke-modt': SoS.rose };
            return (
              <div key={a.id} style={{ padding: '12px 18px',
                borderBottom: `1px solid ${SoS.lineSoft}`,
                display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 3, alignSelf: 'stretch',
                  background: SoS.rose, flexShrink: 0, borderRadius: 2 }}/>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13,
                    fontWeight: 600, color: SoS.ink }}>
                    {m ? m.firstName + ' ' + m.lastName : '—'}
                    {log.udfald && (
                      <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700,
                        color: UDFALD_COLOR[log.udfald] || SoS.inkMuted,
                        textTransform: 'uppercase', letterSpacing: 0.5, marginLeft: 8 }}>
                        {UDFALD_LABEL[log.udfald] || log.udfald}
                      </span>
                    )}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11,
                    color: SoS.inkMuted, marginTop: 2 }}>
                    {a.date}{bb ? ' \xb7 ' + bb.name.split(' ')[0] : ''}
                    {log.note ? ` \xb7 “${log.note}”` : ''}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                  {[
                    { id: 'engageret',    e: '💪', label: 'Engageret'    },
                    { id: 'neutral',      e: '😐', label: 'Neutral'      },
                    { id: 'overbelastet', e: '😔', label: 'Overbelastet' },
                  ].map(t => (
                    <button key={t.id}
                      onClick={() => setOpfoelgning(a.id, 'fulgt-op', t.id)}
                      title={`BB: ${t.label}`}
                      style={{ padding: '5px 8px', background: SoS.surface,
                        border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                        cursor: 'pointer', fontSize: 13 }}>
                      {t.e}
                    </button>
                  ))}
                  <button onClick={() => setOpfoelgning(a.id, 'fulgt-op')} style={{
                    padding: '6px 12px', background: SoS.ink, color: '#fff',
                    border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
                    fontFamily: SoS.sans, fontSize: 11, fontWeight: 700 }}>
                    Ring &amp; not\xe9r
                  </button>
                  <button onClick={() => setOpfoelgning(a.id, 'ikke-noedvendigt')} style={{
                    padding: '6px 10px', background: SoS.surfaceAlt, color: SoS.inkMuted,
                    border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                    cursor: 'pointer', fontFamily: SoS.sans, fontSize: 11 }}>
                    Ikke n\xf8dv.
                  </button>
                </div>
              </div>
            );
          })}

          {/* Afventer match */}
          {afventerListe.slice(0, 5).map((m, i) => {
            const days = daysWaiting(m);
            const col  = days >= 5 ? SoS.rose : days >= 3 ? SoS.amber : SoS.lineSoft;
            return (
              <div key={m.id} style={{ padding: '12px 18px',
                borderBottom: i < Math.min(afventerListe.length, 5) - 1
                  ? `1px solid ${SoS.lineSoft}` : 'none',
                display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 3, alignSelf: 'stretch',
                  background: col, flexShrink: 0, borderRadius: 2 }}/>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13,
                    fontWeight: 600, color: SoS.ink }}>
                    {m.firstName} {m.lastName}
                    <span style={{ fontFamily: SoS.sans, fontSize: 11,
                      fontWeight: 400, color: SoS.inkMuted, marginLeft: 6 }}>
                      {m.age} \xe5r
                    </span>
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11,
                    color: SoS.inkMuted, marginTop: 2 }}>
                    {m.hq} \xb7 Venter p\xe5 match
                    {days > 0 && (
                      <span style={{ color: days >= 3 ? SoS.amber : SoS.inkMuted }}>
                        {' '}\xb7 {days} {days === 1 ? 'dag' : 'dage'}
                      </span>
                    )}
                  </div>
                </div>
                <button onClick={() => setTilknytMenneske(m)} style={{
                  padding: '7px 14px', background: SoS.ink, color: '#fff',
                  border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                  whiteSpace: 'nowrap' }}>
                  Tilknyt
                </button>
              </div>
            );
          })}

          {afventerListe.length > 5 && (
            <div style={{ padding: '10px 18px', fontFamily: SoS.sans, fontSize: 11,
              color: SoS.inkMuted, borderTop: `1px solid ${SoS.lineSoft}` }}>
              + {afventerListe.length - 5} flere afventer match → G\xe5 til Mennesker
            </div>
          )}
        </div>
      )}

      {!harDagsorden && (
        <div style={{ marginBottom: 14, padding: '14px 18px',
          border: `1px solid ${SoS.line}`, background: SoS.surface,
          display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 8, height: 8, borderRadius: 4, background: SoS.green }}/>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
            Alt er ajour — ingen afventende handlinger ✓
          </div>
        </div>
      )}

      {tilknytMenneske && (
        <TilknytBrobyggerModal
          menneske={tilknytMenneske}
          onClose={() => setTilknytMenneske(null)}
          onSaved={() => setTilknytMenneske(null)}
        />
      )}

      {/* ══ KPI ════════════════════════════════════════════════════ */}
      <div style={{ display: 'grid',
        gridTemplateColumns: canRapport ? 'repeat(5, 1fr)' : 'repeat(4, 1fr)',
        gap: 10, marginBottom: 14 }}>
        {(() => {
          const aktive = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv').length;
          const konfirmerede = (window.SoS_APPOINTMENTS_BUSY || [])
            .filter(a => a.status === 'confirmed').length;
          const total = Object.keys(window.SoS_MENNESKER || {}).length;
          const kpis = [
            { l: 'Aktive brobyggere', v: String(aktive),
              d: aktive > 0 ? 'aktive' : '—', c: SoS.accent },
            { l: 'Afventer match', v: String(afventerListe.length),
              d: afventerListe.length > 0 ? 'ikke matchet' : 'alle matchet', c: SoS.amber },
            { l: 'Bekr\xe6ftede aftaler', v: String(konfirmerede),
              d: 'registrerede', c: SoS.green },
            { l: 'Registrerede', v: String(total), d: 'i alt', c: SoS.sky },
          ];
          if (canRapport) {
            const afsluttede = Object.values(window.SoS_MENNESKER || {})
              .filter(m => m.status === 'afsluttet');
            kpis.push({ l: 'SROI-estimat',
              v: (afsluttede.length * 47000 / 1000).toFixed(0) + 'k',
              d: 'kr. samfundsv\xe6rdi', c: SoS.sage });
          }
          return kpis;
        })().map((k, i) => (
          <DSCard key={i}>
            <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
              color: SoS.inkMuted, letterSpacing: 1,
              textTransform: 'uppercase' }}>{k.l}</div>
            <div style={{ display: 'flex', alignItems: 'baseline',
              gap: 8, marginTop: 6 }}>
              <span style={{ fontFamily: SoS.mono, fontSize: 28, fontWeight: 700,
                color: k.c || SoS.ink, letterSpacing: -1 }}>{k.v}</span>
              <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                color: SoS.sage }}>{k.d}</span>
            </div>
            <div style={{ height: 3, marginTop: 10, borderRadius: 2,
              background: SoS.lineSoft }}>
              <div style={{ width: '65%', height: '100%',
                background: k.c, borderRadius: 2 }}/>
            </div>
          </DSCard>
        ))}
      </div>

      {/* ══ GRAFER ═════════════════════════════════════════════════ */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr',
        gap: 10, marginBottom: 14 }}>
        <DSCard title="Gennemf\xf8rte aftaler" subtitle="12 m\xe5neder">
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 5, height: 140 }}>
            {(() => {
              const now = new Date();
              const months = Array.from({ length: 12 }, (_, i) => {
                const d = new Date(now.getFullYear(), now.getMonth() - 11 + i, 1);
                return { y: d.getFullYear(), m: d.getMonth() + 1,
                  lbl: ['J','F','M','A','M','J','J','A','S','O','N','D'][d.getMonth()] };
              });
              const appts = window.SoS_APPOINTMENTS_BUSY || [];
              const counts = months.map(({ y, m }) =>
                appts.filter(a => {
                  const [ay, am] = a.date.split('-').map(Number);
                  return ay === y && am === m
                    && a.brobyggerLog && a.brobyggerLog.udfald === 'gennemfoert';
                }).length
              );
              const max = Math.max(...counts, 1);
              return counts.map((v, i) => (
                <div key={i} style={{ flex: 1, display: 'flex',
                  flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                  <div style={{ flex: 1, display: 'flex',
                    alignItems: 'flex-end', width: '100%' }}>
                    <div style={{ width: '100%',
                      height: `${Math.max((v / max) * 100, 4)}%`,
                      background: i >= 9 ? SoS.accent : SoS.accent + '40',
                      borderRadius: '3px 3px 0 0' }}/>
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 9,
                    color: SoS.inkMuted }}>
                    {months[i].lbl}
                  </div>
                </div>
              ));
            })()}
          </div>
        </DSCard>

        <DSCard title="Type-fordeling" subtitle="Aktive forl\xf8b">
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            {(() => {
              const alle = Object.values(window.SoS_MENNESKER || {})
                .filter(m => m.status === 'aktiv');
              const social   = alle.filter(m => m.type === 'social').length;
              const forening = alle.filter(m => m.type === 'forening').length;
              const sundhed  = alle.filter(m => m.type === 'sundhed').length;
              return (
                <>
                  <TypeDonut sundhed={sundhed} forening={forening} social={social} size={90}/>
                  <div style={{ flex: 1 }}>
                    {[
                      { k: 'social', v: social },
                      { k: 'forening', v: forening },
                      { k: 'sundhed', v: sundhed },
                    ].map(x => {
                      const t = SoS_TYPER[x.k];
                      return (
                        <div key={x.k} style={{ display: 'flex', alignItems: 'center',
                          gap: 8, marginBottom: 8 }}>
                          <div style={{ width: 8, height: 8, borderRadius: 4,
                            background: t.color }}/>
                          <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
                            color: SoS.ink }}>{t.short}</span>
                          <span style={{ fontFamily: SoS.sans, fontSize: 12,
                            fontWeight: 600, color: SoS.ink }}>{x.v}</span>
                        </div>
                      );
                    })}
                  </div>
                </>
              );
            })()}
          </div>
        </DSCard>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr',
        gap: 10, marginBottom: 14 }}>
        <DSCard title="Per hoveds\xe6de" subtitle="Aktive forl\xf8b">
          {[
            { hq: 'Hovedstaden', v: 142 }, { hq: 'Aarhus', v: 94 },
            { hq: 'Fyn', v: 71 }, { hq: 'Sj\xe6lland', v: 58 },
            { hq: 'Midt', v: 44 }, { hq: 'Nord', v: 38 },
            { hq: 'Syd', v: 32 }, { hq: 'Kronjylland', v: 21 },
            { hq: 'Sydvest', v: 18 },
          ].map((h, i, arr) => {
            const max = arr[0].v;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center',
                gap: 10, marginBottom: i < arr.length - 1 ? 6 : 0 }}>
                <div style={{ width: 80, fontFamily: SoS.sans, fontSize: 11,
                  color: SoS.ink }}>{h.hq}</div>
                <div style={{ flex: 1, height: 6, background: SoS.lineSoft,
                  borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ width: `${(h.v / max) * 100}%`, height: '100%',
                    background: SoS.hq[h.hq] || SoS.orange, borderRadius: 3 }}/>
                </div>
                <div style={{ width: 30, textAlign: 'right', fontFamily: SoS.sans,
                  fontSize: 11, fontWeight: 600, color: SoS.ink }}>{h.v}</div>
              </div>
            );
          })}
        </DSCard>

        <DSCard title="Effekt \xb7 UCLA-3" subtitle="Selv-rapporteret ensomhed">
          <div style={{ fontFamily: SoS.mono, fontSize: 30, fontWeight: 700,
            color: SoS.ink, letterSpacing: -1 }}>
            −3.3{' '}
            <span style={{ fontSize: 14, color: SoS.inkSoft }}>point gnsn.</span>
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11,
            color: SoS.inkSoft, marginTop: 4 }}>
            Baseret p\xe5 62 besvarelser \xb7 3 mdr efter start
          </div>
          <div style={{ display: 'flex', gap: 14, marginTop: 16, alignItems: 'center' }}>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.rose }}>6.4</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 10,
                color: SoS.inkMuted }}>F\xf8r start</div>
            </div>
            <svg width="40" height="20" viewBox="0 0 40 20">
              <path d="M4 16 Q20 2 36 10" stroke={SoS.sage} strokeWidth="2"
                fill="none" strokeLinecap="round"/>
              <path d="M32 7 L36 10 L32 13" stroke={SoS.sage} strokeWidth="2"
                fill="none" strokeLinecap="round"/>
            </svg>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ fontFamily: SoS.font, fontSize: 24, color: SoS.sage }}>3.1</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 10,
                color: SoS.inkMuted }}>Efter 3 mdr</div>
            </div>
          </div>
          <div style={{ marginTop: 14, padding: 10,
            background: SoS.green + '10', borderLeft: `2px solid ${SoS.green}`,
            fontFamily: SoS.sans, fontSize: 11,
            color: SoS.green, lineHeight: 1.5 }}>
            87% rapporterer mindre ensomhed efter 3 m\xe5neder.
          </div>
        </DSCard>
      </div>

      <DSCard title="Seneste aftaler">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${SoS.line}` }}>
              {['Dato', 'Brobygger', 'Menneske', 'Type', 'Status', 'Varighed'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '8px 4px',
                  fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
                  color: SoS.inkMuted, letterSpacing: 0.8,
                  textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(() => {
              const allAppts = (window.SoS_APPOINTMENTS_BUSY || [])
                .sort((x, y) =>
                  (y.date + (y.start || '')).localeCompare(x.date + (x.start || '')))
                .slice(0, 8);
              if (allAppts.length === 0) return (
                <tr><td colSpan={6} style={{ padding: '20px 4px',
                  textAlign: 'center', fontFamily: SoS.sans,
                  fontSize: 12, color: SoS.inkMuted }}>
                  Ingen registrerede aftaler endnu
                </td></tr>
              );
              return allAppts.map((a, i) => {
                const mn  = (window.SoS_MENNESKER || {})[a.menneskeId];
                const bb  = (window.SoS_BROBYGGERE || []).find(b => b.id === a.brobyggerId);
                const mnLabel = mn
                  ? `${mn.firstName} ${mn.lastName[0]}. (${mn.age})`
                  : (a.menneskeId || '—');
                const ty  = mn ? SoS_TYPER[mn.type] : null;
                const log = a.brobyggerLog;
                const UDFALDS = {
                  gennemfoert: 'Gennemf\xf8rt', afbud: 'Afbud', 'ikke-modt': 'Udeblev' };
                const UDFALDS_C = {
                  gennemfoert: SoS.green, afbud: SoS.amber, 'ikke-modt': SoS.rose };
                const udLabel = log
                  ? (UDFALDS[log.udfald] || log.udfald)
                  : (a.status === 'confirmed' ? 'Bekr\xe6ftet' : 'Afventer');
                const udC = log ? (UDFALDS_C[log.udfald] || SoS.inkMuted) : SoS.inkMuted;
                const varLabel = log && log.varighed
                  ? `${log.varighed >= 60 ? Math.floor(log.varighed / 60) + 't' : ''} ${log.varighed % 60 ? (log.varighed % 60) + 'm' : ''}`.trim()
                  : '—';
                return (
                  <tr key={i} style={{ borderBottom: `1px solid ${SoS.lineSoft}` }}>
                    <td style={{ padding: '10px 4px', fontFamily: SoS.sans,
                      fontSize: 12, color: SoS.inkSoft }}>{a.date}</td>
                    <td style={{ padding: '10px 4px', fontFamily: SoS.sans,
                      fontSize: 12, color: SoS.inkSoft }}>
                      {bb ? bb.name.split(' ')[0] : '—'}
                    </td>
                    <td style={{ padding: '10px 4px', fontFamily: SoS.sans,
                      fontSize: 12, color: SoS.ink }}>{mnLabel}</td>
                    {ty
                      ? <td style={{ padding: '10px 4px' }}>
                          <Pill bg={ty.soft} color={ty.color}>{ty.short}</Pill>
                        </td>
                      : <td style={{ padding: '10px 4px', fontFamily: SoS.sans,
                          fontSize: 12, color: SoS.inkMuted }}>—</td>
                    }
                    <td style={{ padding: '10px 4px' }}>
                      <Pill bg={log ? (udC + '22') : SoS.creamDeep} color={udC}>
                        {udLabel}
                      </Pill>
                    </td>
                    <td style={{ padding: '10px 4px', fontFamily: SoS.sans,
                      fontSize: 12, color: SoS.inkSoft }}>{varLabel}</td>
                  </tr>
                );
              });
            })()}
          </tbody>
        </table>
      </DSCard>
    </>
  );
};

'''
    )
    c = c[:start_idx] + new_dashboard + c[end_idx:]
    ok.append('A1/A2/A4: DesktopDashboard omskrevet')

# ─── Write ───────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print('CRLF-fix: rettet')
else:
    print('CRLF-check: OK')

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

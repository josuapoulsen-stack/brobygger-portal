import sys, re

path = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()
original_len = len(html)

OLD_START = 'const DesktopKalender = () => {'
OLD_END   = '\nconst DesktopRapport = () => ('

idx_start = html.find(OLD_START)
idx_end   = html.find(OLD_END)

if idx_start < 0 or idx_end < 0:
    sys.stdout.buffer.write(b'ERROR: boundaries not found\n')
    sys.exit(1)

# New component — NO inner React components, only plain render functions called with ()
NEW = r"""const DesktopKalender = () => {
  const [weekOffset,  setWeekOffset]  = React.useState(0);
  const [bbFilter,    setBbFilter]    = React.useState('alle');
  const [view,        setView]        = React.useState('uge');
  const [selectedDay, setSelectedDay] = React.useState(null);

  const today = new Date('2026-04-26');
  const startOfWeek = new Date(today);
  const dow = today.getDay();
  startOfWeek.setDate(today.getDate() + (dow === 0 ? -6 : 1 - dow) + weekOffset * 7);

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + i);
    return d;
  });

  const mdr      = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec'];
  const DAYS     = ['Man','Tir','Ons','Tor','Fre','L\u00f8r','S\u00f8n'];
  const pad      = n => String(n).padStart(2, '0');
  const fmt      = d => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  const todayStr = '2026-04-26';

  const weekLabel = days[0].getDate() + '. ' + mdr[days[0].getMonth()]
    + ' \u2013 ' + days[6].getDate() + '. ' + mdr[days[6].getMonth()] + ' ' + days[6].getFullYear();

  const aktiveBb   = SS_BROBYGGERE.filter(b => b.status === 'aktiv' || b.status === 'ny');
  const weekDates  = new Set(days.map(fmt));
  const weekAppts  = SS_APPOINTMENTS_BUSY.filter(a => weekDates.has(a.date));
  const nConfirmed = weekAppts.filter(a => a.status === 'confirmed').length;
  const nPending   = weekAppts.filter(a => a.status === 'pending').length;

  const filtered = dateStr => SS_APPOINTMENTS_BUSY
    .filter(a => a.date === dateStr && (bbFilter === 'alle' || a.brobyggerId === bbFilter))
    .sort((a, b) => a.start.localeCompare(b.start));

  const btn = (extra) => Object.assign({
    padding: '6px 12px', borderRadius: 999, border: '1px solid ' + SS.line,
    fontFamily: SS.sans, fontSize: 12, fontWeight: 500, cursor: 'pointer',
    background: 'transparent', color: SS.inkSoft,
  }, extra);

  // Plain render function — NOT a React component
  const apptRow = (a) => {
    const m  = SS_MENNESKER[a.menneskeId];
    const bb = SS_BROBYGGERE.find(b => b.id === a.brobyggerId);
    const ok = a.status === 'confirmed';
    return (
      <div key={a.id} style={{
        background: '#fff', borderRadius: 10, marginBottom: 8,
        border: '1px solid ' + SS.lineSoft, padding: '12px 14px',
        borderLeft: '4px solid ' + (ok ? SS.sage : SS.sun),
        display: 'grid', gridTemplateColumns: 'auto 1fr auto', gap: 12, alignItems: 'center',
      }}>
        <div style={{ textAlign: 'center', minWidth: 38 }}>
          <div style={{ fontFamily: SS.sans, fontSize: 15, fontWeight: 700, color: SS.ink }}>{a.start}</div>
          <div style={{ fontFamily: SS.sans, fontSize: 10, color: SS.inkMuted }}>{a.end}</div>
        </div>
        <div>
          <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600, color: SS.ink }}>{a.activity}</div>
          <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, marginTop: 2 }}>
            {m ? m.firstName + ' ' + m.lastName : '\u2014'}
          </div>
          <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted, marginTop: 1 }}>{a.location}</div>
        </div>
        {bb && (
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: 30, height: 30, borderRadius: 15, background: bb.bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 3px', fontFamily: SS.sans, fontSize: 11, fontWeight: 700, color: '#fff',
            }}>{bb.avatar}</div>
            <div style={{ fontFamily: SS.sans, fontSize: 9, color: SS.inkMuted }}>{bb.name.split(' ')[0]}</div>
          </div>
        )}
      </div>
    );
  };

  const MAX = 3;

  return (
    <>
      {/* Nav + view toggle */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14,
        background: '#fff', borderRadius: 12, padding: '12px 16px',
        border: '1px solid ' + SS.lineSoft,
      }}>
        <button style={btn({})} onClick={() => setWeekOffset(w => w - 1)}>\u2190</button>
        <div style={{ flex: 1, textAlign: 'center', fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink }}>
          {weekLabel}
        </div>
        <button style={btn(weekOffset === 0 ? { background: SS.orange, color: '#fff', borderColor: SS.orange } : {})}
          onClick={() => setWeekOffset(0)}>I dag</button>
        <button style={btn({})} onClick={() => setWeekOffset(w => w + 1)}>\u2192</button>
        <div style={{ display: 'flex', background: SS.creamDeep, borderRadius: 8, padding: 3, gap: 2 }}>
          {[['uge','Uge'],['dag','Dag'],['liste','Liste']].map(function(pair) {
            var k = pair[0], l = pair[1];
            return (
              <button key={k} onClick={() => setView(k)} style={{
                padding: '5px 10px', borderRadius: 6, border: 'none', cursor: 'pointer',
                fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                background: view === k ? '#fff' : 'transparent',
                color: view === k ? SS.ink : SS.inkMuted,
                boxShadow: view === k ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              }}>{l}</button>
            );
          })}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginBottom: 14 }}>
        {[
          { l: 'Aftaler denne uge', v: weekAppts.length, c: SS.ink  },
          { l: 'Bekr\u00e6ftede',       v: nConfirmed,        c: SS.sage },
          { l: 'Afventer',           v: nPending,          c: SS.sun  },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', borderRadius: 10, border: '1px solid ' + SS.lineSoft, padding: '12px 14px' }}>
            <div style={{ fontFamily: SS.sans, fontSize: 10, fontWeight: 700, color: SS.inkMuted,
              letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 4 }}>{s.l}</div>
            <div style={{ fontFamily: SS.font, fontSize: 28, fontWeight: 500, color: s.c }}>{s.v}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
        <button style={btn(bbFilter === 'alle' ? { background: SS.ink, color: '#fff', borderColor: SS.ink } : {})}
          onClick={() => setBbFilter('alle')}>Alle</button>
        {aktiveBb.map(b => (
          <button key={b.id} style={btn(bbFilter === b.id ? { background: b.bg, color: '#fff', borderColor: b.bg } : {})}
            onClick={() => setBbFilter(b.id)}>{b.name.split(' ')[0]}</button>
        ))}
      </div>

      {/* UGE VIEW */}
      {view === 'uge' && (
        <div style={{ background: '#fff', borderRadius: 12, border: '1px solid ' + SS.lineSoft, overflow: 'hidden' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', borderBottom: '1px solid ' + SS.lineSoft }}>
            {days.map((day, i) => {
              var ds = fmt(day);
              var isToday = ds === todayStr;
              var cnt = filtered(ds).length;
              return (
                <button key={i} onClick={() => { setSelectedDay(ds); setView('dag'); }} style={{
                  padding: '10px 8px', textAlign: 'center', border: 'none', cursor: 'pointer', width: '100%',
                  borderRight: i < 6 ? '1px solid ' + SS.lineSoft : 'none',
                  background: isToday ? SS.orange + '18' : 'transparent',
                }}>
                  <div style={{ fontFamily: SS.sans, fontSize: 10, fontWeight: 700,
                    color: SS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>{DAYS[i]}</div>
                  <div style={{
                    width: 28, height: 28, borderRadius: 14,
                    background: isToday ? SS.orange : 'transparent',
                    color: isToday ? '#fff' : SS.ink,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    margin: '4px auto 2px', fontFamily: SS.sans, fontSize: 14, fontWeight: 600,
                  }}>{day.getDate()}</div>
                  {cnt > 0 && (
                    <div style={{ fontFamily: SS.sans, fontSize: 9, color: isToday ? SS.orange : SS.inkMuted }}>
                      {cnt} afd.
                    </div>
                  )}
                </button>
              );
            })}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', minHeight: 240, alignItems: 'start' }}>
            {days.map((day, i) => {
              var ds  = fmt(day);
              var all = filtered(ds);
              var vis = all.slice(0, MAX);
              var ov  = all.length - MAX;
              var isToday = ds === todayStr;
              return (
                <div key={i} style={{
                  padding: '8px 6px', minHeight: 120,
                  borderRight: i < 6 ? '1px solid ' + SS.lineSoft : 'none',
                  background: isToday ? SS.orange + '06' : 'transparent',
                }}>
                  {all.length === 0 && (
                    <div style={{ textAlign: 'center', paddingTop: 20,
                      fontFamily: SS.sans, fontSize: 12, color: SS.lineSoft }}>\u2014</div>
                  )}
                  {vis.map(a => {
                    var m  = SS_MENNESKER[a.menneskeId];
                    var bb = SS_BROBYGGERE.find(function(b) { return b.id === a.brobyggerId; });
                    var ok = a.status === 'confirmed';
                    return (
                      <div key={a.id} style={{
                        background: ok ? SS.sageSoft : SS.sun + '33',
                        borderLeft: '3px solid ' + (ok ? SS.sage : SS.sun),
                        borderRadius: '0 6px 6px 0', padding: '5px 7px', marginBottom: 4,
                      }}>
                        <div style={{ fontFamily: SS.sans, fontSize: 10, fontWeight: 700, color: SS.inkSoft }}>{a.start}</div>
                        <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600, color: SS.ink, lineHeight: 1.2 }}>
                          {m ? m.firstName : '\u2014'}
                        </div>
                        <div style={{ fontFamily: SS.sans, fontSize: 10, color: SS.inkSoft, lineHeight: 1.2 }}>{a.activity}</div>
                        {bb && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 3 }}>
                            <div style={{
                              width: 14, height: 14, borderRadius: 7, background: bb.bg, flexShrink: 0,
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontFamily: SS.sans, fontSize: 7, fontWeight: 700, color: '#fff',
                            }}>{bb.avatar[0]}</div>
                            <div style={{ fontFamily: SS.sans, fontSize: 9, color: SS.inkMuted }}>
                              {bb.name.split(' ')[0]}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  {ov > 0 && (
                    <button onClick={() => { setSelectedDay(ds); setView('dag'); }} style={{
                      width: '100%', padding: '5px 4px', borderRadius: 6, border: 'none',
                      background: SS.orange + '18', cursor: 'pointer',
                      fontFamily: SS.sans, fontSize: 11, fontWeight: 700, color: SS.orangeDeep,
                    }}>+{ov} mere \u2192</button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* DAG VIEW */}
      {view === 'dag' && (
        <>
          <div style={{
            display: 'flex', gap: 4, marginBottom: 14, background: '#fff',
            borderRadius: 12, padding: 8, border: '1px solid ' + SS.lineSoft, overflowX: 'auto',
          }}>
            {days.map((d, i) => {
              var ds  = fmt(d);
              var sel = ds === (selectedDay || todayStr);
              var cnt = filtered(ds).length;
              var ist = ds === todayStr;
              return (
                <button key={i} onClick={() => setSelectedDay(ds)} style={{
                  flex: '0 0 auto', padding: '8px 14px', borderRadius: 8, border: 'none',
                  background: sel ? SS.orange : 'transparent', cursor: 'pointer', textAlign: 'center',
                }}>
                  <div style={{ fontFamily: SS.sans, fontSize: 10, fontWeight: 700,
                    color: sel ? '#fff' : SS.inkMuted }}>{DAYS[i]}</div>
                  <div style={{ fontFamily: SS.sans, fontSize: 16, fontWeight: 700, marginTop: 2,
                    color: sel ? '#fff' : (ist ? SS.orange : SS.ink) }}>{d.getDate()}</div>
                  {cnt > 0 && (
                    <div style={{ fontFamily: SS.sans, fontSize: 10, marginTop: 2,
                      color: sel ? 'rgba(255,255,255,0.75)' : SS.inkMuted }}>{cnt} afd.</div>
                  )}
                </button>
              );
            })}
          </div>
          {(function() {
            var ds    = selectedDay || todayStr;
            var apts  = filtered(ds);
            if (!apts.length) return (
              <div style={{ textAlign: 'center', padding: '40px 0',
                fontFamily: SS.sans, fontSize: 14, color: SS.inkMuted }}>Ingen aftaler denne dag</div>
            );
            return <>{apts.map(apptRow)}</>;
          })()}
        </>
      )}

      {/* LISTE VIEW */}
      {view === 'liste' && (function() {
        var groups = days
          .map(d => ({ d: d, ds: fmt(d), apts: filtered(fmt(d)) }))
          .filter(g => g.apts.length > 0);
        if (!groups.length) return (
          <div style={{ textAlign: 'center', padding: '40px 0',
            fontFamily: SS.sans, fontSize: 14, color: SS.inkMuted }}>Ingen aftaler denne uge</div>
        );
        return (
          <>
            {groups.map(function(g) {
              var isToday = g.ds === todayStr;
              var di = days.findIndex(x => fmt(x) === g.ds);
              return (
                <div key={g.ds} style={{ marginBottom: 18 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <div style={{
                      width: 38, height: 38, borderRadius: 19, flexShrink: 0,
                      background: isToday ? SS.orange : SS.creamDeep,
                      display: 'flex', flexDirection: 'column',
                      alignItems: 'center', justifyContent: 'center',
                    }}>
                      <span style={{ fontFamily: SS.sans, fontSize: 8, fontWeight: 700,
                        color: isToday ? 'rgba(255,255,255,0.8)' : SS.inkMuted,
                        textTransform: 'uppercase' }}>{DAYS[di]}</span>
                      <span style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 700,
                        lineHeight: 1, color: isToday ? '#fff' : SS.ink }}>{g.d.getDate()}</span>
                    </div>
                    <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600, color: SS.ink }}>
                      {g.apts.length} {g.apts.length === 1 ? 'aftale' : 'aftaler'}
                    </div>
                  </div>
                  {g.apts.map(apptRow)}
                </div>
              );
            })}
          </>
        );
      })()}
    </>
  );
};
"""

html = html[:idx_start] + NEW + html[idx_end:]

# Verify div balance
chunk = html[html.find('const DesktopKalender'):html.find('\nconst DesktopRapport')]
opens  = len(re.findall(r'<div[\s{>]', chunk))
closes = len(re.findall(r'</div>', chunk))
selfc  = len(re.findall(r'<div[^>]*/>', chunk))
ok = (opens - selfc) == closes

sys.stdout.buffer.write(
    f"Div balance: opens={opens} self={selfc} effective={opens-selfc} closes={closes} {'OK' if ok else 'MISMATCH'}\n"
    f"File: {original_len:,} -> {len(html):,} bytes\n".encode('utf-8')
)

if ok:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    sys.stdout.buffer.write(b"Saved.\n")
else:
    sys.stdout.buffer.write(b"NOT saved.\n")

path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

# ── 1. Add thisWeek field to SS_BROBYGGERE ────────────────────────────────────
old_bb = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1 },
  { id: 'bb-2', name: 'Søren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3 },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2 },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0 },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0 },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4 },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2 },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1 },
];"""

new_bb = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1, thisWeek: 2 },
  { id: 'bb-2', name: 'Søren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3, thisWeek: 0 },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2, thisWeek: 1 },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0, thisWeek: 0 },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0, thisWeek: 3 },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4, thisWeek: 0 },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2, thisWeek: 1 },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2 },
];"""

if old_bb in html:
    html = html.replace(old_bb, new_bb, 1)
    print("Patched SS_BROBYGGERE with thisWeek")
else:
    print("ERROR: SS_BROBYGGERE not found")

# ── 2. Inject "Brobygninger i denne uge" section before "Aftaler i dag" ──────
old_section = """            {/* I dag */}
            <div style={{ padding: '16px 20px 8px' }}>
              <SectionHead title="Aftaler i dag"/>
            </div>"""

new_section = """            {/* Brobygninger i denne uge */}
            {(() => {
              const ugeData = SS_BROBYGGERE.filter(b => b.status !== 'pause');
              const totalUge = ugeData.reduce((s, b) => s + b.thisWeek, 0);
              const max = Math.max(...ugeData.map(b => b.thisWeek), 1);
              return (
                <div style={{ padding: '16px 20px 8px' }}>
                  <SectionHead title="Brobygninger denne uge"/>
                  <div style={{
                    background: '#fff', borderRadius: SS.r.lg,
                    border: `1px solid ${SS.lineSoft}`, overflow: 'hidden',
                  }}>
                    {/* Total pill row */}
                    <div style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '14px 16px 10px',
                      borderBottom: `1px solid ${SS.lineSoft}`,
                    }}>
                      <div>
                        <span style={{ fontFamily: SS.font, fontSize: 34, fontWeight: 500,
                          color: SS.ink, lineHeight: 1 }}>{totalUge}</span>
                        <span style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
                          marginLeft: 8 }}>brobygninger</span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted,
                          letterSpacing: 0.3, textTransform: 'uppercase', fontWeight: 600 }}>
                          Uge 17
                        </div>
                        <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.sage,
                          marginTop: 2 }}>↑ 3 fra sidste uge</div>
                      </div>
                    </div>
                    {/* Per-brobygger mini bars */}
                    <div style={{ padding: '10px 16px 12px' }}>
                      {ugeData
                        .filter(b => b.thisWeek > 0 || b.status === 'aktiv')
                        .sort((a, b) => b.thisWeek - a.thisWeek)
                        .map(b => (
                          <div key={b.id} style={{
                            display: 'flex', alignItems: 'center', gap: 10,
                            marginBottom: 7,
                          }}>
                            <div style={{
                              width: 26, height: 26, borderRadius: 13,
                              background: b.bg, display: 'flex',
                              alignItems: 'center', justifyContent: 'center',
                              flexShrink: 0,
                            }}>
                              <span style={{ fontFamily: SS.sans, fontSize: 9,
                                fontWeight: 700, color: '#fff' }}>{b.avatar}</span>
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between',
                                marginBottom: 3 }}>
                                <span style={{ fontFamily: SS.sans, fontSize: 11,
                                  color: SS.ink, fontWeight: 500,
                                  overflow: 'hidden', textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap' }}>
                                  {b.name.split(' ')[0]}
                                </span>
                                <span style={{ fontFamily: SS.sans, fontSize: 11,
                                  color: b.thisWeek > 0 ? SS.ink : SS.inkMuted,
                                  fontWeight: b.thisWeek > 0 ? 600 : 400,
                                  flexShrink: 0, marginLeft: 6 }}>
                                  {b.thisWeek}
                                </span>
                              </div>
                              <div style={{ height: 4, background: SS.lineSoft,
                                borderRadius: 2, overflow: 'hidden' }}>
                                <div style={{
                                  width: `${(b.thisWeek / max) * 100}%`,
                                  height: '100%', borderRadius: 2,
                                  background: b.thisWeek >= 3 ? SS.sage
                                            : b.thisWeek >= 1 ? SS.orange
                                            : SS.lineSoft,
                                  transition: 'width 0.4s ease',
                                }}/>
                              </div>
                            </div>
                          </div>
                        ))
                      }
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* I dag */}
            <div style={{ padding: '8px 20px 8px' }}>
              <SectionHead title="Aftaler i dag"/>
            </div>"""

if old_section in html:
    html = html.replace(old_section, new_section, 1)
    print("Injected 'Brobygninger denne uge' section")
else:
    print("ERROR: 'Aftaler i dag' section not found")
    # Debug: try to find partial match
    partial = "SectionHead title=\"Aftaler i dag\""
    idx = html.find(partial)
    print(f"  Partial match at: {idx}")
    if idx >= 0:
        print(repr(html[idx-200:idx+100]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDone. File: {len(html):,} bytes")

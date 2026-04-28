path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

# ── 1. Patch SS_BROBYGGERE mock data — add thisMonth + openShifts ────────────
old_brobyggere = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv' },
  { id: 'bb-2', name: 'S\u00f8ren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv' },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv' },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause' },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv' },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny' },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv' },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv' },
];"""

new_brobyggere = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1 },
  { id: 'bb-2', name: 'S\u00f8ren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3 },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2 },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0 },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0 },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4 },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2 },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1 },
];"""

if old_brobyggere in html:
    html = html.replace(old_brobyggere, new_brobyggere, 1)
    print("Patched SS_BROBYGGERE with thisMonth + openShifts")
else:
    print("ERROR: SS_BROBYGGERE block not found")

# ── 2. Replace MatchingFlow step 1 (brobygger selection) ─────────────────────
old_step1 = """{step === 1 && menneske && (
          <>
            <div style={{ fontFamily: SS.font, fontSize: 24, fontWeight: 500,
              color: SS.ink, marginBottom: 6, letterSpacing: -0.2 }}>Foresl\u00e5ede brobyggere</div>
            <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft, marginBottom: 16 }}>
              Sorteret efter match-score for {menneske.firstName}.
            </div>
            {SS_BROBYGGERE.slice(0, 5).map((b, i) => {
              const sel = brobyggerId === b.id;
              const score = [94, 87, 78, 64, 52][i];
              return (
                <button key={b.id} onClick={() => setBrobyggerId(b.id)} style={{
                  display: 'flex', gap: 12, alignItems: 'center', width: '100%',
                  padding: 14, marginBottom: 8, textAlign: 'left',
                  background: sel ? SS.orange + '15' : '#fff',
                  border: `2px solid ${sel ? SS.orange : SS.lineSoft}`,
                  borderRadius: SS.r.md, cursor: 'pointer',
                }}>
                  <Avatar initials={b.avatar} bg={b.bg} size={44}/>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink }}>
                      {b.name}
                    </div>
                    <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, marginTop: 2 }}>
                      {b.active} aktive \u00b7 {b.status}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
                      color: score > 80 ? SS.sage : score > 60 ? SS.sun : SS.inkSoft, lineHeight: 1 }}>
                      {score}
                    </div>
                    <div style={{ fontFamily: SS.sans, fontSize: 10, color: SS.inkMuted, marginTop: 2 }}>
                      match
                    </div>
                  </div>
                </button>
              );
            })}
          </>
        )}"""

new_step1 = """{step === 1 && menneske && (() => {
          // Sort available brobyggere by fewest brobygninger this month (ascending)
          const available = SS_BROBYGGERE
            .filter(b => b.status === 'aktiv' || b.status === 'ny')
            .slice()
            .sort((a, b) => a.thisMonth - b.thisMonth);
          return (
            <>
              <div style={{ fontFamily: SS.font, fontSize: 24, fontWeight: 500,
                color: SS.ink, marginBottom: 4, letterSpacing: -0.2 }}>
                V\u00e6lg brobygger
              </div>
              <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft, marginBottom: 16, lineHeight: 1.5 }}>
                Sorteret efter mindst aktivitet denne m\u00e5ned \u2014 de med mest kapacitet \u00f8verst.
              </div>
              {available.map((b) => {
                const sel = brobyggerId === b.id;
                const loadColor = b.thisMonth <= 1 ? SS.sage : b.thisMonth <= 4 ? SS.sun : SS.rose;
                const loadLabel = b.thisMonth === 0 ? 'Ingen denne m\u00e5ned' : `${b.thisMonth} denne m\u00e5ned`;
                const isNew = b.status === 'ny';
                return (
                  <button key={b.id} onClick={() => setBrobyggerId(b.id)} style={{
                    display: 'flex', gap: 12, alignItems: 'center', width: '100%',
                    padding: 14, marginBottom: 8, textAlign: 'left',
                    background: sel ? '#fff' : '#fff',
                    border: `2px solid ${sel ? SS.orange : SS.lineSoft}`,
                    borderRadius: SS.r.md, cursor: 'pointer',
                    boxShadow: sel ? SS.shadow.md : 'none',
                  }}>
                    <Avatar initials={b.avatar} bg={b.bg} size={44}/>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <span style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink }}>
                          {b.name}
                        </span>
                        {isNew && (
                          <span style={{ fontFamily: SS.sans, fontSize: 10, fontWeight: 700,
                            color: SS.sky, background: SS.skySoft,
                            padding: '2px 7px', borderRadius: 999, letterSpacing: 0.3 }}>
                            Ny
                          </span>
                        )}
                      </div>
                      {/* Load bar */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ flex: 1, height: 4, background: SS.lineSoft, borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{
                            width: `${Math.min(100, (b.thisMonth / 8) * 100)}%`,
                            height: '100%', borderRadius: 2,
                            background: loadColor, transition: 'width 0.3s',
                          }}/>
                        </div>
                        <span style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft,
                          whiteSpace: 'nowrap' }}>
                          {loadLabel}
                        </span>
                      </div>
                      <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted, marginTop: 3 }}>
                        {b.active} aktive forl\u00f8b
                        {b.openShifts > 0 && <span style={{ color: SS.sage }}> \u00b7 {b.openShifts} ledige vagter</span>}
                        {b.openShifts === 0 && <span style={{ color: SS.inkMuted }}> \u00b7 ingen \u00e5bne vagter</span>}
                      </div>
                    </div>
                    {sel && (
                      <div style={{ width: 24, height: 24, borderRadius: 12,
                        background: SS.orange, display: 'flex',
                        alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <Icon name="check" size={14} color="#fff" weight={2.5}/>
                      </div>
                    )}
                  </button>
                );
              })}
            </>
          );
        })()}"""

if old_step1 in html:
    html = html.replace(old_step1, new_step1, 1)
    print("Replaced MatchingFlow step 1 brobygger list")
else:
    print("ERROR: step 1 block not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDone. File: {len(html):,} bytes")

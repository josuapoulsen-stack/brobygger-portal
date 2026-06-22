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

# 1) monthOffset-state
sub(
    "  const [weekOffset,   setWeekOffset]   = React.useState(0);",
    "  const [weekOffset,   setWeekOffset]   = React.useState(0);\n  const [monthOffset,  setMonthOffset]  = React.useState(0);",
    "1: monthOffset state")

# 2) days-længde visnings-bevidst (14 ved 14dage)
sub(
    "  const days = Array.from({ length: 7 }, (_, i) => {",
    "  const days = Array.from({ length: view === '14dage' ? 14 : 7 }, (_, i) => {",
    "2: days-længde")

# 3) weekLabel visnings-bevidst
sub(
    "  const weekLabel = (() => {\n"
    "    const m1 = days[0], m2 = days[6];\n"
    "    const s = `${m1.getDate()}. ${MDR[m1.getMonth()]}`;\n"
    "    const e = `${m2.getDate()}. ${MDR[m2.getMonth()]} ${m2.getFullYear()}`;\n"
    "    const d = new Date(Date.UTC(m1.getFullYear(), m1.getMonth(), m1.getDate()));\n"
    "    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));\n"
    "    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));\n"
    "    const wn = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);\n"
    "    return `Uge ${wn}  ·  ${s} – ${e}`;\n"
    "  })();",
    "  const MDR_LANG = ['Januar','Februar','Marts','April','Maj','Juni','Juli','August','September','Oktober','November','December'];\n"
    "  const weekLabel = (() => {\n"
    "    if (view === 'maaned') {\n"
    "      const rm = new Date(baseDate.getFullYear(), baseDate.getMonth() + monthOffset, 1);\n"
    "      return MDR_LANG[rm.getMonth()] + ' ' + rm.getFullYear();\n"
    "    }\n"
    "    const m1 = days[0], m2 = days[days.length - 1];\n"
    "    const s = `${m1.getDate()}. ${MDR[m1.getMonth()]}`;\n"
    "    const e = `${m2.getDate()}. ${MDR[m2.getMonth()]} ${m2.getFullYear()}`;\n"
    "    if (view === '14dage') return `${s} – ${e}`;\n"
    "    const d = new Date(Date.UTC(m1.getFullYear(), m1.getMonth(), m1.getDate()));\n"
    "    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));\n"
    "    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));\n"
    "    const wn = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);\n"
    "    return `Uge ${wn}  ·  ${s} – ${e}`;\n"
    "  })();",
    "3: weekLabel visnings-bevidst")

# 4) Nav prev/next/I dag visnings-bevidst
sub(
    "        <button style={B()} onClick={() => setWeekOffset(n => n - 1)}>&#8592;</button>",
    "        <button style={B()} onClick={() => view === 'maaned' ? setMonthOffset(n => n - 1) : setWeekOffset(n => n - (view === '14dage' ? 2 : 1))}>&#8592;</button>",
    "4a: prev")
sub(
    "        <button style={B()} onClick={() => setWeekOffset(n => n + 1)}>&#8594;</button>",
    "        <button style={B()} onClick={() => view === 'maaned' ? setMonthOffset(n => n + 1) : setWeekOffset(n => n + (view === '14dage' ? 2 : 1))}>&#8594;</button>",
    "4b: next")
sub(
    "        <button style={B(weekOffset === 0 ? { background: SoS.ink, color: '#fff', borderColor: SoS.ink } : {})}\n"
    "          onClick={() => setWeekOffset(0)}>I dag</button>",
    "        <button style={B(weekOffset === 0 && monthOffset === 0 ? { background: SoS.ink, color: '#fff', borderColor: SoS.ink } : {})}\n"
    "          onClick={() => { setWeekOffset(0); setMonthOffset(0); }}>I dag</button>",
    "4c: I dag")

# 5) View-knapper: tilføj 14 dage + Måned
sub(
    "            { k: 'uge',      l: 'Uge'      },\n"
    "            { k: 'dag',      l: 'Dag'      },",
    "            { k: 'uge',      l: 'Uge'      },\n"
    "            { k: '14dage',   l: '14 dage'  },\n"
    "            { k: 'maaned',   l: 'Måned'    },\n"
    "            { k: 'dag',      l: 'Dag'      },",
    "5: view-knapper")

# 6) Ugevisning gælder også 14dage
sub("      {view === 'uge' && (", "      {(view === 'uge' || view === '14dage') && (", "6: uge||14dage")

# 7) Månedsvisning (indsættes før selectedAppt-modal)
MAANED = r'''      {view === 'maaned' && (() => {
        const rm = new Date(baseDate.getFullYear(), baseDate.getMonth() + monthOffset, 1);
        const y = rm.getFullYear(), mo = rm.getMonth();
        const startWd = (new Date(y, mo, 1).getDay() + 6) % 7;
        const dim = new Date(y, mo + 1, 0).getDate();
        const cells = [];
        for (let i = 0; i < startWd; i++) cells.push(null);
        for (let dd = 1; dd <= dim; dd++) cells.push(new Date(y, mo, dd));
        while (cells.length % 7 !== 0) cells.push(null);
        return (
          <div style={{ background: SoS.surface, border: `1px solid ${SoS.line}` }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', borderBottom: `1px solid ${SoS.line}` }}>
              {DNAMES.map((dn, i) => (
                <div key={i} style={{ padding: '8px 6px', textAlign: 'center', fontFamily: SoS.mono,
                  fontSize: 9.5, fontWeight: 600, color: SoS.inkMuted, textTransform: 'uppercase',
                  letterSpacing: 0.5, borderRight: i < 6 ? `1px solid ${SoS.line}` : 'none' }}>{dn}</div>
              ))}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,1fr)' }}>
              {cells.map((cell, i) => {
                if (!cell) return <div key={i} style={{ minHeight: 86,
                  borderRight: (i % 7) < 6 ? `1px solid ${SoS.line}` : 'none',
                  borderTop: `1px solid ${SoS.line}`, background: SoS.surfaceAlt }}/>;
                const ds = fmt(cell), dayA = getAppts(ds), isT = ds === TODAY;
                return (
                  <button key={i} onClick={() => { setSelectedDay(ds); setView('dag'); }} style={{
                    minHeight: 86, textAlign: 'left', border: 'none', cursor: 'pointer', width: '100%',
                    borderRight: (i % 7) < 6 ? `1px solid ${SoS.line}` : 'none',
                    borderTop: `1px solid ${SoS.line}`, padding: '6px 8px',
                    background: isT ? SoS.accent + '08' : 'transparent' }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,
                      color: isT ? SoS.accent : SoS.ink }}>{cell.getDate()}</div>
                    {dayA.length > 0 && (
                      <>
                        <div style={{ display: 'flex', gap: 2, flexWrap: 'wrap', marginTop: 4 }}>
                          {dayA.slice(0, 8).map(a => (
                            <span key={a.id} style={{ width: 6, height: 6, borderRadius: 3,
                              background: a.status === 'confirmed' ? SoS.green : SoS.amber }}/>
                          ))}
                        </div>
                        <div style={{ fontFamily: SoS.mono, fontSize: 9, color: SoS.inkMuted, marginTop: 3 }}>
                          {dayA.length} afd.
                        </div>
                      </>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })()}

      {selectedAppt && (
        <StaffApptDetail appt={selectedAppt}'''

sub(
    "      {selectedAppt && (\n        <StaffApptDetail appt={selectedAppt}",
    MAANED,
    "7: månedsvisning")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

with open(P, 'rb') as f:
    b = f.read()
needle = b".join('" + bytes([0x0a]) + b"');"
if needle in b:
    b = b.replace(needle, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(P, 'wb') as f:
        f.write(b)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f"\nOK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"\nFAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

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

# A) downloadAktivitet-funktion (SVG -> PNG, ingen eksterne libs)
sub(
    "  const handleDownload = (name) => { setDownloading(name); setTimeout(() => setDownloading(null), 2000); };",
    "  const handleDownload = (name) => { setDownloading(name); setTimeout(() => setDownloading(null), 2000); };\n"
    "  const downloadAktivitet = () => {\n"
    "    const svg = document.getElementById('sos-akt-svg'); if (!svg) return;\n"
    "    const xml = new XMLSerializer().serializeToString(svg);\n"
    "    const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml)));\n"
    "    const img = new Image();\n"
    "    img.onload = () => {\n"
    "      const cv = document.createElement('canvas'); cv.width = 1440; cv.height = 920;\n"
    "      const ctx = cv.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0,0,1440,920);\n"
    "      ctx.drawImage(img, 0, 0, 1440, 920);\n"
    "      const a = document.createElement('a'); a.download = 'aktivitetsoverblik-' + new Date().getFullYear() + '.png';\n"
    "      a.href = cv.toDataURL('image/png'); a.click();\n"
    "    };\n"
    "    img.src = url;\n"
    "  };",
    "A: downloadAktivitet")

# B) Tilføj fane
sub(
    "    { id: 'statistik',    label: 'Statistik' },\n"
    "    { id: 'definitioner', label: 'Definitioner' },",
    "    { id: 'statistik',    label: 'Statistik' },\n"
    "    { id: 'aktivitet',    label: 'Aktivitetsoverblik' },\n"
    "    { id: 'definitioner', label: 'Definitioner' },",
    "B: fane")

# C) Aktivitetsoverblik-blok (før definitioner)
BLOK = """    {rapTab === 'aktivitet' && (() => {
      const A = window.SoS_APPOINTMENTS_BUSY || [];
      const MN = window.SoS_MENNESKER || {};
      const pad = n => String(n).padStart(2, '0');
      const year = new Date().getFullYear();
      const dayCount = {};
      A.forEach(a => { if (a.date && Number(a.date.slice(0,4)) === year) dayCount[a.date] = (dayCount[a.date]||0)+1; });
      const total = A.length;
      const done = A.filter(a => a.status === 'gennemfoert' || (a.brobyggerLog && a.brobyggerLog.udfald === 'gennemfoert')).length;
      const cancelled = A.filter(a => ['aflyst','afslaaet','brudt'].indexOf(a.status) >= 0 || (a.brobyggerLog && a.brobyggerLog.udfald === 'afbud')).length;
      const typeC = { social: 0, forening: 0, sundhed: 0 };
      A.forEach(a => { const m = MN[a.menneskeId]; if (m && typeC[m.type] != null) typeC[m.type]++; });
      const start = new Date(year, 0, 1);
      const firstWd = (start.getDay()+6)%7;
      const counts = Object.values(dayCount);
      const maxc = Math.max(1, ...(counts.length ? counts : [1]));
      const cells = [];
      for (let i = 0; i < 365; i++) {
        const dt = new Date(year, 0, 1 + i);
        const ds = year + '-' + pad(dt.getMonth()+1) + '-' + pad(dt.getDate());
        const cnt = dayCount[ds] || 0;
        const col = Math.floor((i + firstWd) / 7), row = (dt.getDay()+6)%7;
        const lvl = cnt === 0 ? 0 : Math.min(4, Math.ceil(cnt / maxc * 4));
        cells.push({ col, row, lvl, isFirst: dt.getDate() === 1, mo: dt.getMonth() });
      }
      const HCOL = ['#F1EAE0','#F6DDB0','#EFB45F','#E0892E','#C95B16'];
      const MND = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec'];
      const x0 = 56, y0 = 120, cs = 12;
      const maxType = Math.max(1, typeC.social, typeC.forening, typeC.sundhed);
      const typeRows = [['social', typeC.social], ['forening', typeC.forening], ['sundhed', typeC.sundhed]];
      const legY = y0 + 7*cs + 13;
      return (
        <div>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12, flexWrap:'wrap', gap:8 }}>
            <div style={{ fontFamily:SoS.sans, fontSize:13, color:SoS.inkSoft }}>Organisationens aktivitet i {year} — til download/print for ledelse og fonde.</div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={downloadAktivitet} style={{ padding:'7px 14px', background:SoS.ink, color:'#fff', border:'none', borderRadius:SoS.r.sm, cursor:'pointer', fontFamily:SoS.sans, fontSize:12, fontWeight:600 }}>Download PNG</button>
              <button onClick={() => window.print()} style={{ padding:'7px 14px', background:SoS.surface, color:SoS.ink, border:`1px solid ${SoS.line}`, borderRadius:SoS.r.sm, cursor:'pointer', fontFamily:SoS.sans, fontSize:12, fontWeight:600 }}>Print</button>
            </div>
          </div>
          <DSCard style={{ padding:0, overflow:'hidden' }}>
            <svg id="sos-akt-svg" viewBox="0 0 720 440" style={{ width:'100%', display:'block', background:'#fff' }} xmlns="http://www.w3.org/2000/svg">
              <text x="24" y="34" style={{ fontFamily:SoS.sans, fontSize:18, fontWeight:700, fill:SoS.ink }}>Aktivitetsoverblik · {year}</text>
              {[['Aftaler i alt', total], ['Gennemførte', done], ['Aflyste', cancelled], ['Mennesker', Object.keys(MN).length]].map((k, i) => (
                <g key={i}>
                  <text x={24 + i*172} y="64" style={{ fontFamily:SoS.sans, fontSize:11, fill:SoS.inkMuted }}>{k[0]}</text>
                  <text x={24 + i*172} y="90" style={{ fontFamily:SoS.sans, fontSize:22, fontWeight:700, fill:SoS.ink }}>{k[1]}</text>
                </g>
              ))}
              {cells.filter(c => c.isFirst).map(c => (
                <text key={c.mo} x={x0 + c.col*cs} y="112" style={{ fontFamily:SoS.mono, fontSize:9, fill:SoS.inkMuted }}>{MND[c.mo]}</text>
              ))}
              {cells.map((c, i) => (
                <rect key={i} x={x0 + c.col*cs} y={y0 + c.row*cs} width="10" height="10" rx="2" fill={HCOL[c.lvl]}/>
              ))}
              <text x="24" y={legY + 9} style={{ fontFamily:SoS.sans, fontSize:10, fill:SoS.inkMuted }}>Mindre</text>
              {HCOL.map((col, i) => (<rect key={i} x={64 + i*14} y={legY} width="10" height="10" rx="2" fill={col}/>))}
              <text x={64 + 5*14 + 4} y={legY + 9} style={{ fontFamily:SoS.sans, fontSize:10, fill:SoS.inkMuted }}>Mere</text>
              <text x="24" y={legY + 44} style={{ fontFamily:SoS.sans, fontSize:13, fontWeight:700, fill:SoS.ink }}>Fordeling på indsatstype</text>
              {typeRows.map((tr, i) => {
                const t = SoS_TYPER[tr[0]]; const by = legY + 60 + i*24;
                return (
                  <g key={tr[0]}>
                    <text x="24" y={by + 11} style={{ fontFamily:SoS.sans, fontSize:12, fill:SoS.ink }}>{t ? t.short : tr[0]}</text>
                    <rect x="140" y={by} width="470" height="14" rx="3" fill={SoS.lineSoft}/>
                    <rect x="140" y={by} width={Math.round(tr[1] / maxType * 470)} height="14" rx="3" fill={t ? t.color : SoS.accent}/>
                    <text x="618" y={by + 11} style={{ fontFamily:SoS.mono, fontSize:11, fill:SoS.inkMuted }}>{tr[1]}</text>
                  </g>
                );
              })}
            </svg>
          </DSCard>
          <div style={{ fontFamily:SoS.sans, fontSize:11, color:SoS.inkMuted, marginTop:10 }}>
            Bygget på systemets aktuelle data. Heatmap viser aftaler pr. dag i {year}.
          </div>
        </div>
      );
    })()}

    {rapTab === 'definitioner' && ("""

sub("    {rapTab === 'definitioner' && (", BLOK, "C: aktivitetsoverblik-blok")

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

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

# 1) Seed nogle finansieringskilder
sub(
    "  finansieringskilder: [],  // fonde/projekter/bevillinger — admin tilføjer",
    "  finansieringskilder: ['Velux Fonden', 'Trygfonden', 'Nordea-fonden'],  // fonde/projekter — admin tilføjer flere",
    "1: seed finansieringskilder")

# 2) Berig a-17/18/19 med strukturerede felter (demo til rapport)
sub(
    "    { id: 'a-17', menneskeId: 'b-2', brobyggerId: 'bb-3', date: d(-6),  start: '13:00', end: '14:00', activity: 'Lægebesøg',            location: 'Klinik Trøjborg',         status: 'confirmed', kategori: 'laege',",
    "    { id: 'a-17', menneskeId: 'b-2', brobyggerId: 'bb-3', date: d(-6),  start: '13:00', end: '14:00', activity: 'Lægebesøg',            location: 'Klinik Trøjborg',         status: 'confirmed', kategori: 'laege', aftaletype: 'Fysisk følgeskab', brobygningstype: 'Sundhed', henvender: 'Region', modtagerType: 'Almen praksis', finansiering: 'Velux Fonden',",
    "2a: berig a-17")

sub(
    "    { id: 'a-18', menneskeId: 'b-4', brobyggerId: 'bb-7', date: d(-5),  start: '10:00', end: '11:00', activity: 'Biblioteksbesøg',       location: 'Dokk1',                   status: 'confirmed',",
    "    { id: 'a-18', menneskeId: 'b-4', brobyggerId: 'bb-7', date: d(-5),  start: '10:00', end: '11:00', activity: 'Biblioteksbesøg',       location: 'Dokk1',                   status: 'aflyst', aflysningsAarsag: 'Manglende brobygger', aflystAf: 'Social Sundhed', aftaletype: 'Supportbrobygning', brobygningstype: 'Social', henvender: 'Personen selv', modtagerType: 'Andet', finansiering: 'Trygfonden',",
    "2b: berig a-18 (aflyst)")

sub(
    "    { id: 'a-19', menneskeId: 'b-3', brobyggerId: 'bb-5', date: d(-12), start: '11:00', end: '12:00', activity: 'Sangeftermiddag',       location: 'Musikhuset Aarhus',       status: 'confirmed',",
    "    { id: 'a-19', menneskeId: 'b-3', brobyggerId: 'bb-5', date: d(-12), start: '11:00', end: '12:00', activity: 'Sangeftermiddag',       location: 'Musikhuset Aarhus',       status: 'confirmed', aftaletype: 'Ringeopgave', brobygningstype: 'Forening', henvender: 'Kommune', modtagerType: 'Kommune', finansiering: 'Velux Fonden',",
    "2c: berig a-19")

# 3) Indsæt struktureret rapport-blok øverst i statistik-fanen
BLOK = """          {(() => {
            const A = window.SoS_APPOINTMENTS_BUSY || [];
            const MN = window.SoS_MENNESKER || {};
            const cancelled = A.filter(a => ['aflyst','afslaaet','brudt'].indexOf(a.status) >= 0 || (a.brobyggerLog && a.brobyggerLog.udfald === 'afbud'));
            const completed = A.filter(a => a.status === 'gennemfoert' || (a.brobyggerLog && a.brobyggerLog.udfald === 'gennemfoert'));
            const beslut = cancelled.length + completed.length;
            const aflysPct = beslut ? Math.round(cancelled.length / beslut * 100) : 0;
            const tally = (arr, fn) => { const o = {}; arr.forEach(x => { const k = fn(x); if (k) o[k] = (o[k]||0)+1; }); return Object.entries(o).sort((a,b)=>b[1]-a[1]); };
            const topAar = tally(cancelled, a => a.aflysningsAarsag || (a.brobyggerLog && a.brobyggerLog.udfald === 'afbud' ? 'Borger afbud' : a.brobyggerLog && a.brobyggerLog.udfald === 'ikke-modt' ? 'Borger udeblev' : 'Andet'));
            const topHs   = tally(A, a => { const m = MN[a.menneskeId]; return m && m.hq ? m.hq : 'Ukendt'; });
            const topModt = tally(A, a => a.modtagerType);
            const topFin  = tally(A, a => a.finansiering);
            const mx = e => e.length ? e[0][1] : 1;
            const bar = (entries, color) => entries.length ? entries.map(([k,v]) => (
              <div key={k} style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}>
                <div style={{ width:130, fontFamily:SoS.sans, fontSize:11, color:SoS.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{k}</div>
                <div style={{ flex:1, height:6, background:SoS.lineSoft, borderRadius:3, overflow:'hidden' }}>
                  <div style={{ width: Math.round(v/mx(entries)*100)+'%', height:'100%', background:color, borderRadius:3 }}/>
                </div>
                <div style={{ width:28, textAlign:'right', fontFamily:SoS.mono, fontSize:11, fontWeight:600, color:SoS.inkMuted }}>{v}</div>
              </div>
            )) : <div style={{ fontFamily:SoS.sans, fontSize:12, color:SoS.inkMuted, padding:'8px 0' }}>Ingen data endnu — registreres på aftalen</div>;
            return (
              <>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                  <DSCard title="Aflysningsrate" subtitle={beslut + ' afgjorte aftaler'}>
                    <div style={{ fontFamily:SoS.mono, fontSize:34, fontWeight:700, letterSpacing:-1, color: aflysPct > 30 ? SoS.amber : SoS.sage }}>{aflysPct}%</div>
                    <div style={{ fontFamily:SoS.sans, fontSize:12, color:SoS.inkSoft, marginTop:2 }}>{cancelled.length} aflyst · {completed.length} gennemført</div>
                  </DSCard>
                  <DSCard title="Top aflysningsårsager">{bar(topAar, SoS.amber)}</DSCard>
                </div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
                  <DSCard title="Per hovedsæde">{bar(topHs, SoS.accent)}</DSCard>
                  <DSCard title="Modtager">{bar(topModt, SoS.sky)}</DSCard>
                </div>
                <DSCard title="Finansiering / projekt">{bar(topFin, SoS.sage)}</DSCard>
              </>
            );
          })()}

"""

sub(
    "        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>\n\n          {/* Udfald + trivsel side om side */}",
    "        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>\n\n" + BLOK + "          {/* Udfald + trivsel side om side */}",
    "3: struktureret rapport-blok")

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

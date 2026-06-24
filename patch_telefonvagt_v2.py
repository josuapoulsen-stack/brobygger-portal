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

# A) Fjern hardkodede Storebælt-zoner (behold feltet tomt; SoS_hqMatch virker som enkelt/alle)
sub("""  merged.zoner = (stored.zoner && typeof stored.zoner === 'object') ? stored.zoner : {
    'Vest for Storebælt': ['Nord', 'Midt', 'Kronjylland', 'Aarhus', 'Sydvest', 'Syd'],
    'Øst for Storebælt': ['Sjælland', 'Hovedstaden'],
  };""",
    "  merged.zoner = (stored.zoner && typeof stored.zoner === 'object') ? stored.zoner : {};",
    "A: tøm zoner")

# B) Fjern zone-option i desktop-dropdown
sub("                {Object.keys(SoS_REFS.zoner || {}).map(z => <option key={z} value={z}>📞 {z}</option>)}\n",
    "",
    "B: fjern desktop zone-option")

# C) Fjern zone-knapper i mobil-vælger
sub("""          {Object.keys(SoS_REFS.zoner || {}).map(z => {
            const sel = picked === z;
            return (
              <button key={z} onClick={() => setPicked(z)} style={{
                display: 'flex', alignItems: 'center', gap: 12, width: '100%',
                padding: 14, marginBottom: 6, textAlign: 'left', background: '#fff',
                border: `2px solid ${sel ? SoS.orange : SoS.lineSoft}`,
                borderRadius: SoS.r.md, cursor: 'pointer',
              }}>
                <span style={{ fontSize: 16 }}>📞</span>
                <span style={{ flex: 1 }}>
                  <span style={{ display: 'block', fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{z}</span>
                  <span style={{ display: 'block', fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>Telefonvagt · {(SoS_REFS.zoner[z] || []).length} hovedsæder</span>
                </span>
                {sel && <Icon name="check" size={16} color={SoS.orange}/>}
              </button>
            );
          })}
          {SoS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {""",
    "          {SoS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {",
    "C: fjern mobil zone-knapper")

# D) AdminMobile-kald: tilføj onPickHq
sub("""        canAllHq={activeRole === "admin" || activeRole === "landssekretariat"}
        onOpenSettings={() => setSettingsOpen(true)}""",
    """        canAllHq={activeRole === "admin" || activeRole === "landssekretariat"}
        onPickHq={(hq) => setViewingHq(hq)}
        onOpenSettings={() => setSettingsOpen(true)}""",
    "D: AdminMobile onPickHq")

# E) AdminMobile-signatur: onPickHq
sub("const AdminMobile = ({ user, viewingHq, ownHq, isAdmin, canAllHq = false, onOpenSettings, onOpenIntake, onOpenMatching, onOpenMessages, onOpenDesktop }) => {",
    "const AdminMobile = ({ user, viewingHq, ownHq, isAdmin, canAllHq = false, onPickHq, onOpenSettings, onOpenIntake, onOpenMatching, onOpenMessages, onOpenDesktop }) => {",
    "E: signatur onPickHq")

# F) State + rad-style
sub("  const isTemporary = viewingHq !== ownHq;",
    "  const isTemporary = viewingHq !== ownHq;\n"
    "  const [hqSwitchOpen, setHqSwitchOpen] = React.useState(false);\n"
    "  const _hqRow = (sel, col) => ({ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: 14, marginBottom: 6, textAlign: 'left', background: '#fff', border: '2px solid ' + (sel ? col : SoS.lineSoft), borderRadius: SoS.r.md, cursor: 'pointer' });",
    "F: state + radstyle")

# G) Eyebrow → tappbar hq-skifter + bottom sheet
sub("""            <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
              color: SoS.accent, textTransform: 'uppercase', letterSpacing: 1 }}>
              {isAdmin ? 'ADMIN — SOCIAL SUNDHED' : canAllHq ? `LANDSSEKRETARIAT — ${viewingHq.toUpperCase()}` : `RAADGIVER — ${viewingHq.toUpperCase()}`}
            </div>""",
    """            <button onClick={() => { if (onPickHq) setHqSwitchOpen(true); }} style={{
              background: 'none', border: 'none', padding: 0, cursor: onPickHq ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', gap: 4,
              fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
              color: SoS.accent, textTransform: 'uppercase', letterSpacing: 1 }}>
              {isAdmin ? 'ADMIN — SOCIAL SUNDHED' : canAllHq ? `LANDSSEKRETARIAT — ${viewingHq.toUpperCase()}` : `RAADGIVER — ${viewingHq.toUpperCase()}`}
              {onPickHq && <Icon name="chevronD" size={12} color={SoS.accent}/>}
            </button>
            {hqSwitchOpen && (
              <div onClick={() => setHqSwitchOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 500,
                background: 'rgba(0,0,0,0.4)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
                <div onClick={e => e.stopPropagation()} style={{ background: '#fff', borderRadius: '20px 20px 0 0',
                  padding: '20px 18px 36px', maxHeight: '75vh', overflowY: 'auto' }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink, marginBottom: 4 }}>Skift hovedsæde</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginBottom: 14 }}>
                    Dæk og lav aftaler for et andet hovedsæde. Nulstilles ved logout.
                  </div>
                  {canAllHq && (
                    <button onClick={() => { onPickHq('Alle hovedsæder'); setHqSwitchOpen(false); }} style={_hqRow(viewingHq === 'Alle hovedsæder', SoS.accent)}>
                      <div style={{ width: 12, height: 12, borderRadius: 6, background: SoS.accent }}/>
                      <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>Alle hovedsæder</span>
                      {viewingHq === 'Alle hovedsæder' && <Icon name="check" size={16} color={SoS.accent}/>}
                    </button>
                  )}
                  {SoS_HOVEDSAEDER.map(h => {
                    const sel = viewingHq === h; const col = (SoS.hq && SoS.hq[h]) || SoS.orange;
                    return (
                      <button key={h} onClick={() => { onPickHq(h); setHqSwitchOpen(false); }} style={_hqRow(sel, col)}>
                        <div style={{ width: 12, height: 12, borderRadius: 6, background: col }}/>
                        <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}>{h}{h === ownHq ? ' · dit' : ''}</span>
                        {sel && <Icon name="check" size={16} color={col}/>}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}""",
    "G: eyebrow hq-skifter + sheet")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

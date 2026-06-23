import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label, count=1):
    global c
    n = c.count(old)
    if n >= 1:
        c = c.replace(old, new, count); ok.append(label + (f' (x{min(n,count)})' if count>1 else ''))
    else:
        fail.append(label)

# 1) Zoner i datalaget (Øst/Vest for Storebælt) + helper
sub("  merged.farver = (stored.farver && typeof stored.farver === 'object') ? stored.farver : {};",
    "  merged.farver = (stored.farver && typeof stored.farver === 'object') ? stored.farver : {};\n"
    "  merged.zoner = (stored.zoner && typeof stored.zoner === 'object') ? stored.zoner : {\n"
    "    'Vest for Storebælt': ['Nord', 'Midt', 'Kronjylland', 'Aarhus', 'Sydvest', 'Syd'],\n"
    "    'Øst for Storebælt': ['Sjælland', 'Hovedstaden'],\n"
    "  };",
    "1a: zoner-data")

sub("window.SoS_saveRefs = saveRefs;",
    "window.SoS_saveRefs = saveRefs;\n"
    "// Telefonvagt: matcher et hovedsæde mod et scope (enkelt hq, 'Alle hovedsæder', eller en zone)\n"
    "window.SoS_hqMatch = function (hq, scope) {\n"
    "  if (!scope || scope === 'Alle hovedsæder') return true;\n"
    "  if (hq === scope) return true;\n"
    "  var z = (SoS_REFS.zoner || {})[scope];\n"
    "  return !!(z && z.indexOf(hq) >= 0);\n"
    "};\n"
    "window.SoS_isZone = function (scope) { return !!(SoS_REFS.zoner && SoS_REFS.zoner[scope]); };",
    "1b: helper")

# 2) Desktop-dropdown: zone-valg (telefonvagt) for alle
sub('                {canAllHq && <option value="Alle hovedsæder">Alle hovedsæder</option>}\n'
    '                {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}',
    '                {canAllHq && <option value="Alle hovedsæder">Alle hovedsæder</option>}\n'
    '                {Object.keys(SoS_REFS.zoner || {}).map(z => <option key={z} value={z}>📞 {z}</option>)}\n'
    '                {SoS_HOVEDSAEDER.map(h => <option key={h} value={h}>{h}</option>)}',
    "2: desktop-dropdown zoner")

# 3) Mobil-vælger: zone-knapper (telefonvagt) for alle
sub("          {SoS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {",
    """          {Object.keys(SoS_REFS.zoner || {}).map(z => {
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
    "3: mobil-vælger zoner")

# 4) Scope-filtre → SoS_hqMatch
sub("  const mns = Object.values(window.SoS_MENNESKER || {}).filter(m => !sc || m.hq === viewingHq);",
    "  const mns = Object.values(window.SoS_MENNESKER || {}).filter(m => window.SoS_hqMatch(m.hq, viewingHq));",
    "4a: UCLA scope")

sub("                    .filter(m => (m.status === 'afventer' || m.status === 'venter') && (viewingHq === 'Alle hovedsæder' || m.hq === viewingHq)).length;",
    "                    .filter(m => (m.status === 'afventer' || m.status === 'venter') && window.SoS_hqMatch(m.hq, viewingHq)).length;",
    "4b: mobil-tæller scope")

sub("    .filter(b => !scopeHq || scopeHq === 'Alle hovedsæder' || b.hq === scopeHq)",
    "    .filter(b => !scopeHq || window.SoS_hqMatch(b.hq, scopeHq))",
    "4c: DesktopBrobyggere scope")

sub("    if (scopeHq && scopeHq !== 'Alle hovedsæder' && m.hq !== scopeHq) return false;",
    "    if (scopeHq && !window.SoS_hqMatch(m.hq, scopeHq)) return false;",
    "4d: DesktopMennesker scope")

sub("(window.SoS_APPOINTMENTS_BUSY || []).filter(a => !_sc0 || (_MN0[a.menneskeId] && _MN0[a.menneskeId].hq === viewingHq))",
    "(window.SoS_APPOINTMENTS_BUSY || []).filter(a => window.SoS_hqMatch((_MN0[a.menneskeId] || {}).hq, viewingHq))",
    "4e: rapport-statistik appts")

sub("      const mns      = Object.values(_MN0).filter(m => !_sc0 || m.hq === viewingHq);",
    "      const mns      = Object.values(_MN0).filter(m => window.SoS_hqMatch(m.hq, viewingHq));",
    "4f: rapport-statistik mns")

sub("          if (l.menneskeId && _MN0[l.menneskeId]) return _MN0[l.menneskeId].hq === viewingHq;",
    "          if (l.menneskeId && _MN0[l.menneskeId]) return window.SoS_hqMatch(_MN0[l.menneskeId].hq, viewingHq);",
    "4g: opkald menneske scope")

sub("          if (l.brobyggerId) { const b = (window.SoS_BROBYGGERE || []).find(x => x.id === l.brobyggerId); return !!b && b.hq === viewingHq; }",
    "          if (l.brobyggerId) { const b = (window.SoS_BROBYGGERE || []).find(x => x.id === l.brobyggerId); return !!b && window.SoS_hqMatch(b.hq, viewingHq); }",
    "4h: opkald brobygger scope")

sub("(window.SoS_APPOINTMENTS_BUSY || []).filter(a => !_sc || (MN[a.menneskeId] && MN[a.menneskeId].hq === viewingHq))",
    "(window.SoS_APPOINTMENTS_BUSY || []).filter(a => window.SoS_hqMatch((MN[a.menneskeId] || {}).hq, viewingHq))",
    "4i: struktureret+aktivitet appts", count=2)

sub("Object.values(MN).filter(m => !_sc || m.hq === viewingHq).length",
    "Object.values(MN).filter(m => window.SoS_hqMatch(m.hq, viewingHq)).length",
    "4j: aktivitet mennesker-count")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

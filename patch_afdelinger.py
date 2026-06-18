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

# 1) Seed afdelinger (2-niveau geografi)
sub(
    "  afdelinger:         [],  // {navn, hovedsaede} — admin tilføjer",
    "  afdelinger:         [\n"
    "    { navn: 'Aarhus C', hovedsaede: 'Aarhus' }, { navn: 'Brabrand', hovedsaede: 'Aarhus' },\n"
    "    { navn: 'Trøjborg', hovedsaede: 'Aarhus' }, { navn: 'Risskov', hovedsaede: 'Aarhus' },\n"
    "    { navn: 'Randers', hovedsaede: 'Midt' }, { navn: 'Viborg', hovedsaede: 'Midt' },\n"
    "    { navn: 'København', hovedsaede: 'Hovedstaden' }, { navn: 'Frederiksberg', hovedsaede: 'Hovedstaden' },\n"
    "  ],  // {navn, hovedsaede} — admin tilføjer flere",
    "1: seed afdelinger")

# 2) Tilføj hq + afdeling til seed-mennesker b-1..b-6
for bid, hq, afd in [
    ('b-1','Aarhus','Aarhus C'), ('b-2','Aarhus','Brabrand'), ('b-3','Aarhus','Aarhus C'),
    ('b-4','Aarhus','Trøjborg'), ('b-5','Midt','Randers'), ('b-6','Hovedstaden','København')]:
    sub(f"    id: '{bid}',",
        f"    id: '{bid}',\n    hq: '{hq}', afdeling: '{afd}',",
        f"2: hq/afdeling på {bid}")

# 3) afdFilter-state i DesktopMennesker
sub(
    "  const [hqFilter,     setHqFilter]     = React.useState('alle');",
    "  const [hqFilter,     setHqFilter]     = React.useState('alle');\n  const [afdFilter,    setAfdFilter]    = React.useState('alle');",
    "3: afdFilter state")

# 4) Filter-logik
sub(
    "    if (hqFilter !== 'alle' && m.hq !== hqFilter) return false;",
    "    if (hqFilter !== 'alle' && m.hq !== hqFilter) return false;\n    if (afdFilter !== 'alle' && m.afdeling !== afdFilter) return false;",
    "4: afdeling filter-logik")

# 5) Nulstil afdeling når hovedsæde skifter
sub("<button onClick={() => setHqFilter('alle')} style={{",
    "<button onClick={() => { setHqFilter('alle'); setAfdFilter('alle'); }} style={{",
    "5a: reset afd ved 'alle'")
sub("<button key={hq} onClick={() => setHqFilter(hq)} style={{",
    "<button key={hq} onClick={() => { setHqFilter(hq); setAfdFilter('alle'); }} style={{",
    "5b: reset afd ved hq-valg")

# 6) Afdelings-chips (vises når et hovedsæde er valgt og har afdelinger)
sub(
    "        ))}\n      </div>\n\n      {/* Tabel */}",
    "        ))}\n      </div>\n\n"
    "      {hqFilter !== 'alle' && SoS_REFS.afdelinger.filter(a => a.hovedsaede === hqFilter).length > 0 && (\n"
    "        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10, paddingLeft: 10,\n"
    "          borderLeft: `2px solid ${SoS.line}` }}>\n"
    "          <button onClick={() => setAfdFilter('alle')} style={{\n"
    "            padding: '4px 10px', borderRadius: SoS.r.sm,\n"
    "            background: afdFilter === 'alle' ? SoS.accent : SoS.surface,\n"
    "            color: afdFilter === 'alle' ? '#fff' : SoS.inkSoft,\n"
    "            border: `1px solid ${afdFilter === 'alle' ? SoS.accent : SoS.line}`,\n"
    "            fontFamily: SoS.sans, fontSize: 11, fontWeight: afdFilter === 'alle' ? 700 : 400,\n"
    "            cursor: 'pointer' }}>Alle afdelinger</button>\n"
    "          {SoS_REFS.afdelinger.filter(a => a.hovedsaede === hqFilter).map(a => (\n"
    "            <button key={a.navn} onClick={() => setAfdFilter(a.navn)} style={{\n"
    "              padding: '4px 10px', borderRadius: SoS.r.sm,\n"
    "              background: afdFilter === a.navn ? SoS.accent : SoS.surface,\n"
    "              color: afdFilter === a.navn ? '#fff' : SoS.inkSoft,\n"
    "              border: `1px solid ${afdFilter === a.navn ? SoS.accent : SoS.line}`,\n"
    "              fontFamily: SoS.sans, fontSize: 11, fontWeight: afdFilter === a.navn ? 700 : 400,\n"
    "              cursor: 'pointer' }}>{a.navn}</button>\n"
    "          ))}\n"
    "        </div>\n"
    "      )}\n\n"
    "      {/* Tabel */}",
    "6: afdelings-chips")

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

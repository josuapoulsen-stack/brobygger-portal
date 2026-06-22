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

# 0) Send viewingHq ind
sub("{section === 'rapport' && canRapport && <DesktopRapport/>}",
    "{section === 'rapport' && canRapport && <DesktopRapport viewingHq={viewingHq}/>}",
    "0: prop")

# 1) Signatur
sub("const DesktopRapport = () => {", "const DesktopRapport = ({ viewingHq }) => {", "1: signatur")

# 2) Statistik-fane: scope appts + mns
sub(
    "      const appts    = window.SoS_APPOINTMENTS_BUSY || [];\n"
    "      const mns      = Object.values(window.SoS_MENNESKER || {});",
    "      const _MN0 = window.SoS_MENNESKER || {};\n"
    "      const _sc0 = !!(viewingHq && viewingHq !== 'Alle hovedsæder');\n"
    "      const appts    = (window.SoS_APPOINTMENTS_BUSY || []).filter(a => !_sc0 || (_MN0[a.menneskeId] && _MN0[a.menneskeId].hq === viewingHq));\n"
    "      const mns      = Object.values(_MN0).filter(m => !_sc0 || m.hq === viewingHq);",
    "2: statistik scope")

# 3) Struktureret-blok (12-space): scope A
sub(
    "            const A = window.SoS_APPOINTMENTS_BUSY || [];\n"
    "            const MN = window.SoS_MENNESKER || {};",
    "            const MN = window.SoS_MENNESKER || {};\n"
    "            const _sc = !!(viewingHq && viewingHq !== 'Alle hovedsæder');\n"
    "            const A = (window.SoS_APPOINTMENTS_BUSY || []).filter(a => !_sc || (MN[a.menneskeId] && MN[a.menneskeId].hq === viewingHq));",
    "3: struktureret scope")

# 4) Aktivitet-fane (6-space): scope A
sub(
    "      const A = window.SoS_APPOINTMENTS_BUSY || [];\n"
    "      const MN = window.SoS_MENNESKER || {};",
    "      const MN = window.SoS_MENNESKER || {};\n"
    "      const _sc = !!(viewingHq && viewingHq !== 'Alle hovedsæder');\n"
    "      const A = (window.SoS_APPOINTMENTS_BUSY || []).filter(a => !_sc || (MN[a.menneskeId] && MN[a.menneskeId].hq === viewingHq));",
    "4: aktivitet scope")

# 5) Mennesker-KPI scoped
sub(
    "['Mennesker', Object.keys(MN).length]",
    "['Mennesker', Object.values(MN).filter(m => !_sc || m.hq === viewingHq).length]",
    "5: mennesker-KPI scoped")

# 6) Scope-label i aktivitet (intro + SVG-titel)
sub(
    "Organisationens aktivitet i {year} — til download/print for ledelse og fonde.",
    "{_sc ? viewingHq : 'Hele organisationen'} · {year} — til download/print for ledelse og fonde.",
    "6a: intro-label")
sub(
    "fill:SoS.ink }}>Aktivitetsoverblik · {year}</text>",
    "fill:SoS.ink }}>Aktivitetsoverblik · {_sc ? viewingHq : 'Alle hovedsæder'} · {year}</text>",
    "6b: svg-titel-label")

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

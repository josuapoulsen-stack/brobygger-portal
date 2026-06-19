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

# 1) Paginerings-state + reset
sub(
    "  const [bbDetaljeId, setBbDetaljeId] = React.useState(null);",
    "  const [bbDetaljeId, setBbDetaljeId] = React.useState(null);\n"
    "  const [aptVis, setAptVis] = React.useState(60);\n"
    "  const [bbVis,  setBbVis]  = React.useState(40);\n"
    "  React.useEffect(() => { setAptVis(60); setBbVis(40); }, [view, weekOffset, selectedDay, bbFilter, typeFilter, statusFilter]);",
    "1: pagination-state + reset")

# 2) Hæv MAX pr. dag i ugevisning (3 → 5)
sub("  const MAX = 3;", "  const MAX = 5;", "2: MAX 3->5")

# 3) Dagsvisning: cap + indlæs flere
sub(
    "            : selAppts.map(renderRow)\n          }",
    "            : (<>\n"
    "                {selAppts.slice(0, aptVis).map(renderRow)}\n"
    "                {selAppts.length > aptVis && (\n"
    "                  <div style={{ textAlign: 'center', marginTop: 8 }}>\n"
    "                    <button onClick={() => setAptVis(v => v + 60)} style={{ padding: '6px 14px',\n"
    "                      background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "                      cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink }}>\n"
    "                      Indlæs flere ({selAppts.length - aptVis})\n"
    "                    </button>\n"
    "                  </div>\n"
    "                )}\n"
    "              </>)\n          }",
    "3: dagsvisning cap")

# 4) Vagtplan: paginér brobygger-rækker
sub("{aktiveBb.map((bb, ri) => (", "{aktiveBb.slice(0, bbVis).map((bb, ri) => (", "4a: vagtplan slice")
sub(
    "      {/* Totals row */}",
    "      {aktiveBb.length > bbVis && (\n"
    "        <div style={{ textAlign: 'center', marginBottom: 14 }}>\n"
    "          <button onClick={() => setBbVis(v => v + 40)} style={{ padding: '6px 14px',\n"
    "            background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "            cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink }}>\n"
    "            Indlæs flere brobyggere ({aktiveBb.length - bbVis})\n"
    "          </button>\n"
    "        </div>\n"
    "      )}\n"
    "\n"
    "      {/* Totals row */}",
    "4b: vagtplan indlæs flere")

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

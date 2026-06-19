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

# ── DesktopMennesker ──
sub(
    "  const [afdFilter,    setAfdFilter]    = React.useState('alle');",
    "  const [afdFilter,    setAfdFilter]    = React.useState('alle');\n"
    "  const [vis,          setVis]          = React.useState(50);\n"
    "  React.useEffect(() => { setVis(50); }, [search, typeFilter, statusFilter, hqFilter, afdFilter, scopeHq, scopeAfd]);",
    "M1: vis-state + reset")
sub(
    "            {filtered.map((m, i) => {",
    "            {filtered.slice(0, vis).map((m, i) => {",
    "M2: slice render")
sub(
    "        <div style={{ padding: '8px 14px', borderTop: `1px solid ${SoS.lineSoft}`,\n"
    "          fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, textAlign: 'right' }}>\n"
    "          {filtered.length} af {alle.length} mennesker\n"
    "        </div>",
    "        <div style={{ padding: '8px 14px', borderTop: `1px solid ${SoS.lineSoft}`,\n"
    "          display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>\n"
    "          <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>\n"
    "            Viser {Math.min(vis, filtered.length)} af {filtered.length}{filtered.length !== alle.length ? ' (' + alle.length + ' i alt)' : ''}\n"
    "          </span>\n"
    "          {filtered.length > vis && (\n"
    "            <button onClick={() => setVis(v => v + 50)} style={{ padding: '5px 12px',\n"
    "              background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "              cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink }}>\n"
    "              Indlæs flere ({filtered.length - vis})\n"
    "            </button>\n"
    "          )}\n"
    "        </div>",
    "M3: footer + indlæs flere")

# ── DesktopBrobyggere ──
sub(
    "  const [selectedBb, setSelectedBb] = React.useState(null);",
    "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
    "  const [vis, setVis] = React.useState(50);\n"
    "  React.useEffect(() => { setVis(50); }, [filter, search, scopeHq, scopeAfd]);",
    "B1: vis-state + reset")
sub(
    "          ) : rows.map(b => {",
    "          ) : rows.slice(0, vis).map(b => {",
    "B2: slice render")
sub(
    "      {/* Footer */}\n"
    "      <div style={{ marginTop: 12, fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,\n"
    "        textAlign: 'right' }}>\n"
    "        {rows.length} af {SoS_BROBYGGERE.length} brobyggere\n"
    "      </div>",
    "      {/* Footer */}\n"
    "      <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>\n"
    "        <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>\n"
    "          Viser {Math.min(vis, rows.length)} af {rows.length}{rows.length !== SoS_BROBYGGERE.length ? ' (' + SoS_BROBYGGERE.length + ' i alt)' : ''}\n"
    "        </span>\n"
    "        {rows.length > vis && (\n"
    "          <button onClick={() => setVis(v => v + 50)} style={{ padding: '5px 12px',\n"
    "            background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,\n"
    "            cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink }}>\n"
    "            Indlæs flere ({rows.length - vis})\n"
    "          </button>\n"
    "        )}\n"
    "      </div>",
    "B3: footer + indlæs flere")

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

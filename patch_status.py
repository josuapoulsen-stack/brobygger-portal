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

# 1) Global status-taksonomi (efter SoS_HOVEDSAEDER) — beholder pending/confirmed
sub(
    "// Bagudkompatibel: mange steder bruger SoS_HOVEDSAEDER — peg på stamdata\nconst SoS_HOVEDSAEDER = SoS_REFS.hovedsaeder;",
    "// Bagudkompatibel: mange steder bruger SoS_HOVEDSAEDER — peg på stamdata\nconst SoS_HOVEDSAEDER = SoS_REFS.hovedsaeder;\n"
    "\n"
    "// Aftale-status (livscyklus). pending/confirmed bevares for bagudkompatibilitet.\n"
    "const AFTALE_STATUS = [\n"
    "  { v: 'kladde',      l: 'Kladde',          c: '#9E9E9E', bg: '#F5F5F5' },\n"
    "  { v: 'pending',     l: 'Ikke bekræftet',  c: '#E87A3E', bg: '#FFF3E0' },\n"
    "  { v: 'confirmed',   l: 'Bekræftet',       c: '#388E3C', bg: '#E8F5E9' },\n"
    "  { v: 'gennemfoert', l: 'Gennemført',      c: '#4A7C59', bg: '#E8F5E9' },\n"
    "  { v: 'aflyst',      l: 'Aflyst',          c: '#C62828', bg: '#FCE4EC' },\n"
    "  { v: 'afslaaet',    l: 'Afslået',         c: '#C62828', bg: '#FCE4EC' },\n"
    "  { v: 'brudt',       l: 'Brudt',           c: '#9E9E9E', bg: '#F5F5F5' },\n"
    "];\n"
    "const AFTALE_STATUS_LABEL = AFTALE_STATUS.reduce((m, s) => { m[s.v] = s.l; return m; }, {});\n"
    "const AFTALE_STATUS_COLOR = AFTALE_STATUS.reduce((m, s) => { m[s.v] = s.c; return m; }, {});\n"
    "const AFTALE_STATUS_BG    = AFTALE_STATUS.reduce((m, s) => { m[s.v] = s.bg; return m; }, {});\n"
    "window.AFTALE_STATUS = AFTALE_STATUS;",
    "1: global AFTALE_STATUS taksonomi")

# 2) Status-vælger i DesktopApptModal (øverst i Klassificering)
sub(
    "            <div style={{ ...labelStyle, marginBottom: 10 }}>Klassificering</div>\n"
    "            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>",
    "            <div style={{ ...labelStyle, marginBottom: 10 }}>Klassificering</div>\n"
    "            <div style={{ marginBottom: 10 }}>\n"
    "              <div style={labelStyle}>Status</div>\n"
    "              <select value={form.status} onChange={upd('status')} style={inputStyle}>\n"
    "                {AFTALE_STATUS.map(s => <option key={s.v} value={s.v}>{s.l}</option>)}\n"
    "              </select>\n"
    "            </div>\n"
    "            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>",
    "2: status-vælger i modal")

# 3) Kalender/liste — generaliser filter + udvid label/farve-maps + filter-chips
sub(
    "    if (statusFilter === 'confirmed' && a.status !== 'confirmed') return false;\n"
    "    if (statusFilter === 'pending'   && a.status !== 'pending')   return false;",
    "    if (statusFilter !== 'alle' && a.status !== statusFilter) return false;",
    "3a: generaliser status-filter")

sub(
    "  const STATUS_LABEL = { confirmed: 'Bekræftet', pending: 'Afventer' };\n"
    "  const STATUS_COLOR = { confirmed: '#388E3C', pending: '#E87A3E' };\n"
    "  const STATUS_BG    = { confirmed: '#E8F5E9', pending: '#FFF3E0' };",
    "  const STATUS_LABEL = AFTALE_STATUS_LABEL;\n"
    "  const STATUS_COLOR = AFTALE_STATUS_COLOR;\n"
    "  const STATUS_BG    = AFTALE_STATUS_BG;",
    "3b: udvid status-maps")

sub(
    "{['alle', 'confirmed', 'pending'].map(s => {",
    "{['alle', 'kladde', 'pending', 'confirmed', 'gennemfoert', 'aflyst', 'afslaaet', 'brudt'].map(s => {",
    "3c: udvid status-filter-chips")

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

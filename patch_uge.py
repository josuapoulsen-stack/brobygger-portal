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

# 1) Render ALLE aftaler pr. dag (drop cap)
sub(
    "              const ds = fmt(day), all = getAppts(ds), vis = all.slice(0, MAX);\n"
    "              const more = all.length - MAX, isT = ds === TODAY;",
    "              const ds = fmt(day), all = getAppts(ds), isT = ds === TODAY;",
    "1: drop slice/more")

# 2) Dag-kolonne: scrollbar med fast maks-højde (layout bundet selvom mange)
sub(
    "                <div key={i} style={{ padding: '8px 6px', minHeight: 120,",
    "                <div key={i} style={{ padding: '8px 6px', minHeight: 120, maxHeight: 420, overflowY: 'auto',",
    "2: scrollbar kolonne")

# 3) Map over ALLE
sub("                  {vis.map(a => {", "                  {all.map(a => {", "3: map all")

# 4) Fjern '+N mere'-knappen (alt renderes nu)
sub(
    "                  {more > 0 && (\n"
    "                    <button onClick={() => { setSelectedDay(ds); setView('dag'); }}\n"
    "                      style={{ width: '100%', padding: '5px 4px', borderRadius: 0, border: 'none',\n"
    "                        background: SoS.accent + '10', cursor: 'pointer',\n"
    "                        fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.accent }}>\n"
    "                      +{more} mere &#8594;\n"
    "                    </button>\n"
    "                  )}\n",
    "",
    "4: fjern +N mere-knap")

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

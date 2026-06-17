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

STATE_BLOCK = """  const TODAY_S = new Date().toISOString().slice(0, 10);
  const [opfVersion, setOpfVersion] = React.useState(0);
  const opfPending = (window.SoS_APPOINTMENTS_BUSY || [])
    .filter(a => a.date < TODAY_S && a.brobyggerLog && !a.raadgiverOpfoelgning)
    .sort((a, b) => a.date.localeCompare(b.date));
  const setOpfoelgning = (apptId, val) => {
    const list = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>
      a.id === apptId ? { ...a, raadgiverOpfoelgning: val } : a);
    window.SoS_APPOINTMENTS_BUSY = list;
    if (window.SoS_STORE) window.SoS_STORE.save('appointments', list);
    setOpfVersion(v => v + 1);
  };"""

# 1) Fjern blok fra den forkerte komponent (første TYPE_C, linje ~7544)
sub(
    "  const TYPE_C = { sundhed: SoS.sundhed, forening: SoS.forening, social: SoS.social };\n" + STATE_BLOCK,
    "  const TYPE_C = { sundhed: SoS.sundhed, forening: SoS.forening, social: SoS.social };",
    "1: revert forkert indsættelse")

# 2) Indsæt i AdminMobile efter pendingMatches (unik linje)
sub(
    "  const pendingMatches = SoS_BROBYGGERE.filter(b => b.pending > 0).length;",
    "  const pendingMatches = SoS_BROBYGGERE.filter(b => b.pending > 0).length;\n" + STATE_BLOCK,
    "2: indsæt state i AdminMobile")

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

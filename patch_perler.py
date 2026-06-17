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

# ── 1) Erstat renderChatText med PerlerMark + generaliseret version ──
OLD_FN = """const renderChatText = (tekst, size) => {
  if (!tekst || String(tekst).indexOf(':sos:') === -1) return tekst;
  const parts = String(tekst).split(':sos:');
  const out = [];
  parts.forEach((p, i) => {
    if (p) out.push(p);
    if (i < parts.length - 1) out.push(
      <span key={'sos' + i} style={{ display: 'inline-flex', verticalAlign: 'middle', margin: '0 1px' }}>
        <SoSLogoMark size={size || 16}/>
      </span>
    );
  });
  return out;
};"""

NEW_FN = """const PerlerMark = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"
    aria-label="Perler på snor" style={{ display: 'block', flexShrink: 0 }}>
    <g fill="none" stroke="#4F7A43" strokeWidth="2" strokeLinecap="round">
      <path d="M27 20 C 21 31, 26 43, 22 55"/>
      <path d="M31 20 C 30 32, 32 41, 31 49"/>
      <path d="M35 20 C 41 31, 36 45, 40 57"/>
    </g>
    <g fill="#6FA85A">
      <circle cx="26" cy="14" r="5"/><circle cx="34" cy="12" r="5"/><circle cx="40" cy="16" r="4.5"/>
      <circle cx="22" cy="18" r="4"/><circle cx="31" cy="18" r="5"/><circle cx="38" cy="20" r="4"/>
      <circle cx="44" cy="13" r="3.5"/>
      <circle cx="24" cy="28" r="3.4"/><circle cx="23" cy="38" r="3.4"/><circle cx="22" cy="48" r="3.4"/><circle cx="21.5" cy="55" r="3"/>
      <circle cx="31" cy="30" r="3.2"/><circle cx="31" cy="40" r="3.2"/><circle cx="31" cy="49" r="3"/>
      <circle cx="37" cy="30" r="3.4"/><circle cx="38" cy="40" r="3.4"/><circle cx="39" cy="50" r="3.4"/><circle cx="40" cy="57" r="3"/>
    </g>
    <g fill="#A6CE96">
      <circle cx="32" cy="11" r="1.6"/><circle cx="24" cy="13" r="1.4"/>
      <circle cx="23" cy="27" r="1.2"/><circle cx="36" cy="29" r="1.2"/>
    </g>
  </svg>
);

const _CHAT_ICONS = { ':sos:': SoSLogoMark, ':perler:': PerlerMark };
const renderChatText = (tekst, size) => {
  if (!tekst) return tekst;
  const parts = String(tekst).split(/(:sos:|:perler:)/g);
  if (parts.length === 1) return tekst;
  return parts.map((p, i) => {
    if (!p) return null;
    const Comp = _CHAT_ICONS[p];
    if (Comp) return (
      <span key={i} style={{ display: 'inline-flex', verticalAlign: 'middle', margin: '0 1px' }}>
        <Comp size={size || 16}/>
      </span>
    );
    return p;
  });
};"""

sub(OLD_FN, NEW_FN, "1: PerlerMark + generaliseret renderChatText")

# ── 2) Tilføj :perler: til paletten (før :sos:) ──
sub(",':sos:'];", ",':perler:',':sos:'];", "2: :perler: i emoji-liste")

# ── 3) Render PerlerMark i picker-flisen ──
sub("{em === ':sos:' ? <SoSLogoMark size={20}/> : em}",
    "{em === ':sos:' ? <SoSLogoMark size={20}/> : em === ':perler:' ? <PerlerMark size={20}/> : em}",
    "3: picker-flise PerlerMark")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

# CRLF-fix
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

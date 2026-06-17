import sys, io, re
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

# ── 1) Udvid emoji-listen (regex så vi ikke skal matche emoji-bytes) ──
NEW_EMOJIS = ("const SOS_EMOJIS = ["
  "'🙂','😊','😀','😄','😁','😉','😍','🥰','😎','🤔','😅','😢','😭',"
  "'👍','👏','🙌','💪','🤝','👌','🙏','👋','🤗',"
  "'❤️','✅','✨','🔥','💯','🎉','📅','📍','⏰','☀️','🌿','💬',"
  "':sos:'];")
c2, n = re.subn(r"const SOS_EMOJIS = \[[^\]]*\];", NEW_EMOJIS, c, count=1)
if n == 1:
    c = c2; ok.append("1: udvidet emoji-liste (35 inkl. logo)")
else:
    fail.append("1: emoji-liste regex")

# ── 2) Indsæt SoSLogoMark (rigtig 3-personers logo) før renderChatText ──
LOGO = """const SoSLogoMark = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"
    aria-label="Social Sundhed" style={{ display: 'block', flexShrink: 0 }}>
    <circle cx="256" cy="256" r="256" fill="#E5792E"/>
    <circle cx="164" cy="188" r="30" fill="#fff"/>
    <circle cx="256" cy="182" r="30" fill="#fff"/>
    <circle cx="348" cy="188" r="30" fill="#fff"/>
    <g fill="none" stroke="#fff" strokeWidth="20" strokeLinecap="round" strokeLinejoin="round">
      <path d="M92 360 C 124 270 148 256 164 256 C 196 256 200 226 214 226 C 234 226 238 256 256 256 C 274 256 278 226 298 226 C 312 226 316 256 348 256 C 364 256 388 270 420 360"/>
      <path d="M164 256 L164 366"/>
      <path d="M256 256 L256 374"/>
      <path d="M348 256 L348 366"/>
    </g>
  </svg>
);

"""
sub("const renderChatText = (tekst, size) => {",
    LOGO + "const renderChatText = (tekst, size) => {",
    "2: indsæt SoSLogoMark")

# ── 3) Brug SoSLogoMark i inline-rendering af :sos: ──
sub("        <SSLogo size={size || 16}/>",
    "        <SoSLogoMark size={size || 16}/>",
    "3: renderChatText bruger SoSLogoMark")

# ── 4) Brug SoSLogoMark i picker-flisen ──
sub("{em === ':sos:' ? <SSLogo size={20}/> : em}",
    "{em === ':sos:' ? <SoSLogoMark size={20}/> : em}",
    "4: picker-flise bruger SoSLogoMark")

# ── 5) Scroll i popover (35 ikoner) ──
sub("boxShadow: '0 8px 30px rgba(0,0,0,0.15)', padding: 8, width: 210,",
    "boxShadow: '0 8px 30px rgba(0,0,0,0.15)', padding: 8, width: 210, maxHeight: 250, overflowY: 'auto',",
    "5: popover scroll")

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

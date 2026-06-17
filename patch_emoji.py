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

# ── EmojiPicker + renderChatText (indsættes efter SSLogo) ──
BLOCK = r'''
// ── Emoji/ikon-vælger til chat + inline SoS-logo via :sos: ───────────────────
const SOS_EMOJIS = ['🙂','😊','👍','🙏','❤️','✅','📅','📍','⏰','☀️','🌿','💬','🎉','👋',':sos:'];

const renderChatText = (tekst, size) => {
  if (!tekst || String(tekst).indexOf(':sos:') === -1) return tekst;
  const parts = String(tekst).split(':sos:');
  const out = [];
  parts.forEach((p, i) => {
    if (p) out.push(p);
    if (i < parts.length - 1) out.push(
      <span key={'sos' + i} style={{ display: 'inline-flex', verticalAlign: 'middle', margin: '0 1px' }}>
        <SSLogo size={size || 16}/>
      </span>
    );
  });
  return out;
};

const EmojiPicker = ({ onPick }) => {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={{ position: 'relative', flexShrink: 0, alignSelf: 'flex-end' }}>
      <button type="button" aria-label="Indsæt emoji eller ikon" onClick={() => setOpen(o => !o)}
        style={{ width: 38, height: 38, borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,
          background: SoS.surface, cursor: 'pointer', fontSize: 18, lineHeight: 1,
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🙂</button>
      {open && (
        <>
          <div onClick={() => setOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 60 }}/>
          <div style={{ position: 'absolute', bottom: 46, right: 0, zIndex: 61,
            background: '#fff', border: `1px solid ${SoS.line}`, borderRadius: SoS.r.md,
            boxShadow: '0 8px 30px rgba(0,0,0,0.15)', padding: 8, width: 210,
            display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 4 }}>
            {SOS_EMOJIS.map(em => (
              <button key={em} type="button" title={em === ':sos:' ? 'Social Sundhed-logo' : em}
                onClick={() => { onPick(em); setOpen(false); }}
                onMouseEnter={e => e.currentTarget.style.background = SoS.surface}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                style={{ height: 34, border: 'none', background: 'transparent', cursor: 'pointer',
                  fontSize: 20, lineHeight: 1, borderRadius: SoS.r.sm,
                  display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {em === ':sos:' ? <SSLogo size={20}/> : em}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

'''

# 1) Indsæt blok efter SSLogo
sub(
    "      fill=\"#ffffff\"\n    />\n  </svg>\n);\n\n// Avatar — initials in colored circle",
    "      fill=\"#ffffff\"\n    />\n  </svg>\n);\n" + BLOCK + "\n// Avatar — initials in colored circle",
    "1: indsæt EmojiPicker + renderChatText")

# 2) DesktopBeskeder — render :sos: i boblen
sub("                      {msg.tekst}\n                    </div>",
    "                      {renderChatText(msg.tekst, 16)}\n                    </div>",
    "2: DesktopBeskeder bobletekst")

# 3) DesktopBeskeder — EmojiPicker i input
sub(
    "                background: SoS.surface }}\n            />\n            <button onClick={sendBesked} disabled={!tekst.trim()}",
    "                background: SoS.surface }}\n            />\n            <EmojiPicker onPick={em => setTekst(t => t + em)}/>\n            <button onClick={sendBesked} disabled={!tekst.trim()}",
    "3: DesktopBeskeder emoji-knap")

# 4) MessagesList (brobygger) — render :sos: i boblen
sub("            }}>{m.tekst}</div>",
    "            }}>{renderChatText(m.tekst, 15)}</div>",
    "4: MessagesList bobletekst")

# 5) MessagesList — EmojiPicker i input
sub(
    "          />\n          <button\n            onClick={sendBbBesked}",
    "          />\n          <EmojiPicker onPick={em => setBbTekst(t => t + em)}/>\n          <button\n            onClick={sendBbBesked}",
    "5: MessagesList emoji-knap")

# 6) Forløb-chat (DesktopMenneskeDetailPanel) — render :sos: i boblen
sub("                            {msg.tekst}\n                          </div>",
    "                            {renderChatText(msg.tekst, 14)}\n                          </div>",
    "6: forløb-chat bobletekst")

# 7) Forløb-chat — EmojiPicker i input
sub(
    "                      lineHeight: 1.45 }}/>\n                  <button onClick={sendBeskedFraForloeb}",
    "                      lineHeight: 1.45 }}/>\n                  <EmojiPicker onPick={em => setBeskedTekst(t => t + em)}/>\n                  <button onClick={sendBeskedFraForloeb}",
    "7: forløb-chat emoji-knap")

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

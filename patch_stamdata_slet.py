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

# 1) sletIdx-state
sub(
    "  const [editIdx, setEditIdx] = React.useState(-1);\n"
    "  const [editVal, setEditVal] = React.useState('');",
    "  const [editIdx, setEditIdx] = React.useState(-1);\n"
    "  const [editVal, setEditVal] = React.useState('');\n"
    "  const [sletIdx, setSletIdx] = React.useState(-1);",
    "1: sletIdx state")

# 2) slet + bedSlet
sub(
    "  const slet = (i) => { liste.splice(i, 1); gem(); };",
    "  const slet = (i) => { liste.splice(i, 1); setSletIdx(-1); gem(); };\n"
    "  const bedSlet = (i, brug) => { if (brug > 0) setSletIdx(i); else slet(i); };",
    "2: bedSlet")

# 3) Slet-knap → bedSlet
sub(
    "                      <button onClick={() => slet(i)} style={{ padding: '5px 10px', background: 'none',\n"
    "                        border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                        fontFamily: SoS.sans, fontSize: 12, color: SoS.rose }}>Slet</button>",
    "                      <button onClick={() => bedSlet(i, brug)} style={{ padding: '5px 10px', background: 'none',\n"
    "                        border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                        fontFamily: SoS.sans, fontSize: 12, color: SoS.rose }}>Slet</button>",
    "3: slet-knap")

# 4) Slet-bekræftelse (efter omdøb-advarslen)
sub(
    "                    ⚠ Ændrer {brug} allerede noteret{brug === 1 ? '' : 'e'} registrering{brug === 1 ? '' : 'er'}. Gør det kun, hvis posten stadig giver mening bagefter — ellers mister de gamle data deres betydning.\n"
    "                  </div>\n"
    "                )}\n"
    "              </div>",
    "                    ⚠ Ændrer {brug} allerede noteret{brug === 1 ? '' : 'e'} registrering{brug === 1 ? '' : 'er'}. Gør det kun, hvis posten stadig giver mening bagefter — ellers mister de gamle data deres betydning.\n"
    "                  </div>\n"
    "                )}\n"
    "                {sletIdx === i && (\n"
    "                  <div style={{ marginTop: 8, marginLeft: 32, padding: '10px 12px',\n"
    "                    background: SoS.rose + '12', border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm }}>\n"
    "                    <div style={{ fontFamily: SoS.sans, fontSize: 11.5, color: '#9A2A2A', lineHeight: 1.45, marginBottom: 8 }}>\n"
    "                      ⚠ \"{navn}\" bruges i {brug} registrering{brug === 1 ? '' : 'er'}. Sletter du, beholder de gamle registreringer værdien, men den kan ikke længere vælges fremover — gør det kun, hvis det stadig giver mening.\n"
    "                    </div>\n"
    "                    <div style={{ display: 'flex', gap: 8 }}>\n"
    "                      <button onClick={() => slet(i)} style={{ padding: '5px 12px', background: SoS.rose,\n"
    "                        color: '#fff', border: 'none', borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                        fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>Slet alligevel</button>\n"
    "                      <button onClick={() => setSletIdx(-1)} style={{ padding: '5px 12px', background: 'none',\n"
    "                        border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                        fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Behold</button>\n"
    "                    </div>\n"
    "                  </div>\n"
    "                )}\n"
    "              </div>",
    "4: slet-bekræftelse")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

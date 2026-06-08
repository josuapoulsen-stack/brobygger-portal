import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

OPKALD = (
    "          {(() => {\n"
    "            const logs = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]')\n"
    "              .filter(l => l.navn && l.navn !== 'Ukendt' && (\n"
    "                l.navn.toLowerCase().includes((m.firstName || '').toLowerCase()) ||\n"
    "                l.navn.toLowerCase().includes((m.lastName || '').toLowerCase())));\n"
    "            if (logs.length === 0) return null;\n"
    "            return (\n"
    "              <div style={{ marginTop: 14 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,\n"
    "                  color: SoS.inkMuted, letterSpacing: 0.9,\n"
    "                  textTransform: 'uppercase', marginBottom: 8 }}>Loggede opkald</div>\n"
    "                {logs.map((l, i) => (\n"
    "                  <div key={l.id} style={{ display: 'flex', gap: 10,\n"
    "                    padding: '8px 0',\n"
    "                    borderTop: i > 0 ? `1px solid ${SoS.lineSoft}` : 'none' }}>\n"
    "                    <div style={{ fontFamily: SoS.mono, fontSize: 10,\n"
    "                      color: SoS.inkMuted, flexShrink: 0, width: 74 }}>\n"
    "                      {l.dato}\n"
    "                    </div>\n"
    "                    <div style={{ flex: 1 }}>\n"
    "                      <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                        fontWeight: 600, color: SoS.ink }}>{l.navn}</div>\n"
    "                      <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                        color: SoS.inkSoft, marginTop: 2, lineHeight: 1.4 }}>{l.note}</div>\n"
    "                    </div>\n"
    "                  </div>\n"
    "                ))}\n"
    "              </div>\n"
    "            );\n"
    "          })()}\n"
)

old = (
    "        {activeTab === 1 && (\n"
    "        <div style={{ padding: '16px 16px 24px' }}>\n"
    "          <MenneskeTimelineInline m={m} />\n"
    "        </div>\n"
    "      )}"
)
new = (
    "        {activeTab === 1 && (\n"
    "        <div style={{ padding: '16px 16px 24px' }}>\n"
    "          <MenneskeTimelineInline m={m} />\n"
    + OPKALD +
    "        </div>\n"
    "      )}"
)

if old in c:
    c = c.replace(old, new, 1)
    print('D2: OK')
else:
    print('D2: FAIL - not found')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Written.')

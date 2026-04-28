# -*- coding: utf-8 -*-
"""
patch_acubiz_link.py
Tilføjer en diskret Acubiz-genvej nederst på brobyggerens hjemskærm.
Klik forsøger at åbne appen (acubiz://), med 1.5 s fallback til App Store / Google Play.
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# Indsæt Acubiz-kortet lige FØR afslutningen af HomeScreen (før </> og };)
OLD_HOME_END = (
    "      <div style={{ padding: '0 20px 20px' }}>\n"
    "        <SectionHead title=\"Brobygningstyper\" />\n"
    "        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>\n"
    "          {Object.values(SoS_TYPER).map(t => (\n"
    "            <div key={t.id} style={{\n"
    "              display: 'flex', alignItems: 'center', gap: 14,\n"
    "              padding: 14, background: '#fff', borderRadius: SoS.r.md,\n"
    "              border: `1px solid ${SoS.lineSoft}`,\n"
    "            }}>\n"
    "              <div style={{ width: 40, height: 40, borderRadius: 20,\n"
    "                background: t.soft, display: 'flex',\n"
    "                alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>\n"
    "                <Icon name={t.icon} size={20} color={t.color} />\n"
    "              </div>\n"
    "              <div style={{ flex: 1, minWidth: 0 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,\n"
    "                  color: SoS.ink }}>{t.label}</div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,\n"
    "                  lineHeight: 1.3, marginTop: 2 }}>{t.desc}</div>\n"
    "              </div>\n"
    "            </div>\n"
    "          ))}\n"
    "        </div>\n"
    "      </div>\n"
    "    </>\n"
    "  );\n"
    "};"
)

ACUBIZ_CARD = (
    "      {/* Acubiz-genvej \u2014 diskret \u00f8verste bilagsapp */}\n"
    "      {(() => {\n"
    "        const openAcubiz = () => {\n"
    "          // Fors\u00f8g at \u00e5bne appen via URL-scheme\n"
    "          const appUrl = 'acubiz://';\n"
    "          const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent);\n"
    "          const store = ios\n"
    "            ? 'https://apps.apple.com/dk/search?term=acubiz'\n"
    "            : 'https://play.google.com/store/search?q=acubiz&c=apps';\n"
    "          window.location.href = appUrl;\n"
    "          // Fallback: hvis appen ikke er installeret, g\u00e5 til store\n"
    "          setTimeout(() => { window.location.href = store; }, 1500);\n"
    "        };\n"
    "        return (\n"
    "          <div style={{ padding: '0 20px 8px' }}>\n"
    "            <button onClick={openAcubiz} style={{\n"
    "              width: '100%', display: 'flex', alignItems: 'center', gap: 12,\n"
    "              padding: '11px 14px', background: '#fff',\n"
    "              border: `1px solid ${SoS.lineSoft}`,\n"
    "              borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',\n"
    "            }}>\n"
    "              {/* Acubiz-ikon: simpel kvitterings-silhouet */}\n"
    "              <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0,\n"
    "                background: '#EAF1FB',\n"
    "                display: 'flex', alignItems: 'center', justifyContent: 'center' }}>\n"
    "                <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                  stroke=\"#3A6DB5\" strokeWidth=\"1.8\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                  <path d=\"M5 4h10l4 4v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z\"/>\n"
    "                  <path d=\"M15 4v5h4\"/>\n"
    "                  <path d=\"M8 13h8M8 17h5\"/>\n"
    "                </svg>\n"
    "              </div>\n"
    "              <div style={{ flex: 1, minWidth: 0 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n"
    "                  color: SoS.ink }}>Acubiz</div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                  color: SoS.inkMuted, marginTop: 1 }}>Kvitteringer og k\u00f8rsels\u00f8konomisk registrering</div>\n"
    "              </div>\n"
    "              <svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                stroke={SoS.inkMuted} strokeWidth=\"1.8\" strokeLinecap=\"round\">\n"
    "                <path d=\"M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6\"/>\n"
    "                <path d=\"M15 3h6v6M10 14L21 3\"/>\n"
    "              </svg>\n"
    "            </button>\n"
    "          </div>\n"
    "        );\n"
    "      })()}\n"
    "\n"
    "      <div style={{ padding: '0 20px 20px' }}>\n"
    "        <SectionHead title=\"Brobygningstyper\" />\n"
    "        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>\n"
    "          {Object.values(SoS_TYPER).map(t => (\n"
    "            <div key={t.id} style={{\n"
    "              display: 'flex', alignItems: 'center', gap: 14,\n"
    "              padding: 14, background: '#fff', borderRadius: SoS.r.md,\n"
    "              border: `1px solid ${SoS.lineSoft}`,\n"
    "            }}>\n"
    "              <div style={{ width: 40, height: 40, borderRadius: 20,\n"
    "                background: t.soft, display: 'flex',\n"
    "                alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>\n"
    "                <Icon name={t.icon} size={20} color={t.color} />\n"
    "              </div>\n"
    "              <div style={{ flex: 1, minWidth: 0 }}>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,\n"
    "                  color: SoS.ink }}>{t.label}</div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,\n"
    "                  lineHeight: 1.3, marginTop: 2 }}>{t.desc}</div>\n"
    "              </div>\n"
    "            </div>\n"
    "          ))}\n"
    "        </div>\n"
    "      </div>\n"
    "    </>\n"
    "  );\n"
    "};"
)

cnt = html.count(OLD_HOME_END)
html = html.replace(OLD_HOME_END, ACUBIZ_CARD, 1)
results.append(('Acubiz-genvej på HomeScreen', cnt, 1))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

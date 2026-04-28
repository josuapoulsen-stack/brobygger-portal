"""
patch_sroi_rapport.py

1. AdminSettings: adds "SROI-parametre" section (isAdmin only)
   - Editable kr/mde for Sundhed, Forening, Social brobygning
   - Editable annual investment figure
   - Saves to window.SROI_SETTINGS for downstream use

2. AdminRapportScreen: converts to stateful, download buttons show feedback toast

3. DesktopRapport: wires "Abn" buttons to open ExportReport
"""
import sys

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. AdminSettings: add SROI state + section + menu entry
# ─────────────────────────────────────────────────────────────────────────────

# Add sroiRates state
OLD_STATE = "  const [bbSent, setBbSent] = React.useState(false);\n  const [staffInvite, setStaffInvite] = React.useState({ name: '', email: '', role: 'raadgiver' });\n  const [staffSent, setStaffSent] = React.useState(false);"
NEW_STATE = "  const [bbSent, setBbSent] = React.useState(false);\n  const [staffInvite, setStaffInvite] = React.useState({ name: '', email: '', role: 'raadgiver' });\n  const [staffSent, setStaffSent] = React.useState(false);\n  const [sroiRates, setSroiRates] = React.useState(\n    window.SROI_SETTINGS || { sundhed: 1840, forening: 1420, social: 1260, investment: 8400000 }\n  );\n  const [sroiSaved, setSroiSaved] = React.useState(false);\n  const saveSROI = () => {\n    window.SROI_SETTINGS = { ...sroiRates };\n    setSroiSaved(true); setTimeout(() => setSroiSaved(false), 1500);\n  };"

if OLD_STATE not in html:
    sys.exit('ERROR: AdminSettings state anchor not found')
html = html.replace(OLD_STATE, NEW_STATE, 1)
print('[OK] sroiRates state added to AdminSettings')

# Add sroi to SECTIONS list (after invite-bb)
OLD_SECTIONS_END = "    { id: 'invite-bb', icon: 'user',     label: 'Inviter brobygger',      sub: 'Send invitationslink', show: true },\n  ];"
NEW_SECTIONS_END = "    { id: 'invite-bb', icon: 'user',     label: 'Inviter brobygger',      sub: 'Send invitationslink', show: true },\n    { id: 'sroi',      icon: 'sparkle',  label: 'SROI-parametre',         sub: `${sroiRates.sundhed} / ${sroiRates.forening} / ${sroiRates.social} kr/mde`, show: isAdmin },\n  ];"
if OLD_SECTIONS_END not in html:
    sys.exit('ERROR: SECTIONS end anchor not found')
html = html.replace(OLD_SECTIONS_END, NEW_SECTIONS_END, 1)
print('[OK] SROI section added to AdminSettings menu')

# Add sroi to TITLES
OLD_TITLES = "  const TITLES = {\n    hq: 'Hoveeds\u00e6de', data: 'Databeskyttelse', lifecycle: 'Brobygger-livscyklus',\n    staff: 'Medarbejdere & roller', 'invite-bb': 'Inviter brobygger',\n  };"

# Let's find the exact TITLES block
import re
m = re.search(r"const TITLES = \{[^}]+\};", html)
if not m:
    print('[WARN] TITLES block not found by regex, trying literal')
    OLD_TITLES2 = "    hq: 'Hoveeds"
    if OLD_TITLES2 in html:
        print('[WARN] found variant with typo')
else:
    old_titles_text = m.group(0)
    # Add sroi to TITLES
    new_titles_text = old_titles_text.replace(
        "'invite-bb': 'Inviter brobygger',",
        "'invite-bb': 'Inviter brobygger', sroi: 'SROI-parametre',"
    )
    if new_titles_text != old_titles_text:
        html = html.replace(old_titles_text, new_titles_text, 1)
        print('[OK] TITLES updated with sroi')
    else:
        print('[WARN] invite-bb not found in TITLES')

# Add SROI section UI — insert before the closing of the Body div
# Find the staff section and add after it
SROI_SECTION_ANCHOR = "      </div>\n    </div>\n  );\n};\n\nwindow.AdminSettings"

SROI_SECTION_UI = """
        {/* SROI-parametre */}
        {section === 'sroi' && isAdmin && (<>
          <div style={{ padding: '10px 0 16px' }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.6, marginBottom: 16 }}>
              Disse v\u00e6rdier bruges til SROI-beregning i rapporter.
              Baseret p\u00e5 Ramb\u00f8ll SROI-guide for civilsamfund.
            </div>
          </div>

          <SectionHead title="Ansl\u00e5et social v\u00e6rdi pr. afd." />
          <NumStepper label="Sundhedsbrobygning" sublabel="Undg\u00e5et indl\u00e6ggelse / bedre sundhed" unit="kr/afd."
            value={sroiRates.sundhed} min={500} max={5000}
            onChange={v => setSroiRates(r => ({ ...r, sundhed: v }))} />
          <NumStepper label="Foreningsbrobygning" sublabel="\u00d8get tilknytning til f\u00e6llesskab" unit="kr/afd."
            value={sroiRates.forening} min={500} max={5000}
            onChange={v => setSroiRates(r => ({ ...r, forening: v }))} />
          <NumStepper label="Socialbrobygning" sublabel="Mindsket ensomhed / \u00f8get livskvalitet" unit="kr/afd."
            value={sroiRates.social} min={500} max={5000}
            onChange={v => setSroiRates(r => ({ ...r, social: v }))} />

          <SectionHead title="\u00c5rlig investering (drift)" />
          <NumStepper label="Investering i alt" sublabel="L\u00f8nninger, lokaler, administration" unit="tkr"
            value={Math.round(sroiRates.investment / 1000)} min={1000} max={50000}
            onChange={v => setSroiRates(r => ({ ...r, investment: v * 1000 }))} />

          {/* Calculated preview */}
          <div style={{ marginTop: 16, padding: 16, background: '#fff',
            borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}` }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
              Beregnet SROI (YTD)
            </div>
            {(() => {
              const ytd = { sundhed: 521, forening: 702, social: 911 };
              const total = ytd.sundhed * sroiRates.sundhed + ytd.forening * sroiRates.forening + ytd.social * sroiRates.social;
              const ratio = (total / sroiRates.investment).toFixed(2);
              return (<>
                <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
                  color: SoS.orange, marginBottom: 4 }}>
                  {(total / 1_000_000).toFixed(1).replace('.', ',')} mio. kr
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
                  1:{ratio} &mdash; for hver krone investeret skabes {ratio} kr social v\u00e6rdi
                </div>
              </>);
            })()}
          </div>

          <div style={{ marginTop: 16 }}>
            <Button full onClick={saveSROI}>
              {sroiSaved ? '\u2713 Gemt' : 'Gem SROI-indstillinger'}
            </Button>
          </div>
        </>)}

"""

if SROI_SECTION_ANCHOR not in html:
    # Try to find a close match
    idx = html.rfind('window.AdminSettings')
    if idx < 0:
        sys.exit('ERROR: AdminSettings closing anchor not found')
    # Find the end of AdminSettings body
    close = html.rfind('      </div>\n    </div>\n  );\n};', 0, idx)
    if close < 0:
        sys.exit('ERROR: AdminSettings body close not found')
    anchor = html[close:close+len(SROI_SECTION_ANCHOR)]
    html = html[:close] + SROI_SECTION_UI + html[close:]
    print('[OK] SROI section UI inserted (fallback method)')
else:
    html = html.replace(SROI_SECTION_ANCHOR, SROI_SECTION_UI + SROI_SECTION_ANCHOR, 1)
    print('[OK] SROI section UI inserted')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Convert AdminRapportScreen to stateful + download feedback
# ─────────────────────────────────────────────────────────────────────────────
OLD_RAPPORT = 'const AdminRapportScreen = () => (\n  <>'
NEW_RAPPORT_HEADER = (
    'const AdminRapportScreen = () => {\n'
    '  const [downloading, setDownloading] = React.useState(null);\n'
    '  const [showExport, setShowExport] = React.useState(false);\n'
    '  const handleDownload = (name) => {\n'
    '    setDownloading(name);\n'
    '    setTimeout(() => setDownloading(null), 2000);\n'
    '  };\n'
    '  return (\n'
    '  <>'
)

if OLD_RAPPORT not in html:
    sys.exit('ERROR: AdminRapportScreen opener not found')
html = html.replace(OLD_RAPPORT, NEW_RAPPORT_HEADER, 1)
print('[OK] AdminRapportScreen converted to stateful')

# Fix closing — change from ); to ); };
# Find the closing of AdminRapportScreen
idx_rapport = html.index('const AdminRapportScreen = () => {')
idx_after = html.index('\nconst KONTAKT_TYPER', idx_rapport)
# Find the ); just before KONTAKT_TYPER
close_idx = html.rfind('\n);', idx_rapport, idx_after)
if close_idx < 0:
    print('[WARN] Could not find AdminRapportScreen closing );')
else:
    html = html[:close_idx] + '\n  );\n}' + html[close_idx+3:]
    print('[OK] AdminRapportScreen closing fixed')

# Wire download buttons — replace the static download button with stateful one
OLD_DL_BTN = (
    '          <button style={{ background: SoS.cream, border: \'none\', borderRadius: 18,\n'
    '            width: 36, height: 36, display: \'flex\', alignItems: \'center\',\n'
    '            justifyContent: \'center\', cursor: \'pointer\' }}>\n'
    '            <Icon name="download" size={16} color={SoS.orange} />\n'
    '          </button>'
)
NEW_DL_BTN = (
    '          <button onClick={() => handleDownload(r.name)}\n'
    '            style={{ background: downloading === r.name ? SoS.sageSoft : SoS.cream,\n'
    '              border: \'none\', borderRadius: 18,\n'
    '              width: 36, height: 36, display: \'flex\', alignItems: \'center\',\n'
    '              justifyContent: \'center\', cursor: \'pointer\',\n'
    '              transition: \'background 0.2s\' }}>\n'
    '            <Icon name={downloading === r.name ? "check" : "download"} size={16}\n'
    '              color={downloading === r.name ? SoS.sage : SoS.orange} />\n'
    '          </button>'
)
if OLD_DL_BTN in html:
    html = html.replace(OLD_DL_BTN, NEW_DL_BTN, 1)
    print('[OK] Download button wired with feedback')
else:
    print('[WARN] Download button not found')

# Wire "Hurtige eksporter" buttons — replace static div with clickable button
OLD_QUICK_EXPORT = (
    '          <div key={i} style={{\n'
    '            background: \'#fff\', borderRadius: SoS.r.md, padding: 14,\n'
    '            border: `1px solid ${SoS.lineSoft}`, cursor: \'pointer\',\n'
    '          }}>\n'
    '            <Icon name={x.icon} size={22} color={SoS.orange} />\n'
    '            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n'
    '              color: SoS.ink, marginTop: 10 }}>{x.label}</div>\n'
    '            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>\n'
    '              {x.desc}\n'
    '            </div>\n'
    '          </div>'
)
NEW_QUICK_EXPORT = (
    '          <button key={i} onClick={() => x.label === \'Fondsans\u00f8gning\' ? setShowExport(true) : handleDownload(x.label)}\n'
    '            style={{\n'
    '              background: downloading === x.label ? SoS.sageSoft : \'#fff\',\n'
    '              borderRadius: SoS.r.md, padding: 14, border: \'none\',\n'
    '              borderBottom: `1px solid ${SoS.lineSoft}`, cursor: \'pointer\',\n'
    '              textAlign: \'left\', transition: \'background 0.2s\' }}>\n'
    '            <Icon name={downloading === x.label ? "check" : x.icon} size={22}\n'
    '              color={downloading === x.label ? SoS.sage : SoS.orange} />\n'
    '            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n'
    '              color: SoS.ink, marginTop: 10 }}>{x.label}</div>\n'
    '            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>\n'
    '              {downloading === x.label ? \'Hentes...\' : x.desc}\n'
    '            </div>\n'
    '          </button>'
)
if OLD_QUICK_EXPORT in html:
    html = html.replace(OLD_QUICK_EXPORT, NEW_QUICK_EXPORT, 1)
    print('[OK] Quick export buttons wired')
else:
    print('[WARN] Quick export button block not found')

# Add ExportReport overlay to AdminRapportScreen (before closing return tag)
# Find the closing </> of AdminRapportScreen
RAPPORT_RETURN_END = '  </>\n  );\n};\n\nconst KONTAKT_TYPER'
RAPPORT_RETURN_WITH_EXPORT = (
    '  </>\n'
    '  );\n'
    '};\n'
    '\n'
    'const KONTAKT_TYPER'
)
# Actually just inject before </> close
OLD_RAPPORT_CLOSE = '  </>\n  );\n};\n\nconst KONTAKT_TYPER'
NEW_RAPPORT_CLOSE = (
    '    {showExport && <ExportReport onClose={() => setShowExport(false)}/>}\n'
    '  </>\n'
    '  );\n'
    '};\n'
    '\n'
    'const KONTAKT_TYPER'
)
if OLD_RAPPORT_CLOSE in html:
    html = html.replace(OLD_RAPPORT_CLOSE, NEW_RAPPORT_CLOSE, 1)
    print('[OK] ExportReport overlay added to AdminRapportScreen')
else:
    print('[WARN] AdminRapportScreen closing not found for overlay injection')

# ─────────────────────────────────────────────────────────────────────────────
# 3. DesktopRapport: convert to stateful + wire Abn buttons to ExportReport
# ─────────────────────────────────────────────────────────────────────────────
OLD_DESKTOP_RAPPORT = 'const DesktopRapport = () => (\n  <>'
NEW_DESKTOP_RAPPORT = (
    'const DesktopRapport = () => {\n'
    '  const [showExport, setShowExport] = React.useState(false);\n'
    '  const [downloading, setDownloading] = React.useState(null);\n'
    '  const handleDownload = (name) => { setDownloading(name); setTimeout(() => setDownloading(null), 2000); };\n'
    '  return (\n'
    '  <>'
)
if OLD_DESKTOP_RAPPORT not in html:
    sys.exit('ERROR: DesktopRapport opener not found')
html = html.replace(OLD_DESKTOP_RAPPORT, NEW_DESKTOP_RAPPORT, 1)
print('[OK] DesktopRapport converted to stateful')

# Fix DesktopRapport closing
idx_dr = html.index('const DesktopRapport = () => {')
idx_after_dr = html.index('\nwindow.DesktopView', idx_dr)
close_dr = html.rfind('\n);', idx_dr, idx_after_dr)
if close_dr >= 0:
    html = html[:close_dr] + '\n  );\n}' + html[close_dr+3:]
    print('[OK] DesktopRapport closing fixed')

# Wire the "Abn" button inside DesktopRapport
OLD_ABN = "          <Button full variant=\"secondary\" style={{ height: 36, fontSize: 13 }}>Åbn</Button>"
NEW_ABN = "          <Button full variant=\"secondary\" style={{ height: 36, fontSize: 13 }} onClick={() => setShowExport(true)}>Åbn</Button>"
if OLD_ABN in html:
    # Replace all 3 occurrences
    html = html.replace(OLD_ABN, NEW_ABN)
    print('[OK] Abn buttons wired to ExportReport')
else:
    print('[WARN] Abn button not found')

# Wire the quick export buttons in DesktopRapport
OLD_DR_QUICK = (
    "          <button key={i} style={{\n"
    "            padding: 16, background: SoS.cream, borderRadius: 10,\n"
    "            border: `1px solid ${SoS.lineSoft}`, cursor: 'pointer',\n"
    "            textAlign: 'left', fontFamily: SoS.sans,\n"
    "          }}>\n"
    "            <Icon name={x.i} size={22} color={SoS.orange}/>\n"
    "            <div style={{ fontSize: 13, fontWeight: 600, color: SoS.ink, marginTop: 10 }}>{x.l}</div>\n"
    "            <div style={{ fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>{x.d}</div>\n"
    "          </button>"
)
NEW_DR_QUICK = (
    "          <button key={i}\n"
    "            onClick={() => x.l === 'SROI komplet' ? setShowExport(true) : handleDownload(x.l)}\n"
    "            style={{\n"
    "              padding: 16, background: downloading === x.l ? SoS.sageSoft : SoS.cream,\n"
    "              borderRadius: 10, border: `1px solid ${SoS.lineSoft}`,\n"
    "              cursor: 'pointer', textAlign: 'left', fontFamily: SoS.sans,\n"
    "              transition: 'background 0.2s',\n"
    "            }}>\n"
    "            <Icon name={downloading === x.l ? 'check' : x.i} size={22}\n"
    "              color={downloading === x.l ? SoS.sage : SoS.orange}/>\n"
    "            <div style={{ fontSize: 13, fontWeight: 600, color: SoS.ink, marginTop: 10 }}>{x.l}</div>\n"
    "            <div style={{ fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>\n"
    "              {downloading === x.l ? 'Hentes...' : x.d}\n"
    "            </div>\n"
    "          </button>"
)
if OLD_DR_QUICK in html:
    html = html.replace(OLD_DR_QUICK, NEW_DR_QUICK, 1)
    print('[OK] DesktopRapport quick export buttons wired')
else:
    print('[WARN] DesktopRapport quick export buttons not found')

# Add ExportReport overlay inside DesktopRapport before closing </>
idx_dr2 = html.index('const DesktopRapport = () => {')
idx_after_dr2 = html.index('\nwindow.DesktopView', idx_dr2)
close_dr2 = html.rfind('  </>\n  );\n}', idx_dr2, idx_after_dr2)
if close_dr2 >= 0:
    html = html[:close_dr2] + '    {showExport && <ExportReport onClose={() => setShowExport(false)}/>}\n  </>\n  );\n}' + html[close_dr2+12:]
    print('[OK] ExportReport overlay added to DesktopRapport')
else:
    print('[WARN] DesktopRapport closing <> not found for overlay')

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] Saved ({len(html.encode("utf-8")):,} bytes)')

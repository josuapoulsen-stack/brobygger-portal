"""
patch_dead_ends_4.py
Fixes remaining dead ends (batch 4):
  1. calcSROI / ExportReport – reads window.SROI_SETTINGS instead of hardcoded rates
  2. ExportReport – "Eksportér" header button, "Del rapport", "Eksportér PDF" wired
  3. DesktopView – top-right "Eksportér" button wired with toast
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ---------------------------------------------------------------------------
# 1. calcSROI – use window.SROI_SETTINGS when available
# ---------------------------------------------------------------------------
OLD = """// Calculate total SROI value
const calcSROI = () => {
  let total = 0;
  Object.entries(REPORT_DATA.byType).forEach(([k, v]) => {
    total += v.completed * SROI_RATES[k].perMeeting;
  });
  return total;
};"""
NEW = """// Calculate total SROI value (uses window.SROI_SETTINGS if admin has saved custom rates)
const calcSROI = () => {
  const custom = window.SROI_SETTINGS;
  let total = 0;
  Object.entries(REPORT_DATA.byType).forEach(([k, v]) => {
    const rate = custom ? (custom[k] || SROI_RATES[k].perMeeting) : SROI_RATES[k].perMeeting;
    total += v.completed * rate;
  });
  return total;
};"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('calcSROI reads SROI_SETTINGS', cnt, html.count(NEW)))

# ---------------------------------------------------------------------------
# 2. ExportReport – add exported/shared state + use SROI_SETTINGS investment
# ---------------------------------------------------------------------------

# 2a. Add exported/shared state
OLD = """  const sroiTotal = calcSROI();
  const investment = 8_400_000; // mocked annual operating cost
  const ratio = (sroiTotal / investment).toFixed(2);"""
NEW = """  const sroiTotal = calcSROI();
  const investment = (window.SROI_SETTINGS && window.SROI_SETTINGS.investment) || 8_400_000;
  const ratio = (sroiTotal / investment).toFixed(2);
  const [exported, setExported] = React.useState(false);
  const [shared, setShared] = React.useState(false);
  const handleExport = () => { setExported(true); setTimeout(() => setExported(false), 2500); };
  const handleShare  = () => { setShared(true);   setTimeout(() => setShared(false),  2500); };"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('ExportReport: state + investment from SROI_SETTINGS', cnt, html.count(NEW)))

# 2b. Wire header "Eksportér" button (the one in the dark topbar)
OLD = """          <button style={{ background: SoS.orange, color: '#fff',
            border: 'none', padding: '6px 14px', borderRadius: 999, cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 4,
          }}>
            <Icon name="download" size={14} color="#fff" weight={2.3}/> Eksportér
          </button>"""
NEW = """          <button onClick={handleExport} style={{ background: exported ? SoS.sage : SoS.orange, color: '#fff',
            border: 'none', padding: '6px 14px', borderRadius: 999, cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 4, transition: 'background 0.2s',
          }}>
            <Icon name={exported ? 'check' : 'download'} size={14} color="#fff" weight={2.3}/>
            {exported ? 'Sendt!' : 'Eksportér'}
          </button>"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('ExportReport: header Eksporter button wired', cnt, html.count(NEW)))

# 2c. Wire "Del rapport" and "Eksportér PDF" buttons in preview tab
OLD = """            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <Button variant="secondary" style={{ flex: 1 }}>
                Del rapport
              </Button>
              <Button style={{ flex: 1 }} icon={<Icon name="download" size={16} color="#fff" weight={2.3}/>}>
                Eksportér PDF
              </Button>
            </div>"""
NEW = """            <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
              <Button variant="secondary" style={{ flex: 1 }}
                onClick={handleShare}
                icon={shared ? <Icon name="check" size={16} color={SoS.ink} weight={2.3}/> : undefined}>
                {shared ? 'Delt!' : 'Del rapport'}
              </Button>
              <Button style={{ flex: 1 }} onClick={handleExport}
                icon={<Icon name={exported ? 'check' : 'download'} size={16} color="#fff" weight={2.3}/>}>
                {exported ? 'Eksporteret!' : 'Eksportér PDF'}
              </Button>
            </div>"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('ExportReport: Del rapport + Eksporter PDF wired', cnt, html.count(NEW)))

# ---------------------------------------------------------------------------
# 3. DesktopView – add deskExported state + wire Eksportér button
# ---------------------------------------------------------------------------

# 3a. Add state to DesktopView
OLD = """const DesktopView = ({ user, ownHq, isAdmin, onClose }) => {
  const [section, setSection] = React.useState('dashboard');
  const [viewingHq, setViewingHq] = React.useState(isAdmin ? 'Alle hovedsæder' : ownHq);"""
NEW = """const DesktopView = ({ user, ownHq, isAdmin, onClose }) => {
  const [section, setSection] = React.useState('dashboard');
  const [viewingHq, setViewingHq] = React.useState(isAdmin ? 'Alle hovedsæder' : ownHq);
  const [deskExported, setDeskExported] = React.useState(false);
  const handleDeskExport = () => { setDeskExported(true); setTimeout(() => setDeskExported(false), 2500); };"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('DesktopView: deskExported state added', cnt, html.count(NEW)))

# 3b. Wire the DesktopView Eksportér button
OLD = """              <button style={{ padding: '7px 14px', borderRadius: 999,
                background: SoS.orange, color: '#fff', border: 'none',
                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 6 }}>
                <Icon name="download" size={12} color="#fff" weight={2.3}/> Eksportér
              </button>"""
NEW = """              <button onClick={handleDeskExport} style={{ padding: '7px 14px', borderRadius: 999,
                background: deskExported ? SoS.sage : SoS.orange, color: '#fff', border: 'none',
                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 6, transition: 'background 0.2s' }}>
                <Icon name={deskExported ? 'check' : 'download'} size={12} color="#fff" weight={2.3}/>
                {deskExported ? 'Eksporteret!' : 'Eksportér'}
              </button>"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('DesktopView: Eksporter button wired', cnt, html.count(NEW)))

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] File saved ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]' if before == 1 and after == 1 else f'[WARN] before={before} after={after}'
    print(f'{status}  {label}')

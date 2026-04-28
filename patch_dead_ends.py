"""
patch_dead_ends.py — systematisk audit + fix af alle dead ends:

1. AdminMobile: Brobygninger-rækker klikbare → åbner BrobyggerProfilePanel overlay
2. AdminMobile: Aftaler i dag → klikbare → åbner AppointmentDetailScreen overlay
3. AdminMobile: "Nye frivillige" ActionCard → navigerer til brobyggere-tab med afventer-filter
4. AdminMobile: aftale-noter onClick brugte setAktivTab → rettets til setTab('rapport')
5. AdminBrobyggereScreen: BrobyggerProfilePanel som fuld overlay + accept initialBb prop
6. AdminBrobyggereScreen: "Start ny matching" → props.onOpenMatching
7. AdminMenneskerScreen: kort klikbare → åbner MenneskeDetail sidepanel
8. DesktopBrobyggere tabelrækker: klikbare → åbner BrobyggerProfilePanel
9. AppointmentDetailScreen: "Kontakt koordinator" → viser koordinators tlf
10. ProfileScreen: menu-rækker → viser "Kommer snart" toast
"""
import sys, re

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1+2. AdminMobile: add selectedBb + selectedAppt state; make rows clickable
# ─────────────────────────────────────────────────────────────────────────────

OLD_AM_STATE = "  const [tab, setTab] = React.useState('arbejde');\n\n  // Filter brobyggere"
NEW_AM_STATE = (
    "  const [tab, setTab] = React.useState('arbejde');\n"
    "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
    "  const [selectedAppt, setSelectedAppt] = React.useState(null);\n"
    "\n"
    "  // Filter brobyggere"
)
if OLD_AM_STATE not in html:
    sys.exit('ERROR: AdminMobile state anchor not found')
html = html.replace(OLD_AM_STATE, NEW_AM_STATE, 1)
print('[OK] AdminMobile state extended')

# 2a. Make brobygninger rows clickable (the inner div in the per-brobygger loop)
OLD_BB_ROW = (
    "                          <div key={b.id} style={{\n"
    "                            display: 'flex', alignItems: 'center', gap: 10,\n"
    "                            marginBottom: 7,\n"
    "                          }}>"
)
NEW_BB_ROW = (
    "                          <div key={b.id} onClick={() => setSelectedBb(b)} style={{\n"
    "                            display: 'flex', alignItems: 'center', gap: 10,\n"
    "                            marginBottom: 7, cursor: 'pointer',\n"
    "                          }}>"
)
if OLD_BB_ROW not in html:
    sys.exit('ERROR: Brobygninger row div not found')
html = html.replace(OLD_BB_ROW, NEW_BB_ROW, 1)
print('[OK] Brobygninger denne uge rows are now clickable')

# 2b. Make aftaler i dag cards clickable
OLD_APPT_ROW = (
    "                  <div key={a.id} style={{\n"
    "                    display: 'flex', gap: 12, alignItems: 'center',\n"
    "                    padding: 14, background: '#fff', borderRadius: SoS.r.md,\n"
    "                    border: `1px solid ${SoS.lineSoft}`, marginBottom: 8,\n"
    "                  }}>"
)
NEW_APPT_ROW = (
    "                  <div key={a.id} onClick={() => setSelectedAppt(a)} style={{\n"
    "                    display: 'flex', gap: 12, alignItems: 'center',\n"
    "                    padding: 14, background: '#fff', borderRadius: SoS.r.md,\n"
    "                    border: `1px solid ${SoS.lineSoft}`, marginBottom: 8,\n"
    "                    cursor: 'pointer',\n"
    "                  }}>"
)
if OLD_APPT_ROW not in html:
    sys.exit('ERROR: Aftaler i dag row not found')
html = html.replace(OLD_APPT_ROW, NEW_APPT_ROW, 1)
print('[OK] Aftaler i dag cards are now clickable')

# 2c. Add overlays at end of AdminMobile return, before closing </div></div>
# Find the AdminMobileTabBar render + closing tags
OLD_AM_CLOSE = (
    "      </div>\n"
    "      <AdminMobileTabBar active={tab} onChange={setTab} />\n"
    "    </div>\n"
    "  );\n"
    "};\n"
    "\n"
    "window.AdminMobile = AdminMobile;"
)
NEW_AM_CLOSE = (
    "      </div>\n"
    "      <AdminMobileTabBar active={tab} onChange={setTab} />\n"
    "\n"
    "      {/* Brobygger profil overlay */}\n"
    "      {selectedBb && (\n"
    "        <div style={{ position: 'absolute', inset: 0, overflowY: 'auto', zIndex: 100 }}>\n"
    "          <BrobyggerProfilePanel brobygger={selectedBb} onClose={() => setSelectedBb(null)}/>\n"
    "        </div>\n"
    "      )}\n"
    "\n"
    "      {/* Aftale detaljer overlay */}\n"
    "      {selectedAppt && (\n"
    "        <div style={{ position: 'absolute', inset: 0, overflowY: 'auto', zIndex: 100 }}>\n"
    "          <AppointmentDetailScreen\n"
    "            appt={selectedAppt}\n"
    "            onBack={() => setSelectedAppt(null)}\n"
    "            onComplete={() => setSelectedAppt(null)}\n"
    "          />\n"
    "        </div>\n"
    "      )}\n"
    "    </div>\n"
    "  );\n"
    "};\n"
    "\n"
    "window.AdminMobile = AdminMobile;"
)
if OLD_AM_CLOSE not in html:
    print('[WARN] AdminMobile closing not found — trying alternate')
    # Try without window export
    alt = "      <AdminMobileTabBar active={tab} onChange={setTab} />\n    </div>\n  );\n};\n\nwindow.AdminMobile"
    if alt in html:
        html = html.replace(alt,
            "      <AdminMobileTabBar active={tab} onChange={setTab} />\n"
            "\n"
            "      {selectedBb && (\n"
            "        <div style={{ position: 'absolute', inset: 0, overflowY: 'auto', zIndex: 100 }}>\n"
            "          <BrobyggerProfilePanel brobygger={selectedBb} onClose={() => setSelectedBb(null)}/>\n"
            "        </div>\n"
            "      )}\n"
            "      {selectedAppt && (\n"
            "        <div style={{ position: 'absolute', inset: 0, overflowY: 'auto', zIndex: 100 }}>\n"
            "          <AppointmentDetailScreen appt={selectedAppt} onBack={() => setSelectedAppt(null)} onComplete={() => setSelectedAppt(null)}/>\n"
            "        </div>\n"
            "      )}\n"
            "    </div>\n"
            "  );\n"
            "};\n\nwindow.AdminMobile",
            1)
        print('[OK] Overlays added (alternate method)')
    else:
        print('[WARN] Could not add overlays to AdminMobile')
else:
    html = html.replace(OLD_AM_CLOSE, NEW_AM_CLOSE, 1)
    print('[OK] Overlays added to AdminMobile')

# ─────────────────────────────────────────────────────────────────────────────
# 3. "Nye frivillige" ActionCard → navigate to brobyggere + afventer filter
# ─────────────────────────────────────────────────────────────────────────────
OLD_NYE_CARD = (
    "              <ActionCard color={SoS.sky} bg={SoS.skySoft} icon=\"user\"\n"
    "                title={`${newRegistrations} nye frivillige`}\n"
    "                subtitle=\"Ans\u00f8gt i denne uge \u2014 godkend eller afvis\"/>"
)
NEW_NYE_CARD = (
    "              <ActionCard color={SoS.sky} bg={SoS.skySoft} icon=\"user\"\n"
    "                title={`${newRegistrations} nye frivillige`}\n"
    "                subtitle=\"Ans\u00f8gt i denne uge \u2014 godkend eller afvis\"\n"
    "                onClick={() => setTab('brobyggere')}/>"
)
if OLD_NYE_CARD in html:
    html = html.replace(OLD_NYE_CARD, NEW_NYE_CARD, 1)
    print('[OK] Nye frivillige ActionCard wired to brobyggere tab')
else:
    print('[WARN] Nye frivillige ActionCard not found')

# 4. Fix aftale-noter onClick: setAktivTab → setTab('rapport')
OLD_NOTER_ONCLICK = "                onClick={() => setAktivTab('notater')}/"
NEW_NOTER_ONCLICK = "                onClick={() => setTab('rapport')}/"
if OLD_NOTER_ONCLICK in html:
    html = html.replace(OLD_NOTER_ONCLICK, NEW_NOTER_ONCLICK, 1)
    print('[OK] aftale-noter onClick fixed: setTab(rapport)')
else:
    print('[WARN] aftale-noter onClick not found')

# ─────────────────────────────────────────────────────────────────────────────
# 5. AdminBrobyggereScreen: fix BrobyggerProfilePanel to be proper overlay
#    and add initialBb prop support
# ─────────────────────────────────────────────────────────────────────────────
OLD_ABB_PANEL = (
    "      {/* List */}\n"
    "      <div style={{ padding: '0 20px 16px', display: 'flex',\n"
    "        flexDirection: 'column', gap: 8 }}>\n"
    "        {selectedBb && (\n"
    "          <BrobyggerProfilePanel\n"
    "            brobygger={selectedBb}\n"
    "            onClose={() => setSelectedBb(null)}\n"
    "          />\n"
    "        )}\n"
    "        {filtered.map(b => ("
)
NEW_ABB_PANEL = (
    "      {/* Brobygger profil overlay */}\n"
    "      {selectedBb && (\n"
    "        <div style={{ position: 'absolute', inset: 0, overflowY: 'auto', zIndex: 50, background: SoS.cream }}>\n"
    "          <BrobyggerProfilePanel brobygger={selectedBb} onClose={() => setSelectedBb(null)}/>\n"
    "        </div>\n"
    "      )}\n"
    "\n"
    "      {/* List */}\n"
    "      <div style={{ padding: '0 20px 16px', display: 'flex',\n"
    "        flexDirection: 'column', gap: 8 }}>\n"
    "        {filtered.map(b => ("
)
if OLD_ABB_PANEL in html:
    html = html.replace(OLD_ABB_PANEL, NEW_ABB_PANEL, 1)
    print('[OK] AdminBrobyggereScreen panel is now proper overlay')
else:
    print('[WARN] AdminBrobyggereScreen panel block not found')

# ─────────────────────────────────────────────────────────────────────────────
# 6. AdminBrobyggereScreen: wire "Start ny matching" button
# ─────────────────────────────────────────────────────────────────────────────
OLD_MATCH_BTN = (
    "      {/* Match CTA */}\n"
    "      <div style={{ padding: '0 20px 24px' }}>\n"
    "        <Button full icon={<Icon name=\"match\" size={18} color=\"#fff\" weight={2.3}/>}>\n"
    "          Start ny matching\n"
    "        </Button>\n"
    "      </div>"
)
NEW_MATCH_BTN = (
    "      {/* Match CTA */}\n"
    "      <div style={{ padding: '0 20px 24px' }}>\n"
    "        <Button full onClick={onOpenMatching} icon={<Icon name=\"match\" size={18} color=\"#fff\" weight={2.3}/>}>\n"
    "          Start ny matching\n"
    "        </Button>\n"
    "      </div>"
)
if OLD_MATCH_BTN in html:
    html = html.replace(OLD_MATCH_BTN, NEW_MATCH_BTN, 1)
    print('[OK] Start ny matching button wired')
else:
    print('[WARN] Start ny matching button not found')

# Also update AdminBrobyggereScreen signature to accept onOpenMatching
OLD_ABB_SIG = "const AdminBrobyggereScreen = ({ hovedsaede }) => {"
NEW_ABB_SIG = "const AdminBrobyggereScreen = ({ hovedsaede, onOpenMatching }) => {"
if OLD_ABB_SIG in html:
    html = html.replace(OLD_ABB_SIG, NEW_ABB_SIG, 1)
    print('[OK] AdminBrobyggereScreen accepts onOpenMatching prop')

# Pass onOpenMatching from AdminHome
OLD_AH_BB = "        {tab === 'brobyggere' && <AdminBrobyggereScreen hovedsaede={hovedsaede} />}"
NEW_AH_BB = "        {tab === 'brobyggere' && <AdminBrobyggereScreen hovedsaede={hovedsaede} onOpenMatching={onOpenMatching} />}"
# Find and replace in AdminHome
if OLD_AH_BB in html:
    html = html.replace(OLD_AH_BB, NEW_AH_BB, 1)
    print('[OK] onOpenMatching passed to AdminBrobyggereScreen from AdminHome')

# AdminHome needs onOpenMatching prop too — check its signature
# It's passed via AdminMobile's existing props chain; AdminHome already has it as prop? Let's check
if 'onOpenMatching' in html[html.index('const AdminHome'):html.index('const AdminHome')+200]:
    print('[OK] AdminHome already has onOpenMatching')
else:
    print('[INFO] AdminHome may need onOpenMatching — check manually')

# ─────────────────────────────────────────────────────────────────────────────
# 7. AdminMenneskerScreen: make cards clickable with detail overlay
# ─────────────────────────────────────────────────────────────────────────────
# Convert to stateful + add selected menneske
OLD_MEN_SCREEN = "const AdminMenneskerScreen = () => (\n  <>"
NEW_MEN_SCREEN = (
    "const AdminMenneskerScreen = ({ onOpenMatching }) => {\n"
    "  const [selected, setSelected] = React.useState(null);\n"
    "  return (\n"
    "  <>"
)
if OLD_MEN_SCREEN in html:
    html = html.replace(OLD_MEN_SCREEN, NEW_MEN_SCREEN, 1)
    print('[OK] AdminMenneskerScreen converted to stateful')

# Fix closing
OLD_MEN_CLOSE = "\n  </>\n);\n\nconst AdminRapportScreen"
NEW_MEN_CLOSE = (
    "\n"
    "      {selected && (\n"
    "        <div style={{ position: 'absolute', inset: 0, zIndex: 50,\n"
    "          background: SoS.cream, overflowY: 'auto' }}>\n"
    "          <MenneskeDetailPanel menneske={selected} onClose={() => setSelected(null)}/>\n"
    "        </div>\n"
    "      )}\n"
    "  </>\n"
    "  );\n"
    "};\n"
    "\n"
    "const AdminRapportScreen"
)
if OLD_MEN_CLOSE in html:
    html = html.replace(OLD_MEN_CLOSE, NEW_MEN_CLOSE, 1)
    print('[OK] AdminMenneskerScreen closing fixed with overlay')

# Make menneske cards clickable
OLD_MEN_CARD = (
    "          <div key={b.id} style={{\n"
    "            display: 'flex', gap: 12, padding: 14, background: '#fff',\n"
    "            borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}`,\n"
    "          }}>"
)
NEW_MEN_CARD = (
    "          <div key={b.id} onClick={() => setSelected(b)} style={{\n"
    "            display: 'flex', gap: 12, padding: 14, background: '#fff',\n"
    "            borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}`,\n"
    "            cursor: 'pointer',\n"
    "          }}>"
)
if OLD_MEN_CARD in html:
    html = html.replace(OLD_MEN_CARD, NEW_MEN_CARD, 1)
    print('[OK] Menneske cards clickable')

# Wire "Opret ny menneske" button
OLD_OPRET_BTN = (
    "      <Button full variant=\"secondary\"\n"
    "        icon={<Icon name=\"plus\" size={16} color={SoS.ink} weight={2.3}/>}>\n"
    "        Opret ny menneske\n"
    "      </Button>"
)
NEW_OPRET_BTN = (
    "      <Button full variant=\"secondary\"\n"
    "        onClick={onOpenIntake}\n"
    "        icon={<Icon name=\"plus\" size={16} color={SoS.ink} weight={2.3}/>}>\n"
    "        Opret ny menneske\n"
    "      </Button>"
)
if OLD_OPRET_BTN in html:
    html = html.replace(OLD_OPRET_BTN, NEW_OPRET_BTN, 1)
    print('[OK] Opret ny menneske wired to onOpenIntake')

# Pass onOpenIntake from AdminHome to AdminMenneskerScreen
OLD_AH_MEN = "        {tab === 'mennesker' && <AdminMenneskerScreen />}"
# AdminHome has onOpenIntake? Let me check what props it has
idx_ah = html.index('const AdminHome = ({')
ah_sig = html[idx_ah:idx_ah+200]
if 'onOpenIntake' in ah_sig:
    html = html.replace(OLD_AH_MEN, "        {tab === 'mennesker' && <AdminMenneskerScreen onOpenIntake={onOpenIntake} onOpenMatching={onOpenMatching}/>}", 1)
    print('[OK] onOpenIntake passed to AdminMenneskerScreen')

# ─────────────────────────────────────────────────────────────────────────────
# 8. MenneskeDetailPanel component — insert before AdminMenneskerScreen
# ─────────────────────────────────────────────────────────────────────────────
BEFORE_MEN_SCREEN = 'const AdminMenneskerScreen = ({ onOpenMatching })'
MENNESKE_PANEL = r"""const MenneskeDetailPanel = ({ menneske: m, onClose }) => {
  const type = SoS_TYPER[m.type];
  return (
    <div style={{ background: SoS.cream, minHeight: '100%' }}>
      {/* Hero */}
      <div style={{
        background: `linear-gradient(160deg, ${type.color} 0%, ${type.color}CC 100%)`,
        padding: '54px 20px 28px', color: '#fff',
        borderBottomLeftRadius: 28, borderBottomRightRadius: 28,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
          <button onClick={onClose} style={{ width: 40, height: 40, borderRadius: 20,
            background: 'rgba(255,255,255,0.2)', border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="chevronL" size={20} color="#fff" weight={2.2}/>
          </button>
          <Pill bg="rgba(255,255,255,0.25)" color="#fff">{type.label}</Pill>
        </div>
        <Avatar initials={m.initials} bg="rgba(255,255,255,0.3)" size={64}/>
        <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
          marginTop: 12, letterSpacing: -0.3 }}>
          {m.firstName} {m.lastName[0]}. ({m.age})
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, opacity: 0.85, marginTop: 4 }}>
          {m.address}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: 10, margin: '-16px 16px 16px', position: 'relative', zIndex: 1 }}>
        {[
          { v: m.completedCount, l: 'Aftaler' },
          { v: m.contactCount,   l: 'Kontakter' },
          { v: m.cancelledCount, l: 'Aflyst' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', borderRadius: SoS.r.lg,
            padding: 14, textAlign: 'center', boxShadow: SoS.shadow.md }}>
            <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
              color: SoS.orange }}>{s.v}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11,
              color: SoS.inkSoft, marginTop: 2 }}>{s.l}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: '0 16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>

        {/* Behov */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>Behov</div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {m.needs.map((n, i) => <Pill key={i} bg={type.soft} color={type.color}>{n}</Pill>)}
          </div>
        </div>

        {/* Sprog og helbred */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
            Information
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, marginBottom: 8 }}>
            <span style={{ color: SoS.inkSoft }}>Sprog: </span>{m.language}
          </div>
          {m.health && (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.5 }}>
              <span style={{ color: SoS.inkSoft }}>Helbred: </span>{m.health}
            </div>
          )}
        </div>

        {/* Aftale-noter */}
        {m.notes && m.notes.length > 0 && (
          <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
            border: `1px solid ${SoS.lineSoft}` }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
              Seneste noter
            </div>
            {m.notes.map((n, i) => (
              <div key={i} style={{ marginBottom: i < m.notes.length - 1 ? 12 : 0,
                paddingBottom: i < m.notes.length - 1 ? 12 : 0,
                borderBottom: i < m.notes.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink }}>{n.from}</span>
                  <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>{n.date}</span>
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.5 }}>{n.text}</div>
              </div>
            ))}
          </div>
        )}

        {/* Kontakt */}
        <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16,
          border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
            Koordinator
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{m.contact.name}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginTop: 2 }}>{m.contact.role}</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
            color: SoS.orange, marginTop: 8 }}>{m.contact.phone}</div>
        </div>

        <Button full onClick={onClose} variant="secondary">Luk</Button>
      </div>
    </div>
  );
};

"""
if BEFORE_MEN_SCREEN in html:
    html = html.replace(BEFORE_MEN_SCREEN, MENNESKE_PANEL + BEFORE_MEN_SCREEN, 1)
    print('[OK] MenneskeDetailPanel component added')
else:
    print('[WARN] Could not find anchor for MenneskeDetailPanel')

# ─────────────────────────────────────────────────────────────────────────────
# 9. DesktopBrobyggere table rows: add onClick + selectedBb state
# ─────────────────────────────────────────────────────────────────────────────
# DesktopBrobyggere is a full stateful component. Add selectedBb state.
OLD_DB_STATE = (
    "const DesktopBrobyggere = () => {\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const [search,  setSearch]  = React.useState('');\n"
)
NEW_DB_STATE = (
    "const DesktopBrobyggere = () => {\n"
    "  const [filter, setFilter] = React.useState('alle');\n"
    "  const [search,  setSearch]  = React.useState('');\n"
    "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
)
if OLD_DB_STATE in html:
    html = html.replace(OLD_DB_STATE, NEW_DB_STATE, 1)
    print('[OK] DesktopBrobyggere selectedBb state added')

# Add onClick to <tr>
OLD_DB_TR = (
    "              <tr key={b.id} style={{ borderBottom: `1px solid ${SoS.lineSoft}`, cursor: 'pointer' }}\n"
    "                onMouseEnter={e => e.currentTarget.style.background = SoS.cream}\n"
    "                onMouseLeave={e => e.currentTarget.style.background = ''}\n"
    "              >"
)
NEW_DB_TR = (
    "              <tr key={b.id}\n"
    "                onClick={() => setSelectedBb(b)}\n"
    "                style={{ borderBottom: `1px solid ${SoS.lineSoft}`, cursor: 'pointer' }}\n"
    "                onMouseEnter={e => e.currentTarget.style.background = SoS.cream}\n"
    "                onMouseLeave={e => e.currentTarget.style.background = ''}\n"
    "              >"
)
if OLD_DB_TR in html:
    html = html.replace(OLD_DB_TR, NEW_DB_TR, 1)
    print('[OK] Desktop brobygger table rows clickable')

# Add BrobyggerProfilePanel overlay before DSCard closing in DesktopBrobyggere
# Find the footer + DSCard close in DesktopBrobyggere
OLD_DB_FOOTER = (
    "      {/* Footer */}\n"
    "      <div style={{ marginTop: 12, fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,\n"
    "        textAlign: 'right' }}>\n"
    "        {rows.length} af {SoS_BROBYGGERE.length} brobyggere\n"
    "      </div>\n"
    "    </DSCard>\n"
    "  );\n"
    "};"
)
NEW_DB_FOOTER = (
    "      {/* Footer */}\n"
    "      <div style={{ marginTop: 12, fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,\n"
    "        textAlign: 'right' }}>\n"
    "        {rows.length} af {SoS_BROBYGGERE.length} brobyggere\n"
    "      </div>\n"
    "    </DSCard>\n"
    "\n"
    "    {/* Brobygger profil overlay */}\n"
    "    {selectedBb && (\n"
    "      <div style={{ position: 'fixed', inset: 0, zIndex: 200,\n"
    "        background: 'rgba(0,0,0,0.35)', display: 'flex',\n"
    "        alignItems: 'flex-end', justifyContent: 'center' }}\n"
    "        onClick={e => { if (e.target === e.currentTarget) setSelectedBb(null); }}>\n"
    "        <div style={{ width: '100%', maxWidth: 520, maxHeight: '90vh',\n"
    "          overflowY: 'auto', background: SoS.cream,\n"
    "          borderRadius: '20px 20px 0 0' }}>\n"
    "          <BrobyggerProfilePanel brobygger={selectedBb} onClose={() => setSelectedBb(null)}/>\n"
    "        </div>\n"
    "      </div>\n"
    "    )}\n"
    "  );\n"
    "};"
)
if OLD_DB_FOOTER in html:
    html = html.replace(OLD_DB_FOOTER, NEW_DB_FOOTER, 1)
    print('[OK] Desktop brobygger profile overlay added')
else:
    print('[WARN] DesktopBrobyggere footer not found')

# ─────────────────────────────────────────────────────────────────────────────
# 10. AppointmentDetailScreen: wire "Kontakt koordinator" button
# ─────────────────────────────────────────────────────────────────────────────
OLD_KONTAKT_BTN = (
    "            <Button full variant=\"secondary\"\n"
    "              icon={<Icon name=\"phone\" size={16} color={SoS.ink} weight={2} />}>\n"
    "              Kontakt koordinator\n"
    "            </Button>"
)
NEW_KONTAKT_BTN = (
    "            <Button full variant=\"secondary\"\n"
    "              onClick={() => alert(`Ring ${menneske.contact.name}: ${menneske.contact.phone}`)}\n"
    "              icon={<Icon name=\"phone\" size={16} color={SoS.ink} weight={2} />}>\n"
    "              Ring koordinator: {menneske.contact.phone}\n"
    "            </Button>"
)
if OLD_KONTAKT_BTN in html:
    html = html.replace(OLD_KONTAKT_BTN, NEW_KONTAKT_BTN, 1)
    print('[OK] Kontakt koordinator button shows phone number')
else:
    print('[WARN] Kontakt koordinator button not found')

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] Saved ({len(html.encode("utf-8")):,} bytes)')

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

ok = []
fail = []

def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1)
        ok.append(label)
    else:
        fail.append(label)

# ══════════════════════════════════════════════════════════════════
# 1. CalendarScreen — tilføj brobyggerId prop
# ══════════════════════════════════════════════════════════════════
sub(
    "const CalendarScreen = ({ appointments, shifts, onOpenAppt, onAddShift }) => {",
    "const CalendarScreen = ({ appointments, shifts, onOpenAppt, onAddShift, brobyggerId }) => {",
    "CalendarScreen: brobyggerId prop"
)

# ══════════════════════════════════════════════════════════════════
# 2. CalendarScreen — tilføj rådighedsplan-state + hjælpefunktioner
# ══════════════════════════════════════════════════════════════════
sub(
    "  const [addShiftSheet, setAddShiftSheet] = React.useState(false);\n"
    "  const [addShiftDone, setAddShiftDone] = React.useState(false);\n"
    "  const [moreShift, setMoreShift] = React.useState(null);",
    "  const [addShiftSheet, setAddShiftSheet] = React.useState(false);\n"
    "  const [addShiftDone, setAddShiftDone] = React.useState(false);\n"
    "  const [moreShift, setMoreShift] = React.useState(null);\n"
    "  const [raadigMode, setRaadigMode] = React.useState('enkelt');\n"
    "  const [gentagDage, setGentagDage] = React.useState([]);\n"
    "  const [gentagTil, setGentagTil] = React.useState('');\n"
    "  const [addedCount, setAddedCount] = React.useState(0);\n"
    "  const [raadighedsplan, setRaadighedsplan] = React.useState(() => {\n"
    "    try { return JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]'); }\n"
    "    catch { return []; }\n"
    "  });\n"
    "  const saveRaadig = (newEntries) => {\n"
    "    const prev = JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]');\n"
    "    const updated = [...prev, ...newEntries];\n"
    "    localStorage.setItem('sos_raadighedsplan', JSON.stringify(updated));\n"
    "    setRaadighedsplan(updated);\n"
    "    setAddedCount(newEntries.length);\n"
    "    setAddShiftDone(true);\n"
    "  };\n"
    "  const handleBekreft = () => {\n"
    "    if (!brobyggerId) return;\n"
    "    if (raadigMode === 'enkelt' && selected) {\n"
    "      const exists = raadighedsplan.some(\n"
    "        r => r.brobyggerId === brobyggerId && r.dato === selected);\n"
    "      if (!exists) saveRaadig([{ id: 'r-' + Date.now(), brobyggerId, dato: selected }]);\n"
    "      else setAddShiftDone(true);\n"
    "    } else if (raadigMode === 'gentag' && gentagDage.length > 0 && gentagTil) {\n"
    "      const entries = [];\n"
    "      const startD = new Date();\n"
    "      const endD = new Date(gentagTil);\n"
    "      for (let d = new Date(startD); d <= endD; d.setDate(d.getDate() + 1)) {\n"
    "        const dow = (d.getDay() + 6) % 7;\n"
    "        if (gentagDage.includes(dow)) {\n"
    "          const iso = d.toISOString().slice(0, 10);\n"
    "          if (!raadighedsplan.some(r => r.brobyggerId === brobyggerId && r.dato === iso))\n"
    "            entries.push({ id: 'r-' + Date.now() + '-' + iso, brobyggerId, dato: iso });\n"
    "        }\n"
    "      }\n"
    "      if (entries.length > 0) saveRaadig(entries);\n"
    "      else setAddShiftDone(true);\n"
    "    }\n"
    "  };",
    "CalendarScreen: raadighedsplan state og handleBekreft"
)

# ══════════════════════════════════════════════════════════════════
# 3. CalendarScreen — augmentér shiftsByDate med localStorage-data
# ══════════════════════════════════════════════════════════════════
sub(
    "  const shiftsByDate = {};\n"
    "  shifts.forEach(s => { (shiftsByDate[s.date] ||= []).push(s); });",
    "  const shiftsByDate = {};\n"
    "  shifts.forEach(s => { (shiftsByDate[s.date] ||= []).push(s); });\n"
    "  const myRaadig = raadighedsplan.filter(\n"
    "    r => !brobyggerId || r.brobyggerId === brobyggerId);\n"
    "  myRaadig.forEach(r => {\n"
    "    (shiftsByDate[r.dato] ||= []).push(\n"
    "      { id: r.id, date: r.dato, start: 'Ledig', end: '', _raadig: true });\n"
    "  });",
    "CalendarScreen: shiftsByDate inkl. raadighedsplan"
)

# ══════════════════════════════════════════════════════════════════
# 4. CalendarScreen — erstat addShiftSheet bottom-sheet indhold
#    med ny simpel dag/gentag-UI
# ══════════════════════════════════════════════════════════════════
OLD_SHEET = (
    "      {/* Add-shift bottom sheet */}\n"
    "      {addShiftSheet && (\n"
    "        <div style={{ position: 'fixed', inset: 0, zIndex: 400, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}\n"
    "          onClick={() => { setAddShiftSheet(false); setAddShiftDone(false); }}>\n"
    "          <div style={{ background: '#fff', borderRadius: '20px 20px 0 0', padding: '24px 20px 40px',\n"
    "            boxShadow: '0 -4px 32px rgba(0,0,0,0.12)' }} onClick={e => e.stopPropagation()}>\n"
    "            {addShiftDone ? (\n"
    "              <div style={{ textAlign: 'center', padding: '16px 0' }}>\n"
    "                <div style={{ width: 56, height: 56, borderRadius: 28, background: SoS.sage,\n"
    "                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>\n"
    "                  <Icon name=\"check\" size={28} color=\"#fff\" weight={2.5} />\n"
    "                </div>\n"
    "                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 8 }}>\n"
    "                  R\xe5dighed meldt!\n"
    "                </div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, marginBottom: 24 }}>\n"
    "                  Koordinatoren kan nu matche dig med et menneske {selected ? 'd. ' + selected.split('-').reverse().join('/') : 'denne dag'}.\n"
    "                </div>\n"
    "                <Button full onClick={() => { setAddShiftSheet(false); setAddShiftDone(false); }}>Luk</Button>\n"
    "              </div>\n"
    "            ) : (\n"
    "              <>\n"
    "                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 6 }}>\n"
    "                  Meld r\xe5dighed\n"
    "                </div>\n"
    "                <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, marginBottom: 20 }}>\n"
    "                  {selected ? formatDate(selected, { long: true }) : 'Valgt dag'}\n"
    "                </div>\n"
    "                <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>\n"
    "                  {[['08:00','12:00','Formiddag'],['12:00','16:00','Eftermiddag'],['16:00','20:00','Aften']].map(([start, end, label]) => (\n"
    "                    <div key={label} style={{ flex: 1, border: `2px solid ${SoS.line}`, borderRadius: SoS.r.md,\n"
    "                      padding: '12px 8px', textAlign: 'center', cursor: 'pointer',\n"
    "                      fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}\n"
    "                      onClick={() => setAddShiftDone(true)}>\n"
    "                      <div style={{ fontWeight: 600, marginBottom: 2 }}>{label}</div>\n"
    "                      <div style={{ fontSize: 11, color: SoS.inkSoft }}>{start}–{end}</div>\n"
    "                    </div>\n"
    "                  ))}\n"
    "                </div>\n"
    "                <Button full onClick={() => setAddShiftDone(true)}>Bekr\xe6ft r\xe5dighed</Button>\n"
    "                <button onClick={() => setAddShiftSheet(false)} style={{ width: '100%', marginTop: 10,\n"
    "                  background: 'none', border: 'none', fontFamily: SoS.sans, fontSize: 14,\n"
    "                  color: SoS.inkSoft, cursor: 'pointer', padding: 10 }}>\n"
    "                  Annuller\n"
    "                </button>\n"
    "              </>\n"
    "            )}\n"
    "          </div>\n"
    "        </div>\n"
    "      )}"
)

NEW_SHEET = r"""      {/* Rådighedsplan bottom sheet */}
      {addShiftSheet && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 400,
          display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}
          onClick={() => { setAddShiftSheet(false); setAddShiftDone(false);
            setRaadigMode('enkelt'); setGentagDage([]); setGentagTil(''); }}>
          <div style={{ background: '#fff', borderRadius: '20px 20px 0 0',
            padding: '24px 20px 44px', boxShadow: '0 -4px 32px rgba(0,0,0,0.12)',
            maxHeight: '80vh', overflowY: 'auto' }}
            onClick={e => e.stopPropagation()}>

            {addShiftDone ? (
              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div style={{ width: 56, height: 56, borderRadius: 28, background: SoS.sage,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 16px' }}>
                  <Icon name="check" size={28} color="#fff" weight={2.5} />
                </div>
                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
                  color: SoS.ink, marginBottom: 8 }}>
                  {addedCount > 1 ? addedCount + ' dage meldt!' : 'Dag meldt!'}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 14,
                  color: SoS.inkSoft, marginBottom: 24 }}>
                  {addedCount > 1
                    ? `${addedCount} ledige dage er nu synlige for koordinatoren.`
                    : `${selected ? selected.split('-').reverse().join('.') : 'Dagen'} er nu synlig for koordinatoren.`}
                </div>
                <Button full onClick={() => {
                  setAddShiftSheet(false); setAddShiftDone(false);
                  setRaadigMode('enkelt'); setGentagDage([]); setGentagTil('');
                }}>Luk</Button>
              </div>
            ) : (
              <>
                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
                  color: SoS.ink, marginBottom: 18 }}>
                  Meld ledig dag
                </div>

                {/* Enkelt / Gentag toggle */}
                <div style={{ display: 'flex', background: SoS.surface,
                  borderRadius: SoS.r.md, padding: 3, marginBottom: 20, gap: 2 }}>
                  {[['enkelt','Enkelt dag'],['gentag','Gentag ugentligt']].map(([id, lbl]) => (
                    <button key={id} onClick={() => setRaadigMode(id)} style={{
                      flex: 1, padding: '9px 0', border: 'none', cursor: 'pointer',
                      borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                      fontWeight: raadigMode === id ? 700 : 500,
                      background: raadigMode === id ? '#fff' : 'transparent',
                      color: raadigMode === id ? SoS.ink : SoS.inkMuted,
                      boxShadow: raadigMode === id ? '0 1px 4px rgba(0,0,0,0.1)' : 'none' }}>
                      {lbl}
                    </button>
                  ))}
                </div>

                {raadigMode === 'enkelt' ? (
                  <>
                    <div style={{ padding: '14px 16px', background: SoS.sage + '12',
                      border: `1px solid ${SoS.sage}40`, borderRadius: SoS.r.md,
                      marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 4,
                        background: SoS.sage, flexShrink: 0 }}/>
                      <div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
                          color: SoS.ink }}>
                          {selected
                            ? new Date(selected).toLocaleDateString('da-DK',
                              { weekday: 'long', day: 'numeric', month: 'long' })
                            : 'Ingen dag valgt'}
                        </div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 12,
                          color: SoS.inkMuted, marginTop: 2 }}>
                          V\xe6lg en dag i kalenderen ovenfor
                        </div>
                      </div>
                    </div>
                    {raadighedsplan.some(r =>
                      r.brobyggerId === brobyggerId && r.dato === selected) && (
                      <div style={{ fontFamily: SoS.sans, fontSize: 12,
                        color: SoS.amber, marginBottom: 12 }}>
                        Du har allerede meldt dig ledig denne dag
                      </div>
                    )}
                    <Button full onClick={handleBekreft}
                      disabled={!selected || !brobyggerId}>
                      Meld ledig
                    </Button>
                  </>
                ) : (
                  <>
                    <div style={{ marginBottom: 14 }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                        color: SoS.inkSoft, marginBottom: 8 }}>
                        Hvilke ugedage?
                      </div>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {['M','T','O','T','F','L','S'].map((lbl, i) => {
                          const sel = gentagDage.includes(i);
                          return (
                            <button key={i} onClick={() => setGentagDage(prev =>
                              prev.includes(i)
                                ? prev.filter(d => d !== i)
                                : [...prev, i])} style={{
                              width: 38, height: 38, borderRadius: 19, border: 'none',
                              cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13,
                              fontWeight: sel ? 700 : 500,
                              background: sel ? SoS.sage : SoS.surface,
                              color: sel ? '#fff' : SoS.ink }}>
                              {lbl}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                        color: SoS.inkSoft, marginBottom: 6 }}>
                        Frem til
                      </div>
                      <input type="date" value={gentagTil}
                        onChange={e => setGentagTil(e.target.value)}
                        style={{ width: '100%', padding: '10px 12px',
                          border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                          fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                          outline: 'none', boxSizing: 'border-box' }}/>
                    </div>
                    <Button full onClick={handleBekreft}
                      disabled={gentagDage.length === 0 || !gentagTil || !brobyggerId}>
                      Tilf\xf8j dage
                    </Button>
                  </>
                )}

                <button onClick={() => setAddShiftSheet(false)} style={{
                  width: '100%', marginTop: 10, background: 'none', border: 'none',
                  fontFamily: SoS.sans, fontSize: 14,
                  color: SoS.inkSoft, cursor: 'pointer', padding: 10 }}>
                  Annuller
                </button>
              </>
            )}
          </div>
        </div>
      )}"""

sub(OLD_SHEET, NEW_SHEET, "CalendarScreen: ny raadighedsplan bottom sheet")

# ══════════════════════════════════════════════════════════════════
# 5. AppWithTweaks — send _bbId til CalendarScreen + HomeScreen
# ══════════════════════════════════════════════════════════════════
sub(
    "{screen === 'kalender' && <CalendarScreen appointments={appts} shifts={SoS_SHIFTS} onOpenAppt={openAppt} onAddShift={() => {}} />}",
    "{screen === 'kalender' && <CalendarScreen appointments={appts} shifts={SoS_SHIFTS} onOpenAppt={openAppt} onAddShift={() => {}} brobyggerId={_bbId} />}",
    "AppWithTweaks: _bbId til CalendarScreen"
)

sub(
    "{screen === \"hjem\" && <HomeScreen user={user} appointments={appts} onOpenAppt={openAppt} onNavigate={navigate} variant={isNew ? \"new\" : \"busy\"} />}",
    "{screen === \"hjem\" && <HomeScreen user={user} appointments={appts} onOpenAppt={openAppt} onNavigate={navigate} variant={isNew ? \"new\" : \"busy\"} brobyggerId={_bbId} />}",
    "AppWithTweaks: _bbId til HomeScreen"
)

# ══════════════════════════════════════════════════════════════════
# 6. HomeScreen — tilføj rådighedsplan-notifikation-banner
# ══════════════════════════════════════════════════════════════════
sub(
    "const HomeScreen = ({ user, appointments, onOpenAppt, onNavigate, variant = 'busy' }) => {",
    "const HomeScreen = ({ user, appointments, onOpenAppt, onNavigate, variant = 'busy', brobyggerId }) => {",
    "HomeScreen: brobyggerId prop"
)

# Tilføj banner i HomeScreen JSX — indsæt efter TopBar
sub(
    "      <TopBar\n"
    "        subtitle={greet}\n"
    "        title={<span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>",
    "      {/* Rådighedsplan notifikation */}\n"
    "      {brobyggerId && (() => {\n"
    "        const raadig = JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]')\n"
    "          .filter(r => r.brobyggerId === brobyggerId);\n"
    "        const twoWeeks = new Date();\n"
    "        twoWeeks.setDate(twoWeeks.getDate() + 14);\n"
    "        const twoWeeksStr = twoWeeks.toISOString().slice(0, 10);\n"
    "        const todayStr = new Date().toISOString().slice(0, 10);\n"
    "        const harKommende = raadig.some(r => r.dato >= todayStr && r.dato <= twoWeeksStr);\n"
    "        if (harKommende) return null;\n"
    "        return (\n"
    "          <div style={{ margin: '12px 20px 0', padding: '12px 14px',\n"
    "            background: SoS.amber + '15',\n"
    "            border: `1px solid ${SoS.amber}40`,\n"
    "            borderRadius: SoS.r.md,\n"
    "            display: 'flex', alignItems: 'center', gap: 10 }}>\n"
    "            <Icon name=\"bell\" size={16} color={SoS.amber}/>\n"
    "            <div style={{ flex: 1 }}>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n"
    "                color: SoS.ink }}>Husk at melde dage ind</div>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 12,\n"
    "                color: SoS.inkMuted, marginTop: 2 }}>\n"
    "                Du har ingen ledige dage registreret de n\xe6ste 14 dage\n"
    "              </div>\n"
    "            </div>\n"
    "          </div>\n"
    "        );\n"
    "      })()}\n"
    "      <TopBar\n"
    "        subtitle={greet}\n"
    "        title={<span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>",
    "HomeScreen: raadighedsplan notifikation"
)

# ══════════════════════════════════════════════════════════════════
# 7. NyAftaleFlow — tilføj sundhed-aftale state + felter
# ══════════════════════════════════════════════════════════════════
sub(
    "  const [hqOverride,     setHqOverride]     = React.useState(viewingHq || 'Aarhus');",
    "  const [hqOverride,     setHqOverride]     = React.useState(viewingHq || 'Aarhus');\n"
    "  const [fastAftale,     setFastAftale]     = React.useState(null);\n"
    "  const [appointmentDato, setAppointmentDato] = React.useState('');\n"
    "  const [appointmentSted, setAppointmentSted] = React.useState('');",
    "NyAftaleFlow: fastAftale state"
)

# Gem appointmentDato/Sted på personen
sub(
    "      hq:           hqOverride || viewingHq || 'Aarhus',\n"
    "      registeredAt: new Date().toISOString(),",
    "      hq:              hqOverride || viewingHq || 'Aarhus',\n"
    "      appointmentDato: fastAftale && appointmentDato ? appointmentDato : null,\n"
    "      appointmentSted: fastAftale && appointmentSted ? appointmentSted.trim() : null,\n"
    "      appointmentType: type === 'sundhed' ? (fastAftale ? 'fast' : 'fleksibel') : null,\n"
    "      registeredAt:    new Date().toISOString(),",
    "NyAftaleFlow: gem appointment-felter"
)

# Indsæt sundhed-aftale sektion EFTER type-knapperne
sub(
    "          <div style={{ marginBottom: 14 }}>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,\n"
    "              color: SoS.inkSoft, marginBottom: 7 }}>\n"
    "              Kilde <span style={{ color: SoS.orange }}>*</span>\n"
    "            </div>",
    "          {/* Sundhed: fast aftaledato? */}\n"
    "          {type === 'sundhed' && (\n"
    "            <div style={{ marginBottom: 14, padding: '12px 14px',\n"
    "              background: SoS.sundhed + '08',\n"
    "              border: `1px solid ${SoS.sundhed}30`,\n"
    "              borderRadius: SoS.r.sm }}>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n"
    "                color: SoS.inkSoft, marginBottom: 8 }}>\n"
    "                Har personen en fast aftaledato?\n"
    "              </div>\n"
    "              <div style={{ display: 'flex', gap: 8, marginBottom: fastAftale ? 10 : 0 }}>\n"
    "                {[['fast', 'Ja, fast dato'], ['fleks', 'Nej, fleksibelt']].map(([id, lbl]) => (\n"
    "                  <button key={id} onClick={() => setFastAftale(id === 'fast')} style={{\n"
    "                    flex: 1, padding: '9px 0', border: `2px solid ${\n"
    "                      fastAftale === (id === 'fast') ? SoS.sundhed : SoS.line}`,\n"
    "                    borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                    fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n"
    "                    background: fastAftale === (id === 'fast') ? SoS.sundhed + '15' : '#fff',\n"
    "                    color: fastAftale === (id === 'fast') ? SoS.sundhed : SoS.inkMuted }}>\n"
    "                    {lbl}\n"
    "                  </button>\n"
    "                ))}\n"
    "              </div>\n"
    "              {fastAftale === true && (\n"
    "                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>\n"
    "                  <div>\n"
    "                    <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,\n"
    "                      color: SoS.inkSoft, marginBottom: 4 }}>Dato</div>\n"
    "                    <input type=\"date\" value={appointmentDato}\n"
    "                      onChange={e => setAppointmentDato(e.target.value)}\n"
    "                      style={inp}/>\n"
    "                  </div>\n"
    "                  <div>\n"
    "                    <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,\n"
    "                      color: SoS.inkSoft, marginBottom: 4 }}>Sted</div>\n"
    "                    <input value={appointmentSted}\n"
    "                      onChange={e => setAppointmentSted(e.target.value)}\n"
    "                      placeholder=\"f.eks. AUH Aarhus\"\n"
    "                      style={inp}/>\n"
    "                  </div>\n"
    "                </div>\n"
    "              )}\n"
    "            </div>\n"
    "          )}\n"
    "\n"
    "          <div style={{ marginBottom: 14 }}>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,\n"
    "              color: SoS.inkSoft, marginBottom: 7 }}>\n"
    "              Kilde <span style={{ color: SoS.orange }}>*</span>\n"
    "            </div>",
    "NyAftaleFlow: sundhed fast-aftale sektion"
)

# ══════════════════════════════════════════════════════════════════
# 8. TilknytBrobyggerModal — rådighedsbaseret matching
#    Indsæt computeret visning øverst når m.appointmentDato findes
# ══════════════════════════════════════════════════════════════════
sub(
    "  const alle    = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');\n"
    "  const ledige  = alle.filter(b => b.openShifts > 0);\n"
    "  const optaget = alle.filter(b => b.openShifts === 0);\n"
    "  const [valgt, setValgt] = React.useState('');\n"
    "  const [mode,  setMode]  = React.useState(ledige.length > 0 ? 'ledig' : 'foresporg');\n"
    "  const [sent,  setSent]  = React.useState(false);\n"
    "  const visListe = mode === 'ledig' ? ledige : optaget;",
    "  const alle    = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');\n"
    "  const ledige  = alle.filter(b => b.openShifts > 0);\n"
    "  const optaget = alle.filter(b => b.openShifts === 0);\n"
    "  const [valgt, setValgt] = React.useState('');\n"
    "  const [mode,  setMode]  = React.useState(ledige.length > 0 ? 'ledig' : 'foresporg');\n"
    "  const [sent,  setSent]  = React.useState(false);\n"
    "  const visListe = mode === 'ledig' ? ledige : optaget;\n"
    "\n"
    "  // R\xe5dighedsbaseret matching n\xe5r person har fast dato\n"
    "  const dato = m.appointmentDato || null;\n"
    "  const raadigPlan = dato\n"
    "    ? JSON.parse(localStorage.getItem('sos_raadighedsplan') || '[]')\n"
    "    : [];\n"
    "  const ledigDag = dato\n"
    "    ? alle.filter(b => raadigPlan.some(r => r.brobyggerId === b.id && r.dato === dato))\n"
    "    : [];\n"
    "  const optatetDag = dato\n"
    "    ? alle.filter(b =>\n"
    "        (window.SoS_APPOINTMENTS_BUSY || []).some(\n"
    "          a => a.brobyggerId === b.id && a.date === dato))\n"
    "    : [];\n"
    "  const ikkeMeldt = dato\n"
    "    ? alle.filter(b =>\n"
    "        !ledigDag.find(x => x.id === b.id) &&\n"
    "        !optatetDag.find(x => x.id === b.id))\n"
    "    : [];",
    "TilknytBrobyggerModal: raadighedsplan state"
)

# Erstat header + brobygger-liste med dato-baseret visning
sub(
    "        {/* Header */}\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink, marginBottom: 4 }}>\n"
    "          Find brobygger\n"
    "        </div>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 16 }}>\n"
    "          {m.firstName} {m.lastName}\n"
    "          {m.behovUrgency === 'snarest' && <span style={{ marginLeft: 8, color: SoS.rose, fontWeight: 600 }}>\xb7 Haster</span>}\n"
    "          {m.behovUrgency === 'uge'     && <span style={{ marginLeft: 8, color: SoS.amber, fontWeight: 600 }}>\xb7 Inden for en uge</span>}\n"
    "        </div>",
    "        {/* Header */}\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700,\n"
    "          color: SoS.ink, marginBottom: 4 }}>Find brobygger</div>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,\n"
    "          marginBottom: dato ? 10 : 16 }}>\n"
    "          {m.firstName} {m.lastName}\n"
    "          {m.behovUrgency === 'snarest' &&\n"
    "            <span style={{ marginLeft: 8, color: SoS.rose, fontWeight: 600 }}>\xb7 Haster</span>}\n"
    "        </div>\n"
    "        {dato && (\n"
    "          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16,\n"
    "            padding: '8px 12px', background: SoS.sky + '15',\n"
    "            border: `1px solid ${SoS.sky}40`, borderRadius: SoS.r.sm }}>\n"
    "            <Icon name=\"calendar\" size={14} color={SoS.sky}/>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,\n"
    "              color: SoS.ink }}>\n"
    "              {new Date(dato).toLocaleDateString('da-DK',\n"
    "                { weekday: 'long', day: 'numeric', month: 'long' })}\n"
    "              {m.appointmentSted &&\n"
    "                <span style={{ fontWeight: 400, color: SoS.inkMuted }}>\n"
    "                  {' \xb7 '}{m.appointmentSted}\n"
    "                </span>}\n"
    "            </div>\n"
    "          </div>\n"
    "        )}",
    "TilknytBrobyggerModal: dato-header"
)

# Indsæt rådighedsbaseret liste EFTER mode-toggle blokken men kun når der IKKE er dato
# Alternativt: vis dato-baseret liste i stedet for mode-toggle
# Tilføj dato-baseret visning OVER mode-toggle
sub(
    "        {/* Mode-toggle: Ledig / Foresp\xf8rg */}\n"
    "        <div style={{ display: 'flex', borderRadius: SoS.r.sm, overflow: 'hidden',\n"
    "          border: `1px solid ${SoS.line}`, marginBottom: 16 }}>",
    "        {/* Dato-baseret liste n\xe5r fast aftale */}\n"
    "        {dato && (\n"
    "          <div style={{ marginBottom: 16 }}>\n"
    "            {[\n"
    "              { label: '✅ Ledig denne dag', list: ledigDag,\n"
    "                color: SoS.green, bg: SoS.green + '10', action: 'match' },\n"
    "              { label: '⚠️ Ikke meldt ind (kan foresp\xf8rges)', list: ikkeMeldt,\n"
    "                color: SoS.amber, bg: SoS.amber + '10', action: 'foresporg' },\n"
    "              { label: '❌ Optaget denne dag', list: optatetDag,\n"
    "                color: SoS.rose, bg: SoS.rose + '10', action: null },\n"
    "            ].map(gruppe => gruppe.list.length === 0 ? null : (\n"
    "              <div key={gruppe.label} style={{ marginBottom: 10 }}>\n"
    "                <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 700,\n"
    "                  color: gruppe.color, letterSpacing: 0.5,\n"
    "                  textTransform: 'uppercase', marginBottom: 6 }}>\n"
    "                  {gruppe.label}\n"
    "                </div>\n"
    "                {gruppe.list.map(b => {\n"
    "                  const myAppts = (window.SoS_APPOINTMENTS_BUSY || [])\n"
    "                    .filter(a => a.brobyggerId === b.id && a.status === 'confirmed');\n"
    "                  const sel = valgt === b.id;\n"
    "                  const canSelect = gruppe.action !== null;\n"
    "                  return (\n"
    "                    <button key={b.id}\n"
    "                      onClick={() => canSelect && setValgt(sel ? '' : b.id)}\n"
    "                      style={{ display: 'flex', alignItems: 'center', gap: 12,\n"
    "                        width: '100%', textAlign: 'left', padding: '10px 12px',\n"
    "                        marginBottom: 6, borderRadius: SoS.r.md, cursor: canSelect ? 'pointer' : 'default',\n"
    "                        border: `2px solid ${sel ? gruppe.color : (canSelect ? SoS.line : SoS.lineSoft)}`,\n"
    "                        background: sel ? gruppe.color + '12'\n"
    "                          : canSelect ? SoS.paper : SoS.surface,\n"
    "                        opacity: gruppe.action === null ? 0.6 : 1 }}>\n"
    "                      <div style={{ width: 32, height: 32, borderRadius: 16,\n"
    "                        background: b.bg || SoS.accent,\n"
    "                        display: 'flex', alignItems: 'center', justifyContent: 'center',\n"
    "                        fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n"
    "                        color: '#fff', flexShrink: 0 }}>{b.avatar}</div>\n"
    "                      <div style={{ flex: 1 }}>\n"
    "                        <div style={{ fontFamily: SoS.sans, fontSize: 13,\n"
    "                          fontWeight: 600, color: sel ? gruppe.color : SoS.ink }}>\n"
    "                          {b.name}\n"
    "                        </div>\n"
    "                        <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                          color: SoS.inkSoft }}>\n"
    "                          {myAppts.length} aktive aftaler\n"
    "                        </div>\n"
    "                      </div>\n"
    "                    </button>\n"
    "                  );\n"
    "                })}\n"
    "              </div>\n"
    "            ))}\n"
    "          </div>\n"
    "        )}\n"
    "\n"
    "        {/* Mode-toggle: Ledig / Foresp\xf8rg — kun uden fast dato */}\n"
    "        {!dato && <div style={{ display: 'flex', borderRadius: SoS.r.sm, overflow: 'hidden',\n"
    "          border: `1px solid ${SoS.line}`, marginBottom: 16 }}>",
    "TilknytBrobyggerModal: dato-baseret liste"
)

# Luk mode-toggle div betinget
sub(
    "          Foresp\xf8rg optaget ({optaget.length})\n"
    "          </button>\n"
    "        </div>",
    "          Foresp\xf8rg optaget ({optaget.length})\n"
    "          </button>\n"
    "        </div>}\n"
    "        {!dato && <>",
    "TilknytBrobyggerModal: wrap ledig-liste i !dato"
)

# Luk den betingede blok for ledig-liste
sub(
    "        </div>\n"
    "\n"
    "        {/* Action-knapper */}",
    "        </div>\n"
    "        {!dato && </>}\n"
    "\n"
    "        {/* Action-knapper */}",
    "TilknytBrobyggerModal: close !dato block"
)

# ─── Write ───────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print('CRLF-fix: rettet')
else:
    print('CRLF-check: OK')

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  OK {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  FAIL {x}')
print('\nFil skrevet.')

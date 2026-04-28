"""
patch_planlagt_pause.py
-----------------------
1. Eksporter StepDots til window (manglede cross-block)
2. Tilfoej pauseUntil + pauseNote til SS_BROBYGGERE mock-data
   - Soeren Nybo (bb-2) faar eksempel-pause til 31. maj 2026
3. Tilfoej planlagt-pause-sektion i BrobyggerProfilePanel
4. Opdater bbAlert: spring advarsler over for brobyggere paa planlagt pause
   + fix null lastActive (afventer-brobyggere)
"""
import sys

IN = OUT = 'Brobygger portal.html'
with open(IN, encoding='utf-8') as f:
    html = f.read()
original = html

# ══════════════════════════════════════════════════════════════
# 1. StepDots export
# ══════════════════════════════════════════════════════════════
OLD_REG = 'window.RegistrerEfterAftale = RegistrerEfterAftale;'
NEW_REG = 'window.StepDots = StepDots;\nwindow.RegistrerEfterAftale = RegistrerEfterAftale;'

if OLD_REG not in html:
    sys.exit('ERROR: RegistrerEfterAftale export not found')
html = html.replace(OLD_REG, NEW_REG, 1)
print('[OK] StepDots eksporteret til window')

# ══════════════════════════════════════════════════════════════
# 2. Mock data: tilfoej pauseUntil + pauseNote til SS_BROBYGGERE
# ══════════════════════════════════════════════════════════════
old_bb1  = "{ id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1, thisWeek: 2, startDate: '2024-10-01', lastActive: '2026-04-20' },"
new_bb1  = "{ id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1, thisWeek: 2, startDate: '2024-10-01', lastActive: '2026-04-20', pauseUntil: null, pauseNote: '' },"

old_bb2  = "{ id: 'bb-2', name: 'S\u00f8ren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3, thisWeek: 0, startDate: '2025-01-15', lastActive: '2026-02-10' },"
new_bb2  = "{ id: 'bb-2', name: 'S\u00f8ren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3, thisWeek: 0, startDate: '2025-01-15', lastActive: '2026-02-10', pauseUntil: '2026-05-31', pauseNote: 'Eksamen' },"

old_bb3  = "{ id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2, thisWeek: 1, startDate: '2025-03-01', lastActive: '2026-04-09' },"
new_bb3  = "{ id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2, thisWeek: 1, startDate: '2025-03-01', lastActive: '2026-04-09', pauseUntil: null, pauseNote: '' },"

old_bb4  = "{ id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: '2024-05-20', lastActive: '2025-09-14' },"
new_bb4  = "{ id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: '2024-05-20', lastActive: '2025-09-14', pauseUntil: null, pauseNote: '' },"

old_bb5  = "{ id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0, thisWeek: 3, startDate: '2024-08-12', lastActive: '2026-04-22' },"
new_bb5  = "{ id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0, thisWeek: 3, startDate: '2024-08-12', lastActive: '2026-04-22', pauseUntil: null, pauseNote: '' },"

old_bb6  = "{ id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4, thisWeek: 0, startDate: '2026-03-01', lastActive: '2026-03-12' },"
new_bb6  = "{ id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4, thisWeek: 0, startDate: '2026-03-01', lastActive: '2026-03-12', pauseUntil: null, pauseNote: '' },"

old_bb7  = "{ id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2, thisWeek: 1, startDate: '2025-06-10', lastActive: '2026-01-20' },"
new_bb7  = "{ id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2, thisWeek: 1, startDate: '2025-06-10', lastActive: '2026-01-20', pauseUntil: null, pauseNote: '' },"

old_bb8  = "{ id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2, startDate: '2025-09-05', lastActive: '2026-04-17' },"
new_bb8  = "{ id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2, startDate: '2025-09-05', lastActive: '2026-04-17', pauseUntil: null, pauseNote: '' },"

old_bb9  = "{ id: 'bb-9', name: 'Karoline Falk',    avatar: 'KF', bg: '#7FA089', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null },"
new_bb9  = "{ id: 'bb-9', name: 'Karoline Falk',    avatar: 'KF', bg: '#7FA089', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null, pauseUntil: null, pauseNote: '' },"

old_bb10 = "{ id: 'bb-10', name: 'David Christiansen', avatar: 'DC', bg: '#B8501E', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null },"
new_bb10 = "{ id: 'bb-10', name: 'David Christiansen', avatar: 'DC', bg: '#B8501E', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null, pauseUntil: null, pauseNote: '' },"

for old, new, tag in [
    (old_bb1,  new_bb1,  'bb-1'), (old_bb2,  new_bb2,  'bb-2'),
    (old_bb3,  new_bb3,  'bb-3'), (old_bb4,  new_bb4,  'bb-4'),
    (old_bb5,  new_bb5,  'bb-5'), (old_bb6,  new_bb6,  'bb-6'),
    (old_bb7,  new_bb7,  'bb-7'), (old_bb8,  new_bb8,  'bb-8'),
    (old_bb9,  new_bb9,  'bb-9'), (old_bb10, new_bb10, 'bb-10'),
]:
    if old not in html:
        sys.exit(f'ERROR: {tag} line not found')
    html = html.replace(old, new, 1)
print('[OK] pauseUntil + pauseNote tilfoejt til alle brobyggere (Soeren: eksempel)')

# ══════════════════════════════════════════════════════════════
# 3. BrobyggerProfilePanel: tilfoej state + planlagt-pause-UI
# ══════════════════════════════════════════════════════════════

# 3a. Tilfoej state-hooks
OLD_STATE = (
    "  const [saved, setSaved] = React.useState(false);\n"
    "\n"
    "  const today = new Date('2026-04-25');"
)
NEW_STATE = (
    "  const [saved, setSaved] = React.useState(false);\n"
    "  const [pauseUntil, setPauseUntil] = React.useState(b.pauseUntil || '');\n"
    "  const [pauseNote, setPauseNote] = React.useState(b.pauseNote || '');\n"
    "  const [pauseSaved, setPauseSaved] = React.useState(false);\n"
    "\n"
    "  const today = new Date('2026-04-25');"
)
if OLD_STATE not in html:
    sys.exit('ERROR: saved-state anchor not found')
html = html.replace(OLD_STATE, NEW_STATE, 1)
print('[OK] State hooks tilfoejt til BrobyggerProfilePanel')

# 3b. Indsaet planlagt-pause-sektion foer status-actions
OLD_STATUS_ACTIONS = "        {/* Status actions */}"
NEW_PAUSE_SECTION = (
    "        {/* Planlagt pause */}\n"
    "        {(status === 'aktiv' || status === 'ny') && (\n"
    "          <div style={{ margin: '0 16px 16px', background: '#fff',\n"
    "            borderRadius: SS.r.md, border: `1px solid ${SS.lineSoft}`, padding: 16 }}>\n"
    "            <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 700,\n"
    "              color: SS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',\n"
    "              marginBottom: 12 }}>Planlagt pause</div>\n"
    "            {pauseUntil && pauseUntil >= '2026-04-26' ? (\n"
    "              <>\n"
    "                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 10 }}>\n"
    "                  <div style={{ width: 32, height: 32, borderRadius: 16, background: SS.sun + '22',\n"
    "                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>\n"
    "                    <Icon name=\"calendar\" size={15} color={SS.orangeDeep}/>\n"
    "                  </div>\n"
    "                  <div>\n"
    "                    <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600, color: SS.ink }}>\n"
    "                      Pause til {new Date(pauseUntil).toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' })}\n"
    "                    </div>\n"
    "                    {pauseNote ? (\n"
    "                      <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, marginTop: 2 }}>\n"
    "                        {pauseNote}\n"
    "                      </div>\n"
    "                    ) : null}\n"
    "                    <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.sage, marginTop: 4, fontWeight: 600 }}>\n"
    "                      Ingen advarsel genereres i perioden\n"
    "                    </div>\n"
    "                  </div>\n"
    "                </div>\n"
    "                <button onClick={() => { setPauseUntil(''); setPauseNote(''); setPauseSaved(false); }}\n"
    "                  style={{ fontFamily: SS.sans, fontSize: 12, color: SS.rose,\n"
    "                    background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>\n"
    "                  Fjern planlagt pause\n"
    "                </button>\n"
    "              </>\n"
    "            ) : (\n"
    "              <>\n"
    "                <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,\n"
    "                  marginBottom: 10, lineHeight: 1.5 }}>\n"
    "                  Brobyggeren melder pause (fx eksamen, rejse). Ingen automatisk advarsel i perioden.\n"
    "                </div>\n"
    "                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 10 }}>\n"
    "                  <div>\n"
    "                    <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,\n"
    "                      color: SS.inkSoft, marginBottom: 5 }}>Pause til</div>\n"
    "                    <input type=\"date\" value={pauseUntil} min=\"2026-04-27\"\n"
    "                      onChange={e => setPauseUntil(e.target.value)}\n"
    "                      style={{ width: '100%', padding: '9px 10px', fontFamily: SS.sans,\n"
    "                        fontSize: 13, color: SS.ink, background: SS.cream,\n"
    "                        border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,\n"
    "                        outline: 'none', boxSizing: 'border-box' }}/>\n"
    "                  </div>\n"
    "                  <div>\n"
    "                    <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,\n"
    "                      color: SS.inkSoft, marginBottom: 5 }}>\u00c5rsag</div>\n"
    "                    <input placeholder=\"fx Eksamen\" value={pauseNote}\n"
    "                      onChange={e => setPauseNote(e.target.value)}\n"
    "                      style={{ width: '100%', padding: '9px 10px', fontFamily: SS.sans,\n"
    "                        fontSize: 13, color: SS.ink, background: SS.cream,\n"
    "                        border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,\n"
    "                        outline: 'none', boxSizing: 'border-box' }}/>\n"
    "                  </div>\n"
    "                </div>\n"
    "                <button\n"
    "                  onClick={() => { if (pauseUntil) { setPauseSaved(true); setTimeout(() => setPauseSaved(false), 2000); } }}\n"
    "                  style={{ width: '100%', padding: '11px 0',\n"
    "                    background: pauseUntil ? SS.sky : SS.lineSoft,\n"
    "                    color: pauseUntil ? '#fff' : SS.inkMuted,\n"
    "                    border: 'none', borderRadius: SS.r.md,\n"
    "                    fontFamily: SS.sans, fontSize: 13, fontWeight: 600,\n"
    "                    cursor: pauseUntil ? 'pointer' : 'default' }}>\n"
    "                  {pauseSaved ? 'Gemt \u2014 ingen advarsel i perioden' : 'Gem planlagt pause'}\n"
    "                </button>\n"
    "              </>\n"
    "            )}\n"
    "          </div>\n"
    "        )}\n"
    "\n"
    "        {/* Status actions */}"
)
if OLD_STATUS_ACTIONS not in html:
    sys.exit('ERROR: Status actions anchor not found')
html = html.replace(OLD_STATUS_ACTIONS, NEW_PAUSE_SECTION, 1)
print('[OK] Planlagt pause-sektion indsat i BrobyggerProfilePanel')

# ══════════════════════════════════════════════════════════════
# 4. Opdater bbAlert: null-check + planlagt pause suppression
# ══════════════════════════════════════════════════════════════
OLD_BBALERT = (
    "  const bbAlert = (b) => {\n"
    "    const m = monthsSince(b.lastActive);\n"
    "    if (m >= lifecycle.endMonths)     return { label: 'Afsluttes snart',  color: SS.rose };\n"
    "    if (m >= lifecycle.pauseMonths)   return { label: 'Foresl\u00e5s pause',   color: SS.sun };\n"
    "    if (m >= lifecycle.warningMonths) return { label: 'Inaktiv',          color: SS.sun };\n"
    "    return null;\n"
    "  };"
)
NEW_BBALERT = (
    "  const bbAlert = (b) => {\n"
    "    if (!b.lastActive) return null;\n"
    "    if (b.pauseUntil && b.pauseUntil >= '2026-04-26') return null;\n"
    "    const m = monthsSince(b.lastActive);\n"
    "    if (m >= lifecycle.endMonths)     return { label: 'Afsluttes snart',  color: SS.rose };\n"
    "    if (m >= lifecycle.pauseMonths)   return { label: 'Foresl\u00e5s pause',   color: SS.sun };\n"
    "    if (m >= lifecycle.warningMonths) return { label: 'Inaktiv',          color: SS.sun };\n"
    "    return null;\n"
    "  };"
)
if OLD_BBALERT not in html:
    sys.exit('ERROR: bbAlert not found')
html = html.replace(OLD_BBALERT, NEW_BBALERT, 1)
print('[OK] bbAlert opdateret med null-check + planlagt pause suppression')

# ══════════════════════════════════════════════════════════════
# Gem
# ══════════════════════════════════════════════════════════════
if html == original:
    sys.exit('ERROR: ingen aendringer foretaget')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] Gemt ({len(html.encode("utf-8")):,} bytes)')

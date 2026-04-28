import re

path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

results = []

# ═══════════════════════════════════════════════════════════════════════════════
# 1. SoS — replace "Social Sundhed" abbreviation in UI labels/titles
# ═══════════════════════════════════════════════════════════════════════════════
replacements = [
    ("Admin \u00b7 Social Sundhed",       "Admin \u00b7 SoS"),
    ("'Admin \u00b7 Social Sundhed'",     "'Admin \u00b7 SoS'"),
    ("`Admin \u00b7 Social Sundhed`",     "`Admin \u00b7 SoS`"),
    ("isAdmin ? 'Admin' : 'R\u00e5dgiver'} \u00b7 Social Sundhed",
     "isAdmin ? 'Admin' : 'R\u00e5dgiver'} \u00b7 SoS"),
    ("isAdmin ? 'Admin \u00b7 SoS' : `Koordinator \u00b7 ${ownHq}`",
     "isAdmin ? 'Admin \u00b7 SoS' : `Koordinator \u00b7 ${ownHq}`"),  # already right
    ("isAdmin ? 'Admin \u00b7 Social Sundhed' : `Koordinator \u00b7 ${ownHq}`",
     "isAdmin ? 'Admin \u00b7 SoS' : `Koordinator \u00b7 ${ownHq}`"),
    # Title tag
    ("<title>Brobygger portal \u2014 Social Sundhed</title>",
     "<title>Brobygger portal \u2014 SoS</title>"),
    # Tab label
    ("'Mig', s: isAdmin ? 'Admin \u00b7 Social Sundhed' : 'R\u00e5dgiver' },",
     "'Mig', s: isAdmin ? 'Admin \u00b7 SoS' : 'R\u00e5dgiver' },"),
    # Messages thread
    ("{ id: 't-2', withName: 'Social Sundhed',",
     "{ id: 't-2', withName: 'SoS',"),
    # Comment headers
    ("// Social Sundhed \u2014 design tokens",     "// SoS \u2014 design tokens"),
    ("// Mock data for Social Sundhed \u2014 Brobygger portal",
     "// Mock data for SoS \u2014 Brobygger portal"),
    ("// Social Sundhed \u2014 shared UI primitives",
     "// SoS \u2014 shared UI primitives"),
    ("// Microsoft login screens but in Social Sundhed's warm shell",
     "// Microsoft login screens but in SoS warm shell"),
    ("(Return on Investment) model for Social Sundhed",
     "(Return on Investment) model for SoS"),
]
sos_count = 0
for old, new in replacements:
    if old in html:
        html = html.replace(old, new)
        sos_count += 1
results.append(f"SoS renaming: {sos_count} substitutions")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. SS_BROBYGGERE — add one 'afventer' entry (Karoline Falk)
# ═══════════════════════════════════════════════════════════════════════════════
old_bb_end = "  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2, startDate: '2025-09-05', lastActive: '2026-04-17' },\n];"
new_bb_end = "  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2, startDate: '2025-09-05', lastActive: '2026-04-17' },\n  { id: 'bb-9', name: 'Karoline Falk',    avatar: 'KF', bg: '#7FA089', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null },\n  { id: 'bb-10', name: 'David Christiansen', avatar: 'DC', bg: '#B8501E', active: 0, pending: 0, status: 'afventer', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: null, lastActive: null },\n];"

if old_bb_end in html:
    html = html.replace(old_bb_end, new_bb_end, 1)
    results.append("Added 2 'afventer' brobyggere to SS_BROBYGGERE")
else:
    results.append("ERROR: SS_BROBYGGERE end not found")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Update 'nye frivillige' ActionCard count to use real SS_BROBYGGERE data
#    + add afventer handling
# ═══════════════════════════════════════════════════════════════════════════════
old_reg_var = "  const pendingMatches = 3;\n  const newRegistrations = 2;"
new_reg_var = "  const pendingMatches = SS_BROBYGGERE.filter(b => b.pending > 0).length;\n  const afventerCount = SS_BROBYGGERE.filter(b => b.status === 'afventer').length;\n  const newRegistrations = afventerCount;"
if old_reg_var in html:
    html = html.replace(old_reg_var, new_reg_var, 1)
    results.append("Updated dashboard counts to use live SS_BROBYGGERE data")
else:
    results.append("WARNING: pendingMatches/newRegistrations var not found")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. AdminBrobyggereScreen — add 'afventer' filter + click-to-profile + badges
# ═══════════════════════════════════════════════════════════════════════════════
old_bb_screen = """AdminBrobyggereScreen = ({ hovedsaede }) => {
  const [filter, setFilter] = React.useState('alle');
  const filtered = SS_BROBYGGERE.filter(b => filter === 'alle' || b.status === filter);"""

new_bb_screen = """AdminBrobyggereScreen = ({ hovedsaede }) => {
  const [filter, setFilter] = React.useState('alle');
  const [selectedBb, setSelectedBb] = React.useState(null);
  const filtered = SS_BROBYGGERE.filter(b => filter === 'alle' || b.status === filter);
  const afventerCount = SS_BROBYGGERE.filter(b => b.status === 'afventer').length;"""

if old_bb_screen in html:
    html = html.replace(old_bb_screen, new_bb_screen, 1)
    results.append("Updated AdminBrobyggereScreen with selectedBb state")
else:
    results.append("ERROR: AdminBrobyggereScreen header not found")

# Add 'afventer' to filter chips
old_filters = """        {[
          { id: 'alle', label: `Alle (${SS_BROBYGGERE.length})` },
          { id: 'aktiv', label: 'Aktive' },
          { id: 'pause', label: 'P\u00e5 pause' },
          { id: 'ny', label: 'Nye' },
        ].map(f => ("""

new_filters = """        {[
          { id: 'alle', label: `Alle (${SS_BROBYGGERE.length})` },
          { id: 'aktiv', label: 'Aktive' },
          { id: 'pause', label: 'P\u00e5 pause' },
          { id: 'ny', label: 'Nye' },
          { id: 'afventer', label: `Afventer (${afventerCount})`, highlight: true },
        ].map(f => ("""

if old_filters in html:
    html = html.replace(old_filters, new_filters, 1)
    results.append("Added 'afventer' filter chip")
else:
    results.append("ERROR: filter chips not found")

# Update filter chip style to show highlight for afventer
old_chip_style = """            background: filter === f.id ? SS.ink : '#fff',
            color: filter === f.id ? '#fff' : SS.ink,
            border: filter === f.id ? 'none' : `1px solid ${SS.line}`,
            fontFamily: SS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',
          }}>{f.label}</button>"""

new_chip_style = """            background: filter === f.id ? (f.highlight ? SS.orange : SS.ink) : '#fff',
            color: filter === f.id ? '#fff' : (f.highlight ? SS.orange : SS.ink),
            border: filter === f.id ? 'none' : `1.5px solid ${f.highlight ? SS.orange + '60' : SS.line}`,
            fontFamily: SS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',
          }}>{f.label}</button>"""

if old_chip_style in html:
    html = html.replace(old_chip_style, new_chip_style, 1)
    results.append("Styled afventer filter chip orange")
else:
    results.append("ERROR: chip style not found")

# Make each brobygger row clickable + add status badges
old_bb_row = """        {filtered.map(b => (
          <div key={b.id} style={{
            display: 'flex', gap: 14, padding: 14, background: '#fff',
            borderRadius: SS.r.md, border: `1px solid ${SS.lineSoft}`,
          }}>
            <Avatar initials={b.avatar} bg={b.bg} size={46} />"""

new_bb_row = """        {selectedBb && (
          <BrobyggerProfilePanel
            brobygger={selectedBb}
            onClose={() => setSelectedBb(null)}
          />
        )}
        {filtered.map(b => (
          <div key={b.id} onClick={() => setSelectedBb(b)} style={{
            display: 'flex', gap: 14, padding: 14, background: '#fff',
            borderRadius: SS.r.md,
            border: `1.5px solid ${b.status === 'afventer' ? SS.orange + '60' : SS.lineSoft}`,
            cursor: 'pointer',
          }}>
            <Avatar initials={b.avatar} bg={b.status === 'afventer' ? SS.lineSoft : b.bg} size={46} />"""

if old_bb_row in html:
    html = html.replace(old_bb_row, new_bb_row, 1)
    results.append("Made brobygger rows clickable + added afventer styling")
else:
    results.append("ERROR: brobygger row not found")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Sensitive data time-window lock in AppointmentDetailScreen
# ═══════════════════════════════════════════════════════════════════════════════
old_health = """            {menneske.health && (
              <InfoRow icon="shield" label="Helbred & hensyn" value={menneske.health} multiline />
            )}"""

new_health = """            {menneske.health && (() => {
              // Check if appointment is within the data-access window (default ±7 days)
              const apptDate = new Date(appt.date);
              const today = new Date('2026-04-25');
              const diffDays = (apptDate - today) / (1000 * 60 * 60 * 24);
              const hasAccess = diffDays >= -7 && diffDays <= 7;
              return hasAccess ? (
                <InfoRow icon="shield" label="Helbred & hensyn" value={menneske.health} multiline />
              ) : (
                <div style={{
                  display: 'flex', gap: 12, alignItems: 'flex-start',
                  padding: '12px 0', borderBottom: `1px solid ${SS.lineSoft}`,
                }}>
                  <div style={{ width: 32, height: 32, borderRadius: 16,
                    background: SS.lineSoft, flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon name="lock" size={14} color={SS.inkMuted}/>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                      color: SS.inkMuted, marginBottom: 3 }}>Helbred & hensyn</div>
                    <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkMuted,
                      lineHeight: 1.4 }}>
                      Adgang l\u00e5st \u2014 f\u00f8lsomme oplysninger er kun synlige
                      7 dage f\u00f8r og efter brobygningen.
                    </div>
                  </div>
                </div>
              );
            })()}"""

if old_health in html:
    html = html.replace(old_health, new_health, 1)
    results.append("Added sensitive data time-window lock to AppointmentDetailScreen")
else:
    results.append("ERROR: health InfoRow not found")

# ═══════════════════════════════════════════════════════════════════════════════
# 6. BrobyggerProfilePanel component — inject before AdminBrobyggereScreen
# ═══════════════════════════════════════════════════════════════════════════════
panel_component = """
const BrobyggerProfilePanel = ({ brobygger: b, onClose }) => {
  const [status, setStatus] = React.useState(b.status);
  const [startDate, setStartDate] = React.useState(b.startDate || '');
  const [showEndConfirm, setShowEndConfirm] = React.useState(false);
  const [ended, setEnded] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  const today = new Date('2026-04-25');
  const fmtDate = (d) => d ? new Date(d).toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' }) : null;
  const monthsActive = b.startDate
    ? Math.round((today - new Date(b.startDate)) / (1000 * 60 * 60 * 24 * 30.4) * 10) / 10
    : null;

  const STATUS_COLORS = {
    aktiv: { bg: SS.sageSoft, color: SS.sage, label: 'Aktiv' },
    pause: { bg: SS.sun + '22', color: SS.orangeDeep, label: 'P\u00e5 pause' },
    ny:    { bg: SS.skySoft, color: SS.sky, label: 'Ny' },
    afventer: { bg: SS.orange + '15', color: SS.orange, label: 'Afventer godkendelse' },
    afsluttet: { bg: '#F5F5F5', color: SS.inkMuted, label: 'Afsluttet' },
  };
  const sc = STATUS_COLORS[status] || STATUS_COLORS.aktiv;

  if (ended) {
    return (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
        zIndex: 500, display: 'flex', alignItems: 'flex-end' }}>
        <div style={{ background: '#fff', borderRadius: '20px 20px 0 0', padding: '28px 24px 44px',
          width: '100%', textAlign: 'center' }}>
          <div style={{ width: 56, height: 56, borderRadius: 28, background: SS.sageSoft,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px' }}>
            <Icon name="check" size={24} color={SS.sage}/>
          </div>
          <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500, color: SS.ink, marginBottom: 8 }}>
            {b.name.split(' ')[0]} er registreret afsluttet
          </div>
          <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft, lineHeight: 1.5, marginBottom: 24 }}>
            En takke-e-mail er sendt. Aktive brobygningsforl\u00f8b er overf\u00f8rt til r\u00e5dgiveren.
          </div>
          <button onClick={onClose} style={{
            width: '100%', padding: '14px 0', background: SS.orange, color: '#fff',
            border: 'none', borderRadius: SS.r.md, fontFamily: SS.sans,
            fontSize: 15, fontWeight: 600, cursor: 'pointer',
          }}>Luk</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
      zIndex: 500, display: 'flex', alignItems: 'flex-end' }}>
      <div style={{ background: SS.cream, borderRadius: '20px 20px 0 0',
        width: '100%', maxHeight: '88vh', overflowY: 'auto', paddingBottom: 40 }}>

        {/* Handle + close */}
        <div style={{ display: 'flex', justifyContent: 'center', padding: '12px 0 0' }}>
          <div style={{ width: 36, height: 4, borderRadius: 2, background: SS.lineSoft }}/>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '8px 16px 0' }}>
          <button onClick={onClose} style={{ background: SS.creamDeep, border: 'none',
            width: 32, height: 32, borderRadius: 16, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="close" size={14} color={SS.ink}/>
          </button>
        </div>

        {/* Profile header */}
        <div style={{ padding: '8px 20px 20px', display: 'flex', gap: 16, alignItems: 'center' }}>
          <div style={{ width: 64, height: 64, borderRadius: 32,
            background: status === 'afventer' ? SS.lineSoft : b.bg,
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <span style={{ fontFamily: SS.sans, fontSize: 20, fontWeight: 700, color: '#fff' }}>{b.avatar}</span>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
              color: SS.ink, letterSpacing: -0.2 }}>{b.name}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
              <span style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
                color: sc.color, background: sc.bg,
                padding: '3px 10px', borderRadius: 999 }}>{sc.label}</span>
              {monthsActive && (
                <span style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft }}>
                  {monthsActive} m\u00e5neder
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Afventer — godkend / afvis */}
        {status === 'afventer' && (
          <div style={{ margin: '0 16px 16px', background: SS.orange + '12',
            border: `1.5px solid ${SS.orange}40`, borderRadius: SS.r.md, padding: 16 }}>
            <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600,
              color: SS.orange, marginBottom: 8 }}>
              Afventer godkendelse
            </div>
            <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
              marginBottom: 14, lineHeight: 1.5 }}>
              Denne brobygger har gennemf\u00f8rt onboarding og venter p\u00e5 at blive aktiveret.
              S\u00e6t en startdato og godkend for at give adgang.
            </div>
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,
                color: SS.inkSoft, marginBottom: 5 }}>Startdato</div>
              <input type="date" value={startDate}
                onChange={e => setStartDate(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', fontFamily: SS.sans,
                  fontSize: 14, color: SS.ink, background: '#fff',
                  border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                  outline: 'none', boxSizing: 'border-box' }}/>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => { setStatus('aktiv'); setSaved(true); setTimeout(() => setSaved(false), 1500); }}
                style={{ flex: 2, padding: '12px 0', background: SS.sage, color: '#fff',
                  border: 'none', borderRadius: SS.r.md, fontFamily: SS.sans,
                  fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                {saved ? '\u2713 Godkendt' : 'Godkend og aktiv\u00e9r'}
              </button>
              <button onClick={() => setStatus('afsluttet')} style={{
                flex: 1, padding: '12px 0', background: '#fff', color: SS.inkSoft,
                border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 14, cursor: 'pointer',
              }}>Afvis</button>
            </div>
          </div>
        )}

        {/* Stats grid */}
        {status !== 'afventer' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
            gap: 8, margin: '0 16px 16px' }}>
            {[
              { label: 'Aktive forl\u00f8b', value: b.active },
              { label: 'Denne m\u00e5ned', value: b.thisMonth },
              { label: 'Ledige vagter', value: b.openShifts },
            ].map(s => (
              <div key={s.label} style={{ background: '#fff', borderRadius: SS.r.md,
                padding: '12px 10px', textAlign: 'center',
                border: `1px solid ${SS.lineSoft}` }}>
                <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
                  color: SS.orange }}>{s.value}</div>
                <div style={{ fontFamily: SS.sans, fontSize: 10, color: SS.inkSoft,
                  marginTop: 2, lineHeight: 1.3 }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Dates */}
        <div style={{ margin: '0 16px 16px', background: '#fff',
          borderRadius: SS.r.md, border: `1px solid ${SS.lineSoft}`, overflow: 'hidden' }}>
          {[
            { label: 'Startdato', value: fmtDate(b.startDate), edit: true },
            { label: 'Sidst aktiv', value: b.lastActive ? fmtDate(b.lastActive) : '\u2014' },
            { label: 'E-mail', value: b.email || 'Ikke registreret' },
          ].map((row, i) => (
            <div key={row.label} style={{ display: 'flex', alignItems: 'center',
              padding: '12px 14px',
              borderBottom: i < 2 ? `1px solid ${SS.lineSoft}` : 'none' }}>
              <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                color: SS.inkMuted, minWidth: 100 }}>{row.label}</div>
              <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.ink, flex: 1 }}>
                {row.value || '\u2014'}
              </div>
            </div>
          ))}
        </div>

        {/* Status actions */}
        {status !== 'afventer' && (
          <div style={{ padding: '0 16px' }}>
            {status === 'aktiv' && (
              <button onClick={() => setStatus('pause')} style={{
                width: '100%', padding: '13px 0', marginBottom: 8,
                background: '#fff', color: SS.ink,
                border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 14, cursor: 'pointer',
              }}>S\u00e6t p\u00e5 pause</button>
            )}
            {status === 'pause' && (
              <button onClick={() => setStatus('aktiv')} style={{
                width: '100%', padding: '13px 0', marginBottom: 8,
                background: SS.sage, color: '#fff',
                border: 'none', borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 14, fontWeight: 600, cursor: 'pointer',
              }}>Genaktiv\u00e9r brobygger</button>
            )}
            {!showEndConfirm ? (
              <button onClick={() => setShowEndConfirm(true)} style={{
                width: '100%', padding: '13px 0',
                background: 'transparent', color: SS.rose,
                border: `1px solid ${SS.rose}40`, borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 14, cursor: 'pointer',
              }}>Registrer afslutning\u2026</button>
            ) : (
              <div style={{ background: SS.rose + '10', border: `1.5px solid ${SS.rose}40`,
                borderRadius: SS.r.md, padding: 14 }}>
                <div style={{ fontFamily: SS.sans, fontSize: 13, fontWeight: 600,
                  color: SS.rose, marginBottom: 6 }}>Er du sikker?</div>
                <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
                  marginBottom: 12, lineHeight: 1.5 }}>
                  {b.name.split(' ')[0]} sendes en takke-besked. Aktive forl\u00f8b overf\u00f8res
                  til r\u00e5dgiveren. Denne handling kan ikke fortrydes.
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={() => setEnded(true)} style={{
                    flex: 1, padding: '11px 0', background: SS.rose, color: '#fff',
                    border: 'none', borderRadius: SS.r.md,
                    fontFamily: SS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',
                  }}>Bekr\u00e6ft afslutning</button>
                  <button onClick={() => setShowEndConfirm(false)} style={{
                    flex: 1, padding: '11px 0', background: '#fff', color: SS.inkSoft,
                    border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                    fontFamily: SS.sans, fontSize: 13, cursor: 'pointer',
                  }}>Annuller</button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

"""

# Inject before AdminBrobyggereScreen
old_anchor = "AdminBrobyggereScreen = ({ hovedsaede }) => {"
if old_anchor in html:
    html = html.replace(old_anchor, panel_component + old_anchor, 1)
    results.append("Injected BrobyggerProfilePanel component")
else:
    results.append("ERROR: AdminBrobyggereScreen anchor not found for panel injection")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. SS.rose — ensure it exists in design tokens (used in panel above)
# ═══════════════════════════════════════════════════════════════════════════════
if 'rose:' not in html:
    old_sun = "  sun:         '#E8B84B',"
    new_sun = "  sun:         '#E8B84B',\n  rose:        '#C46A6A',     // error / destructive"
    if old_sun in html:
        html = html.replace(old_sun, new_sun, 1)
        results.append("Added SS.rose token")
    else:
        results.append("WARNING: sun token not found for rose insertion")
else:
    results.append("SS.rose already exists")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Update window exports for new data
# ═══════════════════════════════════════════════════════════════════════════════
old_exports = "window.SS_BROBYGGERE  = SS_BROBYGGERE;"
new_exports = "window.SS_BROBYGGERE  = SS_BROBYGGERE;\nwindow.SS_MEDARBEJDERE= SS_MEDARBEJDERE;"
if old_exports in html and 'window.SS_MEDARBEJDERE= SS_MEDARBEJDERE;' not in html:
    html = html.replace(old_exports, new_exports, 1)
    results.append("Added SS_MEDARBEJDERE to window exports")
else:
    results.append("SS_MEDARBEJDERE already in exports or export missing")

# ═══════════════════════════════════════════════════════════════════════════════
# Write + report
# ═══════════════════════════════════════════════════════════════════════════════
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"File: {len(html):,} bytes\n")
for r in results:
    print(('OK ' if not r.startswith('ERROR') and not r.startswith('WARNING') else '!! ') + r)

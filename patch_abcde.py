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
# A — BrobyggerProfilSheet komponent
# ══════════════════════════════════════════════════════════════════
PROFIL_SHEET = r"""
const BrobyggerProfilSheet = ({ brobyggerId, onClose }) => {
  const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === brobyggerId);
  if (!bb) return null;

  const PRAFIX = ['Ingen', 'Hr.', 'Fru.', 'Mx.', 'Dr.'];
  const [prafix,    setPrafix]    = React.useState(bb.prafix    || 'Ingen');
  const [types,     setTypes]     = React.useState(bb.types     || ['social', 'forening', 'sundhed']);
  const [transport, setTransport] = React.useState(bb.transport || 'gang');
  const [mobil,     setMobil]     = React.useState(bb.mobil     || '');
  const [email,     setEmail]     = React.useState(bb.email     || '');
  const [saved,     setSaved]     = React.useState(false);

  const toggleType = t => setTypes(p =>
    p.includes(t) ? p.filter(x => x !== t) : [...p, t]);

  const handleSave = () => {
    const updated = (window.SoS_BROBYGGERE || []).map(b =>
      b.id === brobyggerId
        ? { ...b, prafix, types, transport,
            mobil: mobil.trim(), email: email.trim() }
        : b
    );
    window.SoS_BROBYGGERE = updated;
    window.SoS_STORE?.save('brobyggere', updated);
    setSaved(true);
    setTimeout(onClose, 900);
  };

  const inpStyle = {
    width: '100%', padding: '11px 14px',
    border: `1px solid ${SoS.line}`, borderRadius: SoS.r.md,
    fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
    outline: 'none', boxSizing: 'border-box', marginBottom: 8,
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 300,
      display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}
      onClick={onClose}>
      <div style={{ background: '#fff', borderRadius: '20px 20px 0 0',
        padding: '24px 20px 44px', maxHeight: '88vh', overflowY: 'auto',
        boxShadow: '0 -4px 32px rgba(0,0,0,0.15)' }}
        onClick={e => e.stopPropagation()}>

        <div style={{ display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', marginBottom: 22 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 22,
            fontWeight: 500, color: SoS.ink }}>Min profil</div>
          <button onClick={onClose} style={{ background: 'none',
            border: 'none', cursor: 'pointer' }}>
            <Icon name="close" size={18} color={SoS.inkMuted}/>
          </button>
        </div>

        {/* Tiltale/præfix */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8,
            textTransform: 'uppercase', marginBottom: 8 }}>Tiltale</div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {['Ingen', 'Hr.', 'Fru.', 'Mx.', 'Dr.'].map(p => (
              <button key={p} onClick={() => setPrafix(p)} style={{
                padding: '7px 14px', borderRadius: SoS.r.sm,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13,
                fontWeight: prafix === p ? 700 : 400,
                background: prafix === p ? SoS.ink : SoS.surface,
                color: prafix === p ? '#fff' : SoS.ink,
                border: `1px solid ${prafix === p ? SoS.ink : SoS.line}` }}>
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Brobygningstyper */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8,
            textTransform: 'uppercase', marginBottom: 8 }}>
            Brobygningstyper
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {[
              { id: 'social',   l: 'Social',   c: SoS.social   },
              { id: 'forening', l: 'Forening',  c: SoS.forening },
              { id: 'sundhed',  l: 'Sundhed',   c: SoS.sundhed  },
            ].map(t => (
              <button key={t.id} onClick={() => toggleType(t.id)} style={{
                flex: 1, padding: '10px 0',
                border: `2px solid ${types.includes(t.id) ? t.c : SoS.line}`,
                borderRadius: SoS.r.sm, cursor: 'pointer', textAlign: 'center',
                background: types.includes(t.id) ? t.c + '15' : '#fff',
                fontFamily: SoS.sans, fontSize: 13,
                fontWeight: types.includes(t.id) ? 700 : 500,
                color: types.includes(t.id) ? t.c : SoS.ink }}>
                {t.l}
              </button>
            ))}
          </div>
        </div>

        {/* Transport */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8,
            textTransform: 'uppercase', marginBottom: 8 }}>Transport</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {[
              { id: 'gang',      l: 'Til fods'          },
              { id: 'cykel',     l: 'Cykel'             },
              { id: 'offentlig', l: 'Offentlig'         },
              { id: 'bil',       l: 'Bil'               },
            ].map(t => (
              <button key={t.id} onClick={() => setTransport(t.id)} style={{
                padding: '8px 14px', borderRadius: SoS.r.sm,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 13,
                fontWeight: transport === t.id ? 700 : 400,
                background: transport === t.id ? SoS.ink : SoS.surface,
                color: transport === t.id ? '#fff' : SoS.ink,
                border: `1px solid ${transport === t.id ? SoS.ink : SoS.line}` }}>
                {t.l}
              </button>
            ))}
          </div>
        </div>

        {/* Kontakt */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8,
            textTransform: 'uppercase', marginBottom: 8 }}>Kontakt</div>
          <input value={mobil} onChange={e => setMobil(e.target.value)}
            placeholder="Mobilnummer" type="tel" style={inpStyle}/>
          <input value={email} onChange={e => setEmail(e.target.value)}
            placeholder="E-mail" type="email" style={{ ...inpStyle, marginBottom: 0 }}/>
        </div>

        <Button full onClick={handleSave} disabled={types.length === 0}>
          {saved ? '✓ Gemt!' : 'Gem profil'}
        </Button>
      </div>
    </div>
  );
};

"""

sub(
    "\n\nconst HomeScreen = ({ user,",
    PROFIL_SHEET + "\n\nconst HomeScreen = ({ user,",
    "A: BrobyggerProfilSheet komponent"
)

# HomeScreen: tilføj profilOpen state
sub(
    "  const [logTarget,    setLogTarget]    = React.useState(null);\n"
    "  const [apptVersion,  setApptVersion]  = React.useState(0);",
    "  const [logTarget,    setLogTarget]    = React.useState(null);\n"
    "  const [apptVersion,  setApptVersion]  = React.useState(0);\n"
    "  const [profilOpen,   setProfilOpen]   = React.useState(false);",
    "A: profilOpen state"
)

# HomeScreen: tilføj profil-knap i TopBar trailing
sub(
    "        trailing={\n"
    "          <button style={{\n"
    "            width: 44, height: 44, borderRadius: 22, background: '#fff',\n"
    "            border: `1px solid ${SoS.line}`, display: 'flex',\n"
    "            alignItems: 'center', justifyContent: 'center', cursor: 'pointer',\n"
    "            position: 'relative',\n"
    "          }}>",
    "        trailing={\n"
    "          <div style={{ display: 'flex', gap: 6 }}>\n"
    "          <button onClick={() => setProfilOpen(true)} style={{\n"
    "            width: 44, height: 44, borderRadius: 22, background: '#fff',\n"
    "            border: `1px solid ${SoS.line}`, display: 'flex',\n"
    "            alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>\n"
    "            <Icon name=\"shield\" size={20} color={SoS.inkMuted}/>\n"
    "          </button>\n"
    "          <button style={{\n"
    "            width: 44, height: 44, borderRadius: 22, background: '#fff',\n"
    "            border: `1px solid ${SoS.line}`, display: 'flex',\n"
    "            alignItems: 'center', justifyContent: 'center', cursor: 'pointer',\n"
    "            position: 'relative',\n"
    "          }}>",
    "A: profilOpen knap i TopBar"
)

# Luk den ekstra div i trailing
sub(
    "            })()}\n"
    "          </button>\n"
    "        }\n"
    "      />\n"
    "\n"
    "      {next ?",
    "            })()}\n"
    "          </button>\n"
    "          </div>\n"
    "        }\n"
    "      />\n"
    "\n"
    "      {next ?",
    "A: luk trailing div"
)

# Tilføj BrobyggerProfilSheet render
sub(
    "      {logTarget && (\n"
    "        <BrobyggerLogModal\n"
    "          aftale={logTarget}\n"
    "          onClose={() => setLogTarget(null)}\n"
    "          onSave={() => { setApptVersion(v => v + 1); setLogTarget(null); }}\n"
    "        />\n"
    "      )}",
    "      {logTarget && (\n"
    "        <BrobyggerLogModal\n"
    "          aftale={logTarget}\n"
    "          onClose={() => setLogTarget(null)}\n"
    "          onSave={() => { setApptVersion(v => v + 1); setLogTarget(null); }}\n"
    "        />\n"
    "      )}\n"
    "      {profilOpen && (\n"
    "        <BrobyggerProfilSheet\n"
    "          brobyggerId={brobyggerId}\n"
    "          onClose={() => setProfilOpen(false)}\n"
    "        />\n"
    "      )}",
    "A: render BrobyggerProfilSheet"
)

# ══════════════════════════════════════════════════════════════════
# B — AfslutForloebModal: opsummering øverst + større dialog
# ══════════════════════════════════════════════════════════════════
sub(
    "      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 420,\n"
    "        padding: 28, boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>",
    "      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 560,\n"
    "        boxShadow: '0 8px 40px rgba(0,0,0,0.18)', maxHeight: '90vh',\n"
    "        display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>\n"
    "        {/* Forløbs-opsummering */}\n"
    "        {(() => {\n"
    "          const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === m.brobyggerId);\n"
    "          const appts = (window.SoS_APPOINTMENTS_BUSY || [])\n"
    "            .filter(a => a.menneskeId === m.id);\n"
    "          const gennemf = appts.filter(a => a.brobyggerLog?.udfald === 'gennemfoert').length;\n"
    "          const started = m.createdAt || m.registeredAt;\n"
    "          const days = started\n"
    "            ? Math.floor((new Date() - new Date(started)) / (1000*60*60*24))\n"
    "            : null;\n"
    "          return (\n"
    "            <div style={{ padding: '14px 24px', background: SoS.ink,\n"
    "              display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 0 }}>\n"
    "              {[\n"
    "                { l: 'Varighed', v: days != null ? `${days} dage` : '—' },\n"
    "                { l: 'M\xf8der', v: String(gennemf) },\n"
    "                { l: 'Brobygger', v: bb ? bb.name.split(' ')[0] : '—' },\n"
    "              ].map((s, i) => (\n"
    "                <div key={i} style={{ textAlign: 'center',\n"
    "                  padding: '10px 8px',\n"
    "                  borderRight: i < 2 ? '1px solid rgba(255,255,255,0.12)' : 'none' }}>\n"
    "                  <div style={{ fontFamily: SoS.mono, fontSize: 18, fontWeight: 700,\n"
    "                    color: '#fff' }}>{s.v}</div>\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 10,\n"
    "                    color: 'rgba(255,255,255,0.55)', marginTop: 2,\n"
    "                    textTransform: 'uppercase', letterSpacing: 0.5 }}>{s.l}</div>\n"
    "                </div>\n"
    "              ))}\n"
    "            </div>\n"
    "          );\n"
    "        })()}\n"
    "        <div style={{ overflowY: 'auto', flex: 1, padding: 24 }}>",
    "B: AfslutForloebModal opsummering + scroll"
)

# Luk den nye scroll-div
sub(
    "        <div style={{ display: 'flex', gap: 10 }}>\n"
    "          <button onClick={onClose}\n"
    "            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,\n"
    "              background: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer' }}>\n"
    "            Annuller\n"
    "          </button>\n"
    "          <button onClick={handleSave} disabled={!aarsag}\n"
    "            style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "              background: aarsag ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "              fontWeight: 600, color: aarsag ? '#fff' : SoS.inkMuted, cursor: aarsag ? 'pointer' : 'default' }}>\n"
    "            Afslut forl\xf8b\n"
    "          </button>\n"
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "};",
    "        </div>\n"
    "        <div style={{ padding: '12px 24px', borderTop: `1px solid ${SoS.line}`,\n"
    "          display: 'flex', gap: 10, flexShrink: 0 }}>\n"
    "          <button onClick={onClose}\n"
    "            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md,\n"
    "              border: `1px solid ${SoS.line}`,\n"
    "              background: 'none', fontFamily: SoS.sans, fontSize: 14,\n"
    "              color: SoS.inkSoft, cursor: 'pointer' }}>\n"
    "            Annuller\n"
    "          </button>\n"
    "          <button onClick={handleSave} disabled={!aarsag}\n"
    "            style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',\n"
    "              background: aarsag ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,\n"
    "              fontWeight: 600, color: aarsag ? '#fff' : SoS.inkMuted,\n"
    "              cursor: aarsag ? 'pointer' : 'default' }}>\n"
    "            Afslut forl\xf8b\n"
    "          </button>\n"
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "};",
    "B: AfslutForloebModal sticky footer"
)

# ══════════════════════════════════════════════════════════════════
# C — TilknytBrobyggerModal: HQ-bevidst sortering + type-chip
# ══════════════════════════════════════════════════════════════════
sub(
    "  const alle    = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');\n"
    "  const ledige  = alle.filter(b => b.openShifts > 0);\n"
    "  const optaget = alle.filter(b => b.openShifts === 0);",
    "  const _alle   = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');\n"
    "  // HQ-prioritering: brobyggere fra personens HQ f\xf8rst\n"
    "  const alle = [..._alle].sort((a, b) => {\n"
    "    const aMatch = !a.hq || a.hq === m.hq;\n"
    "    const bMatch = !b.hq || b.hq === m.hq;\n"
    "    return aMatch === bMatch ? 0 : aMatch ? -1 : 1;\n"
    "  });\n"
    "  const ledige  = alle.filter(b => b.openShifts > 0);\n"
    "  const optaget = alle.filter(b => b.openShifts === 0);",
    "C: TilknytBrobyggerModal HQ-sortering"
)

# Tilføj type-chip og HQ-chip til brobygger-kortene (i visListe.map)
sub(
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 1 }}>\n"
    "                    {myAppts.length} aktive aftaler\n"
    "                    {mode === 'ledig' && ` \xb7 ${b.openShifts} ledig${b.openShifts !== 1 ? 'e' : ''}`}\n"
    "                  </div>",
    "                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 3,\n"
    "                    flexWrap: 'wrap' }}>\n"
    "                    <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>\n"
    "                      {myAppts.length} aktive\n"
    "                      {mode === 'ledig' && ` \xb7 ${b.openShifts} ledig`}\n"
    "                    </span>\n"
    "                    {b.hq && (\n"
    "                      <span style={{ padding: '1px 6px',\n"
    "                        background: b.hq === m.hq ? SoS.accent + '18' : SoS.surface,\n"
    "                        color: b.hq === m.hq ? SoS.accent : SoS.inkMuted,\n"
    "                        borderRadius: SoS.r.sm, fontFamily: SoS.mono,\n"
    "                        fontSize: 9, fontWeight: 700 }}>\n"
    "                        {b.hq}\n"
    "                      </span>\n"
    "                    )}\n"
    "                    {b.types && m.type && b.types.includes(m.type) && (\n"
    "                      <span style={{ padding: '1px 6px',\n"
    "                        background: SoS.green + '18', color: SoS.green,\n"
    "                        borderRadius: SoS.r.sm, fontFamily: SoS.sans,\n"
    "                        fontSize: 9, fontWeight: 700 }}>\n"
    "                        Matcher type\n"
    "                      </span>\n"
    "                    )}\n"
    "                  </div>",
    "C: HQ + type chips i brobygger-kort"
)

# ══════════════════════════════════════════════════════════════════
# D — DesktopMennesker: tilføj HQ-filter + dage-ventet filter
# ══════════════════════════════════════════════════════════════════
sub(
    "  const [typeFilter,   setTypeFilter]   = React.useState('alle');\n"
    "  const [statusFilter, setStatusFilter] = React.useState('alle');",
    "  const [typeFilter,   setTypeFilter]   = React.useState('alle');\n"
    "  const [statusFilter, setStatusFilter] = React.useState('alle');\n"
    "  const [hqFilter,     setHqFilter]     = React.useState('alle');",
    "D: hqFilter state i DesktopMennesker"
)

sub(
    "    if (typeFilter !== 'alle' && m.type !== typeFilter) return false;\n"
    "    if (statusFilter !== 'alle' && m.status !== statusFilter) return false;\n"
    "    return true;",
    "    if (typeFilter !== 'alle' && m.type !== typeFilter) return false;\n"
    "    if (statusFilter !== 'alle' && m.status !== statusFilter) return false;\n"
    "    if (hqFilter !== 'alle' && m.hq !== hqFilter) return false;\n"
    "    return true;",
    "D: hqFilter i filterfunktion"
)

# Tilføj HQ-filter chips efter eksisterende filter-rækker
sub(
    "      {/* Filtre */}\n"
    "      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>\n"
    "        {['alle', 'sundhed', 'forening', 'social'].map(f => {",
    "      {/* Filtre */}\n"
    "      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>\n"
    "        {['alle', 'sundhed', 'forening', 'social'].map(f => {",
    "D: filter marginBottom"
)

# Tilføj HQ-filter række efter status-filter rækken
sub(
    "      {/* Menneske-liste */}",
    "      {/* HQ + dage filter */}\n"
    "      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>\n"
    "        <button onClick={() => setHqFilter('alle')} style={{\n"
    "          padding: '4px 10px', borderRadius: SoS.r.sm,\n"
    "          background: hqFilter === 'alle' ? SoS.ink : SoS.surface,\n"
    "          color: hqFilter === 'alle' ? '#fff' : SoS.inkSoft,\n"
    "          border: `1px solid ${hqFilter === 'alle' ? SoS.ink : SoS.line}`,\n"
    "          fontFamily: SoS.sans, fontSize: 11, fontWeight: hqFilter === 'alle' ? 700 : 400,\n"
    "          cursor: 'pointer' }}>Alle HQ</button>\n"
    "        {SoS_HOVEDSAEDER.map(hq => (\n"
    "          <button key={hq} onClick={() => setHqFilter(hq)} style={{\n"
    "            padding: '4px 10px', borderRadius: SoS.r.sm,\n"
    "            background: hqFilter === hq ? SoS.ink : SoS.surface,\n"
    "            color: hqFilter === hq ? '#fff' : SoS.inkSoft,\n"
    "            border: `1px solid ${hqFilter === hq ? SoS.ink : SoS.line}`,\n"
    "            fontFamily: SoS.sans, fontSize: 11,\n"
    "            fontWeight: hqFilter === hq ? 700 : 400,\n"
    "            cursor: 'pointer' }}>{hq}</button>\n"
    "        ))}\n"
    "      </div>\n"
    "\n"
    "      {/* Menneske-liste */}",
    "D: HQ filter chips i DesktopMennesker"
)

# ══════════════════════════════════════════════════════════════════
# E — ExportReport: SSLogo + organisation i preview header
# ══════════════════════════════════════════════════════════════════
sub(
    "        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,\n"
    "          letterSpacing: -0.2 }}>Social Return on Investment</div>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 12, opacity: 0.7, marginTop: 2 }}>\n"
    "          {REPORT_DATA.period} \xb7 Alle hoveds\xe6der \xb7 Udkast til Velux Fonden\n"
    "        </div>",
    "        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>\n"
    "          <SSLogo size={32} bg='rgba(255,255,255,0.2)'/>\n"
    "          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n"
    "            opacity: 0.7, textTransform: 'uppercase', letterSpacing: 0.8 }}>\n"
    "            Social Sundhed\n"
    "          </div>\n"
    "        </div>\n"
    "        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,\n"
    "          letterSpacing: -0.2 }}>Social Return on Investment</div>\n"
    "        <div style={{ fontFamily: SoS.sans, fontSize: 12, opacity: 0.7, marginTop: 2 }}>\n"
    "          {REPORT_DATA.period} \xb7 Alle hoveds\xe6der \xb7 Udkast til Velux Fonden\n"
    "        </div>",
    "E: SSLogo i ExportReport header"
)

# Tilføj print-knap i ExportReport
sub(
    "          <Icon name={exported ? 'check' : 'download'} size={14} color=\"#fff\" weight={2.3}/>\n"
    "            {exported ? 'Sendt!' : 'Eksport\xe9r'}\n"
    "          </button>",
    "          <Icon name={exported ? 'check' : 'download'} size={14} color=\"#fff\" weight={2.3}/>\n"
    "            {exported ? 'Sendt!' : 'Eksport\xe9r'}\n"
    "          </button>\n"
    "          <button onClick={() => window.print()} style={{\n"
    "            background: 'rgba(255,255,255,0.15)', color: '#fff',\n"
    "            border: '1px solid rgba(255,255,255,0.3)',\n"
    "            padding: '6px 14px', borderRadius: 999, cursor: 'pointer',\n"
    "            fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,\n"
    "            display: 'flex', alignItems: 'center', gap: 4 }}>\n"
    "            <Icon name='note' size={13} color='#fff'/>\n"
    "            Print\n"
    "          </button>",
    "E: print-knap i ExportReport"
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

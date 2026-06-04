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

# ═══════════════════════════════════════════════════════════════════════════
# 1. DesktopBrugerstyring — ny placeholder-komponent (admin only)
#    Indsættes FØR DesktopView
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "const DesktopView = ({ user, ownHq, isAdmin, onClose }) => {",
    """const DesktopBrugerstyring = () => {
  const [staff,    setStaff]    = React.useState(window.SoS_MEDARBEJDERE || []);
  const [invEmail, setInvEmail] = React.useState('');
  const [invNavn,  setInvNavn]  = React.useState('');
  const [invRole,  setInvRole]  = React.useState('raadgiver');
  const [sent,     setSent]     = React.useState(false);

  const ROLLE_LABELS = {
    brobygger: 'Brobygger', raadgiver: 'Rådgiver',
    leder: 'Leder', admin: 'Admin',
  };
  const ROLLE_COLORS = {
    brobygger: SoS.sage, raadgiver: SoS.sky, leder: SoS.orange, admin: '#C62828',
  };

  const toggleActive = (id) => {
    const updated = staff.map(u => u.id === id ? { ...u, active: u.active === false ? true : false } : u);
    setStaff(updated);
    window.SoS_MEDARBEJDERE = updated;
    window.SoS_STORE?.save('medarbejdere', updated);
  };
  const changeRole = (id, role) => {
    const updated = staff.map(u => u.id === id ? { ...u, role } : u);
    setStaff(updated);
    window.SoS_MEDARBEJDERE = updated;
    window.SoS_STORE?.save('medarbejdere', updated);
  };
  const sendInvite = () => {
    if (!invEmail || !invNavn) return;
    setSent(true);
    setTimeout(() => { setSent(false); setInvEmail(''); setInvNavn(''); }, 2500);
  };

  return (
    <div style={{ maxWidth: 720 }}>

      {/* Aktive brugere */}
      <DSCard style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
          color: SoS.inkMuted, letterSpacing: 1, textTransform: 'uppercase',
          marginBottom: 14 }}>Brugere ({staff.length})</div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {['Navn', 'Email', 'HQ', 'Rolle', 'Status', ''].map((h, i) => (
                <th key={i} style={{ textAlign: 'left', fontFamily: SoS.sans, fontSize: 10,
                  fontWeight: 700, color: SoS.inkMuted, letterSpacing: 0.6,
                  textTransform: 'uppercase', padding: '0 8px 10px',
                  borderBottom: `1px solid ${SoS.line}` }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {staff.map((u, i) => {
              const isInactive = u.active === false;
              return (
                <tr key={u.id} style={{ opacity: isInactive ? 0.5 : 1 }}>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                    {u.name}
                  </td>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {u.email}
                  </td>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}`,
                    fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {u.hq || '—'}
                  </td>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
                    <select value={u.role || 'raadgiver'}
                      onChange={e => changeRole(u.id, e.target.value)}
                      disabled={isInactive}
                      style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                        color: ROLLE_COLORS[u.role] || SoS.inkSoft,
                        background: (ROLLE_COLORS[u.role] || SoS.inkSoft) + '15',
                        border: 'none', borderRadius: 999, padding: '4px 10px',
                        cursor: isInactive ? 'default' : 'pointer' }}>
                      {Object.entries(ROLLE_LABELS).map(([v, l]) => (
                        <option key={v} value={v}>{l}</option>
                      ))}
                    </select>
                  </td>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
                    <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                      color: isInactive ? SoS.inkMuted : SoS.sage }}>
                      {isInactive ? 'Inaktiv' : 'Aktiv'}
                    </span>
                  </td>
                  <td style={{ padding: '10px 8px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
                    <button onClick={() => toggleActive(u.id)} style={{
                      padding: '4px 10px', borderRadius: 999, cursor: 'pointer',
                      fontFamily: SoS.sans, fontSize: 11, fontWeight: 600, border: 'none',
                      background: isInactive ? SoS.sageSoft : '#FFE8E0',
                      color: isInactive ? SoS.sage : '#C0392B' }}>
                      {isInactive ? 'Genaktiver' : 'Deaktiver'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </DSCard>

      {/* Inviter ny medarbejder */}
      <DSCard>
        <div style={{ fontFamily: SoS.mono, fontSize: 9.5, fontWeight: 600,
          color: SoS.inkMuted, letterSpacing: 1, textTransform: 'uppercase',
          marginBottom: 14 }}>Inviter ny bruger</div>
        {sent ? (
          <div style={{ padding: 20, textAlign: 'center', background: SoS.sageSoft,
            borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, color: SoS.sage }}>
            ✓ Invitation sendt til {invEmail}
          </div>
        ) : (
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: '1 1 180px' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 4 }}>
                Navn
              </div>
              <input value={invNavn} onChange={e => setInvNavn(e.target.value)}
                placeholder="Fornavn Efternavn"
                style={{ width: '100%', padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13,
                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, outline: 'none',
                  boxSizing: 'border-box' }}/>
            </div>
            <div style={{ flex: '1 1 220px' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 4 }}>
                Email
              </div>
              <input value={invEmail} onChange={e => setInvEmail(e.target.value)}
                placeholder="navn@socialsundhed.org" type="email"
                style={{ width: '100%', padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13,
                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, outline: 'none',
                  boxSizing: 'border-box' }}/>
            </div>
            <div style={{ flex: '0 0 140px' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 4 }}>
                Rolle
              </div>
              <select value={invRole} onChange={e => setInvRole(e.target.value)}
                style={{ width: '100%', padding: '9px 10px', fontFamily: SoS.sans, fontSize: 13,
                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                  background: '#fff', outline: 'none' }}>
                {Object.entries(ROLLE_LABELS).filter(([v]) => v !== 'brobygger').map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <button onClick={sendInvite}
              disabled={!invEmail || !invNavn}
              style={{ padding: '9px 20px', borderRadius: SoS.r.sm, border: 'none',
                background: invEmail && invNavn ? SoS.accent : SoS.lineSoft,
                color: invEmail && invNavn ? '#fff' : SoS.inkMuted,
                fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                cursor: invEmail && invNavn ? 'pointer' : 'default', flexShrink: 0 }}>
              Send invitation
            </button>
          </div>
        )}
      </DSCard>

    </div>
  );
};

const DesktopView = ({ user, ownHq, isAdmin, canRapport = false, canUserMgmt = false, onClose }) => {""",
    "DesktopBrugerstyring: ny komponent + DesktopView udvid signatur"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. DesktopView — initial viewingHq state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  const [viewingHq, setViewingHq] = React.useState(isAdmin ? 'Alle hovedsæder' : ownHq);",
    "  const [viewingHq, setViewingHq] = React.useState(canRapport ? 'Alle hovedsæder' : ownHq);",
    "DesktopView: initial HQ baseret paa canRapport"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Sidebar portal-label
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "                {isAdmin ? 'ADMINISTRATION' : 'RÅDGIVER-PORTAL'}",
    "                {canUserMgmt ? 'ADMINISTRATION' : canRapport ? 'LEDELSE' : 'RÅDGIVER-PORTAL'}",
    "DesktopView sidebar: rollebaseret portal-label"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. Sidebar nav: rapport + brugerstyring
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "              ].concat(isAdmin ? [{ k: 'rapport', l: 'Rapport & eksport', i: 'note' }] : []).map(n => (",
    "              ].concat(canRapport ? [{ k: 'rapport', l: 'Rapport & eksport', i: 'note' }] : [])\n              .concat(canUserMgmt ? [{ k: 'brugerstyring', l: 'Brugerstyring', i: 'shield' }] : []).map(n => (",
    "DesktopView sidebar: rapport (canRapport) + brugerstyring (canUserMgmt)"
)

# ═══════════════════════════════════════════════════════════════════════════
# 5. Sidebar footer rolle-tekst
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "              {isAdmin ? 'Admin' : ownHq}",
    "              {canUserMgmt ? 'Admin' : canRapport ? 'Leder' : ownHq}",
    "DesktopView sidebar footer: rollebaseret tekst"
)

# ═══════════════════════════════════════════════════════════════════════════
# 6. Top-bar rolle og HQ
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "                {isAdmin ? 'Admin' : 'Rådgiver'} · {viewingHq}",
    "                {canUserMgmt ? 'Admin' : canRapport ? 'Leder' : 'Rådgiver'} · {viewingHq}",
    "DesktopView top-bar: rollebaseret label"
)

# ═══════════════════════════════════════════════════════════════════════════
# 7. HQ select — "Alle" kun for canRapport
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "                {isAdmin && <option value=\"Alle hovedsæder\">Alle hovedsæder</option>}",
    "                {canRapport && <option value=\"Alle hovedsæder\">Alle hovedsæder</option>}",
    "DesktopView HQ select: Alle for canRapport"
)

# ═══════════════════════════════════════════════════════════════════════════
# 8. Eksport-knap — kun for canRapport
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """              <button onClick={handleDeskExport} style={{ padding: '7px 14px', borderRadius: SoS.r.sm,
                background: deskExported ? SoS.green : SoS.ink, color: '#fff', border: 'none',
                borderRadius: SoS.r.sm,
                fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 6, transition: 'background 0.2s' }}>
                <Icon name={deskExported ? 'check' : 'download'} size={12} color="#fff" weight={2.3}/>
                {deskExported ? 'Eksporteret!' : 'Eksportér'}
              </button>""",
    """              {canRapport && (
                <button onClick={handleDeskExport} style={{ padding: '7px 14px', borderRadius: SoS.r.sm,
                  background: deskExported ? SoS.green : SoS.ink, color: '#fff', border: 'none',
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 6, transition: 'background 0.2s' }}>
                  <Icon name={deskExported ? 'check' : 'download'} size={12} color="#fff" weight={2.3}/>
                  {deskExported ? 'Eksporteret!' : 'Eksportér'}
                </button>
              )}""",
    "DesktopView: eksport-knap kun for canRapport"
)

# ═══════════════════════════════════════════════════════════════════════════
# 9. DesktopDashboard — skift isAdmin til canRapport
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "          {section === 'dashboard' && <DesktopDashboard viewingHq={viewingHq} isAdmin={isAdmin}/>}",
    "          {section === 'dashboard' && <DesktopDashboard viewingHq={viewingHq} canRapport={canRapport}/>}",
    "DesktopView: DesktopDashboard faar canRapport"
)

# ═══════════════════════════════════════════════════════════════════════════
# 10. Tilfoej brugerstyring sektion-render
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "          {section === 'rapport' && <DesktopRapport/>}",
    "          {section === 'rapport' && canRapport && <DesktopRapport/>}\n          {section === 'brugerstyring' && canUserMgmt && <DesktopBrugerstyring/>}",
    "DesktopView: rapport guarded + brugerstyring sektion"
)

# ═══════════════════════════════════════════════════════════════════════════
# 11. Section-titel: tilfoej brugerstyring
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport' }[section]}",
    "                   kalender: 'Kalender', sroi: 'Effekt & Dokumentation', rapport: 'Rapport & eksport', brugerstyring: 'Brugerstyring' }[section]}",
    "DesktopView: sektion-titel for brugerstyring"
)

# ═══════════════════════════════════════════════════════════════════════════
# 12. DesktopDashboard signatur — isAdmin → canRapport
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "const DesktopDashboard = ({ viewingHq, isAdmin }) => (",
    "const DesktopDashboard = ({ viewingHq, canRapport }) => (",
    "DesktopDashboard: parameter isAdmin → canRapport"
)

# ═══════════════════════════════════════════════════════════════════════════
# 13. AdminSettings — tilfoej canRapport prop + opdater SROI-check
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "const AdminSettings = ({ currentHq, ownHq, onPick, onClose, isAdmin }) => {",
    "const AdminSettings = ({ currentHq, ownHq, onPick, onClose, isAdmin, canRapport = false }) => {",
    "AdminSettings: tilfoej canRapport prop"
)

sub(
    "        {section === 'sroi' && isAdmin && (<>",
    "        {section === 'sroi' && canRapport && (<>",
    "AdminSettings: SROI vises for canRapport (leder + admin)"
)

# ═══════════════════════════════════════════════════════════════════════════
# 14. AppWithTweaks — tilfoej leder til AdminMobile + AdminSettings
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  } else if (activeRole === \"admin\" || activeRole === \"raadgiver\") {\n    if (settingsOpen) {\n      content = <AdminSettings\n        currentHq={viewingHq}\n        ownHq=\"Aarhus\"\n        isAdmin={activeRole === \"admin\"}\n        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}\n        onClose={() => setSettingsOpen(false)} />;\n    } else {\n      content = <AdminMobile\n        user={user}\n        viewingHq={viewingHq}\n        ownHq=\"Aarhus\"\n        isAdmin={activeRole === \"admin\"}\n        onOpenSettings={() => setSettingsOpen(true)}\n        onOpenIntake={() => setTweak(\"flow\", \"intake\")}\n        onOpenMatching={() => setTweak(\"flow\", \"matching\")}\n        onOpenMessages={(id) => setMsgOpenId(id)}\n        onOpenDesktop={() => setDesktopMode(true)} />;",
    "  } else if (activeRole === \"admin\" || activeRole === \"raadgiver\" || activeRole === \"leder\") {\n    const _canRapport = activeRole === \"admin\" || activeRole === \"leder\";\n    if (settingsOpen) {\n      content = <AdminSettings\n        currentHq={viewingHq}\n        ownHq=\"Aarhus\"\n        isAdmin={activeRole === \"admin\"}\n        canRapport={_canRapport}\n        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}\n        onClose={() => setSettingsOpen(false)} />;\n    } else {\n      content = <AdminMobile\n        user={user}\n        viewingHq={viewingHq}\n        ownHq=\"Aarhus\"\n        isAdmin={activeRole === \"admin\"}\n        onOpenSettings={() => setSettingsOpen(true)}\n        onOpenIntake={() => setTweak(\"flow\", \"intake\")}\n        onOpenMatching={() => setTweak(\"flow\", \"matching\")}\n        onOpenMessages={(id) => setMsgOpenId(id)}\n        onOpenDesktop={() => setDesktopMode(true)} />;",
    "AppWithTweaks: tilfoej leder til mobile admin-flow"
)

# ═══════════════════════════════════════════════════════════════════════════
# 15. AppWithTweaks — tilfoej leder til desktop-check
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "  if (desktopMode && (tweaks.role === \"admin\" || tweaks.role === \"raadgiver\")) {",
    "  if (desktopMode && (tweaks.role === \"admin\" || tweaks.role === \"raadgiver\" || tweaks.role === \"leder\")) {",
    "AppWithTweaks: leder faar desktop adgang"
)

# ═══════════════════════════════════════════════════════════════════════════
# 16. DesktopView call — tilfoej canRapport + canUserMgmt
# ═══════════════════════════════════════════════════════════════════════════
sub(
    "          <DesktopView user={user} ownHq=\"Aarhus\" isAdmin={tweaks.role === \"admin\"} onClose={() => setDesktopMode(false)} />",
    "          <DesktopView user={user} ownHq=\"Aarhus\" isAdmin={tweaks.role === \"admin\"} canRapport={tweaks.role === \"leder\" || tweaks.role === \"admin\"} canUserMgmt={tweaks.role === \"admin\"} onClose={() => setDesktopMode(false)} />",
    "AppWithTweaks: DesktopView faar canRapport + canUserMgmt"
)

# ═══════════════════════════════════════════════════════════════════════════
# 17. Desktop TweaksPanel — tilfoej leder option
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """            <TweakRadio label="Rolle" value={tweaks.role}
              options={[
                { value: "brobygger", label: "Brobygger" },
                { value: "raadgiver", label: "Raadgiver" },
                { value: "admin", label: "Admin" },
              ]}
              onChange={(v) => setTweak("role", v)}/>""",
    """            <TweakRadio label="Rolle" value={tweaks.role}
              options={[
                { value: "brobygger", label: "Brobygger" },
                { value: "raadgiver", label: "Raadgiver" },
                { value: "leder",     label: "Leder / Landssekretariat" },
                { value: "admin",     label: "Admin" },
              ]}
              onChange={(v) => setTweak("role", v)}/>""",
    "Desktop TweaksPanel: tilfoej leder"
)

# ═══════════════════════════════════════════════════════════════════════════
# 18. Mobil TweaksPanel — tilfoej leder option
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """          <TweakRadio label="Rolle" value={tweaks.role}
            options={[
              { value: "brobygger", label: "Brobygger (frivillig)" },
              { value: "raadgiver", label: "Raadgiver (eget hq)" },
              { value: "admin", label: "Admin (alle hq)" },
            ]}
            onChange={(v) => setTweak("role", v)}
          />""",
    """          <TweakRadio label="Rolle" value={tweaks.role}
            options={[
              { value: "brobygger", label: "Brobygger (frivillig)" },
              { value: "raadgiver", label: "Raadgiver (eget hq)" },
              { value: "leder",     label: "Leder / Landssekretariat" },
              { value: "admin",     label: "Admin (alle hq)" },
            ]}
            onChange={(v) => setTweak("role", v)}
          />""",
    "Mobil TweaksPanel: tilfoej leder"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ─────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

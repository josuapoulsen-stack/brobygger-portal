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

# ══════════════════════════════════════════════════════════════════════
# 1. AdminMobileTabBar — tilføj badges prop
# ══════════════════════════════════════════════════════════════════════
sub(
    "const AdminMobileTabBar = ({ active, onChange, isAdmin }) => {",
    "const AdminMobileTabBar = ({ active, onChange, isAdmin, badges = {} }) => {",
    "TabBar: badges prop"
)

# ══════════════════════════════════════════════════════════════════════
# 2. TabBar render — badge dot på ikon
# ══════════════════════════════════════════════════════════════════════
sub(
    "            {on && <div style={{ position: 'absolute', top: 0, width: 24, height: 2, background: SoS.accent }}/>}\n            <Icon name={t.icon} size={21} color={on ? SoS.accent : SoS.inkMuted} weight={on ? 2 : 1.7}/>\n            <div style={{ fontFamily: SoS.mono, fontSize: 8, fontWeight: 600,\n              color: on ? SoS.ink : SoS.inkMuted, letterSpacing: 0.3, marginTop: 4 }}>\n              {t.label.toUpperCase()}\n            </div>",
    "            {on && <div style={{ position: 'absolute', top: 0, width: 24, height: 2, background: SoS.accent }}/>}\n            <div style={{ position: 'relative', display: 'inline-flex' }}>\n              <Icon name={t.icon} size={21} color={on ? SoS.accent : SoS.inkMuted} weight={on ? 2 : 1.7}/>\n              {badges[t.id] > 0 && (\n                <div style={{ position: 'absolute', top: -3, right: -6, minWidth: 14, height: 14,\n                  borderRadius: 7, background: SoS.accent, border: `1.5px solid ${SoS.paper}`,\n                  display: 'flex', alignItems: 'center', justifyContent: 'center',\n                  fontFamily: SoS.sans, fontSize: 9, fontWeight: 700, color: '#fff', padding: '0 3px' }}>\n                  {badges[t.id] > 9 ? '9+' : badges[t.id]}\n                </div>\n              )}\n            </div>\n            <div style={{ fontFamily: SoS.mono, fontSize: 8, fontWeight: 600,\n              color: on ? SoS.ink : SoS.inkMuted, letterSpacing: 0.3, marginTop: 4 }}>\n              {t.label.toUpperCase()}\n            </div>",
    "TabBar: badge dot"
)

# ══════════════════════════════════════════════════════════════════════
# 3. AdminMobile — beregn beskedBadge
# ══════════════════════════════════════════════════════════════════════
sub(
    "  const title = TAB_TITLES[tab] || 'Oversigt';",
    "  const title = TAB_TITLES[tab] || 'Oversigt';\n  const beskedBadge = (() => {\n    try {\n      const msgs = JSON.parse(localStorage.getItem('sos_beskeder') || '[]');\n      const myRole = isAdmin ? 'admin' : 'raadgiver';\n      return msgs.filter(m => !m.laest && m.til === myRole).length;\n    } catch { return 0; }\n  })();",
    "AdminMobile: beskedBadge"
)

# ══════════════════════════════════════════════════════════════════════
# 4. AdminMobile — send badges til TabBar
# ══════════════════════════════════════════════════════════════════════
sub(
    "<AdminMobileTabBar active={tab} onChange={setTab} isAdmin={isAdmin}/>",
    "<AdminMobileTabBar active={tab} onChange={setTab} isAdmin={isAdmin} badges={{ beskeder: beskedBadge }}/>",
    "AdminMobile: send badges"
)

# ══════════════════════════════════════════════════════════════════════
# 5. Oversigt — rolle-bevidste hurtige handlinger
# ══════════════════════════════════════════════════════════════════════
match_prompt_old = (
    "            {/* Match-prompt */}\n"
    "            {pendingMatches > 0 && (\n"
    "              <button onClick={onOpenMatching} style={{\n"
    "                margin: '12px 22px 0', width: 'calc(100% - 44px)',\n"
    "                display: 'flex', alignItems: 'center', justifyContent: 'space-between',\n"
    "                padding: '13px 16px', background: SoS.ink, border: 'none',\n"
    "                borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "              }}>\n"
    "                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>\n"
    "                  <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                    stroke=\"#fff\" strokeWidth=\"1.8\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                    <circle cx=\"7.5\" cy=\"7.5\" r=\"3\"/>\n"
    "                    <circle cx=\"16.5\" cy=\"7.5\" r=\"3\"/>\n"
    "                    <path d=\"M2.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5\"/>\n"
    "                    <path d=\"M11.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5\"/>\n"
    "                  </svg>\n"
    "                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: '#fff' }}>\n"
    "                    {pendingMatches} {pendingMatches === 1 ? 'menneske venter' : 'mennesker venter'} p\xe5 match\n"
    "                  </span>\n"
    "                </div>\n"
    "                <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                  stroke={SoS.accent} strokeWidth=\"2\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                  <line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"/>\n"
    "                  <polyline points=\"12 5 19 12 12 19\"/>\n"
    "                </svg>\n"
    "              </button>\n"
    "            )}"
)

match_prompt_new = (
    "            {/* Hurtige handlinger */}\n"
    "            {isAdmin && pendingMatches > 0 && (\n"
    "              <button onClick={onOpenMatching} style={{\n"
    "                margin: '12px 22px 0', width: 'calc(100% - 44px)',\n"
    "                display: 'flex', alignItems: 'center', justifyContent: 'space-between',\n"
    "                padding: '13px 16px', background: SoS.ink, border: 'none',\n"
    "                borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "              }}>\n"
    "                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>\n"
    "                  <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                    stroke=\"#fff\" strokeWidth=\"1.8\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                    <circle cx=\"7.5\" cy=\"7.5\" r=\"3\"/>\n"
    "                    <circle cx=\"16.5\" cy=\"7.5\" r=\"3\"/>\n"
    "                    <path d=\"M2.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5\"/>\n"
    "                    <path d=\"M11.5 19c0-3.3 2.2-5.5 5-5.5s5 2.2 5 5.5\"/>\n"
    "                  </svg>\n"
    "                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: '#fff' }}>\n"
    "                    {pendingMatches} {pendingMatches === 1 ? 'menneske venter' : 'mennesker venter'} p\xe5 match\n"
    "                  </span>\n"
    "                </div>\n"
    "                <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                  stroke={SoS.accent} strokeWidth=\"2\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                  <line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"/>\n"
    "                  <polyline points=\"12 5 19 12 12 19\"/>\n"
    "                </svg>\n"
    "              </button>\n"
    "            )}\n"
    "            {!isAdmin && (\n"
    "              <div style={{ margin: '12px 22px 0', display: 'flex', gap: 8 }}>\n"
    "                <button onClick={onOpenIntake} style={{\n"
    "                  flex: 1, padding: '13px 14px', background: SoS.ink, border: 'none',\n"
    "                  borderRadius: SoS.r.sm, cursor: 'pointer', textAlign: 'left',\n"
    "                  display: 'flex', alignItems: 'center', gap: 8,\n"
    "                }}>\n"
    "                  <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\"\n"
    "                    stroke=\"#fff\" strokeWidth=\"2.2\" strokeLinecap=\"round\" strokeLinejoin=\"round\">\n"
    "                    <line x1=\"12\" y1=\"5\" x2=\"12\" y2=\"19\"/>\n"
    "                    <line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"/>\n"
    "                  </svg>\n"
    "                  <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: '#fff' }}>\n"
    "                    Registr\xe9r ny person\n"
    "                  </span>\n"
    "                </button>\n"
    "                {(() => {\n"
    "                  const afvHq = Object.values(window.SoS_MENNESKER || {})\n"
    "                    .filter(m => (m.status === 'afventer' || m.status === 'venter') && m.hq === viewingHq).length;\n"
    "                  if (afvHq === 0) return null;\n"
    "                  return (\n"
    "                    <div style={{ padding: '10px 14px', background: SoS.amber + '20',\n"
    "                      border: `1px solid ${SoS.amber}40`, borderRadius: SoS.r.sm, flexShrink: 0,\n"
    "                      display: 'flex', flexDirection: 'column', justifyContent: 'center',\n"
    "                      textAlign: 'center', minWidth: 64 }}>\n"
    "                      <div style={{ fontFamily: SoS.mono, fontSize: 20, fontWeight: 700,\n"
    "                        color: SoS.amber, lineHeight: 1 }}>{afvHq}</div>\n"
    "                      <div style={{ fontFamily: SoS.sans, fontSize: 9, color: SoS.amber,\n"
    "                        textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 3 }}>afventer</div>\n"
    "                    </div>\n"
    "                  );\n"
    "                })()}\n"
    "              </div>\n"
    "            )}"
)
sub(match_prompt_old, match_prompt_new, "Oversigt: rolle-handlinger")

# ══════════════════════════════════════════════════════════════════════
# 6. AppWithTweaks — showOnboarding state
# ══════════════════════════════════════════════════════════════════════
sub(
    "  const [showPWA, setShowPWA] = useState(true);\n  const [desktopMode, setDesktopMode] = useState(false);",
    "  const [showPWA, setShowPWA] = useState(true);\n  const [desktopMode, setDesktopMode] = useState(false);\n  const [showOnboarding, setShowOnboarding] = useState(false);",
    "AppWithTweaks: showOnboarding state"
)

# ══════════════════════════════════════════════════════════════════════
# 7. AppWithTweaks — useEffect for auto-onboarding
# ══════════════════════════════════════════════════════════════════════
sub(
    (
        "  useEffect(() => {\n"
        "    setScreen(\"hjem\");\n"
        "    setDetailId(null);\n"
        "    setSettingsOpen(false);\n"
        "    if (activeRole === \"brobygger\") {\n"
        "      setDesktopMode(false);\n"
        "      // Nulstil til erfaren-tilstand (Maja) n\xe5r man skifter til brobygger\n"
        "      if (tweaks.experience === \"new\") setTweak(\"experience\", \"experienced\");\n"
        "    }\n"
        "  }, [activeRole]);"
    ),
    (
        "  useEffect(() => {\n"
        "    setScreen(\"hjem\");\n"
        "    setDetailId(null);\n"
        "    setSettingsOpen(false);\n"
        "    if (activeRole === \"brobygger\") {\n"
        "      setDesktopMode(false);\n"
        "      // Nulstil til erfaren-tilstand (Maja) n\xe5r man skifter til brobygger\n"
        "      if (tweaks.experience === \"new\") setTweak(\"experience\", \"experienced\");\n"
        "    }\n"
        "  }, [activeRole]);\n"
        "\n"
        "  useEffect(() => {\n"
        "    if (activeRole === 'brobygger' && !localStorage.getItem('sos_onboarding_done')) {\n"
        "      setShowOnboarding(true);\n"
        "    } else {\n"
        "      setShowOnboarding(false);\n"
        "    }\n"
        "  }, [activeRole]);"
    ),
    "AppWithTweaks: auto-onboarding useEffect"
)

# ══════════════════════════════════════════════════════════════════════
# 8. AppWithTweaks — content branch for showOnboarding
# ══════════════════════════════════════════════════════════════════════
sub(
    "  } else if (tweaks.flow === \"onboarding\") {\n    content = <OnboardingWizard onClose={() => setTweak(\"flow\", \"none\")} />;",
    (
        "  } else if (tweaks.flow === \"onboarding\") {\n"
        "    content = <OnboardingWizard onClose={() => setTweak(\"flow\", \"none\")} />;\n"
        "  } else if (showOnboarding) {\n"
        "    content = <OnboardingWizard onClose={() => {\n"
        "      localStorage.setItem('sos_onboarding_done', '1');\n"
        "      setShowOnboarding(false);\n"
        "    }} />;"
    ),
    "AppWithTweaks: showOnboarding content branch"
)

# ─── Write ───────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ────────────────────────────────────────────────────────
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

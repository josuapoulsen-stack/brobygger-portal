# -*- coding: utf-8 -*-
"""
patch_multiuser_notifications.py
1. SoS_DEMO global — parse URL params (?rolle=brobygger&navn=Maja&gist=ID&token=PAT)
2. AppWithTweaks — activeRole from URL, override user persona, persona badge
3. Notification permission request
4. MessagesList — inject live thread when in URL mode
5. MessageThread — full BroadcastChannel live chat + Gist cross-device polling
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. Tilføj SoS_DEMO global (URL-params parsing) ───────────────────────────
OLD_STORE_END = "  window.SoS_STORE = { save, load, clear, hydrate };\n  hydrate();\n})();"
NEW_STORE_END = (
    "  window.SoS_STORE = { save, load, clear, hydrate };\n"
    "  hydrate();\n"
    "})();\n"
    "\n"
    "// ── SoS_DEMO — URL-parameter persona (multi-user demo) ──────────────────────\n"
    "// Brug: ?rolle=brobygger&navn=Maja  eller  ?rolle=raadgiver&navn=Linda\n"
    "// Cross-device chat: tilføj &gist=GIST_ID&token=GITHUB_PAT\n"
    "(function () {\n"
    "  const p = new URLSearchParams(window.location.search);\n"
    "  const rolle  = p.get('rolle');   // 'brobygger' | 'raadgiver'\n"
    "  const navn   = p.get('navn');    // visningsnavn, fx 'Maja'\n"
    "  const gistId = p.get('gist');    // GitHub Gist ID (valgfri)\n"
    "  const token  = p.get('token');   // GitHub PAT (valgfri, kræves for Gist-skrivning)\n"
    "  window.SoS_DEMO = { rolle, navn, gistId, token, active: !!rolle };\n"
    "  // Anmod om notifikations-tilladelse når der er en URL-rolle\n"
    "  if (rolle && 'Notification' in window && Notification.permission === 'default') {\n"
    "    Notification.requestPermission();\n"
    "  }\n"
    "})();"
)
cnt = html.count(OLD_STORE_END)
html = html.replace(OLD_STORE_END, NEW_STORE_END, 1)
results.append(('SoS_DEMO URL-param global', cnt, 1))

# ── 2. AppWithTweaks — tilføj activeRole + demo efter useTweaks ──────────────
OLD_TWEAKS_INIT = (
    '  const [tweaks, setTweak] = useTweaks({\n'
    '    "role": "admin",\n'
    '    "busyLevel": "busy",\n'
    '    "experience": "experienced",\n'
    '    "flow": "none"\n'
    '  });\n'
    '\n'
    '  // Auto-skalér enheden'
)
NEW_TWEAKS_INIT = (
    '  const [tweaks, setTweak] = useTweaks({\n'
    '    "role": "admin",\n'
    '    "busyLevel": "busy",\n'
    '    "experience": "experienced",\n'
    '    "flow": "none"\n'
    '  });\n'
    '\n'
    '  // URL-demo mode: ?rolle=brobygger&navn=Maja (to-bruger demo)\n'
    '  const demo = window.SoS_DEMO || {};\n'
    '  const activeRole = demo.active ? demo.rolle : tweaks.role;\n'
    '\n'
    '  // Auto-skalér enheden'
)
cnt = html.count(OLD_TWEAKS_INIT)
html = html.replace(OLD_TWEAKS_INIT, NEW_TWEAKS_INIT, 1)
results.append(('activeRole + demo i AppWithTweaks', cnt, 1))

# ── 3. Overskriv appts og user med URL-persona ────────────────────────────────
OLD_USER = (
    '  const isNew = tweaks.experience === "new";\n'
    '  const isBusy = tweaks.busyLevel === "busy";\n'
    '  const appts = (tweaks.role === "brobygger" && !isBusy) ? SoS_APPOINTMENTS_EMPTY : SoS_APPOINTMENTS_BUSY;\n'
    '\n'
    '  const user = { ...SoS_USER,\n'
    '    name: isNew ? "Sofie Lindahl" : "Maja Holmberg",\n'
    '    firstName: isNew ? "Sofie" : "Maja",\n'
    '    avatar: isNew ? "SL" : "MH",\n'
    '    avatarBg: isNew ? SoS.sky : SoS.orange,\n'
    '  };\n'
    '\n'
    '  useEffect(() => {\n'
    '    setScreen("hjem");\n'
    '    setDetailId(null);\n'
    '    setSettingsOpen(false);\n'
    '    if (tweaks.role === "brobygger") setDesktopMode(false);\n'
    '  }, [tweaks.role]);'
)
NEW_USER = (
    '  const isNew = tweaks.experience === "new";\n'
    '  const isBusy = tweaks.busyLevel === "busy";\n'
    '  const appts = (activeRole === "brobygger" && !isBusy) ? SoS_APPOINTMENTS_EMPTY : SoS_APPOINTMENTS_BUSY;\n'
    '\n'
    '  // Brugerpersona: URL-params overskriver tweak-defaults\n'
    '  const _demoNavn   = demo.active && demo.navn ? demo.navn : null;\n'
    '  const _demoAvatar = _demoNavn ? _demoNavn.split(\' \').map(n => n[0]).join(\'\').slice(0, 2).toUpperCase() : null;\n'
    '  const _defaultNavn = activeRole === \'raadgiver\' ? \'Linda Thomsen\'\n'
    '                      : activeRole === \'admin\'    ? \'Admin Bruger\'\n'
    '                      : isNew ? \'Sofie Lindahl\' : \'Maja Holmberg\';\n'
    '  const _defaultAvatar = activeRole === \'raadgiver\' ? \'LT\'\n'
    '                        : activeRole === \'admin\'    ? \'AB\'\n'
    '                        : isNew ? \'SL\' : \'MH\';\n'
    '  const user = { ...SoS_USER,\n'
    '    name:      _demoNavn   || _defaultNavn,\n'
    '    firstName: (_demoNavn  || _defaultNavn).split(\' \')[0],\n'
    '    avatar:    _demoAvatar || _defaultAvatar,\n'
    '    avatarBg:  demo.active\n'
    '      ? (activeRole === \'brobygger\' ? SoS.orange : SoS.sky)\n'
    '      : (isNew ? SoS.sky : SoS.orange),\n'
    '  };\n'
    '\n'
    '  useEffect(() => {\n'
    '    setScreen("hjem");\n'
    '    setDetailId(null);\n'
    '    setSettingsOpen(false);\n'
    '    if (activeRole === "brobygger") setDesktopMode(false);\n'
    '  }, [activeRole]);'
)
cnt = html.count(OLD_USER)
html = html.replace(OLD_USER, NEW_USER, 1)
results.append(('User persona + appts brug activeRole', cnt, 1))

# ── 4. Erstat tweaks.role med activeRole i content-blokken ───────────────────
OLD_CONTENT = (
    '  let content;\n'
    '  if (tweaks.flow === "mslogin") {\n'
    '    content = <MSLogin onDone={() => setTweak("flow", "none")} onCancel={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "export" && tweaks.role !== "brobygger") {\n'
    '    content = <ExportReport onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "onboarding") {\n'
    '    content = <OnboardingWizard onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "register" && tweaks.role === "brobygger") {\n'
    '    content = <RegistrerEfterAftale appt={SoS_APPOINTMENTS_BUSY[0]} onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "matching" && tweaks.role !== "brobygger") {\n'
    '    content = <MatchingFlow onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "intake" && tweaks.role !== "brobygger") {\n'
    '    content = <IntakeFlow onClose={() => setTweak("flow", "none")} viewingHq={viewingHq}/>;\n'
    '  } else if (tweaks.role === "admin" || tweaks.role === "raadgiver") {\n'
    '    if (settingsOpen) {\n'
    '      content = <AdminSettings\n'
    '        currentHq={viewingHq}\n'
    '        ownHq="Aarhus"\n'
    '        isAdmin={tweaks.role === "admin"}\n'
    '        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}\n'
    '        onClose={() => setSettingsOpen(false)} />;\n'
    '    } else {\n'
    '      content = <AdminMobile\n'
    '        user={user}\n'
    '        viewingHq={viewingHq}\n'
    '        ownHq="Aarhus"\n'
    '        isAdmin={tweaks.role === "admin"}'
)
NEW_CONTENT = (
    '  let content;\n'
    '  if (tweaks.flow === "mslogin") {\n'
    '    content = <MSLogin onDone={() => setTweak("flow", "none")} onCancel={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "export" && activeRole !== "brobygger") {\n'
    '    content = <ExportReport onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "onboarding") {\n'
    '    content = <OnboardingWizard onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "register" && activeRole === "brobygger") {\n'
    '    content = <RegistrerEfterAftale appt={SoS_APPOINTMENTS_BUSY[0]} onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "matching" && activeRole !== "brobygger") {\n'
    '    content = <MatchingFlow onClose={() => setTweak("flow", "none")} />;\n'
    '  } else if (tweaks.flow === "intake" && activeRole !== "brobygger") {\n'
    '    content = <IntakeFlow onClose={() => setTweak("flow", "none")} viewingHq={viewingHq}/>;\n'
    '  } else if (activeRole === "admin" || activeRole === "raadgiver") {\n'
    '    if (settingsOpen) {\n'
    '      content = <AdminSettings\n'
    '        currentHq={viewingHq}\n'
    '        ownHq="Aarhus"\n'
    '        isAdmin={activeRole === "admin"}\n'
    '        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}\n'
    '        onClose={() => setSettingsOpen(false)} />;\n'
    '    } else {\n'
    '      content = <AdminMobile\n'
    '        user={user}\n'
    '        viewingHq={viewingHq}\n'
    '        ownHq="Aarhus"\n'
    '        isAdmin={activeRole === "admin"}'
)
cnt = html.count(OLD_CONTENT)
html = html.replace(OLD_CONTENT, NEW_CONTENT, 1)
results.append(('Content-blok: tweaks.role -> activeRole', cnt, 1))

# ── 5. Erstat role={tweaks.role} i brobygger-indhold og profil ───────────────
OLD_ROLE_PROPS = (
    '          {screen === "notif" && (\n'
    '            msgCompose\n'
    '              ? <ComposeMessage\n'
    '                  role={tweaks.role}\n'
    '                  ownHq={viewingHq}\n'
    '                  onClose={() => setMsgCompose(false)}\n'
    '                />\n'
    '              : msgOpenId\n'
    '              ? <MessageThread\n'
    '                  threadId={msgOpenId}\n'
    '                  role={tweaks.role}\n'
    '                  onBack={() => setMsgOpenId(null)}\n'
    '                />\n'
    '              : <MessagesList\n'
    '                  onOpen={(id) => setMsgOpenId(id)}\n'
    '                  onCompose={() => setMsgCompose(true)}\n'
    '                  role={tweaks.role}\n'
    '                  ownHq={viewingHq}\n'
    '                />\n'
    '          )}\n'
    '          {screen === "profil" && <ProfileScreen user={user} onSwitchRole={() => setTweak("role", "raadgiver")} />}'
)
NEW_ROLE_PROPS = (
    '          {screen === "notif" && (\n'
    '            msgCompose\n'
    '              ? <ComposeMessage\n'
    '                  role={activeRole}\n'
    '                  ownHq={viewingHq}\n'
    '                  onClose={() => setMsgCompose(false)}\n'
    '                />\n'
    '              : msgOpenId\n'
    '              ? <MessageThread\n'
    '                  threadId={msgOpenId}\n'
    '                  role={activeRole}\n'
    '                  onBack={() => setMsgOpenId(null)}\n'
    '                />\n'
    '              : <MessagesList\n'
    '                  onOpen={(id) => setMsgOpenId(id)}\n'
    '                  onCompose={() => setMsgCompose(true)}\n'
    '                  role={activeRole}\n'
    '                  ownHq={viewingHq}\n'
    '                />\n'
    '          )}\n'
    '          {screen === "profil" && <ProfileScreen user={user} onSwitchRole={() => setTweak("role", "raadgiver")} />}'
)
cnt = html.count(OLD_ROLE_PROPS)
html = html.replace(OLD_ROLE_PROPS, NEW_ROLE_PROPS, 1)
results.append(('role props: tweaks.role -> activeRole', cnt, 1))

# ── 6. Tilføj persona-badge og notification-request til mobilvisningen ────────
OLD_MOBILE_RETURN = (
    '  if (isMobile) {\n'
    '    return (\n'
    '      <div style={{\n'
    '        position: \'fixed\', inset: 0, overflow: \'hidden\',\n'
    '        background: SoS.cream,\n'
    '        paddingTop: \'env(safe-area-inset-top)\',\n'
    '        paddingBottom: \'env(safe-area-inset-bottom)\',\n'
    '      }}>\n'
    '        {content}\n'
    '      </div>\n'
    '    );\n'
    '  }'
)
NEW_MOBILE_RETURN = (
    '  if (isMobile) {\n'
    '    return (\n'
    '      <div style={{\n'
    '        position: \'fixed\', inset: 0, overflow: \'hidden\',\n'
    '        background: SoS.cream,\n'
    '        paddingTop: \'env(safe-area-inset-top)\',\n'
    '        paddingBottom: \'env(safe-area-inset-bottom)\',\n'
    '      }}>\n'
    '        {content}\n'
    '        {/* Persona-badge: vises kun i URL-demo mode */}\n'
    '        {demo.active && (\n'
    '          <div style={{\n'
    '            position: \'fixed\', top: \'calc(env(safe-area-inset-top) + 10px)\',\n'
    '            right: 12, zIndex: 9998, pointerEvents: \'none\',\n'
    '            background: activeRole === \'brobygger\' ? SoS.sage : SoS.sky,\n'
    '            color: \'#fff\', borderRadius: 99, padding: \'4px 11px\',\n'
    '            fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n'
    '            boxShadow: \'0 2px 8px rgba(0,0,0,0.25)\',\n'
    '            display: \'flex\', alignItems: \'center\', gap: 5,\n'
    '          }}>\n'
    '            <div style={{ width: 6, height: 6, borderRadius: 3,\n'
    '              background: \'rgba(255,255,255,0.7)\' }}/>\n'
    '            {demo.navn || (activeRole === \'brobygger\' ? \'Brobygger\' : \'R\u00e5dgiver\')}\n'
    '          </div>\n'
    '        )}\n'
    '      </div>\n'
    '    );\n'
    '  }'
)
cnt = html.count(OLD_MOBILE_RETURN)
html = html.replace(OLD_MOBILE_RETURN, NEW_MOBILE_RETURN, 1)
results.append(('Persona-badge i mobilvisning', cnt, 1))

# ── 7. MessagesList: tilføj live-tråd øverst i URL-demo mode ─────────────────
OLD_VISIBLE_THREADS = (
    "  const visibleThreads = role === 'brobygger'\n"
    "    ? SoS_THREADS.filter(t => !t.fromBrobygger)\n"
    "    : SoS_THREADS.filter(t => t.fromBrobygger || t.official);"
)
NEW_VISIBLE_THREADS = (
    "  // I URL-demo mode: tilføj en LIVE-tråd øverst\n"
    "  const _demo = window.SoS_DEMO || {};\n"
    "  const _liveThread = _demo.active ? [{\n"
    "    id: 't-live',\n"
    "    withName: role === 'brobygger' ? 'Koordinator (LIVE)' : (_demo.navn || 'Brobygger') + ' (LIVE)',\n"
    "    withRole: role === 'brobygger' ? 'Demo-koordinator \u00b7 realtid' : 'Demo-brobygger \u00b7 realtid',\n"
    "    avatar: role === 'brobygger' ? 'LT' : (_demo.navn ? _demo.navn.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase() : 'BB'),\n"
    "    bg: role === 'brobygger' ? '#B8501E' : '#E87A3E',\n"
    "    last: '\u00c5ben live-chat mellem de to roller',\n"
    "    time: 'LIVE', unread: 0, online: true, live: true,\n"
    "  }] : [];\n"
    "  const visibleThreads = [\n"
    "    ..._liveThread,\n"
    "    ...(role === 'brobygger'\n"
    "      ? SoS_THREADS.filter(t => !t.fromBrobygger)\n"
    "      : SoS_THREADS.filter(t => t.fromBrobygger || t.official)),\n"
    "  ];"
)
cnt = html.count(OLD_VISIBLE_THREADS)
html = html.replace(OLD_VISIBLE_THREADS, NEW_VISIBLE_THREADS, 1)
results.append(('Live-trad i MessagesList', cnt, 1))

# ── 8. MessageThread: komplet live-chat (BroadcastChannel + Gist) ────────────
OLD_MSG_THREAD = (
    "const MessageThread = ({ threadId, onBack, role }) => {\n"
    "  const thread = SoS_THREADS.find(t => t.id === threadId) || SoS_THREADS[0];\n"
    "  const [draft, setDraft] = React.useState('');\n"
    "  const [localMessages, setLocalMessages] = React.useState([]);\n"
    "  const isBroadcast = !!thread.official;\n"
    "  const allMessages = [...SoS_MESSAGES, ...localMessages];\n"
    "  const handleSend = () => {\n"
    "    if (!draft.trim()) return;\n"
    "    const now = new Date();\n"
    "    const time = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');\n"
    "    setLocalMessages(prev => [...prev, {\n"
    "      id: 'local-' + Date.now(), from: 'me', time, text: draft.trim()\n"
    "    }]);\n"
    "    setDraft('');\n"
    "  };"
)
NEW_MSG_THREAD = (
    "const MessageThread = ({ threadId, onBack, role }) => {\n"
    "  const isLive = threadId === 't-live';\n"
    "  const _d = window.SoS_DEMO || {};\n"
    "  // Live-trad: dynamisk header baseret pa URL-rolle\n"
    "  const _liveThreadInfo = isLive ? {\n"
    "    id: 't-live',\n"
    "    withName: role === 'brobygger' ? 'Koordinator (LIVE)' : (_d.navn || 'Brobygger') + ' (LIVE)',\n"
    "    withRole: role === 'brobygger' ? 'Demo-koordinator \u00b7 realtid' : 'Demo-brobygger \u00b7 realtid',\n"
    "    avatar: role === 'brobygger' ? 'LT' : (_d.navn ? _d.navn.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase() : 'BB'),\n"
    "    bg: role === 'brobygger' ? '#B8501E' : '#E87A3E',\n"
    "    online: true, official: false, live: true,\n"
    "  } : null;\n"
    "  const thread = isLive ? _liveThreadInfo : (SoS_THREADS.find(t => t.id === threadId) || SoS_THREADS[0]);\n"
    "  const [draft, setDraft] = React.useState('');\n"
    "  const [localMessages, setLocalMessages] = React.useState([]);\n"
    "  const [liveMessages, setLiveMessages] = React.useState([]);\n"
    "  const bcRef = React.useRef(null);\n"
    "  const seenCountRef = React.useRef(0);\n"
    "  const isBroadcast = !isLive && !!thread.official;\n"
    "\n"
    "  // Live-chat: BroadcastChannel (samme enhed) + Gist-polling (kryds-enheder)\n"
    "  React.useEffect(() => {\n"
    "    if (!isLive) return;\n"
    "    // Indl\u00e6s gemte beskeder fra localStorage\n"
    "    try {\n"
    "      const stored = localStorage.getItem('sos_live_chat');\n"
    "      if (stored) { const msgs = JSON.parse(stored); setLiveMessages(msgs); seenCountRef.current = msgs.length; }\n"
    "    } catch(e) {}\n"
    "\n"
    "    // BroadcastChannel: sync i realtid (samme browser, forskellig fane)\n"
    "    if ('BroadcastChannel' in window) {\n"
    "      bcRef.current = new BroadcastChannel('sos_live_chat');\n"
    "      bcRef.current.onmessage = (ev) => {\n"
    "        const msgs = ev.data;\n"
    "        setLiveMessages(msgs);\n"
    "        // Notifikation hvis fanen er i baggrunden\n"
    "        if (document.hidden && Notification.permission === 'granted' && msgs.length > seenCountRef.current) {\n"
    "          const latest = msgs[msgs.length - 1];\n"
    "          if (latest.from !== role) new Notification('Ny besked \u2014 Brobygger Portal', { body: (latest.fromName || latest.from) + ': ' + latest.text, icon: 'icon-192.svg' });\n"
    "        }\n"
    "        seenCountRef.current = msgs.length;\n"
    "      };\n"
    "    }\n"
    "\n"
    "    // Gist-polling: cross-device sync (k\u00e6ver ?gist=ID i URL)\n"
    "    let pollInterval = null;\n"
    "    if (_d.gistId) {\n"
    "      const poll = async () => {\n"
    "        try {\n"
    "          const headers = _d.token ? { Authorization: 'Bearer ' + _d.token } : {};\n"
    "          const r = await fetch('https://api.github.com/gists/' + _d.gistId, { headers });\n"
    "          if (!r.ok) return;\n"
    "          const data = await r.json();\n"
    "          const fileContent = Object.values(data.files)[0]?.content;\n"
    "          if (!fileContent) return;\n"
    "          const msgs = JSON.parse(fileContent).messages || [];\n"
    "          localStorage.setItem('sos_live_chat', JSON.stringify(msgs));\n"
    "          setLiveMessages(prev => {\n"
    "            if (msgs.length > seenCountRef.current) {\n"
    "              const latest = msgs[msgs.length - 1];\n"
    "              if (document.hidden && Notification.permission === 'granted' && latest.from !== role)\n"
    "                new Notification('Ny besked \u2014 Brobygger Portal', { body: (latest.fromName || latest.from) + ': ' + latest.text, icon: 'icon-192.svg' });\n"
    "              seenCountRef.current = msgs.length;\n"
    "            }\n"
    "            return msgs;\n"
    "          });\n"
    "        } catch(e) {}\n"
    "      };\n"
    "      poll(); // straks ved mount\n"
    "      pollInterval = setInterval(poll, 8000); // derefter hvert 8. sek\n"
    "    }\n"
    "    return () => { bcRef.current?.close(); if (pollInterval) clearInterval(pollInterval); };\n"
    "  }, [isLive]);\n"
    "\n"
    "  const allMessages = isLive ? liveMessages : [...SoS_MESSAGES, ...localMessages];\n"
    "\n"
    "  const handleSend = async () => {\n"
    "    if (!draft.trim()) return;\n"
    "    const now = new Date();\n"
    "    const time = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');\n"
    "\n"
    "    if (isLive && _d.active) {\n"
    "      const newMsg = { id: String(Date.now()), from: role, fromName: _d.navn || role, text: draft.trim(), time };\n"
    "      const updated = [...liveMessages, newMsg];\n"
    "\n"
    "      if (_d.gistId && _d.token) {\n"
    "        // Cross-device: skriv til Gist\n"
    "        try {\n"
    "          await fetch('https://api.github.com/gists/' + _d.gistId, {\n"
    "            method: 'PATCH',\n"
    "            headers: { Authorization: 'Bearer ' + _d.token, 'Content-Type': 'application/json' },\n"
    "            body: JSON.stringify({ files: { 'sos_chat.json': { content: JSON.stringify({ messages: updated }) } } }),\n"
    "          });\n"
    "        } catch(e) { console.warn('Gist write failed:', e); }\n"
    "      }\n"
    "      // Altid: gem lokalt + broadcast til andre faner\n"
    "      localStorage.setItem('sos_live_chat', JSON.stringify(updated));\n"
    "      bcRef.current?.postMessage(updated);\n"
    "      setLiveMessages(updated);\n"
    "      seenCountRef.current = updated.length;\n"
    "    } else {\n"
    "      setLocalMessages(prev => [...prev, { id: 'local-' + Date.now(), from: 'me', time, text: draft.trim() }]);\n"
    "    }\n"
    "    setDraft('');\n"
    "  };"
)
cnt = html.count(OLD_MSG_THREAD)
html = html.replace(OLD_MSG_THREAD, NEW_MSG_THREAD, 1)
results.append(('MessageThread: live-chat BroadcastChannel + Gist', cnt, 1))

# ── 9. MessageThread: besked-rendering — vis afsender-navn for live-beskeder ──
OLD_MSG_BUBBLE = (
    "        {allMessages.map(m => {\n"
    "          const mine = m.from === 'me';\n"
    "          return (\n"
    "            <div key={m.id} style={{ display: 'flex',\n"
    "              justifyContent: mine ? 'flex-end' : 'flex-start', marginBottom: 6 }}>"
)
NEW_MSG_BUBBLE = (
    "        {allMessages.map(m => {\n"
    "          const mine = isLive ? m.from === role : m.from === 'me';\n"
    "          return (\n"
    "            <div key={m.id} style={{ display: 'flex',\n"
    "              justifyContent: mine ? 'flex-end' : 'flex-start', marginBottom: 6 }}>"
)
cnt = html.count(OLD_MSG_BUBBLE)
html = html.replace(OLD_MSG_BUBBLE, NEW_MSG_BUBBLE, 1)
results.append(('Message-boble mine-logik for live', cnt, 1))

# ── 10. MessageThread: skjul "Linda skriver..." for live-trad ────────────────
OLD_TYPING = (
    "        {!isBroadcast && (\n"
    "          <div style={{ display: 'flex', gap: 4, padding: '8px 14px', alignItems: 'center' }}>\n"
    "            {[0,1,2].map(i => (\n"
    "              <div key={i} style={{ width: 6, height: 6, borderRadius: 3,\n"
    "                background: SoS.inkMuted, opacity: 0.4 }}/>\n"
    "            ))}\n"
    "            <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginLeft: 4 }}>\n"
    "              Linda skriver...\n"
    "            </span>\n"
    "          </div>\n"
    "        )}"
)
NEW_TYPING = (
    "        {!isBroadcast && !isLive && (\n"
    "          <div style={{ display: 'flex', gap: 4, padding: '8px 14px', alignItems: 'center' }}>\n"
    "            {[0,1,2].map(i => (\n"
    "              <div key={i} style={{ width: 6, height: 6, borderRadius: 3,\n"
    "                background: SoS.inkMuted, opacity: 0.4 }}/>\n"
    "            ))}\n"
    "            <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginLeft: 4 }}>\n"
    "              Linda skriver...\n"
    "            </span>\n"
    "          </div>\n"
    "        )}\n"
    "        {isLive && liveMessages.length === 0 && (\n"
    "          <div style={{ padding: '24px 16px', textAlign: 'center', fontFamily: SoS.sans,\n"
    "            fontSize: 13, color: SoS.inkMuted, lineHeight: 1.6 }}>\n"
    "            <div style={{ fontSize: 28, marginBottom: 10 }}>&#128172;</div>\n"
    "            \u00c5ben live-chat. Begge parter kan skrive til hinanden i realtid.\n"
    "            <br/>Del den anden URL med den anden person for at starte chatten.\n"
    "          </div>\n"
    "        )}"
)
cnt = html.count(OLD_TYPING)
html = html.replace(OLD_TYPING, NEW_TYPING, 1)
results.append(('Typing-indicator: skjul for live + tom-state', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

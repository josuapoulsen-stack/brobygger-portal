# -*- coding: utf-8 -*-
"""
patch_notif_bugs.py
1. Acceptér viser "Accepteret ✓" (grøn) — Afslå viser "Afvist" (grå)
2. Reminder-notifikationer er klikbare (åbner kalender via onNavigate)
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. Tilføj `accepted` state + fix Accept/Afslå ────────────────────────────
OLD_DISMISSED_STATE = (
    "  const [dismissed, setDismissed] = React.useState(new Set());\n"
    "  const [expanded, setExpanded]   = React.useState(null); // notif-id der vises udvidet"
)
NEW_DISMISSED_STATE = (
    "  const [dismissed, setDismissed] = React.useState(new Set());\n"
    "  const [accepted,  setAccepted]  = React.useState(new Set());\n"
    "  const [expanded, setExpanded]   = React.useState(null); // notif-id der vises udvidet"
)
cnt = html.count(OLD_DISMISSED_STATE)
html = html.replace(OLD_DISMISSED_STATE, NEW_DISMISSED_STATE, 1)
results.append(('Tilfoej accepted state', cnt, 1))

# ── 2. Fix Accept-knap: sæt accepted + dismissed ─────────────────────────────
OLD_ACCEPT_BTN = (
    "                  <button\n"
    "                    onClick={() => { setExpanded(null); setDismissed(prev => new Set([...prev, n.id])); }}\n"
    "                    style={{ flex: 1, padding: '9px 0', background: SoS.sage,\n"
    "                      color: '#fff', border: 'none', borderRadius: SoS.r.sm,\n"
    "                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>\n"
    "                    Acceptér\n"
    "                  </button>"
)
NEW_ACCEPT_BTN = (
    "                  <button\n"
    "                    onClick={() => { setExpanded(null); setAccepted(prev => new Set([...prev, n.id])); setDismissed(prev => new Set([...prev, n.id])); }}\n"
    "                    style={{ flex: 1, padding: '9px 0', background: SoS.sage,\n"
    "                      color: '#fff', border: 'none', borderRadius: SoS.r.sm,\n"
    "                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>\n"
    "                    Acceptér\n"
    "                  </button>"
)
cnt = html.count(OLD_ACCEPT_BTN)
html = html.replace(OLD_ACCEPT_BTN, NEW_ACCEPT_BTN, 1)
results.append(('Accept-knap saetter accepted state', cnt, 1))

# ── 3. Fix statustekst: vis "Accepteret ✓" eller "Afvist" ────────────────────
OLD_DISMISSED_LABEL = (
    "                {isDismissed && (\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                    color: SoS.inkMuted, marginTop: 6 }}>Afvist</div>\n"
    "                )}"
)
NEW_DISMISSED_LABEL = (
    "                {isDismissed && (\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 11,\n"
    "                    color: accepted.has(n.id) ? SoS.sage : SoS.inkMuted,\n"
    "                    fontWeight: accepted.has(n.id) ? 600 : 400,\n"
    "                    marginTop: 6 }}>\n"
    "                    {accepted.has(n.id) ? 'Accepteret \u2713' : 'Afvist'}\n"
    "                  </div>\n"
    "                )}"
)
cnt = html.count(OLD_DISMISSED_LABEL)
html = html.replace(OLD_DISMISSED_LABEL, NEW_DISMISSED_LABEL, 1)
results.append(('Statustekst accepteret vs afvist', cnt, 1))

# ── 4. MessagesList: modtag onNavigate prop + gør reminder klikbar ────────────
OLD_MSGS_PROPS = "const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose }) => {"
NEW_MSGS_PROPS = "const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose, onNavigate }) => {"
cnt = html.count(OLD_MSGS_PROPS)
html = html.replace(OLD_MSGS_PROPS, NEW_MSGS_PROPS, 1)
results.append(('MessagesList: tilfoej onNavigate prop', cnt, 1))

# ── 5. Gør reminder-notifikationer klikbare ───────────────────────────────────
# Find notifikations-kortet og tilføj onClick for reminder-type
OLD_NOTIF_CARD = (
    "          <div key={n.id} style={{\n"
    "            marginBottom: 8, background: isUnread ? '#fff' : 'transparent',\n"
    "            borderRadius: SoS.r.lg, boxShadow: isUnread ? SoS.shadow.sm : 'none',\n"
    "            border: `1px solid ${isUnread ? SoS.lineSoft : 'transparent'}`,\n"
    "            overflow: 'hidden',\n"
    "          }}>"
)
NEW_NOTIF_CARD = (
    "          <div key={n.id}\n"
    "            onClick={n.type === 'reminder' && onNavigate ? () => onNavigate('kalender') : undefined}\n"
    "            style={{\n"
    "              marginBottom: 8, background: isUnread ? '#fff' : 'transparent',\n"
    "              borderRadius: SoS.r.lg, boxShadow: isUnread ? SoS.shadow.sm : 'none',\n"
    "              border: `1px solid ${isUnread ? SoS.lineSoft : 'transparent'}`,\n"
    "              overflow: 'hidden',\n"
    "              cursor: n.type === 'reminder' ? 'pointer' : 'default',\n"
    "            }}>"
)
cnt = html.count(OLD_NOTIF_CARD)
html = html.replace(OLD_NOTIF_CARD, NEW_NOTIF_CARD, 1)
results.append(('Reminder-notifikation klikbar -> kalender', cnt, 1))

# ── 6. Send onNavigate fra AppWithTweaks til MessagesList ────────────────────
OLD_MSGS_LIST_CALL = (
    "              : <MessagesList\n"
    "                  onOpen={(id) => setMsgOpenId(id)}\n"
    "                  onCompose={() => setMsgCompose(true)}\n"
    "                  role={activeRole}\n"
    "                  ownHq={viewingHq}\n"
    "                />"
)
NEW_MSGS_LIST_CALL = (
    "              : <MessagesList\n"
    "                  onOpen={(id) => setMsgOpenId(id)}\n"
    "                  onCompose={() => setMsgCompose(true)}\n"
    "                  role={activeRole}\n"
    "                  ownHq={viewingHq}\n"
    "                  onNavigate={navigate}\n"
    "                />"
)
cnt = html.count(OLD_MSGS_LIST_CALL)
html = html.replace(OLD_MSGS_LIST_CALL, NEW_MSGS_LIST_CALL, 1)
results.append(('Send onNavigate til MessagesList', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

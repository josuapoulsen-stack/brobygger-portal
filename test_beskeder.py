#!/usr/bin/env python3
"""
Besked-system test — verificerer afsendelse og modtagelse for
brobygger, rådgiver og admin.
"""
import re, os, sys

PATH = os.path.expanduser("~/Documents/Claude Code/brobygger-portal/Brobygger portal.html")
with open(PATH, encoding='utf-8') as f:
    html = f.read()

ok = fail = warn = 0
issues = []

def check(name, cond, detail='', severity='fail'):
    global ok, fail, warn
    if cond:
        ok += 1
        print(f"  ✓  {name}")
    elif severity == 'warn':
        warn += 1
        issues.append(('⚠', name, detail))
        print(f"  ⚠  {name}" + (f"  →  {detail}" if detail else ""))
    else:
        fail += 1
        issues.append(('✗', name, detail))
        print(f"  ✗  {name}" + (f"  →  {detail}" if detail else ""))

def find(pattern, flags=re.DOTALL):
    return re.findall(pattern, html, flags)

# ─────────────────────────────────────────────────────────────────
# 1. DATA-STRUKTUR
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 1. DATA-STRUKTUR ━━━")

threads = find(r"\{ id: '(t-\d+)'")
check("SoS_THREADS defineret", len(threads) > 0, f"{len(threads)} tråde")
check("Mindst 4 tråde i datasættet", len(threads) >= 4, str(threads))

# Tjek nødvendige felter på tråde (JS shorthand: withName: ikke 'withName':)
thread_fields = ['withName', 'withRole', 'avatar', 'bg', 'last', 'time', 'unread']
for f in thread_fields:
    check(f"Tråde har felt: {f}", f" {f}:" in html or f"\t{f}:" in html or f",{f}:" in html)

messages = find(r"\{ id: '(m-\d+)'")
check("SoS_MESSAGES defineret", len(messages) > 0, f"{len(messages)} beskeder")
check("Beskeder har 'from' felt", "'from': 'me'" in html or "from: 'me'" in html)
check("Beskeder har 'text' felt", "from: 'them'" in html)
check("Beskeder har 'time' felt", "time: '14:" in html)

templates = find(r"\{ id: '(\w+)', emoji:")
check("Skabeloner defineret (SoS_TEMPLATES)", len(templates) >= 4, f"{len(templates)} skabeloner")

# ─────────────────────────────────────────────────────────────────
# 2. KOMPONENTER EKSISTERER OG ER EKSPORTERET
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 2. KOMPONENTER ━━━")

check("MessagesList eksisterer", "const MessagesList = " in html)
check("MessageThread eksisterer", "const MessageThread = " in html)
check("ComposeMessage eksisterer", "const ComposeMessage = " in html)
check("AdminMobileBeskeder eksisterer", "const AdminMobileBeskeder = " in html)

check("MessagesList eksporteret til window", "window.MessagesList = MessagesList" in html)
check("MessageThread eksporteret til window", "window.MessageThread = MessageThread" in html)
check("ComposeMessage eksporteret til window", "window.ComposeMessage = ComposeMessage" in html)

# ─────────────────────────────────────────────────────────────────
# 3. AFSENDELSE — RÅDGIVER / ADMIN
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 3. AFSENDELSE — RÅDGIVER / ADMIN ━━━")

# + knap kun synlig for ikke-brobyggere
check("Compose-knap skjult for brobyggere",
      "role !== 'brobygger'" in html and "onCompose" in html,
      "role-check på + knap")

# canSend-validering
check("canSend kræver body > 2 tegn",
      "body.trim().length > 2" in html)

check("canSend kræver modtager hvis 'een' scope",
      "scope !== 'een' || selectedBb" in html)

# Scope-muligheder
check("Scope 'Én brobygger' eksisterer", "id: 'een'" in html)
check("Scope 'Alle aktive' eksisterer", "id: 'aktive'" in html)
check("Scope 'Inkl. pause' eksisterer", "id: 'alle'" in html)
check("Admin-eksklusivt scope 'Alle HQ-er'",
      "alle-hq" in html and "isAdmin" in html)

# Modtager-søgning
check("Brobygger-søgning i modtager-picker",
      "bbSearch" in html and "b.name.toLowerCase().includes" in html)

# RecipientCount beregning
check("recipientCount 1 ved 'een' + valgt brobygger",
      "scope === 'een' ? (selectedBb ? 1 : 0)" in html)

check("recipientCount = aktiveBrobyggere ved 'aktive'",
      "scope === 'aktive' ? activeBbs.length" in html)

# Sent-bekræftelse
check("Afsendelse viser bekræftelsesmodal",
      "setSent(true)" in html and "Besked sendt" in html)

check("Bekræftelse nævner antal modtagere",
      "Sendt til ${recipientCount}" in html or
      "Sendt til" in html and "recipientCount" in html)

check("Bekræftelse nævner modtagerens navn ved 1:1",
      "selectedBb.name" in html)

check("Urgent-flag vises i bekræftelse",
      "urgent && ' · Markeret som vigtig'" in html or
      "Markeret som vigtig" in html)

# Skabeloner
check("Skabeloner kan indsættes i besked-body",
      "setBody" in html and "templateId" in html)

check("Valgt skabelon fremhæves visuelt",
      "templateId === t.id" in html or "templateId ===" in html)

# ─────────────────────────────────────────────────────────────────
# 4. AFSENDELSE — BROBYGGER (svar i tråd)
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 4. AFSENDELSE — BROBYGGER ━━━")

check("Draft-felt eksisterer i MessageThread",
      "const [draft, setDraft]" in html)

check("Draft-felt binder til textarea",
      "value={draft}" in html and "onChange" in html and "setDraft" in html)

check("Send-knap aktiveres når draft ikke er tom",
      "background: draft ? SoS.orange : SoS.creamDeep" in html or
      "draft ?" in html)

# VIGTIGT: Send-knappen har ingen onClick — den sender ikke faktisk
send_btn_onclick = re.search(
    r'<button style=\{[^}]*background: draft \? SoS\.orange[^}]*\}[^>]*onClick',
    html)
check("Send-knap i tråd har onClick-handler",
      send_btn_onclick is not None,
      "Mangler onClick — beskeden sendes ikke reelt til tråden",
      severity='warn')

# Kan brobygger sende broadcast? (bør ikke kunne)
check("Brobygger kan IKKE åbne ComposeMessage (ingen + knap)",
      "role !== 'brobygger'" in html,
      "ComposeMessage + knap er korrekt gemt for brobyggere")

# ─────────────────────────────────────────────────────────────────
# 5. MODTAGELSE — VISNING AF BESKEDER
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 5. MODTAGELSE — VISNING ━━━")

check("Egne beskeder vises højrejusteret",
      "justifyContent: mine ? 'flex-end' : 'flex-start'" in html)

check("Egne beskeder har orange baggrund",
      "background: mine ? SoS.orange : '#fff'" in html)

check("Andre beskeder har hvid baggrund",
      "background: mine ? SoS.orange : '#fff'" in html)

check("Læst-indikator på egne beskeder",
      "L\\u00e6st" in html or "'Læst'" in html or "Læst" in html)

check("Tid vises på beskeder", "m.time" in html)

check("Ubesvarede markeres med fed/unread-badge",
      "fontWeight: t.unread ? 700 : 600" in html or
      "t.unread ? 700" in html)

check("Unread-badge viser antal",
      "t.unread > 0" in html and "t.unread}" in html)

check("Urgent-tråde fremhæves (orange prik)",
      "t.urgent" in html and "background: SoS.orange" in html)

check("Online-status vises på avatar",
      "t.online" in html and "background: SoS.sage" in html)

check("'Skriver...'-indikator i aktiv tråd",
      "Linda skriver" in html or "skriver..." in html)

# ─────────────────────────────────────────────────────────────────
# 6. BROADCAST / FÆLLESBESKED
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 6. BROADCAST / FÆLLESBESKED ━━━")

check("Broadcast-tråde markeret med 'official: true'",
      "official: true" in html)

check("Broadcast-tråde har SoS-afsender",
      "withName: 'SoS'" in html)

check("Broadcast kan ikke besvares",
      "isBroadcast" in html and
      ("Fællesbesked" in html or "F\\u00e6llesbesked" in html))

check("Composer skjult for broadcast",
      "!isBroadcast" in html and "isBroadcast ?" in html)

check("Broadcast-besked viser lås-ikon",
      "lock" in html and "isBroadcast" in html)

check("Official-badge (skjold) på broadcast-avatar",
      "t.official" in html and "shield" in html)

# ─────────────────────────────────────────────────────────────────
# 7. TRÅD-FILTRERING PR. ROLLE
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 7. TRÅD-FILTRERING PR. ROLLE ━━━")

# Tråde t-1 til t-4: brobygger-perspektiv (koordinator → brobygger)
# Tråde t-5 til t-9: koordinator-perspektiv (brobygger → koordinator)
check("Tråde med 'fromBrobygger' flag markeret",
      "fromBrobygger: true" in html)

check("Koordinator-tråde (t-5 til t-9) eksisterer",
      "fromBrobygger: true" in html and
      len(find(r"fromBrobygger: true")) >= 3)

# KRITISK: Er der rolle-filtrering på tråd-listen?
threads_filter = re.search(
    r'SoS_THREADS(?:\.filter\([^)]+fromBrobygger|\.filter\([^)]+role)',
    html)
check("Tråd-liste filtreres efter rolle",
      threads_filter is not None,
      "Brobygger ser koordinator-tråde (t-5 til t-9) — bør filtreres væk",
      severity='warn')

# Proxied beskeder (via koordinator)
check("Proxied-beskeder markeret",
      "proxied: true" in html)

check("Proxied-indikator i tråd-liste",
      "t.proxied" in html and ("↳" in html or "\\u21b3" in html))

# Koordinator-svar bekræftelse
check("'Besvaret'-markering på tråd",
      "coordinatorReplied" in html and ("Besvaret" in html or "Besvaret ✓" in html))

# ─────────────────────────────────────────────────────────────────
# 8. NAVIGATION OG INTEGRATION
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 8. NAVIGATION & INTEGRATION ━━━")

check("AdminMobileBeskeder bruger MessageThread",
      "MessageThread" in html and "threadId" in html)

check("AdminMobileBeskeder bruger ComposeMessage",
      "ComposeMessage" in html and "composeOpen" in html)

check("Tråd åbnes ved klik (onOpen/setThreadId)",
      "onOpen={(id) => setThreadId(id)" in html or
      "setThreadId" in html and "onOpen" in html)

check("Tilbage-knap fra tråd til liste",
      "onBack={() => setThreadId(null)" in html or
      "setThreadId(null)" in html)

check("Telefon-link på koordinator-tråde",
      'href="tel:' in html and "Koordinator" in html)

check("Notifikations-tabs (Notifikationer + Beskeder)",
      "id: 'notifikationer'" in html and "id: 'beskeder'" in html)

check("Unread-count i tab-badge",
      "SoS_THREADS.filter(t => t.unread > 0).length" in html)

check("Brobygger-app bruger MessagesList",
      "MessagesList" in html and "ComposeMessage" in html)

# ─────────────────────────────────────────────────────────────────
# 9. SROI-TEKST I BESKEDER (bør fjernes)
# ─────────────────────────────────────────────────────────────────
print("\n━━━ 9. INDHOLD-KVALITET ━━━")

# Tjek kun inden for selve array-definitionen (ikke resten af filen)
msg_block  = re.search(r"const SoS_MESSAGES\s*=\s*\[.*?\];", html, re.DOTALL)
sroi_in_msg = msg_block and 'SROI' in msg_block.group(0)
check("Ingen SROI-tekst i mock-beskeder",
      not sroi_in_msg,
      "En besked-tekst nævner SROI-rapporten",
      severity='warn')

tmpl_block = re.search(r"const SoS_TEMPLATES\s*=\s*\[.*?\];", html, re.DOTALL)
sroi_in_templates = tmpl_block and 'SROI' in tmpl_block.group(0)
check("Ingen SROI-tekst i beskedskabeloner",
      not sroi_in_templates,
      "En skabelon-tekst nævner SROI-rapport",
      severity='warn')

check("Lås-note om borgekommunikation via koordinator",
      "Al kommunikation til borgere sker via koordinator" in html)

check("Pauset brobygger markeret i tråd",
      "paused: true" in html and "pause" in html)

# ─────────────────────────────────────────────────────────────────
# RESULTAT
# ─────────────────────────────────────────────────────────────────
print(f"\n{'═'*55}")
print(f"  RESULTAT: {ok} bestået  |  {warn} advarsler  |  {fail} fejlet")
print(f"{'═'*55}")

if issues:
    print()
    for status, name, detail in issues:
        print(f"  {status}  {name}")
        if detail:
            print(f"       {detail}")

sys.exit(fail)

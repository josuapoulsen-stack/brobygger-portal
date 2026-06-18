import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# A) BrobyggerLogModal.save: sæt aftale-status ud fra udfald
sub(
    "  const save = () => {\n"
    "    const log = { udfald, varighed: udfald === 'gennemfoert' ? varighed : 0,\n"
    "      note: note.trim(), loggedAt: new Date().toISOString() };\n"
    "    // Gem på aftalen\n"
    "    const newList = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>\n"
    "      a.id === aftale.id\n"
    "        ? { ...a, brobyggerLog: log, raadgiverOpfoelgning: null }\n"
    "        : a\n"
    "    );",
    "  const save = () => {\n"
    "    const log = { udfald, varighed: udfald === 'gennemfoert' ? varighed : 0,\n"
    "      note: note.trim(), loggedAt: new Date().toISOString() };\n"
    "    // Udfald driver aftale-status (gennemført / afbud→aflyst; udeblevet beholder status)\n"
    "    const nyStatus = udfald === 'gennemfoert' ? 'gennemfoert'\n"
    "                   : udfald === 'afbud' ? 'aflyst' : null;\n"
    "    // Gem på aftalen\n"
    "    const newList = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>\n"
    "      a.id === aftale.id\n"
    "        ? { ...a, brobyggerLog: log, raadgiverOpfoelgning: null,\n"
    "            status: nyStatus || a.status,\n"
    "            ...(udfald === 'afbud' ? { aflysningsAarsag: a.aflysningsAarsag || 'Borger afbud' } : {}) }\n"
    "        : a\n"
    "    );",
    "A: log-udfald → status")

# B) AppointmentDetailScreen: fjern redundant/forkert overskrivning (save() skrev allerede listen)
sub(
    "          onSave={(log) => {\n"
    "            const updAppts = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>\n"
    "              a.id === appt.id ? { ...a, brobyggerLog: log } : a\n"
    "            );\n"
    "            window.SoS_APPOINTMENTS_BUSY = updAppts;\n"
    "            window.SoS_STORE?.save('appointments', updAppts);\n"
    "            setShowLog(false);\n"
    "            onComplete?.();\n"
    "          }}",
    "          onSave={() => { setShowLog(false); onComplete?.(); }}",
    "B: fjern redundant log-overskrivning")

# C) Aflysnings-flow (brobygger): persistér status='aflyst' + struktureret årsag/aflystAf
sub(
    "              <Button full onClick={() => { setCancelled(true); setShowCancel(false); }}\n"
    "                disabled={!aflysAarsag}",
    "              <Button full onClick={() => {\n"
    "                  const aMap = { mennesket: 'Borger afbud', brobygger: 'Andet',\n"
    "                    sygdom: 'Borger sygdom', koordinator: 'Andet', andet: 'Andet' };\n"
    "                  const afMap = { mennesket: 'Personen selv', brobygger: 'Social Sundhed',\n"
    "                    sygdom: 'Personen selv', koordinator: 'Social Sundhed', andet: 'Ekstern' };\n"
    "                  const upd = (window.SoS_APPOINTMENTS_BUSY || []).map(a => a.id === appt.id\n"
    "                    ? { ...a, status: 'aflyst', aflysningsAarsag: aMap[aflysAarsag] || 'Andet',\n"
    "                        aflystAf: afMap[aflysAarsag] || '' } : a);\n"
    "                  window.SoS_APPOINTMENTS_BUSY = upd;\n"
    "                  if (window.SoS_STORE) window.SoS_STORE.save('appointments', upd);\n"
    "                  setCancelled(true); setShowCancel(false);\n"
    "                }}\n"
    "                disabled={!aflysAarsag}",
    "C: aflysnings-flow → status='aflyst'")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

with open(P, 'rb') as f:
    b = f.read()
needle = b".join('" + bytes([0x0a]) + b"');"
if needle in b:
    b = b.replace(needle, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(P, 'wb') as f:
        f.write(b)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f"\nOK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"\nFAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

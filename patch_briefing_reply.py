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

# 1) Briefing logges som besked som standard
sub(
    "  const [sendBesked, setSendBesked] = React.useState(false);",
    "  const [sendBesked, setSendBesked] = React.useState(true);",
    "1: sendBesked default")

# 2) AppointmentDetailScreen modtager onOpenBeskeder
sub(
    "const AppointmentDetailScreen = ({ appt, onBack, onComplete }) => {",
    "const AppointmentDetailScreen = ({ appt, onBack, onComplete, onOpenBeskeder }) => {",
    "2: signatur")

# 3) Skrivebeskyttet briefing-kort: henvis svar til Beskeder
sub(
"""          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
            lineHeight: 1.55, whiteSpace: 'pre-wrap' }}>{appt.brobyggerNote}</div>
        </div>
      )}""",
"""          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
            lineHeight: 1.55, whiteSpace: 'pre-wrap' }}>{appt.brobyggerNote}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12,
            paddingTop: 12, borderTop: `1px solid ${SoS.lineSoft}` }}>
            <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
              Du kan ikke svare her — skriv dit svar i Beskeder.
            </span>
            {onOpenBeskeder && (
              <button onClick={onOpenBeskeder} style={{ flexShrink: 0, padding: '7px 14px',
                background: SoS.orange, color: '#fff', border: 'none', borderRadius: SoS.r.md,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 700 }}>
                Svar i Beskeder
              </button>
            )}
          </div>
        </div>
      )}""",
"3: svar-henvisning")

# 4) Call-site i AppWithTweaks (brobygger-flow)
sub(
    "<AppointmentDetailScreen appt={appt} onBack={backFromAppt} onComplete={backFromAppt} />",
    "<AppointmentDetailScreen appt={appt} onBack={backFromAppt} onComplete={backFromAppt} onOpenBeskeder={() => { setDetailId(null); setScreen(\"notif\"); }} />",
    "4: call-site AppWithTweaks")

# 5) Call-site i AdminMobile (tab-system)
sub(
    "<AppointmentDetailScreen appt={selectedAppt} onBack={() => setSelectedAppt(null)} onComplete={() => setSelectedAppt(null)}/>",
    "<AppointmentDetailScreen appt={selectedAppt} onBack={() => setSelectedAppt(null)} onComplete={() => setSelectedAppt(null)} onOpenBeskeder={() => { setSelectedAppt(null); setTab('beskeder'); }}/>",
    "5: call-site AdminMobile")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

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
# 1. MSLogin — tilføj rollevælger til "Vælg en konto"-trinnet
#    Erstatter den ene "Maja Holmberg"-knap med 3 persona-knapper
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """          {step === 0 && <>
            <div style={{ fontFamily: SoS.sans, fontSize: 22, fontWeight: 600,
              color: SoS.ink, marginBottom: 6 }}>Vælg en konto</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>
              til at fortsætte til Social Sundhed
            </div>

            <button onClick={() => setStep(1)} style={{
              display: 'flex', alignItems: 'center', gap: 12, width: '100%',
              padding: '12px 8px', background: 'none', border: 'none',
              borderBottom: `1px solid ${SoS.line}`, cursor: 'pointer', textAlign: 'left',
            }}>
              <Avatar initials="MH" bg={SoS.orange} size={36}/>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                  Maja Holmberg
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                  maja.holmberg@socialsundhed.org
                </div>
              </div>
            </button>

            <button style={{
              display: 'flex', alignItems: 'center', gap: 12, width: '100%',
              padding: '12px 8px', background: 'none', border: 'none',
              cursor: 'pointer', textAlign: 'left',
            }}>
              <div style={{ width: 36, height: 36, borderRadius: 18, background: SoS.creamDeep,
                display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="plus" size={18} color={SoS.inkSoft}/>
              </div>
              <span style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}>
                Brug en anden konto
              </span>
            </button>
          </>}""",
    """          {step === 0 && <>
            <div style={{ fontFamily: SoS.sans, fontSize: 22, fontWeight: 600,
              color: SoS.ink, marginBottom: 6 }}>Vælg en konto</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>
              til at fortsætte til Social Sundhed
            </div>

            {/* Demo-personas — erstattes af rigtige MS-konti i produktion */}
            {[
              { rolle: 'admin',     initials: 'SA', bg: SoS.ink,    navn: 'Sarah Andersen', email: 'sarah@socialsundhed.org',  label: 'Administrator' },
              { rolle: 'raadgiver', initials: 'LT', bg: SoS.accent, navn: 'Linda Thomsen',  email: 'linda@socialsundhed.org',  label: 'Rådgiver' },
              { rolle: 'brobygger', initials: 'MH', bg: SoS.orange, navn: 'Maja Holmberg',  email: 'maja.holmberg@socialsundhed.org', label: 'Brobygger' },
            ].map((p, i, arr) => (
              <button key={p.rolle} onClick={() => { setSelectedRolle(p.rolle); setStep(1); }} style={{
                display: 'flex', alignItems: 'center', gap: 12, width: '100%',
                padding: '12px 8px', background: 'none', border: 'none',
                borderBottom: i < arr.length - 1 ? `1px solid ${SoS.line}` : 'none',
                cursor: 'pointer', textAlign: 'left',
              }}>
                <Avatar initials={p.initials} bg={p.bg} size={36}/>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                    {p.navn}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {p.email}
                  </div>
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                  background: SoS.creamDeep, borderRadius: SoS.r.sm, padding: '2px 8px' }}>
                  {p.label}
                </div>
              </button>
            ))}
          </>}""",
    "MSLogin: rollevælger med 3 personas"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. MSLogin — tilføj selectedRolle state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """const MSLogin = ({ onDone, onCancel }) => {
  const [step, setStep] = React.useState(0); // 0 pick, 1 password, 2 2FA, 3 success
  const [code, setCode] = React.useState(['', '', '', '', '', '']);
  const inputRefs = React.useRef([]);""",
    """const MSLogin = ({ onDone, onCancel }) => {
  const [step, setStep] = React.useState(0); // 0 pick, 1 password, 2 2FA, 3 success
  const [code, setCode] = React.useState(['', '', '', '', '', '']);
  const [selectedRolle, setSelectedRolle] = React.useState('raadgiver');
  const inputRefs = React.useRef([]);""",
    "MSLogin: selectedRolle state"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. MSLogin — når 2FA-kode er fuldt indtastet → kald onDone med rolle
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """    if (nc.every(c => c !== '')) setTimeout(() => setStep(3),""",
    """    if (nc.every(c => c !== '')) setTimeout(() => { setStep(3); setTimeout(() => onDone(selectedRolle), 900); },""",
    "MSLogin: onDone kalder med selectedRolle efter 2FA"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. AppWithTweaks — brug rolle fra MSLogin-onDone til at sætte tweaks.role
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """    content = <MSLogin onDone={() => setTweak("flow", "none")} onCancel={() => setTweak("flow", "none")} />;""",
    """    content = <MSLogin
      onDone={(rolle) => { if (rolle) setTweak("role", rolle); setTweak("flow", "none"); }}
      onCancel={() => setTweak("flow", "none")}
    />;""",
    "AppWithTweaks: modtag rolle fra MSLogin og sæt tweaks.role"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'OK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

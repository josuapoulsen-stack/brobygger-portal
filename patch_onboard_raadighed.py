import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

A = c.index("const OnboardingWizard = ({ onClose }) => {")
B = c.index("const MSLogin = ({ onDone, onCancel }) => {")
seg = c[A:B]
orig = seg

BLOCK = """        {step === 4 && (
          <>
            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,
              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>
              Hvornår kan du typisk?
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>
              Dette er bare en vejledende idé — du melder rådighed når det passer dig.
            </div>
            {['Hverdage formiddag', 'Hverdage eftermiddag', 'Hverdage aften', 'Weekend formiddag', 'Weekend eftermiddag'].map(opt => {
              const sel = data.availability.includes(opt);
              return (
                <button key={opt} onClick={() => toggle('availability', opt)} style={{
                  display: 'flex', alignItems: 'center', gap: 14, width: '100%',
                  padding: 14, marginBottom: 6, textAlign: 'left',
                  background: sel ? SoS.orange + '15' : '#fff',
                  border: `2px solid ${sel ? SoS.orange : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, cursor: 'pointer',
                }}>
                  <Icon name="clock" size={20} color={sel ? SoS.orange : SoS.inkMuted}/>
                  <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>
                    {opt}
                  </span>
                  {sel && <Icon name="check" size={18} color={SoS.orange} weight={2.5}/>}
                </button>
              );
            })}
          </>
        )}

"""

steps_failures = []
def must(cond, label):
    if not cond: steps_failures.append(label)

must(BLOCK in seg, "rådighed-blok findes")
seg = seg.replace(BLOCK, "")

# Omnummerér (rækkefølge: 5→4 først, derefter 6→5)
must("step === 5" in seg, "step===5 findes")
seg = seg.replace("step === 5", "step === 4")
must("step === 6" in seg, "step===6 findes")
seg = seg.replace("step === 6", "step === 5")
must("step < 6" in seg, "step < 6 findes")
seg = seg.replace("step < 6", "step < 5")

# Fjern 'Rådighed' fra steps-array
must("'Typer', 'Rådighed', 'Sprog'" in seg, "steps-array findes")
seg = seg.replace("'Typer', 'Rådighed', 'Sprog'", "'Typer', 'Sprog'")

# Tekst: Seks → Fem spørgsmål
seg = seg.replace("Seks hurtige spørgsmål", "Fem hurtige spørgsmål")

c = c[:A] + seg + c[B:]

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

if steps_failures:
    print("FAIL:", steps_failures)
else:
    print("OK: rådighed-trin fjernet + omnummereret")
    print("  resterende 'step === 6' i segment:", seg.count("step === 6"))
    print("  resterende 'Rådighed' i segment:", seg.count("Rådighed"))

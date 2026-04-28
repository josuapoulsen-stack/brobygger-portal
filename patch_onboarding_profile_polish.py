# -*- coding: utf-8 -*-
"""
patch_onboarding_profile_polish.py
1. OnboardingWizard: nyt 'Om dig'-trin (personlige oplysninger + inkl. køn)
   + gemmer til SoS_STORE ved afslutning
2. ProfileScreen: redigerbar 'Personlige oplysninger' med gem til localStorage
3. Ryd live-chat knap i TweaksPanel
4. Brobygger default = Maja (erfaren) — nulstil ved rollesskift
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ════════════════════════════════════════════════════════════════════════════
# 1. ONBOARDING WIZARD
# ════════════════════════════════════════════════════════════════════════════

# 1a. Udvid initial data + steps-array
OLD_OB_INIT = (
    "  const [step, setStep] = React.useState(0);\n"
    "  const [data, setData] = React.useState({\n"
    "    hovedsaede: null, types: [], availability: [], transport: null, languages: [],\n"
    "  });\n"
    "  const set = (k, v) => setData(d => ({ ...d, [k]: v }));\n"
    "  const toggle = (k, v) => setData(d => ({ ...d, [k]: d[k].includes(v) ? d[k].filter(x => x !== v) : [...d[k], v] }));\n"
    "\n"
    "  const steps = ['Velkommen', 'Hoveds\u00e6de', 'Typer', 'R\u00e5dighed', 'Sprog', 'F\u00e6rdig'];"
)
NEW_OB_INIT = (
    "  const [step, setStep] = React.useState(0);\n"
    "  const [data, setData] = React.useState({\n"
    "    fornavn: '', efternavn: '', email: '', mobil: '', kon: null,\n"
    "    hovedsaede: null, types: [], availability: [], transport: null, languages: [],\n"
    "  });\n"
    "  const set = (k, v) => setData(d => ({ ...d, [k]: v }));\n"
    "  const toggle = (k, v) => setData(d => ({ ...d, [k]: d[k].includes(v) ? d[k].filter(x => x !== v) : [...d[k], v] }));\n"
    "\n"
    "  const steps = ['Velkommen', 'Om dig', 'Hoveds\u00e6de', 'Typer', 'R\u00e5dighed', 'Sprog', 'F\u00e6rdig'];"
)
cnt = html.count(OLD_OB_INIT)
html = html.replace(OLD_OB_INIT, NEW_OB_INIT, 1)
results.append(('Onboarding: udvid state + steps', cnt, 1))

# 1b. Gradient-betingelse: step === 5 → step === 6
OLD_GRAD = (
    "      background: step === 0 || step === 5\n"
    "        ? `linear-gradient(165deg, ${SoS.orangeSoft} 0%, ${SoS.orange} 60%, ${SoS.orangeDeep} 100%)`\n"
    "        : SoS.cream,\n"
    "      display: 'flex', flexDirection: 'column',\n"
    "      color: step === 0 || step === 5 ? '#fff' : SoS.ink, transition: 'background 0.3s',"
)
NEW_GRAD = (
    "      background: step === 0 || step === 6\n"
    "        ? `linear-gradient(165deg, ${SoS.orangeSoft} 0%, ${SoS.orange} 60%, ${SoS.orangeDeep} 100%)`\n"
    "        : SoS.cream,\n"
    "      display: 'flex', flexDirection: 'column',\n"
    "      color: step === 0 || step === 6 ? '#fff' : SoS.ink, transition: 'background 0.3s',"
)
cnt = html.count(OLD_GRAD)
html = html.replace(OLD_GRAD, NEW_GRAD, 1)
results.append(('Onboarding: gradient step 5->6', cnt, 1))

# 1c. Header synlighed: step !== 5 → step !== 6
OLD_HDR = "      {step !== 0 && step !== 5 && ("
NEW_HDR = "      {step !== 0 && step !== 6 && ("
cnt = html.count(OLD_HDR)
html = html.replace(OLD_HDR, NEW_HDR, 1)
results.append(('Onboarding: header synlighed step 5->6', cnt, 1))

# 1d. Step 1 (Hovedsæde) → step 2; indsæt 'Om dig' som step 1
# Find step===1 blokken og erstat dens åbning med step===2
OLD_STEP1_OPEN = "        {step === 1 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilket hoveds\u00e6de?"
NEW_STEP1_OPEN = "        {step === 2 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilket hoveds\u00e6de?"
cnt = html.count(OLD_STEP1_OPEN)
html = html.replace(OLD_STEP1_OPEN, NEW_STEP1_OPEN, 1)
results.append(('Onboarding: Hoveds. step 1->2', cnt, 1))

OLD_STEP2 = "{step === 2 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilke typer vil du hj\u00e6lpe med?"
NEW_STEP2 = "{step === 3 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilke typer vil du hj\u00e6lpe med?"
cnt = html.count(OLD_STEP2)
html = html.replace(OLD_STEP2, NEW_STEP2, 1)
results.append(('Onboarding: Typer step 2->3', cnt, 1))

OLD_STEP3 = "{step === 3 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvorn\u00e5r kan du typisk?"
NEW_STEP3 = "{step === 4 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvorn\u00e5r kan du typisk?"
cnt = html.count(OLD_STEP3)
html = html.replace(OLD_STEP3, NEW_STEP3, 1)
results.append(('Onboarding: Radighed step 3->4', cnt, 1))

OLD_STEP4 = "{step === 4 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilke sprog taler du?"
NEW_STEP4 = "{step === 5 && (\n          <>\n            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n              color: SoS.ink, marginBottom: 8, letterSpacing: -0.3 }}>\n              Hvilke sprog taler du?"
cnt = html.count(OLD_STEP4)
html = html.replace(OLD_STEP4, NEW_STEP4, 1)
results.append(('Onboarding: Sprog step 4->5', cnt, 1))

OLD_STEP5 = "{step === 5 && (\n          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center' }}>"
NEW_STEP5 = "{step === 6 && (\n          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center' }}>"
cnt = html.count(OLD_STEP5)
html = html.replace(OLD_STEP5, NEW_STEP5, 1)
results.append(('Onboarding: Faerdig step 5->6', cnt, 1))

# 1e. Indsæt 'Om dig' (step 1) — og opdater Færdig-data-reference
OLD_STEP_WELCOME_END = (
    "        {step === 0 && (\n"
    "          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>\n"
    "            <SSLogo size={72} bg=\"rgba(255,255,255,0.2)\"/>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,\n"
    "              letterSpacing: 1.5, marginTop: 22, textTransform: 'uppercase', opacity: 0.85 }}>\n"
    "              Velkommen som brobygger\n"
    "            </div>\n"
    "            <div style={{ fontFamily: SoS.font, fontSize: 42, fontWeight: 400,\n"
    "              lineHeight: 1.05, letterSpacing: -1, marginTop: 12 }}>\n"
    "              Lad os l\u00e6re dig<br/><span style={{ fontStyle: 'italic' }}>at kende</span>\n"
    "            </div>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 15, lineHeight: 1.5,\n"
    "              marginTop: 18, opacity: 0.9, maxWidth: 300 }}>\n"
    "              Fem hurtige sp\u00f8rgsm\u00e5l \u2014 s\u00e5 kan vi matche dig med mennesker der passer til dig.\n"
    "            </div>\n"
    "          </div>\n"
    "        )}\n"
    "\n"
    "        {step === 2 && ("
)
NEW_STEP_WELCOME_END = (
    "        {step === 0 && (\n"
    "          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>\n"
    "            <SSLogo size={72} bg=\"rgba(255,255,255,0.2)\"/>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,\n"
    "              letterSpacing: 1.5, marginTop: 22, textTransform: 'uppercase', opacity: 0.85 }}>\n"
    "              Velkommen som brobygger\n"
    "            </div>\n"
    "            <div style={{ fontFamily: SoS.font, fontSize: 42, fontWeight: 400,\n"
    "              lineHeight: 1.05, letterSpacing: -1, marginTop: 12 }}>\n"
    "              Lad os l\u00e6re dig<br/><span style={{ fontStyle: 'italic' }}>at kende</span>\n"
    "            </div>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 15, lineHeight: 1.5,\n"
    "              marginTop: 18, opacity: 0.9, maxWidth: 300 }}>\n"
    "              Seks hurtige sp\u00f8rgsm\u00e5l \u2014 s\u00e5 kan vi matche dig med mennesker der passer til dig.\n"
    "            </div>\n"
    "          </div>\n"
    "        )}\n"
    "\n"
    "        {/* ── Om dig (step 1) ── */}\n"
    "        {step === 1 && (() => {\n"
    "          const inpStyle = {\n"
    "            width: '100%', padding: '12px 14px', border: `1.5px solid ${SoS.lineSoft}`,\n"
    "            borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 15, color: SoS.ink,\n"
    "            background: '#fff', outline: 'none', marginBottom: 12, boxSizing: 'border-box',\n"
    "          };\n"
    "          const KON_OPTIONS = [\n"
    "            'Mand', 'Kvinde', 'Non-bin\u00e6r', 'Foretr\u00e6kker ikke at oplyse',\n"
    "          ];\n"
    "          return (\n"
    "            <>\n"
    "              <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n"
    "                color: SoS.ink, marginBottom: 4, letterSpacing: -0.3 }}>Om dig</div>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>\n"
    "                Dine oplysninger er kun synlige for din koordinator.\n"
    "              </div>\n"
    "              <input value={data.fornavn} onChange={e => set('fornavn', e.target.value)}\n"
    "                placeholder=\"Fornavn *\" style={inpStyle}/>\n"
    "              <input value={data.efternavn} onChange={e => set('efternavn', e.target.value)}\n"
    "                placeholder=\"Efternavn *\" style={inpStyle}/>\n"
    "              <input value={data.email} onChange={e => set('email', e.target.value)}\n"
    "                type=\"email\" placeholder=\"E-mailadresse *\" style={inpStyle}/>\n"
    "              <input value={data.mobil} onChange={e => set('mobil', e.target.value)}\n"
    "                type=\"tel\" inputMode=\"tel\" placeholder=\"Mobilnummer (8 cifre) *\" style={inpStyle}/>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,\n"
    "                color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',\n"
    "                marginBottom: 10, marginTop: 4 }}>K\u00f8n</div>\n"
    "              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 8 }}>\n"
    "                {KON_OPTIONS.map(opt => {\n"
    "                  const sel = data.kon === opt;\n"
    "                  return (\n"
    "                    <button key={opt} onClick={() => set('kon', sel ? null : opt)} style={{\n"
    "                      padding: '9px 16px', borderRadius: 999, cursor: 'pointer',\n"
    "                      background: sel ? SoS.orange : '#fff',\n"
    "                      color: sel ? '#fff' : SoS.ink,\n"
    "                      border: `2px solid ${sel ? SoS.orange : SoS.lineSoft}`,\n"
    "                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 500,\n"
    "                    }}>{opt}</button>\n"
    "                  );\n"
    "                })}\n"
    "              </div>\n"
    "            </>\n"
    "          );\n"
    "        })()}\n"
    "\n"
    "        {step === 2 && ("
)
cnt = html.count(OLD_STEP_WELCOME_END)
html = html.replace(OLD_STEP_WELCOME_END, NEW_STEP_WELCOME_END, 1)
results.append(('Onboarding: indsaet Om dig step 1', cnt, 1))

# 1f. Footer: bund-panel step === 5 → step === 6 (to steder)
OLD_FOOTER = (
    "      <div style={{ padding: '16px 20px 34px', display: 'flex', gap: 10,\n"
    "        background: step === 0 || step === 5 ? 'transparent' : '#fff',\n"
    "        borderTop: step === 0 || step === 5 ? 'none' : `1px solid ${SoS.line}` }}>\n"
    "        <Button full\n"
    "          onClick={() => step === 5 ? onClose() : setStep(step + 1)}\n"
    "          variant={step === 0 || step === 5 ? 'secondary' : 'primary'}\n"
    "          style={step === 0 || step === 5\n"
    "            ? { background: '#fff', color: SoS.orange, boxShadow: SoS.shadow.md }\n"
    "            : {}}>\n"
    "          {step === 0 ? 'Kom i gang' : step === 5 ? 'G\u00e5 til appen' : 'Forts\u00e6t'}\n"
    "        </Button>\n"
    "      </div>"
)
NEW_FOOTER = (
    "      <div style={{ padding: '16px 20px 34px', display: 'flex', gap: 10,\n"
    "        background: step === 0 || step === 6 ? 'transparent' : '#fff',\n"
    "        borderTop: step === 0 || step === 6 ? 'none' : `1px solid ${SoS.line}` }}>\n"
    "        {/* Forrige-knap (ikke på trin 0, 1 og 6) */}\n"
    "        {step > 1 && step < 6 && (\n"
    "          <Button onClick={() => setStep(step - 1)} variant=\"secondary\"\n"
    "            style={{ flex: '0 0 auto', padding: '0 18px' }}>\n"
    "            <Icon name=\"chevronL\" size={18} color={SoS.ink}/>\n"
    "          </Button>\n"
    "        )}\n"
    "        <Button full\n"
    "          disabled={step === 1 && (!data.fornavn.trim() || !data.email.trim() || !data.mobil.trim())}\n"
    "          onClick={() => {\n"
    "            if (step === 6) {\n"
    "              // Gem til localStorage\n"
    "              window.SoS_STORE?.save('profile', {\n"
    "                navn:      (data.fornavn + ' ' + data.efternavn).trim(),\n"
    "                fornavn:   data.fornavn,\n"
    "                efternavn: data.efternavn,\n"
    "                email:     data.email,\n"
    "                mobil:     data.mobil,\n"
    "                kon:       data.kon,\n"
    "              });\n"
    "              onClose();\n"
    "            } else {\n"
    "              setStep(step + 1);\n"
    "            }\n"
    "          }}\n"
    "          variant={step === 0 || step === 6 ? 'secondary' : 'primary'}\n"
    "          style={step === 0 || step === 6\n"
    "            ? { background: '#fff', color: SoS.orange, boxShadow: SoS.shadow.md }\n"
    "            : {}}>\n"
    "          {step === 0 ? 'Kom i gang' : step === 6 ? 'G\u00e5 til appen' : 'Forts\u00e6t'}\n"
    "        </Button>\n"
    "      </div>"
)
cnt = html.count(OLD_FOOTER)
html = html.replace(OLD_FOOTER, NEW_FOOTER, 1)
results.append(('Onboarding: footer + gem-logik step 5->6', cnt, 1))

# 1g. Færdig-tekst: data.hovedsaede reference (step 6, var step 5)
OLD_FAERDIG_TEXT = (
    "              Din koordinator i {data.hoveds\u00e6de || 'dit hoveds\u00e6de'} kigger p\u00e5 dine svar og vender tilbage inden for f\u00e5 dage."
)
NEW_FAERDIG_TEXT = (
    "              {data.fornavn && <span>Hej {data.fornavn}! </span>}Din koordinator i {data.hoveds\u00e6de || 'dit hoveds\u00e6de'} kigger p\u00e5 dine svar og vender tilbage inden for f\u00e5 dage."
)
cnt = html.count(OLD_FAERDIG_TEXT)
html = html.replace(OLD_FAERDIG_TEXT, NEW_FAERDIG_TEXT, 1)
results.append(('Onboarding: Faerdig-tekst med fornavn', cnt, 1))

# ════════════════════════════════════════════════════════════════════════════
# 2. PROFILESCREEN — redigerbar "Personlige oplysninger"
# ════════════════════════════════════════════════════════════════════════════

# 2a. Tilføj states i ProfileScreen
OLD_PROFILE_STATE = "  const [subPage, setSubPage] = React.useState(null);"
NEW_PROFILE_STATE = (
    "  const [subPage, setSubPage] = React.useState(null);\n"
    "  // Redigerbare profilfelter — indl\u00e6ses fra localStorage\n"
    "  const [pf, setPf] = React.useState(() => {\n"
    "    const s = window.SoS_STORE?.load('profile');\n"
    "    return {\n"
    "      navn:  s?.navn  || user.name || '',\n"
    "      email: s?.email || 'maja.holmberg@socialsundhed.org',\n"
    "      mobil: s?.mobil || '+45 23 45 67 89',\n"
    "    };\n"
    "  });\n"
    "  const [pEdit, setPEdit] = React.useState(false);\n"
    "  const [pSaved, setPSaved] = React.useState(false);\n"
    "  const saveProfile = () => {\n"
    "    window.SoS_STORE?.save('profile', pf);\n"
    "    setPEdit(false);\n"
    "    setPSaved(true);\n"
    "    setTimeout(() => setPSaved(false), 2500);\n"
    "  };"
)
cnt = html.count(OLD_PROFILE_STATE)
html = html.replace(OLD_PROFILE_STATE, NEW_PROFILE_STATE, 1)
results.append(('ProfileScreen: tilfoej redigerings-states', cnt, 1))

# 2b. Erstat statisk personlig-underside med redigerbar udgave
OLD_PERSONLIG = (
    "  // \u2500\u2500 Personlige oplysninger-underside\n"
    "  if (subPage === 'personlig') return (\n"
    "    <>\n"
    "      <BackHeader title=\"Personlige oplysninger\"/>\n"
    "      <div style={{ padding: '16px 20px 20px' }}>\n"
    "        <div style={{ background: '#fff', borderRadius: SoS.r.lg,\n"
    "          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>\n"
    "          {[\n"
    "            { label: 'Navn', value: user.name },\n"
    "            { label: 'Rolle', value: 'Brobygger' },\n"
    "            { label: 'Hoveds\u00e6de', value: user.hoveds\u00e6de || 'Aarhus' },\n"
    "            { label: 'Startdato', value: 'Oktober 2024' },\n"
    "            { label: 'Email', value: 'maja.holmberg@socialsundhed.org' },\n"
    "            { label: 'Telefon', value: '+45 23 45 67 89' },\n"
    "          ].map((row, i, arr) => (\n"
    "            <div key={i} style={{ padding: '13px 16px',\n"
    "              borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',\n"
    "              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>\n"
    "              <span style={{ fontFamily: SoS.sans, fontSize: 13,\n"
    "                color: SoS.inkSoft }}>{row.label}</span>\n"
    "              <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500,\n"
    "                color: SoS.ink }}>{row.value}</span>\n"
    "            </div>\n"
    "          ))}\n"
    "        </div>\n"
    "        <div style={{ padding: '12px 14px', background: SoS.creamDeep, borderRadius: SoS.r.md,\n"
    "          fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>\n"
    "          For at \u00e6ndre dine oplysninger skal du kontakte din koordinator.\n"
    "        </div>\n"
    "      </div>\n"
    "    </>\n"
    "  );"
)
NEW_PERSONLIG = (
    "  // \u2500\u2500 Personlige oplysninger-underside (redigerbar)\n"
    "  if (subPage === 'personlig') {\n"
    "    const inpSt = {\n"
    "      width: '100%', padding: '11px 13px', border: `1.5px solid ${pEdit ? SoS.orange + '80' : SoS.lineSoft}`,\n"
    "      borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,\n"
    "      background: pEdit ? '#fff' : SoS.creamDeep, outline: 'none', boxSizing: 'border-box',\n"
    "      transition: 'border-color 0.2s, background 0.2s',\n"
    "    };\n"
    "    return (\n"
    "      <>\n"
    "        <BackHeader title=\"Personlige oplysninger\"/>\n"
    "        <div style={{ padding: '16px 20px 20px' }}>\n"
    "\n"
    "          {/* Ikke-redigerbare felter */}\n"
    "          <div style={{ background: '#fff', borderRadius: SoS.r.lg,\n"
    "            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>\n"
    "            {[\n"
    "              { label: 'Rolle',      value: 'Brobygger' },\n"
    "              { label: 'Hoveds\u00e6de', value: user.hoveds\u00e6de || 'Aarhus' },\n"
    "              { label: 'Startdato', value: 'Oktober 2024' },\n"
    "            ].map((row, i, arr) => (\n"
    "              <div key={i} style={{ padding: '13px 16px',\n"
    "                borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',\n"
    "                display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>\n"
    "                <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{row.label}</span>\n"
    "                <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>{row.value}</span>\n"
    "              </div>\n"
    "            ))}\n"
    "          </div>\n"
    "\n"
    "          {/* Redigerbare felter */}\n"
    "          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n"
    "            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase',\n"
    "            marginBottom: 10 }}>Dine oplysninger</div>\n"
    "\n"
    "          {[{ label: 'Navn', key: 'navn' }, { label: 'Email', key: 'email' }, { label: 'Mobil', key: 'mobil' }].map(f => (\n"
    "            <div key={f.key} style={{ marginBottom: 10 }}>\n"
    "              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginBottom: 4 }}>{f.label}</div>\n"
    "              <input\n"
    "                value={pf[f.key]}\n"
    "                readOnly={!pEdit}\n"
    "                type={f.key === 'email' ? 'email' : f.key === 'mobil' ? 'tel' : 'text'}\n"
    "                inputMode={f.key === 'mobil' ? 'tel' : undefined}\n"
    "                onChange={e => setPf(prev => ({ ...prev, [f.key]: e.target.value }))}\n"
    "                style={{ ...inpSt }}\n"
    "              />\n"
    "            </div>\n"
    "          ))}\n"
    "\n"
    "          {pSaved && (\n"
    "            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px',\n"
    "              background: SoS.sageSoft, borderRadius: SoS.r.md, marginBottom: 12 }}>\n"
    "              <Icon name=\"check\" size={16} color={SoS.sage} weight={2.5}/>\n"
    "              <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.sage, fontWeight: 600 }}>Gemt!</span>\n"
    "            </div>\n"
    "          )}\n"
    "\n"
    "          {pEdit ? (\n"
    "            <div style={{ display: 'flex', gap: 10 }}>\n"
    "              <Button full onClick={saveProfile}>Gem \u00e6ndringer</Button>\n"
    "              <Button variant=\"secondary\" onClick={() => setPEdit(false)} style={{ flex: '0 0 auto', padding: '0 18px' }}>Annuller</Button>\n"
    "            </div>\n"
    "          ) : (\n"
    "            <Button full variant=\"secondary\" onClick={() => setPEdit(true)}>Rediger oplysninger</Button>\n"
    "          )}\n"
    "        </div>\n"
    "      </>\n"
    "    );\n"
    "  }"
)
cnt = html.count(OLD_PERSONLIG)
html = html.replace(OLD_PERSONLIG, NEW_PERSONLIG, 1)
results.append(('ProfileScreen: redigerbar personlig side', cnt, 1))

# ════════════════════════════════════════════════════════════════════════════
# 3. RYDLIVE-CHAT KNAP I TWEAKSPANEL
# ════════════════════════════════════════════════════════════════════════════
OLD_RESET_BTN = (
    "        <TweakSection label=\"Testdata\">\n"
    "          <button onClick={() => {\n"
    "            if (window.confirm('Nulstil al testdata og genindl\u00e6s prototypen?')) {\n"
    "              window.SoS_STORE?.clear();\n"
    "              window.location.reload();\n"
    "            }\n"
    "          }} style={{\n"
    "            width: '100%', padding: '8px 0', borderRadius: 8, border: 'none',\n"
    "            background: '#FFE8E0', color: '#C0392B',\n"
    "            fontFamily: 'system-ui', fontSize: 12, fontWeight: 600, cursor: 'pointer',\n"
    "          }}>\n"
    "            Nulstil testdata\n"
    "          </button>\n"
    "        </TweakSection>"
)
NEW_RESET_BTN = (
    "        <TweakSection label=\"Testdata\">\n"
    "          <button onClick={() => {\n"
    "            localStorage.removeItem('sos_live_chat');\n"
    "            alert('Live-chat ryddet.');\n"
    "          }} style={{\n"
    "            width: '100%', padding: '8px 0', borderRadius: 8, border: 'none',\n"
    "            background: '#E8F0FE', color: '#1A56DB',\n"
    "            fontFamily: 'system-ui', fontSize: 12, fontWeight: 600, cursor: 'pointer',\n"
    "            marginBottom: 6,\n"
    "          }}>\n"
    "            Ryd live-chat\n"
    "          </button>\n"
    "          <button onClick={() => {\n"
    "            if (window.confirm('Nulstil al testdata og genindl\u00e6s prototypen?')) {\n"
    "              window.SoS_STORE?.clear();\n"
    "              window.location.reload();\n"
    "            }\n"
    "          }} style={{\n"
    "            width: '100%', padding: '8px 0', borderRadius: 8, border: 'none',\n"
    "            background: '#FFE8E0', color: '#C0392B',\n"
    "            fontFamily: 'system-ui', fontSize: 12, fontWeight: 600, cursor: 'pointer',\n"
    "          }}>\n"
    "            Nulstil testdata\n"
    "          </button>\n"
    "        </TweakSection>"
)
cnt = html.count(OLD_RESET_BTN)
html = html.replace(OLD_RESET_BTN, NEW_RESET_BTN, 1)
results.append(('TweaksPanel: Ryd live-chat knap', cnt, 1))

# ════════════════════════════════════════════════════════════════════════════
# 4. BROBYGGER DEFAULT = MAJA (nulstil experience ved rolleskift)
# ════════════════════════════════════════════════════════════════════════════
OLD_ROLE_EFFECT = (
    "  useEffect(() => {\n"
    "    setScreen(\"hjem\");\n"
    "    setDetailId(null);\n"
    "    setSettingsOpen(false);\n"
    "    if (activeRole === \"brobygger\") setDesktopMode(false);\n"
    "  }, [activeRole]);"
)
NEW_ROLE_EFFECT = (
    "  useEffect(() => {\n"
    "    setScreen(\"hjem\");\n"
    "    setDetailId(null);\n"
    "    setSettingsOpen(false);\n"
    "    if (activeRole === \"brobygger\") {\n"
    "      setDesktopMode(false);\n"
    "      // Nulstil til erfaren-tilstand (Maja) n\u00e5r man skifter til brobygger\n"
    "      if (tweaks.experience === \"new\") setTweak(\"experience\", \"experienced\");\n"
    "    }\n"
    "  }, [activeRole]);"
)
cnt = html.count(OLD_ROLE_EFFECT)
html = html.replace(OLD_ROLE_EFFECT, NEW_ROLE_EFFECT, 1)
results.append(('Brobygger default = Maja ved rolleskift', cnt, 1))

# ── Save ──────────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

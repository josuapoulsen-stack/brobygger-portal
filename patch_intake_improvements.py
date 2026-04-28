# -*- coding: utf-8 -*-
"""
patch_intake_improvements.py
1. Type-specifikke behov i intake (sundhed/forening/social)
2. Ryd selectedBehov når type skifter
3. Tom-state prompt når ingen type valgt
4. Telefon-validering: præcis 8 cifre
5. Telefon-fejlhint under feltet
6. SROI + helbredsforhold flyttes under GDPR-boks
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. Erstat INTAKE_BEHOV med type-specifik map ─────────────────────────
idx = html.find('INTAKE_BEHOV = [')
end_idx = html.find('];\n\nconst FieldLabel', idx) + len('];\n')
if idx != -1 and end_idx > idx:
    NEW_BEHOV = (
        'INTAKE_BEHOV_BY_TYPE = {\n'
        "  sundhed: [\n"
        "    'Hj\u00e6lp til l\u00e6gebes\u00f8g',\n"
        "    'F\u00f8lge til behandling',\n"
        "    'Transport og ledsagelse',\n"
        "    'Medicin og dosering',\n"
        "    'Kontakt til sundhedsv\u00e6senet',\n"
        "    'Genptr\u00e6ning og motion',\n"
        "    'Kost og ern\u00e6ring',\n"
        "    'Praktisk st\u00f8tte i hverdagen',\n"
        "    'Andet',\n"
        '  ],\n'
        '  forening: [\n'
        "    'Foreningsliv og f\u00e6llesskab',\n"
        "    'Sport og motion',\n"
        "    'Sproglig st\u00f8tte',\n"
        "    'Kulturelle aktiviteter',\n"
        "    'Frivilligt arbejde',\n"
        "    'Netv\u00e6rk og socialt f\u00e6llesskab',\n"
        "    'Hobby og interesser',\n"
        "    'Integration og tilh\u00f8rsforhold',\n"
        "    'Andet',\n"
        '  ],\n'
        '  social: [\n'
        "    'Selskab og samtale',\n"
        "    'G\u00e5ture / frisk luft',\n"
        "    'F\u00f8lgeskab og n\u00e6rv\u00e6r',\n"
        "    'Let motion',\n"
        "    'Indk\u00f8b og \u00e6rinder',\n"
        "    'Kulturelle oplevelser',\n"
        "    'Praktisk hj\u00e6lp',\n"
        "    'Modvirke ensomhed',\n"
        "    'Andet',\n"
        '  ],\n'
        '};\n'
    )
    html = html[:idx] + NEW_BEHOV + html[end_idx:]
    results.append(('INTAKE_BEHOV_BY_TYPE', 1, 1))
else:
    results.append(('INTAKE_BEHOV_BY_TYPE', 0, 1))

# ── 2. Ryd selectedBehov når type skiftes ────────────────────────────────
OLD_TYPE_CLICK = "onClick={() => setType(t.id)}"
NEW_TYPE_CLICK = "onClick={() => { setType(t.id); setSelectedBehov([]); }}"
cnt = html.count(OLD_TYPE_CLICK)
html = html.replace(OLD_TYPE_CLICK, NEW_TYPE_CLICK, 1)
results.append(('Ryd behov ved typeskift', cnt, 1))

# ── 3. Brug type-specifik liste + tom-state ──────────────────────────────
OLD_MAP = '{INTAKE_BEHOV.map(b => {'
NEW_MAP = '{(INTAKE_BEHOV_BY_TYPE[type] || []).map(b => {'
cnt = html.count(OLD_MAP)
html = html.replace(OLD_MAP, NEW_MAP, 1)
results.append(('Behov map -> type-specifik', cnt, 1))

# Tilføj tom-state prompt og betinget div-åbning
OLD_BEHOV_LABEL = (
    "{/* Specifikke behov */}\n"
    "            <FieldLabel note=\"v\u00e6lg alle der passer\">Specifikke behov</FieldLabel>\n"
    "            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 22 }}>"
)
NEW_BEHOV_LABEL = (
    "{/* Specifikke behov */}\n"
    "            <FieldLabel note={type ? 'v\u00e6lg alle der passer' : 'v\u00e6lg en type ovenfor f\u00f8rst'}>"
    "Specifikke behov</FieldLabel>\n"
    "            {!type && (\n"
    "              <div style={{ padding: '14px 16px', background: SoS.creamDeep,\n"
    "                borderRadius: SoS.r.sm, marginBottom: 22,\n"
    "                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>\n"
    "                V\u00e6lg en brobygningstype ovenfor for at se relevante behov.\n"
    "              </div>\n"
    "            )}\n"
    "            {type && <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 22 }}>"
)
cnt = html.count(OLD_BEHOV_LABEL)
html = html.replace(OLD_BEHOV_LABEL, NEW_BEHOV_LABEL, 1)
results.append(('Behov tom-state + betinget div', cnt, 1))

# Luk den betingede div (efter chip-listen)
OLD_BEHOV_CLOSE = (
    "              </button>\n"
    "                  );\n"
    "                })}\n"
    "            </div>\n"
    "\n"
    "            {/* Kontekstnote"
)
NEW_BEHOV_CLOSE = (
    "              </button>\n"
    "                  );\n"
    "                })}\n"
    "            </div>}\n"
    "\n"
    "            {/* Kontekstnote"
)
cnt = html.count(OLD_BEHOV_CLOSE)
html = html.replace(OLD_BEHOV_CLOSE, NEW_BEHOV_CLOSE, 1)
results.append(('Behov betinget div luk', cnt, 1))

# ── 4. Telefon-validering: præcis 8 cifre ───────────────────────────────
OLD_CAN1 = (
    "const canNext1 = form.firstName.trim().length > 0 "
    "&& form.age.trim().length > 0 "
    "&& form.phone.trim().length > 0;"
)
NEW_CAN1 = (
    "const phoneDigits = form.phone.replace(/\\D/g, '');\n"
    "  const phoneOk = phoneDigits.length === 8;\n"
    "  const canNext1 = form.firstName.trim().length > 0 "
    "&& form.age.trim().length > 0 && phoneOk;"
)
cnt = html.count(OLD_CAN1)
html = html.replace(OLD_CAN1, NEW_CAN1, 1)
results.append(('Telefon-validering 8 cifre', cnt, 1))

# ── 5. Telefon-fejlhint under inputfeltet ────────────────────────────────
# Indsæt hint efter inputStyle afslutning for phone-feltet
OLD_PHONE_INPUT = (
    "                <input\n"
    "                  type={field.type || 'text'}\n"
    "                  placeholder={field.placeholder}\n"
    "                  value={form[field.key]}\n"
    "                  onChange={e => setForm(f => ({ ...f, [field.key]: e.target.value }))}\n"
    "                  style={inputStyle}\n"
    "                />\n"
    "              </div>"
)
NEW_PHONE_INPUT = (
    "                <input\n"
    "                  type={field.type || 'text'}\n"
    "                  placeholder={field.placeholder}\n"
    "                  value={form[field.key]}\n"
    "                  onChange={e => setForm(f => ({ ...f, [field.key]: e.target.value }))}\n"
    "                  style={{...inputStyle,\n"
    "                    borderColor: field.key === 'phone' && form.phone.length > 0 && !phoneOk\n"
    "                      ? '#E05252' : inputStyle.borderColor }}\n"
    "                />\n"
    "                {field.key === 'phone' && form.phone.length > 0 && !phoneOk && (\n"
    "                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: '#E05252',\n"
    "                    marginTop: 4 }}>Mobilnummer skal v\u00e6re pr\u00e6cis 8 cifre</div>\n"
    "                )}\n"
    "              </div>"
)
cnt = html.count(OLD_PHONE_INPUT)
html = html.replace(OLD_PHONE_INPUT, NEW_PHONE_INPUT, 1)
results.append(('Telefon fejlhint', cnt, 1))

# ── 6. Flyt SROI + helbredsforhold under GDPR-boks ──────────────────────
# Find samtykke-boks (GDPR art. 9 info-boks) i step 2
# Den indeholder tekst om GDPR — vi vil at SROI + helbred er INDEN i eller UNDER den
# Aktuelt er rækkefølgen: [SROI] [Helbred] [Kontekstnote]
# Vi ønsker: [Kontekstnote / GDPR-info] [SROI] [Helbred]
# Find kontekstnote-sektionen og flyt den op over SROI
OLD_CONTEXT = (
    "            {/* Kontekstnote"
)
# Vi leder efter den faktiske tekst
idx_sroi = html.find('{/* SROI-m\u00e5lgruppe')
idx_context = html.find('{/* Kontekstnote', idx_sroi)
if idx_sroi != -1 and idx_context != -1:
    # Find end of kontekstnote block — det slutter ved næste {/* eller ved step-close
    idx_helbred = html.find('{/* Faglig helbreds', idx_sroi)
    # Extract kontekstnote block (between context and helbred)
    context_block = html[idx_context:idx_helbred]
    # Remove it from current position
    html_without_context = html[:idx_context] + html[idx_helbred:]
    # Insert it before SROI
    new_sroi_idx = html_without_context.find('{/* SROI-m\u00e5lgruppe')
    html = html_without_context[:new_sroi_idx] + context_block + html_without_context[new_sroi_idx:]
    results.append(('GDPR-kontekstnote flyttes over SROI', 1, 1))
else:
    results.append(('GDPR-kontekstnote flytning', 0, 1))

# ── Save ──────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

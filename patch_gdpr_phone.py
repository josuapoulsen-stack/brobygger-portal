# -*- coding: utf-8 -*-
"""
patch_gdpr_phone.py
1. Telefon-felt: type='tel' + inputMode='tel' (viser nummerblok på mobil)
2. SROI + helbredsforhold pakkes ind i en GDPR-sektion med header
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ── 1. Tilf\u00f8j type: 'tel' til telefon-feltet ─────────────────────────────
OLD_PHONE_FIELD = (
    "{ key: 'phone',     label: 'Telefon',   "
    "placeholder: 'f.eks. +45 28 34 56 78', required: true },"
)
NEW_PHONE_FIELD = (
    "{ key: 'phone',     label: 'Telefon',   type: 'tel', "
    "placeholder: '12 34 56 78', required: true },"
)
cnt = html.count(OLD_PHONE_FIELD)
html = html.replace(OLD_PHONE_FIELD, NEW_PHONE_FIELD, 1)
results.append(('Telefon type=tel', cnt, 1))

# Tilf\u00f8j ogs\u00e5 inputMode p\u00e5 selve input-elementet
OLD_INPUT_EL = (
    "                <input\n"
    "                  type={field.type || 'text'}\n"
    "                  placeholder={field.placeholder}\n"
    "                  value={form[field.key]}\n"
    "                  onChange={e => setForm(f => ({ ...f, [field.key]: e.target.value }))}\n"
    "                  style={{...inputStyle,\n"
    "                    borderColor: field.key === 'phone' && form.phone.length > 0 && !phoneOk\n"
    "                      ? '#E05252' : inputStyle.borderColor }}\n"
    "                />"
)
NEW_INPUT_EL = (
    "                <input\n"
    "                  type={field.type || 'text'}\n"
    "                  inputMode={field.key === 'phone' ? 'tel' : 'text'}\n"
    "                  placeholder={field.placeholder}\n"
    "                  value={form[field.key]}\n"
    "                  onChange={e => setForm(f => ({ ...f, [field.key]: e.target.value }))}\n"
    "                  style={{...inputStyle,\n"
    "                    borderColor: field.key === 'phone' && form.phone.length > 0 && !phoneOk\n"
    "                      ? '#E05252' : inputStyle.borderColor }}\n"
    "                />"
)
cnt = html.count(OLD_INPUT_EL)
html = html.replace(OLD_INPUT_EL, NEW_INPUT_EL, 1)
results.append(('inputMode=tel p\u00e5 input', cnt, 1))

# ── 2. Pak SROI + helbred ind i GDPR-sektion ─────────────────────────────
# Find start: f\u00f8r SROI-sektionen
SROI_START = '            {/* Sundhedsudfordring \u2014 intern klassifikation */}'
# Find end: f\u00f8r Kontekstnote
KONTEKST = '            {/* Kontekstnote */}'

idx_sroi = html.find(SROI_START)
idx_kontekst = html.find(KONTEKST, idx_sroi)

if idx_sroi != -1 and idx_kontekst != -1:
    inner_block = html[idx_sroi:idx_kontekst]

    GDPR_WRAPPER = (
        "            {/* GDPR-f\u00f8lsomme felter \u2014 Art. 9 */}\n"
        "            <div style={{\n"
        "              border: `1.5px solid ${SoS.orange}30`,\n"
        "              borderRadius: SoS.r.lg,\n"
        "              overflow: 'hidden',\n"
        "              marginBottom: 20,\n"
        "            }}>\n"
        "              {/* GDPR-header */}\n"
        "              <div style={{\n"
        "                background: `${SoS.orange}12`,\n"
        "                borderBottom: `1px solid ${SoS.orange}25`,\n"
        "                padding: '10px 14px',\n"
        "                display: 'flex', alignItems: 'center', gap: 8,\n"
        "              }}>\n"
        "                <Icon name=\"shield\" size={14} color={SoS.orange}/>\n"
        "                <div>\n"
        "                  <span style={{ fontFamily: SoS.sans, fontSize: 12,\n"
        "                    fontWeight: 700, color: SoS.orange }}>\n"
        "                    F\u00f8lsomme oplysninger \u2014 GDPR art.\u00a09\n"
        "                  </span>\n"
        "                  <span style={{ fontFamily: SoS.sans, fontSize: 11,\n"
        "                    color: SoS.inkSoft, marginLeft: 8 }}>\n"
        "                    Frivilligt \u00b7 kun til fagligt brug\n"
        "                  </span>\n"
        "                </div>\n"
        "              </div>\n"
        "              <div style={{ padding: '14px 14px 4px' }}>\n"
        + inner_block
        + "              </div>\n"
        "            </div>\n"
        "\n"
    )

    html = html[:idx_sroi] + GDPR_WRAPPER + html[idx_kontekst:]
    results.append(('GDPR-wrapper om SROI + helbred', 1, 1))
else:
    results.append(('GDPR-wrapper om SROI + helbred', 0, 1))

# ── Save ──────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before >= 1 else '[WARN]'
    print(f'{status} {label} (fundet: {before})')

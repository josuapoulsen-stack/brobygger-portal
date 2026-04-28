# -*- coding: utf-8 -*-
"""
patch_health_intake_ui.py
Erstatter den gamle enkelt-textarea health-sektion i IntakeFlow step 2
med det nye to-lags design:
  1. SROI-målgruppe (analytisk radio-gruppe)
  2. Faglig helbreds-sektion (kategorier + fritekst, admin-togglable)
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

START_ANCHOR = '{/* Udfordringer og diagnoser \u2014 f\u00f8lsomt felt */}'
END_AFTER    = '              />\n            </div>'
NEXT_AFTER   = '\n\n            {/* Kontekstnote'

start_idx = html.find(START_ANCHOR)
end_idx   = html.find(END_AFTER + NEXT_AFTER, start_idx)

if start_idx == -1 or end_idx == -1:
    print(f'[WARN] Anchors ikke fundet: start={start_idx} end={end_idx}')
else:
    remove_end = end_idx + len(END_AFTER)
    old_block = html[start_idx:remove_end]

    NEW_BLOCK = """{/* SROI-m\u00e5lgruppe \u2014 analytisk felt */}
            <div style={{
              background: SoS.creamDeep, borderRadius: SoS.r.md,
              padding: '12px 14px', marginBottom: 12,
            }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                color: SoS.ink, marginBottom: 6 }}>
                Matcher SROI-m\u00e5lgruppe?
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                marginBottom: 10, lineHeight: 1.4 }}>
                Bruges kun til aggregeret SROI-rapportering. Gemmes aldrig per borger i rapporter.
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(window.SROI_MAALGRUPPE_OPTIONS || []).map(opt => (
                  <label key={opt.id} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 12px', borderRadius: SoS.r.sm,
                    background: sroiMaalgruppe === opt.id ? SoS.orange + '15' : '#fff',
                    border: `1.5px solid ${sroiMaalgruppe === opt.id ? SoS.orange : SoS.lineSoft}`,
                    cursor: 'pointer',
                  }}>
                    <input
                      type="radio"
                      name="sroiMaalgruppe"
                      value={opt.id}
                      checked={sroiMaalgruppe === opt.id}
                      onChange={() => setSroiMaalgruppe(opt.id)}
                      style={{ accentColor: SoS.orange, width: 16, height: 16, flexShrink: 0 }}
                    />
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
                      {opt.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Faglig helbreds-sektion \u2014 kun hvis aktiveret i admin */}
            {(window.SoS_SETTINGS || {}).visHelbredsforhold !== false && (
              <div style={{
                background: '#FFF8F0', border: `1.5px solid ${SoS.orange}30`,
                borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 14,
              }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', marginBottom: 10 }}>
                  <Icon name="shield" size={14} color={SoS.orange} style={{ marginTop: 1 }}/>
                  <div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                      color: SoS.orange }}>
                      Relevante helbredsforhold \u2014 fagligt brug
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                      marginTop: 2, lineHeight: 1.4 }}>
                      Frivilligt. GDPR art.\u00a09. Bruges kun af brobygger til at st\u00f8tte relationen
                      \u2014 ikke til diagnosticering eller individuel SROI-beregning.
                    </div>
                  </div>
                </div>

                {/* Kategori-flervalg */}
                <div style={{ marginBottom: 10 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                    color: SoS.inkSoft, marginBottom: 6, letterSpacing: 0.4,
                    textTransform: 'uppercase' }}>Overordnet kategori</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {(window.HELBREDS_KATEGORIER || []).map(kat => {
                      const on = helbredsKategorier.includes(kat.id);
                      return (
                        <button key={kat.id}
                          onClick={() => setHelbredsKategorier(prev =>
                            on ? prev.filter(k => k !== kat.id) : [...prev, kat.id]
                          )}
                          style={{
                            padding: '5px 12px', borderRadius: 999,
                            border: `1.5px solid ${on ? SoS.orange : SoS.lineSoft}`,
                            background: on ? SoS.orange + '15' : '#fff',
                            fontFamily: SoS.sans, fontSize: 12,
                            color: on ? SoS.orangeDeep : SoS.ink,
                            fontWeight: on ? 600 : 400,
                            cursor: 'pointer',
                          }}>
                          {kat.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Fritekst */}
                <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                  color: SoS.inkSoft, marginBottom: 6, letterSpacing: 0.4,
                  textTransform: 'uppercase' }}>Faglige noter til brobygger</div>
                <textarea
                  placeholder="F.eks. let demens, angst, mobilitetsvanskeligheder, kronisk smerte..."
                  value={udfordringer}
                  onChange={e => setUdfordringer(e.target.value)}
                  rows={3}
                  style={{
                    width: '100%', padding: '10px 12px',
                    fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                    background: '#fff',
                    border: `1.5px solid ${SoS.orange}40`,
                    borderRadius: SoS.r.sm, outline: 'none', resize: 'none',
                    boxSizing: 'border-box', lineHeight: 1.5,
                  }}
                />
              </div>
            )}"""

    html = html[:start_idx] + NEW_BLOCK + html[remove_end:]
    print('[OK]  IntakeFlow: health UI erstattet')
    print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)

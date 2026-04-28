"""
patch_dead_ends_3.py
Fixes remaining dead ends (batch 3):
  1. CalendarScreen – "Rådighed" header button + "Meld rådig denne dag" wired to local sheet
  2. Shift "more" button – adds onClick with bottom-sheet options
  3. DesktopSROI – reads window.SROI_SETTINGS instead of hardcoded values
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# ---------------------------------------------------------------------------
# 1.  CalendarScreen: add state + wire buttons + add bottom sheets
# ---------------------------------------------------------------------------

# 1a. Add new state variables after `const [selected, setSelected]`
OLD = "  const [selected, setSelected] = React.useState('2026-04-27');\n\n  // Build calendar grid"
NEW = """  const [selected, setSelected] = React.useState('2026-04-27');
  const [addShiftSheet, setAddShiftSheet] = React.useState(false);
  const [addShiftDone, setAddShiftDone] = React.useState(false);
  const [moreShift, setMoreShift] = React.useState(null);

  // Build calendar grid"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('CalendarScreen: new state vars', cnt, html.count(NEW)))

# 1b. Wire header "Rådighed" button (onClick={onAddShift} -> local sheet)
OLD = "          <button onClick={onAddShift} style={{\n            height: 44, padding: '0 16px', borderRadius: 22,\n            background: SoS.orange, color: '#fff', border: 'none',\n            display: 'flex', alignItems: 'center', gap: 6,\n            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,\n            boxShadow: SoS.shadow.glow, cursor: 'pointer',\n          }}>"
NEW = "          <button onClick={() => setAddShiftSheet(true)} style={{\n            height: 44, padding: '0 16px', borderRadius: 22,\n            background: SoS.orange, color: '#fff', border: 'none',\n            display: 'flex', alignItems: 'center', gap: 6,\n            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,\n            boxShadow: SoS.shadow.glow, cursor: 'pointer',\n          }}>"

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('CalendarScreen: header Radighed button wired', cnt, html.count(NEW)))

# 1c. Wire "Meld rådig denne dag" button
OLD = '            <Button variant="secondary" onClick={onAddShift}\n              icon={<Icon name="plus" size={16} color={SoS.ink} weight={2.3} />}>\n              Meld rådig denne dag\n            </Button>'
NEW = '            <Button variant="secondary" onClick={() => setAddShiftSheet(true)}\n              icon={<Icon name="plus" size={16} color={SoS.ink} weight={2.3} />}>\n              Meld rådig denne dag\n            </Button>'

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('CalendarScreen: Meld raadig button wired', cnt, html.count(NEW)))

# 1d. Wire shift "more" button
OLD = '            <button style={{ background: \'none\', border: \'none\', cursor: \'pointer\', padding: 4 }}>\n              <Icon name="more" size={20} color={SoS.inkSoft} />\n            </button>\n          </div>\n        ))}\n      </div>\n    </>\n  );\n};\n\nwindow.CalendarScreen'
NEW = '''            <button onClick={() => setMoreShift(s)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
              <Icon name="more" size={20} color={SoS.inkSoft} />
            </button>
          </div>
        ))}
      </div>

      {/* Add-shift bottom sheet */}
      {addShiftSheet && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 400, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}
          onClick={() => { setAddShiftSheet(false); setAddShiftDone(false); }}>
          <div style={{ background: '#fff', borderRadius: '20px 20px 0 0', padding: '24px 20px 40px',
            boxShadow: '0 -4px 32px rgba(0,0,0,0.12)' }} onClick={e => e.stopPropagation()}>
            {addShiftDone ? (
              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div style={{ width: 56, height: 56, borderRadius: 28, background: SoS.sage,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                  <Icon name="check" size={28} color="#fff" weight={2.5} />
                </div>
                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 8 }}>
                  Rådighed meldt!
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, marginBottom: 24 }}>
                  Koordinatoren kan nu matche dig med en borger {selected ? 'd. ' + selected.split('-').reverse().join('/') : 'denne dag'}.
                </div>
                <Button full onClick={() => { setAddShiftSheet(false); setAddShiftDone(false); }}>Luk</Button>
              </div>
            ) : (
              <>
                <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 6 }}>
                  Meld rådighed
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, marginBottom: 20 }}>
                  {selected ? formatDate(selected, { long: true }) : 'Valgt dag'}
                </div>
                <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
                  {[['08:00','12:00','Formiddag'],['12:00','16:00','Eftermiddag'],['16:00','20:00','Aften']].map(([start, end, label]) => (
                    <div key={label} style={{ flex: 1, border: `2px solid ${SoS.line}`, borderRadius: SoS.r.md,
                      padding: '12px 8px', textAlign: 'center', cursor: 'pointer',
                      fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}
                      onClick={() => setAddShiftDone(true)}>
                      <div style={{ fontWeight: 600, marginBottom: 2 }}>{label}</div>
                      <div style={{ fontSize: 11, color: SoS.inkSoft }}>{start}–{end}</div>
                    </div>
                  ))}
                </div>
                <Button full onClick={() => setAddShiftDone(true)}>Bekræft rådighed</Button>
                <button onClick={() => setAddShiftSheet(false)} style={{ width: '100%', marginTop: 10,
                  background: 'none', border: 'none', fontFamily: SoS.sans, fontSize: 14,
                  color: SoS.inkSoft, cursor: 'pointer', padding: 10 }}>
                  Annuller
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Shift "more" bottom sheet */}
      {moreShift && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 400, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}
          onClick={() => setMoreShift(null)}>
          <div style={{ background: '#fff', borderRadius: '20px 20px 0 0', padding: '24px 20px 40px',
            boxShadow: '0 -4px 32px rgba(0,0,0,0.12)' }} onClick={e => e.stopPropagation()}>
            <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink, marginBottom: 4 }}>
              Rådighed kl. {moreShift.start}–{moreShift.end}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>
              Afventer match fra koordinator
            </div>
            <button style={{ width: '100%', padding: '14px 0', background: SoS.creamDeep,
              border: 'none', borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 15,
              fontWeight: 600, color: SoS.red || '#D64545', cursor: 'pointer', marginBottom: 10 }}
              onClick={() => setMoreShift(null)}>
              Fjern rådighed
            </button>
            <button style={{ width: '100%', padding: '14px 0', background: 'none',
              border: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
              cursor: 'pointer' }}
              onClick={() => setMoreShift(null)}>
              Luk
            </button>
          </div>
        </div>
      )}
    </>
  );
};

window.CalendarScreen'''

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('CalendarScreen: more button + bottom sheets', cnt, html.count('window.CalendarScreen')))

# ---------------------------------------------------------------------------
# 2.  DesktopSROI – read from window.SROI_SETTINGS
# ---------------------------------------------------------------------------
OLD = """const DesktopSROI = () => {
  const sroi = 521 * 1840 + 702 * 1420 + 911 * 1260;
  const investment = 8_400_000;"""
NEW = """const DesktopSROI = () => {
  const rates = window.SROI_SETTINGS || { sundhed: 1840, forening: 1420, social: 1260, investment: 8400000 };
  const sroi = 521 * rates.sundhed + 702 * rates.forening + 911 * rates.social;
  const investment = rates.investment;"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('DesktopSROI: reads window.SROI_SETTINGS', cnt, html.count(NEW)))

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] File saved ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]' if before == 1 and after == 1 else f'[WARN] before={before} after={after}'
    print(f'{status}  {label}')

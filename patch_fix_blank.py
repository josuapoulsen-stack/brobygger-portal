"""
patch_fix_blank.py — Fix blank page after kalender patches.

Root causes fixed:
  1. IIFE {(() => { const downloadICS = ...; return (...); })()} in JSX
     → moved downloadICS to component body, plain <div> in JSX
  2. ...(isAdmin ? [{...}] : []) spread in sidebar array
     → replaced with .concat() which Babel handles flawlessly
  3. Added on-page error display (no F12 needed if something else breaks)
"""

import sys, re

IN  = 'Brobygger portal.html'
OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

original = html

# ─── FIX 1: Add on-page error display right after <div id="root"></div> ──────
OLD_ROOT = '<div id="root"></div>'
NEW_ROOT = '''<div id="root"></div>
<div id="sos-err" style="display:none;position:fixed;top:0;left:0;right:0;z-index:99999;
  background:#c0392b;color:#fff;padding:14px 18px;font:13px/1.5 monospace;
  white-space:pre-wrap;word-break:break-all;"></div>
<script>
window.onerror = function(msg, src, line, col, err) {
  var d = document.getElementById('sos-err');
  if (d) { d.style.display = 'block';
    d.textContent = 'JS ERROR: ' + msg + '\\n  at ' + src + ':' + line + ':' + col; }
};
</script>'''

if OLD_ROOT not in html:
    sys.exit('ERROR: could not find <div id="root"> anchor')

html = html.replace(OLD_ROOT, NEW_ROOT, 1)
print('[OK] Added on-page error display')

# ─── FIX 2: Move downloadICS out of IIFE, into AppointmentDetailScreen body ──

# Step A: add downloadICS function after "const type = SS_TYPER[menneske.type];"
OLD_TYPE_LINE = '  const type = SS_TYPER[menneske.type];\n\n  return ('

NEW_WITH_FN = (
    '  const type = SS_TYPER[menneske.type];\n\n'
    '  const downloadICS = () => {\n'
    '    const dt = appt.date.replace(/-/g, \'\');\n'
    '    const ts = appt.start.replace(\':\', \'\') + \'00\';\n'
    '    const te = appt.end.replace(\':\', \'\') + \'00\';\n'
    '    const lines = [\n'
    '      \'BEGIN:VCALENDAR\',\n'
    '      \'VERSION:2.0\',\n'
    '      \'PRODID:-//SoS Brobygger Portal//DA\',\n'
    '      \'BEGIN:VEVENT\',\n'
    '      \'DTSTART:\' + dt + \'T\' + ts,\n'
    '      \'DTEND:\' + dt + \'T\' + te,\n'
    '      \'SUMMARY:Brobygning \\u2013 \' + (menneske ? menneske.firstName : \'\') + \' (\' + appt.activity + \')\',\n'
    '      \'DESCRIPTION:\' + appt.activity,\n'
    '      \'LOCATION:\' + appt.location,\n'
    '      \'STATUS:\' + (appt.status === \'confirmed\' ? \'CONFIRMED\' : \'TENTATIVE\'),\n'
    '      \'END:VEVENT\',\n'
    '      \'END:VCALENDAR\',\n'
    '    ];\n'
    '    const blob = new Blob([lines.join(\'\\r\\n\')], { type: \'text/calendar;charset=utf-8\' });\n'
    '    const url = URL.createObjectURL(blob);\n'
    '    const a = document.createElement(\'a\');\n'
    '    a.href = url; a.download = \'brobygning-\' + appt.date + \'.ics\'; a.click();\n'
    '    URL.revokeObjectURL(url);\n'
    '  };\n\n'
    '  return ('
)

# Only match inside AppointmentDetailScreen block (it's the only component
# that has both "const menneske = SS_MENNESKER[appt.menneskeId]" and
# "const type = SS_TYPER[menneske.type]" directly in body)
if OLD_TYPE_LINE not in html:
    sys.exit('ERROR: could not find type-line anchor in AppointmentDetailScreen')

# Guard: make sure there's exactly one occurrence
count_type = html.count(OLD_TYPE_LINE)
if count_type != 1:
    sys.exit(f'ERROR: type-line anchor appears {count_type}x (expected 1)')

html = html.replace(OLD_TYPE_LINE, NEW_WITH_FN, 1)
print('[OK] Added downloadICS to AppointmentDetailScreen body')

# Step B: Replace the IIFE block in JSX with plain <div>
OLD_IIFE = (
    '      {/* Kalender-download */}\n'
    '      {(() => {\n'
    '        const downloadICS = () => {\n'
    '          const dt = appt.date.replace(/-/g, \'\');\n'
    '          const ts = appt.start.replace(\':\', \'\') + \'00\';\n'
    '          const te = appt.end.replace(\':\', \'\') + \'00\';\n'
    '          const lines = [\n'
    '            \'BEGIN:VCALENDAR\',\n'
    '            \'VERSION:2.0\',\n'
    '            \'PRODID:-//SoS Brobygger Portal//DA\',\n'
    '            \'BEGIN:VEVENT\',\n'
    '            \'DTSTART:\' + dt + \'T\' + ts,\n'
    '            \'DTEND:\' + dt + \'T\' + te,\n'
    '            \'SUMMARY:Brobygning \\u2013 \' + (menneske ? menneske.firstName : \'\') + \' (\' + appt.activity + \')\',\n'
    '            \'DESCRIPTION:\' + appt.activity,\n'
    '            \'LOCATION:\' + appt.location,\n'
    '            \'STATUS:\' + (appt.status === \'confirmed\' ? \'CONFIRMED\' : \'TENTATIVE\'),\n'
    '            \'END:VEVENT\',\n'
    '            \'END:VCALENDAR\',\n'
    '          ];\n'
    '          const blob = new Blob([lines.join(\'\\r\\n\')],\n'
    '            { type: \'text/calendar;charset=utf-8\' });\n'
    '          const url = URL.createObjectURL(blob);\n'
    '          const a = document.createElement(\'a\');\n'
    '          a.href = url; a.download = \'brobygning-\' + appt.date + \'.ics\'; a.click();\n'
    '          URL.revokeObjectURL(url);\n'
    '        };\n'
    '        return (\n'
    '          <div style={{ padding: \'0 20px 4px\' }}>\n'
    '            <button onClick={downloadICS} style={{\n'
    '              width: \'100%\', padding: \'13px 0\',\n'
    '              background: \'#fff\', border: `1px solid ${SS.line}`,\n'
    '              borderRadius: SS.r.md, cursor: \'pointer\',\n'
    '              display: \'flex\', alignItems: \'center\', justifyContent: \'center\', gap: 8,\n'
    '              fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink,\n'
    '            }}>\n'
    '              <Icon name="calendar" size={16} color={SS.sky} weight={2}/>\n'
    '              Gem i kalender (.ics)\n'
    '            </button>\n'
    '            <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted,\n'
    '              textAlign: \'center\', marginTop: 6 }}>\n'
    '              \u00c5bner i Outlook, Apple Kalender og Google Kalender\n'
    '            </div>\n'
    '          </div>\n'
    '        );\n'
    '      })()}'
)

NEW_DIV = (
    '      {/* Kalender-download */}\n'
    '      <div style={{ padding: \'0 20px 4px\' }}>\n'
    '        <button onClick={downloadICS} style={{\n'
    '          width: \'100%\', padding: \'13px 0\',\n'
    '          background: \'#fff\', border: `1px solid ${SS.line}`,\n'
    '          borderRadius: SS.r.md, cursor: \'pointer\',\n'
    '          display: \'flex\', alignItems: \'center\', justifyContent: \'center\', gap: 8,\n'
    '          fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink,\n'
    '        }}>\n'
    '          <Icon name="calendar" size={16} color={SS.sky} weight={2}/>\n'
    '          Gem i kalender (.ics)\n'
    '        </button>\n'
    '        <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted,\n'
    '          textAlign: \'center\', marginTop: 6 }}>\n'
    '          \u00c5bner i Outlook, Apple Kalender og Google Kalender\n'
    '        </div>\n'
    '      </div>'
)

if OLD_IIFE not in html:
    # Try to find just the start to give useful diagnostic
    probe = '      {(() => {\n        const downloadICS = () => {'
    if probe in html:
        sys.exit('ERROR: IIFE start found but full string did not match — whitespace mismatch')
    else:
        sys.exit('ERROR: could not find IIFE block at all')

html = html.replace(OLD_IIFE, NEW_DIV, 1)
print('[OK] Replaced IIFE in JSX with plain <div>')

# ─── FIX 3: Replace sidebar spread with .concat() ────────────────────────────
OLD_SPREAD = (
    '              ...(isAdmin ? [{ k: \'rapport\', l: \'Rapport & eksport\', i: \'note\' }] : []),\n'
    '            ].map(n => ('
)
NEW_CONCAT = (
    '            ].concat(isAdmin ? [{ k: \'rapport\', l: \'Rapport & eksport\', i: \'note\' }] : []).map(n => ('
)

if OLD_SPREAD not in html:
    sys.exit('ERROR: could not find sidebar spread')

html = html.replace(OLD_SPREAD, NEW_CONCAT, 1)
print('[OK] Replaced sidebar spread with .concat()')

# ─── Write ────────────────────────────────────────────────────────────────────
if html == original:
    sys.exit('ERROR: no changes made — all replacements failed')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

size = len(html.encode('utf-8'))
print(f'\n✓ Saved {OUT} ({size:,} bytes)')
print('Done — open the HTML in browser to test.')

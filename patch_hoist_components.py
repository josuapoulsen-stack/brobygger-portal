"""
patch_hoist_components.py
Moves NumStepper and Field out of AdminSettings body → block-level scope.
Defining React components inside another component body is an antipattern
that trips Babel Standalone and causes React to remount them every render.
"""
import sys, textwrap

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

# ── The two inner component blocks (indented 2 spaces inside AdminSettings) ──

INNER_BOTH = (
    '\n'
    '  const NumStepper = ({ label, sublabel, unit, value, min, max, onChange }) => (\n'
    '    <div style={{ display: \'flex\', alignItems: \'center\', gap: 12,\n'
    '      padding: \'13px 0\', borderBottom: `1px solid ${SS.lineSoft}` }}>\n'
    '      <div style={{ flex: 1 }}>\n'
    '        <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 500, color: SS.ink }}>{label}</div>\n'
    '        {sublabel && <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted, marginTop: 2 }}>{sublabel}</div>}\n'
    '      </div>\n'
    '      <div style={{ display: \'flex\', alignItems: \'center\', gap: 8 }}>\n'
    '        <button onClick={() => onChange(Math.max(min, value - 1))} style={{\n'
    '          width: 30, height: 30, borderRadius: 15, border: `1.5px solid ${SS.lineSoft}`,\n'
    '          background: \'#fff\', cursor: \'pointer\', fontSize: 18, color: SS.ink,\n'
    '          display: \'flex\', alignItems: \'center\', justifyContent: \'center\',\n'
    '        }}>\u2212</button>\n'
    '        <div style={{ textAlign: \'center\', minWidth: 38 }}>\n'
    '          <div style={{ fontFamily: SS.font, fontSize: 20, fontWeight: 500, color: SS.orange }}>{value}</div>\n'
    '          {unit && <div style={{ fontFamily: SS.sans, fontSize: 9, color: SS.inkMuted }}>{unit}</div>}\n'
    '        </div>\n'
    '        <button onClick={() => onChange(Math.min(max, value + 1))} style={{\n'
    '          width: 30, height: 30, borderRadius: 15, border: `1.5px solid ${SS.lineSoft}`,\n'
    '          background: \'#fff\', cursor: \'pointer\', fontSize: 18, color: SS.ink,\n'
    '          display: \'flex\', alignItems: \'center\', justifyContent: \'center\',\n'
    '        }}>+</button>\n'
    '      </div>\n'
    '    </div>\n'
    '  );\n'
    '\n'
    '  const Field = ({ label, placeholder, value, onChange, required }) => (\n'
    '    <div style={{ marginBottom: 12 }}>\n'
    '      <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,\n'
    '        color: SS.inkSoft, marginBottom: 5 }}>\n'
    '        {label}{required && <span style={{ color: SS.orange }}> *</span>}\n'
    '      </div>\n'
    '      <input placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)}\n'
    '        style={{ width: \'100%\', padding: \'11px 13px\', fontFamily: SS.sans,\n'
    '          fontSize: 14, color: SS.ink, background: \'#fff\',\n'
    '          border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,\n'
    '          outline: \'none\', boxSizing: \'border-box\' }} />\n'
    '    </div>\n'
    '  );\n'
)

if INNER_BOTH not in html:
    sys.exit('ERROR: could not find inner NumStepper+Field block — whitespace mismatch?')

# Dedented (block-level) versions — remove the leading 2 spaces from every line
def dedent2(s):
    lines = s.split('\n')
    result = []
    for l in lines:
        if l.startswith('  '):
            result.append(l[2:])
        else:
            result.append(l)
    return '\n'.join(result)

BLOCK_LEVEL = dedent2(INNER_BOTH)

# Anchor: insert block-level components just before AdminSettings definition
BEFORE_ADMIN = '// Settings — temporary HQ switch\nconst AdminSettings'
if BEFORE_ADMIN not in html:
    sys.exit('ERROR: could not find AdminSettings anchor')

html = html.replace(
    BEFORE_ADMIN,
    '// Helper components for AdminSettings\n' + BLOCK_LEVEL.strip() + '\n\n// Settings — temporary HQ switch\nconst AdminSettings',
    1
)

# Remove the inner versions from AdminSettings body
html = html.replace(INNER_BOTH, '\n', 1)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Hoisted NumStepper and Field to block scope')
print(f'[OK] File saved ({len(html.encode("utf-8")):,} bytes)')

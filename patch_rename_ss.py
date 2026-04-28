"""
patch_rename_ss.py
Renames every SS_ prefix in the codebase to SoS_ so the abbreviation
"SS" no longer appears anywhere in JavaScript.
Design-token object (window.SoS) is already correct and untouched.
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

before = html.count('SS_')
html = html.replace('SS_', 'SoS_')
after  = html.count('SS_')

# Sanity: no SS_ left
assert after == 0, f'Still {after} SS_ occurrences after replace!'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Renamed {before} SS_ -> SoS_ occurrences')
print(f'[OK] File saved ({len(html.encode("utf-8")):,} bytes)')
print()
print('Convention going forward:')
print('  SoS          -> design tokens object (window.SoS)')
print('  SoS_NAVNX    -> mock / shared data arrays (window.SoS_NAVNX)')
print('  No SS prefix anywhere.')

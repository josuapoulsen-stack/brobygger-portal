# -*- coding: utf-8 -*-
"""
patch_fix_map_fragment.py
Fixes JSX syntax error in MatchingFlow menneske-list:
.map() callback returned <button> + 2 conditional siblings without a fragment wrapper.
Fix: wrap in <React.Fragment key={b.id}>...</React.Fragment>
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

# The .map callback currently does:
#   return (
#     <button key={b.id} ...>...</button>
#     {b.brobygning && (...)}
#     {b.previousBrobygger && (...)}
#   );
#
# Fix: wrap in React.Fragment with the key, remove key from button

OLD = 'return (\n                <button key={b.id} onClick={() => setMenneskeId(b.id)} style={{'
NEW = 'return (\n                <React.Fragment key={b.id}>\n                <button onClick={() => setMenneskeId(b.id)} style={{'

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('map fragment: open tag', cnt, 1))

# Close the fragment just before );  after the previousBrobygger block
# The closing sequence is:  )}\n              );\n
OLD_CLOSE = ')}\n              );\n'
NEW_CLOSE = ')}\n              </React.Fragment>\n              );\n'

# There can be multiple )}\n              );\n — we want the one right after previousBrobygger
# Find it by searching from the previousBrobygger position
prev_idx = html.find('{b.previousBrobygger && (')
close_idx = html.find(OLD_CLOSE, prev_idx)
if close_idx != -1:
    html = html[:close_idx] + NEW_CLOSE + html[close_idx + len(OLD_CLOSE):]
    results.append(('map fragment: close tag', 1, 1))
else:
    results.append(('map fragment: close tag', 0, 0))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 else f'[WARN] before={before}'
    print(f'{status} {label}')

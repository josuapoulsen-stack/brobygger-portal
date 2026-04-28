import sys, re

path = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# Ordered from most specific to least specific to avoid partial-match collisions
replacements = [
    # Data constant + window export
    ('SS_BORGERE',          'SS_MENNESKER'),
    # Component names
    ('AdminBorgereScreen',  'AdminMenneskerScreen'),
    ('DesktopBorgere',      'DesktopMennesker'),
    # Callback prop
    ('onOpenBorger',        'onOpenMenneske'),
    # State setter before variable (both contain 'borgerId')
    ('setBorgerId',         'setMenneskeId'),
    # State variable + data property key
    ('borgerId',            'menneskeId'),
    # Stats data key
    ('activeBorgere',       'aktiveMennesker'),
]

total = 0
for old, new in replacements:
    count = html.count(old)
    html = html.replace(old, new)
    total += count
    sys.stdout.buffer.write(f"  {old:<30s} -> {new:<25s}  ({count}x)\n".encode('utf-8'))

# Sanity check: no 'borger' should remain (case-insensitive) except inside 'brobygger'
# We strip 'brobygger' occurrences before checking
check = re.sub(r'[Bb]ro[Bb]ygger', '', html)
remaining = re.findall(r'(?i)[Bb]orger', check)
if remaining:
    sys.stdout.buffer.write(f"\nWARNING: {len(remaining)} remaining 'borger' occurrences:\n".encode('utf-8'))
    # Show context for each
    for m in re.finditer(r'(?i)[Bb]orger', check):
        snippet = check[max(0,m.start()-40):m.end()+40].replace('\n',' ')
        sys.stdout.buffer.write(f"  ...{snippet}...\n".encode('utf-8'))
else:
    sys.stdout.buffer.write(b"\nSanity check PASSED: no 'borger' remains outside 'brobygger'\n")

sys.stdout.buffer.write(f"\nTotal replacements: {total}\nFile: {original_len:,} -> {len(html):,} bytes\n".encode('utf-8'))

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
sys.stdout.buffer.write(b"Saved.\n")

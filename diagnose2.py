import re, sys

with open('Brobygger portal.html', encoding='utf-8') as f:
    html = f.read()

blocks = re.findall(r'<script type="text/babel">(.*?)</script>', html, re.DOTALL)

# Check each block for the spread-in-array pattern (known Babel standalone issue)
for i, b in enumerate(blocks):
    if '...(isAdmin' in b or '...(' in b:
        lines = b.split('\n')
        for j, l in enumerate(lines):
            if '...(' in l:
                sys.stdout.buffer.write(
                    f'  Block {i+1}, line ~{j+1}: {l.strip()}\n'.encode('utf-8')
                )

# Check for any </script> accidentally inside a block
for i, b in enumerate(blocks):
    if '</script' in b.lower():
        sys.stdout.buffer.write(f'  Block {i+1}: contains </script> tag!\n'.encode('utf-8'))

# Find what changed in blocks around the kalender patches (DesktopView block)
# Look for block containing DesktopView
for i, b in enumerate(blocks):
    if 'DesktopView' in b and 'const DesktopView' in b:
        sys.stdout.buffer.write(f'  DesktopView is in block {i+1}\n'.encode('utf-8'))
        ob = b.count('{')
        cb = b.count('}')
        sys.stdout.buffer.write(f'  Braces: {ob} open, {cb} close\n'.encode('utf-8'))

sys.stdout.buffer.write(b'Done\n')

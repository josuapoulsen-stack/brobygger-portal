import re

with open('Brobygger portal.html', encoding='utf-8') as f:
    html = f.read()

opens  = html.count('<script type="text/babel">')
closes_tag = len(re.findall(r'</script>', html))
print(f'script opens={opens}  closes={closes_tag}')

blocks = re.findall(r'<script type="text/babel">(.*?)</script>', html, re.DOTALL)
print(f'Parseable blocks: {len(blocks)}')

for i, b in enumerate(blocks):
    issues = []
    ticks = b.count('`')
    if ticks:
        issues.append(f'{ticks} backticks')
    if '...(is' in b:
        issues.append('spread-in-JSX')
    ob = b.count('{')
    cb = b.count('}')
    if abs(ob - cb) > 4:
        issues.append(f'brace mismatch ({ob} vs {cb})')
    op = b.count('(')
    cp = b.count(')')
    if abs(op - cp) > 4:
        issues.append(f'paren mismatch ({op} vs {cp})')
    if issues:
        # Show first line with content
        first = next((l.strip() for l in b.split('\n') if l.strip()), '')
        print(f'  Block {i+1:02d} [{first[:60]}]: {", ".join(issues)}')

print('Done.')

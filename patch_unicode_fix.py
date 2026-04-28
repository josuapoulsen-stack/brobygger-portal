# -*- coding: utf-8 -*-
"""
patch_unicode_fix.py
Erstatter bogstav-escaped Unicode-sekvenser i HTML-filen med rigtige UTF-8 tegn,
så JSX-tekstnoder (og kommentarer) vises korrekt.
JavaScript string-literals fungerer med begge former, men JSX text nodes kræver UTF-8.
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

REPLACEMENTS = [
    # Småt bogstaver
    (r'\u00f8', 'ø'),
    (r'\u00e6', 'æ'),
    (r'\u00e5', 'å'),
    (r'\u00f6', 'ö'),
    # Store bogstaver
    (r'\u00d8', 'Ø'),
    (r'\u00c6', 'Æ'),
    (r'\u00c5', 'Å'),
    # Tegnsætning
    (r'\u2014', '—'),
    (r'\u2013', '–'),
    (r'\u00b7', '·'),
    (r'\u00e9', 'é'),
    (r'\u00e8', 'è'),
    (r'\u00ea', 'ê'),
    (r'\u00eb', 'ë'),
]

total = 0
for esc, char in REPLACEMENTS:
    count = html.count(esc)
    if count:
        html = html.replace(esc, char)
        total += count
        print(f'[OK] {esc} -> {char!r}  ({count} steder)')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print()
print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes) — {total} escape-sekvenser erstattet med UTF-8')

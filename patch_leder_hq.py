import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label, count=1):
    global c
    n = c.count(old)
    if n:
        c = c.replace(old, new, count); ok.append(label + (f' (x{min(n,count)})' if count>1 else ''))
    else:
        fail.append(label)

# 1) Default viewingHq: org-bredt kun for admin (daglig leder → eget hq)
sub(
    "  const [viewingHq, setViewingHq] = React.useState(canRapport ? 'Alle hovedsæder' : ownHq);",
    "  const [viewingHq, setViewingHq] = React.useState(canUserMgmt ? 'Alle hovedsæder' : ownHq);",
    "1: default viewingHq")

# 2) 'Alle hovedsæder'-option kun for admin
sub(
    "                {canRapport && <option value=\"Alle hovedsæder\">Alle hovedsæder</option>}",
    "                {canUserMgmt && <option value=\"Alle hovedsæder\">Alle hovedsæder</option>}",
    "2: alle-hovedsæder-option")

# 3) Relabel leder → Daglig leder (begge tweak-paneler)
sub(
    "{ value: \"leder\",     label: \"Leder / Landssekretariat\" },",
    "{ value: \"leder\",     label: \"Daglig leder (eget hq)\" },",
    "3: relabel leder", count=2)

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

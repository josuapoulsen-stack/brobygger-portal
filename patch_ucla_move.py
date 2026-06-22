import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

start_marker = "// ── UCLA-3 (ensomhedsmåling)"
end_marker   = "// ── SoS_DEMO — URL-parameter persona"
anchor       = "window.SoS_MENNESKER     = SoS_MENNESKER;\n"

if start_marker not in c or end_marker not in c or anchor not in c:
    print("FAIL: markør mangler"); sys.exit(1)

s = c.index(start_marker)
e = c.index(end_marker)
block = c[s:e]               # UCLA-blokken inkl. afsluttende blanklinjer
# Fjern fra plain-scriptet
c = c[:s] + c[e:]
# Indsæt i babel-blokken lige efter SoS_MENNESKER-defineringen
i = c.index(anchor) + len(anchor)
c = c[:i] + "\n" + block + c[i:]

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

# sanity: blokken skal nu stå før babel-blokkens slut (</script> ~670-området), ikke i plain-scriptet
print("OK: UCLA-blok flyttet ind i babel-blokken efter SoS_MENNESKER")
print("Babel-pos (skal være lav linje):", c[:c.index(start_marker)].count("\n") + 1)

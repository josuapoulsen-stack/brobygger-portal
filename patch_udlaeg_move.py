import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

start_marker = "      {/* Acubiz-genvej — diskret øverste bilagsapp */}"
end_marker   = "      <UdlaegKort brobyggerId={brobyggerId} user={user} />"
ins_marker   = "    <>\n      {/* Rådighedsplan notifikation */}"

if start_marker not in c or end_marker not in c or ins_marker not in c:
    print("FAIL: markør mangler",
          start_marker in c, end_marker in c, ins_marker in c); sys.exit(1)

s = c.index(start_marker)
e = c.index(end_marker) + len(end_marker)
block = c[s:e]                       # Acubiz-IIFE + UdlaegKort
# Fjern fra nuværende placering
c = c[:s] + c[e:]

# Indsæt øverst under en "Udlæg"-overskrift
section = ("    <>\n"
          "      {/* Udlæg — øverst og tydeligt så det ikke drukner blandt aftaler */}\n"
          "      <div style={{ padding: '16px 20px 0' }}>\n"
          "        <SectionHead title=\"Udlæg\" />\n"
          "      </div>\n"
          + block + "\n\n"
          "      {/* Rådighedsplan notifikation */}")
c = c.replace(ins_marker, section, 1)

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print("OK: Udlæg-sektion flyttet øverst med overskrift")

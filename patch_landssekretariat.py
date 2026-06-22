import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# 1) ROLLE_LABELS
sub("    leder: 'Leder', admin: 'Admin',",
    "    leder: 'Leder', landssekretariat: 'Landssekretariat', admin: 'Admin',",
    "1: ROLLE_LABELS")

# 2) ROLLE_COLORS
sub("    brobygger: SoS.sage, raadgiver: SoS.sky, leder: SoS.orange, admin: '#C62828',",
    "    brobygger: SoS.sage, raadgiver: SoS.sky, leder: SoS.orange, landssekretariat: '#6D4FC2', admin: '#C62828',",
    "2: ROLLE_COLORS")

# 3) DesktopView signatur — tilføj canAllHq
sub("const DesktopView = ({ user, ownHq, ownAfdeling, isAdmin, canRapport = false, canUserMgmt = false, onClose }) => {",
    "const DesktopView = ({ user, ownHq, ownAfdeling, isAdmin, canRapport = false, canAllHq = false, canUserMgmt = false, onClose }) => {",
    "3: DesktopView signatur")

# 4) viewingHq default — org-bredt for canAllHq
sub("  const [viewingHq, setViewingHq] = React.useState(canUserMgmt ? 'Alle hovedsæder' : ownHq);",
    "  const [viewingHq, setViewingHq] = React.useState(canAllHq ? 'Alle hovedsæder' : ownHq);",
    "4: viewingHq default")

# 5) Sidebar-label
sub("                  {canUserMgmt ? 'ADMINISTRATION' : canRapport ? 'LEDELSE' : 'RÅDGIVER-PORTAL'}",
    "                  {canUserMgmt ? 'ADMINISTRATION' : canAllHq ? 'LANDSSEKRETARIAT' : canRapport ? 'LEDELSE' : 'RÅDGIVER-PORTAL'}",
    "5: sidebar-label")

# 6) 'Alle hovedsæder'-option — gate på canAllHq
sub('                {canUserMgmt && <option value="Alle hovedsæder">Alle hovedsæder</option>}',
    '                {canAllHq && <option value="Alle hovedsæder">Alle hovedsæder</option>}',
    "6: alle-hovedsæder-option")

# 7) Render-branch (mobil)
sub('  } else if (activeRole === "admin" || activeRole === "raadgiver" || activeRole === "leder") {',
    '  } else if (activeRole === "admin" || activeRole === "raadgiver" || activeRole === "leder" || activeRole === "landssekretariat") {',
    "7: render-branch")

# 8) _canRapport
sub('    const _canRapport = activeRole === "admin" || activeRole === "leder";',
    '    const _canRapport = activeRole === "admin" || activeRole === "leder" || activeRole === "landssekretariat";',
    "8: _canRapport")

# 9) desktopMode-guard
sub('  if (desktopMode && (tweaks.role === "admin" || tweaks.role === "raadgiver" || tweaks.role === "leder")) {',
    '  if (desktopMode && (tweaks.role === "admin" || tweaks.role === "raadgiver" || tweaks.role === "leder" || tweaks.role === "landssekretariat")) {',
    "9: desktopMode-guard")

# 10) DesktopView-kald — canRapport + canAllHq
sub('isAdmin={tweaks.role === "admin"} canRapport={tweaks.role === "leder" || tweaks.role === "admin"} canUserMgmt={tweaks.role === "admin"} onClose={() => setDesktopMode(false)} />',
    'isAdmin={tweaks.role === "admin"} canRapport={tweaks.role === "leder" || tweaks.role === "landssekretariat" || tweaks.role === "admin"} canAllHq={tweaks.role === "landssekretariat" || tweaks.role === "admin"} canUserMgmt={tweaks.role === "admin"} onClose={() => setDesktopMode(false)} />',
    "10: DesktopView-kald")

# 11) TweaksPanel (desktop)
sub('                { value: "leder",     label: "Daglig leder (eget hq)" },\n                { value: "admin",     label: "Admin" },',
    '                { value: "leder",     label: "Daglig leder (eget hq)" },\n                { value: "landssekretariat", label: "Landssekretariat (alle hq)" },\n                { value: "admin",     label: "Admin" },',
    "11: tweaks desktop")

# 12) TweaksPanel (mobil)
sub('              { value: "leder",     label: "Daglig leder (eget hq)" },\n              { value: "admin",     label: "Admin (alle hq)" },',
    '              { value: "leder",     label: "Daglig leder (eget hq)" },\n              { value: "landssekretariat", label: "Landssekretariat (alle hq)" },\n              { value: "admin",     label: "Admin (alle hq)" },',
    "12: tweaks mobil")

# 13) Default navn/avatar
sub("""  const _defaultNavn = activeRole === 'raadgiver' ? 'Linda Thomsen'
                      : activeRole === 'admin'    ? 'Admin Bruger'
                      : isNew ? 'Sofie Lindahl' : 'Maja Holmberg';
  const _defaultAvatar = activeRole === 'raadgiver' ? 'LT'
                        : activeRole === 'admin'    ? 'AB'
                        : isNew ? 'SL' : 'MH';""",
"""  const _defaultNavn = activeRole === 'raadgiver' ? 'Linda Thomsen'
                      : activeRole === 'admin'    ? 'Admin Bruger'
                      : activeRole === 'landssekretariat' ? 'Henrik Dahl'
                      : isNew ? 'Sofie Lindahl' : 'Maja Holmberg';
  const _defaultAvatar = activeRole === 'raadgiver' ? 'LT'
                        : activeRole === 'admin'    ? 'AB'
                        : activeRole === 'landssekretariat' ? 'HD'
                        : isNew ? 'SL' : 'MH';""",
"13: default navn/avatar")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

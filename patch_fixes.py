path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

fixes = 0

# ── 1. Fix 2 missing </div> at end of AdminSettings return ───────────────────
# The block ends:  </>)}\n        </>)}\n      </div>\n    </div>\n  );\n};
# We need 2 more closing divs before the last two
old_end = (
    "          </>)}\n"
    "        </>)}\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "};"
)
new_end = (
    "          </>)}\n"
    "        </>)}\n"
    "      </div>\n"          # closes invite-bb wrapper div (if any)
    "      </div>\n"          # closes body <div style={{flex:1, overflowY:'auto'}}>
    "    </div>\n"            # closes outer container
    "  );\n"
    "};"
)

# Verify the old pattern is unique in AdminSettings block
idx_admin = html.find('const AdminSettings = ({ currentHq')
chunk = html[idx_admin:]
if old_end in chunk[:30000]:
    # Replace only within the AdminSettings block
    html = html[:idx_admin] + chunk[:30000].replace(old_end, new_end, 1) + chunk[30000:]
    fixes += 1
    print("Fixed: 2 missing </div> in AdminSettings")
else:
    print("ERROR: AdminSettings end pattern not found")
    # Debug: show last lines
    end_idx = html.find('window.AdminMobile = AdminMobile;', idx_admin)
    print(repr(html[end_idx-200:end_idx]))

# ── 2. Export IntakeFlow to window (block 23 is after app.jsx — needs export) ─
old_intake_end = (
    "  );\n"
    "};\n"
    "</script>\n"
    "</body>"
)
new_intake_end = (
    "  );\n"
    "};\n"
    "\n"
    "window.IntakeFlow = IntakeFlow;\n"
    "</script>\n"
    "</body>"
)

if old_intake_end in html:
    html = html.replace(old_intake_end, new_intake_end, 1)
    fixes += 1
    print("Fixed: IntakeFlow exported to window")
else:
    # Try alternate ending (IntakeFlow is last block before </body>)
    idx_intake = html.rfind('const IntakeFlow =')
    end_body = html.rfind('</body>')
    if idx_intake > 0 and end_body > idx_intake:
        intake_chunk = html[idx_intake:end_body]
        # Find the end of the component
        last_script = intake_chunk.rfind('</script>')
        if last_script >= 0:
            insert_at = idx_intake + last_script
            html = html[:insert_at] + '\nwindow.IntakeFlow = IntakeFlow;\n' + html[insert_at:]
            fixes += 1
            print("Fixed (alt): IntakeFlow exported to window")
    else:
        print("ERROR: Could not find IntakeFlow end for export")

# ── 3. Add SS_BROBYGGERE + SS_MEDARBEJDERE to window (block 2, no exports) ───
# These are used across blocks — safer to explicitly export them
old_ss_user_end = "const SS_USER = {\n  name: 'Maja Holmberg',"
# Find where block 2 ends (before block 3 starts)
# Block 2 ends before: </script> then <!-- ui-kit -->
idx_b2 = html.find('const SS_TYPER =')
end_b2 = html.find('</script>', idx_b2)

chunk_b2 = html[idx_b2:end_b2]
if 'window.SS_BORGERE' not in chunk_b2:
    insert_snippet = (
        "\n\n// Export mock data to global scope\n"
        "window.SS_TYPER       = SS_TYPER;\n"
        "window.SS_BORGERE     = SS_BORGERE;\n"
        "window.SS_BROBYGGERE  = SS_BROBYGGERE;\n"
        "window.SS_MEDARBEJDERE= SS_MEDARBEJDERE;\n"
        "window.SS_APPOINTMENTS_BUSY  = SS_APPOINTMENTS_BUSY;\n"
        "window.SS_APPOINTMENTS_EMPTY = SS_APPOINTMENTS_EMPTY;\n"
        "window.SS_HISTORIK    = SS_HISTORIK;\n"
        "window.SS_SHIFTS      = SS_SHIFTS;\n"
        "window.SS_HOVEDSAEDER = SS_HOVEDSAEDER;\n"
        "window.SS_USER        = SS_USER;\n"
    )
    html = html[:end_b2] + insert_snippet + html[end_b2:]
    fixes += 1
    print("Fixed: Mock data exported to window from block 2")
else:
    print("Mock data already exported to window — OK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n{fixes} fixes applied. File: {len(html):,} bytes")

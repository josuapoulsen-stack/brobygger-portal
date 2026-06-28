import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

old = "  var blob = new Blob([html], { type: 'text/html;charset=utf-8' });"
new = ("""  // Revisionsspor (GDPR art. 30): log hvem der trak indsigtsrapporten, om hvem og hvornår
  try {
    var _audit = JSON.parse(localStorage.getItem('sos_audit_log') || '[]');
    _audit.unshift({
      id: 'audit-' + nu.getTime(),
      handling: 'gdpr_indsigtsrapport',
      menneske_id: menneskeId,
      menneske_navn: navn,
      udfoert_af: window.SoS_AKTIV_BRUGER || 'ukendt',
      tidspunkt: nu.toISOString(),
    });
    localStorage.setItem('sos_audit_log', JSON.stringify(_audit.slice(0, 1000)));
  } catch (e) {}
  var blob = new Blob([html], { type: 'text/html;charset=utf-8' });""")

if old in c:
    c = c.replace(old, new, 1)
    with open(P, 'w', encoding='utf-8') as f:
        f.write(c)
    print("OK: audit-log i SoS_gdprRapport")
else:
    print("FAIL: anker ikke fundet")

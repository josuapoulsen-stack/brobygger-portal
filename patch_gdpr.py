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

# 1) Global GDPR-rapport-bygger (indsigtsret, art. 15)
GDPR = r"""window.SoS_normPhone = function (s) { var d = String(s == null ? '' : s).replace(/\D/g, ''); return d.length > 8 ? d.slice(-8) : d; };

// GDPR indsigtsrapport (art. 15) — samler alt registreret om ét menneske → download som printbar HTML
window.SoS_gdprRapport = function (menneskeId) {
  var m = (window.SoS_MENNESKER || {})[menneskeId];
  if (!m) return;
  var esc = function (s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };
  var bbNavn = function (id) { var b = (window.SoS_BROBYGGERE || []).find(function (x) { return x.id === id; }); return b ? b.name : (id || '—'); };
  var ls = function (k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return []; } };
  var nu = new Date();
  var stamp = nu.toISOString().slice(0, 10) + ' kl. ' + nu.toTimeString().slice(0, 5);
  var navn = ((m.firstName || '') + ' ' + (m.lastName || '')).trim() || 'Ukendt';
  var typeLabel = (window.SoS_TYPER && SoS_TYPER[m.type] && SoS_TYPER[m.type].label) || m.type || '—';

  var appts = (window.SoS_APPOINTMENTS_BUSY || []).filter(function (a) { return a.menneskeId === menneskeId; })
    .sort(function (a, b) { return (a.date || '').localeCompare(b.date || ''); });
  var opkald = ls('sos_opkald_log').filter(function (l) { return l.menneskeId === menneskeId; });
  var kontakter = (window.SoS_KONTAKTER || []).filter(function (k) { return k.menneskeId === menneskeId; })
    .sort(function (a, b) { return (a.dato || '').localeCompare(b.dato || ''); });
  var henv = (m.henvendelser || []).slice().sort(function (a, b) { return (a.dato || '').localeCompare(b.dato || ''); });
  var ucla = m.ucla3;
  var kps = m.kontaktpersoner || (m.kontaktperson ? [m.kontaktperson] : []);

  function rowsTable(rows) {
    var body = rows.filter(function (r) { return r[1]; })
      .map(function (r) { return '<tr><th>' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>'; }).join('');
    return body ? '<table class="kv">' + body + '</table>' : '<p class="tom">Intet registreret.</p>';
  }
  function sektion(titel, indhold) { return '<section><h2>' + esc(titel) + '</h2>' + indhold + '</section>'; }

  // Stamdata
  var stam = rowsTable([
    ['Navn', navn], ['Alder', m.age != null ? m.age + ' år' : ''], ['Køn', m.koen],
    ['Telefon', m.mobil], ['E-mail', m.email], ['Adresse', m.address], ['Mødested', m.meetPoint],
    ['Hovedsæde', m.hq], ['Afdeling', m.afdeling], ['Indsatstype', typeLabel], ['Status', m.status],
    ['Sprog', m.language], ['Henvisningskilde', m.kilde], ['Oprettet', m.startedAt || (m.createdAt)],
    ['Samtykke givet', m.consentAt ? new Date(m.consentAt).toLocaleString('da-DK') : ''],
    ['Tilknyttet brobygger', m.brobyggerId ? bbNavn(m.brobyggerId) : ''],
  ]);

  // Behov
  var behov = (m.needs && m.needs.length) ? '<ul>' + m.needs.map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul>' : '<p class="tom">Intet registreret.</p>';

  // Helbred (følsomt, art. 9)
  var helbred = '';
  if (m.health) helbred += '<p>' + esc(m.health) + '</p>';
  if (m.helbredsKategorier && m.helbredsKategorier.length) helbred += '<p>Kategorier: ' + esc(m.helbredsKategorier.join(', ')) + '</p>';
  if (!helbred) helbred = '<p class="tom">Intet registreret.</p>';

  // Henvendelser
  var henvH = henv.length
    ? '<table class="liste"><tr><th>Dato</th><th>Hvem</th><th>Note</th></tr>' + henv.map(function (h, i) {
        return '<tr><td>' + esc(h.dato) + '</td><td>' + esc(h.type) + (h.navn ? ' (' + esc(h.navn) + ')' : '') + (i === 0 ? ' <em>(første)</em>' : '') + '</td><td>' + esc(h.note || '') + '</td></tr>';
      }).join('') + '</table>'
    : '<p class="tom">Intet registreret.</p>';

  // Kontaktpersoner
  var kpH = kps.length
    ? '<ul>' + kps.map(function (k) { return '<li>' + esc((k.navn || '') + (k.rolle ? ' — ' + k.rolle : '') + (k.tlf ? ' · ' + k.tlf : '')) + '</li>'; }).join('') + '</ul>'
    : '<p class="tom">Intet registreret.</p>';

  // UCLA-3
  var uclaH;
  if (ucla && ucla.optedOut) uclaH = '<p>Mennesket har fravalgt ensomhedsmåling (UCLA-3).</p>';
  else if (ucla && ucla.baseline) {
    var rows = [['Baseline (' + esc(ucla.baseline.dato) + ')', ucla.baseline.sum + ' / 9']];
    (ucla.opfoelgninger || []).forEach(function (o) { rows.push(['Opfølgning (' + esc(o.dato) + ')', o.sum + ' / 9']); });
    uclaH = rowsTable(rows) + '<p class="note">Skala 3–9 — lavere score = mindre ensomhed.</p>';
  } else uclaH = '<p class="tom">Ingen måling registreret.</p>';

  // Aftaler
  var aftH = appts.length
    ? '<table class="liste"><tr><th>Dato</th><th>Aktivitet</th><th>Brobygger</th><th>Status</th></tr>' + appts.map(function (a) {
        return '<tr><td>' + esc(a.date) + (a.start ? ' ' + esc(a.start) : '') + '</td><td>' + esc(a.activity || a.aftaletype || '') + '</td><td>' + esc(a.brobyggerId ? bbNavn(a.brobyggerId) : '—') + '</td><td>' + esc(a.status || '') + '</td></tr>';
      }).join('') + '</table>'
    : '<p class="tom">Ingen aftaler registreret.</p>';

  // Kontakthændelser
  var kontH = kontakter.length
    ? '<table class="liste"><tr><th>Dato</th><th>Type</th><th>Note</th></tr>' + kontakter.map(function (k) {
        return '<tr><td>' + esc(k.dato) + '</td><td>' + esc(k.type || '') + '</td><td>' + esc(k.note || '') + '</td></tr>';
      }).join('') + '</table>'
    : '<p class="tom">Ingen kontakthændelser registreret.</p>';

  // Opkald
  var opkH = opkald.length
    ? '<table class="liste"><tr><th>Dato</th><th>Type</th><th>Note</th></tr>' + opkald.map(function (l) {
        return '<tr><td>' + esc(l.dato) + '</td><td>' + esc(l.type || '') + (l.underType ? ' · ' + esc(l.underType) : '') + '</td><td>' + esc(l.note || '') + '</td></tr>';
      }).join('') + '</table>'
    : '<p class="tom">Ingen opkald registreret.</p>';

  // Noter
  var noterH = (m.notes && m.notes.length)
    ? '<ul>' + m.notes.map(function (n) { return '<li>' + (n.date ? '<strong>' + esc(n.date) + (n.from ? ' (' + esc(n.from) + ')' : '') + ':</strong> ' : '') + esc(n.text || n.tekst || '') + '</li>'; }).join('') + '</ul>'
    : '<p class="tom">Ingen noter registreret.</p>';

  var css = 'body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a130d;max-width:780px;margin:32px auto;padding:0 24px;line-height:1.5}'
    + 'h1{font-size:22px;margin:0 0 2px} h2{font-size:15px;margin:26px 0 8px;border-bottom:1px solid #e6ded3;padding-bottom:4px}'
    + '.meta{color:#7a6f63;font-size:12px;margin-bottom:18px} .intro{background:#f7f2ea;border-left:3px solid #E87A3E;padding:10px 14px;font-size:13px;border-radius:4px}'
    + 'table{width:100%;border-collapse:collapse;font-size:13px} .kv th{text-align:left;width:200px;color:#7a6f63;font-weight:600;vertical-align:top;padding:3px 8px 3px 0}'
    + '.kv td{padding:3px 0} .liste th{text-align:left;border-bottom:1px solid #e6ded3;color:#7a6f63;font-size:11px;text-transform:uppercase;padding:4px 8px 4px 0}'
    + '.liste td{border-bottom:1px solid #f0eae0;padding:5px 8px 5px 0;vertical-align:top} ul{margin:4px 0;padding-left:18px} .tom{color:#9a8f80;font-style:italic;font-size:13px}'
    + '.note{color:#7a6f63;font-size:11px} footer{margin-top:30px;border-top:1px solid #e6ded3;padding-top:12px;color:#7a6f63;font-size:11px} @media print{body{margin:0}}';

  var html = '<!doctype html><html lang="da"><head><meta charset="utf-8"><title>Indsigtsrapport — ' + esc(navn) + '</title><style>' + css + '</style></head><body>'
    + '<h1>Indsigtsrapport</h1>'
    + '<div class="meta">Social Sundhed · jf. GDPR art. 15 (indsigtsret) · genereret ' + esc(stamp) + '</div>'
    + '<div class="intro">Denne rapport viser de personoplysninger, Social Sundhed har registreret om <strong>' + esc(navn) + '</strong>. Har du spørgsmål, ønsker du oplysninger rettet eller slettet, kan du kontakte os.</div>'
    + sektion('Stamoplysninger', stam)
    + sektion('Behov', behov)
    + sektion('Helbred / hensyn (følsomme oplysninger)', helbred)
    + sektion('Henvendelser', henvH)
    + sektion('Kontaktpersoner', kpH)
    + sektion('Ensomhedsmåling (UCLA-3)', uclaH)
    + sektion('Aftaler', aftH)
    + sektion('Kontakthændelser', kontH)
    + sektion('Telefonopkald', opkH)
    + sektion('Noter', noterH)
    + '<footer>Genereret automatisk fra Brobygger-portalen. Indeholder data fra menneskets profil, aftaler, henvendelser, kontakter og opkald. Kontakt din koordinator for berigtigelse eller sletning (GDPR art. 16 & 17).</footer>'
    + '</body></html>';

  var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'indsigtsrapport-' + (navn.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'menneske') + '-' + nu.toISOString().slice(0, 10) + '.html';
  a.click();
};"""

sub("window.SoS_normPhone = function (s) { var d = String(s == null ? '' : s).replace(/\\D/g, ''); return d.length > 8 ? d.slice(-8) : d; };",
    GDPR, "1: GDPR-rapport-funktion")

# 2) Thread canUserMgmt → DesktopMennesker
sub("{section === 'mennesker' && <DesktopMennesker initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)} scopeHq={viewingHq} scopeAfd={onlyMine ? ownAfdeling : null}/>}",
    "{section === 'mennesker' && <DesktopMennesker initialTarget={searchTarget} onTargetConsumed={() => setSearchTarget(null)} scopeHq={viewingHq} scopeAfd={onlyMine ? ownAfdeling : null} canUserMgmt={canUserMgmt}/>}",
    "2: DesktopView-kald")

sub("const DesktopMennesker = ({ initialTarget, onTargetConsumed, scopeHq, scopeAfd }) => {",
    "const DesktopMennesker = ({ initialTarget, onTargetConsumed, scopeHq, scopeAfd, canUserMgmt = false }) => {",
    "3: DesktopMennesker signatur")

sub("""        <DesktopMenneskeDetailPanel
          menneske={selected}
          onClose={() => setSelected(null)}""",
"""        <DesktopMenneskeDetailPanel
          menneske={selected}
          canUserMgmt={canUserMgmt}
          onClose={() => setSelected(null)}""",
    "4: detail-panel-kald")

sub("const DesktopMenneskeDetailPanel = ({ menneske: m, onClose, onRefresh }) => {",
    "const DesktopMenneskeDetailPanel = ({ menneske: m, onClose, onRefresh, canUserMgmt = false }) => {",
    "5: detail-panel signatur")

# 6) GDPR-knap i actions strip (kun admin)
sub("""            Afslut forløb
          </button>
        )}
      </div>

      {/* Tilfoej kontakt — overlay modal */}""",
"""            Afslut forløb
          </button>
        )}
        {canUserMgmt && (
          <button onClick={() => window.SoS_gdprRapport && window.SoS_gdprRapport(m.id)}
            title="Download alt registreret om personen (GDPR art. 15 — indsigtsret)" style={{
            padding: '8px 14px', borderRadius: SoS.r.sm, background: 'transparent', color: SoS.ink,
            border: `1px solid ${SoS.line}`, fontFamily: SoS.sans, fontSize: 12, cursor: 'pointer', flexShrink: 0,
            display: 'flex', alignItems: 'center', gap: 5 }}>
            <Icon name="download" size={13} color={SoS.ink} weight={2.3}/>
            GDPR-rapport
          </button>
        )}
      </div>

      {/* Tilfoej kontakt — overlay modal */}""",
    "6: GDPR-knap")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

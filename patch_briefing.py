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

# ── Ny komponent-blok (raw string: backslashes/\n/${} bevares verbatim) ──
COMPONENTS = r'''const SoS_BRIEFING_SEEDS = [
  { id: 'seed-sundhed', navn: 'Hospitals-/lægeledsagelse', indsats: 'sundhed', erStandard: true,
    tekst: 'Hej {{bb_fornavn}}\n\nDu skal ledsage {{fornavn}} ({{alder}}) til {{aktivitet}} d. {{dato}} kl. {{tid}}.\nMødested: {{sted}}.\n\nBehov: {{behov}}\nSprog: {{sprog}}\n\nKontakt ved spørgsmål: {{kontaktperson}} ({{kontaktperson_tlf}}).' },
  { id: 'seed-social', navn: 'Første besøg (social)', indsats: 'social', erStandard: true,
    tekst: 'Hej {{bb_fornavn}}\n\nDu skal mødes med {{fornavn}} ({{alder}}) d. {{dato}} kl. {{tid}}.\nMødested: {{sted}}.\n\nLidt om {{fornavn}}: {{behov}}.\nStart gerne roligt — I aftaler samtaleemner og hensyn undervejs.' },
  { id: 'seed-forening', navn: 'Aktivitet (forening)', indsats: 'forening', erStandard: true,
    tekst: 'Hej {{bb_fornavn}}\n\n{{fornavn}} ({{alder}}) deltager i {{aktivitet}} d. {{dato}} kl. {{tid}}.\nMødested: {{sted}}.\n\nBehov: {{behov}}.' },
];

// Flettefelter (helbred bevidst UDELADT — indsættes kun via eksplicit knap + advarsel)
const _briefingResolve = (s, m, appt, bb) => {
  const map = {
    fornavn:           m ? (m.firstName || '') : '',
    efternavn:         m ? (m.lastName || '') : '',
    alder:             (m && m.age != null) ? (m.age + ' år') : '',
    adresse:           m ? (m.address || '') : '',
    moedested:         m ? (m.meetPoint || '') : '',
    telefon:           m ? (m.mobil || '') : '',
    sprog:             m ? (m.language || '') : '',
    behov:             (m && m.needs) ? m.needs.join(', ') : '',
    indsats:           (m && SoS_TYPER[m.type] && SoS_TYPER[m.type].label) || (m && m.type) || '',
    praeferencer:      (m && m.praeferencer) ? [m.praeferencer.tidspunkt, m.praeferencer.frekvens].filter(Boolean).join(', ') : '',
    kontaktperson:     (m && m.kontaktperson && m.kontaktperson.navn) || (m && m.contact && m.contact.name) || '',
    kontaktperson_tlf: (m && m.kontaktperson && m.kontaktperson.tlf) || (m && m.contact && m.contact.phone) || '',
    dato:              appt.date || '',
    tid:               appt.start ? (appt.start + (appt.end ? '–' + appt.end : '')) : '',
    sted:              appt.location || (m && m.appointmentSted) || '',
    aktivitet:         appt.activity || '',
    bb_fornavn:        bb ? (bb.name || '').split(' ')[0] : '',
  };
  return String(s).replace(/\{\{(\w+)\}\}/g, (whole, k) => (k in map) ? map[k] : whole);
};

const _BRIEFING_FELTER = [
  ['Fornavn','fornavn'],['Alder','alder'],['Adresse','adresse'],['Mødested','moedested'],
  ['Telefon','telefon'],['Sprog','sprog'],['Behov','behov'],['Indsats','indsats'],
  ['Præferencer','praeferencer'],['Kontaktperson','kontaktperson'],['Kontakt-tlf','kontaktperson_tlf'],
  ['Dato','dato'],['Tid','tid'],['Sted','sted'],['Aktivitet','aktivitet'],['Brobygger','bb_fornavn'],
];

const BriefingModal = ({ appt, onClose, onApply }) => {
  const m  = SoS_MENNESKER[appt.menneskeId];
  const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === appt.brobyggerId);
  const [view, setView]   = React.useState('compose');   // compose | skabeloner | rediger
  const [tekst, setTekst] = React.useState(appt.brobyggerNote || '');
  const [valgt, setValgt] = React.useState('');
  const [sendBesked, setSendBesked] = React.useState(false);
  const [gemt, setGemt]   = React.useState(false);
  const [stored, setStored] = React.useState(() => {
    try { return JSON.parse(localStorage.getItem('sos_besked_skabeloner') || '[]'); } catch { return []; }
  });
  // rediger-felter
  const [redId, setRedId]           = React.useState(null);
  const [redNavn, setRedNavn]       = React.useState('');
  const [redIndsats, setRedIndsats] = React.useState('alle');
  const [redTekst, setRedTekst]     = React.useState('');

  const alle = [...SoS_BRIEFING_SEEDS, ...stored];
  const mType = m ? m.type : null;
  const sorteret = [...alle].sort((a, b) => {
    const r = x => x.indsats === mType ? 0 : x.indsats === 'alle' ? 1 : 2;
    return r(a) - r(b);
  });

  const persistStored = (arr) => { setStored(arr); localStorage.setItem('sos_besked_skabeloner', JSON.stringify(arr)); };

  const brugSkabelon = (id) => {
    setValgt(id);
    const t = alle.find(x => x.id === id);
    if (t) setTekst(_briefingResolve(t.tekst, m, appt, bb));
  };
  const indsaetFelt = (token) => {
    const v = _briefingResolve('{{' + token + '}}', m, appt, bb);
    if (!v) return;
    setTekst(t => (t && !t.endsWith('\n') && !t.endsWith(' ')) ? t + ' ' + v : t + v);
  };
  const indsaetHelbred = () => {
    if (!m || !m.health) return;
    if (!window.confirm('Indsæt følsomme helbredsoplysninger (GDPR art. 9)?\n\n"' + m.health + '"')) return;
    setTekst(t => (t ? t + '\n' : '') + 'Helbred & hensyn: ' + m.health);
  };

  const gemPaaAftale = () => {
    if (appt.id) {
      const list = (window.SoS_APPOINTMENTS_BUSY || []).map(a => a.id === appt.id ? { ...a, brobyggerNote: tekst } : a);
      window.SoS_APPOINTMENTS_BUSY = list;
      if (window.SoS_STORE) window.SoS_STORE.save('appointments', list);
    }
    if (sendBesked && appt.brobyggerId) {
      const msgs = JSON.parse(localStorage.getItem('sos_beskeder') || '[]');
      msgs.push({ id: 'msg-' + Date.now(), fra: 'admin', til: appt.brobyggerId, tekst: tekst, sendt: new Date().toISOString(), laest: false });
      localStorage.setItem('sos_beskeder', JSON.stringify(msgs));
      const nk = 'sos_notifikationer';
      const ns = JSON.parse(localStorage.getItem(nk) || '[]');
      ns.push({ id: 'n-' + Date.now(), type: 'briefing', read: false, createdAt: new Date().toISOString(),
        text: 'Briefing til aftale d. ' + (appt.date || ''), brobyggerId: appt.brobyggerId });
      localStorage.setItem(nk, JSON.stringify(ns));
    }
    if (onApply) onApply(tekst);
    setGemt(true);
    setTimeout(onClose, 600);
  };

  const startRediger = (t) => {
    if (t) {
      setRedId(t.erStandard ? null : t.id);
      setRedNavn(t.erStandard ? (t.navn + ' (kopi)') : t.navn);
      setRedIndsats(t.indsats); setRedTekst(t.tekst);
    } else { setRedId(null); setRedNavn(''); setRedIndsats('alle'); setRedTekst(''); }
    setView('rediger');
  };
  const gemSkabelon = () => {
    if (!redNavn.trim() || !redTekst.trim()) return;
    if (redId) persistStored(stored.map(s => s.id === redId ? { ...s, navn: redNavn.trim(), indsats: redIndsats, tekst: redTekst } : s));
    else persistStored([...stored, { id: 'skab-' + Date.now(), navn: redNavn.trim(), indsats: redIndsats, tekst: redTekst, erStandard: false }]);
    setView('skabeloner');
  };
  const sletSkabelon = (id) => { if (window.confirm('Slet skabelonen?')) persistStored(stored.filter(s => s.id !== id)); };

  const overlay = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 400,
    display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 };
  const box = { background: '#fff', width: '100%', maxWidth: 540, maxHeight: '90vh',
    display: 'flex', flexDirection: 'column', borderRadius: SoS.r.lg, overflow: 'hidden',
    boxShadow: '0 20px 60px rgba(0,0,0,0.25)' };
  const inp = { width: '100%', padding: '9px 12px', border: `1px solid ${SoS.line}`,
    borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, color: SoS.ink,
    outline: 'none', boxSizing: 'border-box' };
  const lbl = { fontFamily: SoS.sans, fontSize: 11, fontWeight: 600, color: SoS.inkSoft, marginBottom: 5 };
  const INDSATS = [['alle','Alle'],['social','Social'],['forening','Forening'],['sundhed','Sundhed']];

  // ── Header ──
  const header = (titel, tilbage) => (
    <div style={{ padding: '14px 20px', borderBottom: `1px solid ${SoS.line}`,
      display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
      {tilbage && (
        <button onClick={tilbage} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}>
          <Icon name="chevronL" size={20} color={SoS.ink}/>
        </button>
      )}
      <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700, color: SoS.ink }}>{titel}</div>
      <button onClick={onClose} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer' }}>
        <Icon name="close" size={16} color={SoS.inkMuted}/>
      </button>
    </div>
  );

  // ── COMPOSE ──
  if (view === 'compose') return (
    <div style={overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={box}>
        {header('Briefing til ' + (bb ? bb.name.split(' ')[0] : 'brobygger'))}
        <div style={{ overflowY: 'auto', padding: 20, flex: 1 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginBottom: 14 }}>
            {m ? (m.firstName + ' ' + m.lastName) : '—'} · {appt.date || ''}{appt.start ? ' kl. ' + appt.start : ''}
          </div>

          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Skabelon</div>
            <div style={{ display: 'flex', gap: 8 }}>
              <select value={valgt} onChange={e => brugSkabelon(e.target.value)} style={{ ...inp, flex: 1 }}>
                <option value="">Vælg skabelon…</option>
                {sorteret.map(t => (
                  <option key={t.id} value={t.id}>{t.navn}{t.indsats !== 'alle' ? ' · ' + t.indsats : ''}</option>
                ))}
              </select>
              <button onClick={() => setView('skabeloner')} style={{ padding: '0 12px',
                background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, color: SoS.ink, whiteSpace: 'nowrap' }}>
                Rediger
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
            <select value="" onChange={e => { if (e.target.value) { indsaetFelt(e.target.value); e.target.value = ''; } }}
              style={{ ...inp, width: 'auto', flex: 1 }}>
              <option value="">+ Indsæt felt fra kortet…</option>
              {_BRIEFING_FELTER.map(([l, t]) => <option key={t} value={t}>{l}</option>)}
            </select>
            {m && m.health && (
              <button onClick={indsaetHelbred} title="Følsom — kræver bekræftelse" style={{ padding: '0 12px',
                background: SoS.amber + '18', border: `1px solid ${SoS.amber}`, borderRadius: SoS.r.sm,
                cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.amber }}>
                + Helbred ⚠
              </button>
            )}
          </div>

          <textarea value={tekst} onChange={e => setTekst(e.target.value)} rows={9}
            placeholder="Skriv en briefing, eller vælg en skabelon ovenfor…"
            style={{ ...inp, resize: 'vertical', lineHeight: 1.5, minHeight: 160 }}/>
        </div>

        <div style={{ padding: '14px 20px', borderTop: `1px solid ${SoS.line}`, flexShrink: 0 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginBottom: 12 }}>
            <input type="checkbox" checked={sendBesked} onChange={e => setSendBesked(e.target.checked)}/>
            <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>
              Send også som besked til {bb ? bb.name.split(' ')[0] : 'brobyggeren'} (notifikation)
            </span>
          </label>
          <button onClick={gemPaaAftale} disabled={!tekst.trim()} style={{ width: '100%', padding: '12px 0',
            background: gemt ? SoS.green : (tekst.trim() ? SoS.ink : SoS.lineSoft),
            color: tekst.trim() ? '#fff' : SoS.inkMuted, border: 'none', borderRadius: SoS.r.sm,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, cursor: tekst.trim() ? 'pointer' : 'default' }}>
            {gemt ? '✓ Gemt på aftalen' + (sendBesked ? ' og sendt' : '') : 'Gem på aftalen' + (sendBesked ? ' og send' : '')}
          </button>
        </div>
      </div>
    </div>
  );

  // ── SKABELONER (liste) ──
  if (view === 'skabeloner') return (
    <div style={overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={box}>
        {header('Skabeloner', () => setView('compose'))}
        <div style={{ overflowY: 'auto', padding: 16, flex: 1 }}>
          <button onClick={() => startRediger(null)} style={{ width: '100%', padding: '10px 0', marginBottom: 14,
            background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm,
            fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
            + Ny skabelon
          </button>
          {sorteret.map(t => (
            <div key={t.id} style={{ border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
              padding: '12px 14px', marginBottom: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: SoS.ink, flex: 1 }}>{t.navn}</div>
                {t.erStandard && <span style={{ fontFamily: SoS.mono, fontSize: 9, fontWeight: 700,
                  color: SoS.inkMuted, background: SoS.surface, padding: '2px 6px', borderRadius: 3 }}>STANDARD</span>}
                <span style={{ fontFamily: SoS.mono, fontSize: 9, color: SoS.inkMuted }}>{t.indsats}</span>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                <button onClick={() => { brugSkabelon(t.id); setView('compose'); }} style={{ flex: 1, padding: '6px 0',
                  background: SoS.ink, color: '#fff', border: 'none', borderRadius: SoS.r.sm,
                  cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600 }}>Brug</button>
                <button onClick={() => startRediger(t)} style={{ padding: '6px 12px', background: SoS.surface,
                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
                  fontFamily: SoS.sans, fontSize: 12, color: SoS.ink }}>{t.erStandard ? 'Dupliker' : 'Rediger'}</button>
                {!t.erStandard && (
                  <button onClick={() => sletSkabelon(t.id)} style={{ padding: '6px 10px', background: 'none',
                    border: `1px solid ${SoS.rose}55`, borderRadius: SoS.r.sm, cursor: 'pointer',
                    fontFamily: SoS.sans, fontSize: 12, color: SoS.rose }}>Slet</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // ── REDIGER ──
  return (
    <div style={overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={box}>
        {header(redId ? 'Rediger skabelon' : 'Ny skabelon', () => setView('skabeloner'))}
        <div style={{ overflowY: 'auto', padding: 20, flex: 1 }}>
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Navn</div>
            <input value={redNavn} onChange={e => setRedNavn(e.target.value)} placeholder="f.eks. Lægebesøg" style={inp}/>
          </div>
          <div style={{ marginBottom: 12 }}>
            <div style={lbl}>Indsats</div>
            <div style={{ display: 'flex', gap: 6 }}>
              {INDSATS.map(([v, l]) => (
                <button key={v} onClick={() => setRedIndsats(v)} style={{ flex: 1, padding: '7px 0',
                  border: `1.5px solid ${redIndsats === v ? SoS.ink : SoS.line}`, borderRadius: SoS.r.sm,
                  background: redIndsats === v ? SoS.ink : '#fff', color: redIndsats === v ? '#fff' : SoS.ink,
                  cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: redIndsats === v ? 700 : 400 }}>{l}</button>
              ))}
            </div>
          </div>
          <div style={{ marginBottom: 8 }}>
            <div style={lbl}>Flettefelter (klik for at indsætte)</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
              {_BRIEFING_FELTER.map(([l, t]) => (
                <button key={t} onClick={() => setRedTekst(x => x + '{{' + t + '}}')} style={{ padding: '4px 9px',
                  background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
                  cursor: 'pointer', fontFamily: SoS.mono, fontSize: 10, color: SoS.ink }}>{l}</button>
              ))}
            </div>
          </div>
          <textarea value={redTekst} onChange={e => setRedTekst(e.target.value)} rows={7}
            placeholder="Skriv skabelonteksten med {{flettefelter}}…"
            style={{ ...inp, resize: 'vertical', lineHeight: 1.5, minHeight: 130, marginBottom: 12 }}/>
          <div style={lbl}>Forhåndsvisning (mod {m ? m.firstName : 'mennesket'})</div>
          <div style={{ background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm,
            padding: '10px 12px', fontFamily: SoS.sans, fontSize: 12, color: SoS.ink,
            lineHeight: 1.5, whiteSpace: 'pre-wrap', minHeight: 40 }}>
            {redTekst ? _briefingResolve(redTekst, m, appt, bb) : <span style={{ color: SoS.inkMuted }}>—</span>}
          </div>
        </div>
        <div style={{ padding: '14px 20px', borderTop: `1px solid ${SoS.line}`, flexShrink: 0, display: 'flex', gap: 8 }}>
          <button onClick={() => setView('skabeloner')} style={{ flex: 1, padding: '11px 0', background: SoS.surface,
            border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',
            fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>Annuller</button>
          <button onClick={gemSkabelon} disabled={!redNavn.trim() || !redTekst.trim()} style={{ flex: 2, padding: '11px 0',
            background: (redNavn.trim() && redTekst.trim()) ? SoS.ink : SoS.lineSoft,
            color: (redNavn.trim() && redTekst.trim()) ? '#fff' : SoS.inkMuted, border: 'none',
            borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,
            cursor: (redNavn.trim() && redTekst.trim()) ? 'pointer' : 'default' }}>Gem skabelon</button>
        </div>
      </div>
    </div>
  );
};

'''

# 1) Indsæt komponenter før DesktopApptModal
sub("const DesktopApptModal = ({ initial = {}, onClose, onSave, onDelete }) => {",
    COMPONENTS + "const DesktopApptModal = ({ initial = {}, onClose, onSave, onDelete }) => {",
    "1: indsæt BriefingModal + helpers")

# 2) State i DesktopApptModal
sub("  const isEdit  = !!initial.id;",
    "  const isEdit  = !!initial.id;\n  const [briefingOpen, setBriefingOpen] = React.useState(false);",
    "2: briefingOpen state")

# 3) Briefing-knap over brobyggerNote-textarea
sub(
    "            <textarea\n"
    "              placeholder=\"Fx: Husk at medbringe medicinlisten. Navn på læge er Hansen.\"\n"
    "              value={form.brobyggerNote}",
    "            {form.menneskeId && form.brobyggerId && (\n"
    "              <button type=\"button\" onClick={() => setBriefingOpen(true)}\n"
    "                style={{ marginBottom: 8, padding: '7px 12px', background: SoS.surface,\n"
    "                  border: `1px solid ${SoS.line}`, borderRadius: SoS.r.sm, cursor: 'pointer',\n"
    "                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink,\n"
    "                  display: 'inline-flex', alignItems: 'center', gap: 6 }}>\n"
    "                📋 Brug skabelon / hent fra menneskets kort\n"
    "              </button>\n"
    "            )}\n"
    "            <textarea\n"
    "              placeholder=\"Fx: Husk at medbringe medicinlisten. Navn på læge er Hansen.\"\n"
    "              value={form.brobyggerNote}",
    "3: briefing-knap i DesktopApptModal")

# 4) Render BriefingModal i DesktopApptModal (efter footer-div)
sub(
    "            {isEdit ? 'Gem ændringer' : 'Opret aftale'}\n"
    "          </button>\n"
    "        </div>\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "};\n"
    "\n"
    "const PostAftaleModal",
    "            {isEdit ? 'Gem ændringer' : 'Opret aftale'}\n"
    "          </button>\n"
    "        </div>\n"
    "        {briefingOpen && (\n"
    "          <BriefingModal\n"
    "            appt={{ ...form, id: initial.id }}\n"
    "            onClose={() => setBriefingOpen(false)}\n"
    "            onApply={(t) => setForm(f => ({ ...f, brobyggerNote: t }))}\n"
    "          />\n"
    "        )}\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "};\n"
    "\n"
    "const PostAftaleModal",
    "4: render BriefingModal")

# 5) Vis briefing til brobyggeren i AppointmentDetailScreen
sub(
    "          {appt.activity}\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      {/* Menneske card */}",
    "          {appt.activity}\n"
    "        </div>\n"
    "      </div>\n"
    "\n"
    "      {appt.brobyggerNote && appt.brobyggerNote.trim() && (\n"
    "        <div style={{ margin: '16px 16px 0', background: '#fff',\n"
    "          borderRadius: SoS.r.xl, padding: 16, boxShadow: SoS.shadow.md,\n"
    "          borderLeft: `4px solid ${SoS.orange}` }}>\n"
    "          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>\n"
    "            <Icon name=\"note\" size={15} color={SoS.orange}/>\n"
    "            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,\n"
    "              color: SoS.inkMuted, letterSpacing: 1, textTransform: 'uppercase' }}>Besked fra rådgiver</div>\n"
    "          </div>\n"
    "          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,\n"
    "            lineHeight: 1.55, whiteSpace: 'pre-wrap' }}>{appt.brobyggerNote}</div>\n"
    "        </div>\n"
    "      )}\n"
    "\n"
    "      {/* Menneske card */}",
    "5: vis briefing i AppointmentDetailScreen")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

# CRLF-fix
with open(P, 'rb') as f:
    b = f.read()
needle = b".join('" + bytes([0x0a]) + b"');"
if needle in b:
    b = b.replace(needle, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(P, 'wb') as f:
        f.write(b)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f"\nOK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"\nFAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

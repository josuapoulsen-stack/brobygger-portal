#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_messaging_final.py
Applies 7 changes to Brobygger portal.html
"""

import re, sys, os

PATH = r"C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html"

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
changes_applied = []

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 1: Tilføj mobil/email til SoS_BORGERE
# ─────────────────────────────────────────────────────────────────────────────

# b-1 Ingrid
old = "{ id: 'b-1',"
# Find the full b-1 object and add fields before closing brace
# Strategy: find each borger object by id and insert before its closing brace

def add_borger_fields(html, borger_id, mobil, mobilOptOut, email):
    """Find the borger object by id in SoS_MENNESKER and add contact fields before closing brace."""
    # SoS_MENNESKER uses object syntax: 'b-1': { id: 'b-1', ...  },
    # Find the entry by looking for the key pattern followed by the id field
    start_marker = f"  '{borger_id}': {{"
    idx = html.find(start_marker)
    if idx == -1:
        # Try alternate spacing
        start_marker = f"  '{borger_id}':{{"
        idx = html.find(start_marker)
    if idx == -1:
        print(f"  ERROR: Could not find borger {borger_id} (tried '  \\'{borger_id}\\': {{' )")
        return html, False

    # Find the inner object start (the { after the colon)
    inner_brace_start = html.find('{', idx + len(f"  '{borger_id}':"))
    if inner_brace_start == -1:
        print(f"  ERROR: No {{ found after key for {borger_id}")
        return html, False

    # Count braces from the inner object opening
    brace_count = 0
    i = inner_brace_start
    while i < len(html):
        if html[i] == '{':
            brace_count += 1
        elif html[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                insert_pos = i

                email_val = f"'{email}'" if email else 'null'
                mobil_val = f"'{mobil}'" if mobil else 'null'
                mobilOptOut_val = 'true' if mobilOptOut else 'false'

                fields = (
                    f",\n    mobil: {mobil_val},"
                    f"\n    mobilOptOut: {mobilOptOut_val},"
                    f"\n    email: {email_val}"
                )

                obj_slice = html[inner_brace_start:i]
                if 'mobilOptOut' in obj_slice:
                    print(f"  SKIP: borger {borger_id} already has mobilOptOut")
                    return html, False

                html = html[:insert_pos] + fields + '\n  ' + html[insert_pos:]
                return html, True
        i += 1

    print(f"  ERROR: Could not find closing brace for borger {borger_id}")
    return html, False

borgere_data = [
    ('b-1', '+45 31 22 44 11', False, None),
    ('b-2', '+45 42 88 12 34', False, 'ahmad.k@mail.dk'),
    ('b-3', None, True, None),
    ('b-4', '+45 29 77 00 55', False, None),
]

for bid, mobil, opt_out, email in borgere_data:
    html, ok = add_borger_fields(html, bid, mobil, opt_out, email)
    status = "OK" if ok else "SKIP/ERROR"
    changes_applied.append(f"Ændring 1 – borger {bid}: {status}")
    print(f"  Ændring 1 – borger {bid}: {status}")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 2: Tilføj mobil/email til SoS_BROBYGGERE
# ─────────────────────────────────────────────────────────────────────────────

brobyggere_data = [
    ('bb-1', '+45 23 45 67 89', 'maja.holmberg@socialsundhed.org'),
    ('bb-2', '+45 31 22 09 18', 'soren.nybo@socialsundhed.org'),
    ('bb-3', '+45 42 11 33 44', 'fatima.elsayed@socialsundhed.org'),
    ('bb-4', '+45 26 54 78 90', 'jens.vangsgaard@socialsundhed.org'),
    ('bb-5', '+45 51 23 45 67', 'lise.abildgaard@socialsundhed.org'),
    ('bb-6', '+45 60 11 22 33', 'mikkel.hauge@socialsundhed.org'),
    ('bb-7', '+45 72 88 44 00', 'anja.poulsen@socialsundhed.org'),
    ('bb-8', '+45 81 55 66 77', 'karim.abbas@socialsundhed.org'),
]

def add_brobygger_fields(html, bb_id, mobil, email):
    start_marker = f"{{ id: '{bb_id}',"
    idx = html.find(start_marker)
    if idx == -1:
        print(f"  ERROR: Could not find brobygger {bb_id}")
        return html, False

    brace_count = 0
    i = idx
    while i < len(html):
        if html[i] == '{':
            brace_count += 1
        elif html[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                insert_pos = i
                obj_slice = html[idx:i]
                if 'mobil:' in obj_slice:
                    print(f"  SKIP: brobygger {bb_id} already has mobil")
                    return html, False

                fields = (
                    f",\n    mobil: '{mobil}',"
                    f"\n    email: '{email}'"
                )
                html = html[:insert_pos] + fields + '\n  ' + html[insert_pos:]
                return html, True
        i += 1

    print(f"  ERROR: Could not find closing brace for brobygger {bb_id}")
    return html, False

for bb_id, mobil, email in brobyggere_data:
    html, ok = add_brobygger_fields(html, bb_id, mobil, email)
    status = "OK" if ok else "SKIP/ERROR"
    changes_applied.append(f"Ændring 2 – brobygger {bb_id}: {status}")
    print(f"  Ændring 2 – brobygger {bb_id}: {status}")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 3: Vis borger mobil i AppointmentDetailScreen / InfoRow
# ─────────────────────────────────────────────────────────────────────────────

NEW_BORGER_INFOROW = '''              {revealed && (
                borger.mobilOptOut
                  ? <InfoRow icon="phone" label="Mobilkontakt" value={
                      <span style={{ color: SoS.inkMuted, fontStyle: 'italic' }}>
                        Borgeren ønsker ikke mobilkontakt \u2013 kontakt via koordinator
                      </span>
                    } />
                  : borger.mobil
                    ? <InfoRow icon="phone" label="Mobil (borger)" value={borger.mobil}
                        action={<Icon name="phone" size={16} color={SoS.orange} />} />
                    : <InfoRow icon="phone" label="Mobil (borger)" value={
                        <span style={{ color: SoS.rose, fontStyle: 'italic' }}>Ikke registreret</span>
                      } />
              )}
'''

TARGET_INFOROW = '<InfoRow icon="phone" label="Koordinator"'

idx = html.find(TARGET_INFOROW)
if idx == -1:
    print("  ERROR: Could not find InfoRow phone/Koordinator")
    changes_applied.append("Ændring 3: ERROR – target not found")
else:
    # Check if already patched
    preceding = html[max(0, idx-300):idx]
    if 'mobilOptOut' in preceding:
        print("  SKIP: Ændring 3 already applied")
        changes_applied.append("Ændring 3: SKIP")
    else:
        # Find the start of the line (for indentation)
        line_start = html.rfind('\n', 0, idx) + 1
        html = html[:line_start] + NEW_BORGER_INFOROW + html[line_start:]
        print("  Ændring 3: OK")
        changes_applied.append("Ændring 3: OK")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 4: Vis brobyggerens mobil + email i BrobyggerProfilePanel
# ─────────────────────────────────────────────────────────────────────────────

KONTAKT_DIV = '''
                {/* Kontaktoplysninger */}
                <div style={{ marginTop: 12, padding: '12px 16px', background: SoS.cream,
                  borderRadius: SoS.r.md }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                    color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
                    Kontakt
                  </div>
                  {b.mobil ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                      <Icon name="phone" size={16} color={SoS.orange}/>
                      <span style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}>{b.mobil}</span>
                    </div>
                  ) : (
                    <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.rose, marginBottom: 6 }}>
                      \u26a0 Mobilnummer mangler
                    </div>
                  )}
                  {b.email && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <Icon name="note" size={16} color={SoS.orange}/>
                      <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{b.email}</span>
                    </div>
                  )}
                </div>'''

# Find BrobyggerProfilePanel and a distinctive pattern near the stats section
# Look for "b.active} aktive" or "b.started" in the panel
# We want to insert after the stats div that shows active count

# Strategy: find the panel component, then find } aktive</div> or similar
# and insert after the next closing </div>

# Look for the pattern in BrobyggerProfilePanel
panel_start = html.find('BrobyggerProfilePanel')
if panel_start == -1:
    print("  ERROR: BrobyggerProfilePanel not found")
    changes_applied.append("Ændring 4: ERROR – panel not found")
else:
    # Check if already applied
    panel_region = html[panel_start:panel_start+5000]
    if 'Kontaktoplysninger' in panel_region:
        print("  SKIP: Ændring 4 already applied")
        changes_applied.append("Ændring 4: SKIP")
    else:
        # Find "aktive" in the panel region
        aktive_idx = html.find('aktive', panel_start)
        if aktive_idx == -1:
            print("  ERROR: 'aktive' not found in BrobyggerProfilePanel region")
            changes_applied.append("Ændring 4: ERROR – aktive not found")
        else:
            # Find the next </div> after this
            next_div_close = html.find('</div>', aktive_idx)
            if next_div_close == -1:
                print("  ERROR: No </div> after aktive")
                changes_applied.append("Ændring 4: ERROR")
            else:
                insert_pos = next_div_close + len('</div>')
                html = html[:insert_pos] + KONTAKT_DIV + html[insert_pos:]
                print("  Ændring 4: OK")
                changes_applied.append("Ændring 4: OK")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 5: Erstat MessagesList + MessageThread med komplet ny kode
# ─────────────────────────────────────────────────────────────────────────────

NEW_MESSAGING_BLOCK = r"""// ── Coordinator compose modal ─────────────────────────────────────────────
const SoS_TEMPLATES = [
  { id: 'noter', emoji: '📋', label: 'Husk at notere',
    text: 'Husk at udfylde en registrering efter din næste aftale. Det tager 2 minutter og er vigtigt for vores dokumentation og SROI-rapport.' },
  { id: 'afbud', emoji: '📞', label: 'Meld afbud i tid',
    text: 'Husk altid at melde afbud til din koordinator senest 24 timer før en planlagt aftale, så vi kan underrette borgeren i god tid.' },
  { id: 'info',  emoji: '📅', label: 'Infomøde',
    text: 'Vi holder infomøde for brobyggere snart. Dato og program følger — sæt allerede et kryds i kalenderen!' },
  { id: 'ros',   emoji: '⭐', label: 'Tak og ros',
    text: 'Tak for din fantastiske indsats som brobygger. Det arbejde du gør gør en reel forskel. Vi sætter stor pris på dig!' },
  { id: 'husk',  emoji: '🔔', label: 'Husk arrangement',
    text: 'Husk vores fælles arrangement. Meld tilbage til din koordinator om du kommer.' },
];

const ComposeMessage = ({ role, ownHq, onClose }) => {
  const isAdmin = role === 'admin';
  const [scope, setScope] = React.useState('aktive');
  const [pickingBb, setPickingBb] = React.useState(false);
  const [selectedBb, setSelectedBb] = React.useState(null);
  const [bbSearch, setBbSearch] = React.useState('');
  const [templateId, setTemplateId] = React.useState(null);
  const [body, setBody] = React.useState('');
  const [urgent, setUrgent] = React.useState(false);
  const [sent, setSent] = React.useState(false);

  const SCOPES = [
    { id: 'een',      label: 'Én brobygger',   sub: 'Vælg nedenfor' },
    { id: 'aktive',   label: 'Alle aktive',     sub: 'Ekskl. pause' },
    { id: 'alle',     label: 'Inkl. pause',     sub: 'Alle i ' + (ownHq || 'HQ') },
    ...(isAdmin ? [{ id: 'alle-hq', label: "Alle HQ'er", sub: 'Tværgående fællesbesked' }] : []),
  ];

  const allBbs    = (window.SoS_BROBYGGERE || []);
  const activeBbs = allBbs.filter(b => b.status === 'aktiv');
  const recipientCount = scope === 'een' ? (selectedBb ? 1 : 0)
    : scope === 'aktive' ? activeBbs.length
    : scope === 'alle'   ? allBbs.length
    : 412;

  const canSend = body.trim().length > 2 && (scope !== 'een' || selectedBb);

  const filteredBbs = allBbs.filter(b =>
    !bbSearch || b.name.toLowerCase().includes(bbSearch.toLowerCase())
  );

  if (sent) return (
    <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)',
      zIndex: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ background: '#fff', borderRadius: SoS.r.xl, padding: 32, textAlign: 'center', width: '100%' }}>
        <div style={{ width: 64, height: 64, borderRadius: 32, background: SoS.sageSoft,
          display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
          <Icon name="check" size={28} color={SoS.sage}/>
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 8 }}>
          Besked sendt
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.5, marginBottom: 20 }}>
          {recipientCount === 1 && selectedBb ? `Sendt til ${selectedBb.name}` : `Sendt til ${recipientCount} brobyggere`}
          {urgent && ' · Markeret som vigtig'}
        </div>
        <Button full onClick={onClose}>Luk</Button>
      </div>
    </div>
  );

  if (pickingBb) return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      overflowY: 'auto', zIndex: 300, display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '54px 16px 12px', background: '#fff', position: 'sticky',
        top: 0, zIndex: 10, borderBottom: `1px solid ${SoS.lineSoft}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={() => setPickingBb(false)} style={{ width: 36, height: 36,
          borderRadius: 18, background: SoS.creamDeep, border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="chevronL" size={18} color={SoS.ink} weight={2.2}/>
        </button>
        <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink }}>Vælg brobygger</div>
      </div>
      <div style={{ padding: '10px 12px 6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8,
          background: '#fff', borderRadius: SoS.r.md, padding: '10px 14px',
          border: `1px solid ${SoS.lineSoft}` }}>
          <Icon name="search" size={14} color={SoS.inkMuted}/>
          <input value={bbSearch} onChange={e => setBbSearch(e.target.value)}
            placeholder="Søg brobygger..." style={{ flex: 1, background: 'transparent',
              border: 'none', outline: 'none', fontFamily: SoS.sans, fontSize: 14 }}/>
        </div>
      </div>
      <div style={{ padding: '4px 12px 20px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {filteredBbs.map(b => {
          const statusColor = b.status === 'aktiv' ? SoS.sage : b.status === 'pause' ? '#8A6D1E' : SoS.sky;
          const statusBg = b.status === 'aktiv' ? SoS.sageSoft : b.status === 'pause' ? SoS.sun + '33' : SoS.skySoft;
          return (
            <button key={b.id} onClick={() => { setSelectedBb(b); setPickingBb(false); }} style={{
              display: 'flex', gap: 12, padding: 14, background: '#fff',
              border: `2px solid ${selectedBb?.id === b.id ? SoS.orange : SoS.lineSoft}`,
              borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left', alignItems: 'center',
            }}>
              <Avatar initials={b.avatar} bg={b.bg} size={42}/>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{b.name}</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                  {b.active} aktive forløb
                </div>
              </div>
              <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                padding: '3px 8px', borderRadius: 999, background: statusBg, color: statusColor }}>
                {b.status}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column', zIndex: 200 }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 12px', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={onClose} style={{ background: 'none', border: 'none',
          fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.inkSoft, cursor: 'pointer' }}>
          Annuller
        </button>
        <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500, color: SoS.ink }}>Ny besked</div>
        <button onClick={() => setSent(true)} disabled={!canSend} style={{
          padding: '8px 16px', background: canSend ? SoS.orange : SoS.lineSoft,
          color: canSend ? '#fff' : SoS.inkMuted, border: 'none', borderRadius: 999,
          fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: canSend ? 'pointer' : 'default',
        }}>Send</button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 20px' }}>
        {/* Scope picker */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Send til
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {SCOPES.map(s => (
              <button key={s.id} onClick={() => { setScope(s.id); if (s.id !== 'een') setSelectedBb(null); }}
                style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
                  background: scope === s.id ? SoS.orange + '12' : '#fff',
                  border: `2px solid ${scope === s.id ? SoS.orange : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left' }}>
                <div style={{ width: 10, height: 10, borderRadius: 5,
                  background: scope === s.id ? SoS.orange : SoS.lineSoft, flexShrink: 0 }}/>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{s.label}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>{s.sub}</div>
                </div>
                {scope === s.id && <Icon name="check" size={16} color={SoS.orange} weight={2.5}/>}
              </button>
            ))}
          </div>
        </div>

        {/* Picker for single bb */}
        {scope === 'een' && (
          <button onClick={() => setPickingBb(true)} style={{
            display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: 14,
            background: '#fff', border: `2px dashed ${selectedBb ? SoS.orange : SoS.line}`,
            borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left', marginBottom: 16,
          }}>
            {selectedBb
              ? <><Avatar initials={selectedBb.avatar} bg={selectedBb.bg} size={40}/>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{selectedBb.name}</div>
                  </div>
                  <Icon name="chevron" size={16} color={SoS.inkMuted}/></>
              : <><div style={{ width: 40, height: 40, borderRadius: 20, background: SoS.creamDeep,
                    display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name="users" size={20} color={SoS.inkMuted}/>
                </div>
                <span style={{ flex: 1, fontFamily: SoS.sans, fontSize: 14, color: SoS.inkMuted }}>
                  Vælg brobygger...
                </span>
                <Icon name="chevron" size={16} color={SoS.inkMuted}/></>
            }
          </button>
        )}

        {/* Recipient counter */}
        {(scope !== 'een' || selectedBb) && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px',
            background: SoS.creamDeep, borderRadius: SoS.r.md, marginBottom: 14 }}>
            <Icon name="users" size={14} color={SoS.orange}/>
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
              Sendes til <strong style={{ color: SoS.ink }}>{recipientCount} {recipientCount === 1 ? 'brobygger' : 'brobyggere'}</strong>
              {scope === 'een' && selectedBb && ` · ${selectedBb.name}`}
            </span>
          </div>
        )}

        {/* Urgent toggle */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '12px 14px', background: urgent ? SoS.orange + '12' : '#fff',
          border: `1.5px solid ${urgent ? SoS.orange : SoS.lineSoft}`,
          borderRadius: SoS.r.md, marginBottom: 16, cursor: 'pointer' }}
          onClick={() => setUrgent(!urgent)}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <Icon name="bell" size={16} color={urgent ? SoS.orange : SoS.inkMuted}/>
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                color: urgent ? SoS.orange : SoS.ink }}>Vigtig besked</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                Vises med orange markering i indbakken
              </div>
            </div>
          </div>
          <div style={{ width: 32, height: 18, borderRadius: 9,
            background: urgent ? SoS.orange : SoS.lineSoft, position: 'relative',
            transition: 'background 0.2s', flexShrink: 0 }}>
            <div style={{ position: 'absolute', top: 2, left: urgent ? 14 : 2, width: 14, height: 14,
              borderRadius: 7, background: '#fff', transition: 'left 0.2s',
              boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }}/>
          </div>
        </div>

        {/* Templates */}
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Hurtig skabelon
          </div>
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
            {SoS_TEMPLATES.map(t => (
              <button key={t.id} onClick={() => { setTemplateId(t.id); setBody(t.text); }}
                style={{ flexShrink: 0, padding: '8px 12px',
                  background: templateId === t.id ? SoS.orange : '#fff',
                  color: templateId === t.id ? '#fff' : SoS.ink,
                  border: `1.5px solid ${templateId === t.id ? SoS.orange : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 12,
                  fontWeight: 500, cursor: 'pointer', whiteSpace: 'nowrap' }}>
                {t.emoji} {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Text area */}
        <div style={{ marginBottom: 6 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Besked
          </div>
          <textarea value={body} onChange={e => { setBody(e.target.value); setTemplateId(null); }}
            placeholder="Skriv din besked her\u2026" rows={5}
            style={{ width: '100%', padding: 14, borderRadius: SoS.r.md,
              background: '#fff', border: `1.5px solid ${SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
              lineHeight: 1.5, resize: 'none', outline: 'none', boxSizing: 'border-box' }}/>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
            textAlign: 'right', marginTop: 4 }}>{body.length} tegn</div>
        </div>

        {/* Note: broadcast = read only */}
        {scope !== 'een' && (
          <div style={{ padding: 12, background: SoS.creamDeep, borderRadius: SoS.r.md,
            display: 'flex', gap: 8 }}>
            <Icon name="lock" size={14} color={SoS.orangeDeep}/>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, lineHeight: 1.5 }}>
              Fællesbeskeder er read-only for modtagerne \u2014 brobyggere kan ikke svare.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// \u2500\u2500 Thread list \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
const MessagesList = ({ onOpen, onBack, role, ownHq, onCompose }) => (
  <div style={{ position: 'absolute', inset: 0, background: SoS.cream, overflowY: 'auto', paddingBottom: 90 }}>
    <div style={{ padding: '54px 16px 10px', background: '#fff',
      borderBottom: `1px solid ${SoS.line}`,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500, color: SoS.ink }}>Beskeder</div>
      <div style={{ display: 'flex', gap: 8 }}>
        {role && role !== 'brobygger' && onCompose && (
          <button onClick={onCompose} style={{
            width: 40, height: 40, borderRadius: 20, background: SoS.orange, border: 'none',
            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: SoS.shadow.glow,
          }}><Icon name="plus" size={20} color="#fff" weight={2.5}/></button>
        )}
        <button style={{ width: 40, height: 40, borderRadius: 20, background: '#fff',
          border: 'none', boxShadow: SoS.shadow.sm, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}><Icon name="search" size={20} color={SoS.ink}/></button>
      </div>
    </div>

    <div style={{ padding: '8px 12px' }}>
      {SoS_THREADS.map(t => (
        <button key={t.id} onClick={() => onOpen(t.id)} style={{
          display: 'flex', gap: 12, width: '100%', padding: 14,
          background: t.unread ? '#fff' : 'transparent',
          border: 'none', borderRadius: SoS.r.lg, cursor: 'pointer', textAlign: 'left',
          marginBottom: 4, boxShadow: t.unread ? SoS.shadow.sm : 'none',
          alignItems: 'center', position: 'relative',
        }}>
          {t.urgent && (
            <div style={{ position: 'absolute', top: 10, left: 10, width: 6, height: 6,
              borderRadius: 3, background: SoS.orange }}/>
          )}
          <div style={{ position: 'relative' }}>
            <Avatar initials={t.avatar} bg={t.bg} size={48}/>
            {t.online && <div style={{ position: 'absolute', bottom: 0, right: 0, width: 12, height: 12,
              borderRadius: 6, background: SoS.sage, border: '2px solid #fff' }}/>}
            {t.official && <div style={{ position: 'absolute', bottom: -2, right: -2, width: 18, height: 18,
              borderRadius: 9, background: SoS.orange, border: '2px solid #fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="shield" size={10} color="#fff" weight={2.5}/>
            </div>}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: t.unread ? 700 : 600,
                color: SoS.ink }}>{t.withName}</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11,
                color: t.unread ? SoS.orange : SoS.inkMuted, fontWeight: t.unread ? 600 : 400 }}>
                {t.time}
              </div>
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
              {t.withRole}
              {t.coordinatorReplied && (
                <span style={{ marginLeft: 6, color: SoS.sage, fontWeight: 600 }}>\u00b7 Besvaret \u2713</span>
              )}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginTop: 4, gap: 8 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13,
                color: t.unread ? SoS.ink : SoS.inkSoft,
                fontWeight: t.unread ? 500 : 400,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>{t.proxied && '\u21b3 '}{t.last}</div>
              {t.unread > 0 && <div style={{ minWidth: 20, height: 20, borderRadius: 10,
                background: SoS.orange, color: '#fff', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 6px' }}>
                {t.unread}
              </div>}
            </div>
          </div>
        </button>
      ))}
    </div>

    <div style={{ margin: '8px 20px 16px', padding: 14, background: SoS.creamDeep,
      borderRadius: SoS.r.md, display: 'flex', gap: 10 }}>
      <Icon name="lock" size={16} color={SoS.orangeDeep}/>
      <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
        color: SoS.orangeDeep, lineHeight: 1.5 }}>
        Al kommunikation til borgere sker via koordinator.
      </div>
    </div>
  </div>
);

const MessageThread = ({ threadId, onBack, role }) => {
  const thread = SoS_THREADS.find(t => t.id === threadId) || SoS_THREADS[0];
  const [draft, setDraft] = React.useState('');
  const isBroadcast = !!thread.official;

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 12px', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none',
          padding: 4, cursor: 'pointer' }}>
          <Icon name="chevronL" size={22} color={SoS.ink}/>
        </button>
        <Avatar initials={thread.avatar} bg={thread.bg} size={40}/>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
            {thread.withName}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: thread.online ? SoS.sage : SoS.inkSoft }}>
            {thread.online ? '\u25cf Online' : thread.withRole}
            {thread.coordinatorReplied && (
              <span style={{ marginLeft: 6, color: SoS.sage }}>\u00b7 Besvaret \u2713</span>
            )}
          </div>
        </div>
        {thread.withRole && thread.withRole.includes('Koordinator') && (
          <a href="tel:+4523456789" style={{ width: 36, height: 36, borderRadius: 18,
            background: SoS.sageSoft, display: 'flex', alignItems: 'center',
            justifyContent: 'center', textDecoration: 'none' }}>
            <Icon name="phone" size={18} color={SoS.sage}/>
          </a>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 8px' }}>
        <div style={{ textAlign: 'center', margin: '8px 0 16px' }}>
          <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
            background: SoS.creamDeep, padding: '4px 10px', borderRadius: 999 }}>I dag</span>
        </div>

        {isBroadcast && (
          <div style={{ padding: '10px 14px', background: SoS.creamDeep,
            borderRadius: SoS.r.md, marginBottom: 12,
            display: 'flex', gap: 8, alignItems: 'flex-start' }}>
            <Icon name="lock" size={14} color={SoS.orangeDeep}/>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, lineHeight: 1.5 }}>
              F\u00e6llesbesked \u2014 du kan ikke svare p\u00e5 denne
            </div>
          </div>
        )}

        {SoS_MESSAGES.map(m => {
          const mine = m.from === 'me';
          return (
            <div key={m.id} style={{ display: 'flex',
              justifyContent: mine ? 'flex-end' : 'flex-start', marginBottom: 6 }}>
              <div style={{ maxWidth: '78%', padding: '10px 14px',
                borderRadius: mine ? `${SoS.r.lg}px ${SoS.r.lg}px 6px ${SoS.r.lg}px`
                  : `${SoS.r.lg}px ${SoS.r.lg}px ${SoS.r.lg}px 6px`,
                background: mine ? SoS.orange : '#fff', color: mine ? '#fff' : SoS.ink,
                fontFamily: SoS.sans, fontSize: 14, lineHeight: 1.4,
                boxShadow: mine ? 'none' : SoS.shadow.sm }}>
                {m.text}
                <div style={{ fontSize: 10, marginTop: 4,
                  opacity: mine ? 0.7 : 0.5, fontWeight: 400 }}>
                  {m.time}{mine && ' \u00b7 L\u00e6st'}
                </div>
              </div>
            </div>
          );
        })}

        {!isBroadcast && (
          <div style={{ display: 'flex', gap: 4, padding: '8px 14px', alignItems: 'center' }}>
            {[0,1,2].map(i => (
              <div key={i} style={{ width: 6, height: 6, borderRadius: 3,
                background: SoS.inkMuted, opacity: 0.4 }}/>
            ))}
            <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginLeft: 4 }}>
              Linda skriver...
            </span>
          </div>
        )}
      </div>

      {/* Composer */}
      {!isBroadcast ? (
        <div style={{ padding: '12px 16px 30px', background: '#fff',
          borderTop: `1px solid ${SoS.line}`,
          display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <button style={{ width: 38, height: 38, borderRadius: 19,
            background: SoS.creamDeep, border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Icon name="plus" size={20} color={SoS.ink}/>
          </button>
          <div style={{ flex: 1, background: SoS.creamDeep, borderRadius: 22,
            padding: '10px 14px', minHeight: 38 }}>
            <textarea value={draft} onChange={e => setDraft(e.target.value)}
              placeholder={`Skriv til ${thread.withName.split(' ')[0]}...`} rows={1}
              style={{ width: '100%', background: 'transparent', border: 'none',
                outline: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                resize: 'none' }}/>
          </div>
          <button style={{ width: 38, height: 38, borderRadius: 19,
            background: draft ? SoS.orange : SoS.creamDeep, border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            transition: 'background 0.2s' }}>
            <Icon name="chevron" size={18} color={draft ? '#fff' : SoS.inkMuted} weight={2.5}/>
          </button>
        </div>
      ) : (
        <div style={{ padding: '12px 16px 30px', background: '#fff',
          borderTop: `1px solid ${SoS.line}` }}>
          <div style={{ padding: '12px 14px', background: SoS.creamDeep, borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, textAlign: 'center' }}>
            F\u00e6llesbesked \u00b7 kan ikke besvares
          </div>
        </div>
      )}
    </div>
  );
};

window.MessagesList = MessagesList;
window.MessageThread = MessageThread;
window.ComposeMessage = ComposeMessage;"""

# Find the START of the old block
START_MARKER = "const MessagesList = ({ onOpen, onBack }) =>"
END_MARKER = "window.MessageThread = MessageThread;"

start_idx = html.find(START_MARKER)
if start_idx == -1:
    print("  ERROR: Ændring 5 – START marker not found")
    changes_applied.append("Ændring 5: ERROR – start not found")
else:
    end_idx = html.find(END_MARKER, start_idx)
    if end_idx == -1:
        print("  ERROR: Ændring 5 – END marker not found")
        changes_applied.append("Ændring 5: ERROR – end not found")
    else:
        end_idx += len(END_MARKER)
        html = html[:start_idx] + NEW_MESSAGING_BLOCK + html[end_idx:]
        print("  Ændring 5: OK")
        changes_applied.append("Ændring 5: OK")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 6: Opdater SoS_THREADS med coordinatorReplied og urgent
# ─────────────────────────────────────────────────────────────────────────────

# t-1: add coordinatorReplied: false, urgent: true
# t-3: add coordinatorReplied: true

def add_thread_fields(html, thread_id, fields_dict):
    start_marker = f"{{ id: '{thread_id}',"
    idx = html.find(start_marker)
    if idx == -1:
        print(f"  ERROR: thread {thread_id} not found")
        return html, False

    brace_count = 0
    i = idx
    while i < len(html):
        if html[i] == '{':
            brace_count += 1
        elif html[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                insert_pos = i
                obj_slice = html[idx:i]

                fields_str = ''
                for key, val in fields_dict.items():
                    if key not in obj_slice:
                        if isinstance(val, bool):
                            fields_str += f",\n    {key}: {'true' if val else 'false'}"
                        else:
                            fields_str += f",\n    {key}: {val}"

                if not fields_str:
                    print(f"  SKIP: thread {thread_id} already has all fields")
                    return html, False

                html = html[:insert_pos] + fields_str + '\n  ' + html[insert_pos:]
                return html, True
        i += 1
    return html, False

html, ok = add_thread_fields(html, 't-1', {'coordinatorReplied': False, 'urgent': True})
changes_applied.append(f"Ændring 6 – t-1: {'OK' if ok else 'SKIP/ERROR'}")
print(f"  Ændring 6 – t-1: {'OK' if ok else 'SKIP/ERROR'}")

html, ok = add_thread_fields(html, 't-3', {'coordinatorReplied': True})
changes_applied.append(f"Ændring 6 – t-3: {'OK' if ok else 'SKIP/ERROR'}")
print(f"  Ændring 6 – t-3: {'OK' if ok else 'SKIP/ERROR'}")

# ─────────────────────────────────────────────────────────────────────────────
# ÆNDRING 7: Wire ComposeMessage ind i AdminMobile beskeder-tab
# ─────────────────────────────────────────────────────────────────────────────

OLD_MESSAGES_TAB = """{tab === 'beskeder' && (
  <div style={{ position: 'relative', minHeight: 500 }}>
    <MessagesList onOpen={onOpenMessages}/>
  </div>
)}"""

NEW_MESSAGES_TAB = """{tab === 'beskeder' && (() => {
  const [composeOpen, setComposeOpen] = React.useState(false);
  const [threadId, setThreadId] = React.useState(null);
  return (
    <div style={{ position: 'relative', minHeight: 500 }}>
      {composeOpen && <ComposeMessage role={isAdmin ? 'admin' : 'raadgiver'} ownHq={viewingHq} onClose={() => setComposeOpen(false)}/>}
      {threadId
        ? <MessageThread threadId={threadId} onBack={() => setThreadId(null)} role={isAdmin ? 'admin' : 'raadgiver'}/>
        : <MessagesList onOpen={(id) => setThreadId(id)} role={isAdmin ? 'admin' : 'raadgiver'} ownHq={viewingHq} onCompose={() => setComposeOpen(true)}/>
      }
    </div>
  );
})()}"""

if OLD_MESSAGES_TAB in html:
    html = html.replace(OLD_MESSAGES_TAB, NEW_MESSAGES_TAB)
    print("  Ændring 7: OK (exact match)")
    changes_applied.append("Ændring 7: OK")
else:
    # Try a more flexible search
    # Look for tab === 'beskeder' with MessagesList onOpen={onOpenMessages}
    import re as re_mod
    pattern = r"\{tab === 'beskeder' && \(\s*<div[^>]*>\s*<MessagesList onOpen=\{onOpenMessages\}/>\s*</div>\s*\)\}"
    m = re_mod.search(pattern, html)
    if m:
        html = html[:m.start()] + NEW_MESSAGES_TAB + html[m.end():]
        print("  Ændring 7: OK (regex match)")
        changes_applied.append("Ændring 7: OK (regex)")
    else:
        # Dump what we find near 'beskeder'
        idx = html.find("tab === 'beskeder'")
        if idx != -1:
            snippet = html[idx:idx+300]
            print(f"  WARNING Ændring 7: Could not match – snippet:\n{snippet}")
        else:
            print("  ERROR Ændring 7: 'tab === beskeder' not found at all")
        changes_applied.append("Ændring 7: ERROR – no match")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE FILE
# ─────────────────────────────────────────────────────────────────────────────

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)

new_len = len(html)
print(f"\nFil skrevet: {PATH}")
print(f"Størrelse: {original_len} -> {new_len} bytes (diff: +{new_len - original_len})")
print("\nOpsummering:")
for c in changes_applied:
    print(f"  {c}")

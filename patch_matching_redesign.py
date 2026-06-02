import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'r', encoding='utf-8') as f:
    c = f.read()

ok = []
fail = []

def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1)
        ok.append(label)
    else:
        fail.append(label)

# ═══════════════════════════════════════════════════════════════════════════
# 1. Fix manglende `const` på TilknytBrobyggerModal + redesign hele komponenten
# ═══════════════════════════════════════════════════════════════════════════
OLD_TILKNYT = r"""TilknytBrobyggerModal = ({ menneske: m, onClose, onSaved }) => {
  const brobyggere = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');
  const [valgt, setValgt] = React.useState('');

  const handleSave = () => {
    if (!valgt) return;
    const updated = { ...(window.SoS_MENNESKER || {}) };
    updated[m.id] = { ...m, brobyggerId: valgt, status: 'aktiv', matchedAt: new Date().toISOString() };
    window.SoS_MENNESKER = updated;
    window.SoS_STORE.save('mennesker', updated);
    onSaved && onSaved();
    onClose();
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.45)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 400,
        padding: 28, boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink, marginBottom: 4 }}>
          Tilknyt brobygger
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 20 }}>
          {m.firstName} {m.lastName} afventer match
        </div>
        {brobyggere.length === 0 && (
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, textAlign: 'center', padding: '20px 0' }}>
            Ingen aktive brobyggere med ledig kapacitet
          </div>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20, maxHeight: 280, overflowY: 'auto' }}>
          {brobyggere.map(b => {
            const myAppts = (window.SoS_APPOINTMENTS_BUSY || []).filter(a => a.brobyggerId === b.id);
            const aktive = myAppts.filter(a => a.status === 'confirmed').length;
            return (
              <button key={b.id} onClick={() => setValgt(b.id)}
                style={{ display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left',
                  padding: '10px 14px', borderRadius: SoS.r.md, cursor: 'pointer',
                  border: `2px solid ${valgt === b.id ? SoS.accent : SoS.line}`,
                  background: valgt === b.id ? SoS.accent + '12' : SoS.paper }}>
                <div style={{ width: 36, height: 36, borderRadius: 18, background: b.bg || SoS.accent,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
                  {b.avatar}
                </div>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
                    color: valgt === b.id ? SoS.accent : SoS.ink }}>{b.name}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 1 }}>
                    {aktive} aktive aftaler
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={onClose}
            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,
              background: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer' }}>
            Annuller
          </button>
          <button onClick={handleSave} disabled={!valgt}
            style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',
              background: valgt ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,
              fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>
            Tilknyt brobygger
          </button>
        </div>
      </div>
    </div>
  );
};"""

NEW_TILKNYT = r"""const TilknytBrobyggerModal = ({ menneske: m, onClose, onSaved }) => {
  const alle    = (window.SoS_BROBYGGERE || []).filter(b => b.status === 'aktiv');
  const ledige  = alle.filter(b => b.openShifts > 0);
  const optaget = alle.filter(b => b.openShifts === 0);
  const [valgt, setValgt] = React.useState('');
  const [mode,  setMode]  = React.useState(ledige.length > 0 ? 'ledig' : 'foresporg');
  const [sent,  setSent]  = React.useState(false);
  const visListe = mode === 'ledig' ? ledige : optaget;

  const handleMatch = () => {
    if (!valgt) return;
    const updated = { ...(window.SoS_MENNESKER || {}) };
    updated[m.id] = { ...updated[m.id], brobyggerId: valgt, status: 'aktiv',
      matchedAt: new Date().toISOString().slice(0, 10), matchAnmodning: null };
    window.SoS_MENNESKER = updated;
    window.SoS_STORE?.save('mennesker', updated);
    onSaved?.({ brobyggerId: valgt });
    onClose();
  };

  const handleForesporg = () => {
    if (!valgt) return;
    const updated = { ...(window.SoS_MENNESKER || {}) };
    updated[m.id] = { ...updated[m.id],
      matchAnmodning: { brobyggerId: valgt, sendt: new Date().toISOString(), status: 'afventer' } };
    window.SoS_MENNESKER = updated;
    window.SoS_STORE?.save('mennesker', updated);
    const nk = 'sos_notifikationer';
    const ns = JSON.parse(localStorage.getItem(nk) || '[]');
    ns.push({ id: 'n-' + Date.now(), type: 'match-anmodning', read: false,
      createdAt: new Date().toISOString(),
      text: `Forespørgsel: ${m.firstName} ${m.lastName} søger en brobygger`,
      brobyggerId: valgt });
    localStorage.setItem(nk, JSON.stringify(ns));
    onSaved?.({ matchAnmodning: true });
    setSent(true);
  };

  if (sent) {
    const bb = alle.find(b => b.id === valgt);
    return (
      <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.45)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 380,
          padding: 36, textAlign: 'center', boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>
          <div style={{ fontSize: 44, marginBottom: 12 }}>📨</div>
          <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink, marginBottom: 8 }}>
            Forespørgsel sendt!
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 24 }}>
            {bb?.name} modtager en besked og kan acceptere eller afvise.
          </div>
          <button onClick={onClose} style={{ padding: '10px 32px', borderRadius: SoS.r.md,
            background: SoS.accent, color: '#fff', border: 'none',
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
            OK
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.45)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: SoS.paper, borderRadius: SoS.r.lg, width: '100%', maxWidth: 440,
        padding: 28, boxShadow: '0 8px 40px rgba(0,0,0,0.18)' }}>

        {/* Header */}
        <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: SoS.ink, marginBottom: 4 }}>
          Find brobygger
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 16 }}>
          {m.firstName} {m.lastName}
          {m.behovUrgency === 'snarest' && <span style={{ marginLeft: 8, color: SoS.rose, fontWeight: 600 }}>· Haster</span>}
          {m.behovUrgency === 'uge'     && <span style={{ marginLeft: 8, color: SoS.amber, fontWeight: 600 }}>· Inden for en uge</span>}
        </div>

        {/* Mode-toggle: Ledig / Forespørg */}
        <div style={{ display: 'flex', borderRadius: SoS.r.sm, overflow: 'hidden',
          border: `1px solid ${SoS.line}`, marginBottom: 16 }}>
          <button onClick={() => { setMode('ledig'); setValgt(''); }}
            style={{ flex: 1, padding: '8px 0', border: 'none', cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
              background: mode === 'ledig' ? SoS.accent : SoS.paper,
              color: mode === 'ledig' ? '#fff' : SoS.inkSoft }}>
            Ledige ({ledige.length})
          </button>
          <button onClick={() => { setMode('foresporg'); setValgt(''); }}
            style={{ flex: 1, padding: '8px 0', border: 'none', borderLeft: `1px solid ${SoS.line}`,
              cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
              background: mode === 'foresporg' ? '#D97706' : SoS.paper,
              color: mode === 'foresporg' ? '#fff' : SoS.inkSoft }}>
            Forespørg optaget ({optaget.length})
          </button>
        </div>

        {/* Info-banner for forespørg-mode */}
        {mode === 'foresporg' && (
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: '#92400E',
            background: '#FEF3C7', borderRadius: SoS.r.sm, padding: '8px 12px', marginBottom: 12 }}>
            Disse brobyggere har ingen ledige tider, men kan forespørges.
            De modtager en notifikation og vælger selv om de vil tage sagen.
          </div>
        )}
        {mode === 'ledig' && ledige.length === 0 && (
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted,
            textAlign: 'center', padding: '16px 0' }}>
            Ingen ledige brobyggere lige nu.
            <button onClick={() => setMode('foresporg')}
              style={{ display: 'block', margin: '8px auto 0', background: 'none', border: 'none',
                fontFamily: SoS.sans, fontSize: 13, color: '#D97706', cursor: 'pointer',
                textDecoration: 'underline' }}>
              Forespørg en optaget brobygger →
            </button>
          </div>
        )}

        {/* Brobygger-liste */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20,
          maxHeight: 260, overflowY: 'auto' }}>
          {visListe.map(b => {
            const myAppts = (window.SoS_APPOINTMENTS_BUSY || [])
              .filter(a => a.brobyggerId === b.id && a.status === 'confirmed');
            const sel = valgt === b.id;
            const selColor = mode === 'foresporg' ? '#D97706' : SoS.accent;
            return (
              <button key={b.id} onClick={() => setValgt(sel ? '' : b.id)}
                style={{ display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left',
                  padding: '10px 14px', borderRadius: SoS.r.md, cursor: 'pointer',
                  border: `2px solid ${sel ? selColor : SoS.line}`,
                  background: sel ? selColor + '12' : SoS.paper }}>
                <div style={{ width: 36, height: 36, borderRadius: 18, background: b.bg || SoS.accent,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
                  {b.avatar}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
                    color: sel ? selColor : SoS.ink }}>{b.name}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 1 }}>
                    {myAppts.length} aktive aftaler
                    {mode === 'ledig' && ` · ${b.openShifts} ledig${b.openShifts !== 1 ? 'e' : ''} tid${b.openShifts !== 1 ? 'er' : ''}`}
                  </div>
                </div>
                {mode === 'ledig' && (
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 600,
                    color: SoS.green, background: SoS.green + '18', borderRadius: SoS.r.sm,
                    padding: '3px 8px', flexShrink: 0 }}>
                    {b.openShifts} ledig{b.openShifts !== 1 ? 'e' : ''}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Action-knapper */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={onClose}
            style={{ flex: 1, padding: '11px 0', borderRadius: SoS.r.md, border: `1px solid ${SoS.line}`,
              background: 'none', fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, cursor: 'pointer' }}>
            Annuller
          </button>
          {mode === 'ledig' ? (
            <button onClick={handleMatch} disabled={!valgt}
              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',
                background: valgt ? SoS.accent : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,
                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>
              Match med brobygger
            </button>
          ) : (
            <button onClick={handleForesporg} disabled={!valgt}
              style={{ flex: 2, padding: '11px 0', borderRadius: SoS.r.md, border: 'none',
                background: valgt ? '#D97706' : SoS.lineSoft, fontFamily: SoS.sans, fontSize: 14,
                fontWeight: 600, color: valgt ? '#fff' : SoS.inkMuted, cursor: valgt ? 'pointer' : 'default' }}>
              Send forespørgsel
            </button>
          )}
        </div>
      </div>
    </div>
  );
};"""

sub(OLD_TILKNYT, NEW_TILKNYT, "TilknytBrobyggerModal: fix const + redesign ledig/forespørg")

# ═══════════════════════════════════════════════════════════════════════════
# 2. IntakeFlow: tilføj behovUrgency state
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [kpTlf,       setKpTlf]       = React.useState('');
  const canFinish = consent;""",
    """  const [kpTlf,       setKpTlf]       = React.useState('');
  const [behovUrgency, setBehovUrgency] = React.useState('');
  const canFinish = consent;""",
    "IntakeFlow: behovUrgency state"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. IntakeFlow handleFinish: gem behovUrgency på nye mennesker
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """      consentAt:     new Date().toISOString(),
      brobyggerId:   null,
    };""",
    """      consentAt:     new Date().toISOString(),
      brobyggerId:   null,
      behovUrgency:  behovUrgency || null,
    };""",
    "IntakeFlow handleFinish: behovUrgency på nyt menneske"
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. IntakeFlow step 1 UI: tilføj "Hvornår er der brug for hjælp?" sektion
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """                )}
              </div>
            </div>
          </>
        )}

                {/* ── STEP 2: Behov ── */}""",
    """                )}
              </div>
            </div>

            {/* ── Hvornår er der brug for hjælp ── */}
            <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '14px 16px',
              border: `1px solid ${SoS.lineSoft}` }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                color: SoS.ink, marginBottom: 10 }}>
                Hvornår er der brug for hjælp?{' '}
                <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, fontWeight: 400 }}>
                  — valgfri
                </span>
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {[
                  { id: 'snarest',    label: 'Snarest muligt', sub: '2–3 dage',  clr: SoS.rose },
                  { id: 'uge',        label: 'Inden for en uge', sub: '7 dage',   clr: SoS.amber },
                  { id: 'fleksibelt', label: 'Fleksibelt',     sub: 'Ingen hast', clr: SoS.green },
                ].map(u => (
                  <button key={u.id}
                    onClick={() => setBehovUrgency(behovUrgency === u.id ? '' : u.id)}
                    style={{ padding: '6px 14px', borderRadius: SoS.r.sm, cursor: 'pointer',
                      fontFamily: SoS.sans, fontSize: 12,
                      background: behovUrgency === u.id ? u.clr + '20' : '#fff',
                      border: `1.5px solid ${behovUrgency === u.id ? u.clr : SoS.line}`,
                      color: behovUrgency === u.id ? u.clr : SoS.inkSoft,
                      fontWeight: behovUrgency === u.id ? 600 : 400,
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <span>{u.label}</span>
                    <span style={{ fontSize: 10, opacity: 0.7 }}>{u.sub}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

                {/* ── STEP 2: Behov ── */}""",
    "IntakeFlow step 1: urgency-vælger"
)

# ═══════════════════════════════════════════════════════════════════════════
# 5. DesktopMennesker-banner: vis forespørgsel-afventer tilstand
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """          if (selected.status === 'afventer' || selected.status === 'venter') return (
            <div style={{ padding: '8px 16px', background: SoS.amberSoft || '#FFF8E1',
              borderBottom: `1px solid ${SoS.line}`, fontFamily: SoS.sans, fontSize: 12,
              color: SoS.amber, display: 'flex', alignItems: 'center', gap: 6 }}>
              ⏳ Afventer match med brobygger
            </div>
          );
          return null;
        })()}""",
    """          const anm = selected.matchAnmodning;
          if (anm?.status === 'afventer') {
            const anmBb = (window.SoS_BROBYGGERE || []).find(b => b.id === anm.brobyggerId);
            return (
              <div style={{ padding: '8px 16px', background: '#EEF2FF',
                borderBottom: `1px solid ${SoS.line}`, fontFamily: SoS.sans, fontSize: 12,
                color: '#4338CA', display: 'flex', alignItems: 'center', gap: 6 }}>
                ✉️ Forespørgsel sendt til {anmBb?.name || 'brobygger'} · Afventer svar
              </div>
            );
          }
          if (selected.status === 'afventer' || selected.status === 'venter') return (
            <div style={{ padding: '8px 16px', background: SoS.amberSoft || '#FFF8E1',
              borderBottom: `1px solid ${SoS.line}`, fontFamily: SoS.sans, fontSize: 12,
              color: SoS.amber, display: 'flex', alignItems: 'center', gap: 6 }}>
              ⏳ Afventer match med brobygger
            </div>
          );
          return null;
        })()}""",
    "DesktopMennesker: forespørgsel-afventer banner"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f'OK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

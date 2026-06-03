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
# 1. AppointmentDetailScreen — vis kontaktperson + aftaledetaljer
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """              action={<Icon name="phone" size={16} color={SoS.orange} />} multiline
            />
          </>
        )}
      </div>

      {/* Brobygningsstige */}""",
    """              action={<Icon name="phone" size={16} color={SoS.orange} />} multiline
            />
            {menneske.kontaktperson?.navn && (
              <InfoRow icon="user" label="Kontaktperson"
                value={<div>
                  <div>{menneske.kontaktperson.navn}</div>
                  {menneske.kontaktperson.relation && (
                    <div style={{ fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                      {menneske.kontaktperson.relation}
                    </div>
                  )}
                </div>}
                action={menneske.kontaktperson.tlf
                  ? <Icon name="phone" size={16} color={SoS.sky}/>
                  : null}
                multiline
              />
            )}
          </>
        )}
      </div>

      {/* Aftale-detaljer */}
      {(appt.fremmoedeType || appt.aktivitetsTid || appt.aftaleForm === 'gentagende') && (
        <div style={{ padding: '0 16px 16px' }}>
          <SectionHead title="Aftaledetaljer" />
          <div style={{ background: '#fff', borderRadius: SoS.r.lg,
            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden' }}>
            {appt.fremmoedeType && (
              <InfoRow icon="pin" label="Fremmøde"
                value={
                  appt.fremmoedeType === 'hjemmet' ? '🏠 Følges fra hjemmet' :
                  appt.fremmoedeType === 'sted'    ? '📍 Mødes på stedet' :
                                                     '🤝 Mødes hos byggeren'
                } />
            )}
            {appt.aktivitetsTid && (
              <InfoRow icon="clock" label="Tidspunkt for aktivitet" value={appt.aktivitetsTid} />
            )}
            {appt.aftaleForm === 'gentagende' && (
              <InfoRow icon="calendar" label="Gentagelse"
                value={
                  appt.gentagelse === 'ugentligt'   ? '↻ Ugentligt' :
                  appt.gentagelse === 'hver14dag'   ? '↻ Hver 14. dag' :
                  appt.gentagelse === 'maanedligt'  ? '↻ Månedligt' :
                                                      '↻ Variabelt'
                } />
            )}
          </div>
        </div>
      )}

      {/* Brobygningsstige */}""",
    "AppointmentDetailScreen: kontaktperson + aftaledetaljer"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2a. MessagesList — tilføj sosNotifs state + accept/decline handlers
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """  const [expanded, setExpanded]   = React.useState(null); // notif-id der vises udvidet
  const NOTIF_ICON  = { match: 'match', reminder: 'clock', message: 'bell' };""",
    """  const [expanded, setExpanded]   = React.useState(null); // notif-id der vises udvidet
  const [sosNotifs, setSosNotifs] = React.useState(() => JSON.parse(localStorage.getItem('sos_notifikationer') || '[]'));
  const [sosBesk,   setSosBesk]   = React.useState(() => JSON.parse(localStorage.getItem('sos_beskeder')      || '[]'));

  const handleAcceptMatch = (n) => {
    const upd = { ...(window.SoS_MENNESKER || {}) };
    const mEntry = Object.values(upd).find(m => m.matchAnmodning?.brobyggerId === n.brobyggerId);
    if (mEntry) {
      upd[mEntry.id] = { ...upd[mEntry.id], brobyggerId: n.brobyggerId, matchAnmodning: null };
      window.SoS_MENNESKER = upd;
      window.SoS_STORE?.save('mennesker', upd);
    }
    const ns = sosNotifs.map(x => x.id === n.id ? { ...x, status: 'accepteret', read: true } : x);
    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
  };
  const handleDeclineMatch = (n) => {
    const upd = { ...(window.SoS_MENNESKER || {}) };
    const mEntry = Object.values(upd).find(m => m.matchAnmodning?.brobyggerId === n.brobyggerId);
    if (mEntry) {
      upd[mEntry.id] = { ...upd[mEntry.id],
        matchAnmodning: { ...upd[mEntry.id].matchAnmodning, status: 'afvist' } };
      window.SoS_MENNESKER = upd;
      window.SoS_STORE?.save('mennesker', upd);
    }
    const ns = sosNotifs.map(x => x.id === n.id ? { ...x, status: 'afvist', read: true } : x);
    setSosNotifs(ns); localStorage.setItem('sos_notifikationer', JSON.stringify(ns));
  };

  const NOTIF_ICON  = { match: 'match', reminder: 'clock', message: 'bell' };""",
    "MessagesList: sosNotifs + sosBesk state + accept/decline handlers"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2b. MessagesList — vis sosNotifs match-anmodninger efter SoS_NOTIFICATIONS.map
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """        })}
      </div>
    )}

    {/* ── BESKEDER ── */}
    {tab === 'beskeder' && (
    <div style={{ padding: '8px 12px' }}>
      {visibleThreads.map(t => (""",
    """        })}

        {/* Forespørgsler fra koordinatorer (sos_notifikationer) */}
        {sosNotifs.filter(n => n.type === 'match-anmodning').map(n => {
          const bb = (window.SoS_BROBYGGERE || []).find(b => b.id === n.brobyggerId);
          const isHandled = n.status === 'accepteret' || n.status === 'afvist';
          return (
            <div key={n.id} style={{
              marginBottom: 8, background: '#fff', borderRadius: SoS.r.lg,
              boxShadow: !isHandled ? SoS.shadow.sm : 'none',
              border: `1px solid ${isHandled ? 'transparent' : SoS.lineSoft}`,
            }}>
              <div style={{ display: 'flex', gap: 12, padding: '14px 16px', alignItems: 'flex-start' }}>
                <div style={{ width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                  background: SoS.orange + '18', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon name="match" size={20} color={SoS.orange}/>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: isHandled ? 500 : 700, color: SoS.ink, marginBottom: 2 }}>
                    Forespørgsel om brobygning
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.4 }}>
                    {n.text}
                  </div>
                  {!isHandled && (
                    <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                      <button onClick={() => handleAcceptMatch(n)} style={{
                        flex: 1, padding: '9px 0', background: SoS.sage, color: '#fff',
                        border: 'none', borderRadius: SoS.r.sm,
                        fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                        Acceptér
                      </button>
                      <button onClick={() => handleDeclineMatch(n)} style={{
                        flex: 1, padding: '9px 0', background: SoS.creamDeep, color: SoS.ink,
                        border: 'none', borderRadius: SoS.r.sm,
                        fontFamily: SoS.sans, fontSize: 13, cursor: 'pointer' }}>
                        Afvis
                      </button>
                    </div>
                  )}
                  {isHandled && (
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, marginTop: 6,
                      color: n.status === 'accepteret' ? SoS.sage : SoS.inkMuted,
                      fontWeight: n.status === 'accepteret' ? 600 : 400 }}>
                      {n.status === 'accepteret' ? 'Accepteret ✓' : 'Afvist'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    )}

    {/* ── BESKEDER ── */}
    {tab === 'beskeder' && (
    <div style={{ padding: '8px 12px' }}>
      {role === 'brobygger' && sosBesk.length === 0 && (
        <div style={{ padding: '40px 0', textAlign: 'center',
          fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
          Ingen beskeder endnu
        </div>
      )}
      {role === 'brobygger' && sosBesk.map((m, _i) => (
        <div key={m.id} style={{ display: 'flex', gap: 10, padding: '8px 0',
          flexDirection: m.fra === 'admin' ? 'row' : 'row-reverse', alignItems: 'flex-end' }}>
          <Avatar initials={m.fra === 'admin' ? 'SS' : 'BB'} bg={m.fra === 'admin' ? SoS.accent : SoS.orange} size={30}/>
          <div style={{ maxWidth: '80%' }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 3,
              textAlign: m.fra === 'admin' ? 'left' : 'right' }}>
              {m.fra === 'admin' ? 'Social Sundhed' : 'Dig'} · {new Date(m.sendt).toLocaleTimeString('da-DK', { hour: '2-digit', minute: '2-digit' })}
            </div>
            <div style={{
              background: m.fra === 'admin' ? '#fff' : SoS.accent,
              color: m.fra === 'admin' ? SoS.ink : '#fff',
              border: m.fra === 'admin' ? `1px solid ${SoS.lineSoft}` : 'none',
              borderRadius: SoS.r.md, padding: '8px 12px',
              fontFamily: SoS.sans, fontSize: 13, lineHeight: 1.45,
              display: 'inline-block',
            }}>{m.tekst}</div>
          </div>
        </div>
      ))}
      {role !== 'brobygger' && visibleThreads.map(t => (""",
    "MessagesList: sosNotifs + sosBesk rendering i tabs"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2c. MessagesList — luk beskeder-tab ternary (tilføj ) efter visibleThreads.map blok)
# ═══════════════════════════════════════════════════════════════════════════
# Find the closing of visibleThreads.map which ends with ))} then </div> )}
# The lock-message banner is just before the closing, so we use that as anchor
sub(
    """    {tab === 'beskeder' && (
      <div style={{ margin: '0 16px 16px', padding: 14, background: SoS.creamDeep,
        borderRadius: SoS.r.md, display: 'flex', gap: 10, flexShrink: 0 }}>
        <Icon name="lock" size={16} color={SoS.orangeDeep}/>
        <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
          color: SoS.orangeDeep, lineHeight: 1.5 }}>
          Al kommunikation til mennesker sker via koordinator.
        </div>
      </div>
    )}
  </div>
  );
};""",
    """    {tab === 'beskeder' && role !== 'brobygger' && (
      <div style={{ margin: '0 16px 16px', padding: 14, background: SoS.creamDeep,
        borderRadius: SoS.r.md, display: 'flex', gap: 10, flexShrink: 0 }}>
        <Icon name="lock" size={16} color={SoS.orangeDeep}/>
        <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11,
          color: SoS.orangeDeep, lineHeight: 1.5 }}>
          Al kommunikation til mennesker sker via koordinator.
        </div>
      </div>
    )}
  </div>
  );
};""",
    "MessagesList: skjul koordinator-banner for brobygger"
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. DesktopKalender — saveAppt med gentagende serie
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """const saveAppt = (data) => {
    const newList = data.id
      ? appointments.map(a => a.id === data.id ? data : a)
      : [...appointments, { ...data, id: 'a-' + Date.now() }];
    window.SoS_APPOINTMENTS_BUSY = newList;
    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);
    setAppts(newList);
    setApptModal(null);
  };""",
    """const saveAppt = (data) => {
    let newItems = [];
    if (data.id) {
      // Opdatering af eksisterende aftale (ingen serie)
      const newList = appointments.map(a => a.id === data.id ? data : a);
      window.SoS_APPOINTMENTS_BUSY = newList;
      if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);
      setAppts(newList);
      setApptModal(null);
      return;
    }
    const base = { ...data, id: 'a-' + Date.now() };
    newItems = [base];
    if (data.aftaleForm === 'gentagende' && data.gentagelse && data.gentagelse !== 'variabelt') {
      const shiftDate = (iso, days, months) => {
        const d = new Date(iso);
        if (days)   d.setDate(d.getDate() + days);
        if (months) d.setMonth(d.getMonth() + months);
        return d.toISOString().slice(0, 10);
      };
      const steps = data.gentagelse === 'ugentligt'  ? { days: 7,  count: 7 } :
                    data.gentagelse === 'hver14dag'  ? { days: 14, count: 7 } :
                    /* maanedligt */                   { months: 1, count: 5 };
      for (let i = 1; i <= steps.count; i++) {
        newItems.push({ ...base,
          id:   'a-' + (Date.now() + i),
          date: shiftDate(base.date, steps.days ? steps.days * i : 0, steps.months ? steps.months * i : 0),
        });
      }
    }
    const newList = [...appointments, ...newItems];
    window.SoS_APPOINTMENTS_BUSY = newList;
    if (window.SoS_STORE) window.SoS_STORE.save('appointments', newList);
    setAppts(newList);
    setApptModal(null);
  };""",
    "saveAppt: generer serie for gentagende aftaler"
)

# ═══════════════════════════════════════════════════════════════════════════
# 5. Fjern historik fra mobil screen-renderer
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """{screen === "historik" && <HistorikScreen history={isNew ? [] : SoS_HISTORIK} onOpenMenneske={(id) => { const h = SoS_HISTORIK.find(x => x.menneskeId === id); if (h) openAppt(h.id); }} />}""",
    """{/* historik-tab fjernet — info vises under aftale-detaljer */}""",
    "Fjern HistorikScreen fra mobil screen-renderer"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix: tjek for problematisk \n i .join() ─────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print("CRLF-fix: .join('\\n') erstattet med .join('\\\\n')")
else:
    print("CRLF-check: OK (ingen problematisk .join)")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

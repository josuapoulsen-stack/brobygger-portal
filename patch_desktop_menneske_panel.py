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
# 1. Indsæt DesktopMenneskeDetailPanel komponent FØR DesktopMennesker
# ═══════════════════════════════════════════════════════════════════════════
NEW_COMPONENT = """const DesktopMenneskeDetailPanel = ({ menneske: m, onClose, onRefresh }) => {
  const type        = SoS_TYPER[m.type];
  const [activeTab,   setActiveTab]   = React.useState(0);
  const [addOpen,     setAddOpen]     = React.useState(false);
  const [afslutOpen,  setAfslutOpen]  = React.useState(false);
  const [tilknytOpen, setTilknytOpen] = React.useState(false);
  const [localKey,    setLocalKey]    = React.useState(0);

  const stats      = React.useMemo(() => calcMenneskeStats(m.id), [m.id, localKey]);
  const niveauMeta = INDSATS_META[stats.indsatsniveau];
  const recentKont = React.useMemo(
    () => [...stats.alle].sort((a, b) => b.dato.localeCompare(a.dato)).slice(0, 5),
    [stats.alle]
  );
  const mennAppts  = React.useMemo(
    () => (window.SoS_APPOINTMENTS_BUSY || [])
            .filter(a => a.menneskeId === m.id)
            .sort((a, b) => b.date.localeCompare(a.date)),
    [m.id, localKey]
  );

  const handleSaved = () => { setLocalKey(k => k + 1); onRefresh?.(); };
  const today       = new Date().toISOString().slice(0, 10);
  const TABS        = ['Oversigt', 'Tidslinje', 'Aftaler', 'Detaljer'];

  // Sektion-overskrift — simpel hjælpefunktion (ikke komponent)
  const sh = txt => (
    <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, color: SoS.inkMuted,
      letterSpacing: 0.9, textTransform: 'uppercase', marginBottom: 10 }}>{txt}</div>
  );

  return (
    <>
      {/* ── Stats strip ───────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr',
        borderBottom: `1px solid ${SoS.line}`, background: SoS.surface }}>
        {[
          { v: stats.antalKontakter,    l: 'Kontakter' },
          { v: stats.antalGennemfoerte, l: 'Gennemført' },
          { v: stats.antalFolgeskaber,  l: 'Følgeskaber' },
        ].map((s, i) => (
          <div key={i} style={{ textAlign: 'center', padding: '10px 8px',
            borderRight: `1px solid ${SoS.line}` }}>
            <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 600,
              color: SoS.ink, lineHeight: 1 }}>{s.v}</div>
            <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted, marginTop: 3 }}>{s.l}</div>
          </div>
        ))}
        <div style={{ textAlign: 'center', padding: '10px 8px' }}>
          <div style={{ display: 'inline-block', background: niveauMeta.color,
            color: '#fff', borderRadius: 4, padding: '2px 8px',
            fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, lineHeight: 1.6 }}>
            {niveauMeta.label}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted, marginTop: 3 }}>
            Indsats
          </div>
        </div>
      </div>

      {/* ── Tab-bar ───────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`, paddingLeft: 6 }}>
        {TABS.map((tab, i) => (
          <button key={tab} onClick={() => setActiveTab(i)} style={{
            padding: '10px 14px', border: 'none', cursor: 'pointer',
            background: 'transparent', outline: 'none',
            fontFamily: SoS.sans, fontSize: 12,
            fontWeight: activeTab === i ? 700 : 400,
            color: activeTab === i ? SoS.accent : SoS.inkSoft,
            borderBottom: `2px solid ${activeTab === i ? SoS.accent : 'transparent'}`,
            marginBottom: -1,
          }}>
            {tab}
            {tab === 'Aftaler' && mennAppts.length > 0 && (
              <span style={{ marginLeft: 5, background: SoS.lineSoft, borderRadius: 8,
                padding: '1px 5px', fontSize: 10, color: SoS.inkMuted }}>
                {mennAppts.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Tab content ───────────────────────────────────────────────── */}
      <div style={{ padding: '16px 18px 80px', background: SoS.paper }}>

        {/* ── OVERSIGT ── */}
        {activeTab === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

            {/* Indsatsniveau-badge */}
            <div style={{ background: niveauMeta.color + '18',
              border: `1px solid ${niveauMeta.color}40`,
              borderRadius: SoS.r.md, padding: '10px 14px',
              display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 10, height: 10, borderRadius: 5,
                background: niveauMeta.color, flexShrink: 0 }}/>
              <div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700,
                  color: niveauMeta.color }}>{niveauMeta.label}</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 1 }}>
                  {stats.antalFolgeskaber} følgeskaber registreret
                </div>
              </div>
            </div>

            {/* Behov */}
            {m.needs && m.needs.length > 0 && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                border: `1px solid ${SoS.lineSoft}` }}>
                {sh('Behov')}
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {m.needs.map((n, i) => <Pill key={i} bg={type.soft} color={type.color}>{n}</Pill>)}
                </div>
              </div>
            )}

            {/* Koordinator */}
            {m.contact && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                border: `1px solid ${SoS.lineSoft}` }}>
                {sh('Koordinator')}
                <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                  {m.contact.name}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 1 }}>
                  {m.contact.role}
                </div>
                {m.contact.phone && (
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.orange,
                    fontWeight: 600, marginTop: 6 }}>{m.contact.phone}</div>
                )}
              </div>
            )}

            {/* Kontaktperson */}
            {m.kontaktperson && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                border: `1px solid ${SoS.lineSoft}` }}>
                {sh('Kontaktperson')}
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginBottom: 4 }}>
                  {({
                    plejepersonale: 'Plejepersonale', kommunal: 'Kommunal socialrådgiver',
                    paaroerende: 'Pårørende', ven: 'Ven / bekendt',
                    laege: 'Læge / sygeplejerske', frivillig: 'Frivilligkoordinator', anden: 'Anden',
                  })[m.kontaktperson.type] || m.kontaktperson.type}
                </div>
                {m.kontaktperson.navn && (
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                    {m.kontaktperson.navn}
                  </div>
                )}
                {m.kontaktperson.tlf && (
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.orange, marginTop: 4 }}>
                    {m.kontaktperson.tlf}
                  </div>
                )}
              </div>
            )}

            {/* Seneste kontakter */}
            {recentKont.length > 0 && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                border: `1px solid ${SoS.lineSoft}` }}>
                {sh('Seneste kontakter')}
                {recentKont.map((k, i) => {
                  const meta   = KONTAKT_TYPE_META[k.type] || KONTAKT_TYPE_META['andet'];
                  const sColor = k.status === 'gennemfoert' ? SoS.sage
                    : k.status === 'aflyst' ? SoS.orange : '#D64545';
                  const sLabel = k.status === 'gennemfoert' ? 'Gennemført'
                    : k.status === 'aflyst' ? 'Aflyst' : 'Udeblev';
                  return (
                    <div key={k.id} style={{ display: 'flex', gap: 10, padding: '7px 0',
                      borderBottom: i < recentKont.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
                      alignItems: 'center' }}>
                      <div style={{ width: 8, height: 8, borderRadius: 4,
                        background: meta.color, flexShrink: 0 }}/>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 12,
                          fontWeight: 600, color: SoS.ink }}>{meta.label}</span>
                        {k.note && (
                          <span style={{ fontFamily: SoS.sans, fontSize: 12,
                            color: SoS.inkSoft, marginLeft: 6 }}> · {k.note}</span>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 11,
                          fontWeight: 600, color: sColor }}>{sLabel}</span>
                        <span style={{ fontFamily: SoS.sans, fontSize: 11,
                          color: SoS.inkMuted }}>{k.dato}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

          </div>
        )}

        {/* ── TIDSLINJE ── */}
        {activeTab === 1 && <MenneskeTimelineInline m={m} />}

        {/* ── AFTALER ── */}
        {activeTab === 2 && (
          <div>
            {mennAppts.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0',
                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen aftaler registreret for denne person
              </div>
            ) : mennAppts.map((a, i) => {
              const bb     = (window.SoS_BROBYGGERE || []).find(b => b.id === a.brobyggerId);
              const isPast = a.date < today;
              const apptSt = a.status === 'confirmed'
                ? { l: 'Bekræftet', c: SoS.sage }
                : a.status === 'aflyst'
                ? { l: 'Aflyst',    c: '#D64545' }
                : { l: 'Afventer',  c: SoS.orange };
              return (
                <div key={a.id} style={{ display: 'flex', gap: 12, padding: '10px 0',
                  borderBottom: i < mennAppts.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
                  opacity: isPast ? 0.72 : 1 }}>
                  <div style={{ width: 48, flexShrink: 0, textAlign: 'center',
                    background: isPast ? SoS.creamDeep : SoS.orange + '14',
                    borderRadius: SoS.r.sm, padding: '6px 4px' }}>
                    <div style={{ fontFamily: SoS.mono, fontSize: 12, fontWeight: 700,
                      color: isPast ? SoS.inkMuted : SoS.orange }}>
                      {a.date.slice(5).replace('-', '/')}
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 10, color: SoS.inkMuted }}>
                      {a.start}
                    </div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                      color: SoS.ink }}>
                      {a.activity}
                      {a.aftaleForm === 'gentagende' && (
                        <span style={{ marginLeft: 6, fontFamily: SoS.mono,
                          fontSize: 11, color: SoS.orange }}>↻</span>
                      )}
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>
                      {a.location}{bb ? ` · ${bb.name}` : ''}
                    </div>
                  </div>
                  <div style={{ flexShrink: 0, alignSelf: 'center' }}>
                    <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                      color: apptSt.c }}>{apptSt.l}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ── DETALJER ── */}
        {activeTab === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

            {/* Information */}
            <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
              border: `1px solid ${SoS.lineSoft}` }}>
              {sh('Information')}
              {[
                { l: 'Alder',      v: m.age ? m.age + ' år' : null },
                { l: 'Adresse',    v: m.address },
                { l: 'Postnummer', v: m.postnummer },
                { l: 'Sprog',      v: m.language },
                { l: 'Køn',        v: m.koen && m.koen !== 'vil-ikke-oplyse'
                    ? ({ mand: 'Mand', kvinde: 'Kvinde', 'non-binaer': 'Non-binær' }[m.koen] || m.koen)
                    : null },
              ].filter(r => r.v).map((r, i, arr) => (
                <div key={i} style={{ display: 'flex', gap: 8, padding: '6px 0',
                  borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted,
                    width: 90, flexShrink: 0 }}>{r.l}</span>
                  <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>{r.v}</span>
                </div>
              ))}
              {m.helbredsKategorier && m.helbredsKategorier.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 10,
                  paddingTop: 10, borderTop: `1px solid ${SoS.lineSoft}` }}>
                  {m.helbredsKategorier.map(kid => {
                    const kat = (window.HELBREDS_KATEGORIER || []).find(k => k.id === kid);
                    return kat ? (
                      <Pill key={kid} bg={SoS.orange + '12'} color={SoS.orangeDeep}>{kat.label}</Pill>
                    ) : null;
                  })}
                </div>
              )}
              {m.health && (window.SoS_SETTINGS || {}).visHelbredsforhold !== false && (
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
                  lineHeight: 1.5, marginTop: 10, paddingTop: 10,
                  borderTop: `1px solid ${SoS.lineSoft}` }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                    color: SoS.inkMuted, letterSpacing: 0.9, textTransform: 'uppercase',
                    marginBottom: 6 }}>Helbredsnoter</div>
                  {m.health}
                </div>
              )}
            </div>

            {/* SROI-målgruppe */}
            {m.sroiMaalgruppe && m.sroiMaalgruppe !== 'ingen' && m.sroiMaalgruppe !== 'uoplyst' && (
              (window.SROI_MAALGRUPPE_OPTIONS || []).find(o => o.id === m.sroiMaalgruppe) ? (
                <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                  border: `1px solid ${SoS.lineSoft}` }}>
                  {sh('SROI-målgruppe')}
                  <Pill bg={SoS.creamDeep} color={SoS.inkSoft}>
                    {(window.SROI_MAALGRUPPE_OPTIONS || []).find(o => o.id === m.sroiMaalgruppe).label}
                  </Pill>
                </div>
              ) : null
            )}

            {/* Aftalenoter */}
            {m.notes && m.notes.length > 0 && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, padding: '12px 14px',
                border: `1px solid ${SoS.lineSoft}` }}>
                {sh('Aftalenoter')}
                {m.notes.map((n, i) => (
                  <div key={i} style={{
                    paddingBottom: i < m.notes.length - 1 ? 10 : 0,
                    marginBottom: i < m.notes.length - 1 ? 10 : 0,
                    borderBottom: i < m.notes.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                      <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                        color: SoS.ink }}>{n.from}</span>
                      <span style={{ fontFamily: SoS.sans, fontSize: 11,
                        color: SoS.inkMuted }}>{n.date}</span>
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
                      lineHeight: 1.5 }}>{n.text}</div>
                  </div>
                ))}
              </div>
            )}

          </div>
        )}

      </div>

      {/* ── Actions strip ─────────────────────────────────────────────── */}
      <div style={{ padding: '12px 18px', borderTop: `1px solid ${SoS.line}`,
        background: '#fff', display: 'flex', gap: 8, flexWrap: 'wrap',
        position: 'sticky', bottom: 0, zIndex: 10 }}>
        {(m.status === 'afventer' || m.status === 'venter') && (
          <button onClick={() => setTilknytOpen(true)} style={{
            flex: 1, minWidth: 110, padding: '8px 0', borderRadius: SoS.r.sm,
            background: SoS.green, color: '#fff', border: 'none',
            fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5 }}>
            <Icon name="link" size={13} color="#fff" weight={2.3}/>
            Tilknyt brobygger
          </button>
        )}
        <button onClick={() => setAddOpen(true)} style={{
          flex: 1, minWidth: 110, padding: '8px 0', borderRadius: SoS.r.sm,
          background: SoS.accent, color: '#fff', border: 'none',
          fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5 }}>
          <Icon name="plus" size={13} color="#fff" weight={2.3}/>
          Tilføj kontakt
        </button>
        {m.status !== 'afsluttet' && (
          <button onClick={() => setAfslutOpen(true)} style={{
            padding: '8px 14px', borderRadius: SoS.r.sm,
            background: 'transparent', color: '#C62828',
            border: `1px solid #C6282850`, fontFamily: SoS.sans,
            fontSize: 12, cursor: 'pointer', flexShrink: 0 }}>
            Afslut forløb
          </button>
        )}
      </div>

      {/* Tilfoej kontakt — overlay modal */}
      {addOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 300,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: SoS.cream, borderRadius: SoS.r.xl,
            width: '100%', maxWidth: 480, maxHeight: '85vh', overflowY: 'auto',
            boxShadow: '0 8px 40px rgba(0,0,0,0.2)' }}>
            <AddKontaktFlow
              menneskeId={m.id}
              onClose={() => setAddOpen(false)}
              onSaved={() => { setAddOpen(false); handleSaved(); }}
            />
          </div>
        </div>
      )}
      {afslutOpen && (
        <AfslutForloebModal menneske={m} onClose={() => setAfslutOpen(false)}
          onSaved={() => { setAfslutOpen(false); handleSaved(); onClose(); }}/>
      )}
      {tilknytOpen && (
        <TilknytBrobyggerModal menneske={m} onClose={() => setTilknytOpen(false)}
          onSaved={() => { setTilknytOpen(false); handleSaved(); }}/>
      )}
    </>
  );
};

"""

sub(
    "const DesktopMennesker = ({ initialTarget, onTargetConsumed }) => {",
    NEW_COMPONENT + "const DesktopMennesker = ({ initialTarget, onTargetConsumed }) => {",
    "DesktopMenneskeDetailPanel: nyt rent desktop detaljepanel"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. Erstat det genbrugte mobile panel i DesktopMennesker
# ═══════════════════════════════════════════════════════════════════════════
sub(
    """        {/* The mobile-style panel (reused as-is) */}
        <div style={{ fontSize: '0.9em' }}>
          <MenneskeDetailPanel
            menneske={selected}
            onClose={() => setSelected(null)}
          />
        </div>""",
    """        <DesktopMenneskeDetailPanel
          menneske={selected}
          onClose={() => setSelected(null)}
          onRefresh={() => {
            setRefreshKey(k => k + 1);
            setSelected(prev => prev
              ? (window.SoS_MENNESKER?.[prev.id] || prev)
              : null);
          }}
        />""",
    "DesktopMennesker: brug DesktopMenneskeDetailPanel"
)

# ─── Write ────────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ─── CRLF-fix ─────────────────────────────────────────────────────────────
with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'rb') as f:
    b = f.read()
needle_lf = b".join('" + bytes([0x0a]) + b"');"
if needle_lf in b:
    b2 = b.replace(needle_lf, b".join('" + bytes([0x5c, 0x6e]) + b"');")
    with open(r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html', 'wb') as f:
        f.write(b2)
    print("CRLF-fix: rettet")
else:
    print("CRLF-check: OK")

print(f'\nOK ({len(ok)}):')
for x in ok: print(f'  ✅ {x}')
if fail:
    print(f'\nFAIL ({len(fail)}):')
    for x in fail: print(f'  ❌ {x}')
print('\nFil skrevet.')

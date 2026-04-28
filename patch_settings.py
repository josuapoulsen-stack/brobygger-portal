path = r'C:\Users\Josua Poulsen\Documents\Claude Code\Brobygger portal.html'
with open(path, encoding='utf-8') as f:
    html = f.read()

# ── 1. Add lastActive to SS_BROBYGGERE + add SS_MEDARBEJDERE mock data ────────
# Today is 2026-04-24. Design lastActive so we get interesting states:
# bb-1 Maja: 4 days ago (aktiv, fine)
# bb-2 Søren: 10 weeks ago (aktiv, approaching warning at 2 months)
# bb-3 Fatima: 2 weeks ago (fine)
# bb-4 Jens: 7 months ago (pause, would normally auto-end soon)
# bb-5 Lise: 2 days ago (fine)
# bb-6 Mikkel: 6 weeks ago (ny, approaching warning)
# bb-7 Anja: 3 months ago (aktiv but in warning zone)
# bb-8 Karim: 1 week ago (fine)

old_bb = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1, thisWeek: 2 },
  { id: 'bb-2', name: 'Søren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3, thisWeek: 0 },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2, thisWeek: 1 },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0, thisWeek: 0 },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0, thisWeek: 3 },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4, thisWeek: 0 },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2, thisWeek: 1 },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2 },
];"""

new_bb = """const SS_BROBYGGERE = [
  { id: 'bb-1', name: 'Maja Holmberg',    avatar: 'MH', bg: '#E87A3E', active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1, thisWeek: 2, startDate: '2024-10-01', lastActive: '2026-04-20' },
  { id: 'bb-2', name: 'Søren Nybo',       avatar: 'SN', bg: '#7FA089', active: 2, pending: 0, status: 'aktiv', thisMonth: 1, openShifts: 3, thisWeek: 0, startDate: '2025-01-15', lastActive: '2026-02-10' },
  { id: 'bb-3', name: 'Fatima El-Sayed',  avatar: 'FE', bg: '#6B8CAE', active: 3, pending: 2, status: 'aktiv', thisMonth: 4, openShifts: 2, thisWeek: 1, startDate: '2025-03-01', lastActive: '2026-04-09' },
  { id: 'bb-4', name: 'Jens Vangsgaard',  avatar: 'JV', bg: '#B8501E', active: 1, pending: 0, status: 'pause', thisMonth: 0, openShifts: 0, thisWeek: 0, startDate: '2024-05-20', lastActive: '2025-09-14' },
  { id: 'bb-5', name: 'Lise Abildgaard',  avatar: 'LA', bg: '#C46A6A', active: 5, pending: 1, status: 'aktiv', thisMonth: 7, openShifts: 0, thisWeek: 3, startDate: '2024-08-12', lastActive: '2026-04-22' },
  { id: 'bb-6', name: 'Mikkel Hauge',     avatar: 'MH', bg: '#8C6BAE', active: 0, pending: 0, status: 'ny',   thisMonth: 0, openShifts: 4, thisWeek: 0, startDate: '2026-03-01', lastActive: '2026-03-12' },
  { id: 'bb-7', name: 'Anja Poulsen',     avatar: 'AP', bg: '#E8B84B', active: 2, pending: 0, status: 'aktiv', thisMonth: 2, openShifts: 2, thisWeek: 1, startDate: '2025-06-10', lastActive: '2026-01-20' },
  { id: 'bb-8', name: 'Karim Abbas',      avatar: 'KA', bg: '#4A8B7F', active: 3, pending: 1, status: 'aktiv', thisMonth: 3, openShifts: 1, thisWeek: 2, startDate: '2025-09-05', lastActive: '2026-04-17' },
];

// Staff / medarbejdere
const SS_MEDARBEJDERE = [
  { id: 'u1', name: 'Mette Kjærsgaard', avatar: 'MK', bg: '#E87A3E', role: 'admin',    hq: 'Aarhus', email: 'mette@socialsundhed.dk',  joined: '2023-02-01' },
  { id: 'u2', name: 'Peter Lund',       avatar: 'PL', bg: '#6B8CAE', role: 'raadgiver', hq: 'Aarhus', email: 'peter@socialsundhed.dk',  joined: '2024-01-10' },
  { id: 'u3', name: 'Dina Osman',       avatar: 'DO', bg: '#7FA089', role: 'raadgiver', hq: 'Aarhus', email: 'dina@socialsundhed.dk',   joined: '2024-06-15' },
  { id: 'u4', name: 'Rasmus Holm',      avatar: 'RH', bg: '#8C6BAE', role: 'raadgiver', hq: 'Midt',   email: 'rasmus@socialsundhed.dk', joined: '2025-03-01' },
];"""

if old_bb in html:
    html = html.replace(old_bb, new_bb, 1)
    print("Updated SS_BROBYGGERE with startDate/lastActive + added SS_MEDARBEJDERE")
else:
    print("ERROR: SS_BROBYGGERE not found")

# ── 2. Replace AdminSettings with expanded version ────────────────────────────
# Find start and end of existing AdminSettings
start_marker = 'const AdminSettings = '
end_marker = '\nconst SS_Settings = AdminSettings;\n</script>'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker, start_idx)

if start_idx < 0 or end_idx < 0:
    print(f"ERROR: AdminSettings block not found (start={start_idx}, end={end_idx})")
    # Try to find alternate end
    alt = html.find('= AdminSettings;', start_idx)
    print(f"  Alt end: {alt}")
    print(repr(html[alt-20:alt+60]))
else:
    old_admin_settings_block = html[start_idx : end_idx + len(end_marker)]

    new_admin_settings_block = r"""const AdminSettings = ({ currentHq, ownHq, onPick, onClose, isAdmin }) => {
  const [picked, setPicked] = React.useState(currentHq);
  const [section, setSection] = React.useState(null); // null = menu

  // ── Settings state ────────────────────────────────────────────────────────
  const [dataAccess, setDataAccess] = React.useState({ daysBefore: 7, daysAfter: 7 });
  const [lifecycle, setLifecycle] = React.useState({
    warningMonths: 2,   // varsling
    pauseMonths:   4,   // automatisk pause
    endMonths:     8,   // automatisk afslutning
  });
  const [staff, setStaff] = React.useState(SS_MEDARBEJDERE.filter(u => u.hq === ownHq));
  const [saved, setSaved] = React.useState(false);

  // ── Invite state ─────────────────────────────────────────────────────────
  const [bbInvite, setBbInvite] = React.useState({ name: '', email: '', phone: '' });
  const [bbSent, setBbSent] = React.useState(false);
  const [staffInvite, setStaffInvite] = React.useState({ name: '', email: '', role: 'raadgiver' });
  const [staffSent, setStaffSent] = React.useState(false);

  // ── Helpers ───────────────────────────────────────────────────────────────
  const today = new Date('2026-04-24');
  const monthsSince = (dateStr) => {
    const d = new Date(dateStr);
    return (today - d) / (1000 * 60 * 60 * 24 * 30.4);
  };
  const bbStatus = (b) => {
    const m = monthsSince(b.lastActive);
    if (m >= lifecycle.endMonths)   return { level: 'end',     label: 'Afsluttes snart', color: SS.rose };
    if (m >= lifecycle.pauseMonths) return { level: 'pause',   label: 'Foreslås pause',  color: SS.sun };
    if (m >= lifecycle.warningMonths) return { level: 'warn',  label: 'Inaktiv',         color: SS.sun };
    return null;
  };

  const saveAndBack = () => {
    setSaved(true);
    setTimeout(() => { setSaved(false); setSection(null); }, 1200);
  };

  const NumStepper = ({ label, sublabel, value, min, max, onChange }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12,
      padding: '12px 0', borderBottom: `1px solid ${SS.lineSoft}` }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 500, color: SS.ink }}>{label}</div>
        {sublabel && <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkMuted, marginTop: 2 }}>{sublabel}</div>}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <button onClick={() => onChange(Math.max(min, value - 1))} style={{
          width: 30, height: 30, borderRadius: 15, border: `1.5px solid ${SS.lineSoft}`,
          background: '#fff', cursor: 'pointer', fontFamily: SS.sans, fontSize: 18,
          color: SS.ink, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>−</button>
        <span style={{ fontFamily: SS.font, fontSize: 20, fontWeight: 500,
          color: SS.orange, minWidth: 28, textAlign: 'center' }}>{value}</span>
        <button onClick={() => onChange(Math.min(max, value + 1))} style={{
          width: 30, height: 30, borderRadius: 15, border: `1.5px solid ${SS.lineSoft}`,
          background: '#fff', cursor: 'pointer', fontFamily: SS.sans, fontSize: 18,
          color: SS.ink, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>+</button>
      </div>
    </div>
  );

  // ── Section renderers ─────────────────────────────────────────────────────

  const renderHq = () => (
    <>
      <SectionHead title="Dit hoveds\u00e6de"/>
      <div style={{ background: '#fff', borderRadius: SS.r.md, padding: 16,
        border: `1px solid ${SS.lineSoft}`, marginBottom: 24,
        display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 12, height: 12, borderRadius: 6, background: SS.hq[ownHq] || SS.orange }}/>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 600, color: SS.ink }}>{ownHq}</div>
          <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft }}>Dit prim\u00e6re hoveds\u00e6de</div>
        </div>
        <Pill bg={SS.sageSoft} color={SS.sage}>Standard</Pill>
      </div>
      <SectionHead title="Se midlertidigt et andet hoveds\u00e6de"/>
      <div style={{ padding: 12, background: SS.creamDeep, borderRadius: SS.r.md,
        marginBottom: 12, display: 'flex', gap: 10 }}>
        <Icon name="lock" size={16} color={SS.orangeDeep}/>
        <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.orangeDeep, lineHeight: 1.5 }}>
          Nulstilles automatisk n\u00e5r du logger ud. Dine handlinger logges i revisionsspor.
        </div>
      </div>
      {SS_HOVEDSAEDER.filter(h => h !== ownHq).map(h => {
        const sel = picked === h;
        return (
          <button key={h} onClick={() => setPicked(h)} style={{
            display: 'flex', alignItems: 'center', gap: 12, width: '100%',
            padding: 14, marginBottom: 6, textAlign: 'left',
            background: '#fff',
            border: `2px solid ${sel ? (SS.hq[h] || SS.orange) : SS.lineSoft}`,
            borderRadius: SS.r.md, cursor: 'pointer',
          }}>
            <div style={{ width: 12, height: 12, borderRadius: 6, background: SS.hq[h] || SS.orange }}/>
            <span style={{ flex: 1, fontFamily: SS.sans, fontSize: 14, color: SS.ink }}>{h}</span>
            {sel && <Icon name="check" size={16} color={SS.hq[h] || SS.orange}/>}
          </button>
        );
      })}
      <button onClick={() => { onPick(picked); }} style={{
        width: '100%', marginTop: 12, padding: '14px 0',
        background: picked !== currentHq ? SS.orange : SS.lineSoft,
        color: picked !== currentHq ? '#fff' : SS.inkMuted,
        border: 'none', borderRadius: SS.r.md,
        fontFamily: SS.sans, fontSize: 15, fontWeight: 600, cursor: 'pointer',
      }}>
        Skift til {picked}
      </button>
    </>
  );

  const renderDataAccess = () => (
    <>
      <div style={{ background: '#FFF8F0', border: `1.5px solid ${SS.orange}30`,
        borderRadius: SS.r.md, padding: '12px 14px', marginBottom: 20 }}>
        <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
          color: SS.orange, marginBottom: 4 }}>GDPR \u2014 Artikel 9 (f\u00f8lsomme oplysninger)</div>
        <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, lineHeight: 1.5 }}>
          Brobyggere m\u00e5 kun se helbredsoplysninger og diagnoser i den periode, de har en aktiv brobygning.
          Udenfor vinduet vises data sk\u00e6rmet \u2014 kun brobygningstype og behov er synlige.
        </div>
      </div>
      <div style={{ background: '#fff', borderRadius: SS.r.md,
        border: `1px solid ${SS.lineSoft}`, padding: '0 16px', marginBottom: 20 }}>
        <NumStepper
          label="Dage f\u00f8r aftalen"
          sublabel="Brobygger f\u00e5r adgang X dage inden brobygningen"
          value={dataAccess.daysBefore} min={1} max={30}
          onChange={v => setDataAccess(d => ({ ...d, daysBefore: v }))}
        />
        <NumStepper
          label="Dage efter aftalen"
          sublabel="Adgang forts\u00e6tter X dage efter seneste brobygning"
          value={dataAccess.daysAfter} min={1} max={30}
          onChange={v => setDataAccess(d => ({ ...d, daysAfter: v }))}
        />
      </div>
      <div style={{ background: SS.creamDeep, borderRadius: SS.r.md,
        padding: '12px 14px', marginBottom: 20 }}>
        <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
          color: SS.ink, marginBottom: 4 }}>Eksempel med nuv\u00e6rende indstillinger</div>
        <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, lineHeight: 1.6 }}>
          Aftale d. <strong>1. maj</strong> \u2192 adgang fra <strong>{(() => {
            const d = new Date('2026-05-01');
            d.setDate(d.getDate() - dataAccess.daysBefore);
            return d.toLocaleDateString('da-DK', { day: 'numeric', month: 'long' });
          })()}</strong> til <strong>{(() => {
            const d = new Date('2026-05-01');
            d.setDate(d.getDate() + dataAccess.daysAfter);
            return d.toLocaleDateString('da-DK', { day: 'numeric', month: 'long' });
          })()}</strong>
        </div>
      </div>
      <button onClick={saveAndBack} style={{
        width: '100%', padding: '14px 0',
        background: SS.sage, color: '#fff', border: 'none',
        borderRadius: SS.r.md, fontFamily: SS.sans, fontSize: 15,
        fontWeight: 600, cursor: 'pointer',
      }}>
        {saved ? '\u2713 Gemt' : 'Gem indstillinger'}
      </button>
    </>
  );

  const renderLifecycle = () => {
    const atRisk = SS_BROBYGGERE.filter(b => bbStatus(b));
    return (
      <>
        <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
          marginBottom: 16, lineHeight: 1.5 }}>
          Det er sv\u00e6rt at vide, hvorn\u00e5r en brobygger ikke vil mere.
          Disse parametre styrer, hvorn\u00e5r systemet automatisk reagerer p\u00e5 inaktivitet.
        </div>
        <div style={{ background: '#fff', borderRadius: SS.r.md,
          border: `1px solid ${SS.lineSoft}`, padding: '0 16px', marginBottom: 20 }}>
          <NumStepper
            label="Varsling"
            sublabel={"M\u00e5neder uden brobygning \u2192 notifikation til r\u00e5dgiver"}
            value={lifecycle.warningMonths} min={1} max={12}
            onChange={v => setLifecycle(l => ({ ...l, warningMonths: v }))}
          />
          <NumStepper
            label="Automatisk pause"
            sublabel={"M\u00e5neder uden brobygning \u2192 status s\u00e6ttes til 'pause'"}
            value={lifecycle.pauseMonths} min={1} max={24}
            onChange={v => setLifecycle(l => ({ ...l, pauseMonths: v }))}
          />
          <NumStepper
            label="Automatisk afslutning"
            sublabel={"M\u00e5neder uden aktivitet \u2192 brobygger afsluttes automatisk"}
            value={lifecycle.endMonths} min={1} max={36}
            onChange={v => setLifecycle(l => ({ ...l, endMonths: v }))}
          />
        </div>

        {/* Brobyggere i farezonen */}
        {atRisk.length > 0 && (
          <>
            <SectionHead title="Kr\u00e6ver opm\u00e6rksomhed nu"/>
            {SS_BROBYGGERE.filter(b => bbStatus(b)).map(b => {
              const st = bbStatus(b);
              const months = monthsSince(b.lastActive);
              return (
                <div key={b.id} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: 14, background: '#fff', marginBottom: 8,
                  borderRadius: SS.r.md, border: `1.5px solid ${st.color}40`,
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 18, background: b.bg,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  }}>
                    <span style={{ fontFamily: SS.sans, fontSize: 11,
                      fontWeight: 700, color: '#fff' }}>{b.avatar}</span>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: SS.sans, fontSize: 13,
                      fontWeight: 600, color: SS.ink }}>{b.name}</div>
                    <div style={{ fontFamily: SS.sans, fontSize: 11,
                      color: SS.inkSoft, marginTop: 2 }}>
                      Inaktiv i {Math.round(months * 10) / 10} m\u00e5neder
                      {b.lastActive && ` \u00b7 sidst aktiv ${new Date(b.lastActive).toLocaleDateString('da-DK', { day: 'numeric', month: 'short' })}`}
                    </div>
                  </div>
                  <Pill bg={st.color + '22'} color={st.color}>{st.label}</Pill>
                </div>
              );
            })}
          </>
        )}

        <div style={{ background: SS.creamDeep, borderRadius: SS.r.md,
          padding: '12px 14px', marginBottom: 20 }}>
          <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
            color: SS.ink, marginBottom: 4 }}>Om automatisk afslutning</div>
          <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft, lineHeight: 1.5 }}>
            N\u00e5r en brobygger afsluttes automatisk, f\u00e5r de en venlig e-mail der takker for indsatsen
            og inviterer dem til at vende tilbage n\u00e5r de har tid. Aktive brobygningsforl\u00f8b overf\u00f8res
            til r\u00e5dgiveren inden afslutning.
          </div>
        </div>
        <button onClick={saveAndBack} style={{
          width: '100%', padding: '14px 0',
          background: SS.sage, color: '#fff', border: 'none',
          borderRadius: SS.r.md, fontFamily: SS.sans, fontSize: 15,
          fontWeight: 600, cursor: 'pointer',
        }}>
          {saved ? '\u2713 Gemt' : 'Gem parametre'}
        </button>
      </>
    );
  };

  const renderStaff = () => (
    <>
      <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
        marginBottom: 16, lineHeight: 1.5 }}>
        Tildel roller til medarbejdere p\u00e5 {ownHq}-hoveds\u00e6det. Kun admins kan \u00e6ndre roller.
      </div>
      {staff.map(u => (
        <div key={u.id} style={{
          display: 'flex', alignItems: 'center', gap: 12,
          padding: 14, background: '#fff', marginBottom: 8,
          borderRadius: SS.r.md, border: `1px solid ${SS.lineSoft}`,
        }}>
          <div style={{
            width: 40, height: 40, borderRadius: 20, background: u.bg,
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <span style={{ fontFamily: SS.sans, fontSize: 13,
              fontWeight: 700, color: '#fff' }}>{u.avatar}</span>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: SS.sans, fontSize: 14,
              fontWeight: 600, color: SS.ink }}>{u.name}</div>
            <div style={{ fontFamily: SS.sans, fontSize: 11,
              color: SS.inkSoft, marginTop: 1, overflow: 'hidden',
              textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{u.email}</div>
          </div>
          {isAdmin ? (
            <select
              value={u.role}
              onChange={e => setStaff(s => s.map(m => m.id === u.id ? { ...m, role: e.target.value } : m))}
              style={{
                fontFamily: SS.sans, fontSize: 12, fontWeight: 600,
                color: u.role === 'admin' ? SS.orange : SS.sage,
                background: u.role === 'admin' ? SS.orange + '15' : SS.sageSoft,
                border: 'none', borderRadius: 999, padding: '5px 10px', cursor: 'pointer',
              }}>
              <option value="raadgiver">R\u00e5dgiver</option>
              <option value="admin">Admin</option>
            </select>
          ) : (
            <Pill
              bg={u.role === 'admin' ? SS.orange + '15' : SS.sageSoft}
              color={u.role === 'admin' ? SS.orange : SS.sage}>
              {u.role === 'admin' ? 'Admin' : 'R\u00e5dgiver'}
            </Pill>
          )}
        </div>
      ))}

      {/* Invite staff */}
      <div style={{ marginTop: 20 }}>
        <SectionHead title="Inviter medarbejder"/>
        {staffSent ? (
          <div style={{ padding: 16, background: SS.sageSoft, borderRadius: SS.r.md,
            fontFamily: SS.sans, fontSize: 14, color: SS.sage, textAlign: 'center' }}>
            \u2713 Invitation sendt til {staffInvite.email}
          </div>
        ) : (
          <>
            {[
              { key: 'name', label: 'Navn', placeholder: 'Fulde navn' },
              { key: 'email', label: 'E-mail', placeholder: 'navn@socialsundhed.dk' },
            ].map(f => (
              <div key={f.key} style={{ marginBottom: 10 }}>
                <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,
                  color: SS.inkSoft, marginBottom: 5 }}>{f.label}</div>
                <input placeholder={f.placeholder} value={staffInvite[f.key]}
                  onChange={e => setStaffInvite(si => ({ ...si, [f.key]: e.target.value }))}
                  style={{ width: '100%', padding: '11px 13px', fontFamily: SS.sans,
                    fontSize: 14, color: SS.ink, background: '#fff',
                    border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                    outline: 'none', boxSizing: 'border-box' }} />
              </div>
            ))}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,
                color: SS.inkSoft, marginBottom: 5 }}>Rolle</div>
              <div style={{ display: 'flex', gap: 8 }}>
                {['raadgiver', 'admin'].map(r => (
                  <button key={r} onClick={() => setStaffInvite(si => ({ ...si, role: r }))}
                    style={{
                      flex: 1, padding: '10px 0',
                      fontFamily: SS.sans, fontSize: 13, fontWeight: 600,
                      color: staffInvite.role === r ? '#fff' : SS.inkSoft,
                      background: staffInvite.role === r ? SS.orange : '#fff',
                      border: `1.5px solid ${staffInvite.role === r ? SS.orange : SS.lineSoft}`,
                      borderRadius: SS.r.md, cursor: 'pointer',
                    }}>
                    {r === 'raadgiver' ? 'R\u00e5dgiver' : 'Admin'}
                  </button>
                ))}
              </div>
            </div>
            <button
              disabled={!staffInvite.name || !staffInvite.email}
              onClick={() => setStaffSent(true)}
              style={{
                width: '100%', padding: '13px 0',
                background: staffInvite.name && staffInvite.email ? SS.orange : SS.lineSoft,
                color: staffInvite.name && staffInvite.email ? '#fff' : SS.inkMuted,
                border: 'none', borderRadius: SS.r.md,
                fontFamily: SS.sans, fontSize: 14, fontWeight: 600, cursor: 'pointer',
              }}>
              Send invitation
            </button>
          </>
        )}
      </div>
    </>
  );

  const renderInviteBb = () => (
    <>
      <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft,
        marginBottom: 20, lineHeight: 1.5 }}>
        Send en invitationslink til en potentiel brobygger. De opretter selv en profil
        og g\u00e5r igennem onboarding-processen, inden de godkendes.
      </div>
      {bbSent ? (
        <div style={{ padding: 20, background: SS.sageSoft, borderRadius: SS.r.md,
          textAlign: 'center' }}>
          <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500,
            color: SS.sage, marginBottom: 6 }}>Invitation sendt \u2713</div>
          <div style={{ fontFamily: SS.sans, fontSize: 13, color: SS.inkSoft }}>
            {bbInvite.name} f\u00e5r en e-mail eller SMS med link til at tilmelde sig.
          </div>
          <button onClick={() => { setBbSent(false); setBbInvite({ name: '', email: '', phone: '' }); }}
            style={{ marginTop: 16, padding: '10px 20px', background: 'transparent',
              border: `1px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
              fontFamily: SS.sans, fontSize: 13, cursor: 'pointer', color: SS.inkSoft }}>
            Inviter endnu en
          </button>
        </div>
      ) : (
        <>
          {[
            { key: 'name',  label: 'Navn',    placeholder: 'F\u00f8r- og efternavn', required: true },
            { key: 'email', label: 'E-mail',  placeholder: 'Valgfrit' },
            { key: 'phone', label: 'Telefon', placeholder: 'Valgfrit — til SMS-invitation' },
          ].map(f => (
            <div key={f.key} style={{ marginBottom: 12 }}>
              <div style={{ fontFamily: SS.sans, fontSize: 11, fontWeight: 600,
                color: SS.inkSoft, marginBottom: 5 }}>
                {f.label}{f.required && <span style={{ color: SS.orange }}> *</span>}
              </div>
              <input placeholder={f.placeholder} value={bbInvite[f.key]}
                onChange={e => setBbInvite(b => ({ ...b, [f.key]: e.target.value }))}
                style={{ width: '100%', padding: '11px 13px', fontFamily: SS.sans,
                  fontSize: 14, color: SS.ink, background: '#fff',
                  border: `1.5px solid ${SS.lineSoft}`, borderRadius: SS.r.md,
                  outline: 'none', boxSizing: 'border-box' }} />
            </div>
          ))}
          <div style={{ background: SS.creamDeep, borderRadius: SS.r.md,
            padding: '10px 14px', marginBottom: 16 }}>
            <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft, lineHeight: 1.5 }}>
              Invitation udl\u00f8ber efter 14 dage. Den nye brobygger g\u00e5r gennem onboarding
              og vises som "afventer godkendelse" indtil du godkender dem.
            </div>
          </div>
          <button
            disabled={!bbInvite.name}
            onClick={() => setBbSent(true)}
            style={{
              width: '100%', padding: '14px 0',
              background: bbInvite.name ? SS.orange : SS.lineSoft,
              color: bbInvite.name ? '#fff' : SS.inkMuted,
              border: 'none', borderRadius: SS.r.md,
              fontFamily: SS.sans, fontSize: 15, fontWeight: 600, cursor: 'pointer',
            }}>
            Send invitation
          </button>
        </>
      )}
    </>
  );

  // ── Section menu items ────────────────────────────────────────────────────
  const SECTIONS = [
    { id: 'hq',        icon: 'building', label: 'Hoveds\u00e6de',            sub: `Viser ${currentHq}`,                      show: true },
    { id: 'data',      icon: 'lock',     label: 'Databeskyttelse',           sub: `F\u00f8lsomt data: \u00b1${dataAccess.daysBefore}/${dataAccess.daysAfter} dage`,  show: true },
    { id: 'lifecycle', icon: 'calendar', label: 'Brobygger-livscyklus',      sub: `Afslutning efter ${lifecycle.endMonths} m\u00e5neder`,  show: true },
    { id: 'staff',     icon: 'users',    label: 'Medarbejdere & roller',     sub: `${staff.length} p\u00e5 ${ownHq}`,           show: isAdmin },
    { id: 'invite-bb', icon: 'user',     label: 'Inviter brobygger',         sub: 'Send invitationslink',                    show: true },
  ];

  const TITLES = {
    hq: 'Hoveds\u00e6de',
    data: 'Databeskyttelse',
    lifecycle: 'Brobygger-livscyklus',
    staff: 'Medarbejdere & roller',
    'invite-bb': 'Inviter brobygger',
  };

  return (
    <div style={{ position: 'absolute', inset: 0, background: SS.cream,
      display: 'flex', flexDirection: 'column' }}>

      {/* Header */}
      <div style={{ padding: '54px 20px 16px', background: '#fff',
        borderBottom: `1px solid ${SS.lineSoft}`,
        display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
        <button onClick={section ? () => setSection(null) : onClose}
          style={{ background: 'none', border: 'none', padding: 4, cursor: 'pointer' }}>
          <Icon name="chevronL" size={22} color={SS.ink}/>
        </button>
        <div>
          <div style={{ fontFamily: SS.font, fontSize: 22, fontWeight: 500 }}>
            {section ? TITLES[section] : 'Indstillinger'}
          </div>
          {!section && (
            <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft }}>
              {ownHq} \u00b7 {isAdmin ? 'Admin' : 'R\u00e5dgiver'}
            </div>
          )}
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
        {!section && (
          <>
            {SECTIONS.filter(s => s.show).map(s => (
              <button key={s.id} onClick={() => setSection(s.id)} style={{
                display: 'flex', alignItems: 'center', gap: 14, width: '100%',
                padding: '14px 16px', marginBottom: 8, textAlign: 'left',
                background: '#fff', border: `1px solid ${SS.lineSoft}`,
                borderRadius: SS.r.md, cursor: 'pointer',
              }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 20,
                  background: SS.creamDeep, flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Icon name={s.icon} size={18} color={SS.inkSoft}/>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SS.sans, fontSize: 14, fontWeight: 600,
                    color: SS.ink }}>{s.label}</div>
                  <div style={{ fontFamily: SS.sans, fontSize: 12, color: SS.inkSoft,
                    marginTop: 2 }}>{s.sub}</div>
                </div>
                <Icon name="chevronR" size={16} color={SS.inkMuted}/>
              </button>
            ))}
            {/* Brobyggere needing attention */}
            {(() => {
              const atRisk = SS_BROBYGGERE.filter(b => bbStatus(b));
              if (!atRisk.length) return null;
              return (
                <div style={{ marginTop: 8, padding: '10px 14px',
                  background: SS.sun + '22', border: `1px solid ${SS.sun}`,
                  borderRadius: SS.r.md, cursor: 'pointer' }}
                  onClick={() => setSection('lifecycle')}>
                  <div style={{ fontFamily: SS.sans, fontSize: 12, fontWeight: 700,
                    color: SS.orangeDeep }}>
                    {atRisk.length} brobygger{atRisk.length > 1 ? 'e' : ''} kr\u00e6ver opm\u00e6rksomhed
                  </div>
                  <div style={{ fontFamily: SS.sans, fontSize: 11, color: SS.inkSoft, marginTop: 3 }}>
                    {atRisk.map(b => b.name.split(' ')[0]).join(', ')} \u2014 tjek livscyklus-indstillinger
                  </div>
                </div>
              );
            })()}
          </>
        )}
        {section === 'hq'        && renderHq()}
        {section === 'data'      && renderDataAccess()}
        {section === 'lifecycle' && renderLifecycle()}
        {section === 'staff'     && renderStaff()}
        {section === 'invite-bb' && renderInviteBb()}
      </div>
    </div>
  );
};

const SS_Settings = AdminSettings;
</script>"""

    html = html.replace(old_admin_settings_block, new_admin_settings_block, 1)
    print("Replaced AdminSettings with expanded version")

# ── 3. Pass isAdmin to AdminSettings in app.jsx ──────────────────────────────
old_settings_call = """      content = <AdminSettings
        currentHq={viewingHq}
        ownHq="Aarhus"
        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}
        onClose={() => setSettingsOpen(false)} />;"""

new_settings_call = """      content = <AdminSettings
        currentHq={viewingHq}
        ownHq="Aarhus"
        isAdmin={tweaks.role === "admin"}
        onPick={(hq) => { setViewingHq(hq); setSettingsOpen(false); }}
        onClose={() => setSettingsOpen(false)} />;"""

if old_settings_call in html:
    html = html.replace(old_settings_call, new_settings_call, 1)
    print("Passed isAdmin to AdminSettings")
else:
    print("ERROR: AdminSettings call not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDone. File: {len(html):,} bytes")

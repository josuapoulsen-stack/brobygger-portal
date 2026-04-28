#!/usr/bin/env python3
"""
patch_dead_ends_2.py — Fix dead ends in Brobygger portal.html
Applies surgical string replacements for 8 fixes.
Exit code always 0; prints [OK] or [WARN] per step.
"""

import sys

FILE = r"C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html"


def apply(content, description, old, new):
    if old in content:
        count = content.count(old)
        if count > 1:
            print(f"[WARN] {description} — found {count} occurrences, replacing first only")
            content = content.replace(old, new, 1)
        else:
            content = content.replace(old, new)
            print(f"[OK]   {description}")
    else:
        print(f"[WARN] {description} — old string not found, skipping")
    return content


def main():
    with open(FILE, encoding='utf-8') as f:
        src = f.read()

    # ─── FIX 1a: CalendarScreen — add setMonth + helpers ──────────────────────
    src = apply(
        src,
        "Fix 1a: CalendarScreen month state — add setMonth + prevMonth/nextMonth",
        "  const [month] = React.useState(new Date('2026-04-24'));",
        "  const [month, setMonth] = React.useState(new Date('2026-04-24'));\n"
        "  const prevMonth = () => setMonth(d => new Date(d.getFullYear(), d.getMonth() - 1, 1));\n"
        "  const nextMonth = () => setMonth(d => new Date(d.getFullYear(), d.getMonth() + 1, 1));",
    )

    # ─── FIX 1b: CalendarScreen — wire chevronL onClick to prevMonth ──────────
    src = apply(
        src,
        "Fix 1b: CalendarScreen chevronL button — wire prevMonth onClick",
        "          <button style={{ width: 36, height: 36, borderRadius: 18,\n"
        "            background: '#fff', border: `1px solid ${SoS.line}`,\n"
        "            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>\n"
        "            <Icon name=\"chevronL\" size={18} color={SoS.ink} />\n"
        "          </button>\n"
        "          <button style={{ width: 36, height: 36, borderRadius: 18,\n"
        "            background: '#fff', border: `1px solid ${SoS.line}`,\n"
        "            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>\n"
        "            <Icon name=\"chevron\" size={18} color={SoS.ink} />\n"
        "          </button>",
        "          <button onClick={prevMonth} style={{ width: 36, height: 36, borderRadius: 18,\n"
        "            background: '#fff', border: `1px solid ${SoS.line}`,\n"
        "            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>\n"
        "            <Icon name=\"chevronL\" size={18} color={SoS.ink} />\n"
        "          </button>\n"
        "          <button onClick={nextMonth} style={{ width: 36, height: 36, borderRadius: 18,\n"
        "            background: '#fff', border: `1px solid ${SoS.line}`,\n"
        "            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>\n"
        "            <Icon name=\"chevron\" size={18} color={SoS.ink} />\n"
        "          </button>",
    )

    # ─── FIX 1c: CalendarScreen — fix hardcoded iso string ────────────────────
    src = apply(
        src,
        "Fix 1c: CalendarScreen grid cells — dynamic iso from month state",
        "          const iso = `2026-04-${String(d).padStart(2, '0')}`;\n"
        "          const isSel = iso === selected;\n"
        "          const isToday = iso === '2026-04-24';",
        "          const iso = `${year}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;\n"
        "          const isSel = iso === selected;\n"
        "          const isToday = iso === '2026-04-27';",
    )

    # ─── FIX 1d: CalendarScreen — update selected initial value ───────────────
    src = apply(
        src,
        "Fix 1d: CalendarScreen — update selected initial value to 2026-04-27",
        "  const [selected, setSelected] = React.useState('2026-04-24');",
        "  const [selected, setSelected] = React.useState('2026-04-27');",
    )

    # ─── FIX 2a: MessageThread — add sent state ────────────────────────────────
    src = apply(
        src,
        "Fix 2a: MessageThread — add sent state after draft state",
        "  const [draft, setDraft] = React.useState('');",
        "  const [draft, setDraft] = React.useState('');\n"
        "  const [sent, setSent] = React.useState(false);",
    )

    # ─── FIX 2b: MessageThread — replace send button with onClick logic ────────
    src = apply(
        src,
        "Fix 2b: MessageThread — wire send button with sent feedback",
        "        <button style={{ width: 38, height: 38, borderRadius: 19,\n"
        "          background: draft ? SoS.orange : SoS.creamDeep, border: 'none', cursor: 'pointer',\n"
        "          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,\n"
        "          transition: 'background 0.2s' }}>\n"
        "          <Icon name=\"chevron\" size={18} color={draft ? '#fff' : SoS.inkMuted} weight={2.5}/>\n"
        "        </button>",
        "        <button onClick={() => { if (draft.trim()) { setSent(true); setDraft(''); setTimeout(() => setSent(false), 2000); } }}\n"
        "          style={{ width: 38, height: 38, borderRadius: 19,\n"
        "          background: draft ? SoS.orange : SoS.creamDeep, border: 'none', cursor: 'pointer',\n"
        "          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,\n"
        "          transition: 'background 0.2s' }}>\n"
        "          <Icon name={sent ? 'check' : 'chevron'} size={18} color={draft || sent ? '#fff' : SoS.inkMuted} weight={2.5}/>\n"
        "        </button>",
    )

    # ─── FIX 3: ProfileScreen — convert to stateful function with toast ────────
    # Step 3a: change opening signature
    src = apply(
        src,
        "Fix 3a: ProfileScreen — opening arrow fn parens to braces",
        "const ProfileScreen = ({ user, onSwitchRole }) => (\n"
        "  <>\n"
        "    <TopBar title=\"Profil\" />",
        "const ProfileScreen = ({ user, onSwitchRole }) => {\n"
        "  const [toast, setToast] = React.useState(null);\n"
        "  const showToast = (label) => { setToast(label); setTimeout(() => setToast(null), 2000); };\n"
        "  return (\n"
        "  <>\n"
        "    <TopBar title=\"Profil\" />",
    )

    # Step 3b: add onClick to menu row div
    src = apply(
        src,
        "Fix 3b: ProfileScreen — add onClick to menu row div",
        "          <div key={i} style={{\n"
        "            display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px',\n"
        "            borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',\n"
        "            cursor: 'pointer',\n"
        "          }}>",
        "          <div key={i} onClick={() => showToast(row.label)} style={{\n"
        "            display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px',\n"
        "            borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',\n"
        "            cursor: 'pointer',\n"
        "          }}>",
    )

    # Step 3c: close the component — add toast overlay, wrap closing parens
    src = apply(
        src,
        "Fix 3c: ProfileScreen — add toast overlay and close stateful function",
        "      <Button full variant=\"secondary\" onClick={onSwitchRole}>\n"
        "        Skift til ansat-visning\n"
        "      </Button>\n"
        "    </div>\n"
        "  </>\n"
        ");\n"
        "\n"
        "Object.assign(window, { HistorikScreen, NotifScreen, ProfileScreen });",
        "      <Button full variant=\"secondary\" onClick={onSwitchRole}>\n"
        "        Skift til ansat-visning\n"
        "      </Button>\n"
        "    </div>\n"
        "    {toast && (\n"
        "      <div style={{ position: 'fixed', bottom: 90, left: '50%', transform: 'translateX(-50%)',\n"
        "        background: SoS.ink, color: '#fff', padding: '12px 20px', borderRadius: 999,\n"
        "        fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, zIndex: 999,\n"
        "        boxShadow: '0 4px 20px rgba(0,0,0,0.2)', whiteSpace: 'nowrap' }}>\n"
        "        {toast} — kommer snart\n"
        "      </div>\n"
        "    )}\n"
        "  </>\n"
        "  );\n"
        "};\n"
        "\n"
        "Object.assign(window, { HistorikScreen, NotifScreen, ProfileScreen });",
    )

    # ─── FIX 4a: AppointmentDetailScreen — add cancel/cancelled state ──────────
    src = apply(
        src,
        "Fix 4a: AppointmentDetailScreen — add showCancel + cancelled state",
        "  const [revealed, setRevealed] = React.useState(false);",
        "  const [revealed, setRevealed] = React.useState(false);\n"
        "  const [showCancel, setShowCancel] = React.useState(false);\n"
        "  const [cancelled, setCancelled] = React.useState(false);",
    )

    # Step 4b: wire onClick on "Aflys aftale" button
    src = apply(
        src,
        "Fix 4b: AppointmentDetailScreen — wire Aflys aftale button onClick",
        "            <Button full variant=\"ghost\"\n"
        "              icon={<Icon name=\"x\" size={16} color={SoS.rose} weight={2.2} />}\n"
        "              style={{ color: SoS.rose }}>\n"
        "              Aflys aftale\n"
        "            </Button>",
        "            <Button full variant=\"ghost\"\n"
        "              onClick={() => setShowCancel(true)}\n"
        "              icon={<Icon name=\"x\" size={16} color={SoS.rose} weight={2.2} />}\n"
        "              style={{ color: SoS.rose }}>\n"
        "              Aflys aftale\n"
        "            </Button>",
    )

    # Step 4c: insert cancel overlays before closing div of AppointmentDetailScreen
    src = apply(
        src,
        "Fix 4c: AppointmentDetailScreen — insert cancel/cancelled overlays",
        "\n    </div>\n  );\n};\n\nwindow.AppointmentDetailScreen = AppointmentDetailScreen;",
        "\n"
        "      {showCancel && !cancelled && (\n"
        "        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',\n"
        "          display: 'flex', alignItems: 'flex-end', zIndex: 999 }}>\n"
        "          <div style={{ width: '100%', background: '#fff', borderRadius: '20px 20px 0 0',\n"
        "            padding: '24px 20px 40px' }}>\n"
        "            <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,\n"
        "              color: SoS.ink, marginBottom: 8 }}>Aflys aftale?</div>\n"
        "            <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,\n"
        "              lineHeight: 1.5, marginBottom: 24 }}>\n"
        "              Din koordinator bliver informeret. Aftalen fjernes fra din kalender.\n"
        "            </div>\n"
        "            <div style={{ display: 'flex', gap: 10 }}>\n"
        "              <Button full variant=\"secondary\" onClick={() => setShowCancel(false)}>\n"
        "                Behold aftale\n"
        "              </Button>\n"
        "              <Button full onClick={() => { setCancelled(true); setShowCancel(false); }}\n"
        "                style={{ background: SoS.rose, color: '#fff' }}>\n"
        "                Bekræft aflysning\n"
        "              </Button>\n"
        "            </div>\n"
        "          </div>\n"
        "        </div>\n"
        "      )}\n"
        "      {cancelled && (\n"
        "        <div style={{ position: 'absolute', inset: 0, background: SoS.cream,\n"
        "          display: 'flex', flexDirection: 'column', alignItems: 'center',\n"
        "          justifyContent: 'center', padding: 32 }}>\n"
        "          <div style={{ width: 64, height: 64, borderRadius: 32, background: SoS.rose + '22',\n"
        "            display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>\n"
        "            <Icon name=\"x\" size={28} color={SoS.rose} weight={2.5}/>\n"
        "          </div>\n"
        "          <div style={{ fontFamily: SoS.font, fontSize: 24, fontWeight: 500,\n"
        "            color: SoS.ink, marginBottom: 8, textAlign: 'center' }}>\n"
        "            Aftale aflyst\n"
        "          </div>\n"
        "          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,\n"
        "            textAlign: 'center', lineHeight: 1.6, marginBottom: 28 }}>\n"
        "            Din koordinator er informeret. Vi finder en ny tid.\n"
        "          </div>\n"
        "          <Button full onClick={onBack}>Gå tilbage</Button>\n"
        "        </div>\n"
        "      )}\n"
        "    </div>\n"
        "  );\n"
        "};\n"
        "\n"
        "window.AppointmentDetailScreen = AppointmentDetailScreen;",
    )

    # ─── FIX 5a: RegistrerEfterAftale — add submitted state ───────────────────
    src = apply(
        src,
        "Fix 5a: RegistrerEfterAftale — add submitted state",
        "  const set = (k, v) => setData(d => ({ ...d, [k]: v }));",
        "  const set = (k, v) => setData(d => ({ ...d, [k]: v }));\n"
        "  const [submitted, setSubmitted] = React.useState(false);",
    )

    # Step 5b: change Indsend button to setSubmitted
    src = apply(
        src,
        "Fix 5b: RegistrerEfterAftale — Indsend button sets submitted instead of onClose",
        "          onClick={() => step === steps.length - 1 ? onClose() : setStep(step + 1)}",
        "          onClick={() => step === steps.length - 1 ? setSubmitted(true) : setStep(step + 1)}",
    )

    # Step 5c: add done screen before return
    src = apply(
        src,
        "Fix 5c: RegistrerEfterAftale — add submitted done screen before return",
        "  return (\n"
        "    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, display: 'flex', flexDirection: 'column' }}>\n"
        "      {/* Header */}\n"
        "      <div style={{ padding: '54px 20px 12px', background: '#fff', borderBottom: `1px solid ${SoS.line}` }}>",
        "  if (submitted) return (\n"
        "    <div style={{ position: 'absolute', inset: 0, background: SoS.cream,\n"
        "      display: 'flex', flexDirection: 'column', alignItems: 'center',\n"
        "      justifyContent: 'center', padding: 32 }}>\n"
        "      <div style={{ width: 72, height: 72, borderRadius: 36, background: SoS.sageSoft,\n"
        "        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 }}>\n"
        "        <Icon name=\"check\" size={32} color={SoS.sage} weight={2.5}/>\n"
        "      </div>\n"
        "      <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,\n"
        "        color: SoS.ink, textAlign: 'center', marginBottom: 8 }}>\n"
        "        Tak for registreringen!\n"
        "      </div>\n"
        "      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,\n"
        "        textAlign: 'center', lineHeight: 1.6, marginBottom: 28 }}>\n"
        "        Kontakten tæller med i statistik og SROI-beregning.\n"
        "        {data.continues === false && ' Forløbet er markeret som afsluttet.'}\n"
        "      </div>\n"
        "      <Button full onClick={onClose}>Luk</Button>\n"
        "    </div>\n"
        "  );\n"
        "\n"
        "  return (\n"
        "    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, display: 'flex', flexDirection: 'column' }}>\n"
        "      {/* Header */}\n"
        "      <div style={{ padding: '54px 20px 12px', background: '#fff', borderBottom: `1px solid ${SoS.line}` }}>",
    )

    # ─── FIX 6a: AdminBrobyggereScreen — add search state ─────────────────────
    src = apply(
        src,
        "Fix 6a: AdminBrobyggereScreen — add search state",
        "  const [filter, setFilter] = React.useState('alle');\n"
        "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
        "  const filtered = SoS_BROBYGGERE.filter(b => filter === 'alle' || b.status === filter);",
        "  const [filter, setFilter] = React.useState('alle');\n"
        "  const [selectedBb, setSelectedBb] = React.useState(null);\n"
        "  const [search, setSearch] = React.useState('');\n"
        "  const filtered = SoS_BROBYGGERE.filter(b => (filter === 'alle' || b.status === filter) && (!search || b.name.toLowerCase().includes(search.toLowerCase())));",
    )

    # Step 6b: wire search input
    src = apply(
        src,
        "Fix 6b: AdminBrobyggereScreen — wire search input value/onChange",
        "          <input placeholder=\"Søg brobygger…\" style={{",
        "          <input placeholder=\"Søg brobygger…\" value={search} onChange={e => setSearch(e.target.value)} style={{",
    )

    # ─── FIX 7: App.js — wire HistorikScreen onOpenMenneske ───────────────────
    src = apply(
        src,
        "Fix 7: App.js — wire HistorikScreen onOpenMenneske to openAppt",
        '{screen === "historik" && <HistorikScreen history={isNew ? [] : SoS_HISTORIK} onOpenMenneske={() => {}} />}',
        '{screen === "historik" && <HistorikScreen history={isNew ? [] : SoS_HISTORIK} onOpenMenneske={(id) => { const h = SoS_HISTORIK.find(x => x.menneskeId === id); if (h) openAppt(h.id); }} />}',
    )

    # ─── FIX 8a: RegistrerEfterAftale — add observations to data state ────────
    src = apply(
        src,
        "Fix 8a: RegistrerEfterAftale — add observations to initial data state",
        "    happened: null, contactCount: 1, duration: 60, feedback: 3,\n"
        "    note: '', continues: null, endReason: null,",
        "    happened: null, contactCount: 1, duration: 60, feedback: 3,\n"
        "    note: '', continues: null, endReason: null, observations: [],",
    )

    # Step 8b: replace observation chip div with interactive version
    src = apply(
        src,
        "Fix 8b: RegistrerEfterAftale — wire observation chips to state",
        "                <div key={t} style={{\n"
        "                  padding: '8px 14px', borderRadius: 999, background: '#fff',\n"
        "                  border: `1px solid ${SoS.lineSoft}`, fontFamily: SoS.sans, fontSize: 13,\n"
        "                  color: SoS.ink, cursor: 'pointer',\n"
        "                }}>{t}</div>",
        "                <div key={t} onClick={() => set('observations', data.observations.includes(t) ? data.observations.filter(x => x !== t) : [...data.observations, t])} style={{\n"
        "                  padding: '8px 14px', borderRadius: 999,\n"
        "                  background: data.observations.includes(t) ? SoS.orange + '18' : '#fff',\n"
        "                  border: `1px solid ${data.observations.includes(t) ? SoS.orange : SoS.lineSoft}`,\n"
        "                  fontFamily: SoS.sans, fontSize: 13,\n"
        "                  color: data.observations.includes(t) ? SoS.orangeDeep : SoS.ink,\n"
        "                  cursor: 'pointer',\n"
        "                }}>{t}</div>",
    )

    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(src)

    print(f"\nDone — wrote {len(src.encode('utf-8'))} bytes to {FILE}")


if __name__ == '__main__':
    main()

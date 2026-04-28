# -*- coding: utf-8 -*-
"""
patch_definitioner.py
Tilføjer "Definitioner"-fane i DesktopRapport med:
  - Indsatsniveauer og deres betingelser
  - Kontakttyper og SROI-relevans
  - Note om automatisk klassificering
"""

IN = OUT = 'Brobygger portal.html'

with open(IN, encoding='utf-8') as f:
    html = f.read()

results = []

OLD = """const DesktopRapport = () => {
  const [showExport, setShowExport] = React.useState(false);
  const [downloading, setDownloading] = React.useState(null);
  const handleDownload = (name) => { setDownloading(name); setTimeout(() => setDownloading(null), 2000); };
  return (
  <>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',"""

NEW = """const DesktopRapport = () => {
  const [showExport, setShowExport] = React.useState(false);
  const [downloading, setDownloading] = React.useState(null);
  const [rapTab, setRapTab] = React.useState('rapporter');
  const handleDownload = (name) => { setDownloading(name); setTimeout(() => setDownloading(null), 2000); };

  const RAP_TABS = [
    { id: 'rapporter',    label: 'Rapporter & eksport' },
    { id: 'definitioner', label: 'Definitioner' },
  ];

  return (
  <>
    {/* Fane-vælger */}
    <div style={{ display: 'flex', gap: 4, marginBottom: 16,
      background: SoS.creamDeep, borderRadius: 10, padding: 4 }}>
      {RAP_TABS.map(t => {
        const sel = rapTab === t.id;
        return (
          <button key={t.id} onClick={() => setRapTab(t.id)} style={{
            flex: 1, padding: '8px 0', borderRadius: 8, border: 'none',
            background: sel ? '#fff' : 'transparent',
            boxShadow: sel ? SoS.shadow.sm : 'none',
            fontFamily: SoS.sans, fontSize: 13, fontWeight: sel ? 700 : 400,
            color: sel ? SoS.ink : SoS.inkSoft, cursor: 'pointer',
            transition: 'all 0.15s',
          }}>{t.label}</button>
        );
      })}
    </div>

    {/* ── RAPPORTER-FANE ── */}
    {rapTab === 'rapporter' && <>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',"""

cnt = html.count(OLD)
html = html.replace(OLD, NEW, 1)
results.append(('DesktopRapport: tab-bar + rapporter-fane', cnt, 1))

# Luk rapporter-fane og tilfoej definitioner-fane før {showExport && ...}
OLD_END = """    {showExport && <ExportReport onClose={() => setShowExport(false)}/>}
  </>
  );
}

window.DesktopView"""

NEW_END = """    {showExport && <ExportReport onClose={() => setShowExport(false)}/>}
    </>}

    {/* ── DEFINITIONER-FANE ── */}
    {rapTab === 'definitioner' && (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

        {/* Indsatsniveauer */}
        <DSCard title="Indsatsniveauer">
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
            marginBottom: 14, lineHeight: 1.6 }}>
            Indsatsniveauet beregnes <strong>automatisk</strong> fra registrerede kontakthændelser.
            Niveauet stiger, når betingelserne opfyldes — det kan ikke manuelt sættes.
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${SoS.line}` }}>
                {['Niveau', 'Betingelse', 'SROI-relevans'].map(h => (
                  <th key={h} style={{ padding: '6px 10px', textAlign: 'left',
                    fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                    color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                {
                  niveau: 'Ingen kontakt',
                  color: '#999',
                  betingelse: '0 registrerede hændelser',
                  sroi: 'Tæller ikke',
                },
                {
                  niveau: 'Kontakt etableret',
                  color: '#6B8CAE',
                  betingelse: '≥ 1 gennemført hændelse (enhver type)',
                  sroi: 'Grunddata — bruges til intensitetsanalyse',
                },
                {
                  niveau: 'Personligt møde',
                  color: '#7FA089',
                  betingelse: '≥ 1 gennemført "Møde med brobygger"',
                  sroi: 'Kvalificeret kontakt — tæller i volumen',
                },
                {
                  niveau: 'Følgeskab',
                  color: '#E87A3E',
                  betingelse: '≥ 1 gennemført følgeskab (primær eller sekundær)',
                  sroi: 'Kerneydelse — tæller direkte i SROI-beregning',
                },
                {
                  niveau: 'Fler-aftaleforløb',
                  color: '#D64545',
                  betingelse: '≥ 2 gennemførte følgeskaber',
                  sroi: 'Højeste SROI-værdi — bruges til intensitet 2–3 / 4+',
                },
              ].map((r, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${SoS.lineSoft}` }}>
                  <td style={{ padding: '10px 10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 10, height: 10, borderRadius: 5,
                        background: r.color, flexShrink: 0 }}/>
                      <span style={{ fontFamily: SoS.sans, fontSize: 13,
                        fontWeight: 600, color: r.color }}>{r.niveau}</span>
                    </div>
                  </td>
                  <td style={{ padding: '10px 10px', fontFamily: SoS.sans,
                    fontSize: 13, color: SoS.ink }}>{r.betingelse}</td>
                  <td style={{ padding: '10px 10px', fontFamily: SoS.sans,
                    fontSize: 12, color: SoS.inkSoft, lineHeight: 1.4 }}>{r.sroi}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </DSCard>

        {/* Kontakttyper */}
        <DSCard title="Kontakttyper">
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
            marginBottom: 14, lineHeight: 1.6 }}>
            Hver kontakthændelse klassificeres med én af nedenstående typer.
            Typen afgør, om hændelsen tæller som følgeskab og i hvilken sektor.
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${SoS.line}` }}>
                {['Type', 'Beskrivelse', 'Tæller som', 'Sektor'].map(h => (
                  <th key={h} style={{ padding: '6px 10px', textAlign: 'left',
                    fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                    color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                {
                  type: 'Telefonisk kontakt',
                  color: '#6B8CAE',
                  desc: 'Opkald eller SMS-kontakt med mennesket',
                  taller: 'Kontakt',
                  sektor: '—',
                },
                {
                  type: 'Møde med brobygger',
                  color: '#7FA089',
                  desc: 'Fysisk eller digitalt møde — ikke følgeskab',
                  taller: 'Kontakt + Møde',
                  sektor: '—',
                },
                {
                  type: 'Følgeskab – primær sundhed',
                  color: '#E87A3E',
                  desc: 'Ledsagelse til praktiserende læge, tandlæge o.l.',
                  taller: 'Kontakt + Møde + Følgeskab',
                  sektor: 'Primær',
                },
                {
                  type: 'Følgeskab – sekundær sundhed',
                  color: '#D64545',
                  desc: 'Ledsagelse til sygehus, ambulatorium, speciallæge',
                  taller: 'Kontakt + Møde + Følgeskab',
                  sektor: 'Sekundær',
                },
                {
                  type: 'Andet',
                  color: '#999',
                  desc: 'Øvrige hændelser, der ikke passer i de andre kategorier',
                  taller: 'Kontakt',
                  sektor: '—',
                },
              ].map((r, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${SoS.lineSoft}` }}>
                  <td style={{ padding: '10px 10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 10, height: 10, borderRadius: 5,
                        background: r.color, flexShrink: 0 }}/>
                      <span style={{ fontFamily: SoS.sans, fontSize: 13,
                        fontWeight: 600, color: r.color }}>{r.type}</span>
                    </div>
                  </td>
                  <td style={{ padding: '10px 10px', fontFamily: SoS.sans,
                    fontSize: 13, color: SoS.ink, lineHeight: 1.4 }}>{r.desc}</td>
                  <td style={{ padding: '10px 10px', fontFamily: SoS.sans,
                    fontSize: 12, color: SoS.inkSoft }}>{r.taller}</td>
                  <td style={{ padding: '10px 10px' }}>
                    {r.sektor !== '—' ? (
                      <Pill bg={r.color + '22'} color={r.color}>{r.sektor}</Pill>
                    ) : (
                      <span style={{ fontFamily: SoS.sans, fontSize: 12,
                        color: SoS.inkMuted }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </DSCard>

        {/* SROI-intensitet */}
        <DSCard title="SROI-intensitetsklasser">
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
            marginBottom: 14, lineHeight: 1.6 }}>
            Til SROI-rapportering grupperes fler-aftaleforløb yderligere efter intensitet
            (antal gennemførte følgeskaber), da mere intensive forløb antages at have
            højere social gevinst.
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
            {[
              { label: '1 følgeskab', sublabel: 'Enkelt-forløb', desc: 'Borger er nået til følgeskab-niveau. Tæller i SROI, men indgår ikke i fler-aftaleforløb.', color: '#E87A3E' },
              { label: '2–3 følgeskaber', sublabel: 'Fler-aftaleforløb', desc: 'Vedvarende kontakt. Primær SROI-population for intensitetsanalyse.', color: '#D64545' },
              { label: '4+ følgeskaber', sublabel: 'Intensivt forløb', desc: 'Højintensivt forløb. Rapporteres separat som højeste SROI-kategori.', color: '#9B2335' },
            ].map((k, i) => (
              <div key={i} style={{ padding: 14, borderRadius: SoS.r.md,
                border: `2px solid ${k.color}22`, background: k.color + '08' }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 9, fontWeight: 700,
                  color: k.color, letterSpacing: 0.8, textTransform: 'uppercase',
                  marginBottom: 4 }}>{k.sublabel}</div>
                <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500,
                  color: k.color, marginBottom: 6 }}>{k.label}</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
                  lineHeight: 1.5 }}>{k.desc}</div>
              </div>
            ))}
          </div>
        </DSCard>

        {/* Statusdefinitioner */}
        <DSCard title="Hændelsesstatus — definitioner">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { status: 'Gennemført', color: '#7FA089', def: 'Kontakten/aftalen fandt sted som planlagt. Tæller med i alle beregninger.' },
              { status: 'Aflyst', color: '#E87A3E', def: 'Aftalen blev aflyst i god tid (af mennesket, brobygger eller koordinator). Tæller ikke som gennemført.' },
              { status: 'Udeblev', color: '#D64545', def: 'Mennesket mødte ikke op uden afbud. Registreres separat, da det kan indikere behov for ekstra opfølgning.' },
            ].map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 14, padding: 12,
                background: s.color + '08', borderRadius: SoS.r.md,
                border: `1px solid ${s.color}33` }}>
                <Pill bg={s.color + '22'} color={s.color} style={{ flexShrink: 0, alignSelf: 'flex-start' }}>
                  {s.status}
                </Pill>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.5 }}>
                  {s.def}
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, padding: 12, background: SoS.creamDeep,
            borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 12,
            color: SoS.inkSoft, lineHeight: 1.6 }}>
            <strong style={{ color: SoS.ink }}>Datagrundlag:</strong> Al klassificering sker automatisk
            ud fra registrerede hændelser. Ingen tælle-felter gemmes direkte på borgeren — data
            beregnes altid live fra event-loggen for at sikre konsistens og sporbarhed.
          </div>
        </DSCard>

      </div>
    )}
  </>
  );
}

window.DesktopView"""

cnt = html.count(OLD_END)
html = html.replace(OLD_END, NEW_END, 1)
results.append(('DesktopRapport: definitioner-fane tilfojet', cnt, 1))

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[OK] Fil gemt ({len(html.encode("utf-8")):,} bytes)')
print()
for label, before, after in results:
    status = '[OK]  ' if before == 1 and after == 1 else f'[WARN] before={before} after={after}'
    print(f'{status} {label}')

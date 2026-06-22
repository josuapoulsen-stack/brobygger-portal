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

# A) Per-menneske: filtrér på menneskeId (+ legacy navn) og vis type
sub(
"""              const logs = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]')
                .filter(l => l.navn && l.navn !== 'Ukendt' && (
                  l.navn.toLowerCase().includes((m.firstName || '').toLowerCase()) ||
                  l.navn.toLowerCase().includes((m.lastName || '').toLowerCase())));""",
"""              const _OPKTYPE = { samtale_menneske: 'Samtale', samtale_brobygger: 'Samtale (brobygger)', ringeopgave: 'Ringeopgave' };
              const _RINGELBL = { bestil_tid: 'bestil tid', forny_recept: 'forny recept', kontakt_forening: 'kontakt forening', andet: 'andet' };
              const logs = JSON.parse(localStorage.getItem('sos_opkald_log') || '[]')
                .filter(l => l.menneskeId ? l.menneskeId === m.id : (l.navn && l.navn !== 'Ukendt' && (
                  l.navn.toLowerCase().includes((m.firstName || '').toLowerCase()) ||
                  l.navn.toLowerCase().includes((m.lastName || '').toLowerCase()))));""",
"A1: per-menneske filter")

sub(
"""                        <div style={{ fontFamily: SoS.sans, fontSize: 12,
                          fontWeight: 600, color: SoS.ink }}>{l.navn}</div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11,
                          color: SoS.inkSoft, marginTop: 2 }}>{l.note}</div>""",
"""                        <div style={{ fontFamily: SoS.sans, fontSize: 12,
                          fontWeight: 600, color: SoS.ink }}>{(_OPKTYPE[l.type] || 'Opkald')}{l.underType ? ' · ' + (_RINGELBL[l.underType] || l.underType) : ''}</div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11,
                          color: SoS.inkSoft, marginTop: 2 }}>{l.note}</div>""",
"A2: per-menneske type-label")

# B) Statistik-fane: beregn opkaldsstatistik (hovedsæde-scoped)
sub(
"""      const mns      = Object.values(_MN0).filter(m => !_sc0 || m.hq === viewingHq);
      const logged   = appts.filter(a => a.brobyggerLog);""",
"""      const mns      = Object.values(_MN0).filter(m => !_sc0 || m.hq === viewingHq);
      const opkald = (() => { try { return JSON.parse(localStorage.getItem('sos_opkald_log') || '[]'); } catch (e) { return []; } })()
        .filter(l => {
          if (!_sc0) return true;
          if (l.menneskeId && _MN0[l.menneskeId]) return _MN0[l.menneskeId].hq === viewingHq;
          if (l.brobyggerId) { const b = (window.SoS_BROBYGGERE || []).find(x => x.id === l.brobyggerId); return !!b && b.hq === viewingHq; }
          return false;
        });
      const opkSamtaleM = opkald.filter(l => l.type === 'samtale_menneske' || (!l.type && l.kind === 'menneske')).length;
      const opkSamtaleB = opkald.filter(l => l.type === 'samtale_brobygger' || (!l.type && l.kind === 'brobygger')).length;
      const opkRinge    = opkald.filter(l => l.type === 'ringeopgave');
      const ringeUnder  = (() => { const o = {}; opkRinge.forEach(l => { const k = l.underType || 'andet'; o[k] = (o[k] || 0) + 1; }); return o; })();
      const RINGE_LBL   = { bestil_tid: 'Bestil tid', forny_recept: 'Forny recept', kontakt_forening: 'Kontakt forening', andet: 'Andet' };
      const logged   = appts.filter(a => a.brobyggerLog);""",
"B: beregn opkald")

# C) Render opkalds-kort øverst i statistik-fanen
sub(
"""      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

          {(() => {
            const MN = window.SoS_MENNESKER || {};""",
"""      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

          {opkald.length > 0 && (
            <DSCard title="Opkaldsstatistik">
              <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: opkRinge.length ? 12 : 0 }}>
                {[['Samtaler med mennesker', opkSamtaleM, SoS.orange],
                  ['Samtaler med brobyggere', opkSamtaleB, SoS.sky],
                  ['Ringeopgaver', opkRinge.length, SoS.sage],
                  ['Opkald i alt', opkald.length, SoS.ink]].map((k, i) => (
                  <div key={i}>
                    <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 600, color: k[2] }}>{k[1]}</div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>{k[0]}</div>
                  </div>
                ))}
              </div>
              {opkRinge.length > 0 && (
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', borderTop: `1px solid ${SoS.lineSoft}`, paddingTop: 10 }}>
                  {Object.entries(ringeUnder).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
                    <span key={k} style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.ink,
                      background: SoS.surface, border: `1px solid ${SoS.line}`, borderRadius: 999, padding: '4px 10px' }}>
                      {(RINGE_LBL[k] || k)}: {v}
                    </span>
                  ))}
                </div>
              )}
            </DSCard>
          )}

          {(() => {
            const MN = window.SoS_MENNESKER || {};""",
"C: render opkald-kort")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

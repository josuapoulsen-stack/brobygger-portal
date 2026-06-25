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

# 1) Seed → objekter med hovedsæde
sub("  samarbejdspartnere: ['Region Sjælland', 'Københavns Kommune', 'ÆHF (magistrat)'],",
    "  samarbejdspartnere: [{ navn: 'Region Sjælland', hovedsaede: 'Sjælland' }, { navn: 'Københavns Kommune', hovedsaede: 'Hovedstaden' }, { navn: 'ÆHF (magistrat)', hovedsaede: 'Aarhus' }],",
    "1: seed objekter")

# 2) Builder-migration: normalisér evt. gamle string-poster → {navn, hovedsaede:'Alle hovedsæder'}
sub("  merged.farver = (stored.farver && typeof stored.farver === 'object') ? stored.farver : {};",
    "  merged.farver = (stored.farver && typeof stored.farver === 'object') ? stored.farver : {};\n"
    "  merged.samarbejdspartnere = (merged.samarbejdspartnere || []).map(function (x) { return typeof x === 'string' ? { navn: x, hovedsaede: 'Alle hovedsæder' } : x; });",
    "2: builder migration")

# 3) STAMDATA: marker som obj (så hovedsæde-felt vises)
sub("  { key: 'samarbejdspartnere',  label: 'Samarbejdspartnere / henvisere' },",
    "  { key: 'samarbejdspartnere',  label: 'Samarbejdspartnere / henvisere', obj: true },",
    "3: STAMDATA obj")

# 4) Editor: 'Alle hovedsæder' i hovedsæde-select for samarbejdspartnere
sub("              {SoS_REFS.hovedsaeder.map(h => <option key={h} value={h}>{h}</option>)}\n            </select>\n          )}",
    "              {(kat === 'samarbejdspartnere' ? ['Alle hovedsæder'].concat(SoS_REFS.hovedsaeder) : SoS_REFS.hovedsaeder).map(h => <option key={h} value={h}>{h}</option>)}\n            </select>\n          )}",
    "4: editor alle-hovedsæder")

# 5) Editor: placeholder for samarbejdspartner-navn
sub("            placeholder={meta.obj ? 'Afdelingens navn…' : 'Ny post…'}",
    "            placeholder={meta.obj ? (kat === 'samarbejdspartnere' ? 'Navn på partner / henviser…' : 'Afdelingens navn…') : 'Ny post…'}",
    "5: editor placeholder")

# 6) Aftale-modal: filtrér efter menneskets hovedsæde + render navn
sub("                  {(SoS_REFS.samarbejdspartnere || []).map(x => <option key={x} value={x}>{x}</option>)}",
    "                  {(SoS_REFS.samarbejdspartnere || []).filter(x => {\n"
    "                    const phq = (typeof x === 'object' && x) ? x.hovedsaede : null;\n"
    "                    const m = (window.SoS_MENNESKER || {})[form.menneskeId];\n"
    "                    const mhq = m ? m.hq : null;\n"
    "                    return !phq || phq === 'Alle hovedsæder' || !mhq || phq === mhq;\n"
    "                  }).map(x => { const navn = (typeof x === 'object' && x) ? x.navn : x; return <option key={navn} value={navn}>{navn}</option>; })}",
    "6: aftale-modal filter")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

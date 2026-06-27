import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\api\openapi.yaml'
with open(P, 'r', encoding='utf-8') as f:
    c = f.read()

ok, fail = [], []
def sub(old, new, label):
    global c
    if old in c:
        c = c.replace(old, new, 1); ok.append(label)
    else:
        fail.append(label)

# 1) AftaleStatus-enum afstemt med prototypen
sub(
"""    AftaleStatus:
      type: string
      enum: [planlagt, gennemfoert, aflyst, udsat]""",
"""    AftaleStatus:
      type: string
      enum: [planlagt, gennemfoert, aflyst, udsat, kladde, pending, confirmed, afslaaet, brudt]""",
"1: AftaleStatus enum")

# 2) Nye ressource-skemaer før responses:
NEW = """    UclaSlags:
      type: string
      enum: [baseline, opfoelgning]

    OpkaldType:
      type: string
      enum: [samtale_menneske, samtale_brobygger, ringeopgave]

    Henvendelse:
      type: object
      description: En henvendelse i et menneskes forløb. Tidligste dato = førstegangshenvender.
      properties:
        id: { type: string, format: uuid }
        menneske_id: { type: string, format: uuid }
        type: { type: string, description: "Henvendertype fra stamdata (fx 'Personen selv', 'Kommune')" }
        navn: { type: string, nullable: true }
        dato: { type: string, format: date }
        note: { type: string, nullable: true }
        created_at: { type: string, format: date-time }

    UclaMaaling:
      type: object
      description: UCLA-3 ensomhedsmåling (score 3–9; lavere = mindre ensom).
      properties:
        id: { type: string, format: uuid }
        menneske_id: { type: string, format: uuid }
        slags: { $ref: "#/components/schemas/UclaSlags" }
        q1: { type: integer, nullable: true }
        q2: { type: integer, nullable: true }
        q3: { type: integer, nullable: true }
        sum: { type: integer, minimum: 3, maximum: 9 }
        dato: { type: string, format: date }
        label: { type: string, nullable: true }

    UdlaegKonto:
      type: object
      description: Brobyggers bankoplysninger til kreditor-oprettelse. Kontonr. returneres aldrig i klartekst.
      properties:
        id: { type: string, format: uuid }
        brobygger_id: { type: string, format: uuid }
        navn: { type: string }
        email: { type: string, nullable: true }
        reg_nr: { type: string }
        konto_nr_mask: { type: string, description: "Maskeret (fx '•••• 7890'); fuldt nr. kun ved autoriseret kreditor-eksport" }
        aar: { type: integer }
        kreditor_nr: { type: string, nullable: true }
        indsendt_at: { type: string, format: date-time }

    Opkald:
      type: object
      description: Logget telefonopkald. Skal kobles til menneske ELLER brobygger.
      properties:
        id: { type: string, format: uuid }
        type: { $ref: "#/components/schemas/OpkaldType" }
        under_type: { type: string, nullable: true, description: "ringeopgave: bestil_tid|forny_recept|kontakt_forening|andet" }
        menneske_id: { type: string, format: uuid, nullable: true }
        brobygger_id: { type: string, format: uuid, nullable: true }
        tlf: { type: string, nullable: true }
        note: { type: string }
        dato: { type: string, format: date }
        tid: { type: string, nullable: true }

    BeskedSkabelon:
      type: object
      description: Beskedskabelon ejet af en rådgiver; tekst kan indeholde {{flettefelter}}.
      properties:
        id: { type: string, format: uuid }
        ejer_id: { type: string, format: uuid }
        navn: { type: string }
        indsats: { type: string, enum: [alle, social, forening, sundhed] }
        tekst: { type: string }
        er_standard: { type: boolean }

    Stamdata:
      type: object
      description: Admin-redigerbart reference-data (erstatter SoS_REFS).
      properties:
        id: { type: string, format: uuid }
        kategori: { type: string, description: "hovedsaeder|afdelinger|aftaletyper|henvendere|modtagere|transportplaner|aflysningsaarsager|aflystAf|finansieringskilder|samarbejdspartnere|brobygningstyper" }
        navn: { type: string }
        hovedsaede: { type: string, nullable: true, description: "Hq-specifik; null/'Alle hovedsæder' = landsdækkende" }
        farve: { type: string, nullable: true }
        sort_order: { type: integer }
        aktiv: { type: boolean }

    Kontaktperson:
      type: object
      properties:
        id: { type: string, format: uuid }
        menneske_id: { type: string, format: uuid }
        rolle: { type: string, nullable: true }
        navn: { type: string, nullable: true }
        tlf: { type: string, nullable: true }

  responses:
    Unauthorized:"""

sub(
"""        hq:
          type: string
          nullable: true

  responses:
    Unauthorized:""",
NEW,
"2: nye skemaer")

with open(P, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

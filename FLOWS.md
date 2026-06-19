# Flows & data — Brobygger Portal

> **Levende dokument.** Opdatér når et flow eller et datafelt ændrer sig.
> Mermaid-diagrammerne renderes automatisk på GitHub.
> Sidst opdateret: juni 2026.

Dette kort viser **hvilke flows der findes i appen** (pr. rolle) og **hvilken data hvert trin genererer** — hele vejen fra en henvendelse til det rapportgrundlag systemet producerer.

---

## 1. Hovedflow — borgerens rejse (med data)

```mermaid
flowchart TD
  HENV["Henvender:<br/>borger selv · kommune · region<br/>pårørende · læge · hospital"] -->|henvendelse| INT

  subgraph S1["1 · Intake (rådgiver)"]
    INT["Registrér menneske<br/>(NyAftaleFlow / IntakeFlow)"]
    INT --> M[("Menneske<br/>SoS_MENNESKER")]
    INT --> KP["Kontaktpersoner<br/>(sagsbehandler/pårørende)"]
    INT --> SAM["Samtykke (tidsstempel)"]
  end

  M -->|"status: afventer"| S2

  subgraph S2["2 · Matching (rådgiver)"]
    MATCH["Tilknyt brobygger"]
    MATCH --> Q{"Ledig brobygger<br/>der matcher?"}
    Q -->|ja| ASSIGN["Tilknyt → status aktiv"]
    Q -->|forespørg| REQ[("Match-anmodning<br/>+ notifikation")]
    Q -->|nej| WL[("Venteliste<br/>sos_venteliste")]
  end

  REQ -->|"brobygger svarer (mobil)"| RESP{"Accepter / Afvis"}
  RESP -->|accept| ASSIGN
  RESP -->|afvis| MATCH

  ASSIGN --> S3

  subgraph S3["3 · Aftale (rådgiver)"]
    APPT["Opret aftale<br/>(DesktopApptModal)"]
    APPT --> AD[("Aftale<br/>SoS_APPOINTMENTS_BUSY")]
    APPT --> KLASS["Klassificering:<br/>aftaletype · brobygningstype<br/>henvender · modtager<br/>samarbejdspartner · finansiering"]
    APPT --> BRIEF["Briefing til brobygger<br/>(skabelon + fletning)"]
  end

  BRIEF --> AD
  AD -->|"status: pending → confirmed"| S4

  subgraph S4["4 · Gennemførsel (brobygger)"]
    LOG["Log udfald (mobil)"]
    LOG --> U{Udfald}
    U -->|gennemført| GEN["status → gennemfoert"]
    U -->|afbud| AFB["status → aflyst<br/>+ aflysningsårsag"]
    U -->|mødte ikke op| NOS["brobyggerLog (no-show)"]
    LOG --> KONT[("Kontaktlog<br/>SoS_KONTAKTER")]
  end

  KONT --> TRAP["Indsatsniveau (trappe)<br/>beregnes automatisk"]
  GEN --> S5
  AFB --> S5
  NOS --> S5

  subgraph S5["5 · Opfølgning (rådgiver)"]
    OPF["Ring & notér (dagsorden)"]
    OPF --> RO["raadgiverOpfoelgning<br/>+ brobyggerTrivsel"]
  end

  RO --> S6

  subgraph S6["6 · Afslutning (rådgiver)"]
    AFS["Afslut forløb"]
    AFS --> AFSD["status: afsluttet<br/>afslutårsag · trivsel · outcome"]
  end

  AFSD --> RAP["Rapport / dokumentation"]
  TRAP --> RAP
```

---

## 2. Rådighed & venteliste-loop (brobygger ↔ rådgiver)

```mermaid
flowchart LR
  BB["Brobygger melder<br/>ledige dage (mobil)"] --> RP[("Rådighedsplan<br/>sos_raadighedsplan")]
  RP --> CHK{"Matcher en person<br/>på ventelisten?"}
  CHK -->|ja| VM[("Venteliste-match<br/>sos_venteliste_matches")]
  VM --> DASH["Rådgiverens dagsorden:<br/>'Match nu'"]
  CHK -->|nej| IDLE["Ingen handling"]
  BB -.->|"ingen dage i 14 dage"| REMIND["Påmindelse på oversigt"]
```

---

## 3. Beskeder & notifikationer

```mermaid
flowchart LR
  R["Rådgiver"] -->|besked| BESK[("sos_beskeder")]
  B["Brobygger"] -->|besked| BESK
  BESK --> R
  BESK --> B
  SYS["System-hændelser<br/>(match · nyt-match · briefing · ny-aftale)"] --> NOTIF[("sos_notifikationer")]
  NOTIF --> B
  NOTIF --> R
```

---

## 4. Trappe-model (indsatsniveau) — hvor langt er mennesket nået

```mermaid
flowchart LR
  T0["Ingen kontakt"]:::grey --> T1["Kontakt etableret"]:::sand --> T2["Personligt møde"]:::amber --> T3["Følgeskab"]:::orange --> T4["Fler-aftaleforløb"]:::deep
  classDef grey fill:#9E9E9E,color:#fff
  classDef sand fill:#CDB89A,color:#3a2f24
  classDef amber fill:#E5A95F,color:#3a2f24
  classDef orange fill:#E8782E,color:#fff
  classDef deep fill:#C95B16,color:#fff
```

Beregnes automatisk af `calcMenneskeStats` ud fra `SoS_KONTAKTER`. Stiger mod orange = jeres mål (gennemførte brobygninger). Tidlige trin er også fremskridt — nuancen "kontakt er en succes" lever i analyser, ikke i blødere labels.

---

## 5. Data systemet genererer

| Hændelse | Data / entitet | localStorage-nøgle |
|---|---|---|
| Registrér menneske | Menneske + kontaktpersoner + samtykke | `sos_mennesker` |
| Tilknyt/forespørg brobygger | brobyggerId / matchAnmodning | `sos_mennesker`, `sos_notifikationer` |
| Sæt på venteliste | venteliste-post | `sos_venteliste` |
| Brobygger melder rådighed | ledige datoer | `sos_raadighedsplan` |
| Venteliste-match opstår | match-notifikation til rådgiver | `sos_venteliste_matches` |
| Opret/redigér aftale | Aftale + klassificering + briefing | `sos_appointments` |
| Log udfald | brobyggerLog + status + kontaktlog | `sos_appointments`, `sos_kontakter` |
| Opfølgning | raadgiverOpfoelgning + trivsel | `sos_appointments` |
| Afslut forløb | afslutårsag + trivsel + outcome | `sos_mennesker` |
| Beskeder | tovejs-tråde | `sos_beskeder` |
| Opkald-log | hurtige notater | `sos_opkald_log` |
| Stamdata (admin) | referencelister | `sos_refs` |

---

## 6. Stamdata (admin) — driver alle dropdowns

```mermaid
flowchart LR
  ADMIN["Admin: Stamdata-skærm"] --> REFS[("SoS_REFS<br/>sos_refs")]
  REFS --> D1["Hovedsæder + afdelinger"]
  REFS --> D2["Aftaletyper · brobygningstyper"]
  REFS --> D3["Henvisningstyper · modtagere"]
  REFS --> D4["Aflysningsårsager · aflyst-af · transport"]
  REFS --> D5["Samarbejdspartnere"]
  REFS --> D6["Finansieringskilder / projekter"]
  REFS -.->|bruges i| APPT["Aftale-modal + intake + filtre"]
```

---

## 7. Rapport-output (det vi trækker ud)

Aggregeres fra ovenstående — aldrig per-borger følsomme data i eksport:

- **Aktivitet:** aftaletype-fordeling, gennemførte vs. aflyste
- **Kapacitet:** aflysningsrate + top-årsager (fx "manglende brobygger")
- **Geografi:** per hovedsæde / afdeling
- **Samarbejde:** henvender / modtager / samarbejdspartner
- **Finansiering:** per finansieringskilde / projekt
- **Effekt:** trappe-fordeling (`byNiveau`), trivsel-udvikling, SROI-snapshot

---

## Skala & ydelse (designkrav)

Systemet skal kunne håndtere **+5.000 aftaler/år · +500 brobyggere · +50 medarbejdere** (akkumuleret over år → titusinder af aftaler).

| Lag | Konsekvens |
|---|---|
| **Prototype** | In-memory filtrering er fint. Reelle grænser: lister der renderer ALLE rækker (mennesker/brobyggere/kalender) hakker ved tusinder → kræver paginering/virtualisering. localStorage (~5–10 MB) rækker ikke til års-data. |
| **Scoping** | Rådgiver → eget hovedsæde/afdeling reducerer rendered rækker markant — også en ydelsesfordel, ikke kun UX. |
| **Produktion** | PostgreSQL m. indekser · server-side paginering + filtrering (scoping = WHERE-clauses) · rapporter/SROI som aggregerede queries, aldrig client-side load af alle rækker. |

> Passer allerede: normalisering, struktureret-først, scoping, aggregeret rapportering. Største åbne prototype-risiko: **listerne mangler paginering/virtualisering.**

## Sådan holdes kortet ajour
Når et flow eller felt ændres: opdatér det relevante diagram + tabel her i samme commit som kodeændringen. Diagrammerne er ren tekst (Mermaid), så de er nemme at rette.

# GDPR-compliance — SoS Brobygger Portal

**Sidst opdateret:** 2025-01-01  
**Dataansvarlig:** Støt op om en Mentalig Sundhed (SoS)  
**Databehandlere:** Microsoft Azure (EU-region), GitHub (CI/CD)  
**Kontakt:** [Udfyld DPO-kontakt her]

---

## 1. Retsgrundlag (GDPR Art. 6 + 9)

| Datatype | Retsgrundlag | Artikel |
|---|---|---|
| Navn, email, telefon (brobyggere) | Berettiget interesse + kontrakt | Art. 6(1)(b)(f) |
| Navn, kontaktoplysninger (mennesker/borgere) | Samtykke + berettiget interesse | Art. 6(1)(a)(f) |
| **Helbredsoplysninger (mennesker)** | **Udtrykkelig samtykke** | **Art. 9(2)(a)** |
| Aktivitetslog og aftaledata | Berettiget interesse (tilsyn, rapportering) | Art. 6(1)(f) |
| Azure Entra ID login-data | Kontrakt (adgangskontrol) | Art. 6(1)(b) |

---

## 2. Art. 9 — Særlige kategorier (helbredsdata)

- [ ] **Samtykke indhentes** eksplicit og separat fra almene vilkår
- [ ] **Samtykke gemmes** med tidsstempel og version i `audit_log`
- [ ] **Helbredsnoter krypteres** med `pgp_sym_encrypt()` i PostgreSQL (migration 001)
- [ ] **Krypteringsnøgle** opbevares i Azure Key Vault — IKKE i kode eller env-filer
- [ ] **Adgang til helbredsdata** logges i `audit_log` (migration 003)
- [ ] **Minimering:** Kun de helbredsoplysninger der er nødvendige for matchingen gemmes
- [ ] **Brobyggere** har IKKE adgang til helbredsnoter — kun rådgivere og admins

---

## 3. Registreredes rettigheder (Art. 15–22)

| Ret | Implementering | Status |
|---|---|---|
| Indsigt (Art. 15) | `GET /v1/mennesker/{id}` — koordinator eksporterer på anmodning | ⬜ Planlægges |
| Berigtigelse (Art. 16) | `PATCH /v1/mennesker/{id}` | ✅ API klar |
| Sletning (Art. 17) | Soft-delete + anonymisering efter 30 dage (migration 004) | ✅ Implementeret |
| Dataportabilitet (Art. 20) | JSON-eksport endpoint (tilføjes FASE 2) | ⬜ Planlægges |
| Indsigelse (Art. 21) | Manuel håndtering via koordinator | ⬜ Procedure dokumenteres |

---

## 4. Dataopbevaring og sletning

| Data | Opbevaringstid | Sletningsmekanisme |
|---|---|---|
| Aktive mennesker/borgere | Hele forløbets varighed + 1 år | Soft-delete → anonymisering (30 dage) |
| Afsluttede forløb (anonym) | 5 år (statistikformål) | Automatisk anonymisering |
| Helbredsnoter | Samme som forløb | Krypteret, slettes ved anonymisering |
| Audit-log | 5 år | `ryd_gammel_audit()` (migration 004) |
| Push-subscriptions | Til afmelding eller sletning af bruger | Kaskade-slet med bruger |
| Azure Entra ID-data | Styres af Azure / virksomhedens politik | Slet bruger i Entra ID |

---

## 5. Databehandleraftaler (DPA)

- [ ] **Microsoft Azure** — [Microsoft Online Service Terms + DPA](https://www.microsoft.com/licensing/product-licensing/products)
- [ ] **GitHub** — [GitHub DPA](https://docs.github.com/en/site-policy/privacy-policies/github-data-protection-agreement) *(kun CI/CD — ingen brugerdata)*
- [ ] **SoS interne DPA** — underbehandlere dokumenteres her

---

## 6. Tekniske sikkerhedsforanstaltninger

- [ ] **TLS 1.2+** overalt — Azure Static Web Apps + App Service enforce HTTPS
- [ ] **Azure-region:** `northeurope` eller `westeurope` — EU-data kun
- [ ] **PostgreSQL SSL** — `sslmode=require` i DATABASE_URL
- [ ] **Row-Level Security (RLS)** — brobyggere ser kun egne data (migration 004)
- [ ] **MFA obligatorisk** — Azure Entra ID Conditional Access-policy
- [ ] **Krypteringsnøgler i Key Vault** — ikke i kode eller env
- [ ] **Penetrationstest** — gennemføres inden go-live
- [ ] **Sårbarhedsscanning** — GitHub Dependabot aktiveret

---

## 7. Databrud-procedure (Art. 33)

1. Opdagelse → informér DPO inden for **1 time**
2. DPO vurderer alvor → anmeld til Datatilsynet inden for **72 timer** ved høj risiko
3. Informér berørte registrerede uden unødig forsinkelse (Art. 34) ved høj risiko for den registrerede
4. Dokumentér hændelsen i brud-log

Datatilsynets anmeldelsesportal: https://www.datatilsynet.dk/anmeld-et-databrud

---

## 8. Konsekvensanalyse (DPIA — Art. 35)

Systemet behandler **helbredsoplysninger om sårbare borgere** — DPIA er **obligatorisk**.

- [ ] DPIA påbegyndt: [dato]
- [ ] DPIA godkendt af DPO: [dato]
- [ ] DPIA sendt til Datatilsynet (forhørspligt hvis høj restrisiko): [dato]

Datatilsynets DPIA-vejledning: https://www.datatilsynet.dk/media/6562/dpia-vejledning.pdf

---

## 9. Fortegnelse over behandlingsaktiviteter (Art. 30)

| Behandling | Formål | Kategorier | Modtagere | Overførsler |
|---|---|---|---|---|
| Personregistrering (mennesker) | Matchmaking og forløbsstyring | Stamdata + helbred | Koordinatorer, brobyggere (begrænset) | Ingen (EU only) |
| Brugeradgang (brobyggere/rådgivere) | Autentifikation og autorisation | Stamdata, login-log | Microsoft Entra ID | EU |
| Kommunikation (beskeder) | Koordinering af frivilligforløb | Kommunikationsdata | Parterne i tråden | Ingen |
| Statistik og SROI | Dokumentation over for donorer | Anonymiserede aggregater | SoS ledelse, donorer | Ingen |

---

## 10. Tjekliste inden go-live

- [ ] DPA med Microsoft underskrevet
- [ ] DPIA gennemført og godkendt
- [ ] Krypteringsnøgle i Azure Key Vault (ikke i .env)
- [ ] MFA-policy aktiveret i Entra ID
- [ ] Samtykke-flow implementeret i onboarding
- [ ] Sletningsflow testet end-to-end
- [ ] Audit-log verificeret (skrives korrekt)
- [ ] Penetrationstest gennemført
- [ ] Privatlivspolitik publiceret og linket fra appen
- [ ] Personalet er oplært i håndtering af databrud

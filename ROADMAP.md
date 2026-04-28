# SoS Brobygger Portal — Roadmap & Implementeringslog
> Social Sundhed · Sidst opdateret: 2026-04-27  
> Microsoft 365: **Ja** — SoS har eksisterende M365-tenant + Azure Nonprofit-kreditter

---

## Nøglebeslutninger

| Emne | Beslutning |
|------|-----------|
| **Hvem bygger** | Claude + Josua — iterativt, ingen ekstern leverandør |
| **App-type** | Webbaseret PWA — optimeret til mobil, ingen App Store |
| **Hosting** | Azure (nonprofit-kreditter — Josua checker adgang) |
| **Auth: medarbejdere** | Microsoft SSO via Entra ID |
| **Auth: brobyggere** | Magic link → persistent session → valgfrit fingeraftryk |
| **Statistik** | Ledere og rådgivere kan trække statistik inkl. SROI |
| **Fundraising** | Prototypen bruges ikke til fundraising |

---

## Designprincipper for implementering

> **1. Sikkerhed først.**  
> Data om sårbare mennesker og frivillige skal behandles med samme omhu som et patientjournalsystem. Sikkerhed er ikke en feature — det er en forudsætning.

> **2. Færre ting, der virker upåklageligt.**  
> En brobygger der ikke kan se sin aftale kl. 9 om morgenen er et fejlslagent system — uanset hvor mange andre features der virker. Hver funktion vi vælger skal virke altid, hurtigt og uden forbehold.

> **3. Byg smalt, byg solidt — skaler senere.**  
> SoS forventes at vokse. Det betyder at vi *ikke* bygger til fremtiden nu — vi bygger noget der er nemt at udvide når behovet opstår.

**Hvad det betyder konkret:**
- Hellere ingen feature end en halvfærdig feature
- Sikkerhed og stabilitet testes grundigt inden ny funktionalitet tilføjes
- Tilføj ikke integrationer før de er efterspurgte
- Byg API'et så det er let at tilslutte nye klienter (mobil-app, kommunesystem, mv.)
- Undgå vendor lock-in på forretningslogik — Azure til infrastruktur er fint, men kernelogik skal kunne flyttes
- Ét simpelt databaseskema fremfor et "perfekt" skema med for mange relationer fra dag ét

---

## Status lige nu
Prototypen er en single-file HTML-fil med React/Babel via CDN og fiktive data.
Den bruges til at afklare flows, UI og logik — ikke til produktion.

**Aktuel filstørrelse:** ~541 KB · alle tre roller fungerer (brobygger, rådgiver, admin)

---

## 1. PROTOTYPE (det vi har)

### Færdigt ✓
- [x] Design system (farver, typografi, ikoner, tokens)
- [x] Brobygger-app: kalender, aftaledetaljer, historik, profil
- [x] Admin-desktop: oversigt, brobyggere, mennesker (tabel + søgning), brobygninger (tabel + filter), kalender, beskeder, indstillinger
- [x] Admin-mobil: arbejde, brobyggere, mennesker, kalender, beskeder, profil — alle tabs fungerer
- [x] Intake-flow: 5-trins registrering (kilde → basisinfo → behov → **brobygningsønske** → samtykke)
- [x] Brobygningsønske i intake: dato, starttidspunkt, varighed, frekvens, notat
- [x] Matching-flow: forenklet til 3 trin — vælg menneske → vælg brobygger → bekræft
- [x] Matching viser pre-udfyldte brobygningsoplysninger fra intake (ingen dobbeltindtastning)
- [x] Genbrug af tidligere brobygger: foreslås automatisk øverst med badge
- [x] BrobyggerProfilePanel: godkend/afvis afventer, pause, registrer afslutning
- [x] Følsom-data-lås: brobyggere ser kun sundhedsdata ±7 dage (konfigurerbart)
- [x] Afventer-status: nye brobyggere venter på godkendelse
- [x] Livscyklus-parametre: advarsel, pause og afslutning ved inaktivitet (konfigurerbart)
- [x] Indstillinger: HQ-info, dataadgang, livscyklus, **brobygningstyper on/off pr. HQ**, matching-frist, medarbejdere, inviter brobyggere, SROI-parametre
- [x] Matching-frist: rødAdvarsel på startskærm hvis menneske har ventet >N timer (N konfigurerbart)
- [x] Brobygninger-i-denne-uge widget på admin-dashboard
- [x] Beskeder-fanen (brobygger): to tabs — Notifikationer (handlingskort) + Beskeder (tråde)
- [x] Profil-skærm (brobygger): alle undersider fungerer (oplysninger, præferencer, privatliv, notifikationer, sprog)
- [x] Tom-state: ny brobygger uden aftaler ser velkomstskærm
- [x] Søgning: fungerer i både brobygger- og menneskelister (mobil + desktop)
- [x] Mobilnummer påkrævet for mennesker (med opt-out) og brobyggere
- [x] Al UI viser "mennesker" — ingen steder står der "borgere"

### Mangler i prototypen ✗
- [ ] **Tilgængelighed (a11y)** — ingen aria-labels, fokus-management, tastaturnavigation

### Skal fjernes inden produktion ⚠️
- [ ] **Rolle-switcher (TweaksPanel)** — "Vis prototypen som Brobygger / Rådgiver / Admin"-panelet er udelukkende til demo og præsentation. Det må **ikke** eksistere i produktionsappen — roller tildeles via Entra ID og er aldrig brugervalgte. Hele `TweaksPanel`-komponenten og `AppWithTweaks`-wrapperen skal erstattes af rigtig auth-routing.
- [ ] **Fiktive data** — alle `SoS_MENNESKER`, `SoS_BROBYGGERE`, `SoS_APPOINTMENTS_BUSY` osv. erstattes af rigtige API-kald mod databasen.
- [ ] **Hardkodet HQ** — `ownHq="Aarhus"` og `viewingHq` er hardkodet; skal komme fra brugerens token/profil.
- [ ] **Mock-beskeder og notifikationer** — `SoS_NOTIFICATIONS`, `SoS_MESSAGES` er statiske; erstattes af WebSocket eller polling.
- [ ] **localStorage-persistence** — bruges udelukkende til prototype-brugertest. Skal fjernes og erstattes af rigtige API-kald når produktionsbackend er klar. Nøgler at slette: `sos_mennesker`, `sos_brobyggere`, `sos_brobygninger`, `sos_settings`.

---

## 2. PRODUKTION — Teknisk fundament

### 2a. Backend & database
> **Hosting: Azure** — samme vendor som M365/Entra ID, EU-datacenter, dækket af nonprofit-kreditter.  
> **Nonprofit-kreditter: ~$3.500 USD/år (~24.000 DKK)** — dækker al estimeret hosting med god margin.

- [x] Azure nonprofit-kreditter tilgængelige ✓
- [ ] Aktivér Azure-abonnement under nonprofit-programmet (tjek portal.azure.com)
- [ ] **MVP-skema — kun det nødvendige:**
  - `brobyggere` (profil, status, livscyklus)
  - `mennesker` (grunddata + følsomme data krypteret)
  - `brobygninger` (kobling brobygger ↔ menneske)
  - `aftaler` (dato, aktivitet, sted)
  - `brugere` (medarbejdere med roller)
  - *Tilføj tabeller når behovet opstår — ikke på forhånd*
- [ ] REST API: FastAPI + PostgreSQL (samme stack som Bifrost)
- [ ] Migrationer fra dag ét (Alembic) — nemt at udvide skemaet ved vækst
- [ ] Datakryptering: Azure håndterer at-rest; følsomme felter (helbred) krypteres på applikationsniveau
- [ ] Backup: Azure automatisk backup, 7-dages restore (inkluderet)

### 2b. Autentificering
> **SoS bruger Microsoft 365** — dette forenkler auth betydeligt.

**Medarbejdere (rådgivere + admins)**
- [x] M365-tenant eksisterer ✓
- [ ] Opret App Registration i Azure Portal (15 min)
  - Redirect URI: `https://[app-domæne]/auth/callback`
  - Scopes: `openid`, `profile`, `email`, `User.Read`
- [ ] Brug **MSAL.js** (Microsofts officielle browser-bibliotek) til SSO
  - Medarbejdere klikker "Log ind med Microsoft" → eksisterende @socialsundhed.dk-konto
  - Ingen separat kodeord at huske
- [ ] Tildel roller via Entra ID App Roles eller security groups:
  - `SoS-Admin` → admin-adgang
  - `SoS-Raadgiver` → rådgiver-adgang
- [ ] Betinget adgang: kræv MFA for admin-rollen (anbefalet)

**Brobyggere (frivillige — har ikke org-konto)**
- [ ] **Anbefalet: Magic link via email**
  - Rådgiver inviterer → brobygger modtager link → logger ind uden kodeord
  - Kræver kun en email-adresse (privat gmail, hotmail osv. er fint)
  - Ingen app-installation nødvendig for at komme i gang
- [ ] Alternativ: SMS-engangskode (OTP) — god til dem uden email-vane
- [ ] Invitation-token gemmes i databasen med udløbsdato (48 timer)
- [ ] Ved første login: brobygger bekræfter navn + giver samtykke

**Fælles**
- [ ] Rollebaseret adgang: `brobygger` / `raadgiver` / `admin`
- [ ] Session-håndtering og token-refresh
- [ ] Logout fra alle enheder

### 2c. Frontend — fra prototype til rigtig app
- [ ] Flyt fra single-file HTML til et build-setup (forslag: Vite + React)
- [ ] PWA-manifest + service worker → brobyggere kan installere på telefon
- [ ] Push-notifikationer (Web Push API eller native via PWA)
- [ ] Responsivt design testet på rigtige enheder (Android + iOS)
- [ ] Bundle-optimering (lazy loading af admin-views)

### 2d. Integrationer
> **Princip: ingen integrationer i MVP** — bortset fra det der er nødvendigt for auth og email.  
> Tilføjes når der er et konkret behov og en bruger der efterspørger det.

**MVP (skal med)**
- [ ] **Email via Exchange Online** — magic links, bekræftelser, påmindelser
  - Kræver: `no-reply@socialsundhed.dk` postkasse + app-tilladelse i Entra

**Fase 2+ (tilføj når efterspurgt)**
- [ ] **Outlook-kalender** — Graph API, rådgivere ser aftaler i Outlook
- [ ] **SMS-gateway** — kun hvis brobyggere uden email-vane er et reelt problem i praksis
- [ ] **Microsoft Teams** — notifikationer til rådgivere via Teams-bot
- [ ] **Kommunalt system** — NEXUS, KMD eller lignende — afklar først om det overhovedet er relevant

---

## 3. GDPR & Compliance

### Lovgivning
- [ ] **Databehandleraftale** med hosting-leverandør (kræves — GDPR Art. 28)
- [ ] **Fortegnelse over behandlingsaktiviteter** (GDPR Art. 30) — hvem, hvad, hvorfor, hvor længe
- [ ] **Retsgrundlag** dokumenteret for hvert datapunkt:
  - Grunddata (navn, tlf): samtykke eller legitim interesse
  - Helbredsdata (diagnoser, udfordringer): eksplicit samtykke (Art. 9)
  - Lokaliseringsdata (mødeadresser): samtykke
- [ ] **Samtykkehåndtering** — digitalt samtykke med dato/version, kan trækkes tilbage
- [ ] **Sletningsflow** — menneske kan slettes; hvad sker med historik?
- [ ] **Dataadgang på forespørgsel** — ret til indsigt (Art. 15), berigtigelse (Art. 16)
- [ ] **Brud-procedure** — hvem gør hvad hvis data lækkes? Anmeldelse til Datatilsynet inden 72t

### Allerede implementeret i prototype
- [x] Følsom-data-lås: brobyggere ser kun helbredsdata ±7 dage (konfigurerbart)
- [x] Adgangskontrol pr. rolle
- [x] GDPR-informationsboks i intake-flow

### Mangler
- [ ] Samtykke-log i databasen (hvornår, hvad, IP/enhed)
- [ ] Automatisk sletning efter konfigurerbar periode
- [ ] Data minimering — review af hvilke felter der faktisk er nødvendige
- [ ] Privacy policy og cookiepolitik

---

## 4. ORGANISATION & DRIFT

### Inden go-live
- [ ] **Pilotgruppe** — 2-3 brobyggere + 1 rådgiver tester i 4 uger
- [ ] **Onboarding-materiale** — kort videoguide til brobyggere (de er ikke tech-savvy)
- [ ] **Supportkanal** — hvem hjælper brobyggere hvis noget ikke virker?
- [ ] **Driftsaftale** — hvem ejer kodebasen? Hvem vedligeholder? Hvem betaler hosting?

### Løbende
- [ ] Fejlrapportering og monitoring (fx Sentry)
- [ ] Analytics — brugsdata (uden at krænke privatliv)
- [ ] Versionsstyring og deploy-pipeline (GitHub Actions / Azure DevOps)
- [ ] Kvartalsvis review af adgangslister og roller

---

## 5. ÅBNE SPØRGSMÅL

| Spørgsmål | Status |
|-----------|--------|
| Bruger SoS Microsoft 365 i dag? | **Ja** ✓ |
| Hvem bygger appen? | **Claude + Josua** ✓ |
| Webbaseret eller native app? | **Webbaseret PWA** ✓ |
| Bruges til fundraising? | **Nej** ✓ |
| Azure nonprofit-kreditter aktiveret? | Josua checker — pending |
| Er der krav fra kommunen om lokal dataopbevaring? | Uafklaret |
| Er der andre systemer der skal integreres? | Uafklaret |
| Hvad er forventet antal brobyggere og mennesker ved launch? | ~500 brobyggere, 1-2 år gns. tilknytning ✓ |

---

## 6. FORESLÅET RÆKKEFØLGE

> Hver fase skal føles færdig og brugbar i sig selv — ikke som en halv løsning der venter på næste fase.

```
Fase 0 — Nu (prototype) ← vi er her
  → Brug prototype til at afklare åbne spørgsmål og vise til interessenter
  → Færdiggør de vigtigste prototype-mangler (tom-states, rådgiver-view)
  → Tag stilling til: hvornår er vi klar til at bygge rigtigt?

Fase 1 — Fundament (ca. 1 måned)
  → Aktivér Azure nonprofit-kreditter
  → App Registration i Entra ID (SSO til medarbejdere — én dag)
  → Minimalt database-skema + FastAPI skeleton
  → Magic link-flow til brobyggere
  → GDPR-databehandleraftale med Microsoft (standardaftale, tilgængelig i Azure-portalen)

Fase 2 — MVP: det der skal virke fra dag ét (ca. 2 måneder)
  KUN disse features:
  → Brobygger-app (PWA): se kalender, se aftaledetaljer, se historik
  → Admin-web: registrer menneske, opret brobygning, administrer brobyggere
  → Invitation af brobyggere via email
  → Rollebaseret adgang (brobygger / rådgiver / admin)
  → Samtykke ved oprettelse af menneske
  IKKE med i MVP:
  → Outlook-sync, Teams-notifikationer, SMS, kommunal integration

Fase 3 — Pilot (ca. 1 måned)
  → 5-10 brobyggere + 2 rådgivere i rigtig brug
  → Fejlretning baseret på faktisk feedback
  → Onboarding-guide til brobyggere

Fase 4 — Fuld launch
  → Alle brobyggere og rådgivere onboardes gradvist (ikke alle på én gang)
  → Monitoring og supportkanal på plads

Fase 5+ — Vækst (tilføjes løbende efter behov)
  → Outlook-kalender-sync
  → Rapportering og statistik
  → Eventuelle kommunale integrationer
  → Tilpasninger til nye afdelinger/HQ'er
  → Evt. native mobilapp hvis PWA ikke er nok
```

---

*Filen opdateres løbende. Åbne punkter markeres `- [ ]`, færdige `- [x]`.*

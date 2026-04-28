# Privatlivspolitik — SoS Brobygger Portal

**Version:** 1.0 (udkast — skal godkendes af DPO inden publicering)  
**Gælder fra:** [Indsæt dato]  
**Dataansvarlig:** Støt op om en Mentalig Sundhed (SoS)  
**Kontakt:** [Indsæt adresse, CVR, email]

---

## Hvem er vi?

Støt op om en Mentalig Sundhed (SoS) er en nonprofitorganisation der matcher frivillige brobyggere med mennesker, der har brug for social støtte.

Denne portal bruges af:
- **Brobyggere** — frivillige der registrerer aftaler og kommunikerer med koordinatorer
- **Rådgivere og koordinatorer** — SoS-medarbejdere der administrerer forløb
- **Administratorer** — SoS-personale med fuld adgang

---

## Hvilke data indsamler vi?

### Om brobyggere (frivillige)
- Navn, email og telefonnummer
- Tilgængelighed og typer af brobygning
- Sprog og geografisk tilknytning (HQ)
- Login-aktivitet (tidspunkter, enhedstype)

### Om mennesker (borgere i forløb)
- Navn, kontaktoplysninger, alder og køn
- Behov og ønsker til brobygningsforløb
- **Helbredsoplysninger (særlig kategori, Art. 9):** kun hvis udtrykkeligt samtykke er givet og funktionen er aktiveret af koordinatoren
- Mødehistorik og aktivitetslog (anonymiseret i statistik)

### Automatisk indsamlede data
- IP-adresse og brugeragent (til sikkerhedslog og fejlsporing)
- Sessionsdata (login-tidspunkter, handlinger — gemmes i audit-log)

---

## Retsgrundlag (GDPR Art. 6 + 9)

| Data | Retsgrundlag |
|---|---|
| Brobygger-profil | Kontrakt (frivilligaftale) |
| Kontaktoplysninger på mennesker | Samtykke |
| Helbredsoplysninger | Udtrykkelig samtykke (Art. 9(2)(a)) |
| Login og sikkerhedslog | Berettiget interesse |
| Statistik og SROI | Berettiget interesse (anonymiserede data) |

---

## Deling af data

Vi deler **ikke** personoplysninger med tredjeparter til markedsføringsformål.

**Databehandlere vi bruger:**

| Leverandør | Formål | Lokation |
|---|---|---|
| Microsoft Azure | Hosting, database, login (Entra ID) | EU (Irland/Holland) |
| GitHub | Versionsstyring af kildekode (ingen brugerdata) | USA (SCCs gælder) |

Alle Azure-tjenester er konfigureret til EU-datacentre og er underlagt Microsofts [Data Processing Agreement](https://www.microsoft.com/licensing/product-licensing/products).

---

## Opbevaring og sletning

| Data | Opbevaringstid |
|---|---|
| Aktive forløb | Hele forløbets varighed + 1 år |
| Afsluttede forløb | Anonymiseres automatisk efter 30 dage |
| Anonymiserede aktivitetsdata | Op til 5 år (statistikformål) |
| Login- og sikkerhedslog | 5 år |
| Push-notifikation subscriptions | Slettes med bruger eller ved afmelding |

---

## Dine rettigheder

Du har ret til at:

- **Indsigt (Art. 15):** Anmode om en kopi af dine personoplysninger
- **Berigtigelse (Art. 16):** Få forkerte oplysninger rettet
- **Sletning (Art. 17):** Bede om at dine data slettes ("retten til at blive glemt")
- **Dataportabilitet (Art. 20):** Modtage dine data i maskinlæsbart format
- **Indsigelse (Art. 21):** Gøre indsigelse mod behandling baseret på berettiget interesse
- **Tilbagekaldelse af samtykke:** Til enhver tid, uden at det berører lovligheden af tidligere behandling

Kontakt din koordinator eller skriv til [email] for at udøve dine rettigheder.

---

## Cookies og lokal lagring

Portalen bruger **ikke** reklamecookies eller tracking.

Vi bruger:
- **Session-token (localStorage):** Holder dig logget ind i op til 90 dage på samme enhed. Slettes ved logout.
- **Appens data (localStorage):** Midlertidige data der slettes automatisk.

---

## Sikkerhed

Vi beskytter dine data med:
- TLS 1.2+ på alle forbindelser
- Kryptering af helbredsoplysninger på databaseniveau (pgcrypto)
- MFA-krav for medarbejdere
- Rollebaseret adgangskontrol (brobyggere ser kun egne data)
- Automatisk audit-log af ændringer i følsomme data
- Regelmæssig gennemgang af adgangsrettigheder

---

## Databrud

Hvis vi opdager et databrud der påvirker dine rettigheder, vil vi:
1. Anmelde det til Datatilsynet inden for 72 timer (Art. 33)
2. Informere berørte personer uden unødig forsinkelse, hvis risikoen er høj (Art. 34)

---

## Klage

Du har ret til at klage til **Datatilsynet**:
- Web: [www.datatilsynet.dk](https://www.datatilsynet.dk)
- Telefon: +45 33 19 32 00
- Email: dt@datatilsynet.dk

---

## Ændringer

Vi opdaterer denne politik ved væsentlige ændringer i behandlingen. Den seneste version er altid tilgængelig i appen. Fortsat brug efter en ændring udgør accept af den opdaterede politik.

---

*Sidst opdateret: [Indsæt dato] — Version 1.0*

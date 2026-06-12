# Sikkerheds-checkliste — Brobygger Portal

> **Gylden regel:** Koble aldrig rigtige borgerdata på, før auth-laget (Entra ID + server-side roller) er live og verificeret. Rækkefølgen er det kritiske — ikke om endpointet er offentligt.

Baseret på to sikkerhedsgennemgange (juni 2026): en defensiv audit (6 dimensioner) og en red-team penetrationstest (18 angrebskæder). Konklusion: **intet er udnytteligt i dag** (fiktiv data, ingen aktiv backend), men mønstrene skal lukkes før produktion med rigtige data.

Status: `[ ]` = mangler · `[x]` = klaret

---

## 🔴 Gør nu — ægte lækkede secrets i offentligt repo

- [ ] Roter VAPID-nøgleparret (privatnøglen i `.env.example:33` er kryptografisk verificeret ægte og committet)
- [ ] Scrub `.env.example` fra git-historikken (BFG / `git filter-repo`) — sletning af filen alene fjerner ikke nøglen fra historik (commit `53418c8`)
- [ ] Erstat alle secrets i `.env.example` med rene placeholders (`TODO_GENERATE_DO_NOT_COMMIT`)
- [ ] Tilbagekald alle GitHub-PAT'er der har været i demo-links (`?token=`)
- [ ] Fjern `ghp_`-tokens fra lokale `.url`-genvejsfiler; brug aldrig PAT i delbare links
- [ ] Ret `.gitignore` — fjern inline `#`-kommentarer (understøttes ikke → reglerne matcher intet)
- [ ] `git rm --cached infra/parameters.json` (ligger pt. offentligt trods ignore-hensigt)

## 🟡 Auth-laget — fundamentet

- [ ] Server-side autorisation på **hver** endpoint — rolle udledes kun fra verificeret token
- [ ] Aktivér RS256 / Entra ID JWKS-validering i `backend/routers/auth.py` (er udkommenteret)
- [ ] Slet HS256 dev-stub'en (dekoder med committet dev-secret)
- [ ] Deploy-guard: backend nægter at starte med dev-secret eller FASE-1-stub når `ENVIRONMENT=production`
- [ ] Sørg for at FASE-2 ikke kan deploye med den committede/default `JWT_SECRET`
- [ ] Fjern `?rolle=` URL-param fra produktions-build
- [ ] Fjern default-`admin` boot-tilstand (appen starter pt. som admin uden login)
- [ ] Erstat MSLogin-attrappen (accepterer 6 vilkårlige cifre) med rigtigt MSAL / OAuth-PKCE-flow
- [ ] Brugerstyring: autorisér hver mutation server-side, ikke på client-side boolean

## 🟢 Transport & forsyningskæde

- [ ] SRI-hashes (`integrity=`) på alle CDN-scripts — eller self-host
- [ ] Vite-produktionsbuild — drop runtime-Babel og React dev-builds
- [ ] CSP-header der faktisk gælder på live-hosten (nuværende CSP i `staticwebapp.config.json` rammer kun den ikke-deployede Azure-host; GitHub Pages sender ingen)
- [ ] HSTS + X-Frame-Options aktiv på den rigtige host
- [ ] Fjern Gist + PAT-relay helt — erstat med Azure SignalR (planlagt)
- [ ] Verificér afsender-identitet server-side i chat (pt. fuldt client-trusted)

## 🔵 Data & GDPR

- [ ] Ingen PII i klartekst i localStorage — borgerdata hentes per-request bag auth
- [ ] Privat endpoint på PostgreSQL (kun nået fra API'et, aldrig fra internet)
- [ ] Audit-trail / logning af al adgang til Art. 9-helbredsdata
- [ ] Ret-til-sletning-værktøj (granulær sletning per borger, ikke kun "ryd alt")
- [ ] Dataopbevarings-/sletningspolitik defineret og implementeret
- [ ] Databehandleraftaler på plads for alle processorer
- [ ] Alt hosting i North/West Europe (GDPR-lokalitet)
- [ ] Reelt samtykke-flow med konsekvens (ikke dekorativ checkbox)
- [ ] Fjern fiktivt seed-data med realistiske helbredsnoter fra den offentligt serverede HTML

## ✅ Verifikation før go-live med rigtige data

- [ ] Penetrationstest gentaget mod den faktiske produktions-deployment
- [ ] Bekræftet: anonym request til ethvert data-endpoint returnerer 401/403, ikke data
- [ ] Bekræftet: ingen secrets i klartekst i frontend-bundle, repo eller git-historik
- [ ] Bekræftet: rolle kan ikke ændres client-side til at låse rigtige data op

---

*Genereret ud fra sikkerhedsaudit + red-team juni 2026. Se hukommelsesnote `brobygger-security-audit.md` for fund-detaljer.*

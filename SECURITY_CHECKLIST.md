# Sikkerheds-checkliste — Brobygger Portal

> **Gylden regel:** Koble aldrig rigtige borgerdata på, før auth-laget (Entra ID + server-side roller) er live og verificeret. Rækkefølgen er det kritiske — ikke om endpointet er offentligt.

Baseret på to sikkerhedsgennemgange (juni 2026): en defensiv audit (6 dimensioner) og en red-team penetrationstest (18 angrebskæder). Konklusion: **intet er udnytteligt i dag** (fiktiv data, ingen aktiv backend), men mønstrene skal lukkes før produktion med rigtige data.

Status: `[ ]` = mangler · `[x]` = klaret

---

## 🔴 Gør nu — ægte lækkede secrets i offentligt repo

- [x] Erstat alle secrets i `.env.example` med rene placeholders — VAPID-par placeholdered + advarsel om at generere nyt ved deploy
- [ ] **Generér nyt VAPID-par ved deploy** (`npx web-push generate-vapid-keys`) — privat nøgle KUN i Key Vault. Det gamle par er placeholdered; selve rotationen sker ved deploy.
- [ ] **Scrub `.env.example` fra git-historikken** (BFG / `git filter-repo`) — kræver force-push + din beslutning. Det gamle nøglepar ligger stadig i historik (commit `53418c8`).
- [x] Tilbagekald GitHub-PAT'er fra demo-links — fundne PAT er allerede tilbagekaldt (live-testet: HTTP 401); `.url`-filer var aldrig på remote
- [x] Ret `.gitignore` — inline `#`-kommentarer fjernet (gjorde reglerne virkningsløse)
- [x] `git rm --cached infra/parameters.json` (var tracket offentligt trods ignore-hensigt)

## 🟡 Auth-laget — fundamentet

- [ ] Server-side autorisation på **hver** endpoint — rolle udledes kun fra verificeret token
- [ ] Aktivér RS256 / Entra ID JWKS-validering i `backend/routers/auth.py` (er udkommenteret)
- [ ] Slet HS256 dev-stub'en (dekoder med committet dev-secret)
- [x] Deploy-guard: backend nægter at starte med dev-secret/HS256/TODO-config når `ENVIRONMENT=production` (`backend/config.py` → `_guard_production_secrets`, juni 2026)
- [x] FASE-2 kan ikke deploye med default `JWT_SECRET` — håndhævet af deploy-guard ovenfor (fejler ved opstart)
- [ ] `infra/main.bicep`: erstat literal placeholder-secret-værdier (`jwt-secret`, `vapid-private-key`) med Key Vault-referencer / secure params — committe aldrig secret-værdier i IaC
- [ ] Fjern `?rolle=` URL-param fra produktions-build
- [ ] Fjern default-`admin` boot-tilstand (appen starter pt. som admin uden login)
- [ ] Erstat MSLogin-attrappen (accepterer 6 vilkårlige cifre) med rigtigt MSAL / OAuth-PKCE-flow
- [ ] Brugerstyring: autorisér hver mutation server-side, ikke på client-side boolean

## 🟢 Transport & forsyningskæde

- [x] SRI-hashes (`integrity=` sha384) på alle 3 CDN-scripts + `crossorigin=anonymous` — verificeret i preview
- [~] Vite-produktionsbuild — React/ReactDOM skiftet til produktions-builds; runtime-Babel droppes først ved fuld Vite-build (FASE-2)
- [x] CSP-backstop via `<meta>` på live-hosten (script-src låst til unpkg, connect-src til api.github.com) — verificeret ingen overtrædelser. Fuld CSP-header på Azure forbliver FASE-2
- [ ] HSTS + X-Frame-Options aktiv på den rigtige host (kræver Azure — kan ikke sættes via `<meta>` på GitHub Pages)
- [ ] Fjern Gist + PAT-relay helt — erstat med Azure SignalR (planlagt)
  - [~] Midlertidig afbødning på plads: PAT fjernes fra URL'en straks efter læsning (`history.replaceState`) + konsol-advarsel i `Brobygger portal.html`. Fuld fjernelse afventer SignalR.
- [ ] Verificér afsender-identitet server-side i chat (pt. fuldt client-trusted)

## 🔵 Data & GDPR

- [ ] Ingen PII i klartekst i localStorage — borgerdata hentes per-request bag auth
- [ ] Bankoplysninger (`sos_udlaeg_konti`: reg./kontonr.) + kreditor-CSV-eksport: server-side opbevaring og rolle-tjek på eksport — ingen ægte bankdata i prototypen
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

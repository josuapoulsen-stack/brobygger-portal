import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ok, fail = [], []
def patch(path, old, new, label):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    if old in c:
        c = c.replace(old, new, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        ok.append(label)
    else:
        fail.append(label)

CFG = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\backend\config.py'
HTML = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal\Brobygger portal.html'

# 1) Backend: import model_validator
patch(CFG,
"from pydantic_settings import BaseSettings, SettingsConfigDict\nfrom functools import lru_cache",
"from pydantic_settings import BaseSettings, SettingsConfigDict\nfrom pydantic import model_validator\nfrom functools import lru_cache",
"1: import model_validator")

# 2) Backend: deploy-guard (fail closed i produktion)
patch(CFG,
"""    JWT_SECRET: str = "TODO_CHANGE_IN_PROD_min32chars_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


@lru_cache""",
"""    JWT_SECRET: str = "TODO_CHANGE_IN_PROD_min32chars_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Produktions-vagt: fail closed på usikker konfiguration ─────────────────
    # Backend NÆGTER at starte i produktion med dev-secrets/stub-config.
    @model_validator(mode="after")
    def _guard_production_secrets(self):
        if self.ENVIRONMENT == "production":
            problemer = []
            if "TODO" in self.JWT_SECRET or len(self.JWT_SECRET) < 32:
                problemer.append("JWT_SECRET (default/for kort)")
            if self.JWT_ALGORITHM == "HS256":
                problemer.append("JWT_ALGORITHM=HS256 - brug RS256 + Entra ID JWKS i prod")
            if self.AZURE_TENANT_ID.startswith("TODO") or self.AZURE_CLIENT_ID.startswith("TODO"):
                problemer.append("AZURE_TENANT_ID/AZURE_CLIENT_ID (ikke sat)")
            if "password@localhost" in self.DATABASE_URL:
                problemer.append("DATABASE_URL (default dev-vaerdi)")
            if problemer:
                raise ValueError(
                    "Usikker produktions-konfiguration - backend naegter at starte. "
                    "Ret foer deploy: " + "; ".join(problemer)
                )
        return self


@lru_cache""",
"2: deploy-guard")

# 3) Frontend: fjern PAT fra URL straks + advar
patch(HTML,
"""  const gistId = p.get('gist');    // GitHub Gist ID (valgfri)
  const token  = p.get('token');   // GitHub PAT (valgfri, kræves for Gist-skrivning)
  window.SoS_DEMO = { rolle, navn, gistId, token, active: !!rolle };""",
"""  const gistId = p.get('gist');    // GitHub Gist ID (valgfri)
  const token  = p.get('token');   // GitHub PAT (valgfri, kræves for Gist-skrivning)
  window.SoS_DEMO = { rolle, navn, gistId, token, active: !!rolle };
  // SIKKERHED (kun demo): en PAT i URL'en lækker via historik, logs og referrer.
  // Afbødning: fjern token fra adresselinjen straks efter læsning + advar.
  // FASE 2: Gist/PAT-chatten fjernes helt og erstattes af Azure SignalR.
  if (token) {
    try {
      console.warn('[SoS sikkerhed] GitHub-PAT læst fra URL — KUN demo og usikkert. Fjern Gist/PAT-chatten før produktion (erstattes af Azure SignalR).');
      p.delete('token');
      const _clean = window.location.pathname + (p.toString() ? '?' + p.toString() : '') + window.location.hash;
      window.history.replaceState(null, '', _clean);
    } catch (e) {}
  }""",
"3: PAT-stripping")

print(f"OK ({len(ok)}):")
for x in ok: print("  OK " + x)
if fail:
    print(f"FAIL ({len(fail)}):")
    for x in fail: print("  FAIL " + x)

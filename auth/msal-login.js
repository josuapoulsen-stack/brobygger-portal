/**
 * msal-login.js — Komplet MSAL login-flow til Brobygger Portal
 *
 * Erstatter den nuværende mock-MSLogin komponent i "Brobygger portal.html"
 * NÅR msal-config.js er udfyldt med rigtige Azure-værdier.
 *
 * Bruger MSAL.js v3 via CDN — ingen build-step nødvendig.
 * Tilføj følgende til <head> i HTML-filen:
 *
 *   <script src="https://alcdn.msauth.net/browser/3.23.0/js/msal-browser.min.js"></script>
 *
 * Derefter erstattes den eksisterende MSLogin-komponent med denne.
 */

// ─────────────────────────────────────────────────────────────────────────────
// MSAL-instans (singleton) — initialiseres én gang ved app-start
// ─────────────────────────────────────────────────────────────────────────────
let _msalInstance = null;

async function getMsalInstance() {
  if (_msalInstance) return _msalInstance;

  // Dynamisk import af config — skift til statisk import ved Vite-build
  const { msalConfig } = await import('./msal-config.js');

  _msalInstance = new msal.PublicClientApplication(msalConfig);
  await _msalInstance.initialize();

  // Håndter redirect-svar (ved redirect-flow i stedet for popup)
  await _msalInstance.handleRedirectPromise();

  return _msalInstance;
}

// ─────────────────────────────────────────────────────────────────────────────
// Login-funktion — bruges fra React-komponenten nedenfor
// ─────────────────────────────────────────────────────────────────────────────
export async function signIn() {
  const msalInstance = await getMsalInstance();
  const { loginRequest, getRoleFromClaims } = await import('./msal-config.js');

  try {
    // Popup-flow (bedst til PWA på mobil — ingen redirect/reload)
    const result = await msalInstance.loginPopup(loginRequest);

    const account  = result.account;
    const claims   = result.idTokenClaims;
    const role     = getRoleFromClaims(claims);
    const navn     = claims.name || account.username;
    const email    = account.username;

    return { success: true, account, role, navn, email };

  } catch (err) {
    // Bruger lukkede popup — ikke en fejl
    if (err.errorCode === "user_cancelled") {
      return { success: false, cancelled: true };
    }
    console.error("MSAL login fejl:", err);
    return { success: false, error: err.message };
  }
}

export async function signOut() {
  const msalInstance = await getMsalInstance();
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    await msalInstance.logoutPopup({ account: accounts[0] });
  }
}

export async function getActiveAccount() {
  const msalInstance = await getMsalInstance();
  const { getRoleFromClaims } = await import('./msal-config.js');

  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) return null;

  const account = accounts[0];
  const role    = getRoleFromClaims(account.idTokenClaims);
  const navn    = account.idTokenClaims?.name || account.username;

  return { account, role, navn, email: account.username };
}

export async function getAccessToken() {
  const msalInstance = await getMsalInstance();
  const { tokenRequest } = await import('./msal-config.js');

  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) throw new Error("Ikke logget ind");

  try {
    const result = await msalInstance.acquireTokenSilent({
      ...tokenRequest,
      account: accounts[0],
    });
    return result.accessToken;
  } catch {
    // Silent mislykkedes — prøv med popup (fx efter session-udløb)
    const result = await msalInstance.acquireTokenPopup({
      ...tokenRequest,
      account: accounts[0],
    });
    return result.accessToken;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// React-komponent — drop-in erstatning for mock-MSLogin i HTML-filen
// ─────────────────────────────────────────────────────────────────────────────
//
// Sådan bruges den i AppWithTweaks:
//
//   import { MSLoginReal } from './auth/msal-login.js';
//
//   // I content-blokken:
//   if (tweaks.flow === "mslogin") {
//     content = <MSLoginReal
//       onDone={(user) => {
//         // user = { role, navn, email }
//         setTweak("role", user.role);
//         setTweak("flow", "none");
//       }}
//       onCancel={() => setTweak("flow", "none")}
//     />;
//   }
//
const MSLoginReal = ({ onDone, onCancel }) => {
  const [status, setStatus] = React.useState('idle'); // idle | loading | error
  const [errorMsg, setErrorMsg] = React.useState('');

  const handleLogin = async () => {
    setStatus('loading');
    setErrorMsg('');

    const result = await signIn();

    if (result.success) {
      // Gem bruger-info i SoS_STORE til næste session
      window.SoS_STORE?.save('profile', {
        navn:  result.navn,
        email: result.email,
      });
      onDone({ role: result.role, navn: result.navn, email: result.email });
    } else if (result.cancelled) {
      setStatus('idle');
    } else {
      setStatus('error');
      setErrorMsg(result.error || 'Login mislykkedes');
    }
  };

  // Design matcher den eksisterende MSLogin mock
  return (
    <div style={{
      position: 'absolute', inset: 0, background: '#fff',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '40px 32px',
    }}>
      {/* Microsoft logo */}
      <svg width="108" height="24" viewBox="0 0 108 24" style={{ marginBottom: 32 }}>
        <rect x="0"  y="0"  width="11" height="11" fill="#F25022"/>
        <rect x="13" y="0"  width="11" height="11" fill="#7FBA00"/>
        <rect x="0"  y="13" width="11" height="11" fill="#00A4EF"/>
        <rect x="13" y="13" width="11" height="11" fill="#FFB900"/>
        <text x="32" y="17" fontFamily="Segoe UI, sans-serif" fontSize="16"
          fontWeight="400" fill="#737373">Microsoft</text>
      </svg>

      <div style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: 20,
        fontWeight: 600, color: '#2A1F17', marginBottom: 8, textAlign: 'center' }}>
        Log ind på Brobygger Portal
      </div>
      <div style={{ fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: 13,
        color: '#9B8A7A', marginBottom: 32, textAlign: 'center', lineHeight: 1.5 }}>
        Brug din arbejds- eller personlige Microsoft-konto
      </div>

      {status === 'error' && (
        <div style={{ width: '100%', padding: '12px 14px', background: '#FEE',
          border: '1px solid #FCCACA', borderRadius: 8, marginBottom: 16,
          fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: 13, color: '#C0392B' }}>
          {errorMsg}
        </div>
      )}

      <button onClick={handleLogin} disabled={status === 'loading'} style={{
        width: '100%', padding: '14px 0', borderRadius: 8,
        background: status === 'loading' ? '#E8E8E8' : '#0078D4',
        color: '#fff', border: 'none', cursor: status === 'loading' ? 'default' : 'pointer',
        fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: 15, fontWeight: 600,
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
      }}>
        {status === 'loading' ? (
          <>
            <div style={{ width: 16, height: 16, borderRadius: 8,
              border: '2px solid rgba(255,255,255,0.3)',
              borderTopColor: '#fff', animation: 'spin 0.8s linear infinite' }}/>
            Logger ind...
          </>
        ) : (
          'Log ind med Microsoft'
        )}
      </button>

      <button onClick={onCancel} style={{
        marginTop: 12, background: 'none', border: 'none',
        fontFamily: 'Plus Jakarta Sans, sans-serif', fontSize: 13,
        color: '#9B8A7A', cursor: 'pointer', padding: '8px 0',
      }}>
        Annuller
      </button>

      <div style={{ marginTop: 40, fontFamily: 'Plus Jakarta Sans, sans-serif',
        fontSize: 11, color: '#9B8A7A', textAlign: 'center', lineHeight: 1.6 }}>
        Ved at logge ind accepterer du SoS' databehandlingspolitik.<br/>
        Dine data opbevares sikkert i henhold til GDPR.
      </div>
    </div>
  );
};

// Export til brug i HTML-filen
window.MSLoginReal = MSLoginReal;

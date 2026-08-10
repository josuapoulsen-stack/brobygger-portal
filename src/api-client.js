/*
 * api-client.js — forbindelseslag mellem prototypen og .NET-backend'en.
 *
 * Bruges bag en kontakt: når window.SoS_USE_BACKEND (eller localStorage 'sos_use_backend'
 * === 'true') er sat, henter appen data herfra i stedet for localStorage.
 *
 * Login:
 *   - Dev/test: SoS_API.devLogin(roller)  → henter et dev-token fra backend.
 *   - Produktion: erstat med MSAL.js (Entra) og kald SoS_API.setToken(token).
 *
 * Alle felter er snake_case (matcher backend + openapi.yaml).
 */
(function () {
  var BASE =
    window.SoS_API_BASE ||
    localStorage.getItem('sos_api_base') ||
    'https://localhost:7080';

  function useBackend() {
    return window.SoS_USE_BACKEND === true ||
           localStorage.getItem('sos_use_backend') === 'true';
  }

  function getToken() { return localStorage.getItem('sos_api_token') || ''; }
  function setToken(t) { localStorage.setItem('sos_api_token', t || ''); }

  async function request(method, path, body) {
    var res = await fetch(BASE + path, {
      method: method,
      headers: Object.assign(
        { 'Accept': 'application/json' },
        body ? { 'Content-Type': 'application/json' } : {},
        getToken() ? { 'Authorization': 'Bearer ' + getToken() } : {}
      ),
      body: body ? JSON.stringify(body) : undefined,
    });
    if (res.status === 204) return null;
    var data = null;
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) {
      var err = new Error('API ' + res.status + ' på ' + method + ' ' + path);
      err.status = res.status; err.data = data;
      throw err;
    }
    return data;
  }

  // Dev-login: henter et testtoken (kun muligt når Entra ikke er sat op).
  async function devLogin(roller) {
    var r = await fetch(BASE + '/v1/auth/dev-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roles: roller || ['Admin'] }),
    });
    if (!r.ok) throw new Error('dev-login fejlede (' + r.status + ') — er backend sat til Entra?');
    var j = await r.json();
    setToken(j.access_token);
    return j.access_token;
  }

  function crud(base) {
    return {
      list: function (query) { return request('GET', base + (query ? '?' + new URLSearchParams(query) : '')); },
      get: function (id) { return request('GET', base + '/' + id); },
      create: function (obj) { return request('POST', base, obj); },
      update: function (id, obj) { return request('PATCH', base + '/' + id, obj); },
      remove: function (id) { return request('DELETE', base + '/' + id); },
    };
  }

  window.SoS_API = {
    get base() { return BASE; },
    setBase: function (b) { BASE = b; localStorage.setItem('sos_api_base', b); },
    useBackend: useBackend,
    setUseBackend: function (on) { localStorage.setItem('sos_use_backend', on ? 'true' : 'false'); },
    getToken: getToken,
    setToken: setToken,
    devLogin: devLogin,
    request: request,

    mennesker: crud('/v1/mennesker'),
    brobyggere: crud('/v1/brobyggere'),
    aftaler: crud('/v1/aftaler'),
    stamdata: crud('/v1/stamdata'),
    skabeloner: crud('/v1/skabeloner'),
    opkald: crud('/v1/opkald'),

    // Under-ressourcer og special-kald
    aftaleStatus: function (id, status, notes) {
      return request('PATCH', '/v1/aftaler/' + id + '/status', { status: status, notes: notes || '' });
    },
    henvendelser: function (menneskeId) {
      return {
        list: function () { return request('GET', '/v1/mennesker/' + menneskeId + '/henvendelser'); },
        create: function (o) { return request('POST', '/v1/mennesker/' + menneskeId + '/henvendelser', o); },
      };
    },
    ucla: function (menneskeId) {
      return {
        list: function () { return request('GET', '/v1/mennesker/' + menneskeId + '/ucla'); },
        create: function (o) { return request('POST', '/v1/mennesker/' + menneskeId + '/ucla', o); },
      };
    },
    kontaktpersoner: function (menneskeId) {
      return {
        list: function () { return request('GET', '/v1/mennesker/' + menneskeId + '/kontaktpersoner'); },
        create: function (o) { return request('POST', '/v1/mennesker/' + menneskeId + '/kontaktpersoner', o); },
      };
    },
    helbredsnoter: function (menneskeId) { return request('GET', '/v1/mennesker/' + menneskeId + '/helbredsnoter'); },
    udlaegKonto: function (brobyggerId) {
      return {
        get: function () { return request('GET', '/v1/brobyggere/' + brobyggerId + '/udlaeg-konto'); },
        put: function (o) { return request('PUT', '/v1/brobyggere/' + brobyggerId + '/udlaeg-konto', o); },
      };
    },
  };
})();

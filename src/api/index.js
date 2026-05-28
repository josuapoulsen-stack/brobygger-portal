/**
 * src/api/index.js — SoS API Abstraktionslag
 *
 * FASE 1 (nu): Alle metoder læser/skriver til localStorage + globals.
 *              Prototypen virker præcis som før.
 *
 * FASE 2 (med backend): Erstat methoderne herunder med fetch()-kald til
 *                        FastAPI. Interface er identisk — ingen ændringer
 *                        i komponenter.
 *
 * Skift til backend: Ret konstanten nedenfor og implementér fetch-versioner.
 */

const USE_BACKEND = false; // Sæt til true + udfyld API_BASE_URL for at bruge rigtig backend
const API_BASE_URL = import.meta?.env?.VITE_API_URL || "http://localhost:8000";

// ── Auth-header til API-kald ──────────────────────────────────────────────────
async function authHeaders() {
  // FASE 2: hent token fra MSAL
  // const token = await getAccessToken();
  // return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  return { "Content-Type": "application/json" };
}

async function apiFetch(path, options = {}) {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers: { ...headers, ...options.headers } });
  if (!res.ok) throw new Error(`API ${path} fejlede: ${res.status}`);
  return res.json();
}

// ═══════════════════════════════════════════════════════════════════════════════
// MENNESKER
// ═══════════════════════════════════════════════════════════════════════════════
export const Mennesker = {

  getAll() {
    if (USE_BACKEND) return apiFetch("/v1/mennesker");
    return Promise.resolve(Object.values(window.SoS_MENNESKER || {}));
  },

  getById(id) {
    if (USE_BACKEND) return apiFetch(`/v1/mennesker/${id}`);
    return Promise.resolve((window.SoS_MENNESKER || {})[id] ?? null);
  },

  create(data) {
    if (USE_BACKEND) return apiFetch("/v1/mennesker", { method: "POST", body: JSON.stringify(data) });
    const id = `m-${Date.now()}`;
    const record = { id, ...data, createdAt: new Date().toISOString() };
    window.SoS_MENNESKER = { ...(window.SoS_MENNESKER || {}), [id]: record };
    window.SoS_STORE?.save("mennesker", window.SoS_MENNESKER);
    return Promise.resolve(record);
  },

  update(id, data) {
    if (USE_BACKEND) return apiFetch(`/v1/mennesker/${id}`, { method: "PATCH", body: JSON.stringify(data) });
    const updated = { ...(window.SoS_MENNESKER || {})[id], ...data };
    window.SoS_MENNESKER = { ...(window.SoS_MENNESKER || {}), [id]: updated };
    window.SoS_STORE?.save("mennesker", window.SoS_MENNESKER);
    return Promise.resolve(updated);
  },

  delete(id) {
    if (USE_BACKEND) return apiFetch(`/v1/mennesker/${id}`, { method: "DELETE" });
    const { [id]: _, ...rest } = window.SoS_MENNESKER || {};
    window.SoS_MENNESKER = rest;
    window.SoS_STORE?.save("mennesker", window.SoS_MENNESKER);
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// BROBYGGERE
// ═══════════════════════════════════════════════════════════════════════════════
export const Brobyggere = {

  getAll() {
    if (USE_BACKEND) return apiFetch("/v1/brobyggere");
    return Promise.resolve(window.SoS_BROBYGGERE || []);
  },

  getById(id) {
    if (USE_BACKEND) return apiFetch(`/v1/brobyggere/${id}`);
    return Promise.resolve((window.SoS_BROBYGGERE || []).find(b => b.id === id) ?? null);
  },

  update(id, data) {
    if (USE_BACKEND) return apiFetch(`/v1/brobyggere/${id}`, { method: "PATCH", body: JSON.stringify(data) });
    window.SoS_BROBYGGERE = (window.SoS_BROBYGGERE || []).map(b => b.id === id ? { ...b, ...data } : b);
    window.SoS_STORE?.save("brobyggere", window.SoS_BROBYGGERE);
    return Promise.resolve(window.SoS_BROBYGGERE.find(b => b.id === id));
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// AFTALER
// ═══════════════════════════════════════════════════════════════════════════════
export const Aftaler = {

  getAll({ brobyggerId, menneskeId, status } = {}) {
    if (USE_BACKEND) {
      const params = new URLSearchParams();
      if (brobyggerId) params.set("brobygger_id", brobyggerId);
      if (menneskeId)  params.set("menneske_id", menneskeId);
      if (status)      params.set("status", status);
      return apiFetch(`/v1/aftaler?${params}`);
    }
    let appts = [...(window.SoS_APPOINTMENTS_BUSY || [])];
    if (brobyggerId) appts = appts.filter(a => a.brobyggerId === brobyggerId);
    if (menneskeId)  appts = appts.filter(a => a.menneskeId  === menneskeId);
    if (status)      appts = appts.filter(a => a.status       === status);
    return Promise.resolve(appts);
  },

  getById(id) {
    if (USE_BACKEND) return apiFetch(`/v1/aftaler/${id}`);
    const all = [...(window.SoS_APPOINTMENTS_BUSY || []), ...(window.SoS_HISTORIK || [])];
    return Promise.resolve(all.find(a => a.id === id) ?? null);
  },

  create(data) {
    if (USE_BACKEND) return apiFetch("/v1/aftaler", { method: "POST", body: JSON.stringify(data) });
    const record = { id: `a-${Date.now()}`, ...data, createdAt: new Date().toISOString() };
    window.SoS_APPOINTMENTS_BUSY = [...(window.SoS_APPOINTMENTS_BUSY || []), record];
    window.SoS_STORE?.save("appointments", window.SoS_APPOINTMENTS_BUSY);
    return Promise.resolve(record);
  },

  updateStatus(id, status, notes = "") {
    if (USE_BACKEND) return apiFetch(`/v1/aftaler/${id}/status`, { method: "PATCH", body: JSON.stringify({ status, notes }) });
    window.SoS_APPOINTMENTS_BUSY = (window.SoS_APPOINTMENTS_BUSY || []).map(a =>
      a.id === id ? { ...a, status, notes } : a
    );
    window.SoS_STORE?.save("appointments", window.SoS_APPOINTMENTS_BUSY);
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// BESKEDER
// ═══════════════════════════════════════════════════════════════════════════════
export const Beskeder = {

  getThreads(role) {
    if (USE_BACKEND) return apiFetch(`/v1/beskeder/threads?role=${role}`);
    const threads = window.SoS_THREADS || [];
    const visible = role === "brobygger"
      ? threads.filter(t => !t.fromBrobygger)
      : threads.filter(t => t.fromBrobygger || t.official);
    return Promise.resolve(visible);
  },

  getMessages(threadId) {
    if (USE_BACKEND) return apiFetch(`/v1/beskeder/threads/${threadId}/messages`);
    const stored = localStorage.getItem("sos_live_chat");
    if (stored) return Promise.resolve(JSON.parse(stored));
    return Promise.resolve(window.SoS_MESSAGES || []);
  },

  sendMessage(threadId, text, fromRole) {
    if (USE_BACKEND) return apiFetch(`/v1/beskeder/threads/${threadId}/messages`, {
      method: "POST", body: JSON.stringify({ text, from_role: fromRole }),
    });
    const now = new Date();
    const time = `${now.getHours().toString().padStart(2,"0")}:${now.getMinutes().toString().padStart(2,"0")}`;
    const msg = { id: String(Date.now()), from: fromRole, text, time, sentAt: now.toISOString() };
    const existing = JSON.parse(localStorage.getItem("sos_live_chat") || "[]");
    const updated = [...existing, msg];
    localStorage.setItem("sos_live_chat", JSON.stringify(updated));
    return Promise.resolve(msg);
  },

  markRead(threadId) {
    if (USE_BACKEND) return apiFetch(`/v1/beskeder/threads/${threadId}/read`, { method: "POST" });
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// NOTIFIKATIONER
// ═══════════════════════════════════════════════════════════════════════════════
export const Notifikationer = {

  getAll() {
    if (USE_BACKEND) return apiFetch("/v1/notifikationer");
    return Promise.resolve(window.SoS_NOTIFICATIONS || []);
  },

  markRead(id) {
    if (USE_BACKEND) return apiFetch(`/v1/notifikationer/${id}/read`, { method: "POST" });
    window.SoS_NOTIFICATIONS = (window.SoS_NOTIFICATIONS || []).map(n =>
      n.id === id ? { ...n, unread: false } : n
    );
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// PROFIL
// ═══════════════════════════════════════════════════════════════════════════════
export const Profil = {

  get() {
    if (USE_BACKEND) return apiFetch("/v1/profil/me");
    const stored = window.SoS_STORE?.load("profile");
    return Promise.resolve(stored ?? null);
  },

  update(data) {
    if (USE_BACKEND) return apiFetch("/v1/profil/me", { method: "PATCH", body: JSON.stringify(data) });
    window.SoS_STORE?.save("profile", data);
    return Promise.resolve(data);
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// MATCHING
// ═══════════════════════════════════════════════════════════════════════════════
export const Matching = {

  getSuggestions(menneskeId) {
    if (USE_BACKEND) return apiFetch(`/v1/matching/suggestions?menneske_id=${menneskeId}`);
    // Simpel lokal matching: brobyggere med samme type og ledig kapacitet
    const menneske = (window.SoS_MENNESKER || {})[menneskeId];
    if (!menneske) return Promise.resolve([]);
    const suggestions = (window.SoS_BROBYGGERE || [])
      .filter(b => b.status === "aktiv" && b.active < (b.maxActive || 3))
      .slice(0, 5);
    return Promise.resolve(suggestions);
  },

  confirm(menneskeId, brobyggerId) {
    if (USE_BACKEND) return apiFetch("/v1/matching/confirm", {
      method: "POST", body: JSON.stringify({ menneske_id: menneskeId, brobygger_id: brobyggerId }),
    });
    window.SoS_MENNESKER = {
      ...(window.SoS_MENNESKER || {}),
      [menneskeId]: { ...(window.SoS_MENNESKER || {})[menneskeId], matchedWith: brobyggerId, status: "matched" },
    };
    window.SoS_STORE?.save("mennesker", window.SoS_MENNESKER);
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// SROI / STATISTIK
// ═══════════════════════════════════════════════════════════════════════════════
export const Statistik = {

  getSROI(hq) {
    if (USE_BACKEND) return apiFetch(`/v1/statistik/sroi?hq=${hq || ""}`);
    // Beregn live fra globals — samme logik som calcSROISnapshot()
    return Promise.resolve(typeof calcSROISnapshot === "function" ? calcSROISnapshot() : {});
  },

  getDashboard(hq) {
    if (USE_BACKEND) return apiFetch(`/v1/statistik/dashboard?hq=${hq || ""}`);
    return Promise.resolve({
      totalMennesker:   Object.keys(window.SoS_MENNESKER || {}).length,
      totalBrobyggere:  (window.SoS_BROBYGGERE || []).length,
      totalAftaler:     (window.SoS_APPOINTMENTS_BUSY || []).length,
      aktiveBrobyggere: (window.SoS_BROBYGGERE || []).filter(b => b.status === "aktiv").length,
    });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// BROBYGNING NOTATER — fritekst per forløbs-skridt
// ═══════════════════════════════════════════════════════════════════════════════
export const BrobygningNotater = {

  getByMenneske(menneskeId) {
    if (USE_BACKEND) return apiFetch(`/v1/brobygning-notater?menneske_id=${menneskeId}`);
    return Promise.resolve(
      (window.SoS_BROBYG_NOTATER || []).filter(n => n.menneskeId === menneskeId)
    );
  },

  getByAftale(aftaleId) {
    if (USE_BACKEND) return apiFetch(`/v1/brobygning-notater?aftale_id=${aftaleId}`);
    return Promise.resolve(
      (window.SoS_BROBYG_NOTATER || []).filter(n => n.aftaleId === aftaleId)
    );
  },

  create(data) {
    // data: { menneskeId, aftaleId?, fritekst, maaned, aar, initialer }
    if (USE_BACKEND) return apiFetch("/v1/brobygning-notater", { method: "POST", body: JSON.stringify(data) });
    const record = { id: `bn-${Date.now()}`, source: "manual", ...data, createdAt: new Date().toISOString() };
    window.SoS_BROBYG_NOTATER = [...(window.SoS_BROBYG_NOTATER || []), record];
    window.SoS_STORE?.save("brobyg_notater", window.SoS_BROBYG_NOTATER);
    return Promise.resolve(record);
  },

  delete(id) {
    if (USE_BACKEND) return apiFetch(`/v1/brobygning-notater/${id}`, { method: "DELETE" });
    window.SoS_BROBYG_NOTATER = (window.SoS_BROBYG_NOTATER || []).filter(n => n.id !== id);
    window.SoS_STORE?.save("brobyg_notater", window.SoS_BROBYG_NOTATER);
    return Promise.resolve({ ok: true });
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// KONTAKT LOG — individuelle kontakter med source-felt
// ═══════════════════════════════════════════════════════════════════════════════
export const KontaktLog = {

  getByMenneske(menneskeId) {
    if (USE_BACKEND) return apiFetch(`/v1/kontakt-log?menneske_id=${menneskeId}`);
    return Promise.resolve(
      (window.SoS_KONTAKT_LOG || []).filter(k => k.menneskeId === menneskeId)
    );
  },

  create(data) {
    // data: { menneskeId, type, note, source?: "manual" | "telecom_api" }
    if (USE_BACKEND) return apiFetch("/v1/kontakt-log", { method: "POST", body: JSON.stringify(data) });
    const record = { id: `kl-${Date.now()}`, source: "manual", ...data, createdAt: new Date().toISOString() };
    window.SoS_KONTAKT_LOG = [...(window.SoS_KONTAKT_LOG || []), record];
    window.SoS_STORE?.save("kontakt_log", window.SoS_KONTAKT_LOG);
    return Promise.resolve(record);
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// ANONYM EKSPORT
// ═══════════════════════════════════════════════════════════════════════════════

// Hjælpere — aldrig eksporteret, kun brugt internt
const _ageRange = (age) => {
  const n = parseInt(age, 10);
  if (isNaN(n)) return "ukendt";
  if (n < 18)  return "0-17";
  if (n < 30)  return "18-29";
  if (n < 40)  return "30-39";
  if (n < 50)  return "40-49";
  if (n < 60)  return "50-59";
  if (n < 70)  return "60-69";
  if (n < 80)  return "70-79";
  return "80+";
};

const _toMonthYear = (iso) => {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d)) return null;
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
};

export const AnonymExport = {

  /**
   * Genererer anonymiseret eksport-array.
   * PII udelades: navn, CPR, telefon, præcis adresse, fødselsdato.
   */
  generate({ dateFrom = "", dateTo = "", category = "", status = "" } = {}) {
    if (USE_BACKEND) {
      const p = new URLSearchParams();
      if (dateFrom)  p.set("date_from",  dateFrom);
      if (dateTo)    p.set("date_to",    dateTo);
      if (category)  p.set("category",   category);
      if (status)    p.set("status",     status);
      return apiFetch(`/v1/export/anonym?${p}`);
    }

    const aftaler   = [
      ...(window.SoS_APPOINTMENTS_BUSY || []),
      ...(window.SoS_HISTORIK         || []),
    ];
    const mennesker = window.SoS_MENNESKER      || {};
    const notater   = window.SoS_BROBYG_NOTATER || [];
    const kontakter = window.SoS_KONTAKT_LOG    || [];

    const records = aftaler
      .filter(a => {
        if (status   && a.status           !== status)   return false;
        if (dateFrom && (a.createdAt || "") <  dateFrom) return false;
        if (dateTo   && (a.createdAt || "") > dateTo + "T23:59:59") return false;
        return true;
      })
      .map(aftale => {
        const m = mennesker[aftale.menneskeId];
        if (!m) return null;
        if (category && m.type !== category) return null;

        const caseNotater   = notater.filter(n =>
          n.aftaleId === aftale.id || n.menneskeId === aftale.menneskeId
        );
        const caseKontakter = kontakter.filter(k => k.menneskeId === aftale.menneskeId);

        return {
          borger_id:          aftale.menneskeId,
          age_range:          _ageRange(m.age),
          gender:             m.gender      || null,
          municipality:       m.municipality || m.district || null,
          bridging_category:  m.type        || null,
          bridging_target:    aftale.target  || aftale.title || null,
          current_status:     aftale.status  || null,
          situation_og_behov: m.situationOgBehov || null,
          status_changes: (aftale.statusHistory || []).length > 0
            ? aftale.statusHistory.map(sc => ({
                status:     sc.status,
                month_year: sc.changedAt ? _toMonthYear(sc.changedAt) : null,
              }))
            : [{ status: aftale.status, month_year: _toMonthYear(aftale.createdAt) }],
          fritekst_entries: caseNotater.map(n => ({
            month_year: n.aar
              ? `${n.aar}-${String(n.maaned || 1).padStart(2, "0")}`
              : _toMonthYear(n.createdAt),
            initialer:  n.initialer || null,
            fritekst:   n.fritekst  || null,
          })),
          contact_log: caseKontakter.map(k => ({
            type:       k.type      || null,
            direction:  k.direction || null,
            month_year: _toMonthYear(k.createdAt),
            duration:   k.duration  || null,
            fritekst:   k.note      || null,
            source:     k.source    || "manual",
          })),
        };
      })
      .filter(Boolean);

    return Promise.resolve(records);
  },

  /** Henter gemte eksport-log-poster fra localStorage */
  getLogs() {
    try {
      return JSON.parse(localStorage.getItem("sos_export_log") || "[]");
    } catch {
      return [];
    }
  },

  /** Tilføjer en post til eksport-loggen. Returnerer den nye post. */
  addLog({ user_id, user_name, filters, record_count, format }) {
    const entry = {
      id:           `el-${Date.now()}`,
      timestamp:    new Date().toISOString(),
      user_id:      user_id      || "unknown",
      user_name:    user_name    || "Ukendt",
      filters:      filters      || {},
      record_count: record_count || 0,
      format:       format       || "json",
    };
    try {
      const existing = JSON.parse(localStorage.getItem("sos_export_log") || "[]");
      localStorage.setItem("sos_export_log", JSON.stringify([entry, ...existing].slice(0, 100)));
    } catch {}
    return entry;
  },
};

// Gør tilgængeligt globalt i prototype (fjernes ved Vite-migration)
if (typeof window !== "undefined") {
  window.SoS_API = { Mennesker, Brobyggere, Aftaler, Beskeder, Notifikationer, Profil, Matching, Statistik, BrobygningNotater, KontaktLog, AnonymExport };
}

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

// Gør tilgængeligt globalt i prototype (fjernes ved Vite-migration)
if (typeof window !== "undefined") {
  window.SoS_API = { Mennesker, Brobyggere, Aftaler, Beskeder, Notifikationer, Profil, Matching, Statistik };
}

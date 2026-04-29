/**
 * src/utils/dates.js — Dato-helpers til SoS Brobygger Portal
 *
 * Alle formateringer på dansk, ingen tunge biblioteker (kun Intl API).
 */

const DA = new Intl.DateTimeFormat('da-DK');
const DA_TIME = new Intl.DateTimeFormat('da-DK', { hour: '2-digit', minute: '2-digit' });
const DA_FULL = new Intl.DateTimeFormat('da-DK', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
});
const DA_SHORT = new Intl.DateTimeFormat('da-DK', {
  day: 'numeric', month: 'short',
});

/**
 * Formatér til "mandag 12. maj 2025"
 */
export function formatDatoFull(date) {
  return DA_FULL.format(new Date(date));
}

/**
 * Formatér til "12. maj"
 */
export function formatDatoKort(date) {
  return DA_SHORT.format(new Date(date));
}

/**
 * Formatér til "14:30"
 */
export function formatTid(date) {
  return DA_TIME.format(new Date(date));
}

/**
 * Relativt tidspunkt: "i dag", "i morgen", "om 3 dage", "for 2 dage siden"
 */
export function relativtTidspunkt(date) {
  const now   = new Date();
  const d     = new Date(date);
  const diffMs = d - now;
  const diffDage = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (diffDage === 0)  return 'i dag';
  if (diffDage === 1)  return 'i morgen';
  if (diffDage === -1) return 'i går';
  if (diffDage > 1 && diffDage < 7)  return `om ${diffDage} dage`;
  if (diffDage < -1 && diffDage > -7) return `for ${Math.abs(diffDage)} dage siden`;
  return formatDatoKort(date);
}

/**
 * Tidspunkt til besked-format: "14:37" (i dag) eller "man 12. maj" (ældre)
 */
export function beskedTidspunkt(date) {
  const d   = new Date(date);
  const now = new Date();
  const sammedag = d.toDateString() === now.toDateString();
  return sammedag ? formatTid(d) : formatDatoKort(d);
}

/**
 * Timer som tekst: "1 time 30 min" / "45 min"
 */
export function formatVarighed(minutter) {
  if (minutter < 60) return `${minutter} min`;
  const h = Math.floor(minutter / 60);
  const m = minutter % 60;
  return m > 0 ? `${h} time${h > 1 ? 'r' : ''} ${m} min` : `${h} time${h > 1 ? 'r' : ''}`;
}

/**
 * Er datoen i fortiden?
 */
export function erPasseret(date) {
  return new Date(date) < new Date();
}

/**
 * Antal dage siden (negativt = fremtid)
 */
export function dageSiden(date) {
  return Math.floor((new Date() - new Date(date)) / (1000 * 60 * 60 * 24));
}

/**
 * ISO-dato-streng for i dag: "2025-06-01"
 */
export function iDagISO() {
  return new Date().toISOString().slice(0, 10);
}

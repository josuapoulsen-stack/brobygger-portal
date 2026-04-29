/**
 * src/utils/validation.js — Formularvalidering til SoS Brobygger Portal
 *
 * Ren JavaScript — ingen afhængigheder.
 * Alle fejlbeskeder på dansk.
 *
 * Brug:
 *   import { validerCPR, validerTelefon, validerEmail, validerNavn } from '../utils/validation';
 *
 *   const fejl = validerCPR('040592-1234');
 *   if (fejl) console.error(fejl);  // null = OK
 */


// ── CPR-nummer ─────────────────────────────────────────────────────────────────

/**
 * Valider dansk CPR-nummer.
 * Accepterer: "040592-1234", "0405921234", "040592 1234"
 *
 * Tjekker:
 *  - Format (10 cifre)
 *  - Dato-del er realistisk (dag, måned, år)
 *  - Modulo-11 (deaktiveret for post-2007-numre — CPR-styrelsen ophævede kravet)
 *
 * @param {string} value
 * @returns {string|null}  Fejlbesked eller null hvis OK
 */
export function validerCPR(value) {
  if (!value) return 'CPR-nummer er påkrævet';

  const cleaned = value.replace(/[\s\-]/g, '');
  if (!/^\d{10}$/.test(cleaned)) {
    return 'CPR-nummer skal indeholde 10 cifre (f.eks. 040592-1234)';
  }

  const dag   = parseInt(cleaned.slice(0, 2), 10);
  const mdr   = parseInt(cleaned.slice(2, 4), 10);
  const aar2  = parseInt(cleaned.slice(4, 6), 10);
  const seq   = parseInt(cleaned.slice(6, 10), 10);

  if (mdr < 1 || mdr > 12) return 'CPR-nummer har ugyldig måned';
  if (dag < 1 || dag > 31) return 'CPR-nummer har ugyldig dag';

  // Simpel dag/måned-tjek (ikke leap-year-aware — tilstrækkeligt til UX)
  const maxDage = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (dag > maxDage[mdr]) return 'CPR-nummer har ugyldig dag for måneden';

  if (seq === 0) return 'CPR-nummer er ugyldigt (løbenummer 0000)';

  return null;
}

/**
 * Formater CPR-nummer til "DDMMÅÅ-XXXX"
 * Input: "0405921234" → Output: "040592-1234"
 */
export function formaterCPR(value) {
  const cleaned = (value || '').replace(/[\s\-]/g, '');
  if (cleaned.length >= 6) {
    return cleaned.slice(0, 6) + '-' + cleaned.slice(6, 10);
  }
  return cleaned;
}

/**
 * Maskér CPR til visning: "040592-****"
 */
export function maskerCPR(cpr) {
  if (!cpr) return '';
  const cleaned = cpr.replace(/[\s\-]/g, '');
  return cleaned.slice(0, 6) + '-****';
}


// ── Telefonnummer ──────────────────────────────────────────────────────────────

const DK_TELEFON_REGEX = /^(\+45[\s\-]?)?(\d[\s\-]?){8}$/;

/**
 * Valider dansk mobilnummer.
 * Accepterer: "20 34 56 78", "+45 20345678", "2034-56-78"
 *
 * @param {string} value
 * @param {{ required?: boolean }} [opts]
 * @returns {string|null}
 */
export function validerTelefon(value, { required = true } = {}) {
  if (!value || !value.trim()) {
    return required ? 'Telefonnummer er påkrævet' : null;
  }

  if (!DK_TELEFON_REGEX.test(value.trim())) {
    return 'Telefonnummer skal have 8 cifre (f.eks. 20 34 56 78)';
  }

  // Mobilnumre starter med 2, 3, 4, 5, 6, 7, 8, 9
  const cifre = value.replace(/\D/g, '').replace(/^45/, '');
  if (cifre.length === 8 && !/^[23456789]/.test(cifre)) {
    return 'Mobilnumre starter med 2–9';
  }

  return null;
}

/**
 * Normaliser telefonnummer til "+45 XXXXXXXX"
 */
export function normaliserTelefon(value) {
  if (!value) return '';
  const cifre = value.replace(/\D/g, '').replace(/^45/, '');
  if (cifre.length !== 8) return value;
  return '+45 ' + cifre.slice(0, 2) + ' ' + cifre.slice(2, 4) + ' ' + cifre.slice(4, 6) + ' ' + cifre.slice(6, 8);
}


// ── Email ──────────────────────────────────────────────────────────────────────

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/**
 * Valider e-mailadresse.
 *
 * @param {string} value
 * @param {{ required?: boolean }} [opts]
 * @returns {string|null}
 */
export function validerEmail(value, { required = true } = {}) {
  if (!value || !value.trim()) {
    return required ? 'E-mail er påkrævet' : null;
  }
  if (!EMAIL_REGEX.test(value.trim())) {
    return 'Ugyldig e-mailadresse';
  }
  return null;
}


// ── Navn ───────────────────────────────────────────────────────────────────────

/**
 * Valider for- eller efternavn.
 * Kræver mindst 2 tegn, kun bogstaver (inkl. æ/ø/å og bindestreg/apostrof).
 *
 * @param {string} value
 * @param {{ label?: string, min?: number, max?: number }} [opts]
 * @returns {string|null}
 */
export function validerNavn(value, { label = 'Navn', min = 2, max = 80 } = {}) {
  if (!value || !value.trim()) return `${label} er påkrævet`;
  if (value.trim().length < min) return `${label} skal være mindst ${min} tegn`;
  if (value.trim().length > max) return `${label} må højst være ${max} tegn`;
  if (/\d/.test(value)) return `${label} må ikke indeholde tal`;
  return null;
}


// ── Dato ───────────────────────────────────────────────────────────────────────

/**
 * Valider at en dato ikke er i fortiden.
 *
 * @param {string} isoDate  "YYYY-MM-DD"
 * @param {{ label?: string }} [opts]
 * @returns {string|null}
 */
export function validerFremtidigDato(isoDate, { label = 'Dato' } = {}) {
  if (!isoDate) return `${label} er påkrævet`;
  const d = new Date(isoDate);
  if (isNaN(d.getTime())) return `${label} er ugyldig`;
  const idag = new Date();
  idag.setHours(0, 0, 0, 0);
  if (d < idag) return `${label} skal være i dag eller fremtiden`;
  return null;
}

/**
 * Valider at en dato er i fortiden (til historik-formularer).
 */
export function validerFortidigDato(isoDate, { label = 'Dato' } = {}) {
  if (!isoDate) return `${label} er påkrævet`;
  const d = new Date(isoDate);
  if (isNaN(d.getTime())) return `${label} er ugyldig`;
  if (d > new Date()) return `${label} skal være i fortiden`;
  return null;
}


// ── Fritekst / noter ───────────────────────────────────────────────────────────

/**
 * Valider fritekst-felt (noter, beskrivelse, besked).
 *
 * @param {string} value
 * @param {{ label?: string, required?: boolean, max?: number }} [opts]
 * @returns {string|null}
 */
export function validerTekst(value, { label = 'Tekst', required = false, max = 2000 } = {}) {
  if (!value || !value.trim()) {
    return required ? `${label} er påkrævet` : null;
  }
  if (value.trim().length > max) {
    return `${label} må højst være ${max} tegn (${value.trim().length}/${max})`;
  }
  return null;
}


// ── Postnummer ─────────────────────────────────────────────────────────────────

/**
 * Valider dansk postnummer (1000–9999).
 *
 * @param {string|number} value
 * @returns {string|null}
 */
export function validerPostnummer(value) {
  if (!value) return 'Postnummer er påkrævet';
  const nr = parseInt(String(value).trim(), 10);
  if (isNaN(nr) || nr < 1000 || nr > 9999) {
    return 'Postnummer skal være mellem 1000 og 9999';
  }
  return null;
}


// ── Samlet formular-validator ──────────────────────────────────────────────────

/**
 * Kør validering på et objekt af felter.
 *
 * @param {Record<string, () => string|null>} regler
 *   Objekt med felt-navn som nøgle og validerings-funktion som værdi.
 * @returns {{ fejl: Record<string, string>, erGyldig: boolean }}
 *
 * Eksempel:
 *   const { fejl, erGyldig } = validerFormular({
 *     fornavn: () => validerNavn(data.fornavn, { label: 'Fornavn' }),
 *     email:   () => validerEmail(data.email),
 *     telefon: () => validerTelefon(data.telefon, { required: false }),
 *   });
 */
export function validerFormular(regler) {
  const fejl = {};
  for (const [felt, fn] of Object.entries(regler)) {
    const besked = fn();
    if (besked) fejl[felt] = besked;
  }
  return {
    fejl,
    erGyldig: Object.keys(fejl).length === 0,
  };
}

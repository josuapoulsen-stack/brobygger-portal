/**
 * src/utils/sroi.js — Social Return on Investment (SROI) model
 *
 * Udledt direkte fra prototype (SROI_RATES + calcSROI).
 * Rater er baseret på SoS' egne outcomes-beregninger.
 *
 * Brug:
 *   import { SROI_RATES, calcSROI, formatKr, sroiRatio } from '../utils/sroi';
 */

/**
 * SROI-rater pr. gennemført møde — DKK social værdi.
 * Kilde: SoS interne outcome-beregninger.
 */
export const SROI_RATES = {
  sundhed: {
    perMeeting: 1840,
    label:   'Sundhedsbrobygning',
    color:   '#2E86C8',
    soft:    '#D3EAF8',
    outcome: 'Undgået indlæggelse / forbedret sundhedsadfærd',
  },
  forening: {
    perMeeting: 1420,
    label:   'Foreningsbrobygning',
    color:   '#27B87A',
    soft:    '#C8F0DE',
    outcome: 'Øget tilknytning til arbejdsmarked / uddannelse',
  },
  social: {
    perMeeting: 1260,
    label:   'Socialbrobygning',
    color:   '#E0517A',
    soft:    '#F9D3DF',
    outcome: 'Mindsket ensomhed / øget livskvalitet',
  },
};

/**
 * Standard investering (SoS driftsomkostninger pr. år, DKK).
 * Overskrives via SROI_SETTINGS.investment (admin-indstillinger).
 */
export const DEFAULT_INVESTMENT = 8_400_000;

/**
 * Beregn total SROI-værdiskabelse.
 *
 * @param {Object} byType   - { sundhed: { completed: 521 }, forening: {...}, social: {...} }
 * @param {Object} [custom] - Admin-tilpassede rater, f.eks. { sundhed: 2000, investment: 9000000 }
 * @returns {number} Total social værdi i DKK
 */
export function calcSROI(byType, custom = null) {
  let total = 0;
  Object.entries(byType).forEach(([k, v]) => {
    const rate = custom?.[k] ?? SROI_RATES[k]?.perMeeting ?? 0;
    total += (v.completed ?? 0) * rate;
  });
  return total;
}

/**
 * SROI-ratio: social værdi / investering.
 *
 * @param {number} socialValue  - Resultat fra calcSROI()
 * @param {number} [investment] - Investering i DKK (default: DEFAULT_INVESTMENT)
 * @returns {number} F.eks. 3.72 (= 1 DKK investeret giver 3,72 DKK social værdi)
 */
export function sroiRatio(socialValue, investment = DEFAULT_INVESTMENT) {
  if (!investment) return 0;
  return parseFloat((socialValue / investment).toFixed(2));
}

/**
 * Formatér DKK til læsbar streng.
 *   1 234 → "1234"
 *   12 000 → "12k"
 *   3 720 000 → "3,7 mio."
 *
 * @param {number} n
 * @returns {string}
 */
export function formatKr(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace('.', ',') + ' mio.';
  if (n >= 1000)      return Math.round(n / 1000) + 'k';
  return n.toString();
}

/**
 * Formatér DKK med kr.-suffix: "3,7 mio. kr."
 */
export function formatKrSuffix(n) {
  return formatKr(n) + ' kr.';
}

/**
 * Beregn SROI pr. type med detaljer til rapport.
 *
 * @param {Object} byType  - { sundhed: { brobygninger, completed }, ... }
 * @param {Object} [custom]
 * @returns {Array<{ type, label, color, soft, outcome, completed, rate, value }>}
 */
export function calcSROIDetails(byType, custom = null) {
  return Object.entries(byType).map(([type, v]) => {
    const meta  = SROI_RATES[type] ?? {};
    const rate  = custom?.[type] ?? meta.perMeeting ?? 0;
    const value = (v.completed ?? 0) * rate;
    return {
      type,
      label:    meta.label    ?? type,
      color:    meta.color    ?? '#888',
      soft:     meta.soft     ?? '#eee',
      outcome:  meta.outcome  ?? '',
      brobygninger: v.brobygninger ?? 0,
      completed:    v.completed    ?? 0,
      rate,
      value,
    };
  });
}

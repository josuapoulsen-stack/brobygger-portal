/**
 * src/styles/tokens.js — SoS Design System
 *
 * Direkte kopieret fra prototype (window.SoS_TOKENS).
 * Brug overalt i stedet for hardkodede farver/værdier.
 *
 * Import:
 *   import { SoS } from '../styles/tokens';
 *   import { colors, radii, shadows, fonts } from '../styles/tokens';
 */

export const SoS = {
  // ── Primær palette — udledt af logo #E17A3E ───────────────────────────────
  orange:     '#E87A3E',
  orangeSoft: '#F4A470',
  orangeDeep: '#B8501E',
  cream:      '#FBF5EE',
  creamDeep:  '#F3EADC',
  sand:       '#EFE3D1',

  // ── Semantiske neutraler ──────────────────────────────────────────────────
  ink:      '#2A1F17',   // primær tekst
  inkSoft:  '#6B5B4D',   // sekundær
  inkMuted: '#9B8A7A',   // tertiær
  line:     'rgba(42, 31, 23, 0.08)',
  lineSoft: 'rgba(42, 31, 23, 0.05)',

  // ── Akcenter ─────────────────────────────────────────────────────────────
  sage:     '#7FA089',   // tilgængelighed / grøn
  sageSoft: '#D9E4DA',
  rose:     '#C46A6A',   // aflyst / urgent
  roseSoft: '#F0D5D5',
  sky:      '#6B8CAE',   // info
  skySoft:  '#D6E2EC',
  sun:      '#E8B84B',   // notifikationer

  // ── HQ-farver ────────────────────────────────────────────────────────────
  hq: {
    'Sjælland':    '#C46A6A',
    'Hovedstaden': '#E87A3E',
    'Fyn':         '#E8B84B',
    'Nord':        '#6B8CAE',
    'Midt':        '#7FA089',
    'Kronjylland': '#8C6BAE',
    'Aarhus':      '#B8501E',
    'Syd':         '#4A8B7F',
    'Sydvest':     '#D98B5F',
  },

  // ── Afrunding ────────────────────────────────────────────────────────────
  r: { xs: 8, sm: 12, md: 16, lg: 20, xl: 28, pill: 999 },

  // ── Skygger ──────────────────────────────────────────────────────────────
  shadow: {
    sm:   '0 1px 2px rgba(42,31,23,0.04), 0 2px 8px rgba(42,31,23,0.04)',
    md:   '0 4px 12px rgba(42,31,23,0.06), 0 12px 32px rgba(42,31,23,0.06)',
    lg:   '0 8px 24px rgba(42,31,23,0.08), 0 24px 64px rgba(42,31,23,0.08)',
    glow: '0 8px 32px rgba(232,122,62,0.22)',
  },

  // ── Typografi ────────────────────────────────────────────────────────────
  font: "'Fraunces', ui-serif, Georgia, serif",
  sans: "'Inter', -apple-system, system-ui, sans-serif",
};

// Named exports for convenience
export const { r: radii, shadow: shadows, hq: hqColors } = SoS;
export const fonts = { serif: SoS.font, sans: SoS.sans };

/** Returnér HQ-farve med fallback */
export function hqColor(hq) {
  return SoS.hq[hq] ?? SoS.orange;
}

/** CSS-variabel-streng (bruges i global stylesheet) */
export const cssVariables = `
  :root {
    --sos-orange:      ${SoS.orange};
    --sos-cream:       ${SoS.cream};
    --sos-ink:         ${SoS.ink};
    --sos-ink-soft:    ${SoS.inkSoft};
    --sos-ink-muted:   ${SoS.inkMuted};
    --sos-sage:        ${SoS.sage};
    --sos-rose:        ${SoS.rose};
    --sos-sky:         ${SoS.sky};
    --sos-sans:        ${SoS.sans};
    --sos-font:        ${SoS.font};
    --sos-r-sm:        ${SoS.r.sm}px;
    --sos-r-md:        ${SoS.r.md}px;
    --sos-r-lg:        ${SoS.r.lg}px;
    --sos-r-pill:      ${SoS.r.pill}px;
  }
`;

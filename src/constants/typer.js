/**
 * src/constants/typer.js — Brobygningstyper
 *
 * Enkelt kilde til sandhed for de tre brobygningstyper.
 * Migreret fra prototype SoS_TYPER.
 * Bruges i frontend (ikoner, farver, labels) og backend (SROI-rates).
 */

export const TYPER = {
  sundhed: {
    id:      'sundhed',
    label:   'Sundhedsbrobygning',
    short:   'Sundhed',
    color:   '#2E86C8',
    soft:    '#D3EAF8',
    icon:    'shield',
    desc:    'Følgeordninger til læge, tandlæge, hospital og sundhedsvæsen.',
  },
  forening: {
    id:      'forening',
    label:   'Foreningsbrobygning',
    short:   'Forening',
    color:   '#27B87A',
    soft:    '#C8F0DE',
    icon:    'users',
    desc:    'Hjælp til at blive del af foreninger, fritid og fællesskaber.',
  },
  social: {
    id:      'social',
    label:   'Socialbrobygning',
    short:   'Social',
    color:   '#E0517A',
    soft:    '#F9D3DF',
    icon:    'heart',
    desc:    'Samtale, gåture, følgeskab — mod ensomhed og isolation.',
  },
};

export const TYPER_LIST = Object.values(TYPER);

/** Hent type-objekt med fallback */
export function getType(id) {
  return TYPER[id] ?? null;
}

export const DAGENS_DAG = ['SØN', 'MAN', 'TIR', 'ONS', 'TOR', 'FRE', 'LØR'];

export const HOVEDSAEDER = [
  'Sjælland', 'Hovedstaden', 'Fyn', 'Nord', 'Midt',
  'Kronjylland', 'Aarhus', 'Syd', 'Sydvest',
];

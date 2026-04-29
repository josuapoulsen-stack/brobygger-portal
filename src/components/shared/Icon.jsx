/**
 * src/components/shared/Icon.jsx — SoS ikon-bibliotek
 *
 * Direkte migreret fra prototype (Lucide-inspirerede håndtegnede stier).
 * Ingen afhængighed til lucide-react — alt er inline SVG.
 *
 * Brug:
 *   import { Icon } from '../shared';
 *   <Icon name="home" size={24} color={SoS.ink} weight={1.8} />
 *
 * Tilgængelige ikoner:
 *   home, calendar, clock, bell, user, pin, phone,
 *   chevron, chevronL, chevronD, chevronU,
 *   plus, check, x, shield, heart, note, language,
 *   accessible, sparkle, download, menu, filter,
 *   users, match, chart, lock, search, star, more
 */

import React from 'react';

const PATHS = {
  home:       <><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></>,
  calendar:   <><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></>,
  clock:      <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  bell:       <><path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 8H4c0-2 2-3 2-8z"/><path d="M10 20a2 2 0 0 0 4 0"/></>,
  user:       <><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></>,
  pin:        <><path d="M12 21s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></>,
  phone:      <><path d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A15 15 0 0 1 3 6a2 2 0 0 1 2-2z"/></>,
  chevron:    <><path d="M9 6l6 6-6 6"/></>,
  chevronL:   <><path d="M15 6l-6 6 6 6"/></>,
  chevronD:   <><path d="M6 9l6 6 6-6"/></>,
  chevronU:   <><path d="M6 15l6-6 6 6"/></>,
  plus:       <><path d="M12 5v14M5 12h14"/></>,
  check:      <><path d="M5 12l4 4 10-10"/></>,
  x:          <><path d="M6 6l12 12M18 6L6 18"/></>,
  shield:     <><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/></>,
  heart:      <><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/></>,
  note:       <><path d="M5 4h10l4 4v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M15 4v5h4M8 13h8M8 17h5"/></>,
  language:   <><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></>,
  accessible: <><circle cx="12" cy="5" r="1.5"/><path d="M8 10h8M10 10v6l-2 4M14 10v3h4l-2 7"/></>,
  sparkle:    <><path d="M12 3l1.8 4.7L18 9l-4.2 1.3L12 15l-1.8-4.7L6 9l4.2-1.3z"/><path d="M19 15l.8 2L22 18l-2.2.5L19 21l-.8-2L16 18l2.2-.5z"/></>,
  download:   <><path d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16"/></>,
  menu:       <><path d="M4 6h16M4 12h16M4 18h16"/></>,
  filter:     <><path d="M3 5h18l-7 9v5l-4 2v-7z"/></>,
  users:      <><circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-3 3-5 7-5s7 2 7 5"/><circle cx="17" cy="7" r="2.5"/><path d="M17 12c3 0 5 2 5 4"/></>,
  match:      (color) => <><circle cx="7" cy="8" r="3"/><circle cx="17" cy="8" r="3"/><path d="M10 8h4M12 14v6M9 20h6"/></>,
  chart:      <><path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></>,
  lock:       <><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></>,
  search:     <><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></>,
  star:       <><path d="M12 3l2.8 6 6.2.8-4.5 4.2 1.2 6.2L12 17l-5.7 3.2L7.5 14 3 9.8 9.2 9z"/></>,
};

// "more" ikon bruger fill — håndteres separat
function MoreIcon({ size, color, weight }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke={color} strokeWidth={weight} strokeLinecap="round" strokeLinejoin="round"
      style={{ display: 'block', flexShrink: 0 }}>
      <circle cx="5"  cy="12" r="1.5" fill={color} stroke="none"/>
      <circle cx="12" cy="12" r="1.5" fill={color} stroke="none"/>
      <circle cx="19" cy="12" r="1.5" fill={color} stroke="none"/>
    </svg>
  );
}

export function Icon({ name, size = 24, color = 'currentColor', weight = 1.8 }) {
  if (name === 'more') return <MoreIcon size={size} color={color} weight={weight} />;

  const content = typeof PATHS[name] === 'function' ? PATHS[name](color) : PATHS[name];

  if (!content) {
    // Fallback: lille cirkel for ukendte ikonnavne (nemmere at debugge end blank)
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
        stroke={color} strokeWidth={weight} style={{ display: 'block', flexShrink: 0 }}>
        <circle cx="12" cy="12" r="4" />
      </svg>
    );
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={weight}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {content}
    </svg>
  );
}

/**
 * SoS-logo — hvidt hjerte i orange/customfarvet cirkel.
 * Migreret fra prototype SSLogo.
 */
export function SSLogo({ size = 40, color = '#E87A3E', bg = null }) {
  return (
    <svg width={size} height={size} viewBox="0 0 512 512"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Brobygger Portal"
      style={{ display: 'block', flexShrink: 0 }}>
      <circle cx="256" cy="256" r="256" fill={bg || color} />
      <path
        d="M 256 400
           C 168 338, 96 288, 96 214
           C 96 162, 138 128, 184 128
           C 218 128, 244 146, 256 174
           C 268 146, 294 128, 328 128
           C 374 128, 416 162, 416 214
           C 416 288, 344 338, 256 400 Z"
        fill="#ffffff"
      />
    </svg>
  );
}

export default Icon;

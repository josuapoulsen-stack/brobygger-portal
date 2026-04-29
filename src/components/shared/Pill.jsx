/**
 * src/components/shared/Pill.jsx
 *
 * Lille badge/tag — bruges til statusvisning, filtre og labels.
 * Migreret direkte fra prototype Pill.
 *
 * Props:
 *   children — tekst
 *   bg       — string baggrundfarve (default: SoS.creamDeep)
 *   color    — string tekstfarve    (default: SoS.ink)
 *   icon     — ReactNode — ikon til venstre for tekst
 *   size     — "sm" | "md"         (default: "md")
 *   style    — object ekstra styles
 *
 * Foruddefinerede varianter via `variant` prop:
 *   "aktiv"    — grøn
 *   "ny"       — orange
 *   "pause"    — gul
 *   "inaktiv"  — grå
 *   "afventer" — gul/amber
 *   "bekræftet"— grøn
 *   "aflyst"   — rød
 *   "pending"  — amber (alias for afventer)
 *
 * Brug:
 *   <Pill variant="aktiv">Aktiv</Pill>
 *   <Pill bg={SoS.sageSoft} color={SoS.sage} icon={<Icon name="check" size={10}/>}>Bekræftet</Pill>
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

// Foruddefinerede statusvarianter — matcher prototype-farverne
const VARIANTS = {
  aktiv:      { bg: SoS.sageSoft,  color: '#3A7A54'   },
  ny:         { bg: '#FFF3E8',     color: SoS.orange  },
  pause:      { bg: '#FFF8E1',     color: '#8A6D1E'   },
  inaktiv:    { bg: SoS.lineSoft,  color: SoS.inkMuted },
  afventer:   { bg: SoS.sun + '33', color: '#8A6D1E'  },
  pending:    { bg: SoS.sun + '33', color: '#8A6D1E'  },
  bekræftet:  { bg: SoS.sageSoft,  color: '#3A7A54'   },
  aflyst:     { bg: SoS.roseSoft,  color: SoS.rose    },
  gennemfoert:{ bg: SoS.skySoft,   color: SoS.sky     },
  match:      { bg: '#FFF3E8',     color: SoS.orange  },
};

const SIZE = {
  sm: { height: 20, padding: '0 8px',  fontSize: 10 },
  md: { height: 24, padding: '0 10px', fontSize: 12 },
};

export function Pill({
  children,
  bg,
  color,
  icon,
  variant,
  size     = 'md',
  style: extraStyle = {},
}) {
  const v = variant ? (VARIANTS[variant] ?? {}) : {};
  const resolvedBg    = bg    ?? v.bg    ?? SoS.creamDeep;
  const resolvedColor = color ?? v.color ?? SoS.ink;
  const s = SIZE[size] ?? SIZE.md;

  return (
    <span
      style={{
        display:     'inline-flex',
        alignItems:  'center',
        gap:         5,
        height:      s.height,
        padding:     s.padding,
        borderRadius: 999,
        background:  resolvedBg,
        color:       resolvedColor,
        fontFamily:  SoS.sans,
        fontSize:    s.fontSize,
        fontWeight:  500,
        whiteSpace:  'nowrap',
        flexShrink:  0,
        ...extraStyle,
      }}
    >
      {icon}
      {children}
    </span>
  );
}

export default Pill;

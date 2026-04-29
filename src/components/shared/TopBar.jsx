/**
 * src/components/shared/TopBar.jsx
 *
 * Sticky top bar — bruges på alle app-skærme.
 * Migreret direkte fra prototype TopBar.
 *
 * Props:
 *   title    — string | ReactNode — stor serif-overskrift
 *   subtitle — string             — lille caps-tekst over titel
 *   leading  — ReactNode          — venstre slot (f.eks. tilbage-knap)
 *   trailing — ReactNode          — højre slot (f.eks. notifikations-knap)
 *   bg       — string             — baggrundsfarve (default: SoS.cream)
 *   style    — object             — ekstra inline styles på wrapper
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

export function TopBar({
  title,
  subtitle,
  leading,
  trailing,
  bg    = SoS.cream,
  style = {},
}) {
  return (
    <div
      style={{
        position:   'sticky',
        top:        0,
        background: bg,
        zIndex:     20,
        padding:    '54px 20px 14px',
        display:    'flex',
        alignItems: 'center',
        gap:        12,
        ...style,
      }}
    >
      {leading}

      <div style={{ flex: 1, minWidth: 0 }}>
        {subtitle && (
          <div
            style={{
              fontFamily:    SoS.sans,
              fontSize:      12,
              fontWeight:    600,
              color:         SoS.inkSoft,
              letterSpacing: 0.4,
              textTransform: 'uppercase',
            }}
          >
            {subtitle}
          </div>
        )}
        <div
          style={{
            fontFamily:    SoS.font,
            fontSize:      26,
            fontWeight:    500,
            color:         SoS.ink,
            letterSpacing: -0.3,
            lineHeight:    1.1,
          }}
        >
          {title}
        </div>
      </div>

      {trailing}
    </div>
  );
}

/**
 * SectionHead — lille sektionsoverskrift med valgfri handling.
 * Bruges inden for skærme til at adskille grupper.
 *
 * Props:
 *   title       — string
 *   action      — function — onClick til action-knap
 *   actionLabel — string   — tekst på action-knap (default: "Se alle")
 */
export function SectionHead({ title, action, actionLabel = 'Se alle' }) {
  return (
    <div
      style={{
        display:        'flex',
        alignItems:     'baseline',
        justifyContent: 'space-between',
        padding:        '0 4px',
        marginBottom:   10,
      }}
    >
      <div
        style={{
          fontFamily:    SoS.sans,
          fontSize:      13,
          fontWeight:    600,
          color:         SoS.inkSoft,
          textTransform: 'uppercase',
          letterSpacing: 0.8,
        }}
      >
        {title}
      </div>
      {action && (
        <button
          onClick={action}
          style={{
            background: 'none',
            border:     'none',
            padding:    0,
            cursor:     'pointer',
            fontFamily: SoS.sans,
            fontSize:   13,
            fontWeight: 600,
            color:      SoS.orange,
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default TopBar;

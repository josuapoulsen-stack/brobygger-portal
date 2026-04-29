/**
 * src/components/shared/EmptyState.jsx
 *
 * Bruges når en liste er tom eller et søgeresultat er tomt.
 * Matcher prototypens tomme-liste-mønster.
 *
 * Props:
 *   icon     — ReactNode — ikon eller emoji øverst
 *   title    — string    — primær besked
 *   subtitle — string    — forklarende undertekst (valgfri)
 *   action   — ReactNode — knap eller link (valgfri)
 *   compact  — boolean   — reduceret padding til brug inde i lister
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

export function EmptyState({
  icon,
  title,
  subtitle,
  action,
  compact = false,
}) {
  return (
    <div
      style={{
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        textAlign:      'center',
        padding:        compact ? '24px 16px' : '48px 24px',
        gap:            compact ? 8 : 12,
      }}
    >
      {icon && (
        <div
          style={{
            width:          compact ? 48 : 64,
            height:         compact ? 48 : 64,
            borderRadius:   '50%',
            background:     SoS.cream,
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            marginBottom:   4,
          }}
        >
          {icon}
        </div>
      )}

      <div
        style={{
          fontFamily: SoS.sans,
          fontSize:   compact ? 14 : 15,
          fontWeight: 600,
          color:      SoS.ink,
          lineHeight: 1.3,
        }}
      >
        {title}
      </div>

      {subtitle && (
        <div
          style={{
            fontFamily: SoS.sans,
            fontSize:   compact ? 12 : 13,
            color:      SoS.inkMuted,
            lineHeight: 1.5,
            maxWidth:   260,
          }}
        >
          {subtitle}
        </div>
      )}

      {action && (
        <div style={{ marginTop: compact ? 8 : 16 }}>
          {action}
        </div>
      )}
    </div>
  );
}

export default EmptyState;

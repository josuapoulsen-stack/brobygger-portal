/**
 * src/components/shared/Avatar.jsx
 *
 * Initialer-avatar — matcher prototypens Avatar-komponent 1:1.
 *
 * Props:
 *   initials  — string  (1–2 bogstaver, f.eks. "MJ" eller "T")
 *   bg        — string  baggrundfarve (default: SoS.orangeSoft)
 *   color     — string  tekstfarve   (default: SoS.orangeDeep)
 *   size      — number  diameter i px (default: 40)
 *   badge     — ReactNode — lille overlay nede-højre (f.eks. ⭐ eller online-dot)
 *   style     — extra inline styles
 *
 * Brug:
 *   <Avatar initials="MJ" bg="#D3EAF8" color="#2E86C8" size={44} />
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

export function Avatar({
  initials = '?',
  bg       = SoS.orangeSoft,
  color    = SoS.orangeDeep,
  size     = 40,
  badge    = null,
  style: extraStyle = {},
}) {
  const fontSize = Math.round(size * 0.36);

  return (
    <div
      aria-label={`Avatar: ${initials}`}
      style={{
        position:       'relative',
        width:          size,
        height:         size,
        borderRadius:   '50%',
        background:     bg,
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        flexShrink:     0,
        ...extraStyle,
      }}
    >
      <span
        style={{
          fontFamily: SoS.sans,
          fontSize,
          fontWeight: 700,
          color,
          lineHeight: 1,
          userSelect: 'none',
        }}
      >
        {String(initials).slice(0, 2).toUpperCase()}
      </span>

      {badge && (
        <div
          style={{
            position: 'absolute',
            bottom:   -2,
            right:    -2,
          }}
        >
          {badge}
        </div>
      )}
    </div>
  );
}

// ── Hjælper: online-dot badge ─────────────────────────────────────────────────
export function OnlineDot({ size = 10 }) {
  return (
    <div
      style={{
        width:        size,
        height:       size,
        borderRadius: '50%',
        background:   SoS.sage,
        border:       '2px solid #fff',
      }}
    />
  );
}

export default Avatar;

/**
 * src/components/shared/Card.jsx
 *
 * Generisk SoS kort-komponent.
 *
 * Props:
 *   padding   — string | number  (default: 16)
 *   radius    — number           (default: SoS.r.md)
 *   shadow    — "sm"|"md"|"lg"|"none"  (default: "sm")
 *   onClick   — function — gør kortet klikbart (hover-effekt tilføjes)
 *   active    — boolean — orange kant, brugt til valgte elementer
 *   disabled  — boolean — reduceret opacity
 *   bg        — string — baggrundfarve (default: "#fff")
 *   style     — extra inline styles
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

export function Card({
  children,
  padding  = 16,
  radius   = SoS.r.md,
  shadow   = 'sm',
  onClick  = null,
  active   = false,
  disabled = false,
  bg       = '#fff',
  style: extraStyle = {},
  ...rest
}) {
  const [hovered, setHovered] = React.useState(false);
  const clickable = !!onClick && !disabled;

  const shadowMap = {
    none: 'none',
    sm:   SoS.shadow.sm,
    md:   SoS.shadow.md,
    lg:   SoS.shadow.lg,
  };

  return (
    <div
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      onClick={clickable ? onClick : undefined}
      onKeyDown={clickable ? (e) => e.key === 'Enter' && onClick(e) : undefined}
      onMouseEnter={() => clickable && setHovered(true)}
      onMouseLeave={() => clickable && setHovered(false)}
      style={{
        background:   bg,
        borderRadius: radius,
        padding,
        boxShadow:    shadowMap[shadow] ?? shadowMap.sm,
        border:       active
          ? `2px solid ${SoS.orange}`
          : `1.5px solid ${hovered && clickable ? SoS.line : SoS.lineSoft}`,
        opacity:      disabled ? 0.55 : 1,
        cursor:       clickable ? 'pointer' : 'default',
        transition:   'border-color 0.15s, box-shadow 0.15s, transform 0.1s',
        transform:    hovered && clickable ? 'translateY(-1px)' : 'none',
        outline:      'none',
        ...extraStyle,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}

export default Card;

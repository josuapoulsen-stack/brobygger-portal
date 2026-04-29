/**
 * src/components/shared/Button.jsx
 *
 * SoS primær knap — dækker de varianterne der bruges i prototypen:
 *   primary  (orange, fyldt)
 *   secondary (hvid/cream, outlined)
 *   ghost    (ingen baggund, kun tekst)
 *   danger   (rose, til destruktive handlinger)
 *
 * Props:
 *   variant   — "primary" | "secondary" | "ghost" | "danger"  (default: "primary")
 *   size      — "sm" | "md" | "lg"                             (default: "md")
 *   full      — boolean — fylder forældreelementets bredde
 *   icon      — ReactNode — vises til venstre for label
 *   iconRight — ReactNode — vises til højre for label
 *   loading   — boolean — viser spinner i stedet for label
 *   disabled  — boolean
 *   onClick   — function
 *   type      — "button" | "submit" | "reset"                  (default: "button")
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

// ── Størrelses-tokens ─────────────────────────────────────────────────────────
const SIZE = {
  sm: { padding: '6px 14px',  fontSize: 12, height: 32, iconSize: 14, gap: 5,  radius: SoS.r.sm },
  md: { padding: '10px 20px', fontSize: 14, height: 42, iconSize: 16, gap: 7,  radius: SoS.r.md },
  lg: { padding: '13px 26px', fontSize: 16, height: 52, iconSize: 18, gap: 8,  radius: SoS.r.lg },
};

// ── Variant-tokens ────────────────────────────────────────────────────────────
const VARIANT = {
  primary: {
    background:        SoS.orange,
    color:             '#fff',
    border:            'none',
    hoverBackground:   SoS.orangeDeep,
    activeBackground:  SoS.orangeDeep,
    disabledBackground: SoS.sand,
    disabledColor:     SoS.inkMuted,
    shadow:            SoS.shadow.sm,
  },
  secondary: {
    background:        '#fff',
    color:             SoS.ink,
    border:            `1.5px solid ${SoS.line}`,
    hoverBackground:   SoS.cream,
    activeBackground:  SoS.creamDeep,
    disabledBackground: SoS.cream,
    disabledColor:     SoS.inkMuted,
    shadow:            SoS.shadow.sm,
  },
  ghost: {
    background:        'transparent',
    color:             SoS.ink,
    border:            'none',
    hoverBackground:   SoS.lineSoft,
    activeBackground:  SoS.line,
    disabledBackground: 'transparent',
    disabledColor:     SoS.inkMuted,
    shadow:            'none',
  },
  danger: {
    background:        SoS.rose,
    color:             '#fff',
    border:            'none',
    hoverBackground:   '#a85858',
    activeBackground:  '#8e4545',
    disabledBackground: SoS.roseSoft,
    disabledColor:     '#c46a6a99',
    shadow:            SoS.shadow.sm,
  },
};

// ── Spinner ───────────────────────────────────────────────────────────────────
function Spinner({ color }) {
  return (
    <svg
      width="16" height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      style={{
        animation: 'sos-spin 0.75s linear infinite',
        flexShrink: 0,
      }}
    >
      <circle cx="12" cy="12" r="10" opacity="0.25" />
      <path d="M12 2a10 10 0 0 1 10 10" />
      <style>{`@keyframes sos-spin { to { transform: rotate(360deg); } }`}</style>
    </svg>
  );
}

// ── Komponent ─────────────────────────────────────────────────────────────────
export function Button({
  children,
  variant  = 'primary',
  size     = 'md',
  full     = false,
  icon     = null,
  iconRight = null,
  loading  = false,
  disabled = false,
  onClick,
  type     = 'button',
  style: extraStyle = {},
  ...rest
}) {
  const [hovered, setHovered] = React.useState(false);
  const [active,  setActive]  = React.useState(false);

  const v = VARIANT[variant] ?? VARIANT.primary;
  const s = SIZE[size]       ?? SIZE.md;
  const isDisabled = disabled || loading;

  const bgColor = isDisabled
    ? v.disabledBackground
    : active   ? v.activeBackground
    : hovered  ? v.hoverBackground
    : v.background;

  const textColor = isDisabled ? v.disabledColor : v.color;

  return (
    <button
      type={type}
      disabled={isDisabled}
      onClick={onClick}
      onMouseEnter={() => !isDisabled && setHovered(true)}
      onMouseLeave={() => { setHovered(false); setActive(false); }}
      onMouseDown={() => !isDisabled && setActive(true)}
      onMouseUp={() => setActive(false)}
      style={{
        display:        'inline-flex',
        alignItems:     'center',
        justifyContent: 'center',
        gap:            s.gap,
        width:          full ? '100%' : undefined,
        height:         s.height,
        padding:        s.padding,
        fontSize:       s.fontSize,
        fontFamily:     SoS.sans,
        fontWeight:     600,
        color:          textColor,
        background:     bgColor,
        border:         v.border,
        borderRadius:   s.radius,
        boxShadow:      isDisabled ? 'none' : v.shadow,
        cursor:         isDisabled ? 'not-allowed' : 'pointer',
        transition:     'background 0.15s, box-shadow 0.15s, transform 0.08s',
        transform:      active && !isDisabled ? 'scale(0.98)' : 'scale(1)',
        userSelect:     'none',
        outline:        'none',
        whiteSpace:     'nowrap',
        ...extraStyle,
      }}
      {...rest}
    >
      {loading ? (
        <Spinner color={textColor} />
      ) : (
        <>
          {icon      && <span style={{ display: 'flex', flexShrink: 0 }}>{icon}</span>}
          {children}
          {iconRight && <span style={{ display: 'flex', flexShrink: 0 }}>{iconRight}</span>}
        </>
      )}
    </button>
  );
}

export default Button;

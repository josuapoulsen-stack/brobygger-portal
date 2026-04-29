/**
 * src/components/brobygger/BrobyggerApp.jsx
 *
 * Shell for brobygger-app'en — migreret fra prototype (App → brobygger-gren).
 *
 * FASE 1 (nu): Gengiver placeholder-skærme og TabBar.
 *              Data kommer stadig fra localStorage via src/api/index.js (USE_BACKEND=false).
 * FASE 2:      Erstat placeholder-imports med rigtige komponenter og kald apiFetch().
 *
 * Props:
 *   user       — { id, name, firstName, avatar, avatarBg, hq, azureOid }
 *   onLogout   — function — kaldes ved logout/rolleskift
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SoS } from '../../styles/tokens';

// ── Skærm-imports (FASE 1: placeholders, FASE 2: rigtige komponenter) ─────────
// import HomeScreen      from './HomeScreen';
// import KalenderScreen  from './KalenderScreen';
// import MessagesList    from './MessagesList';
// import ProfileScreen   from './ProfileScreen';

// ── API-lag ───────────────────────────────────────────────────────────────────
import { Notifikationer } from '../../api/index';

// ── Konstanter ────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'hjem',     label: 'Hjem',     icon: HomeIcon },
  { id: 'kalender', label: 'Kalender', icon: CalendarIcon },
  { id: 'historik', label: 'Historik', icon: ClockIcon },
  { id: 'notif',    label: 'Beskeder', icon: BellIcon },
  { id: 'profil',   label: 'Profil',   icon: UserIcon },
];


// ─────────────────────────────────────────────────────────────────────────────
//  Hoved-komponent
// ─────────────────────────────────────────────────────────────────────────────

export function BrobyggerApp({ user, onLogout }) {
  const [screen,    setScreen]    = useState('hjem');
  const [detailId,  setDetailId]  = useState(null);
  const [msgOpenId, setMsgOpenId] = useState(null);
  const [unread,    setUnread]    = useState(0);

  // Hent ulæste notifikationer
  useEffect(() => {
    Notifikationer.list()
      .then(data => setUnread((data || []).filter(n => !n.laest).length))
      .catch(() => {});
  }, [screen]);   // re-check ved tab-skift

  const navigate = useCallback((s) => {
    setDetailId(null);
    setMsgOpenId(null);
    setScreen(s);
  }, []);

  // ── Render screen content ─────────────────────────────────────────────────
  const renderScreen = () => {
    if (detailId) {
      return (
        <PlaceholderScreen
          title="Aftaledetaljer"
          description={`Aftale-ID: ${detailId}\nFASE 2: AppointmentDetailScreen migreres hertil.`}
          onBack={() => setDetailId(null)}
        />
      );
    }

    switch (screen) {
      case 'hjem':
        return (
          <PlaceholderScreen
            title="Hjem"
            description={`Velkommen, ${user?.firstName ?? 'brobygger'}!\n\nFASE 2: HomeScreen migreres hertil.\nViser kommende aftaler, tilgængelighed og notifikationer.`}
          />
        );
      case 'kalender':
        return (
          <PlaceholderScreen
            title="Kalender"
            description="FASE 2: KalenderScreen migreres hertil.\nMed måneds-/ugeoversigt og vagtstyring."
          />
        );
      case 'historik':
        return (
          <PlaceholderScreen
            title="Historik"
            description="FASE 2: HistorikScreen migreres hertil.\nTidligere aftaler og kontakter."
          />
        );
      case 'notif':
        if (msgOpenId) {
          return (
            <PlaceholderScreen
              title="Beskedtråd"
              description={`Tråd-ID: ${msgOpenId}\nFASE 2: MessageThread migreres hertil.`}
              onBack={() => setMsgOpenId(null)}
            />
          );
        }
        return (
          <PlaceholderScreen
            title="Beskeder"
            description="FASE 2: MessagesList + SignalR migreres hertil.\nNotifikationer og chat med koordinator."
          />
        );
      case 'profil':
        return (
          <PlaceholderScreen
            title="Profil"
            description="FASE 2: ProfileScreen migreres hertil.\nTilgængelighed, sprog, brobygningstyper."
            action={onLogout ? { label: 'Log ud', onClick: onLogout } : null}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div
      style={{
        position:   'relative',
        width:      '100%',
        height:     '100%',
        background: SoS.cream,
        overflow:   'hidden',
        display:    'flex',
        flexDirection: 'column',
      }}
    >
      {/* Scrollbar indhold */}
      <div
        style={{
          flex:       1,
          overflowY:  'auto',
          WebkitOverflowScrolling: 'touch',
          paddingBottom: 88,   // plads til TabBar
        }}
      >
        {renderScreen()}
      </div>

      {/* TabBar */}
      <TabBar active={screen} onChange={navigate} notifCount={unread} />
    </div>
  );
}

export default BrobyggerApp;


// ─────────────────────────────────────────────────────────────────────────────
//  TabBar (migreret fra prototype)
// ─────────────────────────────────────────────────────────────────────────────

function TabBar({ active, onChange, notifCount = 0 }) {
  return (
    <div
      style={{
        position:       'absolute',
        bottom:         0,
        left:           0,
        right:          0,
        background:     'rgba(255,255,255,0.92)',
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        borderTop:      `1px solid ${SoS.line}`,
        paddingBottom:  28,
        paddingTop:     10,
        display:        'flex',
        justifyContent: 'space-around',
        zIndex:         50,
      }}
    >
      {TABS.map(({ id, label, icon: IconComp }) => {
        const on         = active === id;
        const showBadge  = id === 'notif' && notifCount > 0;
        const color      = on ? SoS.orange : SoS.inkMuted;

        return (
          <button
            key={id}
            onClick={() => onChange(id)}
            aria-label={label}
            aria-current={on ? 'page' : undefined}
            style={{
              background: 'none',
              border:     'none',
              cursor:     'pointer',
              display:    'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap:        3,
              padding:    '4px 8px',
              position:   'relative',
              color,
              outline:    'none',
            }}
          >
            <div style={{ position: 'relative' }}>
              <IconComp
                size={24}
                color={color}
                strokeWidth={on ? 2.1 : 1.7}
              />
              {showBadge && (
                <div
                  style={{
                    position:       'absolute',
                    top:            -3,
                    right:          -5,
                    minWidth:       16,
                    height:         16,
                    borderRadius:   8,
                    background:     SoS.rose,
                    color:          '#fff',
                    fontFamily:     SoS.sans,
                    fontSize:       10,
                    fontWeight:     700,
                    display:        'flex',
                    alignItems:     'center',
                    justifyContent: 'center',
                    padding:        '0 4px',
                    border:         '2px solid #fff',
                  }}
                >
                  {notifCount > 9 ? '9+' : notifCount}
                </div>
              )}
            </div>
            <span
              style={{
                fontFamily:  SoS.sans,
                fontSize:    10,
                fontWeight:  600,
                letterSpacing: 0.2,
              }}
            >
              {label}
            </span>
          </button>
        );
      })}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
//  PlaceholderScreen — bruges indtil FASE 2-migrering
// ─────────────────────────────────────────────────────────────────────────────

function PlaceholderScreen({ title, description, onBack, action }) {
  return (
    <div style={{ padding: '54px 20px 24px' }}>
      {/* TopBar */}
      <div style={{ marginBottom: 24 }}>
        {onBack && (
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border:     'none',
              cursor:     'pointer',
              padding:    '0 0 8px',
              display:    'flex',
              alignItems: 'center',
              gap:        4,
              color:      SoS.inkSoft,
              fontFamily: SoS.sans,
              fontSize:   13,
            }}
          >
            <ChevronLeftIcon size={16} color={SoS.inkSoft} />
            Tilbage
          </button>
        )}
        <div
          style={{
            fontFamily:  SoS.font,
            fontSize:    26,
            fontWeight:  500,
            color:       SoS.ink,
            letterSpacing: -0.3,
          }}
        >
          {title}
        </div>
      </div>

      {/* Placeholder-kort */}
      <div
        style={{
          background:   SoS.sand,
          borderRadius: SoS.r.md,
          padding:      20,
          border:       `1.5px dashed ${SoS.line}`,
        }}
      >
        <div
          style={{
            fontFamily: SoS.sans,
            fontSize:   13,
            color:      SoS.inkSoft,
            lineHeight: 1.7,
            whiteSpace: 'pre-line',
          }}
        >
          {description}
        </div>
      </div>

      {action && (
        <button
          onClick={action.onClick}
          style={{
            marginTop:    16,
            background:   SoS.rose,
            color:        '#fff',
            border:       'none',
            padding:      '10px 20px',
            borderRadius: SoS.r.md,
            fontFamily:   SoS.sans,
            fontSize:     14,
            fontWeight:   600,
            cursor:       'pointer',
          }}
        >
          {action.label}
        </button>
      )}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
//  Inline SVG-ikoner (Lucide-stil, ingen dependency nødvendig)
// ─────────────────────────────────────────────────────────────────────────────

function SvgIcon({ size = 24, color = 'currentColor', strokeWidth = 2, children }) {
  return (
    <svg
      width={size} height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {children}
    </svg>
  );
}

function HomeIcon(p)         { return <SvgIcon {...p}><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></SvgIcon>; }
function CalendarIcon(p)     { return <SvgIcon {...p}><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></SvgIcon>; }
function ClockIcon(p)        { return <SvgIcon {...p}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></SvgIcon>; }
function BellIcon(p)         { return <SvgIcon {...p}><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></SvgIcon>; }
function UserIcon(p)         { return <SvgIcon {...p}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></SvgIcon>; }
function ChevronLeftIcon(p)  { return <SvgIcon {...p}><polyline points="15 18 9 12 15 6"/></SvgIcon>; }

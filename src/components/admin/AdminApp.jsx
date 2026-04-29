/**
 * src/components/admin/AdminApp.jsx
 *
 * Shell for rådgiver/admin-app'en — parallel til BrobyggerApp.
 *
 * FASE 1: Placeholder-skærme. Data fra USE_BACKEND=false.
 * FASE 2: Erstat imports med rigtige komponenter.
 *
 * Props:
 *   user        — { id, firstName, avatar, avatarBg, hq, isAdmin }
 *   viewingHq   — string — det HQ der vises (kan afvige fra user.hq)
 *   onLogout    — function
 *   onSettings  — function — åbn HQ-vælger/indstillinger
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SoS }         from '../../styles/tokens';
import { Icon }        from '../shared/Icon';
import { hqColor }     from '../../styles/tokens';
import { TYPER }       from '../../constants/typer';
import { Notifikationer } from '../../api/index';

// ── Tabs ──────────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'oversigt',   label: 'Oversigt',   icon: 'chart'  },
  { id: 'brobyggere', label: 'Brobyggere', icon: 'users'  },
  { id: 'mennesker',  label: 'Mennesker',  icon: 'heart'  },
  { id: 'rapport',    label: 'Rapport',    icon: 'note'   },
  { id: 'profil',     label: 'Mig',        icon: 'user'   },
];


// ─────────────────────────────────────────────────────────────────────────────
//  Hoved-komponent
// ─────────────────────────────────────────────────────────────────────────────

export function AdminApp({ user, viewingHq, onLogout, onSettings }) {
  const [tab,    setTab]    = useState('oversigt');
  const [unread, setUnread] = useState(0);

  const isTemporary = viewingHq && user?.hq && viewingHq !== user.hq;
  const isAdmin     = user?.isAdmin ?? false;

  useEffect(() => {
    Notifikationer.list()
      .then(data => setUnread((data || []).filter(n => !n.laest).length))
      .catch(() => {});
  }, [tab]);

  const navigate = useCallback((t) => setTab(t), []);

  return (
    <div style={{
      position:      'relative',
      width:         '100%',
      height:        '100%',
      background:    SoS.cream,
      overflow:      'hidden',
      display:       'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{ background: '#fff', padding: '54px 20px 16px', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              letterSpacing: 1, color: SoS.inkSoft, textTransform: 'uppercase', marginBottom: 2 }}>
              {isAdmin ? 'Admin' : 'Rådgiver'} · SoS
            </div>
            <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500,
              color: SoS.ink, letterSpacing: -0.3 }}>
              Hej {user?.firstName ?? ''}
            </div>
          </div>
          <button
            onClick={onSettings}
            aria-label="Indstillinger"
            style={{ width: 40, height: 40, borderRadius: 20, background: SoS.creamDeep,
              border: 'none', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <Icon name={isAdmin ? 'menu' : 'pin'} size={20} color={SoS.ink} />
          </button>
        </div>

        {/* HQ-indikator */}
        {viewingHq && (
          <button
            onClick={onSettings}
            style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: 8,
              padding: '10px 14px',
              background: isTemporary ? SoS.sun + '22' : SoS.creamDeep,
              border:     isTemporary ? `1px solid ${SoS.sun}` : 'none',
              borderRadius: 12, cursor: 'pointer', textAlign: 'left',
            }}
          >
            <div style={{ width: 10, height: 10, borderRadius: 5, flexShrink: 0,
              background: hqColor(viewingHq) }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                {viewingHq}
              </div>
              {isTemporary && (
                <div style={{ fontFamily: SoS.sans, fontSize: 10, color: '#8A6D1E', marginTop: 1 }}>
                  ⚠ Midlertidig visning · dit eget: {user.hq}
                </div>
              )}
            </div>
            <Icon name="chevron" size={16} color={SoS.inkSoft} />
          </button>
        )}
      </div>

      {/* Indhold */}
      <div style={{ flex: 1, overflowY: 'auto', WebkitOverflowScrolling: 'touch', paddingBottom: 88 }}>
        <AdminPlaceholder
          tab={tab}
          user={user}
          viewingHq={viewingHq}
          isAdmin={isAdmin}
          onLogout={onLogout}
        />
      </div>

      {/* TabBar */}
      <AdminTabBar active={tab} onChange={navigate} />
    </div>
  );
}

export default AdminApp;


// ─────────────────────────────────────────────────────────────────────────────
//  AdminTabBar
// ─────────────────────────────────────────────────────────────────────────────

function AdminTabBar({ active, onChange }) {
  return (
    <div style={{
      position:            'absolute',
      bottom:              0,
      left:                0,
      right:               0,
      background:          'rgba(255,255,255,0.95)',
      backdropFilter:      'blur(20px) saturate(180%)',
      WebkitBackdropFilter:'blur(20px) saturate(180%)',
      borderTop:           `1px solid ${SoS.line}`,
      paddingBottom:       28,
      paddingTop:          10,
      display:             'flex',
      justifyContent:      'space-around',
      zIndex:              50,
    }}>
      {TABS.map(({ id, label, icon }) => {
        const on    = active === id;
        const color = on ? SoS.orange : SoS.inkMuted;
        return (
          <button
            key={id}
            onClick={() => onChange(id)}
            aria-label={label}
            aria-current={on ? 'page' : undefined}
            style={{
              background:    'none',
              border:        'none',
              cursor:        'pointer',
              display:       'flex',
              flexDirection: 'column',
              alignItems:    'center',
              gap:           3,
              padding:       '4px 6px',
              color,
              outline:       'none',
            }}
          >
            <Icon name={icon} size={22} color={color} weight={on ? 2.1 : 1.7} />
            <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 600 }}>
              {label}
            </span>
          </button>
        );
      })}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
//  Placeholder-indhold til alle tabs
// ─────────────────────────────────────────────────────────────────────────────

function AdminPlaceholder({ tab, user, viewingHq, isAdmin, onLogout }) {
  const BESKRIVELSER = {
    oversigt: [
      'KPI-kort: aktive brobyggere, ventende matches, aftaler denne uge',
      'Ringeliste: brobyggere der skal kontaktes',
      'FASE 2: Henter data fra /v1/statistik/dashboard',
    ],
    brobyggere: [
      'Liste over alle brobyggere med status, vagter og type-filter',
      'Søgning + filter på status (aktiv/ny/pause/inaktiv)',
      'FASE 2: /v1/brobyggere + brobygningstype-filter',
    ],
    mennesker: [
      'Liste over mennesker der afventer match',
      'Status-badges: afventer, matchet, aktiv, afsluttet',
      'FASE 2: /v1/mennesker + matching-CTA',
    ],
    rapport: [
      'SROI-rapport med periode-filter og eksport',
      'KPI: brobygninger, timer, effekt i DKK',
      'FASE 2: /v1/statistik/sroi + PDF-eksport',
    ],
    profil: [
      `Logget ind som: ${user?.firstName ?? ''} (${isAdmin ? 'Admin' : 'Rådgiver'})`,
      `Eget HQ: ${user?.hq ?? 'Ukendt'}`,
      'Indstillinger: notifikationer, adgangskode, privatlivspolitik',
    ],
  };

  const lines = BESKRIVELSER[tab] ?? [];

  return (
    <div style={{ padding: '20px 20px 24px' }}>
      <div style={{
        background:   SoS.sand,
        borderRadius: SoS.r.md,
        padding:      20,
        border:       `1.5px dashed ${SoS.line}`,
        marginBottom: 16,
      }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
          color: SoS.inkMuted, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 10 }}>
          FASE 2 — {tab}
        </div>
        {lines.map((l, i) => (
          <div key={i} style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
            lineHeight: 1.7, paddingLeft: 12, borderLeft: `2px solid ${SoS.line}`,
            marginBottom: i < lines.length - 1 ? 6 : 0 }}>
            {l}
          </div>
        ))}
      </div>

      {/* Type-oversigt (altid synlig — ingen backend) */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
          color: SoS.inkSoft, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 10 }}>
          Brobygningstyper
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {Object.values(TYPER).map(t => (
            <div key={t.id} style={{ flex: 1, background: t.soft, borderRadius: SoS.r.sm,
              padding: '10px 8px', textAlign: 'center' }}>
              <Icon name={t.icon} size={18} color={t.color} />
              <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 600,
                color: t.color, marginTop: 4 }}>{t.short}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Log ud (kun på profil-tab) */}
      {tab === 'profil' && onLogout && (
        <button
          onClick={onLogout}
          style={{
            marginTop:    8,
            background:   SoS.roseSoft,
            color:        SoS.rose,
            border:       'none',
            padding:      '10px 20px',
            borderRadius: SoS.r.md,
            fontFamily:   SoS.sans,
            fontSize:     14,
            fontWeight:   600,
            cursor:       'pointer',
            width:        '100%',
          }}
        >
          Log ud
        </button>
      )}
    </div>
  );
}

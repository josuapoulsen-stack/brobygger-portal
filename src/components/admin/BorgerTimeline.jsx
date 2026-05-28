/**
 * src/components/admin/BorgerTimeline.jsx
 *
 * Kronologisk tidslinje per borger — read-only.
 * Viser: registrering, brobygningsforløb (aftaler),
 *         fritekst-notater (BrobygningNotater), kontakter (KontaktLog).
 *
 * Props:
 *   menneske — menneskeObj (skal have .id og .createdAt)
 */

import React, { useEffect, useState } from 'react';
import { Icon } from '../shared';
import { SoS } from '../../styles/tokens';
import { Aftaler, BrobygningNotater, KontaktLog } from '../../api';

// ─── Hjælpere ────────────────────────────────────────────────────────────────
const MAANEDER = ['Jan','Feb','Mar','Apr','Maj','Jun','Jul','Aug','Sep','Okt','Nov','Dec'];

const fmtDato = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return `${d.getDate()}. ${MAANEDER[d.getMonth()]} ${d.getFullYear()}`;
};

const fmtMaanedAar = (maaned, aar) => {
  if (!aar) return '—';
  const m = parseInt(maaned, 10);
  return `${!isNaN(m) ? MAANEDER[m - 1] + ' ' : ''}${aar}`;
};

// ─── Item-typer ───────────────────────────────────────────────────────────────
const TL_TYPES = {
  registr: { icon: 'user',     color: SoS.inkSoft,  label: 'Registrering'  },
  aftale:  { icon: 'calendar', color: SoS.orange,   label: 'Forløb'        },
  notat:   { icon: 'note',     color: SoS.sage,     label: 'Notat'         },
  kontakt: { icon: 'phone',    color: '#5B8DB8',    label: 'Kontakt'       },
};

const STATUS_LABELS = {
  aktiv:     { label: 'Aktiv',     bg: '#E8F5E9', color: '#388E3C' },
  afsluttet: { label: 'Afsluttet', bg: '#FCE4EC', color: '#C62828' },
  pause:     { label: 'Pause',     bg: '#F5F5F5', color: '#9E9E9E' },
  planlagt:  { label: 'Planlagt',  bg: '#FFF3E0', color: '#E87A3E' },
};

// ═══════════════════════════════════════════════════════════════════════════════
export const BorgerTimeline = ({ menneske }) => {
  const [items,   setItems]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!menneske?.id) { setLoading(false); return; }
    setLoading(true);

    Promise.all([
      Aftaler.getAll({ menneskeId: menneske.id }).catch(() => []),
      BrobygningNotater.getByMenneske(menneske.id).catch(() => []),
      KontaktLog.getByMenneske(menneske.id).catch(() => []),
    ]).then(([aftaler, notater, kontakter]) => {
      const tl = [];

      // Registrering
      if (menneske.createdAt) {
        tl.push({
          id: 'reg-0',
          type: 'registr',
          dato: menneske.createdAt,
          titel: `${menneske.firstName || 'Borger'} registreret`,
          sub: menneske.kilde ? `Kilde: ${menneske.kilde}` : null,
        });
      }

      // Aftaler / forløb
      aftaler.forEach(a => {
        const sl = STATUS_LABELS[a.status] || {};
        tl.push({
          id: `aftale-${a.id}`,
          type: 'aftale',
          dato: a.createdAt || a.dato || '',
          titel: a.title || 'Brobygningsforløb',
          sub: a.brobyggerNavn ? `Brobygger: ${a.brobyggerNavn}` : null,
          pill: a.status ? { label: sl.label || a.status, bg: sl.bg, color: sl.color } : null,
        });
      });

      // Fritekst-notater
      notater.forEach(n => {
        const approxDato = n.aar
          ? new Date(parseInt(n.aar), (parseInt(n.maaned) || 1) - 1, 1).toISOString()
          : n.createdAt;
        tl.push({
          id: `notat-${n.id}`,
          type: 'notat',
          dato: approxDato,
          titel: n.fritekst?.length > 90
            ? n.fritekst.slice(0, 90) + '…'
            : n.fritekst || '(tom notat)',
          sub: [fmtMaanedAar(n.maaned, n.aar), n.initialer].filter(Boolean).join(' · '),
        });
      });

      // Kontakter
      kontakter.forEach(k => {
        tl.push({
          id: `kontakt-${k.id}`,
          type: 'kontakt',
          dato: k.createdAt || '',
          titel: k.type || 'Kontakt',
          sub: k.note || null,
          source: k.source,
        });
      });

      // Nyeste øverst
      tl.sort((a, b) => new Date(b.dato) - new Date(a.dato));
      setItems(tl);
      setLoading(false);
    });
  }, [menneske?.id]);

  // ── Loading ─────────────────────────────────────────────────────────────────
  if (loading) return (
    <div style={{ padding: '28px 0', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
      Indlæser tidslinje…
    </div>
  );

  // ── Tom ─────────────────────────────────────────────────────────────────────
  if (items.length === 0) return (
    <div style={{ padding: '28px 16px', textAlign: 'center' }}>
      <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, lineHeight: 1.6 }}>
        Ingen aktivitet registreret endnu.<br />
        Tilføj notater eller registrér kontakter for at se tidslinjen.
      </div>
    </div>
  );

  // ── Tidslinje ───────────────────────────────────────────────────────────────
  return (
    <div style={{ position: 'relative', paddingLeft: 4 }}>
      {items.map((item, idx) => {
        const t = TL_TYPES[item.type] || TL_TYPES.kontakt;
        const isLast = idx === items.length - 1;

        return (
          <div key={item.id} style={{ display: 'flex', gap: 14, position: 'relative' }}>
            {/* Vertikal linje */}
            {!isLast && (
              <div style={{
                position: 'absolute', left: 15, top: 34, bottom: 0, width: 2,
                background: SoS.lineSoft, zIndex: 0,
              }} />
            )}

            {/* Ikon-cirkel */}
            <div style={{
              width: 32, height: 32, borderRadius: 16, flexShrink: 0, zIndex: 1, marginTop: 2,
              background: t.color + '18',
              border: `2px solid ${t.color}50`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Icon name={t.icon} size={14} color={t.color} />
            </div>

            {/* Tekst */}
            <div style={{ flex: 1, paddingBottom: 22 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, flexWrap: 'wrap' }}>
                <div style={{
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: 500,
                  color: SoS.ink, lineHeight: 1.45, flex: 1,
                }}>
                  {item.titel}
                </div>
                {item.pill && (
                  <span style={{
                    fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                    background: item.pill.bg || SoS.creamDeep,
                    color: item.pill.color || SoS.inkSoft,
                    borderRadius: 999, padding: '2px 8px', flexShrink: 0,
                  }}>
                    {item.pill.label}
                  </span>
                )}
              </div>
              {item.sub && (
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                  {item.sub}
                </div>
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
                  {fmtDato(item.dato)}
                </span>
                {item.source === 'telecom_api' && (
                  <span style={{
                    fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                    background: '#E3F2FD', color: '#1565C0',
                    borderRadius: 4, padding: '1px 6px',
                  }}>
                    API
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default BorgerTimeline;

/**
 * src/components/admin/BorgerTimeline.jsx
 *
 * Kronologisk tidslinje per borger.
 * Vertikal midterlinje — hændelser veksler venstre/højre.
 * Klik på hændelse → inline detaljevisning.
 *
 * Props:
 *   menneske — menneskeObj (skal have .id og .createdAt)
 */

import React, { useEffect, useState } from 'react';
import { SoS } from '../../styles/tokens';
import { Aftaler, BrobygningNotater, KontaktLog } from '../../api';

// ─── Formattering ─────────────────────────────────────────────────────────────
const MND = ['januar','februar','marts','april','maj','juni','juli','august','september','oktober','november','december'];
const MND_S = ['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec'];

const fmtDato = (iso) => {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d)) return String(iso);
  return `${d.getDate()}. ${MND[d.getMonth()]} ${d.getFullYear()}`;
};

// ─── Type-definitioner ────────────────────────────────────────────────────────
const TYPER = {
  registr: { color: '#78909C', label: 'Registrering' },
  aftale:  { color: SoS.orange, label: 'Forløb'       },
  notat:   { color: '#5A9E78', label: 'Notat'         },
  opkald:  { color: '#388E3C', label: 'Opkald'        },
  sms:     { color: '#7B5EA7', label: 'SMS'           },
  kontakt: { color: '#5B8DB8', label: 'Kontakt'       },
};

const STATUS_STYLE = {
  aktiv:     { label: 'Aktiv',     bg: '#E8F5E9', color: '#388E3C' },
  afsluttet: { label: 'Afsluttet', bg: '#FCE4EC', color: '#C62828' },
  pause:     { label: 'Pause',     bg: '#F3F3F3', color: '#757575' },
  planlagt:  { label: 'Planlagt',  bg: '#FFF3E0', color: '#E87A3E' },
};

// ─── Byg items fra rå data ────────────────────────────────────────────────────
const buildItems = (menneske, aftaler, notater, kontakter) => {
  const items = [];

  if (menneske.createdAt) {
    items.push({
      id: 'reg-0', type: 'registr',
      dato: menneske.createdAt,
      titel: 'Registreret i systemet',
      detalje: { kilde: menneske.kilde, hq: menneske.hq },
    });
  }

  aftaler.forEach(a => items.push({
    id: `aftale-${a.id}`, type: 'aftale',
    dato: a.createdAt || a.dato || '',
    titel: a.title || 'Brobygningsaftale booket',
    pill: a.status,
    detalje: {
      brobygger: a.brobyggerNavn || null,
      status: a.status,
      dato: a.dato,
      note: a.notes || null,
    },
  }));

  notater.forEach(n => {
    const approxDato = n.aar
      ? new Date(parseInt(n.aar, 10), (parseInt(n.maaned, 10) || 1) - 1, 15).toISOString()
      : n.createdAt;
    items.push({
      id: `notat-${n.id}`, type: 'notat',
      dato: approxDato,
      titel: 'Notat fra brobygger',
      detalje: {
        fritekst: n.fritekst,
        initialer: n.initialer,
        periode: n.aar
          ? `${MND[(parseInt(n.maaned, 10) || 1) - 1]} ${n.aar}`
          : null,
      },
    });
  });

  kontakter.forEach(k => {
    const type = k.subtype === 'sms'    ? 'sms'
               : k.subtype === 'opkald' ? 'opkald'
               : k.type?.toLowerCase().includes('sms') ? 'sms'
               : k.type?.toLowerCase().includes('opkald') ? 'opkald'
               : 'kontakt';
    items.push({
      id: `kontakt-${k.id}`, type,
      dato: k.createdAt || '',
      titel: k.type || 'Kontakt',
      source: k.source,
      detalje: {
        type: k.type,
        direction: k.direction,
        duration: k.duration,
        note: k.note,
        source: k.source,
      },
    });
  });

  items.sort((a, b) => new Date(b.dato) - new Date(a.dato));
  return items;
};

// ─── Detalje-panel ────────────────────────────────────────────────────────────
const DetailRow = ({ label, value }) => (
  <div style={{
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
    padding: '6px 0', borderBottom: `1px solid ${SoS.lineSoft}`,
  }}>
    <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, flexShrink: 0, marginRight: 12 }}>
      {label}
    </span>
    <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.ink, textAlign: 'right', maxWidth: '65%' }}>
      {value}
    </span>
  </div>
);

const ItemDetail = ({ item }) => {
  const d = item.detalje || {};
  const ss = STATUS_STYLE[d.status] || {};

  return (
    <div style={{
      background: '#fff', borderRadius: 10,
      border: `1px solid ${SoS.lineSoft}`,
      padding: '10px 14px', marginTop: 8,
    }}>
      {item.type === 'aftale' && (
        <>
          {d.brobygger && <DetailRow label="Brobygger" value={d.brobygger} />}
          {d.status && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: `1px solid ${SoS.lineSoft}` }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>Status</span>
              <span style={{
                fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                background: ss.bg || SoS.creamDeep, color: ss.color || SoS.ink,
                borderRadius: 99, padding: '2px 9px',
              }}>
                {ss.label || d.status}
              </span>
            </div>
          )}
          {d.dato && <DetailRow label="Aftalt dato" value={fmtDato(d.dato)} />}
          {d.note && (
            <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.6, paddingTop: 8 }}>
              {d.note}
            </div>
          )}
        </>
      )}

      {item.type === 'notat' && (
        <>
          {d.fritekst && (
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.ink,
              lineHeight: 1.65, whiteSpace: 'pre-wrap',
              paddingBottom: (d.initialer || d.periode) ? 8 : 0,
              borderBottom: (d.initialer || d.periode) ? `1px solid ${SoS.lineSoft}` : 'none',
              marginBottom: (d.initialer || d.periode) ? 8 : 0,
            }}>
              {d.fritekst}
            </div>
          )}
          {(d.initialer || d.periode) && (
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
              {[d.initialer, d.periode].filter(Boolean).join(' · ')}
            </div>
          )}
        </>
      )}

      {(item.type === 'kontakt' || item.type === 'opkald' || item.type === 'sms') && (
        <>
          {d.type      && <DetailRow label="Type"    value={d.type} />}
          {d.direction && <DetailRow label="Retning" value={d.direction === 'ind' ? 'Indgående' : 'Udgående'} />}
          {d.duration  && <DetailRow label="Varighed" value={`${d.duration} min`} />}
          {d.note && (
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.ink,
              lineHeight: 1.6, paddingTop: 8,
            }}>
              {d.note}
            </div>
          )}
          {d.source === 'telecom_api' && (
            <div style={{ paddingTop: 8 }}>
              <span style={{
                fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                background: '#E3F2FD', color: '#1565C0',
                borderRadius: 4, padding: '2px 8px',
              }}>
                Automatisk fra telefonisystem
              </span>
            </div>
          )}
        </>
      )}

      {item.type === 'registr' && (
        <>
          {d.kilde && <DetailRow label="Kilde" value={d.kilde} />}
          {d.hq    && <DetailRow label="HQ"    value={d.hq}    />}
        </>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const BorgerTimeline = ({ menneske }) => {
  const [items,      setItems]      = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    if (!menneske?.id) { setLoading(false); return; }
    setLoading(true);
    Promise.all([
      Aftaler.getAll({ menneskeId: menneske.id }).catch(() => []),
      BrobygningNotater.getByMenneske(menneske.id).catch(() => []),
      KontaktLog.getByMenneske(menneske.id).catch(() => []),
    ]).then(([aftaler, notater, kontakter]) => {
      setItems(buildItems(menneske, aftaler, notater, kontakter));
      setLoading(false);
    });
  }, [menneske?.id]);

  const toggle = (id) => setExpandedId(prev => prev === id ? null : id);

  if (loading) return (
    <div style={{ padding: '28px 0', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
      Indlæser tidslinje…
    </div>
  );

  if (items.length === 0) return (
    <div style={{ padding: '28px 16px', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, lineHeight: 1.6 }}>
      Ingen aktivitet registreret endnu.
    </div>
  );

  return (
    <div style={{ position: 'relative', padding: '4px 0 16px' }}>

      {/* ── Kontinuerlig vertikal linje ─────────────────────────────────── */}
      <div style={{
        position:  'absolute',
        left:      '50%',
        top:       0,
        bottom:    0,
        width:     2,
        background:'#1a1a1a',
        transform: 'translateX(-50%)',
        zIndex:    0,
      }} />

      {/* ── Hændelser ───────────────────────────────────────────────────── */}
      {items.map((item, idx) => {
        const isLeft    = idx % 2 === 0;   // titel/beskrivelse på venstre side
        const t         = TYPER[item.type] || TYPER.kontakt;
        const isExpanded = expandedId === item.id;
        const dato      = fmtDato(item.dato);
        const ss        = STATUS_STYLE[item.pill] || {};
        const hasDetail = !!(item.detalje && Object.values(item.detalje).some(Boolean));

        return (
          <React.Fragment key={item.id}>
            {/* ── Hændelse-række ─────────────────────────────────────────── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: isExpanded ? 0 : 24, position: 'relative', zIndex: 1 }}>

              {/* Venstre side */}
              <div style={{ width: '44%', paddingRight: 18, textAlign: 'right' }}>
                {isLeft ? (
                  // Titel venstre
                  <button
                    onClick={() => hasDetail && toggle(item.id)}
                    style={{
                      background: 'none', border: 'none', cursor: hasDetail ? 'pointer' : 'default',
                      textAlign: 'right', padding: 0, width: '100%',
                    }}
                  >
                    <div style={{
                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                      color: SoS.ink, lineHeight: 1.4,
                    }}>
                      {item.titel}
                    </div>
                    {item.source === 'telecom_api' && (
                      <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, background: '#E3F2FD', color: '#1565C0', borderRadius: 3, padding: '1px 5px', marginTop: 3, display: 'inline-block' }}>
                        API
                      </span>
                    )}
                    {item.pill && (
                      <div style={{ marginTop: 3 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, background: ss.bg || SoS.creamDeep, color: ss.color || SoS.inkSoft, borderRadius: 99, padding: '1px 8px' }}>
                          {ss.label || item.pill}
                        </span>
                      </div>
                    )}
                    {hasDetail && (
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: t.color, marginTop: 3 }}>
                        {isExpanded ? 'Skjul ↑' : 'Se detaljer ↓'}
                      </div>
                    )}
                  </button>
                ) : (
                  // Dato venstre
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, paddingTop: 2 }}>
                    {dato}
                  </div>
                )}
              </div>

              {/* Center — markør på linjen */}
              <div style={{
                width: '12%', display: 'flex', justifyContent: 'center',
                position: 'relative', zIndex: 2, flexShrink: 0,
              }}>
                <div style={{
                  width: 10, height: 10, flexShrink: 0,
                  background: isExpanded ? t.color : '#fff',
                  border: `2.5px solid ${t.color}`,
                  transform: 'rotate(45deg)',
                  marginTop: 3,
                  boxShadow: isExpanded ? `0 0 0 3px ${t.color}25` : 'none',
                  transition: 'all 0.15s',
                }} />
              </div>

              {/* Højre side */}
              <div style={{ width: '44%', paddingLeft: 18 }}>
                {isLeft ? (
                  // Dato højre
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, paddingTop: 2 }}>
                    {dato}
                  </div>
                ) : (
                  // Titel højre
                  <button
                    onClick={() => hasDetail && toggle(item.id)}
                    style={{
                      background: 'none', border: 'none', cursor: hasDetail ? 'pointer' : 'default',
                      textAlign: 'left', padding: 0, width: '100%',
                    }}
                  >
                    <div style={{
                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                      color: SoS.ink, lineHeight: 1.4,
                    }}>
                      {item.titel}
                    </div>
                    {item.source === 'telecom_api' && (
                      <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, background: '#E3F2FD', color: '#1565C0', borderRadius: 3, padding: '1px 5px', marginTop: 3, display: 'inline-block' }}>
                        API
                      </span>
                    )}
                    {item.pill && (
                      <div style={{ marginTop: 3 }}>
                        <span style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, background: ss.bg || SoS.creamDeep, color: ss.color || SoS.inkSoft, borderRadius: 99, padding: '1px 8px' }}>
                          {ss.label || item.pill}
                        </span>
                      </div>
                    )}
                    {hasDetail && (
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: t.color, marginTop: 3 }}>
                        {isExpanded ? 'Skjul ↑' : 'Se detaljer ↓'}
                      </div>
                    )}
                  </button>
                )}
              </div>
            </div>

            {/* ── Ekspanderet detalje (fuld bredde) ──────────────────────── */}
            {isExpanded && (
              <div style={{ marginBottom: 24, position: 'relative', zIndex: 1 }}>
                <ItemDetail item={item} />
              </div>
            )}
          </React.Fragment>
        );
      })}

      {/* ── Bund-markør ─────────────────────────────────────────────────── */}
      <div style={{
        position: 'relative', display: 'flex', justifyContent: 'center', zIndex: 1,
      }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: '#1a1a1a', flexShrink: 0,
        }} />
      </div>

    </div>
  );
};

export default BorgerTimeline;

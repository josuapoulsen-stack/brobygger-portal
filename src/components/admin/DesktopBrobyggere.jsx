/**
 * src/components/admin/DesktopBrobyggere.jsx
 *
 * Brobygger-oversigt med søgning, statusfilter og profilpanel.
 * FASE 1: data som props fra AdminApp (mock via USE_BACKEND=false)
 * FASE 2: Brobyggere.getAll({ hq }) → rigtig API
 *
 * Props:
 *   brobyggere  — [ brobyggerObj ]
 *   onMatch(bb) — åbner MatchingFlow med brobygger prævalgt (valgfrit)
 */

import React, { useState } from 'react';
import { Avatar, Icon, Pill } from '../shared';
import { SoS } from '../../styles/tokens';

// ─── Status-farver ────────────────────────────────────────────────────────────
const STATUS_STYLE = {
  aktiv:     { variant: 'aktiv',     label: 'Aktiv' },
  pause:     { variant: 'pause',     label: 'Pause' },
  ny:        { variant: 'ny',        label: 'Ny' },
  afventer:  { variant: 'afventer',  label: 'Afventer' },
  afsluttet: { variant: 'inaktiv',   label: 'Afsluttet' },
};

// ─── Relativ tid ──────────────────────────────────────────────────────────────
const fmtRelativ = (dateStr) => {
  if (!dateStr) return '—';
  const days = Math.round((Date.now() - new Date(dateStr)) / 86_400_000);
  if (days === 0) return 'i dag';
  if (days === 1) return 'i går';
  if (days <= 7)  return `${days}d siden`;
  if (days <= 30) return `${Math.round(days / 7)}u siden`;
  return `${Math.round(days / 30)}mdr siden`;
};

// ─── Brobygger-profilpanel (bottom-sheet overlay) ────────────────────────────
const BrobyggerProfilePanel = ({ bb, onClose }) => {
  const ss = STATUS_STYLE[bb.status] || STATUS_STYLE.aktiv;
  const rows = [
    { label: 'Status',          value: null, pill: true },
    { label: 'Aktive forløb',   value: bb.active ?? '—' },
    { label: 'Denne måned',     value: bb.thisMonth ? `${bb.thisMonth} aftaler` : '—' },
    { label: 'Ledige vagter',   value: bb.openShifts ? `${bb.openShifts} stk.` : '0' },
    { label: 'Sidst aktiv',     value: fmtRelativ(bb.lastActive) },
    { label: 'Brobygningstyper', value: (bb.types || []).join(', ') || '—' },
    { label: 'Sprog',           value: (bb.languages || bb.language || 'Dansk') },
    { label: 'Hovedsæde',       value: bb.hq || '—' },
    ...(bb.pauseUntil ? [{ label: 'Pause til', value: new Date(bb.pauseUntil).toLocaleDateString('da-DK', { day: 'numeric', month: 'long' }) }] : []),
    ...(bb.pauseNote ? [{ label: 'Pauseårsag', value: bb.pauseNote }] : []),
  ];

  return (
    <div style={{ padding: '24px 20px 40px' }}>
      {/* Handle */}
      <div style={{ width: 40, height: 4, borderRadius: 2, background: SoS.lineSoft, margin: '0 auto 20px' }} />

      {/* Hoved-sektion */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
        <Avatar initials={bb.avatar || bb.initials} bg={bb.bg} size={56} />
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink, letterSpacing: -0.2 }}>
            {bb.name || bb.navn}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginTop: 2 }}>
            {bb.email || bb.hq || ''}
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ width: 36, height: 36, borderRadius: 18, background: SoS.creamDeep, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <Icon name="x" size={16} color={SoS.ink} />
        </button>
      </div>

      {/* Detalje-rækker */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
        {rows.map((row, i) => (
          <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '11px 16px', borderBottom: i < rows.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, fontWeight: 600 }}>{row.label}</span>
            {row.pill
              ? <Pill variant={ss.variant}>{ss.label}</Pill>
              : <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, textAlign: 'right', maxWidth: 200 }}>{row.value}</span>
            }
          </div>
        ))}
      </div>

      {/* Handlinger */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          onClick={onClose}
          style={{ flex: 1, padding: '13px 0', background: '#fff', color: SoS.ink, border: `1.5px solid ${SoS.lineSoft}`, borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, cursor: 'pointer' }}
        >
          Luk
        </button>
        <button
          style={{ flex: 2, padding: '13px 0', background: SoS.orange, color: '#fff', border: 'none', borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
        >
          Send besked
        </button>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const DesktopBrobyggere = ({ brobyggere = [] }) => {
  const [filter, setFilter] = useState('alle');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);

  const FILTERS = [
    { id: 'alle',     label: 'Alle' },
    { id: 'aktiv',    label: 'Aktive' },
    { id: 'pause',    label: 'På pause' },
    { id: 'ny',       label: 'Nye' },
    { id: 'afventer', label: 'Afventer' },
  ];

  const rows = brobyggere
    .filter(b => filter === 'alle' || b.status === filter)
    .filter(b => !search || (b.name || b.navn || '').toLowerCase().includes(search.toLowerCase()));

  return (
    <>
      {/* Toolbar */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, padding: 16, marginBottom: 14, border: `1px solid ${SoS.lineSoft}` }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {/* Søgefelt */}
          <div style={{ flex: 1, minWidth: 180, display: 'flex', alignItems: 'center', gap: 8, background: SoS.cream, borderRadius: 8, padding: '8px 14px' }}>
            <Icon name="search" size={14} color={SoS.inkMuted} />
            <input
              placeholder={`Søg i ${brobyggere.length} brobyggere…`}
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', fontFamily: SoS.sans, fontSize: 13 }}
            />
            {search && (
              <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: SoS.inkMuted, fontSize: 16, lineHeight: 1, padding: 0 }}>×</button>
            )}
          </div>

          {/* Statusfiltre */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {FILTERS.map(f => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                style={{
                  padding: '8px 14px', borderRadius: 8, cursor: 'pointer',
                  background: filter === f.id ? SoS.ink : '#fff',
                  color: filter === f.id ? '#fff' : SoS.ink,
                  border: filter === f.id ? 'none' : `1px solid ${SoS.line}`,
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                }}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tabel */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${SoS.line}` }}>
              {['Navn', 'Status', 'Aktive', 'Denne uge', 'Sidst aktiv', 'Planlagt pause'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 12px', fontFamily: SoS.sans, fontSize: 10, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '28px 12px', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                  Ingen brobyggere matcher filteret
                </td>
              </tr>
            ) : rows.map(b => {
              const ss = STATUS_STYLE[b.status] || STATUS_STYLE.aktiv;
              const today = new Date().toISOString().split('T')[0];
              const hasPause = b.pauseUntil && b.pauseUntil >= today;
              return (
                <tr
                  key={b.id}
                  onClick={() => setSelected(b)}
                  style={{ borderBottom: `1px solid ${SoS.lineSoft}`, cursor: 'pointer', transition: 'background 0.1s' }}
                  onMouseEnter={e => e.currentTarget.style.background = SoS.cream}
                  onMouseLeave={e => e.currentTarget.style.background = ''}
                >
                  <td style={{ padding: '12px 12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Avatar initials={b.avatar || b.initials} bg={b.bg} size={28} />
                      <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>
                        {b.name || b.navn}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 12px' }}>
                    <Pill variant={ss.variant}>{ss.label}</Pill>
                  </td>
                  <td style={{ padding: '12px 12px', fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                    {b.active ?? '—'}
                  </td>
                  <td style={{ padding: '12px 12px', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {(b.thisWeek ?? 0) > 0 ? `${b.thisWeek} afd.` : '—'}
                  </td>
                  <td style={{ padding: '12px 12px', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
                    {fmtRelativ(b.lastActive)}
                  </td>
                  <td style={{ padding: '12px 12px' }}>
                    {hasPause ? (
                      <Pill variant="pause">
                        {b.pauseNote || 'Pause'} – til {new Date(b.pauseUntil).toLocaleDateString('da-DK', { day: 'numeric', month: 'short' })}
                      </Pill>
                    ) : (
                      <span style={{ color: SoS.lineSoft, fontFamily: SoS.sans, fontSize: 12 }}>—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ padding: '10px 12px', fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, textAlign: 'right', borderTop: `1px solid ${SoS.lineSoft}`, background: SoS.creamDeep }}>
          {rows.length} af {brobyggere.length} brobyggere
        </div>
      </div>

      {/* Profilpanel overlay */}
      {selected && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}
          onClick={e => { if (e.target === e.currentTarget) setSelected(null); }}
        >
          <div style={{ width: '100%', maxWidth: 520, maxHeight: '80vh', overflowY: 'auto', background: SoS.cream, borderRadius: '20px 20px 0 0' }}>
            <BrobyggerProfilePanel bb={selected} onClose={() => setSelected(null)} />
          </div>
        </div>
      )}
    </>
  );
};

export default DesktopBrobyggere;

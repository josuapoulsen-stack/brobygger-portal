/**
 * src/components/admin/DesktopMennesker.jsx
 *
 * Menneskeoversigt: søgning, type- og statusfilter, detalje-panel.
 * "Opret menneske"-knap åbner IntakeFlow.
 *
 * FASE 1: data som props fra AdminApp (mock via USE_BACKEND=false)
 * FASE 2: Mennesker.getAll({ hq }) → rigtig API
 *
 * Props:
 *   mennesker   — { [id]: menneskeObj }
 *   onIntake()  — åbner IntakeFlow (håndteres i AdminApp)
 */

import React, { useState } from 'react';
import { Avatar, Icon, Pill } from '../shared';
import { SoS } from '../../styles/tokens';
import { TYPER, TYPER_LIST } from '../../constants/typer';

// ─── Status-farver ────────────────────────────────────────────────────────────
const STATUS_FARVER = {
  aktiv:     { bg: '#E8F5E9', color: '#388E3C' },
  venter:    { bg: '#FFF3E0', color: '#E87A3E' },
  pause:     { bg: '#F5F5F5', color: '#9E9E9E' },
  afsluttet: { bg: '#FCE4EC', color: '#C62828' },
};

// ─── Indsatsniveau (afledt af antal kontakter) ────────────────────────────────
const indsatsNiveau = (kontakter) => {
  if (kontakter >= 20) return { label: 'Intensiv',  color: '#C62828' };
  if (kontakter >= 10) return { label: 'Moderat',   color: SoS.orange };
  if (kontakter >= 1)  return { label: 'Opstartet', color: SoS.sage };
  return                      { label: 'Ventende',  color: SoS.inkMuted };
};

// ─── Menneske-detalje-panel (side-overlay) ───────────────────────────────────
const MenneskeDetailPanel = ({ m, onClose, onMatch }) => {
  const t = TYPER[m.type] || TYPER.social;
  const kontakter = (m.activeCount || 0) + (m.completedCount || 0);
  const niveau = indsatsNiveau(kontakter);
  const sf = STATUS_FARVER[m.status] || {};

  const rows = [
    { label: 'Alder',          value: m.age ? `${m.age} år` : '—' },
    { label: 'Sprog',          value: m.language || 'Dansk' },
    { label: 'Brobygningstype',value: t.label },
    { label: 'Kilde',          value: m.kilde || '—' },
    { label: 'Kontakter',      value: kontakter },
    { label: 'Indsatsniveau',  value: niveau.label, color: niveau.color },
    { label: 'Registreret',    value: m.createdAt ? new Date(m.createdAt).toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' }) : '—' },
    { label: 'HQ',             value: m.hq || '—' },
  ];

  return (
    <div style={{ padding: '24px 20px 40px' }}>
      {/* Handle */}
      <div style={{ width: 40, height: 4, borderRadius: 2, background: SoS.lineSoft, margin: '0 auto 20px' }} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
        <Avatar initials={m.initials || (m.firstName[0] + (m.lastName?.[0] || ''))} bg={t.color} size={56} />
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500, color: SoS.ink, letterSpacing: -0.2 }}>
            {m.firstName} {m.lastName}
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
            <Pill variant="custom" bg={t.soft} color={t.color}>{t.short}</Pill>
            {m.status && <Pill variant="custom" bg={sf.bg || SoS.creamDeep} color={sf.color || SoS.inkSoft}>{m.status}</Pill>}
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ width: 36, height: 36, borderRadius: 18, background: SoS.creamDeep, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <Icon name="x" size={16} color={SoS.ink} />
        </button>
      </div>

      {/* Behov */}
      {m.needs && m.needs.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 8 }}>
            Behov
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {m.needs.map(b => (
              <span key={b} style={{ padding: '4px 12px', background: t.soft, color: t.color, borderRadius: 999, fontFamily: SoS.sans, fontSize: 12, fontWeight: 500 }}>
                {b}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Detalje-rækker */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
        {rows.map((row, i) => (
          <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '11px 16px', borderBottom: i < rows.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none' }}>
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, fontWeight: 600 }}>{row.label}</span>
            <span style={{ fontFamily: SoS.sans, fontSize: 13, color: row.color || SoS.ink, fontWeight: row.color ? 600 : 400, textAlign: 'right', maxWidth: 200 }}>
              {row.value}
            </span>
          </div>
        ))}
      </div>

      {/* Brobygningsønske */}
      {m.brobygning && m.brobygning.dato && (
        <div style={{ background: SoS.orange + '0F', border: `1px solid ${SoS.orange}30`, borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 16 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.orange, letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 6 }}>
            Brobygningsønske
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.orangeDeep }}>
            {new Date(m.brobygning.dato).toLocaleDateString('da-DK', { weekday: 'long', day: 'numeric', month: 'long' })}
            {m.brobygning.start && ` kl. ${m.brobygning.start}`}
            {m.brobygning.frekvens && ` · ${m.brobygning.frekvens}`}
          </div>
        </div>
      )}

      {/* Handlinger */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          onClick={onClose}
          style={{ flex: 1, padding: '13px 0', background: '#fff', color: SoS.ink, border: `1.5px solid ${SoS.lineSoft}`, borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, cursor: 'pointer' }}
        >
          Luk
        </button>
        <button
          onClick={() => { onClose(); if (onMatch) onMatch(m); }}
          style={{ flex: 2, padding: '13px 0', background: SoS.orange, color: '#fff', border: 'none', borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
        >
          Start matching
        </button>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const DesktopMennesker = ({ mennesker = {}, onIntake, onMatch }) => {
  const [search,       setSearch]       = useState('');
  const [typeFilter,   setTypeFilter]   = useState('alle');
  const [statusFilter, setStatusFilter] = useState('alle');
  const [selected,     setSelected]     = useState(null);

  const alle = Object.values(mennesker);

  const filtered = alle.filter(m => {
    const navn = `${m.firstName || ''} ${m.lastName || ''}`.toLowerCase();
    if (search && !navn.includes(search.toLowerCase())) return false;
    if (typeFilter !== 'alle' && m.type !== typeFilter) return false;
    if (statusFilter !== 'alle' && m.status !== statusFilter) return false;
    return true;
  });

  return (
    <>
      {/* Toolbar */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 14, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 200, display: 'flex', alignItems: 'center', gap: 8, background: '#fff', borderRadius: 999, padding: '9px 16px', border: `1px solid ${SoS.lineSoft}` }}>
          <Icon name="search" size={16} color={SoS.inkMuted} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Søg på navn…"
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontFamily: SoS.sans, fontSize: 14, color: SoS.ink }}
          />
          {search && <button onClick={() => setSearch('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: SoS.inkMuted, fontSize: 18, padding: 0 }}>×</button>}
        </div>
        <button
          onClick={onIntake}
          style={{ padding: '9px 18px', background: SoS.orange, color: '#fff', border: 'none', borderRadius: 999, fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' }}
        >
          + Opret menneske
        </button>
      </div>

      {/* Filtre */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 14 }}>
        {/* Type */}
        {[{ id: 'alle', label: 'Alle typer', color: SoS.ink, soft: '' }, ...TYPER_LIST.map(t => ({ id: t.id, label: t.label, color: t.color, soft: t.soft }))].map(f => {
          const sel = typeFilter === f.id;
          return (
            <button key={f.id} onClick={() => setTypeFilter(f.id)} style={{ padding: '5px 14px', borderRadius: 999, background: sel ? f.color : '#fff', color: sel ? '#fff' : SoS.inkSoft, border: `1.5px solid ${sel ? f.color : SoS.lineSoft}`, fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400, cursor: 'pointer' }}>
              {f.label}
            </button>
          );
        })}
        <div style={{ width: 1, background: SoS.lineSoft, margin: '0 4px', alignSelf: 'stretch' }} />
        {/* Status */}
        {['alle', 'aktiv', 'venter', 'pause'].map(s => {
          const sel = statusFilter === s;
          const fc = STATUS_FARVER[s] || {};
          return (
            <button key={s} onClick={() => setStatusFilter(s)} style={{ padding: '5px 14px', borderRadius: 999, background: sel ? (fc.color || SoS.ink) : '#fff', color: sel ? '#fff' : SoS.inkSoft, border: `1.5px solid ${sel ? (fc.color || SoS.ink) : SoS.lineSoft}`, fontFamily: SoS.sans, fontSize: 12, fontWeight: sel ? 700 : 400, cursor: 'pointer' }}>
              {s === 'alle' ? 'Alle statusser' : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          );
        })}
      </div>

      {/* Tabel */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: SoS.creamDeep, borderBottom: `2px solid ${SoS.line}` }}>
              {['Menneske', 'Type', 'Status', 'Indsatsniveau', 'Kontakter', 'Registreret'].map(h => (
                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkMuted, letterSpacing: 0.6, textTransform: 'uppercase' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: 32, textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                  {alle.length === 0 ? 'Ingen mennesker registreret endnu' : 'Ingen matcher søgningen'}
                </td>
              </tr>
            )}
            {filtered.map((m, i) => {
              const t = TYPER[m.type] || TYPER.social;
              const sf = STATUS_FARVER[m.status] || {};
              const kontakter = (m.activeCount || 0) + (m.completedCount || 0);
              const niveau = indsatsNiveau(kontakter);
              const dato = m.createdAt || m.registeredAt || '';
              return (
                <tr
                  key={m.id}
                  onClick={() => setSelected(m)}
                  style={{ borderBottom: `1px solid ${SoS.lineSoft}`, cursor: 'pointer', background: i % 2 === 0 ? '#fff' : SoS.cream + '60', transition: 'background 0.1s' }}
                  onMouseEnter={e => e.currentTarget.style.background = SoS.creamDeep}
                  onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? '#fff' : SoS.cream + '60'}
                >
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <Avatar initials={m.initials || (m.firstName?.[0] || '?') + (m.lastName?.[0] || '')} bg={t.color} size={34} />
                      <div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                          {m.firstName} {m.lastName}
                        </div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                          {m.age} år · {(m.language || 'Dansk').split(',')[0]}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <Pill variant="custom" bg={t.soft} color={t.color}>{t.short}</Pill>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <Pill variant="custom" bg={sf.bg || SoS.creamDeep} color={sf.color || SoS.inkSoft}>
                      {m.status || 'venter'}
                    </Pill>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 4, background: niveau.color, flexShrink: 0 }} />
                      <span style={{ fontFamily: SoS.sans, fontSize: 12, color: niveau.color, fontWeight: 600 }}>
                        {niveau.label}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, textAlign: 'center' }}>
                    {kontakter}
                  </td>
                  <td style={{ padding: '12px 14px', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {dato ? new Date(dato).toLocaleDateString('da-DK', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ padding: '10px 14px', background: SoS.creamDeep, fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, borderTop: `1px solid ${SoS.lineSoft}` }}>
          Viser {filtered.length} af {alle.length} mennesker
        </div>
      </div>

      {/* Detalje-panel overlay */}
      {selected && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}
          onClick={e => { if (e.target === e.currentTarget) setSelected(null); }}
        >
          <div style={{ width: '100%', maxWidth: 560, maxHeight: '85vh', overflowY: 'auto', background: SoS.cream, borderRadius: '20px 20px 0 0' }}>
            <MenneskeDetailPanel
              m={selected}
              onClose={() => setSelected(null)}
              onMatch={m => { setSelected(null); if (onMatch) onMatch(m); }}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default DesktopMennesker;

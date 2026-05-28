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

import React, { useState, useEffect } from 'react';
import { Avatar, Icon, Pill } from '../shared';
import { SoS } from '../../styles/tokens';
import { TYPER, TYPER_LIST } from '../../constants/typer';
import { BrobygningNotater, Aftaler } from '../../api';
import { MenneskeTimeline } from './MenneskeTimeline';

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

// ─── Dansk måned-select ───────────────────────────────────────────────────────
const MAANEDER = ['Januar','Februar','Marts','April','Maj','Juni','Juli','August','September','Oktober','November','December'];

// ─── Menneske-detalje-panel (tabbed bottom-sheet) ────────────────────────────
const MenneskeDetailPanel = ({ m, onClose, onMatch }) => {
  const t   = TYPER[m.type] || TYPER.social;
  const sf  = STATUS_FARVER[m.status] || {};
  const kontakter = (m.activeCount || 0) + (m.completedCount || 0);
  const niveau    = indsatsNiveau(kontakter);

  // ── Tabs ──────────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState(0);
  const TABS = ['Profil', 'Notater', 'Tidslinje'];

  // ── Notater-tab state ─────────────────────────────────────────────────────
  const [notater,        setNotater]        = useState([]);
  const [notaterLoading, setNotaterLoading] = useState(false);
  const now = new Date();
  const [newNotat, setNewNotat] = useState({
    fritekst: '', maaned: now.getMonth() + 1, aar: now.getFullYear(), initialer: '',
  });
  const [showForm, setShowForm] = useState(false);
  const [saving,   setSaving]   = useState(false);

  useEffect(() => {
    if (activeTab !== 1) return;
    setNotaterLoading(true);
    BrobygningNotater.getByMenneske(m.id)
      .then(n => setNotater([...n].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))))
      .catch(() => setNotater([]))
      .finally(() => setNotaterLoading(false));
  }, [activeTab, m.id]);

  const handleAddNotat = async () => {
    if (!newNotat.fritekst.trim()) return;
    setSaving(true);
    try {
      const created = await BrobygningNotater.create({ menneskeId: m.id, ...newNotat });
      setNotater(prev => [created, ...prev]);
      setNewNotat({ fritekst: '', maaned: now.getMonth() + 1, aar: now.getFullYear(), initialer: '' });
      setShowForm(false);
    } catch (err) {
      console.error('BrobygningNotater.create:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteNotat = async (id) => {
    await BrobygningNotater.delete(id).catch(() => {});
    setNotater(prev => prev.filter(n => n.id !== id));
  };

  // ── Profil-rækker ─────────────────────────────────────────────────────────
  const rows = [
    { label: 'Alder',           value: m.age ? `${m.age} år` : '—' },
    { label: 'Sprog',           value: m.language || 'Dansk' },
    { label: 'Brobygningstype', value: t.label },
    { label: 'Kilde',           value: m.kilde || '—' },
    { label: 'Kontakter',       value: kontakter },
    { label: 'Indsatsniveau',   value: niveau.label, color: niveau.color },
    { label: 'Registreret',     value: m.createdAt ? new Date(m.createdAt).toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' }) : '—' },
    { label: 'HQ',              value: m.hq || '—' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', maxHeight: '85vh' }}>
      {/* ── Sticky header ─────────────────────────────────────────────────── */}
      <div style={{ padding: '16px 20px 0', flexShrink: 0 }}>
        {/* Handle */}
        <div style={{ width: 40, height: 4, borderRadius: 2, background: SoS.lineSoft, margin: '0 auto 16px' }} />

        {/* Navn + luk */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
          <Avatar initials={m.initials || ((m.firstName?.[0] || '') + (m.lastName?.[0] || ''))} bg={t.color} size={48} />
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.font, fontSize: 19, fontWeight: 500, color: SoS.ink, letterSpacing: -0.2 }}>
              {m.firstName} {m.lastName}
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 5 }}>
              <Pill variant="custom" bg={t.soft} color={t.color}>{t.short}</Pill>
              {m.status && <Pill variant="custom" bg={sf.bg || SoS.creamDeep} color={sf.color || SoS.inkSoft}>{m.status}</Pill>}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ width: 36, height: 36, borderRadius: 18, background: SoS.creamDeep, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}
          >
            <Icon name="x" size={16} color={SoS.ink} />
          </button>
        </div>

        {/* Tab-bar */}
        <div style={{ display: 'flex', gap: 2, background: SoS.creamDeep, borderRadius: 10, padding: 3 }}>
          {TABS.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              style={{
                flex: 1, padding: '7px 0', borderRadius: 8, border: 'none', cursor: 'pointer',
                fontFamily: SoS.sans, fontSize: 13, fontWeight: activeTab === i ? 600 : 400,
                background: activeTab === i ? '#fff' : 'transparent',
                color: activeTab === i ? SoS.ink : SoS.inkSoft,
                boxShadow: activeTab === i ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.15s',
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* ── Scrollbar indhold ─────────────────────────────────────────────── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px 0' }}>

        {/* ══ TAB 0: PROFIL ══════════════════════════════════════════════════ */}
        {activeTab === 0 && (
          <>
            {/* Situation og behov */}
            {m.situationOgBehov && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}`, padding: '12px 14px', marginBottom: 14 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 6 }}>
                  Situation og behov
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.55, whiteSpace: 'pre-wrap' }}>
                  {m.situationOgBehov}
                </div>
              </div>
            )}

            {/* Behov-chips */}
            {m.needs && m.needs.length > 0 && (
              <div style={{ marginBottom: 14 }}>
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
            <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 14 }}>
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
              <div style={{ background: SoS.orange + '0F', border: `1px solid ${SoS.orange}30`, borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 14 }}>
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
          </>
        )}

        {/* ══ TAB 1: NOTATER ════════════════════════════════════════════════ */}
        {activeTab === 1 && (
          <>
            {/* Tilføj-knap */}
            {!showForm && (
              <button
                onClick={() => setShowForm(true)}
                style={{
                  width: '100%', padding: '11px 0', marginBottom: 14,
                  background: '#fff', color: SoS.orange,
                  border: `1.5px dashed ${SoS.orange}60`, borderRadius: SoS.r.md,
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer',
                }}
              >
                + Tilføj notat
              </button>
            )}

            {/* Notat-formular */}
            {showForm && (
              <div style={{ background: '#fff', borderRadius: SoS.r.md, border: `1.5px solid ${SoS.orange}50`, padding: 14, marginBottom: 14 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 10 }}>
                  Nyt notat
                </div>
                <textarea
                  placeholder="Beskriv situationen – undgå navn, CPR, adresse og andre personlige oplysninger"
                  value={newNotat.fritekst}
                  onChange={e => setNewNotat(n => ({ ...n, fritekst: e.target.value }))}
                  rows={4}
                  style={{
                    width: '100%', padding: '10px 12px', marginBottom: 10,
                    fontFamily: SoS.sans, fontSize: 14, color: SoS.ink, lineHeight: 1.5,
                    background: SoS.cream, border: `1.5px solid ${SoS.lineSoft}`,
                    borderRadius: SoS.r.sm, outline: 'none', resize: 'vertical', boxSizing: 'border-box',
                  }}
                />
                <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                  <select
                    value={newNotat.maaned}
                    onChange={e => setNewNotat(n => ({ ...n, maaned: parseInt(e.target.value) }))}
                    style={{ flex: 2, padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, background: '#fff', color: SoS.ink }}
                  >
                    {MAANEDER.map((mn, i) => (
                      <option key={mn} value={i + 1}>{mn}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    placeholder="År"
                    value={newNotat.aar}
                    onChange={e => setNewNotat(n => ({ ...n, aar: parseInt(e.target.value) || now.getFullYear() }))}
                    style={{ flex: 1, padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, textAlign: 'center' }}
                  />
                  <input
                    type="text"
                    placeholder="Initialer"
                    maxLength={4}
                    value={newNotat.initialer}
                    onChange={e => setNewNotat(n => ({ ...n, initialer: e.target.value.toUpperCase() }))}
                    style={{ flex: 1, padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, textAlign: 'center' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => setShowForm(false)}
                    style={{ flex: 1, padding: '10px 0', background: '#fff', color: SoS.inkSoft, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, cursor: 'pointer' }}
                  >
                    Annuller
                  </button>
                  <button
                    onClick={handleAddNotat}
                    disabled={!newNotat.fritekst.trim() || saving}
                    style={{ flex: 2, padding: '10px 0', background: newNotat.fritekst.trim() ? SoS.orange : SoS.lineSoft, color: '#fff', border: 'none', borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: newNotat.fritekst.trim() ? 'pointer' : 'default' }}
                  >
                    {saving ? 'Gemmer…' : 'Gem notat'}
                  </button>
                </div>
              </div>
            )}

            {/* Notatliste */}
            {notaterLoading ? (
              <div style={{ padding: '20px 0', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Indlæser notater…
              </div>
            ) : notater.length === 0 ? (
              <div style={{ padding: '20px 0', textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen notater endnu — tilføj det første ovenfor.
              </div>
            ) : notater.map(n => (
              <div key={n.id} style={{ background: '#fff', borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}`, padding: '12px 14px', marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 8 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                    {MAANEDER[(n.maaned || 1) - 1]} {n.aar}
                    {n.initialer && <span style={{ marginLeft: 8, fontWeight: 700, color: SoS.ink }}>{n.initialer}</span>}
                  </div>
                  <button
                    onClick={() => handleDeleteNotat(n.id)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: SoS.inkMuted, padding: 0, lineHeight: 1 }}
                    title="Slet notat"
                  >
                    <Icon name="x" size={13} color={SoS.inkMuted} />
                  </button>
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink, lineHeight: 1.55, whiteSpace: 'pre-wrap' }}>
                  {n.fritekst}
                </div>
              </div>
            ))}
          </>
        )}

        {/* ══ TAB 2: TIDSLINJE ══════════════════════════════════════════════ */}
        {activeTab === 2 && (
          <MenneskeTimeline menneske={m} />
        )}

        {/* Luft i bunden */}
        <div style={{ height: 80 }} />
      </div>

      {/* ── Sticky footer — handlinger ────────────────────────────────────── */}
      <div style={{ padding: '12px 20px 28px', borderTop: `1px solid ${SoS.lineSoft}`, background: SoS.cream, flexShrink: 0 }}>
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
          <div style={{ width: '100%', maxWidth: 560, maxHeight: '85vh', background: SoS.cream, borderRadius: '20px 20px 0 0', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
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

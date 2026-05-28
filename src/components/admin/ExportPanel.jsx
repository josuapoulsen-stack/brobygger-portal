/**
 * src/components/admin/ExportPanel.jsx
 *
 * Anonym dataeksport — kun rådgiver/admin.
 *
 * Eksporterer brobygningsforløb som JSON (primær) eller CSV (sekundær)
 * uden personhenførbare oplysninger (ingen navne, CPR, telefon, adresse).
 *
 * FASE 1: data fra localStorage/globals via AnonymExport API
 * FASE 2: GET /v1/export/anonym?filters — samme interface
 *
 * Props:
 *   user — { id, firstName, hq, isAdmin }
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Icon } from '../shared';
import { SoS } from '../../styles/tokens';
import { AnonymExport } from '../../api';
import { TYPER_LIST } from '../../constants/typer';

// ─── Konstanter ───────────────────────────────────────────────────────────────
const STATUS_OPTIONS = [
  { id: '',          label: 'Alle' },
  { id: 'planlagt',  label: 'Planlagt'  },
  { id: 'aktiv',     label: 'Aktiv'     },
  { id: 'pause',     label: 'Pause'     },
  { id: 'afsluttet', label: 'Afsluttet' },
];

// ─── CSV-generering ───────────────────────────────────────────────────────────
const escCsv = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;

const toCsvCases = (records) => {
  const headers = [
    'menneske_id', 'age_range', 'gender', 'municipality',
    'bridging_category', 'bridging_target', 'current_status',
    'situation_og_behov', 'fritekst_antal', 'kontakt_antal',
  ];
  const rows = records.map(r => [
    r.menneske_id,
    r.age_range          || '',
    r.gender             || '',
    r.municipality       || '',
    r.bridging_category  || '',
    r.bridging_target    || '',
    r.current_status     || '',
    r.situation_og_behov || '',
    r.fritekst_entries?.length ?? 0,
    r.contact_log?.length      ?? 0,
  ].map(escCsv).join(','));
  return [headers.join(','), ...rows].join('\r\n');
};

const toCsvKontakter = (records) => {
  const headers = ['menneske_id', 'type', 'direction', 'month_year', 'duration', 'fritekst', 'source'];
  const rows = [];
  records.forEach(r => {
    (r.contact_log || []).forEach(k => {
      rows.push([r.menneske_id, k.type, k.direction, k.month_year, k.duration, k.fritekst, k.source].map(escCsv).join(','));
    });
  });
  return [headers.join(','), ...rows].join('\r\n');
};

// ─── Download-hjælper ─────────────────────────────────────────────────────────
const downloadBlob = (content, filename, mime) => {
  const blob = new Blob([content], { type: mime });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const nowYYYYMM = () => new Date().toISOString().slice(0, 7);

// ═══════════════════════════════════════════════════════════════════════════════
export const ExportPanel = ({ user }) => {
  const [dateFrom,  setDateFrom]  = useState('');
  const [dateTo,    setDateTo]    = useState('');
  const [category,  setCategory]  = useState('');
  const [status,    setStatus]    = useState('');
  const [preview,   setPreview]   = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [exporting, setExporting] = useState(false);
  const [logs,      setLogs]      = useState([]);

  // Indlæs log ved mount
  useEffect(() => {
    setLogs(AnonymExport.getLogs());
  }, []);

  // Forhåndsvisning opdateres når filtre ændres
  useEffect(() => {
    setLoading(true);
    AnonymExport.generate({ dateFrom, dateTo, category, status })
      .then(r => setPreview(r))
      .catch(() => setPreview([]))
      .finally(() => setLoading(false));
  }, [dateFrom, dateTo, category, status]);

  const logExport = useCallback((format, count) => {
    const entry = AnonymExport.addLog({
      user_id:      user?.id       || 'unknown',
      user_name:    user?.firstName || 'Ukendt',
      filters:      { dateFrom: dateFrom || null, dateTo: dateTo || null, category: category || null, status: status || null },
      record_count: count,
      format,
    });
    setLogs(prev => [entry, ...prev]);
  }, [user, dateFrom, dateTo, category, status]);

  const handleJSON = async () => {
    if (!preview?.length || exporting || loading) return;
    setExporting(true);
    try {
      const filename = `brobygger_anonym_export_${nowYYYYMM()}.json`;
      const payload  = {
        exported_at:   new Date().toISOString(),
        exported_by:   user?.id || 'unknown',
        hq:            user?.hq || null,
        filters:       { dateFrom: dateFrom || null, dateTo: dateTo || null, category: category || null, status: status || null },
        record_count:  preview.length,
        records:       preview,
      };
      downloadBlob(JSON.stringify(payload, null, 2), filename, 'application/json');
      logExport('json', preview.length);
    } finally {
      setExporting(false);
    }
  };

  const handleCSV = async () => {
    if (!preview?.length || exporting || loading) return;
    setExporting(true);
    try {
      const stamp = nowYYYYMM();
      downloadBlob(toCsvCases(preview),     `brobygger_anonym_export_${stamp}_forloeb.csv`,   'text/csv;charset=utf-8;');
      downloadBlob(toCsvKontakter(preview), `brobygger_anonym_export_${stamp}_kontakter.csv`, 'text/csv;charset=utf-8;');
      logExport('csv', preview.length);
    } finally {
      setExporting(false);
    }
  };

  const hasFilter   = dateFrom || dateTo || category || status;
  const canDownload = !!(preview?.length && !loading && !exporting);

  const filterLabel = [
    category ? TYPER_LIST.find(t => t.id === category)?.label : null,
    status   ? STATUS_OPTIONS.find(s => s.id === status)?.label : null,
    dateFrom && dateTo ? `${dateFrom} – ${dateTo}`
      : dateFrom       ? `fra ${dateFrom}`
      : dateTo         ? `til ${dateTo}`
      : null,
  ].filter(Boolean).join(' · ') || 'Alle forløb';

  return (
    <div>

      {/* ── Titel ─────────────────────────────────────────────────────────── */}
      <div style={{ marginBottom: 18 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 4 }}>
          Dataeksport · Rådgiver/Admin
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, letterSpacing: -0.2 }}>
          Anonym eksport
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginTop: 5, lineHeight: 1.6 }}>
          Brobygningsforløb eksporteret uden personhenførbare oplysninger.
          Navne, CPR, telefon og adresser er aldrig med.
        </div>
      </div>

      {/* ── Filtre ────────────────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderRadius: SoS.r.lg, border: `1px solid ${SoS.lineSoft}`, padding: 16, marginBottom: 14 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 12 }}>
          Filtre
        </div>

        {/* Dato-interval */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.inkSoft, marginBottom: 4 }}>Fra dato</div>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              style={{ width: '100%', padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.inkSoft, marginBottom: 4 }}>Til dato</div>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              style={{ width: '100%', padding: '8px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, boxSizing: 'border-box' }}
            />
          </div>
        </div>

        {/* Kategori */}
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.inkSoft, marginBottom: 4 }}>Kategori</div>
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            style={{ width: '100%', padding: '9px 10px', fontFamily: SoS.sans, fontSize: 13, border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.sm, background: '#fff', color: SoS.ink }}
          >
            <option value="">Alle kategorier</option>
            {TYPER_LIST.map(t => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.inkSoft, marginBottom: 6 }}>Status</div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {STATUS_OPTIONS.map(opt => {
              const on = status === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => setStatus(opt.id)}
                  style={{
                    padding: '6px 13px', borderRadius: 999, cursor: 'pointer',
                    fontFamily: SoS.sans, fontSize: 12, fontWeight: on ? 700 : 400,
                    background: on ? SoS.ink : '#fff',
                    color:      on ? '#fff'  : SoS.inkSoft,
                    border: `1.5px solid ${on ? SoS.ink : SoS.lineSoft}`,
                  }}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Nulstil */}
        {hasFilter && (
          <button
            onClick={() => { setDateFrom(''); setDateTo(''); setCategory(''); setStatus(''); }}
            style={{ marginTop: 10, background: 'none', border: 'none', cursor: 'pointer', fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, padding: 0 }}
          >
            × Nulstil filtre
          </button>
        )}
      </div>

      {/* ── Forhåndsvisning ───────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderRadius: SoS.r.md, border: `1px solid ${SoS.lineSoft}`, padding: '13px 16px', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ width: 40, height: 40, borderRadius: 20, background: SoS.orange + '15', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="chart" size={18} color={SoS.orange} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500, color: SoS.ink }}>
            {loading ? '…' : `${preview?.length ?? 0} forløb`}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
            {filterLabel}
          </div>
        </div>
        {!loading && preview?.length > 0 && (
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, textAlign: 'right' }}>
            {preview.reduce((s, r) => s + (r.contact_log?.length ?? 0), 0)} kontakter<br />
            {preview.reduce((s, r) => s + (r.fritekst_entries?.length ?? 0), 0)} notater
          </div>
        )}
      </div>

      {/* ── Download-knapper ──────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
        <button
          onClick={handleJSON}
          disabled={!canDownload}
          style={{
            flex: 3, padding: '13px 0',
            background: canDownload ? SoS.orange : SoS.lineSoft,
            color: '#fff', border: 'none', borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
            cursor: canDownload ? 'pointer' : 'default',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
          }}
        >
          <Icon name="note" size={16} color="#fff" />
          {exporting ? 'Eksporterer…' : 'Download JSON'}
        </button>
        <button
          onClick={handleCSV}
          disabled={!canDownload}
          style={{
            flex: 2, padding: '13px 0',
            background: '#fff',
            color:  canDownload ? SoS.ink : SoS.inkMuted,
            border: `1.5px solid ${canDownload ? SoS.line : SoS.lineSoft}`,
            borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
            cursor: canDownload ? 'pointer' : 'default',
          }}
        >
          CSV (2 filer)
        </button>
      </div>

      {/* ── GDPR-note ─────────────────────────────────────────────────────── */}
      <div style={{ background: SoS.orange + '09', border: `1px solid ${SoS.orange}25`, borderRadius: SoS.r.md, padding: '10px 14px', marginBottom: 20, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <Icon name="shield" size={14} color={SoS.orange} />
        <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.55, flex: 1 }}>
          Eksporten indeholder <strong>ingen personhenførbare oplysninger.</strong>{' '}
          Mennesker kan ikke identificeres. Menneske-ID er et pseudonymt systemID.
          Alle eksporter logges med brugernavn, tidspunkt og filter.
        </div>
      </div>

      {/* ── Eksport-log ───────────────────────────────────────────────────── */}
      <div>
        <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 10 }}>
          Eksport-log
        </div>
        {logs.length === 0 ? (
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted, paddingBottom: 8 }}>
            Ingen eksporter registreret endnu.
          </div>
        ) : logs.slice(0, 20).map((log, i) => (
          <div
            key={log.id}
            style={{
              display: 'flex', gap: 12, padding: '10px 0',
              borderBottom: i < Math.min(logs.length, 20) - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
            }}
          >
            {/* Format-badge */}
            <div style={{
              flexShrink: 0, width: 36, height: 36, borderRadius: 8,
              background: log.format === 'json' ? SoS.orange + '15' : '#E3F2FD',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 800, color: log.format === 'json' ? SoS.orange : '#1565C0' }}>
                {(log.format || 'JSON').toUpperCase()}
              </span>
            </div>

            {/* Tekst */}
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>
                {log.user_name} · {log.record_count} forløb
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 2 }}>
                {new Date(log.timestamp).toLocaleString('da-DK', {
                  day: 'numeric', month: 'short', year: 'numeric',
                  hour: '2-digit', minute: '2-digit',
                })}
                {Object.values(log.filters || {}).some(Boolean) && (
                  <span> · {Object.entries(log.filters).filter(([, v]) => v).map(([, v]) => v).join(', ')}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

export default ExportPanel;

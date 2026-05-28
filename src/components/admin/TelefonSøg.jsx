/**
 * src/components/admin/TelefonSøg.jsx
 *
 * Flydende telefon-søgekort til adminoversigten.
 * Koordinatoren taster et nummer mens de er i opkald — systemet slår
 * øjeblikkeligt op og viser det matchende menneske.
 *
 * Props:
 *   mennesker     — { [id]: menneskeObj }  (fra AdminApp-state)
 *   onOpenProfil  — (id: string) => void   — navigerer til menneskets profil
 */

import React, { useState, useEffect, useRef } from 'react';
import { SoS } from '../../styles/tokens';
import { Icon } from '../shared/Icon';
import { TYPER } from '../../constants/typer';

// ── Normalisér telefonnummer til 8 cifre ──────────────────────────────────────
function normaliser(str) {
  // Fjern alt der ikke er cifre, strip +45 forrest
  return str.replace(/\D/g, '').replace(/^45/, '');
}

// ── Status-farver (spejlet fra DesktopMennesker) ──────────────────────────────
const STATUS_FARVER = {
  aktiv:     { bg: '#E8F5E9', color: '#388E3C' },
  venter:    { bg: '#FFF3E0', color: '#E87A3E' },
  pause:     { bg: '#F5F5F5', color: '#9E9E9E' },
  afsluttet: { bg: '#FCE4EC', color: '#C62828' },
};

// ─────────────────────────────────────────────────────────────────────────────
export function TelefonSøg({ mennesker = {}, onOpenProfil }) {
  const [åben,    setÅben]    = useState(false);
  const [query,   setQuery]   = useState('');
  const [resultat, setResultat] = useState(null); // null | 'ingen' | menneskeObj
  const inputRef = useRef(null);
  const kortRef  = useRef(null);

  // Auto-focus input når kortet åbnes
  useEffect(() => {
    if (åben) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
      setResultat(null);
    }
  }, [åben]);

  // Luk ved klik udenfor
  useEffect(() => {
    if (!åben) return;
    const handler = (e) => {
      if (kortRef.current && !kortRef.current.contains(e.target)) {
        setÅben(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [åben]);

  // Søg i realtid mens der tastes
  useEffect(() => {
    const normQ = normaliser(query);
    if (normQ.length < 2) {
      setResultat(null);
      return;
    }
    const alle = Object.values(mennesker);
    const match = alle.find(m => {
      const kontakt = normaliser(m.contact || '');
      return kontakt.length >= 2 && kontakt.includes(normQ);
    });
    setResultat(match ?? 'ingen');
  }, [query, mennesker]);

  const handleÅbn = (id) => {
    setÅben(false);
    onOpenProfil?.(id);
  };

  return (
    <div
      ref={kortRef}
      style={{
        position: 'absolute',
        bottom:   96,          // lige over tab-baren (88px + lidt luft)
        right:    18,
        zIndex:   60,
      }}
    >
      {/* Søgekort — vises når åben */}
      {åben && (
        <div style={{
          position:     'absolute',
          bottom:       56,          // over knappen
          right:        0,
          width:        290,
          background:   '#fff',
          borderRadius: 16,
          boxShadow:    '0 8px 32px rgba(0,0,0,0.14), 0 2px 8px rgba(0,0,0,0.08)',
          overflow:     'hidden',
          border:       `1px solid ${SoS.lineSoft}`,
          animation:    'sos-slide-up 0.15s ease',
        }}>
          {/* Kort-header */}
          <div style={{
            padding:        '12px 14px 10px',
            borderBottom:   `1px solid ${SoS.lineSoft}`,
            background:     SoS.creamDeep,
          }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: SoS.inkMuted, textTransform: 'uppercase', letterSpacing: 0.8 }}>
              Opslag på telefonnummer
            </div>
          </div>

          {/* Input */}
          <div style={{ padding: '12px 14px 10px' }}>
            <div style={{
              display:      'flex',
              alignItems:   'center',
              gap:          8,
              background:   SoS.cream,
              borderRadius: 999,
              padding:      '9px 14px',
              border:       `1.5px solid ${SoS.line}`,
            }}>
              <Icon name="phone" size={15} color={SoS.inkMuted} />
              <input
                ref={inputRef}
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Tast nummer…  f.eks. 12 34 56 78"
                type="tel"
                inputMode="tel"
                style={{
                  flex:       1,
                  border:     'none',
                  outline:    'none',
                  background: 'transparent',
                  fontFamily: SoS.sans,
                  fontSize:   15,
                  color:      SoS.ink,
                  letterSpacing: 0.5,
                }}
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  style={{ background: 'none', border: 'none', cursor: 'pointer',
                    color: SoS.inkMuted, fontSize: 18, padding: 0, lineHeight: 1 }}
                >×</button>
              )}
            </div>
          </div>

          {/* Resultat */}
          {resultat && (
            <div style={{ padding: '0 14px 14px' }}>
              {resultat === 'ingen' ? (
                <div style={{
                  background:   SoS.creamDeep,
                  borderRadius: 10,
                  padding:      '12px 14px',
                  fontFamily:   SoS.sans,
                  fontSize:     13,
                  color:        SoS.inkMuted,
                  textAlign:    'center',
                }}>
                  Ingen menneske fundet med dette nummer
                </div>
              ) : (
                <ResultatKort m={resultat} onÅbn={handleÅbn} />
              )}
            </div>
          )}

          {/* Vejledning */}
          {!resultat && (
            <div style={{ padding: '0 14px 14px' }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
                textAlign: 'center', lineHeight: 1.5 }}>
                Brug mens du er i et opkald —<br />
                systemet slår op med det samme
              </div>
            </div>
          )}
        </div>
      )}

      {/* Flydende knap */}
      <button
        onClick={() => setÅben(v => !v)}
        aria-label="Søg på telefonnummer"
        style={{
          width:        48,
          height:       48,
          borderRadius: 24,
          background:   åben ? SoS.ink : SoS.orange,
          border:       'none',
          cursor:       'pointer',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'center',
          boxShadow:    '0 4px 16px rgba(0,0,0,0.18)',
          transition:   'background 0.15s',
          flexShrink:   0,
        }}
      >
        <Icon name={åben ? 'x' : 'phone'} size={22} color="#fff" />
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  ResultatKort — viser den fundne person
// ─────────────────────────────────────────────────────────────────────────────
function ResultatKort({ m, onÅbn }) {
  const type = TYPER[m.type] || TYPER.social;
  const sf   = STATUS_FARVER[m.status] || {};
  const navn = [m.firstName, m.lastName].filter(Boolean).join(' ');

  return (
    <div style={{
      background:   '#fff',
      borderRadius: 12,
      border:       `1.5px solid ${SoS.line}`,
      overflow:     'hidden',
    }}>
      {/* Farvet top-streg */}
      <div style={{ height: 3, background: type.color }} />

      <div style={{ padding: '12px 14px 10px' }}>
        {/* Navn + type */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 18,
            background: type.soft,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Icon name={type.icon} size={18} color={type.color} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 700,
              color: SoS.ink, whiteSpace: 'nowrap', overflow: 'hidden',
              textOverflow: 'ellipsis' }}>
              {navn || 'Ukendt'}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: type.color, fontWeight: 600 }}>
              {type.label}
            </div>
          </div>
        </div>

        {/* Detaljer */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
          {/* Status */}
          {m.status && (
            <span style={{
              background:   sf.bg || SoS.creamDeep,
              color:        sf.color || SoS.inkSoft,
              borderRadius: 999,
              padding:      '3px 10px',
              fontFamily:   SoS.sans,
              fontSize:     11,
              fontWeight:   700,
            }}>
              {m.status.charAt(0).toUpperCase() + m.status.slice(1)}
            </span>
          )}
          {/* Alder */}
          {m.age && (
            <span style={{
              background:   SoS.creamDeep,
              color:        SoS.inkSoft,
              borderRadius: 999,
              padding:      '3px 10px',
              fontFamily:   SoS.sans,
              fontSize:     11,
              fontWeight:   600,
            }}>
              {m.age} år
            </span>
          )}
          {/* HQ */}
          {m.hq && (
            <span style={{
              background:   SoS.creamDeep,
              color:        SoS.inkSoft,
              borderRadius: 999,
              padding:      '3px 10px',
              fontFamily:   SoS.sans,
              fontSize:     11,
            }}>
              {m.hq}
            </span>
          )}
        </div>

        {/* Tlf (viser det matchede nummer) */}
        <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted,
          marginBottom: 12 }}>
          📞 {m.contact}
        </div>

        {/* Knap */}
        <button
          onClick={() => onÅbn(m.id)}
          style={{
            width:        '100%',
            padding:      '10px 0',
            background:   SoS.orange,
            color:        '#fff',
            border:       'none',
            borderRadius: 10,
            fontFamily:   SoS.sans,
            fontSize:     14,
            fontWeight:   700,
            cursor:       'pointer',
          }}
        >
          Åbn profil →
        </button>
      </div>
    </div>
  );
}

export default TelefonSøg;

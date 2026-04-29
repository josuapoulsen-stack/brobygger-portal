/**
 * src/components/brobygger/KalenderScreen.jsx
 *
 * Brobyggerens kalender — migreret fra prototype CalendarScreen.
 * Månedsgrid med aftaler (orange dot) og rådighedsvagter (grøn dot).
 *
 * Props:
 *   appointments — Array<Aftale>
 *   shifts       — Array<{ id, date, start, end, booked }>
 *   mennesker    — Record<id, Menneske>
 *   onOpenAppt   — (id) => void
 *   onAddShift   — () => void  — åbn "meld rådighed"-flow
 */

import React, { useState } from 'react';
import { SoS }          from '../../styles/tokens';
import { Icon, TopBar, SectionHead, Button, Pill } from '../shared';
import { TYPER }             from '../../constants/typer';
import { formatDatoFull }    from '../../utils/dates';

const MND = ['Januar','Februar','Marts','April','Maj','Juni',
             'Juli','August','September','Oktober','November','December'];

function isoToday() {
  return new Date().toISOString().slice(0, 10);
}

function buildGrid(year, month) {
  const firstDay    = new Date(year, month, 1);
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const startWD     = (firstDay.getDay() + 6) % 7; // Mandag-first
  const cells       = [];
  for (let i = 0; i < startWD; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
}

export function KalenderScreen({ appointments = [], shifts = [], mennesker = {}, onOpenAppt, onAddShift }) {
  const today  = isoToday();
  const [month, setMonth] = useState(() => {
    const d = new Date(today); d.setDate(1); return d;
  });
  const [selected, setSelected] = useState(today);

  const year  = month.getFullYear();
  const m     = month.getMonth();
  const cells = buildGrid(year, m);

  const apptsByDate  = {};
  appointments.forEach(a => { (apptsByDate[a.date]  ||= []).push(a); });
  const shiftsByDate = {};
  shifts.forEach(s       => { (shiftsByDate[s.date] ||= []).push(s); });

  const selectedAppts  = apptsByDate[selected]  || [];
  const selectedShifts = shiftsByDate[selected] || [];

  return (
    <>
      <TopBar
        title="Kalender"
        subtitle="Dine vagter og aftaler"
        trailing={
          <button onClick={onAddShift} style={{
            height: 44, padding: '0 16px', borderRadius: 22,
            background: SoS.orange, color: '#fff', border: 'none',
            display: 'flex', alignItems: 'center', gap: 6,
            fontFamily: SoS.sans, fontSize: 14, fontWeight: 600,
            boxShadow: SoS.shadow.glow, cursor: 'pointer',
          }}>
            <Icon name="plus" size={18} color="#fff" weight={2.5} />
            Rådighed
          </button>
        }
      />

      {/* Måneds-navigation */}
      <div style={{ padding: '4px 20px 16px', display: 'flex',
        alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
          color: SoS.ink, letterSpacing: -0.2 }}>
          {MND[m]} {year}
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {[
            { fn: () => setMonth(d => new Date(d.getFullYear(), d.getMonth() - 1, 1)), icon: 'chevronL' },
            { fn: () => setMonth(d => new Date(d.getFullYear(), d.getMonth() + 1, 1)), icon: 'chevron'  },
          ].map(({ fn, icon }) => (
            <button key={icon} onClick={fn} style={{
              width: 36, height: 36, borderRadius: 18,
              background: '#fff', border: `1px solid ${SoS.line}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
            }}>
              <Icon name={icon} size={18} color={SoS.ink} />
            </button>
          ))}
        </div>
      </div>

      {/* Dag-labels */}
      <div style={{ padding: '0 20px', display: 'grid',
        gridTemplateColumns: 'repeat(7, 1fr)', marginBottom: 8 }}>
        {['M','T','O','T','F','L','S'].map((d, i) => (
          <div key={i} style={{ textAlign: 'center', fontFamily: SoS.sans,
            fontSize: 11, fontWeight: 600, color: SoS.inkMuted, letterSpacing: 0.8 }}>
            {d}
          </div>
        ))}
      </div>

      {/* Kalendergrid */}
      <div style={{ padding: '0 12px 20px', display: 'grid',
        gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
        {cells.map((d, i) => {
          if (!d) return <div key={i} />;
          const iso      = `${year}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
          const isSel    = iso === selected;
          const isNow    = iso === today;
          const hasAppts = (apptsByDate[iso]  || []).length;
          const hasShift = (shiftsByDate[iso] || []).length;
          return (
            <button key={i} onClick={() => setSelected(iso)} style={{
              aspectRatio: '1', border: 'none', cursor: 'pointer',
              background:  isSel ? SoS.orange : 'transparent',
              borderRadius: 12, padding: 0,
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', outline: 'none',
            }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 15,
                fontWeight: isNow || isSel ? 700 : 500,
                color: isSel ? '#fff' : (isNow ? SoS.orange : SoS.ink) }}>
                {d}
              </div>
              {(hasAppts || hasShift) && (
                <div style={{ display: 'flex', gap: 2, marginTop: 2 }}>
                  {hasAppts > 0 && <div style={{ width: 4, height: 4, borderRadius: 2,
                    background: isSel ? '#fff' : SoS.orange }} />}
                  {hasShift > 0 && <div style={{ width: 4, height: 4, borderRadius: 2,
                    background: isSel ? 'rgba(255,255,255,0.6)' : SoS.sage }} />}
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Forklaring */}
      <div style={{ padding: '0 20px 16px', display: 'flex', gap: 18 }}>
        {[{ color: SoS.orange, label: 'Aftale' }, { color: SoS.sage, label: 'Rådighed' }].map(({ color, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: 4, background: color }} />
            <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Valgt dag */}
      <div style={{ padding: '0 20px 20px' }}>
        <SectionHead title={formatDatoFull(selected)} />

        {selectedAppts.length === 0 && selectedShifts.length === 0 && (
          <div style={{ padding: '28px 20px', background: '#fff', borderRadius: SoS.r.lg,
            border: `1px dashed ${SoS.line}`, textAlign: 'center' }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft, marginBottom: 12 }}>
              Ingen aftaler eller vagter
            </div>
            <Button variant="secondary" onClick={onAddShift}
              icon={<Icon name="plus" size={16} color={SoS.ink} weight={2.3} />}>
              Meld rådig denne dag
            </Button>
          </div>
        )}

        {selectedAppts.map(a => {
          const menneske = mennesker[a.menneskeId];
          const type     = TYPER[menneske?.type] ?? TYPER.social;
          return (
            <div key={a.id} onClick={() => onOpenAppt?.(a.id)} style={{
              display: 'flex', gap: 12, padding: 14, background: '#fff',
              borderRadius: SoS.r.md, marginBottom: 8, cursor: 'pointer',
              border: `1px solid ${SoS.lineSoft}`, borderLeft: `4px solid ${SoS.orange}`,
            }}>
              <div style={{ textAlign: 'center', minWidth: 48 }}>
                <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500, color: SoS.ink }}>
                  {a.start}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>{a.end}</div>
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink, marginBottom: 2 }}>
                  {menneske?.firstName ?? 'Ukendt'}{menneske?.age ? ` (${menneske.age})` : ''}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 6 }}>
                  {a.activity}
                </div>
                <Pill bg={type.soft} color={type.color}
                  icon={<Icon name={type.icon} size={11} color={type.color} weight={2.2} />}>
                  {type.short}
                </Pill>
              </div>
              <Icon name="chevron" size={18} color={SoS.inkMuted} />
            </div>
          );
        })}

        {selectedShifts.map(s => (
          <div key={s.id} style={{
            display: 'flex', alignItems: 'center', gap: 14, padding: 14,
            background: s.booked ? SoS.sageSoft : '#fff',
            borderRadius: SoS.r.md, marginBottom: 8,
            border: `1px solid ${s.booked ? SoS.sage + '55' : SoS.lineSoft}`,
            borderLeft: `4px solid ${SoS.sage}`,
          }}>
            <Icon name={s.booked ? 'check' : 'clock'} size={20}
              color={s.booked ? SoS.sage : SoS.inkMuted} />
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                Rådighed {s.start}–{s.end}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                {s.booked ? 'Booket af koordinator' : 'Åben vagt'}
              </div>
            </div>
            <Pill variant={s.booked ? 'bekræftet' : 'ny'}>
              {s.booked ? 'Booket' : 'Ledig'}
            </Pill>
          </div>
        ))}
      </div>
    </>
  );
}

export default KalenderScreen;

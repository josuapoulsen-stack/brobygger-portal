/**
 * src/components/admin/MatchingFlow.jsx
 *
 * 3-trins matching-flow: Menneske → Brobygger → Bekræft
 * FASE 1: localStorage-data via useMatching + api/index.js mock
 * FASE 2: skift USE_BACKEND=true → rigtige API-kald
 *
 * Props:
 *   onClose()          — lukker flowet
 *   mennesker          — { [id]: menneskeObj }
 *   brobyggere         — [ brobyggerObj ]
 *   appointments       — [ apptObj ]  (til "sidst fælles")
 */

import React, { useState, useEffect } from 'react';
import { Avatar, Icon, Pill } from '../shared';
import { SoS } from '../../styles/tokens';
import { TYPER } from '../../constants/typer';
import { useMatching } from '../../hooks/useMatching';

// ─── Trin-indikator (vandret bjælke) ─────────────────────────────────────────
const StepDots = ({ step, total, color = SoS.orange }) => (
  <div style={{ display: 'flex', gap: 6, justifyContent: 'center', padding: '8px 0 16px' }}>
    {Array.from({ length: total }).map((_, i) => (
      <div key={i} style={{
        width: i === step ? 24 : 8, height: 8, borderRadius: 4,
        background: i <= step ? color : SoS.lineSoft,
        transition: 'all 0.2s',
      }} />
    ))}
  </div>
);

// ─── Trin 1: Brobygger-valg ──────────────────────────────────────────────────
const MatchingStepBrobygger = ({ menneske, brobyggerId, setBrobyggerId, brobyggere, appointments }) => {
  const DURATIONS_MAP = { 30: '30 min', 60: '1 time', 90: '1½ time', 120: '2 timer' };

  const available = [...brobyggere]
    .filter(b => b.status === 'aktiv' || b.status === 'ny')
    .sort((a, b) => (b.openShifts || 0) - (a.openShifts || 0));

  const prevBb = menneske.previousBrobygger
    ? brobyggere.find(b => b.id === menneske.previousBrobygger)
    : null;

  // Sidst fælles aftale
  const lastAppt = prevBb
    ? [...appointments]
        .filter(a => a.menneskeId === menneske.id && a.brobyggerId === prevBb.id)
        .sort((a, b) => b.date.localeCompare(a.date))[0]
    : null;

  useEffect(() => {
    if (prevBb && !brobyggerId) setBrobyggerId(prevBb.id);
  }, [menneske.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const others = available.filter(b => !prevBb || b.id !== prevBb.id);

  const BrobyggerCard = ({ b, isPrev }) => {
    const sel = brobyggerId === b.id;
    const hasShift = (b.openShifts || 0) > 0;
    return (
      <button
        onClick={() => setBrobyggerId(b.id)}
        style={{
          display: 'flex', gap: 12, alignItems: 'center', width: '100%',
          padding: 14, marginBottom: isPrev ? 16 : 8, textAlign: 'left',
          background: isPrev ? '#FFFBF5' : '#fff',
          border: `2px solid ${sel ? SoS.orange : isPrev ? '#E8A84B' : SoS.lineSoft}`,
          borderRadius: SoS.r.md, cursor: 'pointer',
          boxShadow: sel ? SoS.shadow.md : isPrev ? '0 2px 10px rgba(232,168,75,0.15)' : 'none',
          opacity: !hasShift && !sel && !isPrev ? 0.55 : 1,
          position: 'relative', overflow: 'hidden',
        }}
      >
        {/* Gylden venstre-kant */}
        {isPrev && (
          <div style={{
            position: 'absolute', left: 0, top: 0, bottom: 0,
            width: 4,
            background: 'linear-gradient(180deg, #E8C14B, #E8904B)',
          }} />
        )}
        <div style={{
          paddingLeft: isPrev ? 4 : 0, display: 'flex', gap: 12,
          alignItems: 'center', flex: 1, minWidth: 0,
        }}>
          {/* Avatar med stjerne-overlay for forrige brobygger */}
          <div style={{ position: 'relative', flexShrink: 0 }}>
            <Avatar initials={b.avatar || b.initials} bg={b.bg} size={44} />
            {isPrev && (
              <div style={{
                position: 'absolute', bottom: -3, right: -3,
                width: 18, height: 18, borderRadius: 9,
                background: '#E8C14B', border: '2px solid #FFFBF5',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon name="star" size={9} color="#fff" />
              </div>
            )}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                {b.name || b.navn}
              </span>
              {hasShift ? (
                <span style={{
                  fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                  color: SoS.sage, background: SoS.sageSoft,
                  padding: '2px 7px', borderRadius: 999,
                }}>
                  {b.openShifts} ledige vagter
                </span>
              ) : (
                <span style={{
                  fontFamily: SoS.sans, fontSize: 10,
                  color: SoS.inkMuted, background: SoS.lineSoft + '88',
                  padding: '2px 7px', borderRadius: 999,
                }}>
                  Ingen vagter
                </span>
              )}
            </div>
            {isPrev ? (
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: '#B87A20', fontWeight: 500 }}>
                {lastAppt
                  ? `Sidst tilknyttet ${new Date(lastAppt.date).toLocaleDateString('da-DK', { day: 'numeric', month: 'long' })}`
                  : 'Tidl. tilknyttet brobygger — personen ønsker dem igen'}
              </div>
            ) : (
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>
                {b.active ?? 0} aktive forløb · {b.thisMonth ?? 0} aftaler denne måned
              </div>
            )}
          </div>
          {sel ? (
            <div style={{
              width: 24, height: 24, borderRadius: 12,
              background: SoS.orange, display: 'flex',
              alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <Icon name="check" size={14} color="#fff" />
            </div>
          ) : isPrev ? (
            <div style={{ flexShrink: 0, opacity: 0.5 }}>
              <Icon name="chevron" size={16} color={SoS.inkMuted} />
            </div>
          ) : null}
        </div>
      </button>
    );
  };

  return (
    <>
      <div style={{
        fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
        color: SoS.ink, marginBottom: 4, letterSpacing: -0.2,
      }}>
        Vælg brobygger
      </div>
      {menneske.brobygning ? (
        <div style={{
          background: SoS.orange + '0F',
          border: '1px solid ' + SoS.orange + '30',
          borderRadius: SoS.r.md, padding: '10px 14px', marginBottom: 16,
          display: 'flex', flexWrap: 'wrap', gap: '4px 16px',
        }}>
          <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.orangeDeep, fontWeight: 700 }}>
            {new Date(menneske.brobygning.dato).toLocaleDateString('da-DK', {
              weekday: 'long', day: 'numeric', month: 'long',
            })}
            {' kl. '}{menneske.brobygning.start}
          </span>
          {menneske.brobygning.frekvens && (
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.orangeDeep }}>
              · {menneske.brobygning.frekvens}
            </span>
          )}
          {menneske.brobygning.duration && (
            <span style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.orangeDeep }}>
              · {DURATIONS_MAP[menneske.brobygning.duration] || ''}
            </span>
          )}
        </div>
      ) : (
        <div style={{
          fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
          marginBottom: 16, lineHeight: 1.5,
        }}>
          Sorteret efter ledige vagter.
        </div>
      )}

      {/* Forrige brobygger */}
      {prevBb && (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 8 }}>
            <Icon name="star" size={13} color="#E8C14B" />
            <span style={{
              fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: '#B87A20', letterSpacing: 0.5, textTransform: 'uppercase',
            }}>
              Ønsket brobygger fra tidligere
            </span>
          </div>
          <BrobyggerCard b={prevBb} isPrev={true} />
        </>
      )}

      {/* Øvrige brobyggere */}
      {others.length > 0 && (
        <>
          {prevBb && (
            <div style={{
              fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
              color: SoS.inkMuted, letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 8,
            }}>
              Øvrige brobyggere
            </div>
          )}
          {others.map(b => <BrobyggerCard key={b.id} b={b} isPrev={false} />)}
        </>
      )}
    </>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const MatchingFlow = ({ onClose, mennesker = {}, brobyggere = [], appointments = [] }) => {
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const [menneskeId, setMenneskeId] = useState(null);
  const [brobyggerId, setBrobyggerId] = useState(null);

  // Aftaldetaljer (bruges når menneske.brobygning er null)
  const today = new Date();
  const isoToday = today.toISOString().split('T')[0];
  const [aftaleDato] = useState(isoToday);
  const [aftaleStart, setAftaleStart] = useState(null);
  const [aftaleDuration, setAftaleDuration] = useState(null);

  const { bekræftMatch } = useMatching();

  const menneske = menneskeId ? mennesker[menneskeId] : null;
  const type = menneske ? (TYPER[menneske.type] || TYPER.social) : null;
  const brobygger = brobyggerId ? brobyggere.find(b => b.id === brobyggerId) : null;

  const STEPS = ['Menneske', 'Brobygger', 'Bekræft'];

  const DURATIONS = [
    { label: '30 min', v: 30 },
    { label: '1 time', v: 60 },
    { label: '1½ time', v: 90 },
    { label: '2 timer', v: 120 },
  ];

  const canNext =
    (step === 0 && !!menneskeId) ||
    (step === 1 && !!brobyggerId) ||
    step === 2;

  const fmtDato = (d) =>
    d ? new Date(d).toLocaleDateString('da-DK', { weekday: 'long', day: 'numeric', month: 'long' }) : '';

  const handleSend = async () => {
    const bdata = (menneske.brobygning) || {};
    const dato     = bdata.dato     || aftaleDato;
    const start    = bdata.start    || aftaleStart;
    const duration = bdata.duration || aftaleDuration;

    // FASE 1: mock via useMatching (USE_BACKEND=false)
    // FASE 2: rigtig API-oprettelse via Aftaler.create()
    await bekræftMatch({
      menneskeId,
      brobyggerId,
      dato, start, duration,
      frekvens: bdata.frekvens || null,
    });

    setDone(true);
  };

  // ── Done-skærm ─────────────────────────────────────────────────────────────
  if (done) return (
    <div style={{
      position: 'fixed', inset: 0, background: SoS.cream, zIndex: 200,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: 32,
    }}>
      <div style={{
        width: 72, height: 72, borderRadius: 36, background: SoS.sageSoft,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20,
      }}>
        <Icon name="check" size={32} color={SoS.sage} />
      </div>
      <div style={{
        fontFamily: SoS.font, fontSize: 26, fontWeight: 500,
        color: SoS.ink, textAlign: 'center', marginBottom: 8,
      }}>
        Matching oprettet!
      </div>
      <div style={{
        fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        textAlign: 'center', lineHeight: 1.6, marginBottom: 24,
      }}>
        {brobygger && `${(brobygger.name || brobygger.navn || '').split(' ')[0]} modtager en besked om aftalen.`}
      </div>

      {/* Ring og bekræft — opgave-kort */}
      {menneske && (
        <div style={{
          width: '100%', maxWidth: 400, background: '#fff', borderRadius: SoS.r.xl,
          padding: 20, border: `2px solid ${SoS.orange}33`, marginBottom: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <div style={{
              width: 38, height: 38, borderRadius: 19,
              background: SoS.orange + '22', display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Icon name="phone" size={18} color={SoS.orange} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 700, color: SoS.ink }}>
                Din opgave
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft }}>
                Skal gøres snarest
              </div>
            </div>
            <span style={{
              fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
              color: SoS.orange, background: SoS.orange + '18',
              padding: '3px 8px', borderRadius: 999,
            }}>
              Ventende
            </span>
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.ink, lineHeight: 1.6, marginBottom: 14 }}>
            Ring <strong>{menneske.firstName} {(menneske.lastName || '')[0]}.</strong> og bekræft aftalen med{' '}
            {brobygger && `${(brobygger.name || brobygger.navn || '').split(' ')[0]}`}
            {' — '}{fmtDato((menneske.brobygning || {}).dato || aftaleDato)}
            {' kl. '}{(menneske.brobygning || {}).start || aftaleStart}.
          </div>
          <div style={{
            background: SoS.creamDeep, borderRadius: SoS.r.md,
            padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <Icon name="phone" size={14} color={SoS.inkSoft} />
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted }}>
                {menneske.contact?.name || 'Kontakt'}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 700, color: SoS.ink }}>
                {menneske.contact?.phone || menneske.contact}
              </div>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={onClose}
        style={{
          width: '100%', maxWidth: 400, padding: '15px 0',
          background: SoS.orange, color: '#fff', border: 'none',
          borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 15,
          fontWeight: 600, cursor: 'pointer',
        }}
      >
        Luk og gå til oversigt
      </button>
    </div>
  );

  // ── Flow-skærm ──────────────────────────────────────────────────────────────
  return (
    <div style={{
      position: 'fixed', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column', zIndex: 200,
    }}>
      {/* Header */}
      <div style={{
        padding: '54px 20px 12px', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`,
      }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginBottom: 10,
        }}>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.inkSoft,
            }}
          >
            Afbryd
          </button>
          <div style={{
            fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 1, textTransform: 'uppercase',
          }}>
            Ny matching · {step + 1}/{STEPS.length}
          </div>
          <div style={{ width: 60 }} />
        </div>
        <StepDots step={step} total={STEPS.length} />
      </div>

      {/* Indhold */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>

        {/* ── Trin 0: Vælg menneske ── */}
        {step === 0 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Vælg menneske
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, marginBottom: 16,
            }}>
              Mennesker der venter på match.
            </div>
            {Object.values(mennesker).map(b => {
              const t = TYPER[b.type] || TYPER.social;
              const sel = menneskeId === b.id;
              return (
                <React.Fragment key={b.id}>
                  <button
                    onClick={() => setMenneskeId(b.id)}
                    style={{
                      display: 'flex', gap: 12, width: '100%', padding: 14,
                      marginBottom: 4, textAlign: 'left',
                      background: sel ? t.soft : '#fff',
                      border: `2px solid ${sel ? t.color : SoS.lineSoft}`,
                      borderRadius: SoS.r.md, cursor: 'pointer',
                    }}
                  >
                    <Avatar initials={b.initials} bg={t.color} size={44} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                        {b.firstName} {(b.lastName || '')[0]}. ({b.age})
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                        {(b.needs || []).slice(0, 2).join(' · ')}
                      </div>
                      <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                        <Pill variant="custom" bg={t.soft} color={t.color}>{t.short}</Pill>
                        <Pill variant="custom" bg={SoS.creamDeep} color={SoS.inkSoft}>
                          {(b.language || 'Dansk').split(',')[0]}
                        </Pill>
                      </div>
                    </div>
                  </button>
                  {b.brobygning && (
                    <div style={{
                      marginBottom: 8, padding: '6px 12px',
                      background: SoS.orange + '12', borderRadius: SoS.r.md,
                      border: `1px solid ${SoS.orange}30`,
                      display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap',
                    }}>
                      <Icon name="match" size={12} color={SoS.orange} />
                      <span style={{
                        fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, fontWeight: 600,
                      }}>
                        {new Date(b.brobygning.dato).toLocaleDateString('da-DK', {
                          weekday: 'long', day: 'numeric', month: 'long',
                        })}
                        {' kl. '}{b.brobygning.start}
                        {b.brobygning.frekvens ? ' · ' + b.brobygning.frekvens : ''}
                      </span>
                    </div>
                  )}
                  {b.previousBrobygger && (
                    <div style={{
                      marginBottom: 8, padding: '4px 10px',
                      background: SoS.orange + '18', borderRadius: 999,
                      display: 'inline-flex', gap: 6, alignItems: 'center',
                    }}>
                      <span style={{
                        fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, fontWeight: 700,
                      }}>
                        ↩ Ønsker genbrug af brobygger
                      </span>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
            {Object.keys(mennesker).length === 0 && (
              <div style={{
                padding: 24, textAlign: 'center',
                fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
              }}>
                Ingen mennesker venter på match.
              </div>
            )}
          </>
        )}

        {/* ── Trin 1: Vælg brobygger ── */}
        {step === 1 && menneske && (
          <MatchingStepBrobygger
            menneske={menneske}
            brobyggerId={brobyggerId}
            setBrobyggerId={setBrobyggerId}
            brobyggere={brobyggere}
            appointments={appointments}
          />
        )}

        {/* ── Trin 2: Bekræft ── */}
        {step === 2 && menneske && brobygger && type && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 24, fontWeight: 500,
              color: SoS.ink, marginBottom: 20, letterSpacing: -0.2,
            }}>
              Bekræft matching
            </div>

            <div style={{
              background: '#fff', borderRadius: SoS.r.xl, padding: 24,
              border: `1px solid ${SoS.lineSoft}`, marginBottom: 16,
            }}>
              {/* Avatars */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 20 }}>
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <Avatar initials={menneske.initials} bg={type.color} size={56} />
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink, marginTop: 8 }}>
                    {menneske.firstName}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Menneske</div>
                </div>
                <Icon name="match" size={28} color={SoS.orange} />
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <Avatar
                    initials={brobygger.avatar || brobygger.initials}
                    bg={brobygger.bg}
                    size={56}
                  />
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink, marginTop: 8 }}>
                    {(brobygger.name || brobygger.navn || '').split(' ')[0]}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Brobygger</div>
                </div>
              </div>

              {/* Detaljer */}
              <div style={{ paddingTop: 18, borderTop: `1px solid ${SoS.lineSoft}` }}>
                {[
                  {
                    label: 'Tidspunkt',
                    value: `${new Date((menneske.brobygning || {}).dato || aftaleDato)
                      .toLocaleDateString('da-DK', { day: 'numeric', month: 'short' })} kl. ${
                      (menneske.brobygning || {}).start || aftaleStart || '—'
                    }`,
                  },
                  {
                    label: 'Varighed',
                    value: DURATIONS.find(d =>
                      d.v === ((menneske.brobygning || {}).duration || aftaleDuration)
                    )?.label || '—',
                  },
                  ...((menneske.brobygning || {}).frekvens ? [{
                    label: 'Frekvens',
                    value: menneske.brobygning.frekvens,
                  }] : []),
                  { label: 'Mennesketype', pill: true },
                ].map(row => (
                  <div key={row.label} style={{
                    display: 'flex', justifyContent: 'space-between',
                    alignItems: 'center', marginBottom: 8,
                  }}>
                    <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
                      {row.label}
                    </span>
                    {row.pill ? (
                      <Pill variant="custom" bg={type.soft} color={type.color}>{type.label}</Pill>
                    ) : (
                      <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
                        {row.value}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Brobygger får besked */}
            <div style={{
              padding: 14, background: SoS.sageSoft, borderRadius: SoS.r.md,
              display: 'flex', gap: 10, marginBottom: 10,
            }}>
              <Icon name="sparkle" size={18} color={SoS.sage} />
              <div style={{
                flex: 1, fontFamily: SoS.sans, fontSize: 12,
                color: SoS.sage, lineHeight: 1.5, fontWeight: 600,
              }}>
                {(brobygger.name || brobygger.navn || '').split(' ')[0]} modtager en besked om aftalen.
              </div>
            </div>

            {/* Din opgave */}
            <div style={{
              padding: 14, background: SoS.orange + '12', borderRadius: SoS.r.md,
              display: 'flex', gap: 10, border: `1px solid ${SoS.orange}30`,
            }}>
              <Icon name="phone" size={18} color={SoS.orange} />
              <div style={{
                flex: 1, fontFamily: SoS.sans, fontSize: 12,
                color: SoS.orangeDeep, lineHeight: 1.6,
              }}>
                <strong>Din opgave:</strong> Ring {menneske.firstName} og bekræft aftalen.
                En påmindelse vises i din oversigt, indtil du krydser den af.
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '16px 20px 34px', background: '#fff',
        borderTop: `1px solid ${SoS.line}`, display: 'flex', gap: 10,
      }}>
        {step > 0 && (
          <button
            onClick={() => setStep(s => s - 1)}
            style={{
              flex: 1, padding: '14px 0',
              background: '#fff', color: SoS.ink,
              border: `1.5px solid ${SoS.lineSoft}`,
              borderRadius: SoS.r.md,
              fontFamily: SoS.sans, fontSize: 15, cursor: 'pointer',
            }}
          >
            Tilbage
          </button>
        )}
        <button
          disabled={!canNext}
          onClick={() => step === 2 ? handleSend() : setStep(s => s + 1)}
          style={{
            flex: 2, padding: '14px 0',
            background: canNext ? SoS.orange : SoS.lineSoft,
            color: canNext ? '#fff' : SoS.inkMuted,
            border: 'none', borderRadius: SoS.r.md,
            fontFamily: SoS.sans, fontSize: 15, fontWeight: 600,
            cursor: canNext ? 'pointer' : 'default',
            transition: 'background 0.2s',
          }}
        >
          {step === 2 ? 'Opret matching' : 'Fortsæt'}
        </button>
      </div>
    </div>
  );
};

export default MatchingFlow;

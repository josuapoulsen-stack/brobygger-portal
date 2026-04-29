/**
 * src/components/admin/IntakeFlow.jsx
 *
 * 5-trins registreringsflow til nyt menneske:
 *   0 Kilde → 1 Basisinfo → 2 Behov → 3 Brobygningsønske → 4 Samtykke
 *
 * FASE 1: gemmer til localStorage via api/index.js mock
 * FASE 2: skift USE_BACKEND=true → Mennesker.create() kalder rigtig API
 *
 * Props:
 *   onClose(newMenneske?)  — lukker flowet; sender evt. ny person til parent
 *   viewingHq              — aktivt hovedsæde (streng)
 */

import React, { useState } from 'react';
import { Icon } from '../shared';
import { SoS } from '../../styles/tokens';
import { TYPER, TYPER_LIST } from '../../constants/typer';
import { Mennesker } from '../../api';

// ─── Kildedata ────────────────────────────────────────────────────────────────
const INTAKE_KILDER = [
  {
    id: 'selv', label: 'Egen henvendelse', icon: 'user',
    desc: 'Personen tog selv kontakt',
  },
  {
    id: 'kommune', label: 'Kommunal henvisning', icon: 'users',
    desc: 'Fra sagsbehandler eller jobcenter',
    sub: [
      { id: 'sagsbehandler', label: 'Sagsbehandler' },
      { id: 'jobcenter', label: 'Jobcenter' },
      { id: 'hjemmepleje', label: 'Hjemmepleje' },
      { id: 'sundhedsforv', label: 'Sundhedsforvaltning' },
      { id: 'aeldreomraade', label: 'Ældreomsorg' },
      { id: 'psykiatri_kom', label: 'Psykiatrikoordinator' },
    ],
  },
  {
    id: 'hospital', label: 'Hospitalsudslusning', icon: 'shield',
    desc: 'Via sygehus eller sundhedsvæsen',
    sub: [
      { id: 'indlaggelse', label: 'Indlæggelse' },
      { id: 'akut', label: 'Akutmodtagelse' },
      { id: 'ambulatorium', label: 'Ambulatorium' },
      { id: 'psykiatri', label: 'Psykiatri' },
      { id: 'rehab', label: 'Rehabilitering' },
      { id: 'palliativ', label: 'Palliativt forløb' },
    ],
  },
  {
    id: 'paarørende', label: 'Familie / pårørende', icon: 'heart',
    desc: 'Henvendelse fra nærtstående',
  },
  {
    id: 'org', label: 'Anden organisation', icon: 'star',
    desc: 'NGO, frivilligcenter e.l.',
    sub: [
      { id: 'frivilligcenter', label: 'Frivilligcenter' },
      { id: 'anden_ngo', label: 'Anden NGO' },
      { id: 'kirke', label: 'Kirke / trossamfund' },
      { id: 'fagforening', label: 'Fagforening' },
      { id: 'boligforening', label: 'Boligforening' },
      { id: 'laeger', label: 'Lægepraksis' },
    ],
  },
];

// ─── Behov per brobygningstype ────────────────────────────────────────────────
const BEHOV_BY_TYPE = {
  sundhed: [
    'Hjælp til lægebesøg', 'Følge til behandling', 'Transport og ledsagelse',
    'Medicin og dosering', 'Kontakt til sundhedsvæsenet', 'Genoptræning og motion',
    'Kost og ernæring', 'Praktisk støtte i hverdagen', 'Andet',
  ],
  forening: [
    'Foreningsliv og fællesskab', 'Sport og motion', 'Sproglig støtte',
    'Kulturelle aktiviteter', 'Frivilligt arbejde', 'Netværk og socialt fællesskab',
    'Hobby og interesser', 'Integration og tilhørsforhold', 'Andet',
  ],
  social: [
    'Selskab og samtale', 'Gåture / frisk luft', 'Følgeskab og nærvær',
    'Let motion', 'Indkøb og ærinder', 'Kulturelle oplevelser',
    'Praktisk hjælp', 'Modvirke ensomhed', 'Andet',
  ],
};

// ─── Hjælpe-komponenter ───────────────────────────────────────────────────────
const FieldLabel = ({ children, note }) => (
  <div style={{
    fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
    color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8,
  }}>
    {children}
    {note && (
      <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 0, color: SoS.inkMuted }}>
        {' '}({note})
      </span>
    )}
  </div>
);

const inputStyle = {
  width: '100%', padding: '12px 14px',
  fontFamily: SoS.sans, fontSize: 15, color: SoS.ink,
  background: '#fff', border: `1.5px solid ${SoS.lineSoft}`,
  borderRadius: SoS.r.md, outline: 'none', boxSizing: 'border-box',
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const IntakeFlow = ({ onClose, viewingHq = 'Aarhus' }) => {
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [newPerson, setNewPerson] = useState(null);

  // ── Trin 0: Kilde ──────────────────────────────────────────────────────────
  const [kilde, setKilde] = useState(null);
  const [kildeDetalje, setKildeDetalje] = useState(null);

  // ── Trin 1: Basisinfo ──────────────────────────────────────────────────────
  const [form, setForm] = useState({ firstName: '', lastName: '', age: '', phone: '' });
  const setField = (k, v) => setForm(f => ({ ...f, [k]: v }));

  // ── Trin 2: Behov ──────────────────────────────────────────────────────────
  const [type, setType] = useState(null);
  const [selectedBehov, setSelectedBehov] = useState([]);
  const [udfordringer, setUdfordringer] = useState('');
  const [note, setNote] = useState('');

  // ── Trin 3: Brobygningsønske ───────────────────────────────────────────────
  const today = new Date();
  const [brobygDato, setBrobygDato] = useState(
    new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [brobygStart, setBrobygStart] = useState(null);
  const [brobygDuration, setBrobygDuration] = useState(null);
  const [brobygFrekvens, setBrobygFrekvens] = useState(null);
  const [brobygNote, setBrobygNote] = useState('');

  // ── Trin 4: Samtykke ───────────────────────────────────────────────────────
  const [consent, setConsent] = useState(false);

  // ── Validering ────────────────────────────────────────────────────────────
  const selectedKildeObj = INTAKE_KILDER.find(k => k.id === kilde);
  const kildeHasSub = !!(selectedKildeObj && selectedKildeObj.sub);
  const phoneDigits = form.phone.replace(/\D/g, '');
  const phoneOk = phoneDigits.length === 8;

  const canNext = [
    !!kilde && (!kildeHasSub || !!kildeDetalje),            // 0
    form.firstName.trim().length > 0 && form.age.trim().length > 0 && phoneOk, // 1
    !!type && selectedBehov.length > 0,                     // 2
    !!brobygDato && !!brobygStart && !!brobygDuration,      // 3
    consent,                                                 // 4
  ];

  const STEPS = ['Kilde', 'Basisinfo', 'Behov', 'Brobygningsønske', 'Samtykke'];

  const toggleBehov = (b) =>
    setSelectedBehov(prev =>
      prev.includes(b) ? prev.filter(x => x !== b) : [...prev, b]
    );

  // ── Gem ───────────────────────────────────────────────────────────────────
  const handleFinish = async () => {
    setLoading(true);
    try {
      const payload = {
        firstName: form.firstName.trim(),
        lastName: form.lastName.trim(),
        age: parseInt(form.age) || 0,
        contact: form.phone.trim(),
        type: type || 'social',
        kilde: kilde || 'andet',
        kildeDetalje: kildeDetalje || null,
        needs: selectedBehov,
        health: udfordringer.trim() || 'Ingen særlige forhold.',
        address: '', meetPoint: '', language: 'Dansk',
        activeCount: 0, completedCount: 0, cancelledCount: 0,
        notes: [],
        hq: viewingHq,
        createdAt: new Date().toISOString().split('T')[0],
        brobygning: {
          dato: brobygDato,
          start: brobygStart,
          duration: brobygDuration,
          frekvens: brobygFrekvens,
          note: brobygNote,
        },
      };

      // FASE 1: mock returnerer { ok: true, data: { id, ...payload } }
      // FASE 2: rigtig POST /mennesker
      const result = await Mennesker.create(payload);
      setNewPerson(result?.data || payload);
      setDone(true);
    } catch (err) {
      console.error('IntakeFlow handleFinish:', err);
    } finally {
      setLoading(false);
    }
  };

  // ── Done-skærm ─────────────────────────────────────────────────────────────
  if (done) return (
    <div style={{
      position: 'fixed', inset: 0, background: SoS.cream, zIndex: 300,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: 32,
    }}>
      <div style={{
        width: 72, height: 72, borderRadius: 36, background: SoS.sage,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24,
      }}>
        <Icon name="check" size={32} color="#fff" />
      </div>
      <div style={{
        fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
        color: SoS.ink, textAlign: 'center', letterSpacing: -0.3, marginBottom: 8,
      }}>
        {form.firstName} er registreret
      </div>
      <div style={{
        fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        textAlign: 'center', lineHeight: 1.6, maxWidth: 280, marginBottom: 32,
      }}>
        Oplysningerne er gemt. Du kan nu starte et match, eller vende tilbage til oversigten.
      </div>
      <button
        onClick={() => onClose(newPerson, 'matching')}
        style={{
          width: '100%', maxWidth: 280, padding: '15px 0',
          background: SoS.orange, color: '#fff', border: 'none',
          borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 15,
          fontWeight: 600, cursor: 'pointer', marginBottom: 12,
        }}
      >
        Start matching
      </button>
      <button
        onClick={() => onClose(newPerson)}
        style={{
          width: '100%', maxWidth: 280, padding: '13px 0',
          background: 'transparent', color: SoS.inkSoft,
          border: `1px solid ${SoS.lineSoft}`, borderRadius: SoS.r.md,
          fontFamily: SoS.sans, fontSize: 14, cursor: 'pointer',
        }}
      >
        Tilbage til oversigt
      </button>
    </div>
  );

  // ── Flow-skærm ──────────────────────────────────────────────────────────────
  return (
    <div style={{
      position: 'fixed', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column', zIndex: 300,
    }}>
      {/* Header */}
      <div style={{
        background: '#fff', padding: '54px 20px 16px',
        borderBottom: `1px solid ${SoS.lineSoft}`, flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <button
            onClick={() => onClose()}
            style={{
              width: 36, height: 36, borderRadius: 18, border: 'none',
              background: SoS.creamDeep, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <Icon name="x" size={16} color={SoS.ink} />
          </button>
          <div style={{
            fontFamily: SoS.font, fontSize: 20, fontWeight: 500,
            color: SoS.ink, letterSpacing: -0.2,
          }}>
            Registrer menneske
          </div>
          <button
            onClick={() => onClose()}
            style={{
              marginLeft: 'auto', background: 'none', border: 'none',
              fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
              color: SoS.inkSoft, cursor: 'pointer', padding: '6px 4px',
            }}
          >
            Annuller
          </button>
        </div>
        {/* Trin-bjælke */}
        <div style={{ display: 'flex', gap: 6 }}>
          {STEPS.map((s, i) => (
            <div key={s} style={{
              flex: i === step ? 2 : 1, height: 4, borderRadius: 2,
              background: i < step ? SoS.sage : i === step ? SoS.orange : SoS.lineSoft,
              transition: 'all 0.3s',
            }} />
          ))}
        </div>
        <div style={{
          fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted,
          marginTop: 6, letterSpacing: 0.3,
        }}>
          Trin {step + 1} af {STEPS.length} — {STEPS[step]}
        </div>
      </div>

      {/* Krop */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 20px 120px' }}>

        {/* ── TRIN 0: Kilde ── */}
        {step === 0 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Hvordan kom personen i kontakt?
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
              marginBottom: 20, lineHeight: 1.5,
            }}>
              Vi bruger dette til at forstå hvilke kanaler der virker bedst.
            </div>
            {INTAKE_KILDER.map(k => {
              const sel = kilde === k.id;
              return (
                <div key={k.id} style={{ marginBottom: 8 }}>
                  <button
                    onClick={() => { setKilde(k.id); setKildeDetalje(null); }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 14, width: '100%',
                      padding: '14px 16px', textAlign: 'left',
                      background: sel ? SoS.orange + '12' : '#fff',
                      border: `2px solid ${sel ? SoS.orange : SoS.lineSoft}`,
                      borderRadius: sel && k.sub
                        ? `${SoS.r.md}px ${SoS.r.md}px 0 0`
                        : `${SoS.r.md}px`,
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{
                      width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                      background: sel ? SoS.orange : SoS.creamDeep,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Icon name={k.icon} size={18} color={sel ? '#fff' : SoS.inkSoft} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink,
                      }}>
                        {k.label}
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                        {sel && kildeDetalje
                          ? (k.sub || []).find(s => s.id === kildeDetalje)?.label
                          : k.desc}
                      </div>
                    </div>
                    {sel && kildeDetalje
                      ? <Icon name="check" size={16} color={SoS.orange} />
                      : sel && k.sub
                        ? <Icon name="chevronD" size={14} color={SoS.orange} />
                        : sel
                          ? <Icon name="check" size={16} color={SoS.orange} />
                          : null}
                  </button>

                  {/* Underkategorier */}
                  {sel && k.sub && (
                    <div style={{
                      background: SoS.orange + '08',
                      border: `2px solid ${SoS.orange}`,
                      borderTop: 'none',
                      borderRadius: `0 0 ${SoS.r.md}px ${SoS.r.md}px`,
                      padding: '12px 14px 14px',
                    }}>
                      <div style={{
                        fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
                        color: SoS.orange, letterSpacing: 0.8, textTransform: 'uppercase',
                        marginBottom: 10,
                      }}>
                        Præcisér — hvem konkret?
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
                        {k.sub.map(s => {
                          const subSel = kildeDetalje === s.id;
                          return (
                            <button
                              key={s.id}
                              onClick={() => setKildeDetalje(subSel ? null : s.id)}
                              style={{
                                padding: '7px 13px', borderRadius: 999, cursor: 'pointer',
                                fontFamily: SoS.sans, fontSize: 13, fontWeight: subSel ? 600 : 400,
                                background: subSel ? SoS.orange : '#fff',
                                color: subSel ? '#fff' : SoS.ink,
                                border: `1.5px solid ${subSel ? SoS.orange : SoS.lineSoft}`,
                              }}
                            >
                              {s.label}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </>
        )}

        {/* ── TRIN 1: Basisinfo ── */}
        {step === 1 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Basisoplysninger
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
              marginBottom: 20, lineHeight: 1.5,
            }}>
              Fornavn, alder og telefon er påkrævet. Øvrige oplysninger er frivillige.
            </div>
            {[
              { key: 'firstName', label: 'Fornavn',   placeholder: 'f.eks. Erik',      required: true },
              { key: 'lastName',  label: 'Efternavn', placeholder: 'Valgfrit' },
              { key: 'age',       label: 'Alder',     placeholder: 'f.eks. 72',         required: true, type: 'number' },
              { key: 'phone',     label: 'Telefon',   placeholder: '12 34 56 78',       required: true, type: 'tel' },
            ].map(field => (
              <div key={field.key} style={{ marginBottom: 14 }}>
                <div style={{
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                  color: SoS.ink, marginBottom: 6,
                }}>
                  {field.label}
                  {field.required && <span style={{ color: SoS.orange }}> *</span>}
                </div>
                <input
                  type={field.type || 'text'}
                  inputMode={field.key === 'phone' ? 'tel' : field.key === 'age' ? 'numeric' : 'text'}
                  placeholder={field.placeholder}
                  value={form[field.key]}
                  onChange={e => setField(field.key, e.target.value)}
                  style={{
                    ...inputStyle,
                    borderColor: field.key === 'phone' && form.phone.length > 0 && !phoneOk
                      ? '#E05252'
                      : SoS.lineSoft,
                  }}
                />
                {field.key === 'phone' && form.phone.length > 0 && !phoneOk && (
                  <div style={{
                    fontFamily: SoS.sans, fontSize: 11, color: '#E05252', marginTop: 4,
                  }}>
                    Mobilnummer skal være præcis 8 cifre
                  </div>
                )}
              </div>
            ))}
          </>
        )}

        {/* ── TRIN 2: Behov ── */}
        {step === 2 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Behov og situation
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
              marginBottom: 18, lineHeight: 1.5,
            }}>
              Vælg brobygningstype og beskriv de behov og udfordringer du kender til.
            </div>

            {/* Brobygningstype */}
            <FieldLabel>Brobygningstype</FieldLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 22 }}>
              {TYPER_LIST.map(t => {
                const sel = type === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => { setType(t.id); setSelectedBehov([]); }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
                      background: sel ? t.soft : '#fff',
                      border: `2px solid ${sel ? t.color : SoS.lineSoft}`,
                      borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',
                    }}
                  >
                    <div style={{
                      width: 34, height: 34, borderRadius: 17, flexShrink: 0,
                      background: sel ? t.color : SoS.creamDeep,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Icon name={t.icon} size={16} color={sel ? '#fff' : SoS.inkSoft} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink,
                      }}>
                        {t.label}
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginTop: 2 }}>
                        {t.desc}
                      </div>
                    </div>
                    {sel && <Icon name="check" size={14} color={t.color} />}
                  </button>
                );
              })}
            </div>

            {/* Specifikke behov */}
            <FieldLabel note={type ? 'vælg alle der passer' : 'vælg en type ovenfor først'}>
              Specifikke behov
            </FieldLabel>
            {!type ? (
              <div style={{
                padding: '14px 16px', background: SoS.creamDeep,
                borderRadius: SoS.r.sm, marginBottom: 22,
                fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted,
              }}>
                Vælg en brobygningstype ovenfor for at se relevante behov.
              </div>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 22 }}>
                {(BEHOV_BY_TYPE[type] || []).map(b => {
                  const sel = selectedBehov.includes(b);
                  return (
                    <button
                      key={b}
                      onClick={() => toggleBehov(b)}
                      style={{
                        padding: '8px 14px',
                        fontFamily: SoS.sans, fontSize: 13, fontWeight: sel ? 600 : 400,
                        color: sel ? SoS.orange : SoS.inkSoft,
                        background: sel ? SoS.orange + '15' : '#fff',
                        border: `1.5px solid ${sel ? SoS.orange : SoS.lineSoft}`,
                        borderRadius: 999, cursor: 'pointer',
                      }}
                    >
                      {b}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Art. 9 GDPR-felt */}
            <div style={{
              border: `1.5px solid ${SoS.orange}30`,
              borderRadius: SoS.r.lg, overflow: 'hidden', marginBottom: 20,
            }}>
              <div style={{
                background: `${SoS.orange}12`,
                borderBottom: `1px solid ${SoS.orange}25`,
                padding: '10px 14px',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <Icon name="shield" size={14} color={SoS.orange} />
                <span style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 700, color: SoS.orange }}>
                  Følsomme oplysninger — GDPR art. 9
                </span>
                <span style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft, marginLeft: 4 }}>
                  Frivilligt · kun til fagligt brug
                </span>
              </div>
              <div style={{ padding: '14px 14px 14px' }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600, color: SoS.ink, marginBottom: 6 }}>
                  Faglige noter til brobygger
                </div>
                <div style={{
                  fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft,
                  marginBottom: 10, lineHeight: 1.4,
                }}>
                  Frivilligt. Bruges udelukkende til at støtte relationen — f.eks.
                  mobilitetsvanskeligheder, angst, let demens.
                </div>
                <textarea
                  placeholder="F.eks. let demens, angst, mobilitetsvanskeligheder, kronisk smerte..."
                  value={udfordringer}
                  onChange={e => setUdfordringer(e.target.value)}
                  rows={3}
                  style={{
                    width: '100%', padding: '10px 12px',
                    fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
                    background: '#fff', border: `1.5px solid ${SoS.orange}40`,
                    borderRadius: SoS.r.sm, outline: 'none', resize: 'none',
                    boxSizing: 'border-box', lineHeight: 1.5,
                  }}
                />
              </div>
            </div>

            {/* Kontekstnote */}
            <FieldLabel note="valgfrit">Kontekstnote</FieldLabel>
            <textarea
              placeholder="Anden relevant kontekst om personen eller situationen..."
              value={note}
              onChange={e => setNote(e.target.value)}
              rows={2}
              style={{ ...inputStyle, resize: 'none', lineHeight: 1.5 }}
            />
          </>
        )}

        {/* ── TRIN 3: Brobygningsønske ── */}
        {step === 3 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Brobygningsønske
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
              marginBottom: 20, lineHeight: 1.5,
            }}>
              Hvornår og hvor ofte ønsker personen brobygning?
            </div>

            {/* Dato */}
            <div style={{ marginBottom: 18 }}>
              <FieldLabel>Dato</FieldLabel>
              <input
                type="date"
                value={brobygDato}
                onChange={e => setBrobygDato(e.target.value)}
                style={inputStyle}
              />
            </div>

            {/* Starttidspunkt */}
            <div style={{ marginBottom: 18 }}>
              <FieldLabel>Starttidspunkt</FieldLabel>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'].map(s => (
                  <button
                    key={s}
                    onClick={() => setBrobygStart(s)}
                    style={{
                      padding: '8px 12px', borderRadius: SoS.r.md, cursor: 'pointer',
                      background: brobygStart === s ? SoS.orange : '#fff',
                      color: brobygStart === s ? '#fff' : SoS.ink,
                      border: `1.5px solid ${brobygStart === s ? SoS.orange : SoS.lineSoft}`,
                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Varighed */}
            <div style={{ marginBottom: 18 }}>
              <FieldLabel>Varighed</FieldLabel>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {[
                  { label: '30 min', v: 30 },
                  { label: '1 time', v: 60 },
                  { label: '1½ time', v: 90 },
                  { label: '2 timer', v: 120 },
                ].map(d => (
                  <button
                    key={d.v}
                    onClick={() => setBrobygDuration(d.v)}
                    style={{
                      padding: '8px 14px', borderRadius: SoS.r.md, cursor: 'pointer',
                      flex: 1, minWidth: 80,
                      background: brobygDuration === d.v ? SoS.orange : '#fff',
                      color: brobygDuration === d.v ? '#fff' : SoS.ink,
                      border: `1.5px solid ${brobygDuration === d.v ? SoS.orange : SoS.lineSoft}`,
                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    }}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Frekvens */}
            <div style={{ marginBottom: 18 }}>
              <FieldLabel note="valgfrit">Frekvens</FieldLabel>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {['Éngangs', 'Ugentlig', 'Hver 2. uge', 'Månedlig'].map(f => (
                  <button
                    key={f}
                    onClick={() => setBrobygFrekvens(prev => prev === f ? null : f)}
                    style={{
                      padding: '8px 14px', borderRadius: 999, cursor: 'pointer',
                      background: brobygFrekvens === f ? SoS.orange : '#fff',
                      color: brobygFrekvens === f ? '#fff' : SoS.ink,
                      border: `1.5px solid ${brobygFrekvens === f ? SoS.orange : SoS.lineSoft}`,
                      fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            {/* Notat */}
            <div style={{ marginBottom: 18 }}>
              <FieldLabel note="valgfrit">Notat</FieldLabel>
              <textarea
                value={brobygNote}
                onChange={e => setBrobygNote(e.target.value)}
                rows={2}
                placeholder="F.eks. foretrækker formiddage..."
                style={{ ...inputStyle, resize: 'none', lineHeight: 1.5 }}
              />
            </div>
          </>
        )}

        {/* ── TRIN 4: Samtykke + opsummering ── */}
        {step === 4 && (
          <>
            <div style={{
              fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
              color: SoS.ink, marginBottom: 6, letterSpacing: -0.2,
            }}>
              Bekræft og gem
            </div>
            <div style={{
              fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
              marginBottom: 16, lineHeight: 1.5,
            }}>
              Gennemgå oplysningerne inden du gemmer.
            </div>

            {/* Opsummerings-kort */}
            <div style={{
              background: '#fff', borderRadius: SoS.r.lg,
              border: `1px solid ${SoS.lineSoft}`, marginBottom: 16, overflow: 'hidden',
            }}>
              {/* Person-header */}
              <div style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '14px 16px', borderBottom: `1px solid ${SoS.lineSoft}`,
              }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 24, background: SoS.orange,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                }}>
                  <span style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 700, color: '#fff' }}>
                    {(form.firstName[0] || '?').toUpperCase()}
                    {(form.lastName[0] || '').toUpperCase()}
                  </span>
                </div>
                <div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 16, fontWeight: 600, color: SoS.ink }}>
                    {form.firstName} {form.lastName}
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>
                    {form.age} år{form.phone ? ` · ${form.phone}` : ''}
                  </div>
                </div>
              </div>

              {/* Opsummerings-rækker */}
              {[
                {
                  label: 'Kilde',
                  value: (() => {
                    const ko = INTAKE_KILDER.find(k => k.id === kilde);
                    if (!ko) return '—';
                    const sub = kildeDetalje ? (ko.sub || []).find(s => s.id === kildeDetalje) : null;
                    return sub ? `${ko.label} · ${sub.label}` : ko.label;
                  })(),
                },
                { label: 'Type', value: (TYPER[type] || {}).label || '—' },
                { label: 'Behov', value: selectedBehov.join(', ') || '—' },
                {
                  label: 'Ønsket dato',
                  value: brobygDato
                    ? new Date(brobygDato).toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' })
                    : '—',
                },
                {
                  label: 'Tidspunkt',
                  value: brobygStart
                    ? `kl. ${brobygStart}${brobygDuration
                        ? `, ${[{ v: 30, l: '30 min' }, { v: 60, l: '1 time' }, { v: 90, l: '1½ time' }, { v: 120, l: '2 timer' }]
                            .find(d => d.v === brobygDuration)?.l || ''}`
                        : ''}`
                    : '—',
                },
                ...(udfordringer ? [{ label: 'Udfordringer', value: udfordringer, sensitive: true }] : []),
                ...(note ? [{ label: 'Note', value: note }] : []),
              ].map(row => (
                <div
                  key={row.label}
                  style={{
                    display: 'flex', gap: 10, padding: '10px 16px',
                    borderBottom: `1px solid ${SoS.lineSoft}`,
                    background: row.sensitive ? '#FFF8F0' : 'transparent',
                  }}
                >
                  <div style={{
                    fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
                    color: row.sensitive ? SoS.orange : SoS.inkMuted,
                    minWidth: 100, paddingTop: 1,
                  }}>
                    {row.label}{row.sensitive ? ' 🔒' : ''}
                  </div>
                  <div style={{
                    fontFamily: SoS.sans, fontSize: 13, color: SoS.ink,
                    lineHeight: 1.5, flex: 1,
                  }}>
                    {row.value}
                  </div>
                </div>
              ))}
              <div style={{ padding: '10px 16px' }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
                  Registreret af dig ·{' '}
                  {new Date().toLocaleDateString('da-DK', { day: 'numeric', month: 'long', year: 'numeric' })}
                </div>
              </div>
            </div>

            {/* GDPR-advarsel ved følsomme data */}
            {udfordringer && (
              <div style={{
                background: '#FFF8F0', border: `1.5px solid ${SoS.orange}40`,
                borderRadius: SoS.r.md, padding: '12px 14px', marginBottom: 12,
              }}>
                <div style={{
                  fontFamily: SoS.sans, fontSize: 12, fontWeight: 700,
                  color: SoS.orange, marginBottom: 4,
                }}>
                  OBS: Du har registreret følsomme helbredsoplysninger
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
                  GDPR art. 9 kræver eksplicit samtykke til behandling af helbredsoplysninger.
                  Sørg for at dette er dokumenteret inden du gemmer.
                </div>
              </div>
            )}

            {/* Samtykke-boks */}
            <button
              onClick={() => setConsent(c => !c)}
              style={{
                display: 'flex', gap: 14, alignItems: 'flex-start', width: '100%',
                padding: '14px 16px',
                background: consent ? SoS.sage + '15' : '#fff',
                border: `2px solid ${consent ? SoS.sage : SoS.lineSoft}`,
                borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',
              }}
            >
              <div style={{
                width: 22, height: 22, borderRadius: 6, flexShrink: 0, marginTop: 1,
                background: consent ? SoS.sage : '#fff',
                border: `2px solid ${consent ? SoS.sage : SoS.lineSoft}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {consent && <Icon name="check" size={12} color="#fff" />}
              </div>
              <div>
                <div style={{
                  fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink, marginBottom: 4,
                }}>
                  Samtykke er indhentet og dokumenteret
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
                  Personen er informeret om formålet med registreringen, hvem der har adgang til
                  oplysningerne, og at de til enhver tid kan trække samtykket tilbage.
                  {udfordringer && ' Særskilt samtykke til helbredsoplysninger er dokumenteret.'}
                </div>
              </div>
            </button>
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        padding: '12px 20px 34px',
        background: 'linear-gradient(to top, #fff 60%, transparent)',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', gap: 10 }}>
          {step > 0 && (
            <button
              onClick={() => setStep(s => s - 1)}
              style={{
                flex: 1, padding: '14px 0',
                background: '#fff', color: SoS.ink,
                border: `1.5px solid ${SoS.lineSoft}`, borderRadius: SoS.r.md,
                fontFamily: SoS.sans, fontSize: 15, cursor: 'pointer',
              }}
            >
              Tilbage
            </button>
          )}
          {step < STEPS.length - 1 ? (
            <button
              disabled={!canNext[step]}
              onClick={() => setStep(s => s + 1)}
              style={{
                flex: 2, padding: '14px 0',
                background: canNext[step] ? SoS.orange : SoS.lineSoft,
                color: canNext[step] ? '#fff' : SoS.inkMuted,
                border: 'none', borderRadius: SoS.r.md,
                fontFamily: SoS.sans, fontSize: 15, fontWeight: 600,
                cursor: canNext[step] ? 'pointer' : 'default',
                transition: 'background 0.2s',
              }}
            >
              Næste
            </button>
          ) : (
            <button
              disabled={!consent || loading}
              onClick={handleFinish}
              style={{
                flex: 2, padding: '14px 0',
                background: consent && !loading ? SoS.sage : SoS.lineSoft,
                color: consent && !loading ? '#fff' : SoS.inkMuted,
                border: 'none', borderRadius: SoS.r.md,
                fontFamily: SoS.sans, fontSize: 15, fontWeight: 600,
                cursor: consent && !loading ? 'pointer' : 'default',
                transition: 'background 0.2s',
              }}
            >
              {loading ? 'Gemmer…' : 'Gem og opret'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntakeFlow;

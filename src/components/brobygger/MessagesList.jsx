/**
 * src/components/brobygger/MessagesList.jsx
 *
 * To-fane komponent: Notifikationer + Beskeder (tråd-liste)
 * FASE 1: mock-data fra api/index.js (USE_BACKEND=false)
 * FASE 2: SignalR via useSignalR + Beskeder.getTraade()
 *
 * Props:
 *   notifications  — [ { id, type, title, body, time, unread } ]
 *   threads        — [ { id, withName, withRole, avatar, bg, last, time, unread, online?, urgent?, official? } ]
 *   role           — 'brobygger' | 'raadgiver' | 'admin'
 *   ownHq          — streng (HQ-navn)
 *   onOpenThread(threadId)
 *   onNavigate(tab)
 *   onCompose()    — åbner ComposeMessage (kun koordinator/admin)
 */

import React, { useState } from 'react';
import { Avatar, Icon } from '../shared';
import { SoS } from '../../styles/tokens';

// ─── Ikon + farve pr. notifikationstype ──────────────────────────────────────
const NOTIF_ICON  = { match: 'match', reminder: 'clock', message: 'bell' };
const NOTIF_COLOR = { match: SoS.orange, reminder: SoS.sage, message: SoS.sky };

// ─── Compose-modal (koordinator/admin sender til brobyggere) ─────────────────
const ComposeMessage = ({ role, ownHq, onClose }) => {
  const isAdmin = role === 'admin';
  const [scope, setScope] = useState('aktive');
  const [body, setBody] = useState('');
  const [urgent, setUrgent] = useState(false);
  const [templateId, setTemplateId] = useState(null);
  const [sent, setSent] = useState(false);

  const SCOPES = [
    { id: 'een',    label: 'Én brobygger',  sub: 'Vælg fra liste (FASE 2)' },
    { id: 'aktive', label: 'Alle aktive',    sub: 'Ekskl. pause' },
    { id: 'alle',   label: 'Inkl. pause',    sub: `Alle i ${ownHq || 'HQ'}` },
    ...(isAdmin ? [{ id: 'alle-hq', label: "Alle HQ'er", sub: 'Tværgående fællesbesked' }] : []),
  ];

  const TEMPLATES = [
    { id: 'noter', emoji: '📋', label: 'Husk at notere',
      text: 'Husk at udfylde en registrering efter din næste aftale. Det tager 2 minutter og er vigtigt for vores dokumentation.' },
    { id: 'afbud', emoji: '📞', label: 'Meld afbud i tid',
      text: 'Husk altid at melde afbud til din koordinator senest 24 timer før en planlagt aftale.' },
    { id: 'info',  emoji: '📅', label: 'Infomøde',
      text: 'Vi holder infomøde for brobyggere snart. Dato og program følger — sæt allerede et kryds i kalenderen!' },
    { id: 'ros',   emoji: '⭐', label: 'Tak og ros',
      text: 'Tak for din fantastiske indsats som brobygger. Det arbejde du gør gør en reel forskel!' },
    { id: 'husk',  emoji: '🔔', label: 'Husk arrangement',
      text: 'Husk vores fælles arrangement. Meld tilbage til din koordinator om du kommer.' },
  ];

  const canSend = body.trim().length > 2;

  if (sent) return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 300,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div style={{ background: '#fff', borderRadius: SoS.r.xl, padding: 32, textAlign: 'center', width: '100%', maxWidth: 380 }}>
        <div style={{
          width: 64, height: 64, borderRadius: 32, background: SoS.sageSoft,
          display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
        }}>
          <Icon name="check" size={28} color={SoS.sage} />
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500, color: SoS.ink, marginBottom: 8 }}>
          Besked sendt
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.5, marginBottom: 20 }}>
          {urgent && 'Markeret som vigtig · '}Sendt til {scope === 'alle-hq' ? "alle HQ'er" : scope === 'aktive' ? 'alle aktive brobyggere' : 'brobyggere'}
        </div>
        <button
          onClick={onClose}
          style={{
            width: '100%', padding: '13px 0', background: SoS.orange, color: '#fff',
            border: 'none', borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 15,
            fontWeight: 600, cursor: 'pointer',
          }}
        >
          Luk
        </button>
      </div>
    </div>
  );

  return (
    <div style={{
      position: 'fixed', inset: 0, background: SoS.cream,
      display: 'flex', flexDirection: 'column', zIndex: 200,
    }}>
      {/* Header */}
      <div style={{
        padding: '54px 16px 12px', background: '#fff',
        borderBottom: `1px solid ${SoS.line}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.inkSoft, cursor: 'pointer' }}
        >
          Annuller
        </button>
        <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500, color: SoS.ink }}>Ny besked</div>
        <button
          onClick={() => setSent(true)}
          disabled={!canSend}
          style={{
            padding: '8px 16px', background: canSend ? SoS.orange : SoS.lineSoft,
            color: canSend ? '#fff' : SoS.inkMuted, border: 'none', borderRadius: 999,
            fontFamily: SoS.sans, fontSize: 13, fontWeight: 600,
            cursor: canSend ? 'pointer' : 'default',
          }}
        >
          Send
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 20px' }}>
        {/* Scope */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Send til
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {SCOPES.map(s => (
              <button
                key={s.id}
                onClick={() => setScope(s.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px',
                  background: scope === s.id ? SoS.orange + '12' : '#fff',
                  border: `2px solid ${scope === s.id ? SoS.orange : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',
                }}
              >
                <div style={{ width: 10, height: 10, borderRadius: 5, flexShrink: 0, background: scope === s.id ? SoS.orange : SoS.lineSoft }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>{s.label}</div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>{s.sub}</div>
                </div>
                {scope === s.id && <Icon name="check" size={16} color={SoS.orange} />}
              </button>
            ))}
          </div>
        </div>

        {/* Urgent toggle */}
        <div
          onClick={() => setUrgent(u => !u)}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '12px 14px', marginBottom: 16, cursor: 'pointer',
            background: urgent ? SoS.orange + '12' : '#fff',
            border: `1.5px solid ${urgent ? SoS.orange : SoS.lineSoft}`,
            borderRadius: SoS.r.md,
          }}
        >
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <Icon name="bell" size={16} color={urgent ? SoS.orange : SoS.inkMuted} />
            <div>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: urgent ? SoS.orange : SoS.ink }}>Vigtig besked</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkSoft }}>Vises med orange markering i indbakken</div>
            </div>
          </div>
          <div style={{ width: 32, height: 18, borderRadius: 9, background: urgent ? SoS.orange : SoS.lineSoft, position: 'relative', transition: 'background 0.2s', flexShrink: 0 }}>
            <div style={{ position: 'absolute', top: 2, left: urgent ? 14 : 2, width: 14, height: 14, borderRadius: 7, background: '#fff', transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,0.2)' }} />
          </div>
        </div>

        {/* Skabeloner */}
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Hurtig skabelon
          </div>
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }}>
            {TEMPLATES.map(t => (
              <button
                key={t.id}
                onClick={() => { setTemplateId(t.id); setBody(t.text); }}
                style={{
                  flexShrink: 0, padding: '8px 12px',
                  background: templateId === t.id ? SoS.orange : '#fff',
                  color: templateId === t.id ? '#fff' : SoS.ink,
                  border: `1.5px solid ${templateId === t.id ? SoS.orange : SoS.lineSoft}`,
                  borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 12,
                  fontWeight: 500, cursor: 'pointer', whiteSpace: 'nowrap',
                }}
              >
                {t.emoji} {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Besked */}
        <div style={{ marginBottom: 6 }}>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8 }}>
            Besked
          </div>
          <textarea
            value={body}
            onChange={e => { setBody(e.target.value); setTemplateId(null); }}
            placeholder="Skriv din besked her…"
            rows={5}
            style={{
              width: '100%', padding: 14, borderRadius: SoS.r.md,
              background: '#fff', border: `1.5px solid ${SoS.lineSoft}`,
              fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
              lineHeight: 1.5, resize: 'none', outline: 'none', boxSizing: 'border-box',
            }}
          />
          <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, textAlign: 'right', marginTop: 4 }}>
            {body.length} tegn
          </div>
        </div>

        {scope !== 'een' && (
          <div style={{ padding: 12, background: SoS.creamDeep, borderRadius: SoS.r.md, display: 'flex', gap: 8 }}>
            <Icon name="lock" size={14} color={SoS.orangeDeep} />
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, lineHeight: 1.5 }}>
              Fællesbeskeder er read-only for modtagerne — brobyggere kan ikke svare.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// Hoved-komponent
// ═══════════════════════════════════════════════════════════════════════════════
export const MessagesList = ({
  notifications = [],
  threads = [],
  role = 'brobygger',
  ownHq = '',
  onOpenThread,
  onNavigate,
  onCompose,
}) => {
  const [tab, setTab] = useState('notifikationer');
  const [dismissed, setDismissed] = useState(new Set());
  const [accepted,  setAccepted]  = useState(new Set());
  const [expanded,  setExpanded]  = useState(null);
  const [composing, setComposing] = useState(false);

  const unreadNotif = notifications.filter(n => n.unread && !dismissed.has(n.id)).length;
  const unreadMsg   = threads.filter(t => t.unread > 0).length;

  // Brobyggere ser kun tråde FRA koordinatorer/SoS; koordinatorer ser tråde fra brobyggere
  const visibleThreads = role === 'brobygger'
    ? threads.filter(t => !t.fromBrobygger)
    : threads.filter(t => t.fromBrobygger || t.official);

  if (composing) return (
    <ComposeMessage
      role={role}
      ownHq={ownHq}
      onClose={() => setComposing(false)}
    />
  );

  return (
    <div style={{ position: 'absolute', inset: 0, background: SoS.cream, display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '54px 16px 0', background: '#fff', borderBottom: `1px solid ${SoS.line}`, flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ fontFamily: SoS.font, fontSize: 26, fontWeight: 500, color: SoS.ink }}>Beskeder</div>
          {role !== 'brobygger' && (
            <button
              onClick={() => { setComposing(true); if (onCompose) onCompose(); }}
              style={{
                width: 40, height: 40, borderRadius: 20, background: SoS.orange, border: 'none',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: SoS.shadow.glow,
              }}
            >
              <Icon name="plus" size={20} color="#fff" />
            </button>
          )}
        </div>

        {/* Faner */}
        <div style={{ display: 'flex' }}>
          {[
            { id: 'notifikationer', label: 'Notifikationer', badge: unreadNotif },
            { id: 'beskeder',       label: 'Beskeder',       badge: unreadMsg },
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setTab(f.id)}
              style={{
                flex: 1, padding: '10px 0 12px', background: 'none', border: 'none',
                borderBottom: `2.5px solid ${tab === f.id ? SoS.orange : 'transparent'}`,
                fontFamily: SoS.sans, fontSize: 14,
                fontWeight: tab === f.id ? 700 : 400,
                color: tab === f.id ? SoS.orange : SoS.inkSoft,
                cursor: 'pointer',
              }}
            >
              {f.label}
              {f.badge > 0 && (
                <span style={{
                  marginLeft: 6, background: SoS.orange, color: '#fff',
                  fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
                  borderRadius: 999, padding: '1px 6px',
                }}>
                  {f.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Scrollbar indhold */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 90 }}>

        {/* ── NOTIFIKATIONER ── */}
        {tab === 'notifikationer' && (
          <div style={{ padding: '8px 16px 16px' }}>
            {notifications.length === 0 && (
              <div style={{ padding: 48, textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen notifikationer
              </div>
            )}
            {notifications.map(n => {
              const isDismissed = dismissed.has(n.id);
              const isExpanded  = expanded === n.id;
              const isUnread    = n.unread && !isDismissed;
              const iconColor   = NOTIF_COLOR[n.type] || SoS.orange;
              const iconName    = NOTIF_ICON[n.type]  || 'bell';

              return (
                <div
                  key={n.id}
                  onClick={n.type === 'reminder' && onNavigate ? () => onNavigate('kalender') : undefined}
                  style={{
                    marginBottom: 8, background: isUnread ? '#fff' : 'transparent',
                    borderRadius: SoS.r.lg,
                    boxShadow: isUnread ? SoS.shadow.sm : 'none',
                    border: `1px solid ${isUnread ? SoS.lineSoft : 'transparent'}`,
                    overflow: 'hidden',
                    cursor: n.type === 'reminder' ? 'pointer' : 'default',
                  }}
                >
                  <div style={{ display: 'flex', gap: 12, padding: '14px 16px', alignItems: 'flex-start' }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                      background: iconColor + '18',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <Icon name={iconName} size={20} color={iconColor} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 2 }}>
                        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: isUnread ? 700 : 500, color: SoS.ink }}>
                          {n.title}
                        </div>
                        <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, flexShrink: 0, marginLeft: 8 }}>
                          {n.time}
                        </div>
                      </div>
                      <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft, lineHeight: 1.4 }}>
                        {n.body}
                      </div>

                      {/* Match-knapper */}
                      {n.type === 'match' && !isDismissed && (
                        <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                          <button
                            onClick={e => { e.stopPropagation(); setExpanded(isExpanded ? null : n.id); }}
                            style={{
                              flex: 1, padding: '8px 0', background: SoS.orange, color: '#fff',
                              border: 'none', borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13,
                              fontWeight: 600, cursor: 'pointer',
                            }}
                          >
                            {isExpanded ? 'Skjul aftale' : 'Se aftale'}
                          </button>
                          <button
                            onClick={e => { e.stopPropagation(); setDismissed(prev => new Set([...prev, n.id])); setExpanded(null); }}
                            style={{
                              flex: 1, padding: '8px 0', background: SoS.creamDeep, color: SoS.ink,
                              border: 'none', borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, cursor: 'pointer',
                            }}
                          >
                            Afvis
                          </button>
                        </div>
                      )}

                      {isDismissed && (
                        <div style={{
                          fontFamily: SoS.sans, fontSize: 11, marginTop: 6,
                          color: accepted.has(n.id) ? SoS.sage : SoS.inkMuted,
                          fontWeight: accepted.has(n.id) ? 600 : 400,
                        }}>
                          {accepted.has(n.id) ? 'Accepteret ✓' : 'Afvist'}
                        </div>
                      )}
                    </div>
                    {isUnread && <div style={{ width: 8, height: 8, borderRadius: 4, background: SoS.orange, flexShrink: 0, marginTop: 6 }} />}
                  </div>

                  {/* Udvidet aftaledetalje */}
                  {isExpanded && n.appt && (
                    <div style={{
                      margin: '0 14px 14px', background: SoS.cream, borderRadius: SoS.r.md,
                      padding: '12px 14px', border: `1px solid ${SoS.lineSoft}`,
                    }}>
                      <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, color: SoS.inkSoft, letterSpacing: 0.6, textTransform: 'uppercase', marginBottom: 8 }}>
                        Foreslået aftale
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {[
                          { icon: 'calendar', text: n.appt.date ? new Date(n.appt.date).toLocaleDateString('da-DK', { weekday: 'long', day: 'numeric', month: 'long' }) + ' kl. ' + n.appt.start : '' },
                          { icon: 'clock',    text: n.appt.end ? `Slutter ca. ${n.appt.end}` : '' },
                          { icon: 'pin',      text: n.appt.location },
                          { icon: 'heart',    text: n.appt.activity },
                        ].filter(r => r.text).map((r, i) => (
                          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Icon name={r.icon} size={14} color={SoS.inkMuted} />
                            <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.ink }}>{r.text}</span>
                          </div>
                        ))}
                      </div>
                      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                          onClick={() => { setExpanded(null); setAccepted(prev => new Set([...prev, n.id])); setDismissed(prev => new Set([...prev, n.id])); }}
                          style={{ flex: 1, padding: '9px 0', background: SoS.sage, color: '#fff', border: 'none', borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
                        >
                          Acceptér
                        </button>
                        <button
                          onClick={() => { setExpanded(null); setDismissed(prev => new Set([...prev, n.id])); }}
                          style={{ flex: 1, padding: '9px 0', background: SoS.creamDeep, color: SoS.ink, border: 'none', borderRadius: SoS.r.sm, fontFamily: SoS.sans, fontSize: 13, cursor: 'pointer' }}
                        >
                          Afslå
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* ── BESKEDER ── */}
        {tab === 'beskeder' && (
          <div style={{ padding: '8px 12px' }}>
            {visibleThreads.length === 0 && (
              <div style={{ padding: 48, textAlign: 'center', fontFamily: SoS.sans, fontSize: 13, color: SoS.inkMuted }}>
                Ingen beskeder endnu
              </div>
            )}
            {visibleThreads.map(t => (
              <button
                key={t.id}
                onClick={() => onOpenThread && onOpenThread(t.id)}
                style={{
                  display: 'flex', gap: 12, width: '100%', padding: 14,
                  background: t.unread ? '#fff' : 'transparent',
                  border: 'none', borderRadius: SoS.r.lg, cursor: 'pointer', textAlign: 'left',
                  marginBottom: 4, boxShadow: t.unread ? SoS.shadow.sm : 'none',
                  alignItems: 'center', position: 'relative',
                }}
              >
                {t.urgent && (
                  <div style={{ position: 'absolute', top: 10, left: 10, width: 6, height: 6, borderRadius: 3, background: SoS.orange }} />
                )}
                {/* Avatar + online/official badge */}
                <div style={{ position: 'relative', flexShrink: 0 }}>
                  <Avatar initials={t.avatar} bg={t.bg} size={48} />
                  {t.online && (
                    <div style={{ position: 'absolute', bottom: 0, right: 0, width: 12, height: 12, borderRadius: 6, background: SoS.sage, border: '2px solid #fff' }} />
                  )}
                  {t.official && (
                    <div style={{ position: 'absolute', bottom: -2, right: -2, width: 18, height: 18, borderRadius: 9, background: SoS.orange, border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon name="shield" size={10} color="#fff" />
                    </div>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: t.unread ? 700 : 600, color: SoS.ink }}>
                      {t.withName}
                    </div>
                    <div style={{ fontFamily: SoS.sans, fontSize: 11, color: t.unread ? SoS.orange : SoS.inkMuted, fontWeight: t.unread ? 600 : 400 }}>
                      {t.time}
                    </div>
                  </div>
                  <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
                    {t.withRole}
                    {t.coordinatorReplied && <span style={{ marginLeft: 6, color: SoS.sage, fontWeight: 600 }}>· Besvaret ✓</span>}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4, gap: 8 }}>
                    <div style={{ fontFamily: SoS.sans, fontSize: 13, color: t.unread ? SoS.ink : SoS.inkSoft, fontWeight: t.unread ? 500 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {t.proxied && '↳ '}{t.last}
                    </div>
                    {t.unread > 0 && (
                      <div style={{ minWidth: 20, height: 20, borderRadius: 10, background: SoS.orange, color: '#fff', fontFamily: SoS.sans, fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 6px' }}>
                        {t.unread}
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Lås-note under beskeder */}
      {tab === 'beskeder' && (
        <div style={{ margin: '0 16px 16px', padding: 14, background: SoS.creamDeep, borderRadius: SoS.r.md, display: 'flex', gap: 10, flexShrink: 0 }}>
          <Icon name="lock" size={16} color={SoS.orangeDeep} />
          <div style={{ flex: 1, fontFamily: SoS.sans, fontSize: 11, color: SoS.orangeDeep, lineHeight: 1.5 }}>
            Al kommunikation til borgere sker via koordinator.
          </div>
        </div>
      )}
    </div>
  );
};

export default MessagesList;

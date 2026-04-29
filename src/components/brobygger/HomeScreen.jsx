/**
 * src/components/brobygger/HomeScreen.jsx
 *
 * Brobyggerens startskærm — migreret fra prototype HomeScreen.
 *
 * FASE 1: Data fra props (localStorage via BrobyggerApp → api/index.js).
 * FASE 2: Data fetches her via useApi() + Aftaler.list() + Mennesker.list().
 *
 * Props:
 *   user         — { id, firstName, avatar, avatarBg, hq }
 *   appointments — Array<Aftale>  — sorteret stigende på dato
 *   mennesker    — Record<id, Menneske>  — opslag-map
 *   onOpenAppt   — (id: string) => void
 *   onNavigate   — (screen: string) => void
 *   variant      — "busy" | "new"  (default: "busy")
 */

import React from 'react';
import { SoS }         from '../../styles/tokens';
import { Icon, SSLogo, TopBar, SectionHead, Avatar, Pill, Button } from '../shared';
import { TYPER, DAGENS_DAG } from '../../constants/typer';
import { formatDatoFull }    from '../../utils/dates';

// ─────────────────────────────────────────────────────────────────────────────
//  Hjælpere
// ─────────────────────────────────────────────────────────────────────────────

function isToday(isoDate) {
  return new Date(isoDate).toDateString() === new Date().toDateString();
}

function isTomorrow(isoDate) {
  const tom = new Date();
  tom.setDate(tom.getDate() + 1);
  return new Date(isoDate).toDateString() === tom.toDateString();
}

function whenLabel(isoDate) {
  if (isToday(isoDate))    return 'I dag';
  if (isTomorrow(isoDate)) return 'I morgen';
  return formatDatoFull(isoDate);
}

function calcMaanedStats(appointments, variant) {
  if (variant === 'new') {
    return [
      { value: '0',  label: 'Aftaler',   color: SoS.orange },
      { value: '0',  label: 'Mennesker', color: SoS.sage   },
      { value: '0t', label: 'Timer',     color: SoS.sky    },
    ];
  }
  const apptCount = appointments.length;
  const uniqueM   = new Set(appointments.map(a => a.menneskeId)).size;
  const mins = appointments.reduce((s, a) => {
    if (!a.start || !a.end) return s + 60;
    const [sh, sm] = a.start.split(':').map(Number);
    const [eh, em] = a.end.split(':').map(Number);
    return s + Math.max(0, (eh * 60 + em) - (sh * 60 + sm));
  }, 0);
  const timer = mins >= 60 ? Math.round(mins / 60) + 't' : mins + 'm';
  return [
    { value: String(apptCount), label: 'Aftaler',   color: SoS.orange },
    { value: String(uniqueM),   label: 'Mennesker', color: SoS.sage   },
    { value: timer,             label: 'Timer',     color: SoS.sky    },
  ];
}

function greetingText() {
  const h = new Date().getHours();
  if (h < 10) return 'Godmorgen';
  if (h < 18) return 'God eftermiddag';
  return 'God aften';
}


// ─────────────────────────────────────────────────────────────────────────────
//  Sub-komponenter
// ─────────────────────────────────────────────────────────────────────────────

function NextAppointment({ appt, menneske, onOpen }) {
  if (!appt) return null;
  const type = TYPER[menneske?.type] ?? TYPER.social;
  const when = whenLabel(appt.date);

  return (
    <div
      onClick={onOpen}
      style={{
        margin:       '0 20px 20px',
        borderRadius: 28,
        padding:      24,
        background:   `linear-gradient(145deg, ${SoS.orangeDeep} 0%, ${SoS.orange} 55%, ${SoS.orangeSoft} 130%)`,
        color:        '#fff',
        position:     'relative',
        overflow:     'hidden',
        boxShadow:    SoS.shadow.glow,
        cursor:       'pointer',
      }}
    >
      <div style={{ position: 'absolute', top: -40, right: -40, width: 160, height: 160,
        borderRadius: '50%', background: 'rgba(255,255,255,0.08)' }} />
      <div style={{ position: 'absolute', bottom: -60, right: 40, width: 120, height: 120,
        borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }} />

      <div style={{ position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <div style={{ width: 6, height: 6, borderRadius: 3, background: '#fff', opacity: 0.8 }} />
          <div style={{ fontFamily: SoS.sans, fontSize: 12, fontWeight: 600,
            letterSpacing: 1.2, textTransform: 'uppercase', opacity: 0.85 }}>
            Næste aftale
          </div>
        </div>

        <div style={{ fontFamily: SoS.font, fontSize: 34, fontWeight: 400,
          lineHeight: 1.02, letterSpacing: -0.8, marginBottom: 4 }}>
          {when}
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 34, fontWeight: 400,
          lineHeight: 1.02, letterSpacing: -0.8, marginBottom: 18, fontStyle: 'italic', opacity: 0.95 }}>
          kl. {appt.start}
        </div>

        <div style={{
          display: 'flex', alignItems: 'center', gap: 12,
          padding: '14px', borderRadius: 18,
          background: 'rgba(255,255,255,0.14)',
          backdropFilter: 'blur(10px)', WebkitBackdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.2)',
        }}>
          <Avatar
            initials={menneske?.initialer ?? menneske?.firstName?.[0] ?? '?'}
            bg="rgba(255,255,255,0.22)"
            color="#fff"
            size={46}
          />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 600, marginBottom: 2 }}>
              {menneske?.firstName ?? 'Ukendt'}{menneske?.age ? `, ${menneske.age}` : ''}
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, opacity: 0.85,
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {appt.activity} · {appt.location}
            </div>
          </div>
          <Icon name="chevron" size={20} color="#fff" />
        </div>

        <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
          <Pill bg="rgba(255,255,255,0.18)" color="#fff"
            icon={<Icon name={type.icon} size={12} color="#fff" weight={2.2} />}>
            {type.short}
          </Pill>
          <Pill bg="rgba(255,255,255,0.18)" color="#fff"
            icon={<Icon name="clock" size={12} color="#fff" weight={2.2} />}>
            {appt.start}–{appt.end}
          </Pill>
          {appt.location && (
            <Pill bg="rgba(255,255,255,0.18)" color="#fff"
              icon={<Icon name="pin" size={12} color="#fff" weight={2.2} />}>
              {appt.location.split(',')[0]}
            </Pill>
          )}
        </div>
      </div>
    </div>
  );
}


function NoAppointmentsHero({ onFindShifts }) {
  return (
    <div style={{
      margin: '0 20px 20px', borderRadius: 28, padding: '32px 24px',
      background: `linear-gradient(160deg, ${SoS.creamDeep} 0%, ${SoS.sand} 100%)`,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ position: 'absolute', top: 20, right: 20, opacity: 0.5 }}>
        <Icon name="sparkle" size={36} color={SoS.orange} weight={1.6} />
      </div>
      <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 400,
        lineHeight: 1.1, letterSpacing: -0.5, color: SoS.ink, marginBottom: 8, maxWidth: 260 }}>
        Ingen aftaler i kalenderen lige nu
      </div>
      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        lineHeight: 1.5, marginBottom: 18 }}>
        Meld dig til rådighed og vi matcher dig med et menneske der har brug for din tid.
      </div>
      <Button onClick={onFindShifts} icon={<Icon name="plus" size={18} color="#fff" weight={2.5} />}>
        Meld rådighed
      </Button>
    </div>
  );
}


function UpcomingRow({ appt, menneske, onOpen }) {
  const type = TYPER[menneske?.type] ?? TYPER.social;
  const d    = new Date(appt.date);

  return (
    <div
      onClick={onOpen}
      style={{
        display: 'flex', alignItems: 'center', gap: 14,
        padding: '12px 16px', background: '#fff',
        borderRadius: SoS.r.md, cursor: 'pointer',
        border: `1px solid ${SoS.lineSoft}`,
      }}
    >
      <div style={{
        width: 48, height: 54, borderRadius: 12,
        background: type.soft,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 10, fontWeight: 700,
          color: type.color, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: -1 }}>
          {DAGENS_DAG[d.getDay()]}
        </div>
        <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
          color: type.color, lineHeight: 1 }}>
          {d.getDate()}
        </div>
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 15, fontWeight: 600,
          color: SoS.ink, marginBottom: 2 }}>
          {menneske?.firstName ?? 'Ukendt'} · {appt.start}
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {appt.activity}
        </div>
      </div>

      {(appt.status === 'pending' || appt.status === 'afventer') && (
        <Pill variant="afventer">Afventer</Pill>
      )}
      <Icon name="chevron" size={18} color={SoS.inkMuted} />
    </div>
  );
}


function MonthChips({ data }) {
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
      gap: 10, margin: '0 20px 20px',
    }}>
      {data.map((d, i) => (
        <div key={i} style={{
          background: '#fff', borderRadius: SoS.r.md, padding: '14px 12px',
          border: `1px solid ${SoS.lineSoft}`, textAlign: 'center',
        }}>
          <div style={{ fontFamily: SoS.font, fontSize: 28, fontWeight: 500,
            color: d.color, lineHeight: 1, marginBottom: 4 }}>
            {d.value}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 500,
            color: SoS.inkSoft, letterSpacing: 0.2 }}>
            {d.label}
          </div>
        </div>
      ))}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
//  Hoved-komponent
// ─────────────────────────────────────────────────────────────────────────────

export function HomeScreen({
  user,
  appointments = [],
  mennesker    = {},
  onOpenAppt,
  onNavigate,
  variant      = 'busy',
}) {
  const next         = appointments[0];
  const rest         = appointments.slice(1, 4);
  const maanedStats  = calcMaanedStats(appointments, variant);
  const nextMenneske = next ? (mennesker[next.menneskeId] ?? null) : null;

  return (
    <>
      <TopBar
        subtitle={greetingText()}
        title={
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
            {user?.firstName ?? 'dig'}
            <SSLogo size={34} />
          </span>
        }
        trailing={
          <button
            aria-label="Notifikationer"
            onClick={() => onNavigate?.('notif')}
            style={{
              width: 44, height: 44, borderRadius: 22, background: '#fff',
              border: `1px solid ${SoS.line}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', position: 'relative', flexShrink: 0,
            }}
          >
            <Icon name="bell" size={22} color={SoS.ink} />
            <div style={{ position: 'absolute', top: 10, right: 10,
              width: 8, height: 8, borderRadius: 4,
              background: SoS.rose, border: '2px solid #fff' }} />
          </button>
        }
      />

      {next
        ? <NextAppointment appt={next} menneske={nextMenneske} onOpen={() => onOpenAppt?.(next.id)} />
        : <NoAppointmentsHero onFindShifts={() => onNavigate?.('kalender')} />
      }

      {rest.length > 0 && (
        <div style={{ padding: '0 20px', marginBottom: 22 }}>
          <SectionHead
            title="Kommende"
            action={() => onNavigate?.('kalender')}
            actionLabel="Se alle"
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {rest.map(a => (
              <UpcomingRow
                key={a.id}
                appt={a}
                menneske={mennesker[a.menneskeId] ?? null}
                onOpen={() => onOpenAppt?.(a.id)}
              />
            ))}
          </div>
        </div>
      )}

      <div style={{ padding: '0 20px', marginBottom: 10 }}>
        <SectionHead title={variant === 'new' ? 'Din rejse' : 'Denne måned'} />
      </div>
      <MonthChips data={maanedStats} />

      {variant === 'new' && (
        <div style={{ margin: '0 20px 20px', borderRadius: SoS.r.lg, padding: 18,
          background: '#fff', border: `1px solid ${SoS.lineSoft}` }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            <div style={{ width: 40, height: 40, borderRadius: 20, background: SoS.sageSoft,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Icon name="sparkle" size={20} color={SoS.sage} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.font, fontSize: 18, fontWeight: 500,
                color: SoS.ink, marginBottom: 4 }}>
                Velkommen til, {user?.firstName ?? 'dig'}
              </div>
              <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
                lineHeight: 1.5, marginBottom: 12 }}>
                Du er nu registreret. Meld dig til rådighed for at blive matchet med et menneske, der har brug for dig.
              </div>
              <Button variant="secondary" onClick={() => onNavigate?.('kalender')}>
                Kom i gang
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Acubiz-genvej */}
      <div style={{ padding: '0 20px 8px' }}>
        <button
          onClick={() => {
            const appUrl = 'acubiz://';
            const ios    = /iPhone|iPad|iPod/i.test(navigator.userAgent);
            const store  = ios
              ? 'https://apps.apple.com/dk/search?term=acubiz'
              : 'https://play.google.com/store/search?q=acubiz&c=apps';
            window.location.href = appUrl;
            setTimeout(() => { window.location.href = store; }, 1500);
          }}
          style={{
            width: '100%', display: 'flex', alignItems: 'center', gap: 12,
            padding: '11px 14px', background: '#fff',
            border: `1px solid ${SoS.lineSoft}`,
            borderRadius: SoS.r.md, cursor: 'pointer', textAlign: 'left',
          }}
        >
          <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0,
            background: '#EAF1FB',
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="note" size={18} color="#3A6DB5" weight={1.8} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 600, color: SoS.ink }}>
              Acubiz
            </div>
            <div style={{ fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted, marginTop: 1 }}>
              Kvitteringer og kørselsøkonomisk registrering
            </div>
          </div>
          <Icon name="chevron" size={14} color={SoS.inkMuted} />
        </button>
      </div>

      {/* Brobygningstyper */}
      <div style={{ padding: '0 20px 20px' }}>
        <SectionHead title="Brobygningstyper" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {Object.values(TYPER).map(t => (
            <div key={t.id} style={{
              display: 'flex', alignItems: 'center', gap: 14,
              padding: 14, background: '#fff', borderRadius: SoS.r.md,
              border: `1px solid ${SoS.lineSoft}`,
            }}>
              <div style={{ width: 40, height: 40, borderRadius: 20,
                background: t.soft,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon name={t.icon} size={20} color={t.color} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 600, color: SoS.ink }}>
                  {t.label}
                </div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft,
                  lineHeight: 1.3, marginTop: 2 }}>
                  {t.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default HomeScreen;

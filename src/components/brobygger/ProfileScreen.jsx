/**
 * src/components/brobygger/ProfileScreen.jsx
 *
 * Brobyggerens profilside — migreret fra prototype ProfileScreen.
 * Undersider: personlige oplysninger, notifikationer, privatliv & sikkerhed.
 *
 * Props:
 *   user       — { id, name, firstName, email, mobil, hq, avatar, avatarBg }
 *   onLogout   — function
 */

import React, { useState } from 'react';
import { SoS }          from '../../styles/tokens';
import { Icon, TopBar, Avatar, Button } from '../shared';
import { usePush }       from '../../hooks/usePush';
import { Profil }        from '../../api/index';

// ── Toggle-switch ─────────────────────────────────────────────────────────────
function Toggle({ on, onToggle }) {
  return (
    <button onClick={onToggle} style={{
      width: 48, height: 28, borderRadius: 14,
      background:  on ? SoS.sage : SoS.lineSoft,
      border:      'none', cursor: 'pointer',
      position:    'relative', flexShrink: 0,
      transition:  'background 0.2s',
    }}>
      <div style={{
        width: 20, height: 20, borderRadius: 10, background: '#fff',
        position:   'absolute', top: 4,
        left:       on ? 24 : 4,
        transition: 'left 0.2s',
        boxShadow:  '0 1px 3px rgba(0,0,0,0.2)',
      }} />
    </button>
  );
}

function SubToggle({ label, sublabel, on, onToggle }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14,
      padding: '14px 16px', borderBottom: `1px solid ${SoS.lineSoft}` }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>{label}</div>
        {sublabel && <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>{sublabel}</div>}
      </div>
      <Toggle on={on} onToggle={onToggle} />
    </div>
  );
}

function BackHeader({ title, onBack }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4,
      padding: '54px 16px 12px', background: '#fff',
      borderBottom: `1px solid ${SoS.line}` }}>
      <button onClick={onBack} style={{ background: 'none', border: 'none', padding: 4, cursor: 'pointer' }}>
        <Icon name="chevronL" size={22} color={SoS.ink} />
      </button>
      <div style={{ fontFamily: SoS.font, fontSize: 20, fontWeight: 500,
        color: SoS.ink, marginLeft: 4 }}>{title}</div>
    </div>
  );
}

function MenuRow({ icon, label, subtitle, onClick, danger }) {
  return (
    <button onClick={onClick} style={{
      width: '100%', display: 'flex', alignItems: 'center', gap: 14,
      padding: '14px 16px', background: 'none', border: 'none',
      borderBottom: `1px solid ${SoS.lineSoft}`, cursor: 'pointer', textAlign: 'left',
    }}>
      <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        background: danger ? SoS.roseSoft : SoS.creamDeep,
        display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon name={icon} size={18} color={danger ? SoS.rose : SoS.inkSoft} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500,
          color: danger ? SoS.rose : SoS.ink }}>{label}</div>
        {subtitle && <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkMuted, marginTop: 1 }}>{subtitle}</div>}
      </div>
      <Icon name="chevron" size={16} color={SoS.inkMuted} />
    </button>
  );
}


// ─────────────────────────────────────────────────────────────────────────────
//  Hoved-komponent
// ─────────────────────────────────────────────────────────────────────────────

export function ProfileScreen({ user, onLogout }) {
  const [subPage,  setSubPage]  = useState(null);
  const [pf,       setPf]       = useState({
    navn:  user?.name  ?? '',
    email: user?.email ?? '',
    mobil: user?.mobil ?? '',
  });
  const [pEdit,    setPEdit]    = useState(false);
  const [pSaved,   setPSaved]   = useState(false);
  const [notif,    setNotif]    = useState({
    nyeAftaler: true, pamindelser: true, beskeder: true, systemOpdateringer: false,
  });

  const { subscribed, supported, subscribe, unsubscribe } = usePush();

  const saveProfile = async () => {
    try { await Profil.update(pf); } catch (_) {}
    setPEdit(false);
    setPSaved(true);
    setTimeout(() => setPSaved(false), 2500);
  };

  const toggleNotif = (k) => setNotif(p => ({ ...p, [k]: !p[k] }));

  // ── Notifikationer-underside ──────────────────────────────────────────────
  if (subPage === 'notif') return (
    <>
      <BackHeader title="Notifikationer" onBack={() => setSubPage(null)} />
      <div style={{ padding: '16px 20px 20px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
          <SubToggle label="Nye aftaleforslag"
            sublabel="Når koordinatoren foreslår en ny brobygning"
            on={notif.nyeAftaler}          onToggle={() => toggleNotif('nyeAftaler')} />
          <SubToggle label="Påmindelser"
            sublabel="Dagen før og morgenen for en aftale"
            on={notif.pamindelser}         onToggle={() => toggleNotif('pamindelser')} />
          <SubToggle label="Nye beskeder"
            sublabel="Fra koordinator eller SoS"
            on={notif.beskeder}            onToggle={() => toggleNotif('beskeder')} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>Systemopdateringer</div>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>Portal-nyheder og vedligeholdelse</div>
            </div>
            <Toggle on={notif.systemOpdateringer} onToggle={() => toggleNotif('systemOpdateringer')} />
          </div>
        </div>

        {supported && (
          <div style={{ background: '#fff', borderRadius: SoS.r.lg,
            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: SoS.sans, fontSize: 14, fontWeight: 500, color: SoS.ink }}>Push-notifikationer</div>
                <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginTop: 2 }}>
                  {subscribed ? 'Aktiveret på denne enhed' : 'Ikke aktiveret endnu'}
                </div>
              </div>
              <Toggle on={subscribed} onToggle={subscribed ? unsubscribe : subscribe} />
            </div>
          </div>
        )}

        <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.5 }}>
          Push-notifikationer kræver at du har accepteret tilladelse i din telefon.
          Notifikationer sendes aldrig om natten (kl. 22–07).
        </div>
      </div>
    </>
  );

  // ── Personlige oplysninger ────────────────────────────────────────────────
  if (subPage === 'personlig') {
    const inputStyle = {
      width: '100%', padding: '11px 13px',
      border: `1px solid ${pEdit ? SoS.line : 'transparent'}`,
      borderRadius: SoS.r.md, fontFamily: SoS.sans, fontSize: 14, color: SoS.ink,
      background: pEdit ? '#fff' : SoS.creamDeep, outline: 'none',
      boxSizing: 'border-box', transition: 'border-color 0.2s, background 0.2s',
    };
    return (
      <>
        <BackHeader title="Personlige oplysninger" onBack={() => setSubPage(null)} />
        <div style={{ padding: '16px 20px 20px' }}>
          {/* Systemfelter */}
          <div style={{ background: '#fff', borderRadius: SoS.r.lg,
            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
            {[
              { label: 'Rolle',     value: 'Brobygger'              },
              { label: 'Hovedsæde', value: user?.hq ?? 'Ukendt'     },
              { label: 'Startdato', value: 'Registreret i portalen' },
            ].map((row, i, arr) => (
              <div key={i} style={{ padding: '13px 16px',
                borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{row.label}</span>
                <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>{row.value}</span>
              </div>
            ))}
          </div>

          <div style={{ fontFamily: SoS.sans, fontSize: 11, fontWeight: 700,
            color: SoS.inkMuted, letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 10 }}>
            Dine oplysninger
          </div>

          {[
            { label: 'Navn',  key: 'navn',  type: 'text' },
            { label: 'Email', key: 'email', type: 'email' },
            { label: 'Mobil', key: 'mobil', type: 'tel' },
          ].map(f => (
            <div key={f.key} style={{ marginBottom: 10 }}>
              <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, marginBottom: 4 }}>
                {f.label}
              </div>
              <input
                value={pf[f.key]}
                readOnly={!pEdit}
                type={f.type}
                onChange={e => setPf(p => ({ ...p, [f.key]: e.target.value }))}
                style={inputStyle}
              />
            </div>
          ))}

          {pSaved && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px',
              background: SoS.sageSoft, borderRadius: SoS.r.md, marginBottom: 12 }}>
              <Icon name="check" size={16} color={SoS.sage} weight={2.5} />
              <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.sage, fontWeight: 600 }}>Gemt!</span>
            </div>
          )}

          {pEdit ? (
            <div style={{ display: 'flex', gap: 10 }}>
              <Button full onClick={saveProfile}>Gem ændringer</Button>
              <Button variant="secondary" onClick={() => setPEdit(false)}
                style={{ flex: '0 0 auto', padding: '0 18px' }}>
                Annuller
              </Button>
            </div>
          ) : (
            <Button full variant="secondary" onClick={() => setPEdit(true)}>
              Rediger oplysninger
            </Button>
          )}
        </div>
      </>
    );
  }

  // ── Privatliv & sikkerhed ─────────────────────────────────────────────────
  if (subPage === 'privatliv') return (
    <>
      <BackHeader title="Privatliv & sikkerhed" onBack={() => setSubPage(null)} />
      <div style={{ padding: '16px 20px 20px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 16 }}>
          {[
            { label: 'Databehandlingsaftale', value: 'Underskrevet' },
            { label: 'GDPR-samtykke',         value: 'Accepteret' },
            { label: 'Kryptering',            value: 'TLS 1.3 · SSL' },
            { label: 'Sidst logget ind',       value: 'I dag' },
          ].map((row, i, arr) => (
            <div key={i} style={{ padding: '13px 16px',
              borderBottom: i < arr.length - 1 ? `1px solid ${SoS.lineSoft}` : 'none',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft }}>{row.label}</span>
              <span style={{ fontFamily: SoS.sans, fontSize: 13, fontWeight: 500, color: SoS.ink }}>{row.value}</span>
            </div>
          ))}
        </div>
        <div style={{ fontFamily: SoS.sans, fontSize: 12, color: SoS.inkSoft, lineHeight: 1.6 }}>
          Dine data behandles fortroligt i overensstemmelse med GDPR.
          Kontakt din koordinator hvis du ønsker indsigt i dine oplysninger.
        </div>
      </div>
    </>
  );

  // ── Hovedside ─────────────────────────────────────────────────────────────
  return (
    <>
      <TopBar title="Profil" subtitle="Din konto" />

      {/* Avatar-sektion */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center',
        padding: '24px 20px 20px', gap: 10 }}>
        <Avatar
          initials={user?.avatar ?? user?.firstName?.[0] ?? '?'}
          bg={user?.avatarBg ?? SoS.orange}
          color="#fff"
          size={72}
        />
        <div>
          <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
            color: SoS.ink, textAlign: 'center', letterSpacing: -0.2 }}>
            {user?.name ?? user?.firstName ?? ''}
          </div>
          <div style={{ fontFamily: SoS.sans, fontSize: 13, color: SoS.inkSoft,
            textAlign: 'center', marginTop: 2 }}>
            Brobygger · {user?.hq ?? ''}
          </div>
        </div>
      </div>

      {/* Menu-sektioner */}
      <div style={{ padding: '0 20px 8px' }}>
        <div style={{ background: '#fff', borderRadius: SoS.r.lg,
          border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden', marginBottom: 12 }}>
          <MenuRow icon="user"    label="Personlige oplysninger"
            subtitle="Navn, email, telefon"
            onClick={() => setSubPage('personlig')} />
          <MenuRow icon="bell"    label="Notifikationer"
            subtitle="Push, aftaler, påmindelser"
            onClick={() => setSubPage('notif')} />
          <MenuRow icon="shield"  label="Privatliv & sikkerhed"
            subtitle="GDPR, kryptering, sidst logget ind"
            onClick={() => setSubPage('privatliv')} />
        </div>

        {onLogout && (
          <div style={{ background: '#fff', borderRadius: SoS.r.lg,
            border: `1px solid ${SoS.lineSoft}`, overflow: 'hidden' }}>
            <MenuRow icon="x" label="Log ud" danger onClick={onLogout} />
          </div>
        )}
      </div>

      {/* Version */}
      <div style={{ padding: '16px 20px', textAlign: 'center',
        fontFamily: SoS.sans, fontSize: 11, color: SoS.inkMuted }}>
        SoS Brobygger Portal · FASE 1
      </div>
    </>
  );
}

export default ProfileScreen;

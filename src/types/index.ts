/**
 * src/types/index.ts — Komplet TypeScript datamodel for Brobygger Portal
 *
 * Alle interfaces afspejler den JavaScript-datastruktur der bruges i
 * "Brobygger portal.html" (single-file prototype).
 *
 * Eksporteres som navngivne exports (ingen default).
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Type-unions (diskriminanter / status-typer)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/** Mulige statusser for en brobygger */
export type BrobyggerStatus =
  | 'aktiv'
  | 'pause'
  | 'inaktiv';

/** Mulige statusser for et menneske i systemet */
export type MenneskeStatus =
  | 'aktiv'
  | 'venter'
  | 'afventer'
  | 'pause'
  | 'afsluttet';

/** Mulige statusser for en aftale */
export type AppointmentStatus =
  | 'confirmed'
  | 'pending'
  | 'cancelled';

/** Brobyggnings-typer (behovsområde) */
export type BrobyggningsType =
  | 'sundhed'
  | 'forening'
  | 'social';

/** Kilde til registrering af et menneske */
export type MenneskeKilde =
  | 'selv'
  | 'kommune'
  | 'hospital'
  | 'paarørende'
  | 'org'
  | 'ukendt';

/** Brugerroller i systemet */
export type UserRole =
  | 'raadgiver'
  | 'admin'
  | 'brobygger';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Enum: HovedSaede (de 9 danske regioner + kommunal variant)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * De 9 mulige hovedsæder / regioner i systemet.
 * Bruges til at filtrere brobyggere og rådgivere geografisk.
 */
export enum HovedSaede {
  Aarhus        = 'Aarhus',
  Koebenhavn    = 'København',
  Odense        = 'Odense',
  Aalborg       = 'Aalborg',
  Esbjerg       = 'Esbjerg',
  Randers       = 'Randers',
  Vejle         = 'Vejle',
  Horsens       = 'Horsens',
  Roskilde      = 'Roskilde',
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: Brobygger
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * En brobygger er en frivillig der brobygger mellem mennesker med behov
 * og fællesskaber/tilbud i lokalsamfundet.
 *
 * @example
 * const maja: Brobygger = {
 *   id: 'bb-1', name: 'Maja Holmberg', avatar: 'MH', bg: '#E87A3E',
 *   active: 4, pending: 1, status: 'aktiv', thisMonth: 6, openShifts: 1,
 *   thisWeek: 2, startDate: '2024-10-01', lastActive: '2026-04-20',
 *   pauseUntil: null, pauseNote: '', mobil: '+45 23 45 67 89',
 *   email: 'maja.holmberg@socialsundhed.org'
 * };
 */
export interface Brobygger {
  /** Unik ID, fx 'bb-1' */
  id: string;

  /** Fuldt navn */
  name: string;

  /** Initialer til avatar-visning, fx 'MH' */
  avatar: string;

  /** Baggrundsfarve for avatar (hex-farve) */
  bg: string;

  /** Antal aktive brobygninger */
  active: number;

  /** Antal brobygninger der afventer godkendelse */
  pending: number;

  /** Brobyggerens nuværende status */
  status: BrobyggerStatus;

  /** Antal brobygninger gennemført denne måned */
  thisMonth: number;

  /** Antal åbne vagter / ledige pladser */
  openShifts: number;

  /** Antal brobygninger denne uge */
  thisWeek: number;

  /** Ansættelsesdato / startdato (ISO 8601: YYYY-MM-DD) */
  startDate: string;

  /** Dato for seneste aktivitet (ISO 8601: YYYY-MM-DD) */
  lastActive: string;

  /** Dato for planlagt pause-ophør — null hvis ikke på pause */
  pauseUntil: string | null;

  /** Note om årsag til pause */
  pauseNote: string;

  /** Mobilnummer med landekode */
  mobil: string;

  /** E-mailadresse */
  email: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: HelbredsOplysninger (embedded i Menneske)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Valgfrie helbredsoplysninger tilknyttet et menneske.
 * Gemmes kun hvis relevant og samtykke er givet.
 */
export interface HelbredsOplysninger {
  /** Diagnoser / helbredsudfordringer (fritekst) */
  diagnoser?: string;

  /** Relevant medicin */
  medicin?: string;

  /** Mobilitetsbegrænsninger */
  mobilitet?: string;

  /** Andre relevante helbredsnotater */
  noter?: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: Menneske
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Et menneske er en borger der er registreret i systemet og ønsker
 * brobygning til aktiviteter og fællesskaber.
 */
export interface Menneske {
  /** Unik ID, fx 'b-1' */
  id: string;

  /** Fornavn */
  firstName: string;

  /** Efternavn */
  lastName: string;

  /** Alder i år */
  age: number;

  /** Behovstype / brobyggnings-kategori */
  type: BrobyggningsType;

  /** Aktuel status i forløbet */
  status: MenneskeStatus;

  /** Initialer til avatar-visning, fx 'MH' */
  initials: string;

  /** Bopælsadresse (fritekst) */
  address: string;

  /** Foretrukket møde-/opsamlingssted */
  meetPoint: string;

  /** Valgfrie helbredsoplysninger (kræver samtykke) */
  health?: HelbredsOplysninger;

  /** Mobilnummer — udeladt hvis mobilOptOut er true */
  mobil?: string;

  /** Har personen fravalgt SMS/mobilkontakt? */
  mobilOptOut?: boolean;

  /** Modersmål / foretrukket kommunikationssprog */
  language: string;

  /** Hvorfra/hvordan personen er blevet registreret */
  kilde: MenneskeKilde;

  /** Dato for forløbets start (ISO 8601: YYYY-MM-DD) */
  startedAt: string;

  /** Dato for registrering i systemet (ISO 8601: YYYY-MM-DD) */
  registeredAt: string;

  /** ID på tilknyttet brobygger — undefined hvis ikke matchet endnu */
  brobyggerId?: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: Appointment
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * En aftale/aktivitet mellem et menneske og dennes brobygger.
 *
 * @example
 * const aftale: Appointment = {
 *   id: 'a-1', menneskeId: 'b-1', brobyggerId: 'bb-1',
 *   date: '2026-04-24', start: '10:00', end: '11:30',
 *   activity: 'Gåtur i Risskov', location: 'Risskov strand',
 *   status: 'confirmed'
 * };
 */
export interface Appointment {
  /** Unik ID, fx 'a-1' */
  id: string;

  /** ID på det menneske aftalen er for */
  menneskeId: string;

  /** ID på den brobygger der holder aftalen */
  brobyggerId: string;

  /** Dato for aftalen (ISO 8601: YYYY-MM-DD) */
  date: string;

  /** Starttidspunkt (HH:MM) */
  start: string;

  /** Sluttidspunkt (HH:MM) */
  end: string;

  /** Aktivitetsbeskrivelse, fx 'Gåtur i Risskov' */
  activity: string;

  /** Møde-/aktivitetssted */
  location: string;

  /** Aftalestatus */
  status: AppointmentStatus;

  /** Valgfrie noter om aftalen */
  notes?: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: User (indlogget rådgiver/admin)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Den aktuelt indloggede bruger.
 * Udfyldes fra JWT-claims (Entra ID) eller mock-sessionStorage.
 */
export interface User {
  /** Unik bruger-ID (fra Entra ID object-id eller mock) */
  id: string;

  /** Fornavn */
  firstName: string;

  /** Efternavn */
  lastName: string;

  /** E-mailadresse */
  email: string;

  /** Valgfrit avatar-billede (URL eller initialer) */
  avatar?: string;

  /** Brugerens rolle i systemet */
  role: Extract<UserRole, 'raadgiver' | 'admin'>;

  /** Geografisk tilknytning (primær by/region) */
  hovedsaede: HovedSaede | string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: KontaktLog
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * En kontakt-/opfølgningsregistrering i et menneskes forløb.
 */
export interface KontaktLog {
  /** Unik ID */
  id: string;

  /** ID på det tilknyttede menneske */
  menneskeId: string;

  /** ID på brobygger eller rådgiver der registrerede kontakten */
  registreretAfId: string;

  /** Dato for kontakten (ISO 8601: YYYY-MM-DD) */
  dato: string;

  /** Type af kontakt */
  type: 'telefon' | 'møde' | 'sms' | 'email' | 'andet';

  /** Fritekst-notat */
  notat: string;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Interface: Besked (chat/beskedtråd)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * En besked i besked-systemet (brobygger ↔ rådgiver).
 */
export interface Besked {
  /** Unik ID */
  id: string;

  /** ID på afsender */
  fraId: string;

  /** ID på modtager */
  tilId: string;

  /** Beskedindhold */
  tekst: string;

  /** Tidsstempel (ISO 8601) */
  sendt: string;

  /** Er beskeden læst af modtager? */
  laest: boolean;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Hjælpe-typer til API-svar
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/** Generisk pagineret API-svar */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

/** Generisk API-fejlsvar */
export interface ApiError {
  status: number;
  message: string;
  details?: string;
}

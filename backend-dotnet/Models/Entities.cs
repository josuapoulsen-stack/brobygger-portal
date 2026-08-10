namespace BrobyggerPortal.Api.Models;

// ── Enums (spejler Python-backend'ens domæne) ────────────────────────────────
public enum MenneskeStatus { Ny, Matched, Aktiv, Afsluttet, Venteliste }
public enum BrobyggerStatus { Ny, Aktiv, Pause, Inaktiv }
public enum AftaleStatus { Planlagt, Gennemfoert, Aflyst, Udsat, Kladde, Pending, Confirmed, Afslaaet, Brudt }
public enum AftaleType { Moede, Aktivitet, Telefonopkald, Online }

// ── Mennesker (borgere/klienter) ─────────────────────────────────────────────
public class Menneske
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Navn { get; set; } = string.Empty;
    public int? Alder { get; set; }
    public string? Kon { get; set; }
    public string? Email { get; set; }
    public string? Telefon { get; set; }
    public string? TelefonNorm { get; set; }              // kanonisk telefon til genkendelse
    public string? Adresse { get; set; }
    public List<string> Typer { get; set; } = [];
    public List<string> Sprog { get; set; } = ["dansk"];
    public string? Noter { get; set; }
    public MenneskeStatus Status { get; set; } = MenneskeStatus.Ny;
    public Guid? MatchedWith { get; set; }
    public Guid? RaadgiverId { get; set; }
    public string? Hq { get; set; }
    public string? Afdeling { get; set; }
    public string? Kilde { get; set; }
    public string? Meetpoint { get; set; }
    public string? SroiMaalgruppe { get; set; }
    public List<string>? HelbredsKategorier { get; set; }
    public string? PraeferencerJson { get; set; }         // jsonb (rå JSON indtil videre)
    public int? AfslutTrivsel { get; set; }
    public string? AfslutAarsag { get; set; }
    public bool UclaFravalgt { get; set; }
    // GDPR art. 9 — krypteres server-side, gemmes ALDRIG i klartekst
    public byte[]? HelbredsnoterEnc { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? DeletedAt { get; set; }        // soft-delete
}

// ── Brobyggere (frivillige) ──────────────────────────────────────────────────
public class Brobygger
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Navn { get; set; } = string.Empty;
    public string? Email { get; set; }
    public string? Telefon { get; set; }
    public string? TelefonNorm { get; set; }
    public List<string> Typer { get; set; } = [];
    public List<string> Sprog { get; set; } = ["dansk"];
    public string? Hq { get; set; }
    public string? Afdeling { get; set; }
    public string? Kon { get; set; }
    public string? Bio { get; set; }
    public string? AvatarUrl { get; set; }
    public BrobyggerStatus Status { get; set; } = BrobyggerStatus.Ny;
    public int Active { get; set; }
    public int MaxActive { get; set; } = 3;
    public DateOnly? TilgaengeligFra { get; set; }
    public string? NaesteTid { get; set; }
    public DateOnly? Startdato { get; set; }
    public DateOnly? SenesteMoede { get; set; }
    public string? Noter { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

// ── Aftaler (møder/aktiviteter) ──────────────────────────────────────────────
public class Aftale
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid BrobyggerId { get; set; }
    public Guid MenneskeId { get; set; }
    public DateTimeOffset Dato { get; set; }
    public int Varighed { get; set; } = 60;
    public AftaleType Type { get; set; } = AftaleType.Moede;
    public string? Sted { get; set; }
    public string? Beskrivelse { get; set; }
    public AftaleStatus Status { get; set; } = AftaleStatus.Planlagt;
    public string Notes { get; set; } = string.Empty;
    // Livscyklus: efterspørgsel nu → bekræftelse kan komme dage/uger/måneder senere
    public DateTimeOffset EfterspurgtAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? BekraeftetAt { get; set; }
    // Klassificering (fra stamdata)
    public string? Aftaletype { get; set; }
    public string? Brobygningstype { get; set; }          // Social | Forening | Sundhed
    public string? Henvender { get; set; }
    public string? Modtager { get; set; }
    public string? Finansiering { get; set; }
    public string? Samarbejdspartner { get; set; }
    public string? Afdeling { get; set; }
    public string? AflystAf { get; set; }
    public string? AflysningsAarsag { get; set; }
    public string? Transportplan { get; set; }
    public string? AktivitetsTid { get; set; }
    public string? FremmoedeType { get; set; }
    public string? Gentagelse { get; set; }
    public string? AftaleForm { get; set; }
    public string? BrobyggerNote { get; set; }            // briefing til brobygger
    public string? RaadgiverOpfoelgning { get; set; }
    // brobyggerLog (udfald af afholdt aftale)
    public string? Udfald { get; set; }                   // gennemfoert | afbud | ikke-modt
    public int? VarighedMin { get; set; }
    public string? LogNote { get; set; }
    public DateTimeOffset? LoggedAt { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

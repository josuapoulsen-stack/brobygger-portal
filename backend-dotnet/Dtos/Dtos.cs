using BrobyggerPortal.Api.Models;

namespace BrobyggerPortal.Api.Dtos;

// ═══════════════════════════ MENNESKER ═══════════════════════════
// Helbredsnoter er WRITE-ONLY (GDPR art. 9): modtages ved oprettelse/opdatering,
// krypteres server-side, og returneres ALDRIG i klartekst.

public record MenneskeCreateDto
{
    public string Navn { get; init; } = string.Empty;
    public int? Alder { get; init; }
    public string? Kon { get; init; }
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public string? Adresse { get; init; }
    public List<string> Typer { get; init; } = [];
    public List<string> Sprog { get; init; } = ["dansk"];
    public string? Noter { get; init; }
    public MenneskeStatus Status { get; init; } = MenneskeStatus.Ny;
    public Guid? MatchedWith { get; init; }
    public Guid? RaadgiverId { get; init; }
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kilde { get; init; }
    public string? Meetpoint { get; init; }
    public string? SroiMaalgruppe { get; init; }
    public List<string>? HelbredsKategorier { get; init; }
    public string? Praeferencer { get; init; }        // rå JSON
    public int? AfslutTrivsel { get; init; }
    public string? AfslutAarsag { get; init; }
    public bool UclaFravalgt { get; init; }
    public string? Helbredsnoter { get; init; }       // write-only
}

public record MenneskeUpdateDto
{
    public string? Navn { get; init; }
    public int? Alder { get; init; }
    public string? Kon { get; init; }
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public string? Adresse { get; init; }
    public List<string>? Typer { get; init; }
    public List<string>? Sprog { get; init; }
    public string? Noter { get; init; }
    public MenneskeStatus? Status { get; init; }
    public Guid? MatchedWith { get; init; }
    public Guid? RaadgiverId { get; init; }
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kilde { get; init; }
    public string? Meetpoint { get; init; }
    public string? SroiMaalgruppe { get; init; }
    public List<string>? HelbredsKategorier { get; init; }
    public string? Praeferencer { get; init; }
    public int? AfslutTrivsel { get; init; }
    public string? AfslutAarsag { get; init; }
    public bool? UclaFravalgt { get; init; }
    public string? Helbredsnoter { get; init; }
}

public record MenneskeReadDto
{
    public Guid Id { get; init; }
    public string Navn { get; init; } = string.Empty;
    public int? Alder { get; init; }
    public string? Kon { get; init; }
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public string? TelefonNorm { get; init; }
    public string? Adresse { get; init; }
    public List<string> Typer { get; init; } = [];
    public List<string> Sprog { get; init; } = [];
    public string? Noter { get; init; }
    public MenneskeStatus Status { get; init; }
    public Guid? MatchedWith { get; init; }
    public Guid? RaadgiverId { get; init; }
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kilde { get; init; }
    public string? Meetpoint { get; init; }
    public string? SroiMaalgruppe { get; init; }
    public List<string>? HelbredsKategorier { get; init; }
    public string? Praeferencer { get; init; }
    public int? AfslutTrivsel { get; init; }
    public string? AfslutAarsag { get; init; }
    public bool UclaFravalgt { get; init; }
    public DateTimeOffset CreatedAt { get; init; }

    public static MenneskeReadDto From(Menneske m) => new()
    {
        Id = m.Id, Navn = m.Navn, Alder = m.Alder, Kon = m.Kon, Email = m.Email,
        Telefon = m.Telefon, TelefonNorm = m.TelefonNorm, Adresse = m.Adresse,
        Typer = m.Typer, Sprog = m.Sprog, Noter = m.Noter, Status = m.Status,
        MatchedWith = m.MatchedWith, RaadgiverId = m.RaadgiverId, Hq = m.Hq,
        Afdeling = m.Afdeling, Kilde = m.Kilde, Meetpoint = m.Meetpoint,
        SroiMaalgruppe = m.SroiMaalgruppe, HelbredsKategorier = m.HelbredsKategorier,
        Praeferencer = m.PraeferencerJson, AfslutTrivsel = m.AfslutTrivsel,
        AfslutAarsag = m.AfslutAarsag, UclaFravalgt = m.UclaFravalgt, CreatedAt = m.CreatedAt,
    };
}

// ═══════════════════════════ BROBYGGERE ═══════════════════════════

public record BrobyggerCreateDto
{
    public string Navn { get; init; } = string.Empty;
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public List<string> Typer { get; init; } = [];
    public List<string> Sprog { get; init; } = ["dansk"];
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kon { get; init; }
    public string? Bio { get; init; }
    public string? AvatarUrl { get; init; }
    public BrobyggerStatus Status { get; init; } = BrobyggerStatus.Ny;
    public int Active { get; init; }
    public int MaxActive { get; init; } = 3;
    public DateOnly? TilgaengeligFra { get; init; }
    public string? NaesteTid { get; init; }
    public DateOnly? Startdato { get; init; }
    public DateOnly? SenesteMoede { get; init; }
    public string? Noter { get; init; }
}

public record BrobyggerUpdateDto
{
    public string? Navn { get; init; }
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public List<string>? Typer { get; init; }
    public List<string>? Sprog { get; init; }
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kon { get; init; }
    public string? Bio { get; init; }
    public string? AvatarUrl { get; init; }
    public BrobyggerStatus? Status { get; init; }
    public int? Active { get; init; }
    public int? MaxActive { get; init; }
    public DateOnly? TilgaengeligFra { get; init; }
    public string? NaesteTid { get; init; }
    public DateOnly? Startdato { get; init; }
    public DateOnly? SenesteMoede { get; init; }
    public string? Noter { get; init; }
}

public record BrobyggerReadDto
{
    public Guid Id { get; init; }
    public string Navn { get; init; } = string.Empty;
    public string? Email { get; init; }
    public string? Telefon { get; init; }
    public string? TelefonNorm { get; init; }
    public List<string> Typer { get; init; } = [];
    public List<string> Sprog { get; init; } = [];
    public string? Hq { get; init; }
    public string? Afdeling { get; init; }
    public string? Kon { get; init; }
    public string? Bio { get; init; }
    public string? AvatarUrl { get; init; }
    public BrobyggerStatus Status { get; init; }
    public int Active { get; init; }
    public int MaxActive { get; init; }
    public DateOnly? TilgaengeligFra { get; init; }
    public string? NaesteTid { get; init; }
    public DateOnly? Startdato { get; init; }
    public DateOnly? SenesteMoede { get; init; }
    public string? Noter { get; init; }
    public DateTimeOffset CreatedAt { get; init; }

    public static BrobyggerReadDto From(Brobygger b) => new()
    {
        Id = b.Id, Navn = b.Navn, Email = b.Email, Telefon = b.Telefon, TelefonNorm = b.TelefonNorm,
        Typer = b.Typer, Sprog = b.Sprog, Hq = b.Hq, Afdeling = b.Afdeling, Kon = b.Kon,
        Bio = b.Bio, AvatarUrl = b.AvatarUrl, Status = b.Status, Active = b.Active, MaxActive = b.MaxActive,
        TilgaengeligFra = b.TilgaengeligFra, NaesteTid = b.NaesteTid, Startdato = b.Startdato,
        SenesteMoede = b.SenesteMoede, Noter = b.Noter, CreatedAt = b.CreatedAt,
    };
}

// ═══════════════════════════ AFTALER ═══════════════════════════

public record AftaleCreateDto
{
    public Guid BrobyggerId { get; init; }
    public Guid MenneskeId { get; init; }
    public DateTimeOffset Dato { get; init; }
    public int Varighed { get; init; } = 60;
    public AftaleType Type { get; init; } = AftaleType.Moede;
    public string? Sted { get; init; }
    public string? Beskrivelse { get; init; }
    public AftaleStatus Status { get; init; } = AftaleStatus.Planlagt;
    public string Notes { get; init; } = string.Empty;
    public DateTimeOffset? EfterspurgtAt { get; init; }   // udelades → sættes til nu
    public string? Aftaletype { get; init; }
    public string? Brobygningstype { get; init; }
    public string? Henvender { get; init; }
    public string? Modtager { get; init; }
    public string? Finansiering { get; init; }
    public string? Samarbejdspartner { get; init; }
    public string? Afdeling { get; init; }
    public string? Transportplan { get; init; }
    public string? AktivitetsTid { get; init; }
    public string? FremmoedeType { get; init; }
    public string? Gentagelse { get; init; }
    public string? AftaleForm { get; init; }
    public string? BrobyggerNote { get; init; }
    public string? RaadgiverOpfoelgning { get; init; }
}

public record AftaleStatusUpdateDto
{
    public AftaleStatus Status { get; init; }
    public string Notes { get; init; } = string.Empty;
}

public record AftaleReadDto
{
    public Guid Id { get; init; }
    public Guid BrobyggerId { get; init; }
    public Guid MenneskeId { get; init; }
    public DateTimeOffset Dato { get; init; }
    public int Varighed { get; init; }
    public AftaleType Type { get; init; }
    public string? Sted { get; init; }
    public string? Beskrivelse { get; init; }
    public AftaleStatus Status { get; init; }
    public string Notes { get; init; } = string.Empty;
    public DateTimeOffset EfterspurgtAt { get; init; }
    public DateTimeOffset? BekraeftetAt { get; init; }
    public string? Aftaletype { get; init; }
    public string? Brobygningstype { get; init; }
    public string? Henvender { get; init; }
    public string? Modtager { get; init; }
    public string? Finansiering { get; init; }
    public string? Samarbejdspartner { get; init; }
    public string? Afdeling { get; init; }
    public string? AflystAf { get; init; }
    public string? AflysningsAarsag { get; init; }
    public string? Transportplan { get; init; }
    public string? AktivitetsTid { get; init; }
    public string? FremmoedeType { get; init; }
    public string? Gentagelse { get; init; }
    public string? AftaleForm { get; init; }
    public string? BrobyggerNote { get; init; }
    public string? RaadgiverOpfoelgning { get; init; }
    public string? Udfald { get; init; }
    public int? VarighedMin { get; init; }
    public string? LogNote { get; init; }
    public DateTimeOffset? LoggedAt { get; init; }
    public DateTimeOffset CreatedAt { get; init; }

    public static AftaleReadDto From(Aftale a) => new()
    {
        Id = a.Id, BrobyggerId = a.BrobyggerId, MenneskeId = a.MenneskeId, Dato = a.Dato,
        Varighed = a.Varighed, Type = a.Type, Sted = a.Sted, Beskrivelse = a.Beskrivelse,
        Status = a.Status, Notes = a.Notes, EfterspurgtAt = a.EfterspurgtAt, BekraeftetAt = a.BekraeftetAt,
        Aftaletype = a.Aftaletype, Brobygningstype = a.Brobygningstype,
        Henvender = a.Henvender, Modtager = a.Modtager, Finansiering = a.Finansiering,
        Samarbejdspartner = a.Samarbejdspartner, Afdeling = a.Afdeling, AflystAf = a.AflystAf,
        AflysningsAarsag = a.AflysningsAarsag, Transportplan = a.Transportplan, AktivitetsTid = a.AktivitetsTid,
        FremmoedeType = a.FremmoedeType, Gentagelse = a.Gentagelse, AftaleForm = a.AftaleForm,
        BrobyggerNote = a.BrobyggerNote, RaadgiverOpfoelgning = a.RaadgiverOpfoelgning, Udfald = a.Udfald,
        VarighedMin = a.VarighedMin, LogNote = a.LogNote, LoggedAt = a.LoggedAt, CreatedAt = a.CreatedAt,
    };
}

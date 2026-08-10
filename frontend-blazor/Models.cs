namespace BrobyggerPortal.Web;

// Klientmodeller (snake_case håndteres i ApiClient via JsonNamingPolicy).

public class Menneske
{
    public Guid Id { get; set; }
    public string Navn { get; set; } = "";
    public int? Alder { get; set; }
    public string? Kon { get; set; }
    public string? Email { get; set; }
    public string? Telefon { get; set; }
    public string? Adresse { get; set; }
    public string? Hq { get; set; }
    public string? Afdeling { get; set; }
    public string? Kilde { get; set; }
    public string? SroiMaalgruppe { get; set; }
    public Guid? MatchedWith { get; set; }
    public bool UclaFravalgt { get; set; }
    public string Status { get; set; } = "";
    public DateTimeOffset CreatedAt { get; set; }
}

public class MenneskeCreate
{
    public string Navn { get; set; } = "";
    public int? Alder { get; set; }
    public string? Telefon { get; set; }
    public string? Hq { get; set; }
    public string Status { get; set; } = "ny";
}

public class Brobygger
{
    public Guid Id { get; set; }
    public string Navn { get; set; } = "";
    public string? Telefon { get; set; }
    public string? Hq { get; set; }
    public int Active { get; set; }
    public int MaxActive { get; set; }
    public string Status { get; set; } = "";
}

public class BrobyggerCreate
{
    public string Navn { get; set; } = "";
    public string? Telefon { get; set; }
    public string? Hq { get; set; }
    public int MaxActive { get; set; } = 3;
    public string Status { get; set; } = "ny";
}

public class Aftale
{
    public Guid Id { get; set; }
    public Guid BrobyggerId { get; set; }
    public Guid MenneskeId { get; set; }
    public DateTimeOffset Dato { get; set; }
    public string Type { get; set; } = "moede";
    public string Status { get; set; } = "";
    public DateTimeOffset EfterspurgtAt { get; set; }
    public DateTimeOffset? BekraeftetAt { get; set; }
}

public class AftaleCreate
{
    public Guid BrobyggerId { get; set; }
    public Guid MenneskeId { get; set; }
    public DateTimeOffset Dato { get; set; }
    public string Type { get; set; } = "moede";
    public string Status { get; set; } = "pending";
}

public class Henvendelse
{
    public Guid Id { get; set; }
    public DateTimeOffset Dato { get; set; }
    public string? Kanal { get; set; }
    public string? Resume { get; set; }
    public bool Foerstegang { get; set; }
}
public class HenvendelseCreate
{
    public string? Kanal { get; set; } = "telefon";
    public string? Resume { get; set; }
    public bool Foerstegang { get; set; }
}

public class UclaMaaling
{
    public Guid Id { get; set; }
    public string Slags { get; set; } = "";
    public int Score { get; set; }
    public DateTimeOffset Dato { get; set; }
    public string? Noter { get; set; }
}
public class UclaCreate
{
    public string Slags { get; set; } = "baseline";
    public int Score { get; set; }
    public string? Noter { get; set; }
}

public class Kontaktperson
{
    public Guid Id { get; set; }
    public string Navn { get; set; } = "";
    public string? Relation { get; set; }
    public string? Telefon { get; set; }
    public string? Email { get; set; }
}
public class KontaktpersonCreate
{
    public string Navn { get; set; } = "";
    public string? Relation { get; set; }
    public string? Telefon { get; set; }
    public string? Email { get; set; }
}

public class HelbredsnoterResp
{
    public string? Helbredsnoter { get; set; }
}

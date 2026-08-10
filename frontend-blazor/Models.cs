namespace BrobyggerPortal.Web;

// Klientmodeller (snake_case håndteres i ApiClient via JsonNamingPolicy).

public class Menneske
{
    public Guid Id { get; set; }
    public string Navn { get; set; } = "";
    public int? Alder { get; set; }
    public string? Telefon { get; set; }
    public string? Hq { get; set; }
    public string Status { get; set; } = "";
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

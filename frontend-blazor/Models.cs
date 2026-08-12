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
    public string? Brobygningstype { get; set; }
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
    public string? Beskrivelse { get; set; }
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

public class Trivselsmaaling
{
    public Guid Id { get; set; }
    public string Instrument { get; set; } = "";
    public string Slags { get; set; } = "";
    public int Score { get; set; }
    public int? Ensom { get; set; }
    public int? Faellesskab { get; set; }
    public int? Stoette { get; set; }
    public int? Hverdag { get; set; }
    public int? Velbefindende { get; set; }
    public DateTimeOffset Dato { get; set; }
    public string? Noter { get; set; }
}
public class MaalingCreate
{
    public string Instrument { get; set; } = "kombineret";
    public string Slags { get; set; } = "baseline";
    public int Score { get; set; }
    public int? Ensom { get; set; } = 3;
    public int? Faellesskab { get; set; } = 3;
    public int? Stoette { get; set; } = 3;
    public int? Hverdag { get; set; } = 3;
    public int? Velbefindende { get; set; } = 3;
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

public class UdlaegKonto
{
    public Guid Id { get; set; }
    public Guid BrobyggerId { get; set; }
    public string? RegNr { get; set; }
    public string? Iban { get; set; }
    public bool HarKontoNr { get; set; }
    public string? KontoNrMaske { get; set; }
}
public class UdlaegKontoInput
{
    public string? RegNr { get; set; }
    public string? KontoNr { get; set; }
    public string? Iban { get; set; }
}

public class MenneskeUpdate
{
    public string? Status { get; set; }
    public string? Brobygningstype { get; set; }
    public string? Telefon { get; set; }
    public string? Hq { get; set; }
    public int? Alder { get; set; }
}

public class Opkald
{
    public Guid Id { get; set; }
    public string Type { get; set; } = "";
    public string? Retning { get; set; }
    public int? VarighedSek { get; set; }
    public string? Note { get; set; }
    public DateTimeOffset Tidspunkt { get; set; }
}
public class OpkaldCreate
{
    public Guid MenneskeId { get; set; }
    public string Type { get; set; } = "samtale_menneske";
    public string? Retning { get; set; } = "ind";
    public string? Note { get; set; }
}

public class Besked
{
    public Guid Id { get; set; }
    public string Afsender { get; set; } = "";
    public string Tekst { get; set; } = "";
    public DateTimeOffset Tidspunkt { get; set; }
}
public class BeskedCreate
{
    public string? Afsender { get; set; }
    public string Tekst { get; set; } = "";
}

public class Optael
{
    public string Navn { get; set; } = "";
    public int Antal { get; set; }
}
public class StatistikData
{
    public int AntalMennesker { get; set; }
    public int AntalBrobyggere { get; set; }
    public int LedigKapacitet { get; set; }
    public int AntalMaalinger { get; set; }
    public List<Optael> MenneskerPerStatus { get; set; } = [];
    public List<Optael> AftalerPerStatus { get; set; } = [];
    public List<Optael> MenneskerPerHovedsaede { get; set; } = [];
    public double? TrivselBaselineGns { get; set; }
    public double? TrivselOpfoelgningGns { get; set; }
}

public class Skabelon
{
    public Guid Id { get; set; }
    public string Navn { get; set; } = "";
    public string Indhold { get; set; } = "";
}
public class SkabelonCreate
{
    public string Navn { get; set; } = "";
    public string Indhold { get; set; } = "";
}

public class GdprRapport
{
    public Menneske Menneske { get; set; } = new();
    public string? Helbredsnoter { get; set; }
    public List<Henvendelse> Henvendelser { get; set; } = [];
    public List<Trivselsmaaling> Maalinger { get; set; } = [];
    public List<Kontaktperson> Kontaktpersoner { get; set; } = [];
    public List<Aftale> Aftaler { get; set; } = [];
    public DateTimeOffset Udtrukket { get; set; }
}

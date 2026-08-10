namespace BrobyggerPortal.Api.Models;

public enum UclaSlags { Baseline, Opfoelgning }
public enum OpkaldType { SamtaleMenneske, SamtaleBrobygger, Ringeopgave }

public class Henvendelse
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid MenneskeId { get; set; }
    public DateTimeOffset Dato { get; set; } = DateTimeOffset.UtcNow;
    public string? Kanal { get; set; }              // telefon | mail | fysisk | henvist
    public string? Resume { get; set; }
    public bool Foerstegang { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class UclaMaaling
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid MenneskeId { get; set; }
    public UclaSlags Slags { get; set; } = UclaSlags.Baseline;
    public int Score { get; set; }                  // UCLA-3: 3–9
    public DateTimeOffset Dato { get; set; } = DateTimeOffset.UtcNow;
    public string? Noter { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class Kontaktperson
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid MenneskeId { get; set; }
    public string Navn { get; set; } = string.Empty;
    public string? Relation { get; set; }           // pårørende | instans | andet
    public string? Telefon { get; set; }
    public string? Email { get; set; }
    public string? Noter { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class Opkald
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid? MenneskeId { get; set; }
    public Guid? BrobyggerId { get; set; }
    public OpkaldType Type { get; set; } = OpkaldType.SamtaleMenneske;
    public string? Retning { get; set; }            // ind | ud
    public int? VarighedSek { get; set; }
    public string? Note { get; set; }
    public DateTimeOffset Tidspunkt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class Stamdata
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Kategori { get; set; } = string.Empty;   // henvender | modtager | aflysning_aarsag | ...
    public string Vaerdi { get; set; } = string.Empty;
    public string? Hovedsaede { get; set; }
    public bool Aktiv { get; set; } = true;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class BeskedSkabelon
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid? EjerId { get; set; }               // null = standardskabelon
    public string Navn { get; set; } = string.Empty;
    public string Indhold { get; set; } = string.Empty;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class UdlaegKonto
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid BrobyggerId { get; set; }
    public string? RegNr { get; set; }
    public byte[]? KontoNrEnc { get; set; }         // krypteret server-side (art. 5/32)
    public string? Iban { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

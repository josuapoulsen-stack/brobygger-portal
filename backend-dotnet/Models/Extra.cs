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

public class Trivselsmaaling
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid MenneskeId { get; set; }
    public string Instrument { get; set; } = "kombineret";   // kombineret | ucla3 | who5
    public UclaSlags Slags { get; set; } = UclaSlags.Baseline;
    public int Score { get; set; }                           // total (kombineret: 5–25, højere = bedre trivsel)
    // Kombineret 5-item (Likert 1–5). Null for ucla3/who5.
    public int? Ensom { get; set; }                          // "Jeg føler mig ensom" (reverse-scores)
    public int? Faellesskab { get; set; }                    // "…hører til i et fællesskab"
    public int? Stoette { get; set; }                        // "…personer jeg kan få støtte fra"
    public int? Hverdag { get; set; }                        // "…i stand til at håndtere min hverdag"
    public int? Velbefindende { get; set; }                  // "Mit generelle velbefindende er godt"
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

public class Notifikation
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Type { get; set; } = "";      // ny_aftale | aftale_godkendt | ny_besked | ...
    public string Tekst { get; set; } = "";
    public string? Link { get; set; }
    public bool Laest { get; set; }
    public DateTimeOffset Tidspunkt { get; set; } = DateTimeOffset.UtcNow;
}

// Revisionsspor (GDPR art. 30): hvem gjorde hvad, hvornår — aldrig selve indholdet.
public class AuditLog
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Handling { get; set; } = "";     // gdpr_rapport | kreditor_eksport | helbred_visning | menneske_slettet
    public string? MaalType { get; set; }           // menneske | brobygger | ...
    public Guid? MaalId { get; set; }
    public string Aktoer { get; set; } = "";
    public string? Detalje { get; set; }
    public DateTimeOffset Tidspunkt { get; set; } = DateTimeOffset.UtcNow;
}

public class Besked
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid AftaleId { get; set; }
    public string Afsender { get; set; } = "";
    public string Tekst { get; set; } = "";
    public DateTimeOffset Tidspunkt { get; set; } = DateTimeOffset.UtcNow;
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

using BrobyggerPortal.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Data;

/// <summary>Fiktivt dev-/test-seed. GYLDEN REGEL: kun opdigtet data — aldrig rigtige borgere.</summary>
public static class DbSeeder
{
    public static async Task SeedAsync(BrobyggerDbContext db)
    {
        if (await db.Mennesker.AnyAsync()) return;

        var b1 = new Brobygger { Navn = "Maja Lindberg", Email = "maja@example.com", Telefon = "+45 28 11 22 33", TelefonNorm = "28112233", Typer = ["en-til-en", "cafe-gruppe"], Sprog = ["dansk", "engelsk"], Hq = "København N", Status = BrobyggerStatus.Aktiv, Active = 1, MaxActive = 3 };
        var b2 = new Brobygger { Navn = "Thomas Eriksen", Email = "thomas@example.com", Telefon = "+45 40 55 66 77", TelefonNorm = "40556677", Typer = ["en-til-en"], Hq = "Aarhus C", Status = BrobyggerStatus.Aktiv, Active = 0, MaxActive = 2 };
        var b3 = new Brobygger { Navn = "Amira Osman", Email = "amira@example.com", Telefon = "+45 51 88 99 00", TelefonNorm = "51889900", Typer = ["en-til-en", "netvaerk"], Sprog = ["dansk", "arabisk", "engelsk"], Hq = "København S", Status = BrobyggerStatus.Aktiv, Active = 2, MaxActive = 3 };
        db.Brobyggere.AddRange(b1, b2, b3);

        var m1 = new Menneske { Navn = "Ahmad Karimi", Alder = 34, Kon = "mand", Telefon = "+45 71 20 30 40", TelefonNorm = "71203040", Typer = ["en-til-en"], Sprog = ["dansk", "arabisk"], Status = MenneskeStatus.Matched, MatchedWith = b3.Id, Hq = "København S", Kilde = "Egen henvendelse" };
        var m2 = new Menneske { Navn = "Bente Sørensen", Alder = 68, Kon = "kvinde", Telefon = "+45 22 44 66 88", TelefonNorm = "22446688", Typer = ["cafe-gruppe"], Status = MenneskeStatus.Aktiv, MatchedWith = b1.Id, Hq = "København N", Kilde = "Kommune" };
        var m3 = new Menneske { Navn = "Clara Nielsen", Alder = 29, Kon = "kvinde", Telefon = "+45 30 50 70 90", TelefonNorm = "30507090", Typer = ["en-til-en", "netvaerk"], Status = MenneskeStatus.Ny, Hq = "Aarhus C", Kilde = "Læge", UclaFravalgt = true };
        db.Mennesker.AddRange(m1, m2, m3);

        db.Aftaler.AddRange(
            new Aftale { BrobyggerId = b3.Id, MenneskeId = m1.Id, Dato = DateTimeOffset.UtcNow.AddDays(2), Varighed = 60, Type = AftaleType.Moede, Status = AftaleStatus.Planlagt, Brobygningstype = "Social", BrobyggerNote = "Første møde — mød op 10 min før." },
            new Aftale { BrobyggerId = b1.Id, MenneskeId = m2.Id, Dato = DateTimeOffset.UtcNow.AddDays(-5), Varighed = 90, Type = AftaleType.Aktivitet, Status = AftaleStatus.Gennemfoert, Brobygningstype = "Forening", Udfald = "gennemfoert", VarighedMin = 85 });

        await db.SaveChangesAsync();
    }
}

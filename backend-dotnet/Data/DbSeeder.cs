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

        db.Stamdata.AddRange(
            new Stamdata { Kategori = "henvender", Vaerdi = "Egen henvendelse" },
            new Stamdata { Kategori = "henvender", Vaerdi = "Kommune" },
            new Stamdata { Kategori = "henvender", Vaerdi = "Læge/hospital" },
            new Stamdata { Kategori = "modtager", Vaerdi = "Borger" },
            new Stamdata { Kategori = "modtager", Vaerdi = "Pårørende" },
            new Stamdata { Kategori = "aflysning_aarsag", Vaerdi = "Sygdom" },
            new Stamdata { Kategori = "aflysning_aarsag", Vaerdi = "Udeblevet" },
            new Stamdata { Kategori = "aflysning_aarsag", Vaerdi = "Ombooket" },
            // Program-/indsatstyper (koder) — datalist-forslag; koordinator kan tilføje flere under Stamdata
            new Stamdata { Kategori = "programtype", Vaerdi = "SBB" },
            new Stamdata { Kategori = "programtype", Vaerdi = "IDA" },
            new Stamdata { Kategori = "programtype", Vaerdi = "LP" },
            new Stamdata { Kategori = "indsatstype", Vaerdi = "IDAB" },
            new Stamdata { Kategori = "indsatstype", Vaerdi = "SBB" },
            new Stamdata { Kategori = "indsatstype", Vaerdi = "Ledsagelse" },
            new Stamdata { Kategori = "indsatstype", Vaerdi = "Netværk" });

        await db.SaveChangesAsync();
    }

    /// <summary>Idempotent: sikrer at nye stamdata-kategorier findes selv i en allerede seedet database.</summary>
    public static async Task EnsureStamdataAsync(BrobyggerDbContext db)
    {
        (string kat, string vaerdi)[] ønskede =
        [
            ("programtype","SBB"), ("programtype","IDA"), ("programtype","LP"),
            ("indsatstype","IDAB"), ("indsatstype","SBB"), ("indsatstype","Ledsagelse"), ("indsatstype","Netværk"),
        ];
        var findes = await db.Stamdata
            .Where(s => s.Kategori == "programtype" || s.Kategori == "indsatstype")
            .Select(s => s.Kategori + "|" + s.Vaerdi).ToListAsync();
        var sæt = findes.ToHashSet();
        var nye = ønskede.Where(x => !sæt.Contains(x.kat + "|" + x.vaerdi))
            .Select(x => new Stamdata { Kategori = x.kat, Vaerdi = x.vaerdi }).ToList();
        if (nye.Count == 0) return;
        db.Stamdata.AddRange(nye);
        await db.SaveChangesAsync();
    }
}

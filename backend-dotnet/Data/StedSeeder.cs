using BrobyggerPortal.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Data;

/// <summary>
/// Indlæser det kuraterede SOR-udtræk (Data/steder.csv) i Steder-tabellen ved opstart,
/// hvis den er tom. Offentlige, ikke-personlige stamdata — ikke omfattet af den gyldne regel.
/// </summary>
public static class StedSeeder
{
    public static async Task SeedAsync(BrobyggerDbContext db)
    {
        if (await db.Steder.AnyAsync()) return;

        var sti = Path.Combine(AppContext.BaseDirectory, "Data", "steder.csv");
        if (!File.Exists(sti)) return;

        var linjer = await File.ReadAllLinesAsync(sti, System.Text.Encoding.UTF8);
        var steder = new List<Sted>(linjer.Length);
        // header: sor_id;navn;type;sygehus;shak;vej;postnr;by;region
        for (int i = 1; i < linjer.Length; i++)
        {
            var c = linjer[i].Split(';');
            if (c.Length < 9 || string.IsNullOrWhiteSpace(c[0])) continue;
            var s = new Sted
            {
                SorId = c[0], Navn = c[1],
                Type = NullHvisTom(c[2]), Sygehus = NullHvisTom(c[3]), Shak = NullHvisTom(c[4]),
                Vej = NullHvisTom(c[5]), Postnr = NullHvisTom(c[6]), By = NullHvisTom(c[7]), Region = NullHvisTom(c[8]),
            };
            s.Soegetekst = $"{s.Navn} {s.Sygehus} {s.By} {s.Shak}".ToLowerInvariant();
            steder.Add(s);
        }

        db.ChangeTracker.AutoDetectChangesEnabled = false;
        db.Steder.AddRange(steder);
        await db.SaveChangesAsync();
        db.ChangeTracker.AutoDetectChangesEnabled = true;
    }

    private static string? NullHvisTom(string s) => string.IsNullOrWhiteSpace(s) ? null : s;
}

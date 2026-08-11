using System.Text;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Kreditor-eksport til e-conomic (CSV). KUN Økonomi-rollen. Kontonr. dekrypteres
// server-side ind i filen. Udtræk logges (revisionsspor).
[ApiController, Authorize(Roles = "Oekonomi"), Route("v1/udlaeg/eksport")]
public class UdlaegEksportController(BrobyggerDbContext db, CryptoService crypto, ILogger<UdlaegEksportController> log) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Eksport()
    {
        var konti = await db.UdlaegKonti.ToListAsync();
        var navne = await db.Brobyggere.ToDictionaryAsync(b => b.Id, b => b.Navn);

        log.LogInformation("Kreditor-eksport udtrukket af {Bruger} ({Antal} konti)",
            User.Identity?.Name ?? "ukendt", konti.Count);

        var sb = new StringBuilder();
        sb.AppendLine("navn;reg_nr;konto_nr;iban");
        foreach (var k in konti)
        {
            var navn = navne.TryGetValue(k.BrobyggerId, out var n) ? n : "";
            var konto = crypto.DecryptBank(k.KontoNrEnc) ?? "";
            sb.AppendLine($"{Csv(navn)};{Csv(k.RegNr)};{Csv(konto)};{Csv(k.Iban)}");
        }

        return File(Encoding.UTF8.GetBytes(sb.ToString()), "text/csv; charset=utf-8", "kreditorer.csv");
    }

    private static string Csv(string? s) => s is null ? "" : "\"" + s.Replace("\"", "\"\"") + "\"";
}

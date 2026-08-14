using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Autoudfyld for "sted" på en aftale — søger i SOR-udtrækket (sygehuse/afdelinger m.m.).
[ApiController, Authorize, Route("v1/steder")]
public class StederController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Soeg([FromQuery] string q, [FromQuery] int limit = 20)
    {
        if (string.IsNullOrWhiteSpace(q) || q.Trim().Length < 2)
            return Ok(Array.Empty<object>());

        var s = q.Trim().ToLowerInvariant();
        limit = Math.Clamp(limit, 1, 50);

        // Prefix-match (navn starter med q) rankes før midt-i-tekst-match.
        var rows = await db.Steder
            .Where(x => EF.Functions.ILike(x.Soegetekst, $"%{s}%")
                        && !EF.Functions.ILike(x.Navn, "(Ikke i brug)%")
                        && !EF.Functions.ILike(x.Navn, "(Lukket)%"))
            .OrderByDescending(x => EF.Functions.ILike(x.Navn, $"{s}%"))
            .ThenBy(x => x.Navn)
            .Take(limit)
            .Select(x => new
            {
                x.SorId, x.Navn, x.Type, x.Sygehus, x.Shak,
                x.Vej, x.Postnr, x.By, x.Region,
                label = Label(x.Navn, x.Sygehus, x.By),
            })
            .ToListAsync();

        return Ok(rows);
    }

    // Vist etiket: "Navn · Sygehus (By)" — kun de dele der findes.
    private static string Label(string navn, string? sygehus, string? by)
    {
        var s = navn;
        if (!string.IsNullOrEmpty(sygehus) && sygehus != navn) s += " · " + sygehus;
        if (!string.IsNullOrEmpty(by)) s += $" ({by})";
        return s;
    }
}

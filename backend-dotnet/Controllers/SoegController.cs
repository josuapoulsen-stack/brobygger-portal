using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Fritekstsøgning på tværs af mennesker og brobyggere (navn/telefon).
[ApiController, Authorize, Route("v1/soeg")]
public class SoegController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Soeg([FromQuery] string q)
    {
        if (string.IsNullOrWhiteSpace(q) || q.Length < 2)
            return Ok(new { mennesker = Array.Empty<object>(), brobyggere = Array.Empty<object>() });

        var ciffer = new string(q.Where(char.IsDigit).ToArray());

        var mennesker = await db.Mennesker
            .Where(m => m.DeletedAt == null &&
                (EF.Functions.ILike(m.Navn, $"%{q}%") ||
                 (ciffer.Length >= 2 && m.TelefonNorm != null && m.TelefonNorm.Contains(ciffer))))
            .OrderBy(m => m.Navn).Take(15)
            .Select(m => new { m.Id, m.Navn, m.Telefon, m.Hq, type = "menneske" })
            .ToListAsync();

        var brobyggere = await db.Brobyggere
            .Where(b => EF.Functions.ILike(b.Navn, $"%{q}%") ||
                (ciffer.Length >= 2 && b.TelefonNorm != null && b.TelefonNorm.Contains(ciffer)))
            .OrderBy(b => b.Navn).Take(15)
            .Select(b => new { b.Id, b.Navn, b.Telefon, b.Hq, type = "brobygger" })
            .ToListAsync();

        return Ok(new { mennesker, brobyggere });
    }
}

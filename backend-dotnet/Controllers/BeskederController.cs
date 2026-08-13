using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Besked-tråd pr. aftale. Fundamentet for chat-funktionen: koordinator opretter en aftale
// (evt. fra skabelon) → beskeden lægger sig som første besked; brobygger kan se + svare.
[ApiController, Authorize]
public class BeskederController(BrobyggerDbContext db, BrobyggerPortal.Api.Services.NotifikationService notif) : ControllerBase
{
    public record BeskedInput(string? Afsender, string Tekst);

    [HttpGet("/v1/aftaler/{aftaleId:guid}/beskeder")]
    public async Task<IActionResult> List(Guid aftaleId) =>
        Ok(await db.Beskeder.Where(b => b.AftaleId == aftaleId).OrderBy(b => b.Tidspunkt).ToListAsync());

    [HttpPost("/v1/aftaler/{aftaleId:guid}/beskeder")]
    public async Task<IActionResult> Create(Guid aftaleId, BeskedInput dto)
    {
        if (await db.Aftaler.FindAsync(aftaleId) is null) return NotFound("Aftale ikke fundet");
        var b = new Besked
        {
            AftaleId = aftaleId,
            Afsender = string.IsNullOrWhiteSpace(dto.Afsender) ? (User.Identity?.Name ?? "Koordinator") : dto.Afsender,
            Tekst = dto.Tekst,
        };
        db.Beskeder.Add(b);
        await db.SaveChangesAsync();
        await notif.PushAsync("ny_besked", "Ny besked på en aftale", $"/aftaler/{aftaleId}");
        return Created($"/v1/beskeder/{b.Id}", b);
    }
}

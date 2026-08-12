using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController, Authorize, Route("v1/mennesker/{menneskeId:guid}/match")]
public class MatchController(BrobyggerDbContext db) : ControllerBase
{
    public record MatchDto(Guid BrobyggerId);
    public record MatchForslag(Guid Id, string Navn, string? Hq, int Active, int MaxActive, int Score, string Begrundelse);

    // Rangeret liste af passende brobyggere: kapacitet + samme hovedsæde + fælles behov/sprog.
    [HttpGet("/v1/mennesker/{menneskeId:guid}/match-forslag")]
    public async Task<IActionResult> Forslag(Guid menneskeId)
    {
        var m = await db.Mennesker.FindAsync(menneskeId);
        if (m is null || m.DeletedAt is not null) return NotFound();

        var brobyggere = await db.Brobyggere.Where(b => b.Status == BrobyggerStatus.Aktiv).ToListAsync();
        var forslag = brobyggere.Select(b =>
        {
            var score = 0;
            var grunde = new List<string>();
            if (b.Active < b.MaxActive) { score += 2; } else { grunde.Add("fuld"); }
            if (!string.IsNullOrEmpty(m.Hq) && b.Hq == m.Hq) { score += 3; grunde.Add("samme hovedsæde"); }
            var t = m.Typer.Intersect(b.Typer).Count(); if (t > 0) { score += t; grunde.Add($"{t} fælles behov"); }
            var s = m.Sprog.Intersect(b.Sprog).Count(); if (s > 0) { score += s; grunde.Add($"{s} fælles sprog"); }
            return new MatchForslag(b.Id, b.Navn, b.Hq, b.Active, b.MaxActive, score, string.Join(" · ", grunde));
        })
        .OrderByDescending(x => x.Score).ThenBy(x => x.Navn).Take(5).ToList();

        return Ok(forslag);
    }

    [HttpPost]
    public async Task<IActionResult> Match(Guid menneskeId, MatchDto dto)
    {
        var m = await db.Mennesker.FindAsync(menneskeId);
        if (m is null || m.DeletedAt is not null) return NotFound("Menneske ikke fundet");
        var b = await db.Brobyggere.FindAsync(dto.BrobyggerId);
        if (b is null) return NotFound("Brobygger ikke fundet");
        if (m.MatchedWith == dto.BrobyggerId) return NoContent();
        if (b.Active >= b.MaxActive) return Conflict("Brobygger har ikke kapacitet");

        // Frigør evt. tidligere match
        if (m.MatchedWith is Guid gammel)
        {
            var g = await db.Brobyggere.FindAsync(gammel);
            if (g is not null && g.Active > 0) g.Active--;
        }

        m.MatchedWith = b.Id;
        m.Status = MenneskeStatus.Matched;
        b.Active++;
        m.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpDelete]
    public async Task<IActionResult> Unmatch(Guid menneskeId)
    {
        var m = await db.Mennesker.FindAsync(menneskeId);
        if (m is null) return NotFound();
        if (m.MatchedWith is Guid bid)
        {
            var b = await db.Brobyggere.FindAsync(bid);
            if (b is not null && b.Active > 0) b.Active--;
        }
        m.MatchedWith = null;
        m.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return NoContent();
    }
}

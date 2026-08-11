using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BrobyggerPortal.Api.Controllers;

[ApiController, Authorize, Route("v1/mennesker/{menneskeId:guid}/match")]
public class MatchController(BrobyggerDbContext db) : ControllerBase
{
    public record MatchDto(Guid BrobyggerId);

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

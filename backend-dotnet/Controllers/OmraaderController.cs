using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Områdestruktur (hovedsæder + lokalafdelinger) — styres af koordinator (Admin).
// /v1/omraader beholder den flade form til scope-filteret; /v1/hovedsaeder er til administration.
[ApiController, Authorize, Route("v1")]
public class OmraaderController(BrobyggerDbContext db) : ControllerBase
{
    public record OmraadeFlad(string Hovedsaede, List<string> Afdelinger);
    public record AfdelingDto(Guid Id, string Navn);
    public record HovedsaedeDto(Guid Id, string Navn, List<AfdelingDto> Afdelinger);
    public record NavnDto(string Navn);

    // Flad form til scope-filteret (uændret kontrakt).
    [HttpGet("omraader")]
    public async Task<ActionResult<IEnumerable<OmraadeFlad>>> Omraader()
    {
        var hs = await db.Hovedsaeder.Include(h => h.Afdelinger).OrderBy(h => h.Navn).ToListAsync();
        return Ok(hs.Select(h => new OmraadeFlad(h.Navn, h.Afdelinger.OrderBy(a => a.Navn).Select(a => a.Navn).ToList())));
    }

    // Fuld form til administration (med id'er).
    [HttpGet("hovedsaeder")]
    public async Task<ActionResult<IEnumerable<HovedsaedeDto>>> List()
    {
        var hs = await db.Hovedsaeder.Include(h => h.Afdelinger).OrderBy(h => h.Navn).ToListAsync();
        return Ok(hs.Select(h => new HovedsaedeDto(h.Id, h.Navn,
            h.Afdelinger.OrderBy(a => a.Navn).Select(a => new AfdelingDto(a.Id, a.Navn)).ToList())));
    }

    [HttpPost("hovedsaeder"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> OpretHovedsaede(NavnDto dto)
    {
        if (string.IsNullOrWhiteSpace(dto.Navn)) return BadRequest("Navn mangler");
        var navn = dto.Navn.Trim();
        if (await db.Hovedsaeder.AnyAsync(h => h.Navn == navn)) return Conflict("Findes allerede");
        var h = new Hovedsaede { Navn = navn };
        db.Hovedsaeder.Add(h);
        await db.SaveChangesAsync();
        return Ok(new HovedsaedeDto(h.Id, h.Navn, []));
    }

    [HttpPut("hovedsaeder/{id:guid}"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> OmdoebHovedsaede(Guid id, NavnDto dto)
    {
        var h = await db.Hovedsaeder.FindAsync(id);
        if (h is null) return NotFound();
        if (string.IsNullOrWhiteSpace(dto.Navn)) return BadRequest("Navn mangler");
        h.Navn = dto.Navn.Trim();
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpDelete("hovedsaeder/{id:guid}"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> SletHovedsaede(Guid id)
    {
        var h = await db.Hovedsaeder.FindAsync(id);
        if (h is null) return NotFound();
        db.Hovedsaeder.Remove(h);   // cascade sletter afdelinger
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPost("hovedsaeder/{id:guid}/afdelinger"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> OpretAfdeling(Guid id, NavnDto dto)
    {
        var h = await db.Hovedsaeder.Include(x => x.Afdelinger).FirstOrDefaultAsync(x => x.Id == id);
        if (h is null) return NotFound();
        if (string.IsNullOrWhiteSpace(dto.Navn)) return BadRequest("Navn mangler");
        var navn = dto.Navn.Trim();
        if (h.Afdelinger.Any(a => a.Navn == navn)) return Conflict("Findes allerede");
        var a = new Lokalafdeling { Navn = navn, HovedsaedeId = id };
        db.Lokalafdelinger.Add(a);
        await db.SaveChangesAsync();
        return Ok(new AfdelingDto(a.Id, a.Navn));
    }

    [HttpPut("afdelinger/{id:guid}"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> OmdoebAfdeling(Guid id, NavnDto dto)
    {
        var a = await db.Lokalafdelinger.FindAsync(id);
        if (a is null) return NotFound();
        if (string.IsNullOrWhiteSpace(dto.Navn)) return BadRequest("Navn mangler");
        a.Navn = dto.Navn.Trim();
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpDelete("afdelinger/{id:guid}"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> SletAfdeling(Guid id)
    {
        var a = await db.Lokalafdelinger.FindAsync(id);
        if (a is null) return NotFound();
        db.Lokalafdelinger.Remove(a);
        await db.SaveChangesAsync();
        return NoContent();
    }
}

using BrobyggerPortal.Api.Common;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Dtos;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController]
[Route("v1/brobyggere")]
[Authorize]
public class BrobyggereController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<BrobyggerReadDto>>> List(
        [FromQuery] BrobyggerStatus? status, [FromQuery] string? hq)
    {
        var q = db.Brobyggere.AsQueryable();
        if (status is not null) q = q.Where(b => b.Status == status);
        if (!string.IsNullOrEmpty(hq)) q = q.Where(b => b.Hq == hq);
        var rows = await q.OrderBy(b => b.Navn).ToListAsync();
        return Ok(rows.Select(BrobyggerReadDto.From));
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<BrobyggerReadDto>> Get(Guid id)
    {
        var b = await db.Brobyggere.FindAsync(id);
        if (b is null) return NotFound();
        return BrobyggerReadDto.From(b);
    }

    [HttpPost]
    public async Task<ActionResult<BrobyggerReadDto>> Create(BrobyggerCreateDto dto)
    {
        var b = new Brobygger
        {
            Navn = dto.Navn, Email = dto.Email, Telefon = dto.Telefon, Typer = dto.Typer, Sprog = dto.Sprog,
            Hq = dto.Hq, Afdeling = dto.Afdeling, Region = dto.Region, Kon = dto.Kon, Bio = dto.Bio, AvatarUrl = dto.AvatarUrl,
            Status = dto.Status, Active = dto.Active, MaxActive = dto.MaxActive,
            TilgaengeligFra = dto.TilgaengeligFra, NaesteTid = dto.NaesteTid, Startdato = dto.Startdato,
            SenesteMoede = dto.SenesteMoede, Noter = dto.Noter,
            TelefonNorm = Telefon.Normaliser(dto.Telefon),
        };
        db.Brobyggere.Add(b);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(Get), new { id = b.Id }, BrobyggerReadDto.From(b));
    }

    [HttpPatch("{id:guid}")]
    public async Task<ActionResult<BrobyggerReadDto>> Update(Guid id, BrobyggerUpdateDto dto)
    {
        var b = await db.Brobyggere.FindAsync(id);
        if (b is null) return NotFound();

        if (dto.Navn is not null) b.Navn = dto.Navn;
        if (dto.Email is not null) b.Email = dto.Email;
        if (dto.Telefon is not null) { b.Telefon = dto.Telefon; b.TelefonNorm = Telefon.Normaliser(dto.Telefon); }
        if (dto.Typer is not null) b.Typer = dto.Typer;
        if (dto.Sprog is not null) b.Sprog = dto.Sprog;
        if (dto.Hq is not null) b.Hq = dto.Hq;
        if (dto.Afdeling is not null) b.Afdeling = dto.Afdeling;
        if (dto.Region is not null) b.Region = dto.Region;
        if (dto.Kon is not null) b.Kon = dto.Kon;
        if (dto.Bio is not null) b.Bio = dto.Bio;
        if (dto.AvatarUrl is not null) b.AvatarUrl = dto.AvatarUrl;
        if (dto.Status is not null) b.Status = dto.Status.Value;
        if (dto.Active is not null) b.Active = dto.Active.Value;
        if (dto.MaxActive is not null) b.MaxActive = dto.MaxActive.Value;
        if (dto.TilgaengeligFra is not null) b.TilgaengeligFra = dto.TilgaengeligFra;
        if (dto.NaesteTid is not null) b.NaesteTid = dto.NaesteTid;
        if (dto.Startdato is not null) b.Startdato = dto.Startdato;
        if (dto.SenesteMoede is not null) b.SenesteMoede = dto.SenesteMoede;
        if (dto.Noter is not null) b.Noter = dto.Noter;

        b.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return BrobyggerReadDto.From(b);
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var b = await db.Brobyggere.FindAsync(id);
        if (b is null) return NotFound();
        db.Brobyggere.Remove(b);
        await db.SaveChangesAsync();
        return NoContent();
    }
}

using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Dtos;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController]
[Route("v1/aftaler")]
[Authorize]
public class AftalerController(BrobyggerDbContext db) : ControllerBase
{
    // Statusser der tæller som et "aktivt forløb" på brobyggeren
    private static readonly AftaleStatus[] AktiveStatus =
        [AftaleStatus.Planlagt, AftaleStatus.Pending, AftaleStatus.Confirmed];

    [HttpGet]
    public async Task<ActionResult<IEnumerable<AftaleReadDto>>> List(
        [FromQuery] Guid? brobyggerId, [FromQuery] Guid? menneskeId, [FromQuery] AftaleStatus? status)
    {
        var q = db.Aftaler.AsQueryable();
        if (brobyggerId is not null) q = q.Where(a => a.BrobyggerId == brobyggerId);
        if (menneskeId is not null) q = q.Where(a => a.MenneskeId == menneskeId);
        if (status is not null) q = q.Where(a => a.Status == status);
        var rows = await q.OrderByDescending(a => a.Dato).ToListAsync();
        return Ok(rows.Select(AftaleReadDto.From));
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<AftaleReadDto>> Get(Guid id)
    {
        var a = await db.Aftaler.FindAsync(id);
        if (a is null) return NotFound();
        return AftaleReadDto.From(a);
    }

    [HttpPost]
    public async Task<ActionResult<AftaleReadDto>> Create(AftaleCreateDto dto)
    {
        var brobygger = await db.Brobyggere.FindAsync(dto.BrobyggerId);
        if (brobygger is null) return NotFound("Brobygger ikke fundet");
        if (await db.Mennesker.FindAsync(dto.MenneskeId) is null) return NotFound("Menneske ikke fundet");
        if (AktiveStatus.Contains(dto.Status) && brobygger.Active >= brobygger.MaxActive)
            return Conflict("Brobygger har ikke kapacitet");

        var a = new Aftale
        {
            BrobyggerId = dto.BrobyggerId, MenneskeId = dto.MenneskeId, Dato = dto.Dato,
            Varighed = dto.Varighed, Type = dto.Type, Sted = dto.Sted, Beskrivelse = dto.Beskrivelse,
            Status = dto.Status, Notes = dto.Notes, Aftaletype = dto.Aftaletype,
            Brobygningstype = dto.Brobygningstype, Henvender = dto.Henvender, Modtager = dto.Modtager,
            Finansiering = dto.Finansiering, Samarbejdspartner = dto.Samarbejdspartner, Afdeling = dto.Afdeling,
            Transportplan = dto.Transportplan, AktivitetsTid = dto.AktivitetsTid, FremmoedeType = dto.FremmoedeType,
            Gentagelse = dto.Gentagelse, AftaleForm = dto.AftaleForm, BrobyggerNote = dto.BrobyggerNote,
            RaadgiverOpfoelgning = dto.RaadgiverOpfoelgning,
        };
        db.Aftaler.Add(a);
        await db.SaveChangesAsync();
        // TODO (SSE): push "ny_aftale"-event til brobygger via egen backend-stream
        return CreatedAtAction(nameof(Get), new { id = a.Id }, AftaleReadDto.From(a));
    }

    [HttpPatch("{id:guid}/status")]
    public async Task<ActionResult<AftaleReadDto>> UpdateStatus(Guid id, AftaleStatusUpdateDto dto)
    {
        var a = await db.Aftaler.FindAsync(id);
        if (a is null) return NotFound();
        a.Status = dto.Status;
        if (!string.IsNullOrEmpty(dto.Notes)) a.Notes = dto.Notes;
        a.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return AftaleReadDto.From(a);
    }
}

using BrobyggerPortal.Api.Common;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Dtos;
using BrobyggerPortal.Api.Models;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController]
[Route("v1/mennesker")]
[Authorize]
public class MenneskerController(BrobyggerDbContext db, CryptoService crypto) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<MenneskeReadDto>>> List(
        [FromQuery] MenneskeStatus? status, [FromQuery] string? hq)
    {
        var q = db.Mennesker.Where(m => m.DeletedAt == null);
        if (status is not null) q = q.Where(m => m.Status == status);
        if (!string.IsNullOrEmpty(hq)) q = q.Where(m => m.Hq == hq);
        var rows = await q.OrderByDescending(m => m.CreatedAt).ToListAsync();
        return Ok(rows.Select(MenneskeReadDto.From));
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<MenneskeReadDto>> Get(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        return MenneskeReadDto.From(m);
    }

    [HttpPost]
    public async Task<ActionResult<MenneskeReadDto>> Create(MenneskeCreateDto dto)
    {
        var m = new Menneske
        {
            Navn = dto.Navn, Alder = dto.Alder, Kon = dto.Kon, Email = dto.Email,
            Telefon = dto.Telefon, Adresse = dto.Adresse, Typer = dto.Typer, Sprog = dto.Sprog,
            Noter = dto.Noter, Status = dto.Status, MatchedWith = dto.MatchedWith,
            RaadgiverId = dto.RaadgiverId, Hq = dto.Hq, Afdeling = dto.Afdeling, Kilde = dto.Kilde,
            Meetpoint = dto.Meetpoint, SroiMaalgruppe = dto.SroiMaalgruppe,
            HelbredsKategorier = dto.HelbredsKategorier, PraeferencerJson = dto.Praeferencer,
            AfslutTrivsel = dto.AfslutTrivsel, AfslutAarsag = dto.AfslutAarsag, UclaFravalgt = dto.UclaFravalgt,
            TelefonNorm = Telefon.Normaliser(dto.Telefon),
            HelbredsnoterEnc = crypto.EncryptHealth(dto.Helbredsnoter),   // art. 9 — krypteret
        };
        db.Mennesker.Add(m);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(Get), new { id = m.Id }, MenneskeReadDto.From(m));
    }

    [HttpPatch("{id:guid}")]
    public async Task<ActionResult<MenneskeReadDto>> Update(Guid id, MenneskeUpdateDto dto)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();

        if (dto.Navn is not null) m.Navn = dto.Navn;
        if (dto.Alder is not null) m.Alder = dto.Alder;
        if (dto.Kon is not null) m.Kon = dto.Kon;
        if (dto.Email is not null) m.Email = dto.Email;
        if (dto.Telefon is not null) { m.Telefon = dto.Telefon; m.TelefonNorm = Telefon.Normaliser(dto.Telefon); }
        if (dto.Adresse is not null) m.Adresse = dto.Adresse;
        if (dto.Typer is not null) m.Typer = dto.Typer;
        if (dto.Sprog is not null) m.Sprog = dto.Sprog;
        if (dto.Noter is not null) m.Noter = dto.Noter;
        if (dto.Status is not null) m.Status = dto.Status.Value;
        if (dto.MatchedWith is not null) m.MatchedWith = dto.MatchedWith;
        if (dto.RaadgiverId is not null) m.RaadgiverId = dto.RaadgiverId;
        if (dto.Hq is not null) m.Hq = dto.Hq;
        if (dto.Afdeling is not null) m.Afdeling = dto.Afdeling;
        if (dto.Kilde is not null) m.Kilde = dto.Kilde;
        if (dto.Meetpoint is not null) m.Meetpoint = dto.Meetpoint;
        if (dto.SroiMaalgruppe is not null) m.SroiMaalgruppe = dto.SroiMaalgruppe;
        if (dto.HelbredsKategorier is not null) m.HelbredsKategorier = dto.HelbredsKategorier;
        if (dto.Praeferencer is not null) m.PraeferencerJson = dto.Praeferencer;
        if (dto.AfslutTrivsel is not null) m.AfslutTrivsel = dto.AfslutTrivsel;
        if (dto.AfslutAarsag is not null) m.AfslutAarsag = dto.AfslutAarsag;
        if (dto.UclaFravalgt is not null) m.UclaFravalgt = dto.UclaFravalgt.Value;
        if (dto.Helbredsnoter is not null) m.HelbredsnoterEnc = crypto.EncryptHealth(dto.Helbredsnoter);

        m.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return MenneskeReadDto.From(m);
    }

    // Følsom læsning (art. 9): kun Admin/Rådgiver. TODO: log i revisionsspor (aktør/tid/mål-id).
    [HttpGet("{id:guid}/helbredsnoter"), Authorize(Roles = "Admin,Raadgiver")]
    public async Task<IActionResult> Helbredsnoter(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        return Ok(new { helbredsnoter = crypto.DecryptHealth(m.HelbredsnoterEnc) });
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        // Soft-delete: PII anonymiseres via batch-job efter 30 dage
        m.DeletedAt = DateTimeOffset.UtcNow;
        m.Status = MenneskeStatus.Afsluttet;
        await db.SaveChangesAsync();
        return NoContent();
    }
}

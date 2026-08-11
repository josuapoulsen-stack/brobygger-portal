using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Simple ressourcer: for at holde koden kompakt bindes entiteten direkte ved oprettelse,
// og server-styrede felter (Id, CreatedAt, forældre-id) sættes serverside.

[ApiController, Authorize]
public class HenvendelserController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet("/v1/mennesker/{menneskeId:guid}/henvendelser")]
    public async Task<IActionResult> List(Guid menneskeId) =>
        Ok(await db.Henvendelser.Where(h => h.MenneskeId == menneskeId).OrderBy(h => h.Dato).ToListAsync());

    [HttpPost("/v1/mennesker/{menneskeId:guid}/henvendelser")]
    public async Task<IActionResult> Create(Guid menneskeId, Henvendelse dto)
    {
        dto.Id = Guid.NewGuid(); dto.MenneskeId = menneskeId; dto.CreatedAt = DateTimeOffset.UtcNow;
        db.Henvendelser.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/henvendelser/{dto.Id}", dto);
    }

    [HttpDelete("/v1/henvendelser/{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var h = await db.Henvendelser.FindAsync(id);
        if (h is null) return NotFound();
        db.Henvendelser.Remove(h); await db.SaveChangesAsync();
        return NoContent();
    }
}

[ApiController, Authorize]
public class MaalingerController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet("/v1/mennesker/{menneskeId:guid}/maalinger")]
    public async Task<IActionResult> List(Guid menneskeId) =>
        Ok(await db.Trivselsmaalinger.Where(u => u.MenneskeId == menneskeId).OrderBy(u => u.Dato).ToListAsync());

    [HttpPost("/v1/mennesker/{menneskeId:guid}/maalinger")]
    public async Task<IActionResult> Create(Guid menneskeId, Trivselsmaaling dto)
    {
        dto.Id = Guid.NewGuid(); dto.MenneskeId = menneskeId; dto.CreatedAt = DateTimeOffset.UtcNow;
        // Kombineret: beregn samlet trivsels-score (5–25, højere = bedre). "Ensom" vendes om.
        if (dto.Instrument == "kombineret" &&
            dto.Ensom is int e && dto.Faellesskab is int f && dto.Stoette is int s &&
            dto.Hverdag is int h && dto.Velbefindende is int v)
        {
            dto.Score = (6 - e) + f + s + h + v;
        }
        db.Trivselsmaalinger.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/maalinger/{dto.Id}", dto);
    }
}

[ApiController, Authorize]
public class KontaktpersonerController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet("/v1/mennesker/{menneskeId:guid}/kontaktpersoner")]
    public async Task<IActionResult> List(Guid menneskeId) =>
        Ok(await db.Kontaktpersoner.Where(k => k.MenneskeId == menneskeId).OrderBy(k => k.Navn).ToListAsync());

    [HttpPost("/v1/mennesker/{menneskeId:guid}/kontaktpersoner")]
    public async Task<IActionResult> Create(Guid menneskeId, Kontaktperson dto)
    {
        dto.Id = Guid.NewGuid(); dto.MenneskeId = menneskeId; dto.CreatedAt = DateTimeOffset.UtcNow;
        db.Kontaktpersoner.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/kontaktpersoner/{dto.Id}", dto);
    }

    [HttpDelete("/v1/kontaktpersoner/{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var k = await db.Kontaktpersoner.FindAsync(id);
        if (k is null) return NotFound();
        db.Kontaktpersoner.Remove(k); await db.SaveChangesAsync();
        return NoContent();
    }
}

[ApiController, Authorize, Route("v1/opkald")]
public class OpkaldController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List([FromQuery] Guid? menneskeId, [FromQuery] Guid? brobyggerId, [FromQuery] OpkaldType? type)
    {
        var q = db.Opkald.AsQueryable();
        if (menneskeId is not null) q = q.Where(o => o.MenneskeId == menneskeId);
        if (brobyggerId is not null) q = q.Where(o => o.BrobyggerId == brobyggerId);
        if (type is not null) q = q.Where(o => o.Type == type);
        return Ok(await q.OrderByDescending(o => o.Tidspunkt).ToListAsync());
    }

    [HttpPost]
    public async Task<IActionResult> Create(Opkald dto)
    {
        if (dto.MenneskeId is null && dto.BrobyggerId is null)
            return BadRequest("Opkald skal kobles til et menneske eller en brobygger");
        dto.Id = Guid.NewGuid(); dto.CreatedAt = DateTimeOffset.UtcNow;
        db.Opkald.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/opkald/{dto.Id}", dto);
    }
}

[ApiController, Authorize, Route("v1/stamdata")]
public class StamdataController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List([FromQuery] string? kategori, [FromQuery] string? hovedsaede)
    {
        var q = db.Stamdata.Where(s => s.Aktiv);
        if (!string.IsNullOrEmpty(kategori)) q = q.Where(s => s.Kategori == kategori);
        if (!string.IsNullOrEmpty(hovedsaede)) q = q.Where(s => s.Hovedsaede == hovedsaede);
        return Ok(await q.OrderBy(s => s.Kategori).ThenBy(s => s.Vaerdi).ToListAsync());
    }

    [HttpPost, Authorize(Roles = "Admin")]
    public async Task<IActionResult> Create(Stamdata dto)
    {
        dto.Id = Guid.NewGuid(); dto.CreatedAt = DateTimeOffset.UtcNow;
        db.Stamdata.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/stamdata/{dto.Id}", dto);
    }

    [HttpDelete("{id:guid}"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var s = await db.Stamdata.FindAsync(id);
        if (s is null) return NotFound();
        db.Stamdata.Remove(s); await db.SaveChangesAsync();
        return NoContent();
    }
}

[ApiController, Authorize, Route("v1/skabeloner")]
public class SkabelonerController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List() =>
        Ok(await db.Skabeloner.OrderBy(s => s.Navn).ToListAsync());

    [HttpPost]
    public async Task<IActionResult> Create(BeskedSkabelon dto)
    {
        dto.Id = Guid.NewGuid(); dto.CreatedAt = DateTimeOffset.UtcNow;
        db.Skabeloner.Add(dto); await db.SaveChangesAsync();
        return Created($"/v1/skabeloner/{dto.Id}", dto);
    }

    [HttpPatch("{id:guid}")]
    public async Task<IActionResult> Update(Guid id, BeskedSkabelon dto)
    {
        var s = await db.Skabeloner.FindAsync(id);
        if (s is null) return NotFound();
        s.Navn = dto.Navn;
        s.Indhold = dto.Indhold;
        await db.SaveChangesAsync();
        return Ok(s);
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var s = await db.Skabeloner.FindAsync(id);
        if (s is null) return NotFound();
        db.Skabeloner.Remove(s); await db.SaveChangesAsync();
        return NoContent();
    }
}

// Bankoplysninger — kontonr. maskeres altid udad; kryptering server-side (TODO).
public record UdlaegKontoInputDto(string? RegNr, string? KontoNr, string? Iban);
public record UdlaegKontoReadDto(Guid Id, Guid BrobyggerId, string? RegNr, string? Iban, bool HarKontoNr, string? KontoNrMaske);

// Bankoplysninger: KUN "Oekonomi"-rollen — ikke synligt for rådgivere, brobyggere eller øvrige admins.
[ApiController, Authorize(Roles = "Oekonomi"), Route("v1/brobyggere/{brobyggerId:guid}/udlaeg-konto")]
public class UdlaegKontoController(BrobyggerDbContext db, BrobyggerPortal.Api.Services.CryptoService crypto) : ControllerBase
{
    private UdlaegKontoReadDto Mask(UdlaegKonto k)
    {
        var nr = crypto.DecryptBank(k.KontoNrEnc);
        var maske = nr is { Length: >= 4 } ? "••••" + nr[^4..] : null;
        return new(k.Id, k.BrobyggerId, k.RegNr, k.Iban, k.KontoNrEnc is not null, maske);
    }

    [HttpGet]
    public async Task<IActionResult> Get(Guid brobyggerId)
    {
        var k = await db.UdlaegKonti.FirstOrDefaultAsync(x => x.BrobyggerId == brobyggerId);
        return k is null ? NotFound() : Ok(Mask(k));
    }

    [HttpPut]
    public async Task<IActionResult> Upsert(Guid brobyggerId, UdlaegKontoInputDto dto)
    {
        var k = await db.UdlaegKonti.FirstOrDefaultAsync(x => x.BrobyggerId == brobyggerId);
        if (k is null) { k = new UdlaegKonto { BrobyggerId = brobyggerId }; db.UdlaegKonti.Add(k); }
        k.RegNr = dto.RegNr;
        k.Iban = dto.Iban;
        if (dto.KontoNr is not null) k.KontoNrEnc = crypto.EncryptBank(dto.KontoNr);  // krypteret, aldrig klartekst
        k.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return Ok(Mask(k));
    }
}

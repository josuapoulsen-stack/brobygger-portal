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
public class AftalerController(BrobyggerDbContext db, BrobyggerPortal.Api.Services.NotifikationService notif) : ControllerBase
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

    [HttpGet("eksport"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> Eksport()
    {
        var aftaler = await db.Aftaler.OrderByDescending(a => a.Dato).ToListAsync();
        var mennesker = await db.Mennesker.ToDictionaryAsync(m => m.Id, m => m.Navn);
        var brobyggere = await db.Brobyggere.ToDictionaryAsync(b => b.Id, b => b.Navn);

        var sb = new System.Text.StringBuilder();
        sb.AppendLine("dato;menneske;brobygger;status;type;brobygningstype;sted;udfald");
        foreach (var a in aftaler)
        {
            var mn = mennesker.GetValueOrDefault(a.MenneskeId, "");
            var bb = a.BrobyggerId is Guid bid && brobyggere.TryGetValue(bid, out var n) ? n : "";
            sb.AppendLine($"{a.Dato:yyyy-MM-dd HH:mm};{Csv(mn)};{Csv(bb)};{a.Status};{a.Type};{Csv(a.Brobygningstype)};{Csv(a.Sted)};{Csv(a.Udfald)}");
        }
        return File(System.Text.Encoding.UTF8.GetBytes(sb.ToString()), "text/csv; charset=utf-8", "aftaler.csv");
    }

    private static string Csv(string? s) => s is null ? "" : "\"" + s.Replace("\"", "\"\"") + "\"";

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
        if (await db.Mennesker.FindAsync(dto.MenneskeId) is null) return NotFound("Menneske ikke fundet");
        if (dto.BrobyggerId is Guid bid)
        {
            var brobygger = await db.Brobyggere.FindAsync(bid);
            if (brobygger is null) return NotFound("Brobygger ikke fundet");
            if (AktiveStatus.Contains(dto.Status) && brobygger.Active >= brobygger.MaxActive)
                return Conflict("Brobygger har ikke kapacitet");

            // Dobbeltbookings-tjek: overlappende tidsrum for samme brobygger
            var nySlut = dto.Dato.AddMinutes(dto.Varighed);
            var optaget = await db.Aftaler
                .Where(x => x.BrobyggerId == bid && x.Status != AftaleStatus.Aflyst && x.Status != AftaleStatus.Afslaaet)
                .ToListAsync();
            if (optaget.Any(x => x.Dato < nySlut && dto.Dato < x.Dato.AddMinutes(x.Varighed)))
                return Conflict("Brobygger har allerede en aftale i det tidsrum");
        }

        var a = new Aftale
        {
            BrobyggerId = dto.BrobyggerId, MenneskeId = dto.MenneskeId, Dato = dto.Dato, Slut = dto.Slut,
            Varighed = dto.Varighed, Type = dto.Type, Sted = dto.Sted, Beskrivelse = dto.Beskrivelse,
            Status = dto.Status, Notes = dto.Notes, EfterspurgtAt = dto.EfterspurgtAt ?? DateTimeOffset.UtcNow,
            BekraeftetAt = dto.Status == AftaleStatus.Confirmed ? DateTimeOffset.UtcNow : null,
            BrobyggerTildeltAt = dto.BrobyggerId is not null ? DateTimeOffset.UtcNow : null,
            Aftaletype = dto.Aftaletype,
            Brobygningstype = dto.Brobygningstype, Titel = dto.Titel, Programtype = dto.Programtype,
            Indsatstype = dto.Indsatstype, Samarbejdskommune = dto.Samarbejdskommune, Samarbejdshospital = dto.Samarbejdshospital,
            HenvenderKonkret = dto.HenvenderKonkret, ModtagerKonkret = dto.ModtagerKonkret,
            GentagelserAntal = dto.GentagelserAntal, DageImellem = dto.DageImellem,
            Henvender = dto.Henvender, Modtager = dto.Modtager,
            Finansiering = dto.Finansiering, Samarbejdspartner = dto.Samarbejdspartner, Afdeling = dto.Afdeling,
            Transportplan = dto.Transportplan, AktivitetsTid = dto.AktivitetsTid, FremmoedeType = dto.FremmoedeType,
            Gentagelse = dto.Gentagelse, AftaleForm = dto.AftaleForm, BrobyggerNote = dto.BrobyggerNote,
            RaadgiverOpfoelgning = dto.RaadgiverOpfoelgning,
        };
        db.Aftaler.Add(a);
        await db.SaveChangesAsync();

        // Besked fra skabelon/oprettelse lægges som første besked i aftalens tråd
        if (!string.IsNullOrWhiteSpace(dto.Beskrivelse))
        {
            db.Beskeder.Add(new Besked { AftaleId = a.Id, Afsender = User.Identity?.Name ?? "Koordinator", Tekst = dto.Beskrivelse! });
            await db.SaveChangesAsync();
        }

        await notif.PushAsync("ny_aftale", "Ny aftale efterspurgt", $"/aftaler/{a.Id}");
        return CreatedAtAction(nameof(Get), new { id = a.Id }, AftaleReadDto.From(a));
    }

    [HttpPatch("{id:guid}")]
    public async Task<ActionResult<AftaleReadDto>> Update(Guid id, AftaleUpdateDto dto)
    {
        var a = await db.Aftaler.FindAsync(id);
        if (a is null) return NotFound();
        if (dto.BrobyggerId is not null && a.BrobyggerId != dto.BrobyggerId)
        {
            a.BrobyggerId = dto.BrobyggerId;
            a.BrobyggerTildeltAt = DateTimeOffset.UtcNow;
        }
        if (dto.Dato is not null) a.Dato = dto.Dato.Value;
        if (dto.Slut is not null) a.Slut = dto.Slut;
        if (dto.Varighed is not null) a.Varighed = dto.Varighed.Value;
        if (dto.Type is not null) a.Type = dto.Type.Value;
        if (dto.Sted is not null) a.Sted = dto.Sted;
        if (dto.Beskrivelse is not null) a.Beskrivelse = dto.Beskrivelse;
        if (dto.Brobygningstype is not null) a.Brobygningstype = dto.Brobygningstype;
        a.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return AftaleReadDto.From(a);
    }

    public record AftaleLogDto(string Udfald, int? VarighedMin, string? LogNote);

    // Brobygger-log: registrér udfald af afholdt aftale (gennemfoert|afbud|ikke-modt).
    [HttpPost("{id:guid}/log")]
    public async Task<ActionResult<AftaleReadDto>> Log(Guid id, AftaleLogDto dto)
    {
        var a = await db.Aftaler.FindAsync(id);
        if (a is null) return NotFound();
        a.Udfald = dto.Udfald;
        a.VarighedMin = dto.VarighedMin;
        a.LogNote = dto.LogNote;
        a.LoggedAt = DateTimeOffset.UtcNow;
        if (dto.Udfald == "gennemfoert") a.Status = AftaleStatus.Gennemfoert;
        a.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return AftaleReadDto.From(a);
    }

    [HttpPatch("{id:guid}/status")]
    public async Task<ActionResult<AftaleReadDto>> UpdateStatus(Guid id, AftaleStatusUpdateDto dto)
    {
        var a = await db.Aftaler.FindAsync(id);
        if (a is null) return NotFound();
        a.Status = dto.Status;
        if (!string.IsNullOrEmpty(dto.Notes)) a.Notes = dto.Notes;
        // Registrér bekræftelsestidspunktet første gang aftalen bekræftes
        if (dto.Status == AftaleStatus.Confirmed && a.BekraeftetAt is null)
            a.BekraeftetAt = DateTimeOffset.UtcNow;
        a.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        if (dto.Status == AftaleStatus.Confirmed)
            await notif.PushAsync("aftale_godkendt", "Aftale bekræftet", $"/aftaler/{a.Id}");
        return AftaleReadDto.From(a);
    }
}

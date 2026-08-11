using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Dtos;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Indsigtsret (GDPR art. 15): samlet udtræk af alt registreret om en person.
// Kun Admin/Rådgiver. Udtræk logges (revisionsspor). Følsom læsning — helbred inkluderes,
// da personen har ret til indsigt i egne data.
[ApiController, Authorize(Roles = "Admin,Raadgiver"), Route("v1/mennesker/{menneskeId:guid}/gdpr-rapport")]
public class GdprController(BrobyggerDbContext db, CryptoService crypto, ILogger<GdprController> log) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Rapport(Guid menneskeId)
    {
        var m = await db.Mennesker.FindAsync(menneskeId);
        if (m is null) return NotFound();

        log.LogInformation("GDPR-indsigtsrapport udtrukket for menneske {Id} af {Bruger}",
            menneskeId, User.Identity?.Name ?? "ukendt");

        var henvendelser = await db.Henvendelser.Where(h => h.MenneskeId == menneskeId).OrderBy(h => h.Dato).ToListAsync();
        var maalinger = await db.Trivselsmaalinger.Where(x => x.MenneskeId == menneskeId).OrderBy(x => x.Dato).ToListAsync();
        var kontaktpersoner = await db.Kontaktpersoner.Where(k => k.MenneskeId == menneskeId).ToListAsync();
        var aftaler = await db.Aftaler.Where(a => a.MenneskeId == menneskeId).OrderByDescending(a => a.Dato).ToListAsync();

        return Ok(new
        {
            menneske = MenneskeReadDto.From(m),
            helbredsnoter = crypto.DecryptHealth(m.HelbredsnoterEnc),
            henvendelser,
            maalinger,
            kontaktpersoner,
            aftaler = aftaler.Select(AftaleReadDto.From),
            udtrukket = DateTimeOffset.UtcNow,
        });
    }
}

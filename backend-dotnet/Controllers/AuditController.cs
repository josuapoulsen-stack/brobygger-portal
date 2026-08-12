using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Revisionsspor — kun Admin. Viser hvem der har trukket følsomme data/handlinger.
[ApiController, Authorize(Roles = "Admin"), Route("v1/audit")]
public class AuditController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List([FromQuery] Guid? maalId) =>
        Ok(await db.Auditlog
            .Where(x => maalId == null || x.MaalId == maalId)
            .OrderByDescending(x => x.Tidspunkt)
            .Take(200)
            .ToListAsync());
}

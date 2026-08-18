using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

// Områdestruktur til scope-filteret: hovedsæder og deres lokalafdelinger,
// udledt af de faktiske data (mennesker + brobyggere).
[ApiController, Authorize, Route("v1/omraader")]
public class OmraaderController(BrobyggerDbContext db) : ControllerBase
{
    public record Omraade(string Hovedsaede, List<string> Afdelinger);

    [HttpGet]
    public async Task<ActionResult<IEnumerable<Omraade>>> Get()
    {
        var m = await db.Mennesker.Where(x => x.DeletedAt == null)
            .Select(x => new { x.Hq, x.Afdeling }).ToListAsync();
        var b = await db.Brobyggere.Select(x => new { x.Hq, x.Afdeling }).ToListAsync();

        var omraader = m.Concat(b)
            .Where(x => !string.IsNullOrWhiteSpace(x.Hq))
            .GroupBy(x => x.Hq!)
            .OrderBy(g => g.Key)
            .Select(g => new Omraade(
                g.Key,
                g.Select(x => x.Afdeling)
                 .Where(a => !string.IsNullOrWhiteSpace(a))
                 .Select(a => a!)
                 .Distinct()
                 .OrderBy(a => a)
                 .ToList()))
            .ToList();

        return Ok(omraader);
    }
}

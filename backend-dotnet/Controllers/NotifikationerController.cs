using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController, Authorize, Route("v1/notifikationer")]
public class NotifikationerController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> List() =>
        Ok(await db.Notifikationer.OrderByDescending(n => n.Tidspunkt).Take(50).ToListAsync());

    [HttpPost("{id:guid}/laest")]
    public async Task<IActionResult> Laest(Guid id)
    {
        var n = await db.Notifikationer.FindAsync(id);
        if (n is null) return NotFound();
        n.Laest = true;
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpPost("laes-alle")]
    public async Task<IActionResult> LaesAlle()
    {
        await db.Notifikationer.Where(n => !n.Laest).ExecuteUpdateAsync(s => s.SetProperty(n => n.Laest, true));
        return NoContent();
    }
}

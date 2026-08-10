using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BrobyggerPortal.Api.Controllers;

[ApiController, Authorize, Route("v1/graph")]
public class GraphController(GraphService graph, BrobyggerDbContext db) : ControllerBase
{
    public record TestMailDto(string From, string[] To, string Subject, string Body);

    [HttpPost("test-mail"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> TestMail(TestMailDto dto)
    {
        if (!graph.Enabled) return StatusCode(503, "Graph er ikke konfigureret");
        await graph.SendMailAsync(dto.From, dto.To, dto.Subject, dto.Body);
        return Accepted();
    }

    /// <summary>Opret en Outlook-kalenderaftale for en aftale i en given brugers kalender.</summary>
    [HttpPost("/v1/aftaler/{aftaleId:guid}/kalender"), Authorize(Roles = "Admin,Raadgiver")]
    public async Task<IActionResult> KalenderFraAftale(Guid aftaleId, [FromQuery] string userId)
    {
        if (!graph.Enabled) return StatusCode(503, "Graph er ikke konfigureret");
        var a = await db.Aftaler.FindAsync(aftaleId);
        if (a is null) return NotFound();

        var eventId = await graph.CreateEventAsync(
            userId,
            subject: $"Brobygger-aftale ({a.Type})",
            start: a.Dato,
            end: a.Dato.AddMinutes(a.Varighed),
            location: a.Sted,
            bodyHtml: a.Beskrivelse ?? a.BrobyggerNote);

        return Ok(new { event_id = eventId });
    }
}

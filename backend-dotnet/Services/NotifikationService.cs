using System.Text.Json;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;

namespace BrobyggerPortal.Api.Services;

// Opretter en notifikation (persisteret) og publicerer den til alle SSE-forbindelser.
public class NotifikationService(BrobyggerDbContext db, EventBroker broker)
{
    public async Task PushAsync(string type, string tekst, string? link = null)
    {
        var n = new Notifikation { Type = type, Tekst = tekst, Link = link };
        db.Notifikationer.Add(n);
        await db.SaveChangesAsync();
        broker.Publish(JsonSerializer.Serialize(new { id = n.Id, type, tekst, link, tidspunkt = n.Tidspunkt }));
    }
}

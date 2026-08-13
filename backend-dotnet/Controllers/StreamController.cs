using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace BrobyggerPortal.Api.Controllers;

// Server-Sent Events: én langtidslevende HTTP-forbindelse der pusher notifikationer i realtid.
// Frontend forbinder med EventSource. (Token via query, da EventSource ikke kan sætte headers —
// tilføjes når rigtig auth er live; nu er dev-token nok.)
[ApiController, Authorize, Route("v1/stream")]
public class StreamController(EventBroker broker) : ControllerBase
{
    [HttpGet]
    public async Task Get(CancellationToken ct)
    {
        Response.Headers.Append("Content-Type", "text/event-stream");
        Response.Headers.Append("Cache-Control", "no-cache");
        Response.Headers.Append("Connection", "keep-alive");

        var (id, reader) = broker.Subscribe();
        try
        {
            await Response.WriteAsync(": forbundet\n\n", ct);
            await Response.Body.FlushAsync(ct);
            await foreach (var msg in reader.ReadAllAsync(ct))
            {
                await Response.WriteAsync($"data: {msg}\n\n", ct);
                await Response.Body.FlushAsync(ct);
            }
        }
        catch (OperationCanceledException) { /* klienten lukkede */ }
        finally { broker.Unsubscribe(id); }
    }
}

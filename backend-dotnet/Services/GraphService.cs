using System.Net.Http.Headers;
using System.Net.Http.Json;
using Azure.Core;
using Azure.Identity;

namespace BrobyggerPortal.Api.Services;

/// <summary>
/// Microsoft Graph-integration: send mail + opret Outlook-kalenderaftaler.
/// Token hentes app-only via Azure.Identity; selve kaldene går via REST (stabilt
/// på tværs af Graph-versioner). Aktiveres når "Graph" er konfigureret.
///
/// Konfiguration (appsettings/Key Vault):
///   Graph:Enabled = true
///   Graph:TenantId, Graph:ClientId, Graph:ClientSecret   (lokalt/CI)
///   — i Azure kan Managed Identity bruges i stedet (udelad ClientSecret)
/// Kræver Graph-app-tilladelser: Mail.Send, Calendars.ReadWrite (application).
/// </summary>
public class GraphService
{
    private static readonly HttpClient Http = new() { BaseAddress = new Uri("https://graph.microsoft.com/v1.0/") };
    private readonly TokenCredential? _cred;

    public bool Enabled { get; }

    public GraphService(IConfiguration config)
    {
        Enabled = string.Equals(config["Graph:Enabled"], "true", StringComparison.OrdinalIgnoreCase);
        if (!Enabled) return;

        var tenant = config["Graph:TenantId"];
        var client = config["Graph:ClientId"];
        var secret = config["Graph:ClientSecret"];
        _cred = !string.IsNullOrEmpty(secret) && !string.IsNullOrEmpty(tenant) && !string.IsNullOrEmpty(client)
            ? new ClientSecretCredential(tenant, client, secret)
            : new DefaultAzureCredential(); // Managed Identity i Azure
    }

    private async Task<string> TokenAsync(CancellationToken ct)
    {
        var token = await _cred!.GetTokenAsync(
            new TokenRequestContext(["https://graph.microsoft.com/.default"]), ct);
        return token.Token;
    }

    private async Task<HttpResponseMessage> PostAsync(string path, object body, CancellationToken ct)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(body) };
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", await TokenAsync(ct));
        return await Http.SendAsync(req, ct);
    }

    /// <summary>Send mail som en given afsender (bruger-id eller UPN).</summary>
    public async Task SendMailAsync(string fromUserId, IEnumerable<string> to, string subject, string html, CancellationToken ct = default)
    {
        var body = new
        {
            message = new
            {
                subject,
                body = new { contentType = "HTML", content = html },
                toRecipients = to.Select(a => new { emailAddress = new { address = a } }),
            },
            saveToSentItems = true,
        };
        var resp = await PostAsync($"users/{Uri.EscapeDataString(fromUserId)}/sendMail", body, ct);
        resp.EnsureSuccessStatusCode();
    }

    /// <summary>Opret en Outlook-kalenderaftale i en brugers kalender. Returnerer event-id.</summary>
    public async Task<string?> CreateEventAsync(
        string userId, string subject, DateTimeOffset start, DateTimeOffset end,
        string? location = null, string? bodyHtml = null, CancellationToken ct = default)
    {
        var body = new
        {
            subject,
            body = new { contentType = "HTML", content = bodyHtml ?? "" },
            start = new { dateTime = start.ToString("yyyy-MM-ddTHH:mm:ss"), timeZone = "Europe/Copenhagen" },
            end = new { dateTime = end.ToString("yyyy-MM-ddTHH:mm:ss"), timeZone = "Europe/Copenhagen" },
            location = new { displayName = location ?? "" },
        };
        var resp = await PostAsync($"users/{Uri.EscapeDataString(userId)}/events", body, ct);
        resp.EnsureSuccessStatusCode();
        var created = await resp.Content.ReadFromJsonAsync<Dictionary<string, object>>(cancellationToken: ct);
        return created is not null && created.TryGetValue("id", out var id) ? id?.ToString() : null;
    }
}

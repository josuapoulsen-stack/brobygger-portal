using BrobyggerPortal.Web;
using BrobyggerPortal.Web.Services;
using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Authentication;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

var apiBase = builder.Configuration["ApiBaseUrl"] ?? "http://localhost:5080";
var clientId = builder.Configuration["AzureAd:ClientId"];
var entraConfigured = !string.IsNullOrWhiteSpace(clientId) && !clientId!.StartsWith("TODO");

builder.Services.AddScoped<ScopeState>();

if (entraConfigured)
{
    // Produktion: ægte Microsoft-login via MSAL + Entra-token på API-kald.
    builder.Services.AddMsalAuthentication(options =>
    {
        builder.Configuration.Bind("AzureAd", options.ProviderOptions.Authentication);
        var scope = builder.Configuration["AzureAd:ApiScope"];
        if (!string.IsNullOrWhiteSpace(scope)) options.ProviderOptions.DefaultAccessTokenScopes.Add(scope);
    });
    builder.Services.AddScoped<ApiAuthHandler>();
    builder.Services.AddHttpClient<ApiClient>(c => c.BaseAddress = new Uri(apiBase))
        .AddHttpMessageHandler<ApiAuthHandler>();
}
else
{
    // Lokal udvikling: ingen tenant → dev-token + "logget ind"-dev-bruger.
    builder.Services.AddScoped(_ => new HttpClient { BaseAddress = new Uri(apiBase) });
    builder.Services.AddScoped<ApiClient>();
    builder.Services.AddAuthorizationCore();
    builder.Services.AddScoped<AuthenticationStateProvider, DevAuthStateProvider>();
}

builder.Services.AddSingleton(new AuthMode(entraConfigured));

await builder.Build().RunAsync();

/// <summary>Injiceres i ApiClient så den ved om ægte Entra er aktiv (styrer dev-login).</summary>
public record AuthMode(bool EntraConfigured);

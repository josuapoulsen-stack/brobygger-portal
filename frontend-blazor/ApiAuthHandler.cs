using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.WebAssembly.Authentication;

namespace BrobyggerPortal.Web;

/// <summary>
/// Vedhæfter Entra-access-token på kald til API'et (som ligger på en anden origin).
/// Bruges kun når Entra er konfigureret (MSAL-tilstand).
/// </summary>
public class ApiAuthHandler : AuthorizationMessageHandler
{
    public ApiAuthHandler(IAccessTokenProvider provider, NavigationManager navigation, IConfiguration cfg)
        : base(provider, navigation)
    {
        ConfigureHandler(
            authorizedUrls: [cfg["ApiBaseUrl"] ?? "http://localhost:5080"],
            scopes: [cfg["AzureAd:ApiScope"] ?? ""]);
    }
}

using System.Security.Claims;
using Microsoft.AspNetCore.Components.Authorization;

namespace BrobyggerPortal.Web;

/// <summary>
/// Dev-auth: giver en "logget ind"-bruger med alle roller, når Entra IKKE er konfigureret,
/// så UI'et virker lokalt uden en tenant. I produktion bruges MSAL i stedet (se Program.cs).
/// </summary>
public class DevAuthStateProvider : AuthenticationStateProvider
{
    public override Task<AuthenticationState> GetAuthenticationStateAsync()
    {
        var claims = new List<Claim>
        {
            new(ClaimTypes.Name, "Dev Bruger"),
            new("roles", "Admin"), new("roles", "Raadgiver"), new("roles", "Oekonomi"),
        };
        var identity = new ClaimsIdentity(claims, authenticationType: "Dev", nameType: ClaimTypes.Name, roleType: "roles");
        return Task.FromResult(new AuthenticationState(new ClaimsPrincipal(identity)));
    }
}

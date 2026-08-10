using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;

namespace BrobyggerPortal.Api.Controllers;

[ApiController]
[Route("v1/auth")]
public class AuthController(IConfiguration config, IWebHostEnvironment env, AuthMode authMode) : ControllerBase
{
    [HttpGet("me")]
    [Authorize]
    public IActionResult Me() => Ok(new
    {
        oid = User.FindFirst("oid")?.Value ?? User.FindFirst(ClaimTypes.NameIdentifier)?.Value,
        name = User.Identity?.Name ?? User.FindFirst("name")?.Value,
        roles = User.FindAll("roles").Select(c => c.Value),
    });

    public record DevTokenRequest(
        string Oid = "dev-00000000-0000-0000-0000-000000000001",
        string Name = "Dev Bruger",
        string[]? Roles = null);

    /// <summary>Dev-only: mint et HS256-testtoken. 404 i produktion OG når Entra er sat op.</summary>
    [HttpPost("dev-token")]
    public IActionResult DevToken(DevTokenRequest req)
    {
        if (env.IsProduction() || authMode.EntraConfigured)
            return NotFound();

        var key = config["Dev:JwtSecret"] ?? "dev-hemmelighed-skift-mig-mindst-32-tegn-lang-noegle";
        var roles = req.Roles ?? ["Admin"];
        var claims = new List<Claim>
        {
            new("oid", req.Oid),
            new("name", req.Name),
        };
        claims.AddRange(roles.Select(r => new Claim("roles", r)));

        var creds = new SigningCredentials(
            new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key)), SecurityAlgorithms.HmacSha256);
        var token = new JwtSecurityToken(
            claims: claims, expires: DateTime.UtcNow.AddHours(8), signingCredentials: creds);

        return Ok(new
        {
            access_token = new JwtSecurityTokenHandler().WriteToken(token),
            token_type = "bearer",
            expires_in = 8 * 3600,
        });
    }
}

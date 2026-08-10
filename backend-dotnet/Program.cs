using System.Text.Json;
using System.Text.Json.Serialization;
using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// ── Database (PostgreSQL via Npgsql) ─────────────────────────────────────────
builder.Services.AddDbContext<BrobyggerDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Postgres")));

// ── Entra ID (Azure AD) JWT-validering ───────────────────────────────────────
// Erstatter den håndlavede RS256/JWKS-kode fra Python-backend'en. Microsoft.Identity.Web
// henter selv JWKS, validerer signatur/issuer/audience og udstiller app-roller som claims.
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();

// ── Controllers + JSON i snake_case (matcher OpenAPI-kontrakten) ─────────────
builder.Services
    .AddControllers()
    .AddJsonOptions(o =>
    {
        o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
        o.JsonSerializerOptions.DictionaryKeyPolicy = JsonNamingPolicy.SnakeCaseLower;
        o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        o.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });

// ── CORS (frontend: Static Web App + lokal dev) ──────────────────────────────
var corsOrigins = builder.Configuration.GetSection("Cors:Origins").Get<string[]>() ?? [];
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.WithOrigins(corsOrigins).AllowAnyHeader().AllowAnyMethod()));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

// Sundhedstjek — offentligt (til Azure App Service probes)
app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.Run();

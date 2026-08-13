using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using BrobyggerPortal.Api.Data;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Identity.Web;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// ── Database (PostgreSQL via Npgsql) ─────────────────────────────────────────
builder.Services.AddDbContext<BrobyggerDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Postgres")));

// ── Auth ─────────────────────────────────────────────────────────────────────
// Entra konfigureret  → ægte RS256/JWKS via Microsoft.Identity.Web (produktion).
// Entra IKKE konfigureret + ikke-produktion → HS256 dev-token (testfase).
// Ikke-produktion-kravet håndhæves: prod uden Entra fejler ved opstart.
var azureAd = builder.Configuration.GetSection("AzureAd");
var entraConfigured =
    !(azureAd["TenantId"]?.StartsWith("TODO") ?? true) &&
    !(azureAd["ClientId"]?.StartsWith("TODO") ?? true);

if (!entraConfigured && builder.Environment.IsProduction())
    throw new InvalidOperationException("Entra ID mangler i produktion — auth ikke konfigureret.");

var authBuilder = builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme);
if (entraConfigured)
{
    authBuilder.AddMicrosoftIdentityWebApi(azureAd);
}
else
{
    var devKey = builder.Configuration["Dev:JwtSecret"]
        ?? "dev-hemmelighed-skift-mig-mindst-32-tegn-lang-noegle";
    authBuilder.AddJwtBearer(o =>
    {
        o.MapInboundClaims = false;   // bevar "roles"-claim som den er, så rolle-tjek virker
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(devKey)),
            RoleClaimType = "roles",
        };
        // SSE: EventSource kan ikke sætte Authorization-header, så token accepteres via ?access_token= på /v1/stream
        o.Events = new JwtBearerEvents
        {
            OnMessageReceived = ctx =>
            {
                var t = ctx.Request.Query["access_token"];
                if (!string.IsNullOrEmpty(t) && ctx.Request.Path.StartsWithSegments("/v1/stream"))
                    ctx.Token = t;
                return Task.CompletedTask;
            },
        };
    });
}

builder.Services.AddAuthorization();
builder.Services.AddSingleton(new AuthMode(entraConfigured));
builder.Services.AddSingleton<BrobyggerPortal.Api.Services.GraphService>();
builder.Services.AddDataProtection();
builder.Services.AddSingleton<BrobyggerPortal.Api.Services.CryptoService>();
builder.Services.AddScoped<BrobyggerPortal.Api.Services.AuditService>();
builder.Services.AddSingleton<BrobyggerPortal.Api.Services.EventBroker>();
builder.Services.AddScoped<BrobyggerPortal.Api.Services.NotifikationService>();

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
builder.Services.AddSwaggerGen(o =>
{
    // "Authorize"-knap i Swagger så man kan sende Bearer-token (fx dev-token) med
    var scheme = new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Reference = new Microsoft.OpenApi.Models.OpenApiReference
        {
            Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme,
            Id = "Bearer",
        },
    };
    o.AddSecurityDefinition("Bearer", scheme);
    o.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement { { scheme, [] } });
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// I dev: ingen https-redirect, så den lokale frontend kan kalde http://localhost:5080 uden cert-bøvl
if (!app.Environment.IsDevelopment())
    app.UseHttpsRedirection();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

// Dev: anvend migrations + seed fiktivt data ved rigtig opstart (ikke under dotnet ef-kommandoer).
// GYLDEN REGEL: kun opdigtet seed — aldrig rigtige borgere.
if (app.Environment.IsDevelopment())
{
    app.Lifetime.ApplicationStarted.Register(() =>
    {
        using var scope = app.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<BrobyggerDbContext>();
        db.Database.Migrate();
        BrobyggerPortal.Api.Data.DbSeeder.SeedAsync(db).GetAwaiter().GetResult();
    });
}

app.Run();

/// <summary>Injiceres i controllers så de ved om ægte Entra er aktiv (bruges af dev-token).</summary>
public record AuthMode(bool EntraConfigured);

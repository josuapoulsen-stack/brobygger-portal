using BrobyggerPortal.Web;
using BrobyggerPortal.Web.Services;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Peger på det lokale .NET-API. På Azure sættes dette til API'ets URL.
builder.Services.AddScoped(_ => new HttpClient { BaseAddress = new Uri("http://localhost:5080") });
builder.Services.AddScoped<ApiClient>();
builder.Services.AddScoped<ScopeState>();

await builder.Build().RunAsync();

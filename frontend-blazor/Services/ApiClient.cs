using System.Net.Http.Json;
using System.Text.Json;

namespace BrobyggerPortal.Web.Services;

public class ApiClient(HttpClient http)
{
    private static readonly JsonSerializerOptions Json =
        new(JsonSerializerDefaults.Web) { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower };

    private bool _loggedIn;

    // Dev-login (indtil Entra/MSAL). Henter et testtoken og sætter Bearer-header.
    public async Task EnsureLoginAsync()
    {
        if (_loggedIn) return;
        var res = await http.PostAsJsonAsync("/v1/auth/dev-token", new { roles = new[] { "Admin" } }, Json);
        res.EnsureSuccessStatusCode();
        var tok = await res.Content.ReadFromJsonAsync<DevToken>(Json);
        http.DefaultRequestHeaders.Authorization = new("Bearer", tok!.AccessToken);
        _loggedIn = true;
    }

    private async Task<List<T>> GetList<T>(string path)
    {
        await EnsureLoginAsync();
        return await http.GetFromJsonAsync<List<T>>(path, Json) ?? [];
    }

    public Task<List<Menneske>> GetMennesker() => GetList<Menneske>("/v1/mennesker");
    public async Task CreateMenneske(MenneskeCreate m) { await EnsureLoginAsync(); (await http.PostAsJsonAsync("/v1/mennesker", m, Json)).EnsureSuccessStatusCode(); }

    public Task<List<Brobygger>> GetBrobyggere() => GetList<Brobygger>("/v1/brobyggere");
    public async Task CreateBrobygger(BrobyggerCreate b) { await EnsureLoginAsync(); (await http.PostAsJsonAsync("/v1/brobyggere", b, Json)).EnsureSuccessStatusCode(); }

    public Task<List<Aftale>> GetAftaler() => GetList<Aftale>("/v1/aftaler");
    public async Task CreateAftale(AftaleCreate a) { await EnsureLoginAsync(); (await http.PostAsJsonAsync("/v1/aftaler", a, Json)).EnsureSuccessStatusCode(); }
    public async Task BekraeftAftale(Guid id) { await EnsureLoginAsync(); (await http.PatchAsJsonAsync($"/v1/aftaler/{id}/status", new { status = "confirmed", notes = "" }, Json)).EnsureSuccessStatusCode(); }

    private class DevToken { public string AccessToken { get; set; } = ""; }
}

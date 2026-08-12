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
        // Dev: giv testbrugeren alle roller, så alle skærme kan afprøves. I produktion styrer Entra rollerne.
        var res = await http.PostAsJsonAsync("/v1/auth/dev-token", new { roles = new[] { "Admin", "Raadgiver", "Oekonomi" } }, Json);
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
    public async Task<Brobygger?> GetBrobygger(Guid id) { await EnsureLoginAsync(); return await http.GetFromJsonAsync<Brobygger>($"/v1/brobyggere/{id}", Json); }
    public Task<List<Aftale>> GetAftalerForBrobygger(Guid id) => GetList<Aftale>($"/v1/aftaler?brobyggerId={id}");
    public async Task<UdlaegKonto?> GetUdlaegKonto(Guid brobyggerId)
    {
        await EnsureLoginAsync();
        var r = await http.GetAsync($"/v1/brobyggere/{brobyggerId}/udlaeg-konto");
        if (r.StatusCode == System.Net.HttpStatusCode.NotFound) return null;
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<UdlaegKonto>(Json);
    }
    public async Task<UdlaegKonto?> PutUdlaegKonto(Guid brobyggerId, UdlaegKontoInput dto)
    {
        await EnsureLoginAsync();
        var r = await http.PutAsJsonAsync($"/v1/brobyggere/{brobyggerId}/udlaeg-konto", dto, Json);
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<UdlaegKonto>(Json);
    }
    public async Task UpdateMenneske(Guid id, MenneskeUpdate dto) { await EnsureLoginAsync(); (await http.PatchAsJsonAsync($"/v1/mennesker/{id}", dto, Json)).EnsureSuccessStatusCode(); }

    public async Task<GdprRapport?> GetGdprRapport(Guid id) { await EnsureLoginAsync(); return await http.GetFromJsonAsync<GdprRapport>($"/v1/mennesker/{id}/gdpr-rapport", Json); }

    public async Task<StatistikData?> GetStatistik() { await EnsureLoginAsync(); return await http.GetFromJsonAsync<StatistikData>("/v1/statistik", Json); }

    public async Task<string> GetKreditorCsv() { await EnsureLoginAsync(); return await http.GetStringAsync("/v1/udlaeg/eksport"); }

    public Task<List<Skabelon>> GetSkabeloner() => GetList<Skabelon>("/v1/skabeloner");
    public async Task CreateSkabelon(SkabelonCreate s) { await EnsureLoginAsync(); (await http.PostAsJsonAsync("/v1/skabeloner", s, Json)).EnsureSuccessStatusCode(); }
    public async Task UpdateSkabelon(Guid id, SkabelonCreate s) { await EnsureLoginAsync(); (await http.PatchAsJsonAsync($"/v1/skabeloner/{id}", s, Json)).EnsureSuccessStatusCode(); }
    public async Task DeleteSkabelon(Guid id) { await EnsureLoginAsync(); (await http.DeleteAsync($"/v1/skabeloner/{id}")).EnsureSuccessStatusCode(); }
    public async Task CreateBrobygger(BrobyggerCreate b) { await EnsureLoginAsync(); (await http.PostAsJsonAsync("/v1/brobyggere", b, Json)).EnsureSuccessStatusCode(); }

    public async Task<Menneske?> GetMenneske(Guid id) { await EnsureLoginAsync(); return await http.GetFromJsonAsync<Menneske>($"/v1/mennesker/{id}", Json); }

    public Task<List<Henvendelse>> GetHenvendelser(Guid menneskeId) => GetList<Henvendelse>($"/v1/mennesker/{menneskeId}/henvendelser");
    public async Task CreateHenvendelse(Guid menneskeId, HenvendelseCreate h) { await EnsureLoginAsync(); (await http.PostAsJsonAsync($"/v1/mennesker/{menneskeId}/henvendelser", h, Json)).EnsureSuccessStatusCode(); }

    public Task<List<Trivselsmaaling>> GetMaalinger(Guid menneskeId) => GetList<Trivselsmaaling>($"/v1/mennesker/{menneskeId}/maalinger");
    public async Task CreateMaaling(Guid menneskeId, MaalingCreate u) { await EnsureLoginAsync(); (await http.PostAsJsonAsync($"/v1/mennesker/{menneskeId}/maalinger", u, Json)).EnsureSuccessStatusCode(); }

    public Task<List<Kontaktperson>> GetKontaktpersoner(Guid menneskeId) => GetList<Kontaktperson>($"/v1/mennesker/{menneskeId}/kontaktpersoner");
    public async Task CreateKontaktperson(Guid menneskeId, KontaktpersonCreate k) { await EnsureLoginAsync(); (await http.PostAsJsonAsync($"/v1/mennesker/{menneskeId}/kontaktpersoner", k, Json)).EnsureSuccessStatusCode(); }

    public Task<List<Aftale>> GetAftalerForMenneske(Guid menneskeId) => GetList<Aftale>($"/v1/aftaler?menneskeId={menneskeId}");

    public Task<List<Opkald>> GetOpkaldForMenneske(Guid menneskeId) => GetList<Opkald>($"/v1/opkald?menneskeId={menneskeId}");
    public async Task LogOpkald(OpkaldCreate o) { await EnsureLoginAsync(); await EnsureOk(await http.PostAsJsonAsync("/v1/opkald", o, Json)); }

    public async Task<string?> GetHelbredsnoter(Guid menneskeId)
    {
        await EnsureLoginAsync();
        var r = await http.GetFromJsonAsync<HelbredsnoterResp>($"/v1/mennesker/{menneskeId}/helbredsnoter", Json);
        return r?.Helbredsnoter;
    }

    public Task<List<Aftale>> GetAftaler() => GetList<Aftale>("/v1/aftaler");
    public async Task<Aftale?> GetAftale(Guid id) { await EnsureLoginAsync(); return await http.GetFromJsonAsync<Aftale>($"/v1/aftaler/{id}", Json); }
    public Task<List<Besked>> GetBeskeder(Guid aftaleId) => GetList<Besked>($"/v1/aftaler/{aftaleId}/beskeder");
    public async Task CreateBesked(Guid aftaleId, BeskedCreate dto) { await EnsureLoginAsync(); (await http.PostAsJsonAsync($"/v1/aftaler/{aftaleId}/beskeder", dto, Json)).EnsureSuccessStatusCode(); }
    public async Task CreateAftale(AftaleCreate a) { await EnsureLoginAsync(); await EnsureOk(await http.PostAsJsonAsync("/v1/aftaler", a, Json)); }

    // Læser serverens fejltekst med, så fejlbanneret viser den reelle årsag i stedet for en generisk 500.
    private static async Task EnsureOk(HttpResponseMessage r)
    {
        if (r.IsSuccessStatusCode) return;
        var body = await r.Content.ReadAsStringAsync();
        if (body.Length > 400) body = body[..400];
        throw new Exception($"{(int)r.StatusCode}: {body}");
    }
    public async Task SetAftaleStatus(Guid id, string status) { await EnsureLoginAsync(); (await http.PatchAsJsonAsync($"/v1/aftaler/{id}/status", new { status, notes = "" }, Json)).EnsureSuccessStatusCode(); }

    public async Task Match(Guid menneskeId, Guid brobyggerId) { await EnsureLoginAsync(); (await http.PostAsJsonAsync($"/v1/mennesker/{menneskeId}/match", new { brobyggerId }, Json)).EnsureSuccessStatusCode(); }
    public async Task Unmatch(Guid menneskeId) { await EnsureLoginAsync(); (await http.DeleteAsync($"/v1/mennesker/{menneskeId}/match")).EnsureSuccessStatusCode(); }

    private class DevToken { public string AccessToken { get; set; } = ""; }
}

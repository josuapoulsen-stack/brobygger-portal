namespace BrobyggerPortal.Api.Models;

// ── Steder (fra Sundhedsvæsenets Organisationsregister, SOR) ─────────────────
// Kurateret udtræk: sygehus-hierarkiet (Hospital→Afdeling→Afsnit) + udvalgte
// sundhedsenheder. Bruges til at angive korrekt sted for en aftale via autoudfyld.
public class Sted
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string SorId { get; set; } = string.Empty;   // stabil SOR-nøgle
    public string Navn { get; set; } = string.Empty;    // enhedens navn (fx "Øjenafdeling E")
    public string? Type { get; set; }                   // Hospital | Afdeling | Afsnit | sundhedscenter …
    public string? Sygehus { get; set; }                // moder-institution (fx "Rigshospitalet")
    public string? Shak { get; set; }                   // SHAK/sygehus-afdelingskode
    public string? Vej { get; set; }
    public string? Postnr { get; set; }
    public string? By { get; set; }
    public string? Region { get; set; }
    // Fladt søgefelt (lowercased) — hurtig ILIKE-søgning uden at røre flere kolonner
    public string Soegetekst { get; set; } = string.Empty;
}

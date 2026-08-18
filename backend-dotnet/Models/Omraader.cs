namespace BrobyggerPortal.Api.Models;

// ── Områdestruktur (styres af koordinator) ───────────────────────────────────
// Hovedsæde med tilhørende lokalafdelinger. Bruges af scope-filteret og som
// kilde til hovedsæde/afdeling-valg på mennesker og brobyggere.
public class Hovedsaede
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Navn { get; set; } = string.Empty;
    public List<Lokalafdeling> Afdelinger { get; set; } = [];
}

public class Lokalafdeling
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Navn { get; set; } = string.Empty;
    public Guid HovedsaedeId { get; set; }
}

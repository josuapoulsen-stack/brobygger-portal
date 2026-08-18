namespace BrobyggerPortal.Web;

/// <summary>
/// Delt scope-filter: valgt hovedsæde + lokalafdeling. Lister abonnerer på OnChange
/// og filtrerer deres rækker, så koordinatoren kun ser sit område.
/// </summary>
public class ScopeState
{
    public string? Hovedsaede { get; private set; }
    public string? Afdeling { get; private set; }
    public event Action? OnChange;

    public void SetHovedsaede(string? hq)
    {
        Hovedsaede = string.IsNullOrWhiteSpace(hq) ? null : hq;
        Afdeling = null;   // nulstil afdeling når hovedsæde skifter
        OnChange?.Invoke();
    }

    public void SetAfdeling(string? afd)
    {
        Afdeling = string.IsNullOrWhiteSpace(afd) ? null : afd;
        OnChange?.Invoke();
    }

    public bool Aktiv => Hovedsaede is not null || Afdeling is not null;

    /// <summary>True hvis hq/afdeling er inden for det valgte scope (tomt scope = alt).</summary>
    public bool Matcher(string? hq, string? afdeling)
    {
        if (Hovedsaede is not null && !string.Equals(hq, Hovedsaede, StringComparison.OrdinalIgnoreCase)) return false;
        if (Afdeling is not null && !string.Equals(afdeling, Afdeling, StringComparison.OrdinalIgnoreCase)) return false;
        return true;
    }
}

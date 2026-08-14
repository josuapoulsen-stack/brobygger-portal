namespace BrobyggerPortal.Web;

/// <summary>Fælles status→farveklasse for mono-status-labels (.smono). Dækker menneske-, brobygger- og aftalestatusser.</summary>
public static class StatusFarve
{
    public static string Klasse(string? status) => (status ?? "").ToLowerInvariant() switch
    {
        "confirmed" or "matched" or "aktiv" or "gennemfoert" => "gron",
        "pending" or "venteliste" or "planlagt" or "pause" or "udsat" or "kladde" => "gul",
        "aflyst" or "afslaaet" or "brudt" or "inaktiv" or "afsluttet" => "graa",
        _ => "",
    };
}

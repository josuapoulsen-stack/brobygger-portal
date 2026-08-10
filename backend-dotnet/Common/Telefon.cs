using System.Text.RegularExpressions;

namespace BrobyggerPortal.Api.Common;

public static partial class Telefon
{
    [GeneratedRegex(@"\D")]
    private static partial Regex NonDigits();

    /// <summary>Kanonisk dansk telefon: kun cifre, uden +45/0045-landekode. Bruges til genkendelse.</summary>
    public static string? Normaliser(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw)) return null;
        var d = NonDigits().Replace(raw, "");
        if (d.StartsWith("0045")) d = d[4..];
        else if (d.StartsWith("45") && d.Length == 10) d = d[2..];
        return string.IsNullOrEmpty(d) ? null : d;
    }
}

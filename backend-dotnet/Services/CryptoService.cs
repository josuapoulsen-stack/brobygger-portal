using System.Text;
using Microsoft.AspNetCore.DataProtection;

namespace BrobyggerPortal.Api.Services;

/// <summary>
/// Kryptering af følsomme felter (GDPR art. 9 helbred, art. 5/32 bankoplysninger).
/// Bruger ASP.NET Core Data Protection — nøglerne styres af framework'et og kan i Azure
/// persisteres i Key Vault/Blob. Separate "purposes" isolerer helbred fra bank.
/// </summary>
public class CryptoService
{
    private readonly IDataProtector _health;
    private readonly IDataProtector _bank;

    public CryptoService(IDataProtectionProvider provider)
    {
        _health = provider.CreateProtector("brobygger.helbred.v1");
        _bank = provider.CreateProtector("brobygger.bank.v1");
    }

    public byte[]? EncryptHealth(string? s) => s is null ? null : _health.Protect(Encoding.UTF8.GetBytes(s));
    public string? DecryptHealth(byte[]? b) => b is null ? null : Encoding.UTF8.GetString(_health.Unprotect(b));

    public byte[]? EncryptBank(string? s) => string.IsNullOrEmpty(s) ? null : _bank.Protect(Encoding.UTF8.GetBytes(s));
    public string? DecryptBank(byte[]? b) => b is null ? null : Encoding.UTF8.GetString(_bank.Unprotect(b));
}

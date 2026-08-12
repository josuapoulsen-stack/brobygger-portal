using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;

namespace BrobyggerPortal.Api.Services;

// Skriver revisionsspor. Logger KUN metadata (aktør/handling/mål/tid), aldrig indhold.
public class AuditService(BrobyggerDbContext db)
{
    public async Task LogAsync(string handling, string aktoer, string? maalType = null, Guid? maalId = null, string? detalje = null)
    {
        db.Auditlog.Add(new AuditLog
        {
            Handling = handling,
            Aktoer = string.IsNullOrWhiteSpace(aktoer) ? "ukendt" : aktoer,
            MaalType = maalType,
            MaalId = maalId,
            Detalje = detalje,
        });
        await db.SaveChangesAsync();
    }
}

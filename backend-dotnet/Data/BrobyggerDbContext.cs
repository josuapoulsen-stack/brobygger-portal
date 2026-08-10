using BrobyggerPortal.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Data;

public class BrobyggerDbContext(DbContextOptions<BrobyggerDbContext> options) : DbContext(options)
{
    public DbSet<Menneske> Mennesker => Set<Menneske>();
    public DbSet<Brobygger> Brobyggere => Set<Brobygger>();
    public DbSet<Aftale> Aftaler => Set<Aftale>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<Menneske>(e =>
        {
            e.Property(x => x.Status).HasConversion<string>();
            e.Property(x => x.PraeferencerJson).HasColumnType("jsonb");
            e.HasIndex(x => x.TelefonNorm);
        });

        b.Entity<Brobygger>(e =>
        {
            e.Property(x => x.Status).HasConversion<string>();
            e.HasIndex(x => x.TelefonNorm);
        });

        b.Entity<Aftale>(e =>
        {
            e.Property(x => x.Status).HasConversion<string>();
            e.Property(x => x.Type).HasConversion<string>();
            e.HasIndex(x => x.BrobyggerId);
            e.HasIndex(x => x.MenneskeId);
        });
    }
}

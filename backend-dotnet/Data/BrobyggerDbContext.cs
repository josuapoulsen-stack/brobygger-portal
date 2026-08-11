using BrobyggerPortal.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Data;

public class BrobyggerDbContext(DbContextOptions<BrobyggerDbContext> options) : DbContext(options)
{
    public DbSet<Menneske> Mennesker => Set<Menneske>();
    public DbSet<Brobygger> Brobyggere => Set<Brobygger>();
    public DbSet<Aftale> Aftaler => Set<Aftale>();
    public DbSet<Henvendelse> Henvendelser => Set<Henvendelse>();
    public DbSet<Trivselsmaaling> Trivselsmaalinger => Set<Trivselsmaaling>();
    public DbSet<Kontaktperson> Kontaktpersoner => Set<Kontaktperson>();
    public DbSet<Opkald> Opkald => Set<Opkald>();
    public DbSet<Stamdata> Stamdata => Set<Stamdata>();
    public DbSet<BeskedSkabelon> Skabeloner => Set<BeskedSkabelon>();
    public DbSet<UdlaegKonto> UdlaegKonti => Set<UdlaegKonto>();
    public DbSet<Besked> Beskeder => Set<Besked>();

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

        b.Entity<Henvendelse>().HasIndex(x => x.MenneskeId);
        b.Entity<Trivselsmaaling>(e => { e.Property(x => x.Slags).HasConversion<string>(); e.HasIndex(x => x.MenneskeId); });
        b.Entity<Kontaktperson>().HasIndex(x => x.MenneskeId);
        b.Entity<Opkald>(e => { e.Property(x => x.Type).HasConversion<string>(); e.HasIndex(x => x.MenneskeId); e.HasIndex(x => x.BrobyggerId); });
        b.Entity<Stamdata>().HasIndex(x => new { x.Kategori, x.Hovedsaede });
        b.Entity<UdlaegKonto>().HasIndex(x => x.BrobyggerId).IsUnique();
        b.Entity<Besked>().HasIndex(x => x.AftaleId);
    }
}

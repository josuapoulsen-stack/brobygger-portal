using BrobyggerPortal.Api.Common;
using BrobyggerPortal.Api.Controllers;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace BrobyggerPortal.Tests;

public class LogikTests
{
    private static BrobyggerDbContext NyDb()
    {
        var opts = new DbContextOptionsBuilder<BrobyggerDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        return new BrobyggerDbContext(opts);
    }

    private static MenneskerController NyMenneskerCtrl(BrobyggerDbContext db)
    {
        var crypto = new CryptoService(new EphemeralDataProtectionProvider());
        return new MenneskerController(db, crypto, new AuditService(db));
    }

    // ── Telefon.Normaliser ────────────────────────────────────────────────
    [Fact]
    public void Telefon_normaliseres_ens_uanset_mellemrum()
    {
        Assert.Equal(Telefon.Normaliser("71203040"), Telefon.Normaliser("71 20 30 40"));
    }

    // ── Dublet-genkendelse ────────────────────────────────────────────────
    [Fact]
    public async Task Dublet_samme_telefon_giver_hoej_score()
    {
        var db = NyDb();
        db.Mennesker.Add(new Menneske { Navn = "Ahmad Karimi", Telefon = "+45 71 20 30 40", TelefonNorm = Telefon.Normaliser("71203040") });
        await db.SaveChangesAsync();

        var res = await NyMenneskerCtrl(db).MuligeDubletter(navn: null, telefon: "71203040", alder: null);
        var liste = ((res.Result as OkObjectResult)!.Value as IEnumerable<MenneskerController.DuplikatForslag>)!.ToList();

        Assert.Single(liste);
        Assert.Equal("Ahmad Karimi", liste[0].Navn);
        Assert.True(liste[0].Score >= 100, "samme telefon skal give stærkeste signal");
    }

    [Fact]
    public async Task Dublet_fanger_navne_tastefejl()
    {
        var db = NyDb();
        db.Mennesker.Add(new Menneske { Navn = "Ahmad Karimi" });
        await db.SaveChangesAsync();

        var res = await NyMenneskerCtrl(db).MuligeDubletter(navn: "Ahmed Karmi", telefon: null, alder: null);
        var liste = ((res.Result as OkObjectResult)!.Value as IEnumerable<MenneskerController.DuplikatForslag>)!.ToList();

        Assert.Contains(liste, d => d.Navn == "Ahmad Karimi");
    }

    [Fact]
    public async Task Dublet_ingen_falske_positiver()
    {
        var db = NyDb();
        db.Mennesker.Add(new Menneske { Navn = "Ahmad Karimi", TelefonNorm = "71203040" });
        await db.SaveChangesAsync();

        var res = await NyMenneskerCtrl(db).MuligeDubletter(navn: "Sofie Larsen", telefon: "22334455", alder: null);
        var liste = ((res.Result as OkObjectResult)!.Value as IEnumerable<MenneskerController.DuplikatForslag>)!.ToList();

        Assert.Empty(liste);
    }

    // ── Match-forslag ─────────────────────────────────────────────────────
    [Fact]
    public async Task Match_samme_hovedsaede_rangerer_hoejest()
    {
        var db = NyDb();
        var m = new Menneske { Navn = "Borger", Hq = "Nord", Typer = ["en-til-en"], Sprog = ["dansk"] };
        db.Mennesker.Add(m);
        db.Brobyggere.Add(new Brobygger { Navn = "Samme sted", Hq = "Nord", Typer = ["en-til-one"], Sprog = ["dansk"], Status = BrobyggerStatus.Aktiv, Active = 0, MaxActive = 3 });
        db.Brobyggere.Add(new Brobygger { Navn = "Andet sted", Hq = "Syd", Typer = [], Sprog = [], Status = BrobyggerStatus.Aktiv, Active = 0, MaxActive = 3 });
        await db.SaveChangesAsync();

        var res = await new MatchController(db).Forslag(m.Id) as OkObjectResult;
        var liste = (res!.Value as IEnumerable<MatchController.MatchForslag>)!.ToList();

        Assert.NotEmpty(liste);
        Assert.Equal("Samme sted", liste[0].Navn);  // højeste score først
    }

    [Fact]
    public async Task Match_fuld_brobygger_markeres()
    {
        var db = NyDb();
        var m = new Menneske { Navn = "Borger", Hq = "Nord" };
        db.Mennesker.Add(m);
        db.Brobyggere.Add(new Brobygger { Navn = "Fuld", Hq = "Nord", Status = BrobyggerStatus.Aktiv, Active = 3, MaxActive = 3 });
        await db.SaveChangesAsync();

        var res = await new MatchController(db).Forslag(m.Id) as OkObjectResult;
        var liste = (res!.Value as IEnumerable<MatchController.MatchForslag>)!.ToList();

        Assert.Contains(liste, f => f.Navn == "Fuld" && f.Begrundelse.Contains("fuld"));
    }
}

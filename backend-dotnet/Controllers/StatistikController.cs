using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController, Authorize, Route("v1/statistik")]
public class StatistikController(BrobyggerDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> Hent()
    {
        var mennesker = await db.Mennesker.Where(m => m.DeletedAt == null).ToListAsync();
        var brobyggere = await db.Brobyggere.ToListAsync();
        var aftaler = await db.Aftaler.ToListAsync();
        var maalinger = await db.Trivselsmaalinger.ToListAsync();

        return Ok(new
        {
            antalMennesker = mennesker.Count,
            antalBrobyggere = brobyggere.Count,
            ledigKapacitet = brobyggere.Sum(b => Math.Max(0, b.MaxActive - b.Active)),
            antalMaalinger = maalinger.Count,
            menneskerPerStatus = mennesker.GroupBy(m => m.Status.ToString().ToLowerInvariant())
                .Select(g => new { navn = g.Key, antal = g.Count() }).OrderByDescending(x => x.antal),
            aftalerPerStatus = aftaler.GroupBy(a => a.Status.ToString().ToLowerInvariant())
                .Select(g => new { navn = g.Key, antal = g.Count() }).OrderByDescending(x => x.antal),
            menneskerPerHovedsaede = mennesker.Where(m => !string.IsNullOrEmpty(m.Hq))
                .GroupBy(m => m.Hq!).Select(g => new { navn = g.Key, antal = g.Count() }).OrderByDescending(x => x.antal),
            trivselBaselineGns = Gennemsnit(maalinger, UclaSlags.Baseline),
            trivselOpfoelgningGns = Gennemsnit(maalinger, UclaSlags.Opfoelgning),
        });
    }

    private static double? Gennemsnit(List<Trivselsmaaling> ms, UclaSlags slags)
    {
        var xs = ms.Where(m => m.Slags == slags && m.Instrument == "kombineret").Select(m => (double)m.Score).ToList();
        return xs.Count == 0 ? null : Math.Round(xs.Average(), 1);
    }
}

using BrobyggerPortal.Api.Common;
using BrobyggerPortal.Api.Data;
using BrobyggerPortal.Api.Dtos;
using BrobyggerPortal.Api.Models;
using BrobyggerPortal.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BrobyggerPortal.Api.Controllers;

[ApiController]
[Route("v1/mennesker")]
[Authorize]
public class MenneskerController(BrobyggerDbContext db, CryptoService crypto, AuditService audit) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<MenneskeReadDto>>> List(
        [FromQuery] MenneskeStatus? status, [FromQuery] string? hq)
    {
        var q = db.Mennesker.Where(m => m.DeletedAt == null);
        if (status is not null) q = q.Where(m => m.Status == status);
        if (!string.IsNullOrEmpty(hq)) q = q.Where(m => m.Hq == hq);
        var rows = await q.OrderByDescending(m => m.CreatedAt).ToListAsync();
        return Ok(rows.Select(MenneskeReadDto.From));
    }

    public record DuplikatForslag(Guid Id, string Navn, string? Telefon, string? Hq, int? Alder, int Score, string Grund);

    // Dublet-genkendelse: find eksisterende mennesker der ligner det man er ved at oprette.
    // Telefon (normaliseret) er stærkeste signal; ellers navnelighed (inkl. tidligere navne) + alder.
    [HttpGet("mulige-dubletter")]
    public async Task<ActionResult<IEnumerable<DuplikatForslag>>> MuligeDubletter(
        [FromQuery] string? navn, [FromQuery] string? telefon, [FromQuery] int? alder)
    {
        if (string.IsNullOrWhiteSpace(navn) && string.IsNullOrWhiteSpace(telefon))
            return Ok(Array.Empty<DuplikatForslag>());

        var tlf = Telefon.Normaliser(telefon);
        var navnN = FoldNavn(navn);
        var alle = await db.Mennesker.Where(m => m.DeletedAt == null).ToListAsync();

        var forslag = new List<DuplikatForslag>();
        foreach (var m in alle)
        {
            int score = 0;
            var grunde = new List<string>();

            if (!string.IsNullOrEmpty(tlf) && tlf.Length >= 8 && m.TelefonNorm == tlf)
            { score += 100; grunde.Add("samme telefonnummer"); }

            if (!string.IsNullOrEmpty(navnN))
            {
                var navne = new List<string> { m.Navn };
                if (!string.IsNullOrEmpty(m.TidligereNavne))
                    navne.AddRange(m.TidligereNavne.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries));
                double bedste = navne.Select(n => Lighed(navnN, FoldNavn(n))).DefaultIfEmpty(0).Max();
                if (bedste >= 0.90) { score += 60; grunde.Add("næsten identisk navn"); }
                else if (bedste >= 0.78) { score += 35; grunde.Add("lignende navn"); }
            }

            if (alder is int a && m.Alder is int ma && Math.Abs(a - ma) <= 1 && score > 0)
            { score += 10; grunde.Add("samme alder"); }

            if (score >= 35)
                forslag.Add(new DuplikatForslag(m.Id, m.Navn, m.Telefon, m.Hq, m.Alder, score, string.Join(" · ", grunde)));
        }
        return Ok(forslag.OrderByDescending(x => x.Score).ThenBy(x => x.Navn).Take(5));
    }

    // Navn foldet til sammenligning: små bogstaver, diakritik fjernet, ekstra mellemrum væk.
    private static string FoldNavn(string? s)
    {
        if (string.IsNullOrWhiteSpace(s)) return "";
        var lower = s.Trim().ToLowerInvariant()
            .Replace("æ", "ae").Replace("ø", "oe").Replace("å", "aa");
        var norm = lower.Normalize(System.Text.NormalizationForm.FormD);
        var sb = new System.Text.StringBuilder();
        foreach (var c in norm)
            if (System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) != System.Globalization.UnicodeCategory.NonSpacingMark)
                sb.Append(c);
        return string.Join(' ', sb.ToString().Split(' ', StringSplitOptions.RemoveEmptyEntries));
    }

    // Lighed 0..1 baseret på Levenshtein-afstand.
    private static double Lighed(string a, string b)
    {
        if (a.Length == 0 || b.Length == 0) return 0;
        if (a == b) return 1;
        int[] forrige = new int[b.Length + 1];
        int[] aktuel = new int[b.Length + 1];
        for (int j = 0; j <= b.Length; j++) forrige[j] = j;
        for (int i = 1; i <= a.Length; i++)
        {
            aktuel[0] = i;
            for (int j = 1; j <= b.Length; j++)
            {
                int pris = a[i - 1] == b[j - 1] ? 0 : 1;
                aktuel[j] = Math.Min(Math.Min(aktuel[j - 1] + 1, forrige[j] + 1), forrige[j - 1] + pris);
            }
            (forrige, aktuel) = (aktuel, forrige);
        }
        int dist = forrige[b.Length];
        return 1.0 - (double)dist / Math.Max(a.Length, b.Length);
    }

    [HttpGet("eksport"), Authorize(Roles = "Admin")]
    public async Task<IActionResult> Eksport()
    {
        var rows = await db.Mennesker.Where(m => m.DeletedAt == null).OrderBy(m => m.Navn).ToListAsync();
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("navn;alder;koen;telefon;hovedsaede;afdeling;status;kilde;oprettet");
        foreach (var m in rows)
            sb.AppendLine($"{C(m.Navn)};{m.Alder};{C(m.Kon)};{C(m.Telefon)};{C(m.Hq)};{C(m.Afdeling)};{m.Status};{C(m.Kilde)};{m.CreatedAt:yyyy-MM-dd}");
        byte[] csv = [.. System.Text.Encoding.UTF8.GetPreamble(), .. System.Text.Encoding.UTF8.GetBytes(sb.ToString())];
        return File(csv, "text/csv; charset=utf-8", "mennesker.csv");
    }

    private static string C(string? s) => s is null ? "" : "\"" + s.Replace("\"", "\"\"") + "\"";

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<MenneskeReadDto>> Get(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        return MenneskeReadDto.From(m);
    }

    [HttpPost]
    public async Task<ActionResult<MenneskeReadDto>> Create(MenneskeCreateDto dto)
    {
        var m = new Menneske
        {
            Navn = dto.Navn, Alder = dto.Alder, Kon = dto.Kon, Email = dto.Email,
            Telefon = dto.Telefon, Adresse = dto.Adresse, Typer = dto.Typer, Sprog = dto.Sprog,
            Noter = dto.Noter, Status = dto.Status, MatchedWith = dto.MatchedWith,
            RaadgiverId = dto.RaadgiverId, Hq = dto.Hq, Afdeling = dto.Afdeling, Kilde = dto.Kilde,
            Brobygningstype = dto.Brobygningstype, Region = dto.Region, Meetpoint = dto.Meetpoint, SroiMaalgruppe = dto.SroiMaalgruppe,
            HelbredsKategorier = dto.HelbredsKategorier, PraeferencerJson = dto.Praeferencer,
            AfslutTrivsel = dto.AfslutTrivsel, AfslutAarsag = dto.AfslutAarsag, UclaFravalgt = dto.UclaFravalgt,
            TelefonNorm = Telefon.Normaliser(dto.Telefon),
            HelbredsnoterEnc = crypto.EncryptHealth(dto.Helbredsnoter),   // art. 9 — krypteret
        };
        db.Mennesker.Add(m);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(Get), new { id = m.Id }, MenneskeReadDto.From(m));
    }

    [HttpPatch("{id:guid}")]
    public async Task<ActionResult<MenneskeReadDto>> Update(Guid id, MenneskeUpdateDto dto)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();

        if (dto.Navn is not null && dto.Navn != m.Navn)
        {
            // Navnehistorik: gem det gamle navn (telefon er den stabile id)
            m.TidligereNavne = string.IsNullOrEmpty(m.TidligereNavne) ? m.Navn : $"{m.TidligereNavne}, {m.Navn}";
            m.Navn = dto.Navn;
        }
        if (dto.Alder is not null) m.Alder = dto.Alder;
        if (dto.Kon is not null) m.Kon = dto.Kon;
        if (dto.Email is not null) m.Email = dto.Email;
        if (dto.Telefon is not null) { m.Telefon = dto.Telefon; m.TelefonNorm = Telefon.Normaliser(dto.Telefon); }
        if (dto.Adresse is not null) m.Adresse = dto.Adresse;
        if (dto.Typer is not null) m.Typer = dto.Typer;
        if (dto.Sprog is not null) m.Sprog = dto.Sprog;
        if (dto.Noter is not null) m.Noter = dto.Noter;
        if (dto.Status is not null) m.Status = dto.Status.Value;
        if (dto.MatchedWith is not null) m.MatchedWith = dto.MatchedWith;
        if (dto.RaadgiverId is not null) m.RaadgiverId = dto.RaadgiverId;
        if (dto.Hq is not null) m.Hq = dto.Hq;
        if (dto.Afdeling is not null) m.Afdeling = dto.Afdeling;
        if (dto.Kilde is not null) m.Kilde = dto.Kilde;
        if (dto.Region is not null) m.Region = dto.Region;
        if (dto.Brobygningstype is not null) m.Brobygningstype = dto.Brobygningstype;
        if (dto.Meetpoint is not null) m.Meetpoint = dto.Meetpoint;
        if (dto.SroiMaalgruppe is not null) m.SroiMaalgruppe = dto.SroiMaalgruppe;
        if (dto.HelbredsKategorier is not null) m.HelbredsKategorier = dto.HelbredsKategorier;
        if (dto.Praeferencer is not null) m.PraeferencerJson = dto.Praeferencer;
        if (dto.AfslutTrivsel is not null) m.AfslutTrivsel = dto.AfslutTrivsel;
        if (dto.AfslutAarsag is not null) m.AfslutAarsag = dto.AfslutAarsag;
        if (dto.UclaFravalgt is not null) m.UclaFravalgt = dto.UclaFravalgt.Value;
        if (dto.Helbredsnoter is not null) m.HelbredsnoterEnc = crypto.EncryptHealth(dto.Helbredsnoter);

        m.UpdatedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
        return MenneskeReadDto.From(m);
    }

    // Følsom læsning (art. 9): kun Admin/Rådgiver. TODO: log i revisionsspor (aktør/tid/mål-id).
    [HttpGet("{id:guid}/helbredsnoter"), Authorize(Roles = "Admin,Raadgiver")]
    public async Task<IActionResult> Helbredsnoter(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        await audit.LogAsync("helbred_visning", User.Identity?.Name ?? "ukendt", "menneske", id);
        return Ok(new { helbredsnoter = crypto.DecryptHealth(m.HelbredsnoterEnc) });
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var m = await db.Mennesker.FindAsync(id);
        if (m is null || m.DeletedAt is not null) return NotFound();
        // Soft-delete: PII anonymiseres via batch-job efter 30 dage
        m.DeletedAt = DateTimeOffset.UtcNow;
        m.Status = MenneskeStatus.Afsluttet;
        await db.SaveChangesAsync();
        await audit.LogAsync("menneske_slettet", User.Identity?.Name ?? "ukendt", "menneske", id);
        return NoContent();
    }
}

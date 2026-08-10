using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class Init : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Aftaler",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    BrobyggerId = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Dato = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    Varighed = table.Column<int>(type: "integer", nullable: false),
                    Type = table.Column<string>(type: "text", nullable: false),
                    Sted = table.Column<string>(type: "text", nullable: true),
                    Beskrivelse = table.Column<string>(type: "text", nullable: true),
                    Status = table.Column<string>(type: "text", nullable: false),
                    Notes = table.Column<string>(type: "text", nullable: false),
                    EfterspurgtAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    BekraeftetAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    Aftaletype = table.Column<string>(type: "text", nullable: true),
                    Brobygningstype = table.Column<string>(type: "text", nullable: true),
                    Henvender = table.Column<string>(type: "text", nullable: true),
                    Modtager = table.Column<string>(type: "text", nullable: true),
                    Finansiering = table.Column<string>(type: "text", nullable: true),
                    Samarbejdspartner = table.Column<string>(type: "text", nullable: true),
                    Afdeling = table.Column<string>(type: "text", nullable: true),
                    AflystAf = table.Column<string>(type: "text", nullable: true),
                    AflysningsAarsag = table.Column<string>(type: "text", nullable: true),
                    Transportplan = table.Column<string>(type: "text", nullable: true),
                    AktivitetsTid = table.Column<string>(type: "text", nullable: true),
                    FremmoedeType = table.Column<string>(type: "text", nullable: true),
                    Gentagelse = table.Column<string>(type: "text", nullable: true),
                    AftaleForm = table.Column<string>(type: "text", nullable: true),
                    BrobyggerNote = table.Column<string>(type: "text", nullable: true),
                    RaadgiverOpfoelgning = table.Column<string>(type: "text", nullable: true),
                    Udfald = table.Column<string>(type: "text", nullable: true),
                    VarighedMin = table.Column<int>(type: "integer", nullable: true),
                    LogNote = table.Column<string>(type: "text", nullable: true),
                    LoggedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Aftaler", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Brobyggere",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    Email = table.Column<string>(type: "text", nullable: true),
                    Telefon = table.Column<string>(type: "text", nullable: true),
                    TelefonNorm = table.Column<string>(type: "text", nullable: true),
                    Typer = table.Column<List<string>>(type: "text[]", nullable: false),
                    Sprog = table.Column<List<string>>(type: "text[]", nullable: false),
                    Hq = table.Column<string>(type: "text", nullable: true),
                    Afdeling = table.Column<string>(type: "text", nullable: true),
                    Kon = table.Column<string>(type: "text", nullable: true),
                    Bio = table.Column<string>(type: "text", nullable: true),
                    AvatarUrl = table.Column<string>(type: "text", nullable: true),
                    Status = table.Column<string>(type: "text", nullable: false),
                    Active = table.Column<int>(type: "integer", nullable: false),
                    MaxActive = table.Column<int>(type: "integer", nullable: false),
                    TilgaengeligFra = table.Column<DateOnly>(type: "date", nullable: true),
                    NaesteTid = table.Column<string>(type: "text", nullable: true),
                    Startdato = table.Column<DateOnly>(type: "date", nullable: true),
                    SenesteMoede = table.Column<DateOnly>(type: "date", nullable: true),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Brobyggere", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Henvendelser",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Dato = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    Kanal = table.Column<string>(type: "text", nullable: true),
                    Resume = table.Column<string>(type: "text", nullable: true),
                    Foerstegang = table.Column<bool>(type: "boolean", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Henvendelser", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Kontaktpersoner",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    Relation = table.Column<string>(type: "text", nullable: true),
                    Telefon = table.Column<string>(type: "text", nullable: true),
                    Email = table.Column<string>(type: "text", nullable: true),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Kontaktpersoner", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Mennesker",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    Alder = table.Column<int>(type: "integer", nullable: true),
                    Kon = table.Column<string>(type: "text", nullable: true),
                    Email = table.Column<string>(type: "text", nullable: true),
                    Telefon = table.Column<string>(type: "text", nullable: true),
                    TelefonNorm = table.Column<string>(type: "text", nullable: true),
                    Adresse = table.Column<string>(type: "text", nullable: true),
                    Typer = table.Column<List<string>>(type: "text[]", nullable: false),
                    Sprog = table.Column<List<string>>(type: "text[]", nullable: false),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    Status = table.Column<string>(type: "text", nullable: false),
                    MatchedWith = table.Column<Guid>(type: "uuid", nullable: true),
                    RaadgiverId = table.Column<Guid>(type: "uuid", nullable: true),
                    Hq = table.Column<string>(type: "text", nullable: true),
                    Afdeling = table.Column<string>(type: "text", nullable: true),
                    Kilde = table.Column<string>(type: "text", nullable: true),
                    Meetpoint = table.Column<string>(type: "text", nullable: true),
                    SroiMaalgruppe = table.Column<string>(type: "text", nullable: true),
                    HelbredsKategorier = table.Column<List<string>>(type: "text[]", nullable: true),
                    PraeferencerJson = table.Column<string>(type: "jsonb", nullable: true),
                    AfslutTrivsel = table.Column<int>(type: "integer", nullable: true),
                    AfslutAarsag = table.Column<string>(type: "text", nullable: true),
                    UclaFravalgt = table.Column<bool>(type: "boolean", nullable: false),
                    HelbredsnoterEnc = table.Column<byte[]>(type: "bytea", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    DeletedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Mennesker", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Opkald",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: true),
                    BrobyggerId = table.Column<Guid>(type: "uuid", nullable: true),
                    Type = table.Column<string>(type: "text", nullable: false),
                    Retning = table.Column<string>(type: "text", nullable: true),
                    VarighedSek = table.Column<int>(type: "integer", nullable: true),
                    Note = table.Column<string>(type: "text", nullable: true),
                    Tidspunkt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Opkald", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Skabeloner",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    EjerId = table.Column<Guid>(type: "uuid", nullable: true),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    Indhold = table.Column<string>(type: "text", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Skabeloner", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Stamdata",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Kategori = table.Column<string>(type: "text", nullable: false),
                    Vaerdi = table.Column<string>(type: "text", nullable: false),
                    Hovedsaede = table.Column<string>(type: "text", nullable: true),
                    Aktiv = table.Column<bool>(type: "boolean", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Stamdata", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "UclaMaalinger",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Slags = table.Column<string>(type: "text", nullable: false),
                    Score = table.Column<int>(type: "integer", nullable: false),
                    Dato = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UclaMaalinger", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "UdlaegKonti",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    BrobyggerId = table.Column<Guid>(type: "uuid", nullable: false),
                    RegNr = table.Column<string>(type: "text", nullable: true),
                    KontoNrEnc = table.Column<byte[]>(type: "bytea", nullable: true),
                    Iban = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UdlaegKonti", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Aftaler_BrobyggerId",
                table: "Aftaler",
                column: "BrobyggerId");

            migrationBuilder.CreateIndex(
                name: "IX_Aftaler_MenneskeId",
                table: "Aftaler",
                column: "MenneskeId");

            migrationBuilder.CreateIndex(
                name: "IX_Brobyggere_TelefonNorm",
                table: "Brobyggere",
                column: "TelefonNorm");

            migrationBuilder.CreateIndex(
                name: "IX_Henvendelser_MenneskeId",
                table: "Henvendelser",
                column: "MenneskeId");

            migrationBuilder.CreateIndex(
                name: "IX_Kontaktpersoner_MenneskeId",
                table: "Kontaktpersoner",
                column: "MenneskeId");

            migrationBuilder.CreateIndex(
                name: "IX_Mennesker_TelefonNorm",
                table: "Mennesker",
                column: "TelefonNorm");

            migrationBuilder.CreateIndex(
                name: "IX_Opkald_BrobyggerId",
                table: "Opkald",
                column: "BrobyggerId");

            migrationBuilder.CreateIndex(
                name: "IX_Opkald_MenneskeId",
                table: "Opkald",
                column: "MenneskeId");

            migrationBuilder.CreateIndex(
                name: "IX_Stamdata_Kategori_Hovedsaede",
                table: "Stamdata",
                columns: new[] { "Kategori", "Hovedsaede" });

            migrationBuilder.CreateIndex(
                name: "IX_UclaMaalinger_MenneskeId",
                table: "UclaMaalinger",
                column: "MenneskeId");

            migrationBuilder.CreateIndex(
                name: "IX_UdlaegKonti_BrobyggerId",
                table: "UdlaegKonti",
                column: "BrobyggerId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Aftaler");

            migrationBuilder.DropTable(
                name: "Brobyggere");

            migrationBuilder.DropTable(
                name: "Henvendelser");

            migrationBuilder.DropTable(
                name: "Kontaktpersoner");

            migrationBuilder.DropTable(
                name: "Mennesker");

            migrationBuilder.DropTable(
                name: "Opkald");

            migrationBuilder.DropTable(
                name: "Skabeloner");

            migrationBuilder.DropTable(
                name: "Stamdata");

            migrationBuilder.DropTable(
                name: "UclaMaalinger");

            migrationBuilder.DropTable(
                name: "UdlaegKonti");
        }
    }
}

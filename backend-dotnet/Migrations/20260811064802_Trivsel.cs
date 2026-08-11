using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class Trivsel : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "UclaMaalinger");

            migrationBuilder.AddColumn<string>(
                name: "Brobygningstype",
                table: "Mennesker",
                type: "text",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "Trivselsmaalinger",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Instrument = table.Column<string>(type: "text", nullable: false),
                    Slags = table.Column<string>(type: "text", nullable: false),
                    Score = table.Column<int>(type: "integer", nullable: false),
                    Ensom = table.Column<int>(type: "integer", nullable: true),
                    Faellesskab = table.Column<int>(type: "integer", nullable: true),
                    Stoette = table.Column<int>(type: "integer", nullable: true),
                    Hverdag = table.Column<int>(type: "integer", nullable: true),
                    Velbefindende = table.Column<int>(type: "integer", nullable: true),
                    Dato = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Trivselsmaalinger", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Trivselsmaalinger_MenneskeId",
                table: "Trivselsmaalinger",
                column: "MenneskeId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Trivselsmaalinger");

            migrationBuilder.DropColumn(
                name: "Brobygningstype",
                table: "Mennesker");

            migrationBuilder.CreateTable(
                name: "UclaMaalinger",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    Dato = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    MenneskeId = table.Column<Guid>(type: "uuid", nullable: false),
                    Noter = table.Column<string>(type: "text", nullable: true),
                    Score = table.Column<int>(type: "integer", nullable: false),
                    Slags = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UclaMaalinger", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_UclaMaalinger_MenneskeId",
                table: "UclaMaalinger",
                column: "MenneskeId");
        }
    }
}

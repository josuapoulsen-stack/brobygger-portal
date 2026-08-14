using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class SorSteder : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "StedShak",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "StedSorId",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "Steder",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    SorId = table.Column<string>(type: "text", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    Type = table.Column<string>(type: "text", nullable: true),
                    Sygehus = table.Column<string>(type: "text", nullable: true),
                    Shak = table.Column<string>(type: "text", nullable: true),
                    Vej = table.Column<string>(type: "text", nullable: true),
                    Postnr = table.Column<string>(type: "text", nullable: true),
                    By = table.Column<string>(type: "text", nullable: true),
                    Region = table.Column<string>(type: "text", nullable: true),
                    Soegetekst = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Steder", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Steder_Soegetekst",
                table: "Steder",
                column: "Soegetekst");

            migrationBuilder.CreateIndex(
                name: "IX_Steder_SorId",
                table: "Steder",
                column: "SorId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Steder");

            migrationBuilder.DropColumn(
                name: "StedShak",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "StedSorId",
                table: "Aftaler");
        }
    }
}

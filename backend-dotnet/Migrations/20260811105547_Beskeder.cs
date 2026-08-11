using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class Beskeder : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Beskeder",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    AftaleId = table.Column<Guid>(type: "uuid", nullable: false),
                    Afsender = table.Column<string>(type: "text", nullable: false),
                    Tekst = table.Column<string>(type: "text", nullable: false),
                    Tidspunkt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Beskeder", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Beskeder_AftaleId",
                table: "Beskeder",
                column: "AftaleId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Beskeder");
        }
    }
}

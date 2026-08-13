using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class Notifikationer : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Notifikationer",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Type = table.Column<string>(type: "text", nullable: false),
                    Tekst = table.Column<string>(type: "text", nullable: false),
                    Link = table.Column<string>(type: "text", nullable: true),
                    Laest = table.Column<bool>(type: "boolean", nullable: false),
                    Tidspunkt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Notifikationer", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Notifikationer_Tidspunkt",
                table: "Notifikationer",
                column: "Tidspunkt");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Notifikationer");
        }
    }
}

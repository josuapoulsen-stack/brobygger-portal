using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class AuditLog : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Auditlog",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Handling = table.Column<string>(type: "text", nullable: false),
                    MaalType = table.Column<string>(type: "text", nullable: true),
                    MaalId = table.Column<Guid>(type: "uuid", nullable: true),
                    Aktoer = table.Column<string>(type: "text", nullable: false),
                    Detalje = table.Column<string>(type: "text", nullable: true),
                    Tidspunkt = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Auditlog", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Auditlog_Tidspunkt",
                table: "Auditlog",
                column: "Tidspunkt");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Auditlog");
        }
    }
}

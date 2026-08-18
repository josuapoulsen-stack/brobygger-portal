using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class Omraader : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Hovedsaeder",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Hovedsaeder", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Lokalafdelinger",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Navn = table.Column<string>(type: "text", nullable: false),
                    HovedsaedeId = table.Column<Guid>(type: "uuid", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Lokalafdelinger", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Lokalafdelinger_Hovedsaeder_HovedsaedeId",
                        column: x => x.HovedsaedeId,
                        principalTable: "Hovedsaeder",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Lokalafdelinger_HovedsaedeId",
                table: "Lokalafdelinger",
                column: "HovedsaedeId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Lokalafdelinger");

            migrationBuilder.DropTable(
                name: "Hovedsaeder");
        }
    }
}

using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class RegionSlutNavnehistorik : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Region",
                table: "Mennesker",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "TidligereNavne",
                table: "Mennesker",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Region",
                table: "Brobyggere",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "Slut",
                table: "Aftaler",
                type: "timestamp with time zone",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Region",
                table: "Mennesker");

            migrationBuilder.DropColumn(
                name: "TidligereNavne",
                table: "Mennesker");

            migrationBuilder.DropColumn(
                name: "Region",
                table: "Brobyggere");

            migrationBuilder.DropColumn(
                name: "Slut",
                table: "Aftaler");
        }
    }
}

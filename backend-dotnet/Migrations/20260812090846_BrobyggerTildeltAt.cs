using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class BrobyggerTildeltAt : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTimeOffset>(
                name: "BrobyggerTildeltAt",
                table: "Aftaler",
                type: "timestamp with time zone",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "BrobyggerTildeltAt",
                table: "Aftaler");
        }
    }
}

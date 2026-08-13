using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BrobyggerPortal.Api.Migrations
{
    /// <inheritdoc />
    public partial class AftaleFelter : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "DageImellem",
                table: "Aftaler",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "GentagelserAntal",
                table: "Aftaler",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "HenvenderKonkret",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Indsatstype",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ModtagerKonkret",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Programtype",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Samarbejdshospital",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Samarbejdskommune",
                table: "Aftaler",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Titel",
                table: "Aftaler",
                type: "text",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "DageImellem",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "GentagelserAntal",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "HenvenderKonkret",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "Indsatstype",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "ModtagerKonkret",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "Programtype",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "Samarbejdshospital",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "Samarbejdskommune",
                table: "Aftaler");

            migrationBuilder.DropColumn(
                name: "Titel",
                table: "Aftaler");
        }
    }
}

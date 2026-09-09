from django.core.management.base import BaseCommand, CommandError

from apps.registry import services
from apps.registry.import_piles.parser import MissingColumnsError, UnsupportedFileTypeError
from apps.registry.models import Package


class Command(BaseCommand):
    help = "Import piles from a CSV/XLSX file. Dry-run by default — pass --apply to commit."

    def add_arguments(self, parser):
        parser.add_argument("file", help="Path to the .csv or .xlsx file")
        parser.add_argument("--package", required=True, help="Package code, e.g. S-05")
        parser.add_argument(
            "--coordinate-type",
            required=True,
            choices=["design", "as_built"],
            help="'design' creates/updates the pile hierarchy; 'as_built' updates survey coordinates only",
        )
        parser.add_argument(
            "--apply", action="store_true", help="Commit the import. Without this flag, it's a dry run."
        )

    def handle(self, *args, **options):
        try:
            package = Package.objects.get(code=options["package"])
        except Package.DoesNotExist as exc:
            raise CommandError(f"No Package with code={options['package']!r}") from exc

        try:
            with open(options["file"], "rb") as file_obj:
                report = services.import_piles(
                    package=package,
                    coordinate_type=options["coordinate_type"],
                    file_obj=file_obj,
                    filename=options["file"],
                    apply=options["apply"],
                )
        except (MissingColumnsError, UnsupportedFileTypeError) as exc:
            raise CommandError(str(exc)) from exc

        mode = "APPLIED" if not report.dry_run else "DRY RUN"
        self.stdout.write(
            f"{mode}: {report.total_rows} rows — "
            f"created={report.created} updated={report.updated} "
            f"changed={report.changed} errored={report.errored}"
        )

        if report.reparented:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ {len(report.reparented)} pile(s) reparented to a different cap: "
                    f"{', '.join(report.reparented)}"
                )
            )

        for row in report.rows:
            if row.outcome == "error":
                self.stdout.write(
                    self.style.ERROR(
                        f"  row {row.row_number} (pile_no={row.pile_no}): {'; '.join(row.errors)}"
                    )
                )

        if report.errored:
            raise SystemExit(1)

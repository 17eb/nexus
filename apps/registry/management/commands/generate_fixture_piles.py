from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand

from apps.registry import services
from apps.registry.models import Package

FIXTURE_DIR = Path(apps.get_app_config("registry").path) / "fixtures" / "synthetic"


class Command(BaseCommand):
    help = (
        "Loads the synthetic S-05 package (six piers, mixed 4/6/9-pile caps, "
        "one straddle cap, EPSG:3123 coordinates) via the real import path."
    )

    def handle(self, *args, **options):
        package, created = Package.objects.get_or_create(
            code="S-05",
            defaults={
                "name": "SCRP Package 5 (synthetic)",
                "crs_epsg": 3123,
                "chainage_bearing": "180.000",
            },
        )
        if created:
            self.stdout.write(f"Created package {package.code}")
        else:
            self.stdout.write(f"Using existing package {package.code}")

        for coordinate_type, csv_name in [
            ("design", "design_package_s05.csv"),
            ("as_built", "asbuilt_package_s05.csv"),
        ]:
            path = FIXTURE_DIR / csv_name
            with open(path, "rb") as file_obj:
                report = services.import_piles(
                    package=package,
                    coordinate_type=coordinate_type,
                    file_obj=file_obj,
                    filename=csv_name,
                    apply=True,
                )
            self.stdout.write(
                f"{coordinate_type}: {report.total_rows} rows — "
                f"created={report.created} updated={report.updated} "
                f"changed={report.changed} errored={report.errored}"
            )
            if report.errored:
                for row in report.rows:
                    if row.outcome == "error":
                        self.stdout.write(
                            self.style.ERROR(f"  row {row.row_number}: {'; '.join(row.errors)}")
                        )

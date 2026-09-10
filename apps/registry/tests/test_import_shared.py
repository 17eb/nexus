
import pytest

from apps.registry import services
from apps.registry.factories import PackageFactory
from apps.registry.import_piles.parser import MissingColumnsError
from apps.registry.models import Pile

from .helpers import (
    ASBUILT_HEADERS,
    DESIGN_HEADERS,
    asbuilt_row,
    design_row,
    make_csv_bytes,
    make_xlsx_bytes,
)

pytestmark = pytest.mark.django_db


def test_design_never_writes_asbuilt_fields():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="design.csv",
        apply=True,
    )
    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1")]),
        filename="asbuilt.csv",
        apply=True,
    )
    before = Pile.objects.get(pile_no="P-1")

    # re-run design with a changed easting; asbuilt_* must be untouched
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS, [design_row(pile_no="P-1", label="A", easting="499000.000")]
        ),
        filename="design.csv",
        apply=True,
    )

    after = Pile.objects.get(pile_no="P-1")
    assert after.asbuilt_e == before.asbuilt_e
    assert after.asbuilt_n == before.asbuilt_n
    assert after.asbuilt_z == before.asbuilt_z
    assert after.asbuilt_run_id == before.asbuilt_run_id
    assert after.design_e != before.design_e


def test_header_messiness_tolerance():
    package = PackageFactory(crs_epsg=3123)
    messy_headers = [
        "  Structure Ref ",
        "STRUCTURE_KIND",
        "Pile Cap Ref",
        "Cap  Type",
        "Pile No.",
        "Label",
        "Diameter",
        "Design Length",
        "Easting",
        "Northing",
        "Cutoff Level",
        "Tip Elevation",
        "Unexpected Extra Column",
    ]
    row = design_row(pile_no="P-1", label="A") + ["ignore me"]
    file_obj = make_csv_bytes(messy_headers, [row])

    report = services.import_piles(
        package=package, coordinate_type="design", file_obj=file_obj, filename="messy.csv", apply=True
    )

    assert report.created == 1
    assert report.errored == 0
    assert Pile.objects.filter(pile_no="P-1").exists()


def test_missing_required_column_rejects_whole_file():
    package = PackageFactory(crs_epsg=3123)
    headers = [h for h in DESIGN_HEADERS if h != "diameter"]
    row = [v for v in design_row(pile_no="P-1", label="A") if v != "1500"]
    file_obj = make_csv_bytes(headers, [row])

    with pytest.raises(MissingColumnsError) as exc_info:
        services.import_piles(
            package=package, coordinate_type="design", file_obj=file_obj, filename="bad.csv", apply=True
        )
    assert "diameter_mm" in exc_info.value.missing


def test_duplicate_pile_no_within_file_errors_on_second_occurrence():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A"),
        design_row(pile_no="P-1", label="B"),
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="dupes.csv",
        apply=True,
    )

    assert report.created == 1
    assert report.errored == 1
    assert Pile.objects.filter(pile_no="P-1").count() == 1


def test_csv_and_xlsx_produce_equivalent_reports():
    rows = [design_row(pile_no="P-1", label="A"), design_row(pile_no="P-2", label="B")]

    package_csv = PackageFactory(crs_epsg=3123)
    report_csv = services.import_piles(
        package=package_csv,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=False,
    )

    package_xlsx = PackageFactory(crs_epsg=3123)
    report_xlsx = services.import_piles(
        package=package_xlsx,
        coordinate_type="design",
        file_obj=make_xlsx_bytes(DESIGN_HEADERS, rows),
        filename="piles.xlsx",
        apply=False,
    )

    assert report_csv.created == report_xlsx.created
    assert report_csv.updated == report_xlsx.updated
    assert report_csv.changed == report_xlsx.changed
    assert report_csv.errored == report_xlsx.errored
    assert [r.pile_no for r in report_csv.rows] == [r.pile_no for r in report_xlsx.rows]
    assert [r.outcome for r in report_csv.rows] == [r.outcome for r in report_xlsx.rows]

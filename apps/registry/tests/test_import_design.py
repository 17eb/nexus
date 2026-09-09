import decimal

import pytest

from apps.registry import services
from apps.registry.factories import PackageFactory
from apps.registry.models import ImportRun, Pile, PileCap, Structure

from .helpers import DESIGN_HEADERS, design_row, make_csv_bytes

pytestmark = pytest.mark.django_db


def test_dry_run_creates_nothing():
    package = PackageFactory(crs_epsg=3123)
    rows = [design_row(pile_no="P-1", label="A"), design_row(pile_no="P-2", label="B")]
    file_obj = make_csv_bytes(DESIGN_HEADERS, rows)

    report = services.import_piles(
        package=package, coordinate_type="design", file_obj=file_obj, filename="piles.csv", apply=False
    )

    assert report.dry_run is True
    assert report.created == 2
    assert report.import_run_id is None
    assert Pile.objects.count() == 0
    assert Structure.objects.count() == 0
    assert PileCap.objects.count() == 0
    assert ImportRun.objects.count() == 0


def test_apply_creates_hierarchy():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A", structure_ref="PR01", pile_cap_ref="1"),
        design_row(pile_no="P-2", label="B", structure_ref="PR01", pile_cap_ref="1"),
    ]
    file_obj = make_csv_bytes(DESIGN_HEADERS, rows)

    report = services.import_piles(
        package=package, coordinate_type="design", file_obj=file_obj, filename="piles.csv", apply=True
    )

    assert report.created == 2
    assert Structure.objects.count() == 1
    assert PileCap.objects.count() == 1
    assert Pile.objects.count() == 2
    assert ImportRun.objects.count() == 1

    import_run = ImportRun.objects.get()
    for pile in Pile.objects.all():
        assert pile.created_by_run_id == import_run.id


def test_idempotent_reimport_reports_update_not_create():
    package = PackageFactory(crs_epsg=3123)
    rows = [design_row(pile_no="P-1", label="A"), design_row(pile_no="P-2", label="B")]

    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )

    assert report.created == 0
    assert report.changed == 0
    assert report.updated == 2
    assert all(r.outcome == "update" for r in report.rows)
    assert Pile.objects.count() == 2


def test_two_run_one_value_differs():
    package = PackageFactory(crs_epsg=3123)
    rows = [design_row(pile_no="P-1", label="A"), design_row(pile_no="P-2", label="B")]

    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )

    changed_rows = [
        design_row(pile_no="P-1", label="A", easting="498000.500"),  # design_e differs
        design_row(pile_no="P-2", label="B"),
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, changed_rows),
        filename="piles.csv",
        apply=True,
    )

    changed = [r for r in report.rows if r.outcome == "changed"]
    updated = [r for r in report.rows if r.outcome == "update"]
    assert len(changed) == 1
    assert len(updated) == 1
    assert changed[0].pile_no == "P-1"
    assert changed[0].changed_fields == ["design_e"]
    assert changed[0].previous_values["design_e"] == "498000.000"

    pile = Pile.objects.get(pile_no="P-1")
    assert pile.design_e == decimal.Decimal("498000.500")


def test_reparenting_reports_changed_and_appears_in_reparented_list():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS, [design_row(pile_no="P-1", label="A", pile_cap_ref="1")]
        ),
        filename="piles.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS, [design_row(pile_no="P-1", label="A", pile_cap_ref="2")]
        ),
        filename="piles.csv",
        apply=True,
    )

    assert report.changed == 1
    assert "pile_cap" in report.rows[0].changed_fields
    assert report.reparented == ["P-1"]


def test_design_row_for_pile_no_in_different_package_is_a_row_error_not_a_new_pile():
    package_a = PackageFactory(code="S-04", crs_epsg=3123)
    package_b = PackageFactory(code="S-05", crs_epsg=3123)
    services.import_piles(
        package=package_a,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="piles.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package_b,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="piles.csv",
        apply=True,
    )

    assert report.created == 0
    assert report.errored == 1
    error_row = report.rows[0]
    assert error_row.outcome == "error"
    assert "S-04" in error_row.errors[0]
    assert "S-05" in error_row.errors[0]

    # still exactly one pile, still under package_a — no duplicate/reparented row created
    assert Pile.objects.filter(pile_no="P-1").count() == 1
    assert Pile.objects.get(pile_no="P-1").pile_cap.structure.package_id == package_a.id
    assert not Structure.objects.filter(package=package_b).exists()


def test_mixed_valid_and_invalid_rows():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A"),
        design_row(pile_no="P-2", label="B", diameter="-100"),  # invalid
        design_row(pile_no="P-3", label="C"),
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )

    assert report.created == 2
    assert report.errored == 1
    assert Pile.objects.count() == 2
    assert not Pile.objects.filter(pile_no="P-2").exists()


def test_conflicting_structure_kind_is_a_row_error():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [design_row(pile_no="P-1", label="A", structure_ref="PR01", structure_kind="viaduct")],
        ),
        filename="piles.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [design_row(pile_no="P-2", label="B", structure_ref="PR01", structure_kind="station")],
        ),
        filename="piles.csv",
        apply=True,
    )

    assert report.errored == 1
    assert not Pile.objects.filter(pile_no="P-2").exists()


def test_conflicting_cap_type_is_a_row_error():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [design_row(pile_no="P-1", label="A", pile_cap_ref="1", cap_type="standard")],
        ),
        filename="piles.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [design_row(pile_no="P-2", label="B", pile_cap_ref="1", cap_type="straddle")],
        ),
        filename="piles.csv",
        apply=True,
    )

    assert report.errored == 1


def test_non_positive_diameter_and_length_are_row_errors():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A", diameter="0"),
        design_row(pile_no="P-2", label="B", design_length="-5"),
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )
    assert report.errored == 2


def test_invalid_enum_values_are_row_errors():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A", structure_kind="bridge"),
        design_row(pile_no="P-2", label="B", cap_type="round"),
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )
    assert report.errored == 2

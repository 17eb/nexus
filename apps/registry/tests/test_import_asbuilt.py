import decimal

import pytest

from apps.registry import services
from apps.registry.factories import PackageFactory
from apps.registry.models import Pile

from .helpers import ASBUILT_HEADERS, DESIGN_HEADERS, asbuilt_row, design_row, make_csv_bytes

pytestmark = pytest.mark.django_db


def _seed_pile(package, pile_no="P-1", label="A"):
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no=pile_no, label=label)]),
        filename="design.csv",
        apply=True,
    )


def test_asbuilt_update_populates_only_asbuilt_fields():
    package = PackageFactory(crs_epsg=3123)
    _seed_pile(package, pile_no="P-1")

    report = services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1")]),
        filename="asbuilt.csv",
        apply=True,
    )

    assert report.created == 0  # as_built never creates
    assert report.changed == 1

    pile = Pile.objects.get(pile_no="P-1")
    assert pile.asbuilt_e == decimal.Decimal("498000.030")
    assert pile.asbuilt_n == decimal.Decimal("1556999.980")
    assert pile.asbuilt_z == decimal.Decimal("10.480")
    assert pile.asbuilt_run_id is not None


def test_asbuilt_never_writes_design_fields():
    package = PackageFactory(crs_epsg=3123)
    _seed_pile(package, pile_no="P-1")
    before = Pile.objects.get(pile_no="P-1")

    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1")]),
        filename="asbuilt.csv",
        apply=True,
    )

    after = Pile.objects.get(pile_no="P-1")
    for field in ["design_e", "design_n", "cutoff_level", "tip_elevation", "diameter_mm", "design_length_m"]:
        assert getattr(before, field) == getattr(after, field), field
    assert after.created_by_run_id == before.created_by_run_id  # untouched


def test_asbuilt_may_overwrite_previous_values():
    package = PackageFactory(crs_epsg=3123)
    _seed_pile(package, pile_no="P-1")

    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1", easting="498000.030")]),
        filename="asbuilt.csv",
        apply=True,
    )

    report = services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1", easting="498001.500")]),
        filename="asbuilt.csv",
        apply=True,
    )

    row = report.rows[0]
    assert row.outcome == "changed"
    assert row.previous_values["asbuilt_e"] == "498000.030"

    pile = Pile.objects.get(pile_no="P-1")
    assert pile.asbuilt_e == decimal.Decimal("498001.500")
    assert pile.asbuilt_run_id is not None


def test_asbuilt_second_run_with_identical_values_reports_update_not_changed():
    package = PackageFactory(crs_epsg=3123)
    _seed_pile(package, pile_no="P-1")

    row = asbuilt_row(pile_no="P-1")
    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [row]),
        filename="asbuilt.csv",
        apply=True,
    )
    first_run_id = Pile.objects.get(pile_no="P-1").asbuilt_run_id

    report = services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [row]),
        filename="asbuilt.csv",
        apply=True,
    )

    assert report.rows[0].outcome == "update"
    second_run_id = Pile.objects.get(pile_no="P-1").asbuilt_run_id
    assert second_run_id != first_run_id  # asbuilt_run still advances on a no-op match


def test_asbuilt_row_for_pile_in_different_package_is_a_row_error():
    package_a = PackageFactory(code="S-04", crs_epsg=3123)
    package_b = PackageFactory(code="S-05", crs_epsg=3123)
    _seed_pile(package_a, pile_no="P-1")

    report = services.import_piles(
        package=package_b,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1")]),
        filename="asbuilt.csv",
        apply=True,
    )

    assert report.errored == 1
    assert report.changed == 0
    error_row = report.rows[0]
    assert error_row.outcome == "error"
    assert "S-04" in error_row.errors[0]
    assert "S-05" in error_row.errors[0]

    pile = Pile.objects.get(pile_no="P-1")
    assert pile.asbuilt_e is None
    assert pile.asbuilt_run_id is None


def test_asbuilt_unknown_pile_no_is_a_row_error_but_others_still_apply():
    package = PackageFactory(crs_epsg=3123)
    _seed_pile(package, pile_no="P-1")

    rows = [asbuilt_row(pile_no="P-1"), asbuilt_row(pile_no="DOES-NOT-EXIST")]
    report = services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, rows),
        filename="asbuilt.csv",
        apply=True,
    )

    assert report.errored == 1
    assert report.changed == 1
    error_row = next(r for r in report.rows if r.outcome == "error")
    assert error_row.pile_no == "DOES-NOT-EXIST"

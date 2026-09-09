import pytest

from apps.registry import services
from apps.registry.factories import PackageFactory
from apps.registry.models import ImportRun, Pile

from .helpers import ASBUILT_HEADERS, DESIGN_HEADERS, asbuilt_row, design_row, make_csv_bytes

pytestmark = pytest.mark.django_db


def test_apply_persists_one_import_run_with_matching_counts():
    package = PackageFactory(crs_epsg=3123)
    rows = [
        design_row(pile_no="P-1", label="A"),
        design_row(pile_no="P-2", label="B", diameter="-1"),  # error
    ]
    report = services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, rows),
        filename="piles.csv",
        apply=True,
    )

    assert ImportRun.objects.count() == 1
    import_run = ImportRun.objects.get()
    assert import_run.total_rows == 2
    assert import_run.created_count == report.created == 1
    assert import_run.updated_count == report.updated == 0
    assert import_run.changed_count == report.changed == 0
    assert import_run.errored_count == report.errored == 1
    assert len(import_run.report) == 2
    assert {row["outcome"] for row in import_run.report} == {"create", "error"}


def test_created_by_run_set_once_and_not_overwritten_by_later_changes():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="piles.csv",
        apply=True,
    )
    first_run_id = Pile.objects.get(pile_no="P-1").created_by_run_id

    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS, [design_row(pile_no="P-1", label="A", easting="499999.000")]
        ),
        filename="piles.csv",
        apply=True,
    )

    second_run_id = Pile.objects.get(pile_no="P-1").created_by_run_id
    assert first_run_id == second_run_id


def test_asbuilt_run_updates_on_both_update_and_changed_outcomes():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="piles.csv",
        apply=True,
    )

    row = asbuilt_row(pile_no="P-1")
    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [row]),
        filename="asbuilt.csv",
        apply=True,
    )
    run_after_changed = Pile.objects.get(pile_no="P-1").asbuilt_run_id

    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [row]),  # identical values -> "update"
        filename="asbuilt.csv",
        apply=True,
    )
    run_after_update = Pile.objects.get(pile_no="P-1").asbuilt_run_id

    assert run_after_changed is not None
    assert run_after_update is not None
    assert run_after_update != run_after_changed

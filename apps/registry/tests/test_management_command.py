import csv
import io

import pytest
from django.core.management import CommandError, call_command

from apps.registry.factories import PackageFactory
from apps.registry.models import Pile

from .helpers import DESIGN_HEADERS, design_row

pytestmark = pytest.mark.django_db


def _write_csv(tmp_path, rows, name="piles.csv"):
    path = tmp_path / name
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(DESIGN_HEADERS)
        writer.writerows(rows)
    return str(path)


def test_default_invocation_is_a_dry_run(tmp_path):
    PackageFactory(code="S-05", crs_epsg=3123)
    path = _write_csv(tmp_path, [design_row(pile_no="P-1", label="A")])

    out = io.StringIO()
    call_command("import_piles", path, "--package", "S-05", "--coordinate-type", "design", stdout=out)

    assert Pile.objects.count() == 0
    assert "DRY RUN" in out.getvalue()


def test_apply_flag_commits(tmp_path):
    PackageFactory(code="S-05", crs_epsg=3123)
    path = _write_csv(tmp_path, [design_row(pile_no="P-1", label="A")])

    out = io.StringIO()
    call_command(
        "import_piles", path, "--package", "S-05", "--coordinate-type", "design", "--apply", stdout=out
    )

    assert Pile.objects.count() == 1
    assert "APPLIED" in out.getvalue()


def test_unknown_package_raises_command_error(tmp_path):
    path = _write_csv(tmp_path, [design_row(pile_no="P-1", label="A")])

    with pytest.raises(CommandError):
        call_command("import_piles", path, "--package", "NOPE", "--coordinate-type", "design")


def test_exit_code_1_when_report_has_errors(tmp_path):
    PackageFactory(code="S-05", crs_epsg=3123)
    path = _write_csv(tmp_path, [design_row(pile_no="P-1", label="A", diameter="-1")])

    with pytest.raises(SystemExit) as exc_info:
        call_command("import_piles", path, "--package", "S-05", "--coordinate-type", "design")
    assert exc_info.value.code == 1


def test_reparented_warning_shown_in_dry_run_output(tmp_path):
    PackageFactory(code="S-05", crs_epsg=3123)
    call_command(
        "import_piles",
        _write_csv(tmp_path, [design_row(pile_no="P-1", label="A", pile_cap_ref="1")], "first.csv"),
        "--package",
        "S-05",
        "--coordinate-type",
        "design",
        "--apply",
    )

    out = io.StringIO()
    call_command(
        "import_piles",
        _write_csv(tmp_path, [design_row(pile_no="P-1", label="A", pile_cap_ref="2")], "second.csv"),
        "--package",
        "S-05",
        "--coordinate-type",
        "design",
        "--apply",
        stdout=out,
    )

    assert "reparented" in out.getvalue().lower()

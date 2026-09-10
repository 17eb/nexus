"""Public interface of the registry app. Only functions in this module
should be imported by other apps or by the management commands — nothing
under registry/import_piles/ is a public API (enforced by the
import-linter contract in pyproject.toml)."""

import dataclasses
import uuid
from typing import IO

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from .import_piles import upsert, validators
from .import_piles.parser import MissingColumnsError, UnsupportedFileTypeError, parse_rows
from .import_piles.report import CoordinateType, ImportReport, RowReport
from .models import ImportRun, Package, Pile

__all__ = [
    "import_piles",
    "get_piles_for_package",
    "get_pile",
    "MissingColumnsError",
    "UnsupportedFileTypeError",
]


def import_piles(
    *,
    package: Package,
    coordinate_type: CoordinateType,
    file_obj: IO[bytes],
    filename: str,
    apply: bool = False,
) -> ImportReport:
    """Dry-run by default (`apply=False`); pass `apply=True` to commit.
    Both modes run the identical code path — dry-run just rolls back the
    outer transaction at the end, so there is exactly one implementation
    to keep dry-run and apply reports in sync.

    Raises MissingColumnsError if a required column is entirely absent
    from the file's header row (whole-file rejection, before any row is
    processed) and UnsupportedFileTypeError for anything but .csv/.xlsx.
    """
    parsed_rows = parse_rows(file_obj, filename, coordinate_type)

    row_reports: list[RowReport] = []
    reparented: list[str] = []
    seen_pile_nos: set[str] = set()
    created = updated = changed = errored = 0

    with transaction.atomic():
        import_run = ImportRun.objects.create(
            package=package,
            coordinate_type=coordinate_type,
            filename=filename,
            total_rows=len(parsed_rows),
            created_count=0,
            updated_count=0,
            changed_count=0,
            errored_count=0,
            report=[],
        )

        for row_number, raw_row in parsed_rows:
            if coordinate_type == "design":
                clean, errors = validators.validate_design_row(raw_row, package.crs_epsg)
            else:
                clean, errors = validators.validate_asbuilt_row(raw_row, package.crs_epsg)

            pile_no = (clean or raw_row).get("pile_no") or None

            if not errors and pile_no in seen_pile_nos:
                clean = None
                errors = ["pile_no: duplicate within this file (already seen earlier)"]

            if errors:
                row_reports.append(
                    RowReport(row_number=row_number, pile_no=pile_no, outcome="error", errors=errors)
                )
                errored += 1
                continue

            # Invariant: validate_*_row only returns no errors alongside a
            # non-None `clean` dict and a non-blank pile_no.
            assert clean is not None
            assert pile_no is not None
            seen_pile_nos.add(pile_no)

            try:
                with transaction.atomic():  # savepoint — one bad row doesn't block the rest
                    if coordinate_type == "design":
                        row_report = upsert.upsert_design_row(row_number, clean, package, import_run)
                    else:
                        row_report = upsert.upsert_asbuilt_row(row_number, clean, package, import_run)
            except (IntegrityError, upsert.DomainError) as exc:
                row_report = RowReport(
                    row_number=row_number, pile_no=pile_no, outcome="error", errors=[str(exc)]
                )

            row_reports.append(row_report)
            if row_report.outcome == "create":
                created += 1
            elif row_report.outcome == "update":
                updated += 1
            elif row_report.outcome == "changed":
                changed += 1
                if "pile_cap" in row_report.changed_fields:
                    assert row_report.pile_no is not None
                    reparented.append(row_report.pile_no)
            else:
                errored += 1

        import_run.created_count = created
        import_run.updated_count = updated
        import_run.changed_count = changed
        import_run.errored_count = errored
        import_run.report = [dataclasses.asdict(r) for r in row_reports]
        import_run.save(
            update_fields=["created_count", "updated_count", "changed_count", "errored_count", "report"]
        )

        if not apply:
            transaction.set_rollback(True)

    return ImportReport(
        package_code=package.code,
        coordinate_type=coordinate_type,
        dry_run=not apply,
        total_rows=len(parsed_rows),
        created=created,
        updated=updated,
        changed=changed,
        errored=errored,
        reparented=reparented,
        import_run_id=import_run.id if apply else None,
        rows=row_reports,
    )


def get_piles_for_package(package_id: uuid.UUID) -> tuple[Package, QuerySet[Pile]]:
    package = get_object_or_404(Package, pk=package_id)
    # TODO(M2): scope to the requesting user's memberships once
    # check_permission() exists — list endpoints must fail closed.
    piles = (
        Pile.objects.filter(pile_cap__structure__package=package)
        .select_related("pile_cap", "pile_cap__structure")
        .order_by("pile_cap__structure__ref", "pile_cap__ref", "label")
    )
    return package, piles


def get_pile(pile_id: uuid.UUID) -> Pile:
    """The single-object counterpart to get_piles_for_package() — for
    other apps (e.g. documents) that need to validate a pile_id without
    importing apps.registry.models directly."""
    return get_object_or_404(Pile, pk=pile_id)

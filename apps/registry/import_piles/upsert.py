"""DB-touching upsert logic. Two functions, deliberately not unified
behind a generic "write these fields" helper: `upsert_design_row` only
ever writes design-side fields, `upsert_asbuilt_row` only ever writes
as-built fields. This is what guarantees a design import can never
touch `asbuilt_*` and an as_built import can never touch `design_*` /
`cutoff_level` / `tip_elevation` / `diameter_mm` — the "never copy one
into the other" invariant in docs/data-model.md."""

from ..models import ImportRun, Package, Pile, PileCap, Structure
from .report import RowReport


class DomainError(Exception):
    """A known, anticipated business-rule conflict (e.g. a structure's
    kind disagreeing with what's already stored). Caught by the caller's
    per-row savepoint and turned into an error RowReport, same as an
    IntegrityError would be."""


def upsert_design_row(
    row_number: int, clean: dict, package: Package, import_run: ImportRun
) -> RowReport:
    structure, structure_created = Structure.objects.get_or_create(
        package=package,
        ref=clean["structure_ref"],
        defaults={"kind": clean["structure_kind"]},
    )
    if not structure_created and structure.kind != clean["structure_kind"]:
        raise DomainError(
            f"structure_kind: existing Structure {structure.ref!r} has "
            f"kind={structure.kind!r}, row states {clean['structure_kind']!r}"
        )

    pile_cap, cap_created = PileCap.objects.get_or_create(
        structure=structure,
        ref=clean["pile_cap_ref"],
        defaults={"cap_type": clean["cap_type"]},
    )
    if not cap_created and pile_cap.cap_type != clean["cap_type"]:
        raise DomainError(
            f"cap_type: existing PileCap {pile_cap.ref!r} has "
            f"cap_type={pile_cap.cap_type!r}, row states {clean['cap_type']!r}"
        )

    design_fields = {
        "pile_cap": pile_cap,
        "label": clean["label"],
        "diameter_mm": clean["diameter_mm"],
        "design_length_m": clean["design_length_m"],
        "design_e": clean["easting"],
        "design_n": clean["northing"],
        "cutoff_level": clean["cutoff_level"],
        "tip_elevation": clean["tip_elevation"],
    }

    try:
        pile = Pile.objects.get(
            pile_no=clean["pile_no"], pile_cap__structure__package=package
        )
    except Pile.DoesNotExist:
        other_pile = Pile.objects.filter(pile_no=clean["pile_no"]).first()
        if other_pile is not None:
            other_package = other_pile.pile_cap.structure.package
            raise DomainError(
                f"pile_no: {clean['pile_no']!r} belongs to package "
                f"{other_package.code!r}, not {package.code!r}"
            ) from None
        Pile.objects.create(
            pile_no=clean["pile_no"], created_by_run=import_run, **design_fields
        )
        return RowReport(row_number=row_number, pile_no=clean["pile_no"], outcome="create")

    changed_fields: list[str] = []
    previous_values: dict[str, str] = {}
    for field, new_value in design_fields.items():
        old_value = getattr(pile, field)
        differs = old_value.pk != new_value.pk if field == "pile_cap" else old_value != new_value
        if differs:
            changed_fields.append(field)
            previous_values[field] = str(old_value)
            setattr(pile, field, new_value)

    if changed_fields:
        pile.save(update_fields=[*changed_fields, "updated_at"])
        return RowReport(
            row_number=row_number,
            pile_no=pile.pile_no,
            outcome="changed",
            changed_fields=changed_fields,
            previous_values=previous_values,
        )

    return RowReport(row_number=row_number, pile_no=pile.pile_no, outcome="update")


def upsert_asbuilt_row(
    row_number: int, clean: dict, package: Package, import_run: ImportRun
) -> RowReport:
    try:
        pile = Pile.objects.get(
            pile_no=clean["pile_no"], pile_cap__structure__package=package
        )
    except Pile.DoesNotExist:
        other_pile = Pile.objects.filter(pile_no=clean["pile_no"]).first()
        if other_pile is not None:
            other_package = other_pile.pile_cap.structure.package
            raise DomainError(
                f"pile_no: {clean['pile_no']!r} belongs to package "
                f"{other_package.code!r}, not {package.code!r}"
            ) from None
        raise DomainError(
            f"pile_no: {clean['pile_no']!r} does not exist — run a design import first"
        ) from None

    asbuilt_fields = {
        "asbuilt_e": clean["easting"],
        "asbuilt_n": clean["northing"],
        "asbuilt_z": clean["elevation"],
    }

    changed_fields: list[str] = []
    previous_values: dict[str, str] = {}
    for field, new_value in asbuilt_fields.items():
        old_value = getattr(pile, field)
        if old_value != new_value:
            changed_fields.append(field)
            previous_values[field] = "" if old_value is None else str(old_value)
            setattr(pile, field, new_value)

    # asbuilt_run is set on every matched row, whether or not values
    # actually changed — it records "which run last asserted these
    # as-built values", not just "which run last changed them".
    pile.asbuilt_run = import_run
    pile.save(update_fields=[*changed_fields, "asbuilt_run", "updated_at"])

    if changed_fields:
        return RowReport(
            row_number=row_number,
            pile_no=pile.pile_no,
            outcome="changed",
            changed_fields=changed_fields,
            previous_values=previous_values,
        )

    return RowReport(row_number=row_number, pile_no=pile.pile_no, outcome="update")

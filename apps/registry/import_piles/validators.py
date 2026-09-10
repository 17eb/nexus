"""Pure-Python, no-DB validation and type conversion for one already-
parsed row. Cross-row checks (duplicate pile_no within a file) are
handled by the caller, which sees every row and this module does not."""

import decimal

from ..models import PileCap, Structure
from .report import CoordinateType

DECIMAL_FIELDS_BY_MODE: dict[CoordinateType, list[str]] = {
    "design": ["design_length_m", "easting", "northing", "cutoff_level", "tip_elevation"],
    "as_built": ["easting", "northing", "elevation"],
}

POSITIVE_FIELDS = {"diameter_mm", "design_length_m"}


class RowValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _to_decimal(value: str, field: str, errors: list[str]) -> decimal.Decimal | None:
    try:
        return decimal.Decimal(value)
    except (decimal.InvalidOperation, ValueError):
        errors.append(f"{field}: {value!r} is not a valid number")
        return None


def _to_int(value: str, field: str, errors: list[str]) -> int | None:
    try:
        return int(decimal.Decimal(value))
    except (decimal.InvalidOperation, ValueError):
        errors.append(f"{field}: {value!r} is not a valid integer")
        return None


def validate_design_row(row: dict[str, str], package_crs_epsg: int) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    clean: dict = {}

    for field in ["structure_ref", "pile_cap_ref", "pile_no", "label"]:
        value = row.get(field, "")
        if not value:
            errors.append(f"{field}: required, got blank")
        clean[field] = value

    kind_raw = row.get("structure_kind", "").strip().lower()
    if kind_raw not in dict(Structure.Kind.choices):
        valid_kinds = list(dict(Structure.Kind.choices))
        errors.append(f"structure_kind: {row.get('structure_kind')!r} is not one of {valid_kinds}")
    clean["structure_kind"] = kind_raw

    cap_type_raw = row.get("cap_type", "").strip().lower()
    if cap_type_raw not in dict(PileCap.CapType.choices):
        errors.append(f"cap_type: {row.get('cap_type')!r} is not one of {list(dict(PileCap.CapType.choices))}")
    clean["cap_type"] = cap_type_raw

    diameter = _to_int(row.get("diameter_mm", ""), "diameter_mm", errors)
    clean["diameter_mm"] = diameter

    for field in DECIMAL_FIELDS_BY_MODE["design"]:
        clean[field] = _to_decimal(row.get(field, ""), field, errors)

    for field in POSITIVE_FIELDS:
        positive_value = clean.get(field)
        if positive_value is not None and positive_value <= 0:
            errors.append(f"{field}: must be positive, got {positive_value}")

    _validate_source_crs(row, package_crs_epsg, errors)

    if errors:
        return None, errors
    return clean, errors


def validate_asbuilt_row(row: dict[str, str], package_crs_epsg: int) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    clean: dict = {}

    pile_no = row.get("pile_no", "")
    if not pile_no:
        errors.append("pile_no: required, got blank")
    clean["pile_no"] = pile_no

    for field in DECIMAL_FIELDS_BY_MODE["as_built"]:
        clean[field] = _to_decimal(row.get(field, ""), field, errors)

    _validate_source_crs(row, package_crs_epsg, errors)

    if errors:
        return None, errors
    return clean, errors


def _validate_source_crs(row: dict[str, str], package_crs_epsg: int, errors: list[str]) -> None:
    """If present, source_crs/epsg is validation-only against
    Package.crs_epsg — never persisted per-row (docs/data-model.md's
    Pile has no such field)."""
    source_crs = row.get("source_crs", "").strip()
    if not source_crs:
        return
    try:
        source_epsg = int(source_crs)
    except ValueError:
        errors.append(f"source_crs: {source_crs!r} is not a valid EPSG code")
        return
    if source_epsg != package_crs_epsg:
        errors.append(
            f"source_crs: row states EPSG:{source_epsg} but package is configured for EPSG:{package_crs_epsg}"
        )

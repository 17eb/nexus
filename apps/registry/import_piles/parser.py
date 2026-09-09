"""CSV/XLSX parsing with tolerant header matching. Real files are
messier than the sample: header matching is case- and
whitespace-insensitive, columns may be reordered, and unrecognised extra
columns are ignored rather than rejected."""

import csv
import io
import re
from typing import IO

import openpyxl

from .report import CoordinateType

OPTIONAL_COLUMNS = {"source_crs"}

REQUIRED_COLUMNS: dict[CoordinateType, list[str]] = {
    "design": [
        "structure_ref",
        "structure_kind",
        "pile_cap_ref",
        "cap_type",
        "pile_no",
        "label",
        "diameter_mm",
        "design_length_m",
        "easting",
        "northing",
        "cutoff_level",
        "tip_elevation",
    ],
    "as_built": [
        "pile_no",
        "easting",
        "northing",
        "elevation",
    ],
}

# canonical key -> accepted header spellings (normalised at match time)
_ALIASES: dict[str, set[str]] = {
    "structure_ref": {"structure ref", "pier ref", "structure"},
    "structure_kind": {"structure kind", "kind"},
    "pile_cap_ref": {"pile cap ref", "cap ref", "pile cap"},
    "cap_type": {"cap type"},
    "pile_no": {"pile no", "pile no.", "pileno"},
    "label": {"label", "pile label"},
    "diameter_mm": {"diameter", "diameter mm"},
    "design_length_m": {"design length", "design length m", "length"},
    "easting": {"easting", "e"},
    "northing": {"northing", "n"},
    "elevation": {"elevation", "z", "asbuilt elevation"},
    "cutoff_level": {"cutoff level", "top of pile"},
    "tip_elevation": {"tip elevation"},
    "source_crs": {"source crs", "epsg", "crs", "source epsg"},
}


class MissingColumnsError(Exception):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Missing required column(s): {', '.join(missing)}")


class UnsupportedFileTypeError(Exception):
    pass


def _normalize_header(raw: str) -> str:
    return re.sub(r"[\s_./]+", " ", raw.strip().lower()).strip()


def _alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for canonical, aliases in _ALIASES.items():
        index[_normalize_header(canonical.replace("_", " "))] = canonical
        for alias in aliases:
            index[_normalize_header(alias)] = canonical
    return index


def _map_headers(raw_headers: list[str]) -> dict[int, str]:
    """Returns {column_index: canonical_key} for recognised columns only."""
    alias_index = _alias_index()
    mapping: dict[int, str] = {}
    for i, raw in enumerate(raw_headers):
        if raw is None:
            continue
        canonical = alias_index.get(_normalize_header(str(raw)))
        if canonical:
            mapping[i] = canonical
    return mapping


def _read_csv_rows(file_obj: IO[bytes]) -> list[list[str]]:
    text_stream = io.TextIOWrapper(file_obj, encoding="utf-8-sig", newline="")
    reader = csv.reader(text_stream)
    return [row for row in reader]


def _read_xlsx_rows(file_obj: IO[bytes]) -> list[list[str]]:
    workbook = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    worksheet = workbook.worksheets[0]
    rows: list[list[str]] = []
    for raw_row in worksheet.iter_rows(values_only=True):
        rows.append(["" if v is None else str(v) for v in raw_row])
    return rows


def parse_rows(
    file_obj: IO[bytes], filename: str, coordinate_type: CoordinateType
) -> list[tuple[int, dict[str, str]]]:
    """Returns [(row_number, {canonical_key: raw_string_value})], where
    row_number matches what a user sees in Excel (header row = 1, first
    data row = 2). Raises MissingColumnsError if a required column is
    entirely absent from the header row — the one case where the whole
    file is rejected before any row is processed."""
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        raw_rows = _read_csv_rows(file_obj)
    elif lower_name.endswith(".xlsx"):
        raw_rows = _read_xlsx_rows(file_obj)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type for {filename!r}; expected .csv or .xlsx"
        )

    if not raw_rows:
        raise MissingColumnsError(REQUIRED_COLUMNS[coordinate_type])

    header_row, *data_rows = raw_rows
    column_map = _map_headers(header_row)

    found_canonicals = set(column_map.values())
    missing = [c for c in REQUIRED_COLUMNS[coordinate_type] if c not in found_canonicals]
    if missing:
        raise MissingColumnsError(missing)

    rows: list[tuple[int, dict[str, str]]] = []
    for offset, raw_row in enumerate(data_rows):
        row_number = offset + 2
        if not any(cell.strip() for cell in raw_row if isinstance(cell, str)):
            continue  # skip fully blank rows
        row_dict: dict[str, str] = {}
        for i, canonical in column_map.items():
            value = raw_row[i] if i < len(raw_row) else ""
            row_dict[canonical] = (value or "").strip()
        rows.append((row_number, row_dict))

    return rows

import csv
import io

import openpyxl

DESIGN_HEADERS = [
    "structure ref",
    "structure kind",
    "pile cap ref",
    "cap type",
    "pile no",
    "label",
    "diameter",
    "design length",
    "easting",
    "northing",
    "cutoff level",
    "tip elevation",
]

ASBUILT_HEADERS = ["pile no", "easting", "northing", "elevation"]


def design_row(
    pile_no="P-1",
    label="A",
    structure_ref="PR01",
    structure_kind="viaduct",
    pile_cap_ref="1",
    cap_type="standard",
    diameter="1500",
    design_length="28.000",
    easting="498000.000",
    northing="1557000.000",
    cutoff_level="10.500",
    tip_elevation="-17.500",
):
    return [
        structure_ref,
        structure_kind,
        pile_cap_ref,
        cap_type,
        pile_no,
        label,
        diameter,
        design_length,
        easting,
        northing,
        cutoff_level,
        tip_elevation,
    ]


def asbuilt_row(pile_no="P-1", easting="498000.030", northing="1556999.980", elevation="10.480"):
    return [pile_no, easting, northing, elevation]


def make_csv_bytes(headers: list[str], rows: list[list[str]]) -> io.BytesIO:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return io.BytesIO(buf.getvalue().encode("utf-8"))


def make_xlsx_bytes(headers: list[str], rows: list[list[str]]) -> io.BytesIO:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    assert sheet is not None  # always true for a freshly created Workbook
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    buf = io.BytesIO()
    workbook.save(buf)
    buf.seek(0)
    return buf

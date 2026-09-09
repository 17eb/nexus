"""Report data structures shared by dry-run and apply. There is exactly
one code path for both (see upsert.py) so these are always populated the
same way regardless of `apply`."""

import dataclasses
import uuid
from typing import Literal

RowOutcome = Literal["create", "update", "changed", "error"]
CoordinateType = Literal["design", "as_built"]


@dataclasses.dataclass(frozen=True)
class RowReport:
    row_number: int  # header row = 1, first data row = 2 (matches Excel)
    pile_no: str | None
    outcome: RowOutcome
    changed_fields: list[str] = dataclasses.field(default_factory=list)
    previous_values: dict[str, str] = dataclasses.field(default_factory=dict)
    errors: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class ImportReport:
    package_code: str
    coordinate_type: CoordinateType
    dry_run: bool
    total_rows: int
    created: int
    updated: int
    changed: int
    errored: int
    reparented: list[str]
    import_run_id: uuid.UUID | None
    rows: list[RowReport]

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)

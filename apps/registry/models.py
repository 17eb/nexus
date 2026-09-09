import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """Ordinary bookkeeping timestamps. Not a substitute for the M3
    append-only Event log (Decision D4) — just admin/debugging aids."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Package(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=200)
    # Per-package CRS — never hardcode a coordinate system anywhere in
    # code. See docs/open-questions.md Q8: confirm the real value with
    # the survey team before importing real data.
    crs_epsg = models.PositiveIntegerField()
    chainage_bearing = models.DecimalField(max_digits=6, decimal_places=3)

    # NOTE: docs/data-model.md lists `holiday_calendar` (FK to reference
    # data) on Package. That reference-data model doesn't exist yet — it
    # is M3 work (tracking/calendar.py). The field is deliberately
    # omitted here rather than guessed at, and will be added alongside
    # its target model.

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Structure(TimestampedModel):
    class Kind(models.TextChoices):
        VIADUCT = "viaduct", _("Viaduct")
        STATION = "station", _("Station")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="structures"
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    ref = models.CharField(max_length=32)
    name = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["package", "ref"], name="uniq_structure_ref_per_package"
            )
        ]

    def __str__(self) -> str:
        return f"{self.package.code}/{self.ref}"


class PileCap(TimestampedModel):
    class CapType(models.TextChoices):
        STANDARD = "standard", _("Standard")
        STRADDLE = "straddle", _("Straddle")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    structure = models.ForeignKey(
        Structure, on_delete=models.PROTECT, related_name="pile_caps"
    )
    ref = models.CharField(max_length=32)
    cap_type = models.CharField(max_length=16, choices=CapType.choices)
    # Nullable: nothing in the M1 pile import column set populates a
    # cap-level elevation. No `pile_count` field — Decision D3: cap
    # geometry derives from the positions of its child piles.
    top_level = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["structure", "ref"], name="uniq_pilecap_ref_per_structure"
            )
        ]

    def __str__(self) -> str:
        return f"{self.structure}/{self.ref}"


class ImportRun(TimestampedModel):
    """Provenance record for one `services.import_piles()` call. Lighter
    than the M3 append-only Event log — scoped purely to import
    provenance, no append-only enforcement, no generic action taxonomy.

    Only ever persisted for real (apply=True) runs: creation happens
    inside the same outer transaction as the rest of the import, so a
    dry-run's rollback removes its ImportRun row along with everything
    else."""

    class CoordinateType(models.TextChoices):
        DESIGN = "design", _("Design")
        AS_BUILT = "as_built", _("As-built")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="import_runs"
    )
    coordinate_type = models.CharField(max_length=16, choices=CoordinateType.choices)
    filename = models.CharField(max_length=255)
    total_rows = models.PositiveIntegerField()
    created_count = models.PositiveIntegerField()
    updated_count = models.PositiveIntegerField()
    changed_count = models.PositiveIntegerField()
    errored_count = models.PositiveIntegerField()
    # Full per-row results: row_number, pile_no, outcome, changed_fields,
    # previous_values, errors — see registry/import_piles/report.py.
    report = models.JSONField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.package.code} {self.coordinate_type} import @ {self.created_at:%Y-%m-%d %H:%M}"


class Pile(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pile_cap = models.ForeignKey(
        PileCap, on_delete=models.PROTECT, related_name="piles"
    )
    label = models.CharField(max_length=4)  # "A".."I" — position within the cap
    pile_no = models.CharField(max_length=32, unique=True)  # project-wide identifier

    # diameter_mm is deliberately a PositiveSmallIntegerField, not a
    # Decimal: CLAUDE.md's "store lengths in metres as Decimal" rule is
    # about metres. This field's own name (docs/data-model.md) says its
    # unit is millimetres — it isn't the kind of field that rule
    # addresses.
    diameter_mm = models.PositiveSmallIntegerField()
    design_length_m = models.DecimalField(max_digits=6, decimal_places=3)

    # Design coordinates: from working drawings, available before
    # construction. Required at creation.
    design_e = models.DecimalField(max_digits=12, decimal_places=3)
    design_n = models.DecimalField(max_digits=12, decimal_places=3)

    # As-built coordinates: from survey, available only after
    # construction. Never overwrite design with as-built or vice versa —
    # enforced structurally in registry/import_piles/upsert.py.
    asbuilt_e = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    asbuilt_n = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    asbuilt_z = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )

    # a.k.a. "Top of Pile" on working drawings — same field, do not model
    # as a separate one (docs/domain.md).
    cutoff_level = models.DecimalField(max_digits=8, decimal_places=3)
    tip_elevation = models.DecimalField(max_digits=8, decimal_places=3)

    # Not populated by the M1 pile import — no source column for it.
    # Populated by a future construction/activity workflow (M4+).
    concreting_finished_at = models.DateTimeField(null=True, blank=True)

    created_by_run = models.ForeignKey(
        ImportRun,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        help_text="The design ImportRun that created this pile. Set once, at creation.",
    )
    asbuilt_run = models.ForeignKey(
        ImportRun,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        help_text="The as_built ImportRun that last matched this pile.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pile_cap", "label"], name="uniq_pile_label_per_cap"
            )
        ]

    def __str__(self) -> str:
        return f"{self.pile_no} ({self.pile_cap})"

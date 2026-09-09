# Data model

Indicative, not literal. Field names are binding; types and helpers may
be adjusted with reason. Structural changes (adding or removing a table,
changing a relationship) need to be raised, not assumed.

## registry

```python
class Package(models.Model):
    code                # "S-05"
    name
    crs_epsg            # 3123 — per package, never hardcoded
    chainage_bearing    # degrees; direction of increasing chainage
    holiday_calendar    # FK to reference data — not implemented until M3
                         # (tracking/calendar.py); the M1 migration omits
                         # this field rather than guess at the target
                         # model's shape, and adds it alongside M3.

class Structure(models.Model):
    package             # FK
    kind                # "viaduct" | "station"  ← quota denominators split here
    ref                 # "PR12"
    name

class PileCap(models.Model):
    structure           # FK
    ref
    cap_type            # "standard" | "straddle"
    top_level           # elevation, Decimal

class Pile(models.Model):
    pile_cap            # FK
    label               # "A".."I" — position within the cap
    pile_no             # "P-1045S" — the project-wide identifier
    diameter_mm         # 1500 — PositiveSmallIntegerField, not Decimal;
                         # the field's own unit is mm, not metres, so the
                         # "measurements as Decimal" rule doesn't apply
    design_length_m     # Decimal
    design_e, design_n                  # from working drawings
    asbuilt_e, asbuilt_n, asbuilt_z     # from survey, nullable
    cutoff_level                        # a.k.a. "Top of Pile" on drawings
    tip_elevation
    concreting_finished_at              # nullable; drives concrete-age rules
    created_by_run       # FK ImportRun, nullable — the design import
                          # that created this pile, set once
    asbuilt_run           # FK ImportRun, nullable — the as_built import
                          # that last matched this pile (updated on every
                          # match, whether or not values changed)

class ImportRun(models.Model):
    package               # FK
    coordinate_type        # "design" | "as_built"
    filename
    total_rows, created_count, updated_count, changed_count, errored_count
    report                # JSONField — full per-row results (row_number,
                           # pile_no, outcome, changed_fields,
                           # previous_values, errors)
```

`ImportRun` is provenance for the pile import (M1), not the M3
append-only `Event` log — no append-only enforcement, no generic action
taxonomy. It is only ever persisted for a real (`apply=True`) run: it's
created inside the same DB transaction as the rest of the import, so a
dry-run's rollback removes its row along with everything else.

**There is no `pile_count` on `PileCap`.** Cap geometry is derived from
its piles' coordinates. This is what makes 3 / 4 / 6 / 9 pile caps and
straddle caps work with no special-casing, and what makes an editable
pile count free rather than a feature. Do not add a count field.

**Coordinate display rule:** use as-built when present, otherwise design,
and mark which one is being shown. Never copy one into the other.

## testing

```python
class ActivityType(models.Model):       # reference data, editable
    code                # "LSDT" | "HSDT" | "CSLT"
    name
    min_concrete_age_days               # 7 / 14 / 7
    sequence_order                      # HSDT=1, CSLT=2, LSDT=3

class PileActivity(models.Model):
    pile                # FK
    activity_type       # FK
    status              # see state machine below
    designated_by_gcr   # bool — true for HSDT/CSLT selections
    scheduled_for
    performed_at
    performed_by        # FK user

    def earliest_permitted_date(self):
        # concreting_finished_at + activity_type.min_concrete_age_days

class FieldDataSheet(models.Model):
    activity            # FK PileActivity
    template            # FK FormTemplate
    data                # JSONField — answers keyed by template field id
    completed_at, completed_by
```

`PileActivity` rather than `PileTest` is deliberate. Bored pile
*construction* activities (boring, cage installation, concreting) will
eventually live in the same table. Generalising now costs a day;
retrofitting costs weeks.

### PileActivity status

```
assigned → wir_approved → tested → evaluating → with_gcr → closed
                                                      ↓
                                                  reopened → (back to with_gcr)
```

## submittals

```python
class WIR(models.Model):
    reference           # full string
    project_code, contractor_code, package_code,
    originator_code, doc_type_code, serial      # parsed components
    activity_type       # FK — one WIR per test method

class WIRRevision(models.Model):
    wir                 # FK
    rev                 # "A", "B", "C"
    state               # see state machine
    prepared_by, qc_signed_by                   # Part A
    part_b_checked_by, part_b_may_proceed       # Part B
    decision            # NONO | NONOC_C | NONOC_B | NOR   Part C
    decided_by, decided_at
    submitted_at
    supersedes          # FK self, nullable

class WIRAttachment(models.Model):
    revision            # FK
    slot                # which of the 5 required categories
    document            # FK documents.Document

class WIRActivity(models.Model):    # a WIR covers one or more piles
    revision            # FK
    activity            # FK testing.PileActivity
```

### WIRRevision state machine

```
draft → submitted → part_b_checked → decided
                          ↓
                   (may_not_proceed) → superseded, new revision created
```

Implemented as an explicit transition table. One function per transition,
in `submittals/services.py`. Each emits exactly one `Event`. Nothing else
assigns to `state`.

Completeness validation runs on `draft → submitted`: all five required
attachment slots filled, unless the cube-result slot is not applicable
(see Q7).

## documents

```python
class DocumentType(models.Model):   # reference data — the nine sections
    code, name, sort_order
    requires_revision   # bool

class Document(models.Model):
    pile                # FK, nullable — most documents belong to a pile
    doc_type            # FK
    title
    storage_key         # object storage key; bytes never overwritten
    checksum_sha256
    size_bytes, content_type
    uploaded_by, uploaded_at
    supersedes          # FK self, nullable
    superseded_by       # reverse
```

Upload flow: client requests a presigned PUT → uploads direct to storage
→ confirms to the API → metadata row created. Download: API checks
permission → issues a presigned GET valid ≤ 15 minutes → logs the access.

## tracking

```python
class Event(models.Model):
    actor               # FK user, nullable for system events
    action              # "wir.submitted", "activity.tested", ...
    object_type         # "WIRRevision" | "PileActivity" | "Document"
    object_id
    from_state, to_state
    payload             # JSONField
    occurred_at         # indexed

    class Meta:
        indexes = [(object_type, object_id, occurred_at), (action, occurred_at)]
```

**Append-only.** Enforce it: override `save()` to raise on an existing
pk, override `delete()` to raise, and add a database trigger denying
UPDATE and DELETE. A test asserts all three.

Every SLA figure, every dashboard number and the whole audit trail are
queries over this table. There are no stored duration columns anywhere.

```python
class Membership(models.Model):     # identity
    user, organisation, package, role
```

## Derived, never stored

- Clock 1 and Clock 2 durations
- Column dwell medians
- Coverage against the 100 / 10 / 3 quotas
- Anything on the board header tiles

Cache these for a few minutes rather than computing per request. They do
not need to be live to the second.

## The board endpoint

The Flow board shows cards joining registry, testing, submittals,
documents and tracking. Do not compose this on the client from REST
resources — build one purpose-made read endpoint returning exactly the
render shape:

```
GET /api/v1/board?package=5&structures=PR12-PR18&method=LSDT

{
  "header": { "coverage": [...], "in_flight": 48, "clock1_median_days": 6.5, ... },
  "columns": [
    { "key": "assigned", "name": "...", "count": 182,
      "dwell_median_days": 4, "target_days": null,
      "cards": [ { "pile_no": "P5-PR16-12", "detail": "...", "pack": "0/5",
                   "assignee_initials": "MS", "age_days": 2, "flag": null } ] }
  ]
}
```

This is a deliberate exception to clean resource design. Forty cards
composed client-side is either forty round trips or a very ugly client.

## Import

Bulk pile import from CSV/XLSX survey exports is a module, not a script.
It needs a dry run, a per-row error report, and re-import without
creating duplicates (match on `pile_no`). Expect the real files to be
messier than the sample.

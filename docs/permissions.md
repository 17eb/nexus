# Permissions

Build this before any endpoint exists. It is the single highest-value
test suite in the project and the area where generated code is most
likely to be plausibly wrong.

## The ladder

Every request passes four checks, in this order:

| # | Check | Failure |
|---|---|---|
| 1 | Authenticated? | **401** |
| 2 | Member of the target package? | **404** |
| 3 | Does the role hold the `(action, object_type, doc_type)` grant? | **403** |
| 4 | Does the object's current state permit this action? | **409** |

**Step 2 returns 404, not 403, deliberately.** A non-member must not be
able to learn that a record exists by probing IDs. This is a security
decision, not a style preference — do not "fix" it to 403.

Every list query is scoped by membership at the queryset level, so a
forgotten check fails closed rather than leaking rows.

```python
def check_permission(user, action, object_type, obj=None, doc_type=None):
    """Raises NotAuthenticated / NotFound / PermissionDenied / Conflict."""
```

One function. No hand-rolled checks in views, serializers, admin actions
or management commands.

## The doc_type dimension

The third argument is not optional padding. A geotechnical investigation
subcontractor may upload to *Geotechnical Reports* and nowhere else.
Carrying `doc_type` in the grant tuple from the start means that role
costs nothing. Adding it later is a schema migration plus an audit of
every call site.

## Roles

Two overlapping vocabularies exist. Store the operational role; the
User 0–3 tiers are a summary of upload/view breadth, not separate roles.

| Role | Org | Does |
|---|---|---|
| `creator` | HDDAJV | Everything. Project setup, reference data, user admin. (User 0) |
| `admin` | HDDAJV | Uploads to any section, edits any record. (User 1) |
| `bored_pile_manager` | HDDAJV | Issues look-ahead schedules, assigns activities |
| `office_engineer` | HDDAJV | Prepares and submits WIRs |
| `qc_engineer` | HDDAJV | Signs WIR Part A |
| `pile_test_engineer` | HDDAJV | Fills field data sheets, uploads raw test reports |
| `geotech_engineer` | HDDAJV or 3rd party | Produces and submits evaluation reports |
| `subcontractor` | 3rd party | Uploads to assigned document types only. (User 2) |
| `gcr_reviewer` | GCR | Part B check, Part C decision, comments |
| `viewer` | any | Read only. Download needs admin grant. (User 3) |

**Unresolved:** whether `geotech_engineer` is HDDAJV-internal or a third
party. If third party, evaluation crosses a second organisational
boundary and needs its own submittal step and clock. This is structural.
See `docs/open-questions.md` Q2. Build the internal case; keep the
`Membership.organisation` field so the other case is a data change.

## Matrix

`✓` allowed · `—` denied · `own` only records they created or are assigned

| Action | creator | admin | bp_mgr | office_eng | qc_eng | pile_test_eng | geotech_eng | subcon | gcr | viewer |
|---|---|---|---|---|---|---|---|---|---|---|
| view pile | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| import piles | ✓ | ✓ | — | — | — | — | — | — | — | — |
| edit pile | ✓ | ✓ | — | — | — | — | — | — | — | — |
| assign activity | ✓ | ✓ | ✓ | — | — | — | — | — | — | — |
| designate HSDT/CSLT | ✓ | — | — | — | — | — | — | — | ✓ | — |
| create WIR draft | ✓ | ✓ | — | ✓ | — | — | — | — | — | — |
| sign WIR part A | ✓ | — | — | — | ✓ | — | — | — | — | — |
| submit WIR | ✓ | ✓ | — | ✓ | — | — | — | — | — | — |
| WIR part B check | ✓ | — | — | — | — | — | — | — | ✓ | — |
| WIR decision | — | — | — | — | — | — | — | — | ✓ | — |
| fill field data sheet | ✓ | ✓ | — | — | — | ✓ | ✓ | — | — | — |
| upload raw report | ✓ | ✓ | — | — | — | ✓ | — | — | — | — |
| upload evaluation | ✓ | ✓ | — | — | — | — | ✓ | — | — | — |
| upload document | ✓ | ✓ | — | — | — | own | own | scoped | — | — |
| download document | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | scoped | ✓ | granted |
| comment on WIR | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | — |
| view dashboards | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| manage users | ✓ | — | — | — | — | — | — | — | — | — |
| manage reference data | ✓ | ✓ | — | — | — | — | — | — | — | — |

`scoped` = only the document types granted to that subcontractor.

### Separation of duties

- The user who uploads an evaluation report cannot be the user who
  records its GCR decision.
- A GCR reviewer cannot edit contractor-side records.
- No role can delete a `Document` or an `Event`. Supersession only.

## The test suite

Write this before the endpoints. Parameterise over the whole matrix:

```python
@pytest.mark.parametrize("role,action,object_type,expected", MATRIX)
def test_permission_matrix(role, action, object_type, expected):
    ...
```

Plus explicit cases for:

- Non-member gets **404**, not 403, on a record that exists
- Every list endpoint returns zero rows for a non-member
- Editing a `submitted` WIR returns **409**
- Deciding a WIR twice returns **409**
- Uploading to a document type outside a subcontractor's grant → **403**
- Separation-of-duties violations → **403**

A new endpoint without a corresponding matrix row is incomplete work.

# MVP build plan

Scoped for one part-time developer working with coding agents. Every
milestone ends in something demonstrable.

**Working method.** One branch per task. `make check` green before a task
is done. Open a PR against your own repo and read the whole diff before
merging. Squash on merge.

**Do not run two agents on tasks that both generate migrations.** If a
task's checklist includes a model change, it holds the migration lock.

---

## M0 · Foundations (before any feature)

- [ ] Django project, six empty apps, PostgreSQL, settings split
- [ ] `Makefile` with `check`, `test`, `dev`, `fixtures`
- [ ] ruff, mypy, pytest, factory_boy, import-linter configured
- [ ] import-linter contract enforcing module boundaries — with a
      deliberately failing cross-import to prove the rule fires, then
      removed
- [ ] GitHub Actions running `make check` on every push
- [ ] Branch protection on `main` requiring CI green
- [ ] Vite + React + TS + Tailwind, dark/light theme tokens
- [ ] i18next wired, one string translated into all five modes to prove it
- [ ] `.env.example`; `.env`, `media/`, real project files gitignored

**Done when:** `make check` passes on a fresh clone, CI is green, and the
import rule demonstrably fails on a cross-module import.

---

## M1 · The spatial skeleton — the demo that matters

This is the milestone you show the pile test team. No auth logic, no
workflow. Everything else is built on top of it.

- [ ] `registry` models: Package, Structure, PileCap, Pile
- [ ] `documents` models: DocumentType (the nine sections), Document
- [ ] Synthetic fixture: one package, six piers, mixed 4/6/9-pile caps,
      one straddle cap, realistic EPSG:3123 coordinates
- [ ] CSV/XLSX pile import with dry-run, per-row errors, idempotent
      re-import matched on `pile_no`
- [x] `GET /api/v1/packages/{id}/piles` returning coordinates — **not
      status**: no `PileActivity`/`Document` data exists yet to derive
      one from (`testing`/`documents` apps don't exist), so that part of
      this line isn't built. Unauthenticated pending M2's
      `check_permission()`; see `# TODO(M2)` on the queryset in
      `apps/registry/services.py`.
- [ ] `CorridorMap`: Leaflet, Esri World Imagery basemap, proj4
      EPSG:3123 → WGS84, one marker per pier, clustered
- [ ] `PilePlanView`: SVG cap plan from pile coordinates, rotated to
      chainage bearing, labels A–I, clickable piles
- [ ] Pile record page: the nine document sections, empty states
- [ ] Presigned upload + download of a PDF into one section
- [ ] Marker colour reflects document presence

**Done when:** you can open the app, see the corridor, click a pier, see
the correct cap layout, click pile P-1045S, upload its bored pile record,
and the pin changes colour. On a phone as well as a laptop.

**Validate before building:** get one real as-built survey export and
confirm the coordinate system with the survey team. If the EPSG is wrong,
everything plots in the wrong hemisphere-ish place and you want to know
in week one.

---

## M2 · Identity and the permission ladder

- [ ] `identity`: User, Organisation, Membership, grants
- [ ] `check_permission()` implementing the four-step ladder
- [ ] Queryset-level membership scoping on every list endpoint
- [ ] Admin-created accounts, login, logout, session cookies
- [ ] Parameterised test over the full role matrix in
      `docs/permissions.md`
- [ ] Explicit tests: non-member gets 404 not 403; list endpoints return
      zero rows for non-members; subcontractor doc-type scoping
- [ ] Frontend auth guard and role-aware navigation

**Done when:** the matrix test passes and every existing M1 endpoint goes
through the ladder. No endpoint has a hand-rolled check.

---

## M3 · Events — the keystone

Retrofit onto M1/M2 now, while there is little to retrofit.

- [ ] `Event` model, append-only
- [ ] Enforcement at three levels: `save()` override, `delete()`
      override, DB trigger denying UPDATE and DELETE
- [ ] Test asserting all three refuse
- [ ] Emit events for: document uploaded, document superseded, pile
      imported, user granted access
- [ ] PH working-day calendar in `tracking/calendar.py`, holidays as
      editable reference data
- [ ] `tracking` import-linter rule: may read other modules' services,
      may not write

**Done when:** every state-changing action in the app produces exactly
one event, and attempts to modify an event fail at the database.

---

## M4 · Activities and field data sheets

- [ ] `ActivityType` reference data with `min_concrete_age_days` and
      `sequence_order`
- [ ] `PileActivity` with the status state machine and transition
      functions in `services.py`
- [ ] Auto-assign LSDT to every pile on import
- [ ] Manual designation of HSDT/CSLT piles (GCR role)
- [ ] `earliest_permitted_date()` validation, with a clear error naming
      the concreting date and the required age
- [ ] Sequence validation: HSDT before CSLT before LSDT where multiple
      apply
- [ ] `FormTemplate` + `FieldDataSheet`, one LSDT template
- [ ] Tablet-shaped field sheet form, drafts in `localStorage`, warns on
      navigate-away with unsaved data
- [ ] Raw test report upload → emits the event that starts Clock 1

**Done when:** a pile test engineer can complete an LSDT field sheet on a
tablet, upload the raw report, and the concrete-age rule blocks a test
scheduled too early with an error a non-programmer understands.

---

## M5 · WIR and the review chain

- [ ] `WIR`, `WIRRevision`, `WIRAttachment`, `WIRActivity`
- [ ] Reference parsing into components, and formatting back out
- [ ] Revision state machine with transition functions
- [ ] Attachment completeness validation on submit (the five slots)
- [ ] Part A → Part B → Part C flow with the right role at each step
- [ ] Decisions NONO / NONOC_C / NONOC_B / NOR with comments
- [ ] NONOC and NOR create the next revision; the chain is preserved and
      queryable
- [ ] Evaluation report upload → stops Clock 1, starts Clock 2
- [ ] Decision recorded → stops Clock 2
- [ ] Separation-of-duties enforcement

**Done when:** one pile goes through a complete cycle including a NONOC
resubmission, and the full revision history renders on the pile page with
actors and timestamps.

---

## M6 · Views over the data

Everything here is a query. No new domain state.

- [ ] `GET /api/v1/board` — the denormalised board endpoint
- [ ] Flow board: six columns, dwell medians with target comparison,
      cards move by action only, never by drag
- [ ] Header tiles: coverage as a 3 methods × 2 structure-kinds matrix,
      not a single merged figure
- [ ] Coverage calculation parameterised over the assigned / executed /
      accepted interpretation (Q1)
- [ ] Clock 1 and Clock 2 medians against targets
- [ ] Search and filter by pile no., WIR ref, status, method, date
- [ ] Saved views: two or three per role
- [ ] Data quality view: piles missing coordinates, activities with no
      WIR, WIRs with incomplete packs
- [ ] Short-lived caching on aggregates

**Done when:** the board's figures match a manual reconciliation done by
hand from the same data.

---

## M7 · Ready to pilot

- [ ] Backup configured **and a restore rehearsed on a real dump**
- [ ] Alerting specifically on failed backup jobs
- [ ] Sentry, uptime check
- [ ] Korean and Japanese translations for the pile record and field
      sheet screens
- [ ] Audit log view for `creator`
- [ ] Written cutover date; no historical migration
- [ ] A documented path back to paper

**Done when:** a restore has actually been performed, not merely
configured.

---

## Explicitly deferred

Do not build these without being asked: offline sync, HSDT and CSLT
workflow screens (the LSDT skeleton must prove out first), auto-assembled
WIR packs, DMS export, PDF report generation, notifications and
escalations, delegation/out-of-office, archival, multi-tenancy, SSO,
construction records, PIT/PDA/CSL raw curve parsing.

---

## Running in parallel with the build

These are not code and they unblock the most expensive unknowns. All five
can run concurrently and none needs a line of code written.

1. **Is a contractual DMS the mandated submittal channel?** If yes and
   there is no export path, this becomes a preparation workspace rather
   than a submittal system. Answer before M5.
2. **Get the confidentiality and hosting position in writing** (Q16).
   Blocks using real data anywhere off a local machine.
3. **Collect real sample files**: one as-built survey export, one of each
   WIR attachment type, one filled field data sheet per method. Confirm
   the coordinate system with the survey team.
4. **Escalate the quota denominator question** (Q1) with the three
   interpretations written out so contracts can pick one.
5. **Talk to one GCR reviewer.** Their adoption is the biggest risk, and
   their view should be designed to help them (their queue, oldest first,
   pack attached) rather than to score their turnaround.

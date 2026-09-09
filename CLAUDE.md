# CLAUDE.md — Bored Pile Testing Management (BPTM)

Read this file first. Then read the doc for the module you are working in.

## What this is

A spatial record system for bored pile testing on SCRP Packages 4–6.
Engineers open a map, click a pile, and see every document and test
result for that pile. Behind the map sits a submittal workflow (WIR →
test → evaluation → GCR decision) whose history must be defensible in a
contractual dispute.

**Map-first.** The map is the primary navigation surface, not a feature.
If a change makes the map worse to reach a record, it is the wrong change.

## Stack

| Layer | Choice |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 |
| Frontend | Vite + React 18 + TypeScript + Tailwind |
| Server state | TanStack Query (no Redux, no Zustand) |
| Map | Leaflet + proj4js |
| Files | django-storages (filesystem local, S3-compatible in prod) |
| Auth | Django auth + DRF SessionAuthentication |
| i18n | Django gettext + i18next |
| Tests | pytest, pytest-django, factory_boy |

**Not in the MVP.** Celery, Redis, PostGIS, offline sync, service workers,
PWA install, JWTs, django-allauth, microservices, GraphQL, Docker Compose
beyond a local Postgres. Do not add any of these without being asked.

## Module layout

```
apps/
  identity/    users, orgs, memberships, permission grants
  registry/    packages, structures, pile caps, piles, coordinate import
  testing/     PileActivity, field data sheets, raw reports
  submittals/  WIR, revisions, attachments, decisions
  documents/   file metadata, storage keys, checksums, supersession
  tracking/    events, SLA computation, board and dashboard queries
```

### Boundary rule

Each module exposes `services.py` as its public interface. Cross-module
imports of another module's `models` or internals are forbidden and
checked in CI by import-linter.

`tracking` reads events and never writes domain state.

If you need data from another module, call its service function. If the
service function you need does not exist, add it to that module rather
than reaching into its models.

## Three invariants — never violate these

1. **`Event` is append-only.** No `update()`, no `delete()`, no
   `save()` on an existing row. Ever. Every SLA number, every dashboard
   figure and the audit trail all derive from this table.

2. **State changes go through transition functions.** `WIRRevision.state`
   and `PileActivity.status` are only ever changed by the transition
   functions in that module's `services.py`. Never `obj.state = "x";
   obj.save()` in a view, serializer, admin action or management command.
   Every transition emits exactly one `Event`.

3. **Every endpoint goes through `check_permission()`.** See
   `docs/permissions.md`. List endpoints scope at the queryset level so a
   missing check fails closed. Never hand-roll a permission check.

If a task seems to require breaking one of these, stop and say so instead.

## Conventions

- Business logic lives in `services.py`. Views are thin: parse, call a
  service, serialize. No ORM queries in views beyond a scoped queryset.
- Raise domain errors as `DomainError` subclasses in `services.py`; a DRF
  exception handler maps them to status codes. Views do not build error
  responses by hand.
- All user-facing strings pass through `gettext` (backend) or `t()`
  (frontend). No bare English strings in templates or components.
- Money, no. Measurements, yes: store lengths in metres as `Decimal`,
  never float. Elevations can be negative.
- Timestamps are timezone-aware UTC in the database. Working-day
  arithmetic uses the PH holiday calendar in `tracking/calendar.py`.
- File bytes are never overwritten. A new version is a new `Document` row
  with `supersedes` set.

## Frontend conventions

- Server state is TanStack Query. Local UI state is `useState`. There is
  no global store.
- Two map components, and they are not interchangeable:
  - `CorridorMap` — Leaflet, satellite tiles, real coordinates
    transformed to WGS84 by proj4. Pier-level markers.
  - `PilePlanView` — plain SVG, no Leaflet. Pile cap plan drawn from
    pile coordinates normalised to a local origin and rotated to the
    package chainage bearing.
- Dark and light theme via Tailwind `class` strategy and CSS variables.
  No hardcoded hex outside the theme definition.
- No `<form>` submit handlers that rely on page navigation. Use onClick
  handlers and the API client.

## Running things

```bash
make check       # ruff + mypy + import-linter + pytest — must pass before you say done
make test        # pytest only
make dev         # runserver + vite
make fixtures    # load the synthetic package into a fresh db
```

Run `make check` before claiming a task is complete. If it fails, fix it
or report the failure. Do not weaken a test to make it pass, and do not
mark a test `skip` or `xfail` to get green.

## Data policy while building

**Use synthetic data only.** Real SCRP project data must not be committed
or uploaded to third-party infrastructure until the confidentiality
question is answered in writing. `make fixtures` generates a realistic
synthetic package. Never commit real drawings, borelogs, reports or
survey exports.

## Git

- Branch per task: `feat/`, `fix/`, `chore/`, `refactor/`.
- Small commits, imperative messages that say *why*.
- Never commit directly to `main`.
- One migration-generating task at a time. If your branch and `main` both
  add a migration, regenerate rather than hand-merging.
- Never commit `.env`, real project files, or anything under `media/`.

## Where to look

| Question | File |
|---|---|
| What does this domain term mean | `docs/domain.md` |
| What are the tables | `docs/data-model.md` |
| Who can do what | `docs/permissions.md` |
| Why is it built this way | `docs/decisions.md` |
| What am I building next | `docs/mvp-plan.md` |
| What is still unknown | `docs/open-questions.md` |

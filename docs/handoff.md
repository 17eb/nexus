# Handoff

Written 2026-09-10. Read `CLAUDE.md` first, then this. State below is
verified on `main` at commit `35f6d04` (merged PRs #1 and #2).

## Goal

Bored Pile Testing Management (BPTM) — spatial record system for bored
pile testing on SCRP Packages 4–6. Full spec in `CLAUDE.md` + `docs/`.
Currently mid-M1 ("the spatial skeleton" — `docs/mvp-plan.md`): get the
`registry` data model, pile import, and a read endpoint in place before
any frontend or auth work.

## Current state

**Built and verified (49/49 tests passing, `manage.py check` clean,
`lint-imports` clean, confirmed by hand against the synthetic fixture):**

- Django project scaffold (`nexus/`) — settings split, Postgres via env
  vars, no CI/Makefile/frontend (that's M0, mostly not done — see
  `docs/mvp-plan.md`'s M0 section, which is now accurately annotated
  rather than aspirational).
- `apps/registry` app: `Package`, `Structure`, `PileCap`, `Pile`,
  `ImportRun` models (one migration, `0001_initial`).
- Two-mode (`design`/`as_built`) pile import
  (`apps/registry/import_piles/`, entry point
  `services.import_piles()`), with an import-linter contract keeping
  `import_piles/` internal to `services.py`. CLI:
  `manage.py import_piles` / `manage.py generate_fixture_piles`.
- `GET /api/v1/packages/{id}/piles` — first and only HTTP endpoint. See
  "Key decisions" below for the coordinate-fallback and auth situation.
- Synthetic fixture: package `S-05`, 6 piers, 4/6/9-pile caps + one
  straddle pier, loaded via `manage.py generate_fixture_piles`.

**Not built:** `documents`/`identity`/`testing`/`submittals`/`tracking`
apps, any frontend, auth/permissions, `Event` log, CI, `Makefile`. See
`docs/mvp-plan.md` for the full checklist — it's now kept honest
(partial items are annotated, not just checked or unchecked).

**Untested / not verified:** nothing known-broken. The endpoint's
behavior at real scale (thousands of piles) is untested — only checked
up to ~40 piles (the synthetic fixture + a 9-pile query-count test).

## Key decisions

- **UUID primary keys** on all registry models, not auto-increment —
  matches the anti-enumeration stance already implied by
  `docs/permissions.md`'s 404-not-403 rule.
- **Coordinate display rule** (`docs/data-model.md`: as-built when
  present, else design, mark which) lives as three `@property`s on
  `Pile` (`coordinate_source`, `display_e`, `display_n` —
  `apps/registry/models.py`), not duplicated in the serializer or
  anywhere else. `asbuilt_e`/`asbuilt_n` are always written together by
  the importer, so checking one is a reliable presence check.
- **`ImportRun`** is pile-import-specific provenance (`created_by_run`,
  `asbuilt_run` on `Pile`), explicitly *not* a stand-in for the M3
  `Event` append-only log — narrower scope, no append-only enforcement.
- **`GET /piles` is unauthenticated on purpose.** `check_permission()`
  doesn't exist until M2. `# TODO(M2)` sits directly on the queryset in
  `services.get_piles_for_package()`. A test
  (`test_no_auth_required`) pins today's open behavior so an accidental
  lock-down (or an accidental continued absence of one, once M2 lands)
  fails loudly.
- **`diameter_mm` is an int, not Decimal** — CLAUDE.md's "measurements
  as Decimal" rule is about metres; this field's unit is mm.
- **Import-linter contract is intra-app only for now**
  (`apps.registry.import_piles` internal to `apps.registry.services`,
  in `pyproject.toml`) — the real cross-*module* contract CLAUDE.md
  describes needs the other five apps to exist first.
- **Q19 added to `docs/open-questions.md`**: the import's per-package
  `pile_no` uniqueness enforcement (`upsert.py`) assumes `pile_no` is
  genuinely project-wide unique, not just per-package. Unconfirmed
  against the real site numbering scheme.
- **Q8 (real-world CRS) is still open and still blocking** for real
  data — `docs/open-questions.md`. Everything is parameterized on
  `Package.crs_epsg`, nothing hardcoded, but don't import a real survey
  export until this is confirmed with the survey team.

## Files changed (this build, cumulative)

- `nexus/settings/{base,dev,test}.py`, `manage.py`, `pyproject.toml` —
  project scaffold.
- `apps/registry/models.py` — the five models + the three coordinate
  properties on `Pile`.
- `apps/registry/services.py` — public interface:
  `import_piles()`, `get_piles_for_package()`.
- `apps/registry/import_piles/{parser,validators,upsert,report}.py` —
  import internals, not to be imported from outside `services.py`.
- `apps/registry/{serializers,views,urls}.py` — the pile-list endpoint.
- `nexus/urls.py` — wires `apps.registry.urls` under `api/v1/`.
- `apps/registry/management/commands/{import_piles,generate_fixture_piles}.py`
  — CLI.
- `apps/registry/fixtures/synthetic/*.csv` — hand-fixed demo data (not
  random — deterministic on every run).
- `apps/registry/tests/` — 49 tests across models, both import modes,
  provenance, the management command, and the endpoint.
- `docs/data-model.md`, `docs/mvp-plan.md`, `docs/open-questions.md` —
  kept in sync with what actually got built (not aspirational).

## Dead ends

- **`python3 -m venv .venv` fails on this machine** — `ensurepip` isn't
  available. Fix: `pip install --user --break-system-packages
  virtualenv`, then `python3 -m virtualenv .venv`.
- **Returning a raw `Decimal` from a DRF `SerializerMethodField`
  silently loses precision** — DRF's automatic decimal→string coercion
  only applies to *declared* serializer fields (`serializers.DecimalField`);
  a `SerializerMethodField` returning a bare `Decimal` falls through to
  the JSON encoder's `float()` fallback (`"498000.030"` →`498000.03`).
  Always `str()` explicitly in a method field. Caught by comparing
  against real rendered JSON (`response.json()`), not DRF's pre-render
  `response.data` — the latter hides this bug entirely.
- **A direct `git push` landed on `main` without a PR** earlier this
  session (fast-forward, so git allowed it silently). Nothing enforces
  the PR-only workflow `CLAUDE.md` documents — **branch protection on
  `main` is not configured on GitHub.** Until it is, this can happen
  again by habit, not malice.
- System clock reads 2026 — confirmed correct/intentional, not a bug.
  Don't waste time on it again.

## Next steps

In `docs/mvp-plan.md`'s own order:

1. **Turn on branch protection on `main`** (require PR + status checks)
   — offered, not yet done, no CI exists to require yet either.
2. Finish M1: `documents` app (`DocumentType`, `Document`),
   `CorridorMap`/`PilePlanView` (frontend doesn't exist at all yet),
   pile record page, presigned upload, marker colour by doc presence.
3. Or M0 properly: `Makefile`, ruff/mypy, GitHub Actions running
   `make check`, Vite+React+Tailwind scaffold, i18next.
4. Before importing any **real** survey data: resolve Q8 (CRS) with the
   survey team — see `docs/open-questions.md`.
5. Housekeeping: two local branches
   (`docs/update-m0-checklist-status`, `feat/registry-models-and-pile-import`)
   are fully merged and can be deleted.

## Commands

```bash
# one-time env setup (see "Dead ends" re: venv)
pip install --user --break-system-packages virtualenv
python3 -m virtualenv .venv
.venv/bin/pip install -e ".[dev]"

# local Postgres (already running as `nexus-postgres` container;
# recreate if it's gone)
docker run -d --name nexus-postgres -e POSTGRES_DB=nexus_dev \
  -e POSTGRES_USER=nexus -e POSTGRES_PASSWORD=nexus \
  -p 5432:5432 postgres:16

.venv/bin/python manage.py migrate
.venv/bin/python manage.py generate_fixture_piles   # loads synthetic S-05
.venv/bin/python manage.py runserver

.venv/bin/python -m pytest apps/registry -q          # 49 tests
.venv/bin/python manage.py check
.venv/bin/lint-imports
```

No `.env` file needed for local dev — `nexus/settings/dev.py` supplies
working defaults. `.env.example` documents the variables `base.py`
actually requires (fails loud if unset outside `dev`).

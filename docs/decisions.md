# Decisions

Why the code looks the way it does. If a change would contradict one of
these, raise it rather than working around it.

---

## D1 — The map is the information architecture, not a feature

**Decision.** The corridor map is the default landing view and the
primary way to reach any record.

**Why.** The problem being solved is finding one pile's PDF among
thousands. Aconex and similar systems already do document storage well;
what they cannot do is spatial understanding. A pile's location is the
one attribute an engineer always knows, and the map turns that into
navigation.

**Consequence.** The map ships in the first milestone, before the WIR
workflow. Search, board and list views are alternative front doors to the
same index, not replacements for it.

**Honest caveat.** The map only works if every document is a row that
knows its pile, type and revision. Without that, the map is pins with
nothing behind them. Structured registry first, map immediately after.

---

## D2 — Two map components, not one

**Decision.** `CorridorMap` (Leaflet, georeferenced, satellite tiles) and
`PilePlanView` (plain SVG, schematic) are separate components with
separate jobs.

**Why.** Piles are Ø1.5 m at 4.5 m spacing on a 55.6 km corridor. At
corridor zoom a pile cap is sub-pixel; at pile zoom you see one cap and
no context. No single view does both.

**Consequence.** `PilePlanView` takes pile coordinates, normalises them
to a local origin, rotates to the package chainage bearing and draws
circles. It does not use Leaflet, it prints cleanly, and it does not
fight the map's zoom model.

---

## D3 — Piles carry their own coordinates; pile caps have no pile count

**Decision.** No `pile_count` field. Cap geometry derives from the
positions of its child piles.

**Why.** Caps have 3, 4, 6 or 9 piles, plus straddle caps with two
groups. Storing a count means storing a layout rule per count, then
hardcoding grid positions, then special-casing straddles.

**Consequence.** Every configuration works with one code path. The
requested "user can dynamically change the number of piles in a cap"
becomes free — it is just adding or removing child rows.

---

## D4 — `Event` is append-only and everything derives from it

**Decision.** One append-only event table. No stored durations, no status
history columns, no denormalised SLA fields.

**Why.** These records may be used as evidence in a contractual claim.
An immutable log is what makes the history defensible. It also means SLA
logic can be changed later without risking workflow correctness, because
`tracking` only ever reads.

**Consequence.** Enforced at three levels: model `save()`/`delete()`
overrides, a database trigger denying UPDATE and DELETE, and a test
asserting both. Clocks, dwell medians and coverage figures are all
queries, cached for minutes.

**Cannot be retrofitted.** Build it in the first milestones, before there
is much history to lose.

---

## D5 — Session cookies, not JWTs

**Decision.** DRF `SessionAuthentication` with `HttpOnly`, `Secure`,
`SameSite=Lax` cookies. No `django-allauth`, no token in `localStorage`.

**Why.** JWTs solve stateless horizontal scaling, which this application
does not have. Meanwhile a token in `localStorage` is readable by any XSS,
and revocation matters when someone leaves the project mid-contract.

---

## D6 — Modular monolith with enforced boundaries

**Decision.** Six Django apps, each exposing `services.py`. Cross-module
model imports forbidden, checked by import-linter in CI.

**Why.** Microservices solve organisational scaling — independent teams
deploying independently. There is one developer. The real risk is not
choosing a monolith, it is choosing a monolith and letting every module
import every other module.

**Consequence.** The boundary is what makes a task fit in one agent's
context without reading the whole repo, and what keeps future extraction
cheap. Intention is not enough; the CI rule is the mechanism.

---

## D7 — `PileActivity`, not `PileTest`

**Decision.** The activity table is generic from the start, with
`ActivityType` as reference data.

**Why.** Bored pile *construction* activities (boring, cage, concreting)
are the obvious next scope, and they share the same shape: an obligation
against a pile, with a WIR, a record and a decision. Generalising now
costs about a day. Retrofitting costs weeks.

---

## D8 — i18n wired on day one

**Decision.** `gettext` on the backend and i18next on the frontend from
the first milestone, even with only English translated.

**Why.** English, Korean and Japanese, plus paired modes, are a real
requirement with Hyundai and Dong-Ah on the job. Retrofitting means
touching every template and component ever written.

---

## D9 — Deliberately excluded from the MVP

| Excluded | Reason |
|---|---|
| Offline sync / service worker / PWA install | Longest and least predictable task; the connectivity survey has not been done. `localStorage` drafts cover most of the real risk. |
| Celery + Redis | No background job exists yet. Add when one does. |
| PostGIS | Coordinates are numerics; the transform happens in the browser. Add when a genuine spatial query appears. |
| Microservices, Kubernetes, GraphQL | Solving problems this project does not have. |
| Historical data migration | Set a cutover date. Do not backfill. |
| Being the contractual system of record | Unresolved whether a mandated DMS exists. Position as a preparation and tracking workspace until answered. |

---

## D10 — Synthetic data until the hosting question is answered

**Decision.** No real SCRP files in the repo or on third-party
infrastructure until confidentiality and data-residency positions are
confirmed in writing.

**Why.** This is a live international infrastructure contract. The
constraint is real and immediate, and it costs nothing to respect while
building.

**Consequence.** `make fixtures` generates a realistic synthetic package.
Real files are obtained early for *shape* analysis, examined locally, and
not committed.

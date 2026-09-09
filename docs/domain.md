# Domain reference

Written for someone with no construction background. Every rule here came
from the project team; do not invent additional rules.

## The project

South Commuter Railway Project (SCRP), Packages 4, 5 and 6 — an elevated
viaduct railway, 55.6 km, nine stations.

| Package | Code | Length | Stations |
|---|---|---|---|
| 4 | S-04 | 8.5 km | 2 |
| 5 | S-05 | 12.8 km | 4 |
| 6 | S-06 | 10.2 km | 3 |

Three organisations:

- **DOTr** — Employer (Department of Transportation)
- **GCR** — the Engineer / Consultant / Supervisor. Reviews and approves.
- **HDDAJV** — the Contractor (Hyundai E&C + Dong-Ah Joint Venture). Us.

**Why approval matters commercially:** once GCR approves the reports, the
Contractor can invoice. Approval is a payment gate, not paperwork.

## Structure vocabulary

A viaduct pier, top to bottom:

```
Pre-cast segment  (the deck the train runs on)
Pier head
Pier column
Pile cap          (concrete block tying the piles together)
Bored piles       (drilled shafts in the ground — our scope)
```

**Bored pile / drilled shaft** — a deep concrete column cast in a drilled
hole. Typically Ø1500 mm, 20–35 m long on this project.

**Pile cap** — one per pier, sitting on 3, 4, 6 or 9 piles. A **straddle
pile cap** is a pier that spans a road or obstruction; it has two pile
groups under one pier. Piles within a cap are labelled A, B, C, … I.

**Cut-off level** — the elevation the pile is trimmed to. Excess concrete
above it is chipped away by hand before the cap is cast.

> ⚠ On working drawings this is labelled **"Top of Pile"**, but it means
> the cut-off level. Two different names, one thing. Do not model them as
> separate fields.

**Chainage** — distance along the railway alignment. On SCRP 4/5/6,
increasing chainage is the **southbound** direction. This matters for
drawing the pile cap plan the same way up as the paper drawing.

## Test methods

Testing happens after the pile is cast, to verify structural integrity
and load capacity.

| Method | Full name | Equipment | Frequency |
|---|---|---|---|
| **LSDT** | Low Strain Dynamic Test (Pulse Echo) | PIT — Pile Integrity Tester | 100% |
| **HSDT** | High Strain Dynamic Test | PDA — Pile Driving Analyzer | 10% |
| **CSLT** | Crosshole Sonic Logging Test | CSL by PDI | 3% |

"LSDT" and "PIT" are used interchangeably in the field, as are "HSDT" and
"PDA", and "CSLT" and "CSL". Use the formal codes in the database, accept
the informal ones in search.

### Quota rules

The percentages are **computed separately for viaduct piles and station
piles**. So there are six coverage figures, not three:

```
LSDT: 100% of viaduct piles,  100% of station piles
HSDT:  10% of viaduct piles,   10% of station piles
CSLT:   3% of viaduct piles,    3% of station piles
```

The specific piles for HSDT and CSLT are designated in advance by GCR;
they are not chosen by us. Within one pile cap, HSDT or CSLT typically
lands on at least two piles, at the consultant's discretion.

One pile can carry all three tests.

**Unresolved:** whether the denominator counts assigned, executed or
accepted tests. Build the compliance calculation fully parameterised so
the rule can be switched. See `docs/open-questions.md` Q1.

### Test sequence and concrete age

When a pile carries more than one test, the order is fixed:

```
HSDT (PDA)  →  CSLT (CSL)  →  LSDT (PIT)
```

Minimum concrete age before each test, measured from the pile's
concreting finished date:

| Method | Minimum age |
|---|---|
| HSDT | 14 days |
| CSLT | 7 days (some standards use 11 or 14) |
| LSDT | same as CSLT |

These are configurable reference data, not constants in code — a
different standard may apply on another package.

## The workflow

```
1. Bored Pile Manager issues a look-ahead schedule of piles to be tested.
2. Office Engineer prepares a Work Inspection Request (WIR) and submits
   it to GCR. The QC Engineer signs Part A.
3. The WIR is copied to the Pile Test Engineer, who uses its contents to
   fill in the pile details on the Field Data Sheet.
4. Test is performed on site. Raw data captured on the Field Data Sheet.
5. Pile Test Engineer submits the raw / factual test report to the
   Geotechnical Engineer.                        ← starts Clock 1
6. Geotechnical Engineer produces the Evaluation Report and submits to
   GCR.                          ← stops Clock 1, starts Clock 2
7. GCR issues a decision.                        ← stops Clock 2
```

### The WIR

A Work Inspection Request is the contractual gate — no test may proceed
without one. There is one WIR per test method, so a pile carrying all
three tests appears on three WIRs.

Reference format, which is structured and should be stored in parts as
well as whole:

```
NSCR-HDDAJV-S06-ZWD-WIR-CN-026485  Rev: A
 |     |      |   |   |   |   |      |
 |     |      |   |   |   |   |      revision letter
 |     |      |   |   |   serial
 |     |      |   |   document type
 |     |      |   originator code
 |     |      package
 |     contractor
 project
```

The paper form has three parts, filled by different parties in order:

- **Part A** — Contractor. Works described, documents listed, date/time,
  requested by, QC Engineer signature.
- **Part B** — GCR initial check. May the inspection proceed? Is a
  resubmission required?
- **Part C** — GCR inspection/test result. The decision.

Required attachments for a pile test WIR:

1. Working drawings
2. Geotechnical borelog with SPT data
3. Isolated key plan
4. Bored pile records
5. Compressive strength (cube) test results, where applicable

### GCR decisions

| Code | Meaning | Consequence |
|---|---|---|
| **NONO** | Notice of No Objection | Proceed. Closed. |
| **NONOC C** | No objection with comments, category C | Proceed subject to remedial items. **Resubmission of the WIR is required.** |
| **NONOC B** | No objection with comments, category B | As above, different comment category. |
| **NOR** | Notice of Rejection | Permission not given. Remedial action, then resubmit. |

NONOC and NOR both create a new revision of the WIR. The revision chain
must be preserved intact — this is the record that would be used as
evidence in a claim.

### The two clocks

| | From | To | Measures |
|---|---|---|---|
| **Clock 1** | Pile Test Engineer uploads raw test report | Geotechnical Engineer submits evaluation | Our internal turnaround |
| **Clock 2** | Evaluation submitted to GCR | GCR issues decision | GCR's review turnaround |

Both are computed from the `Event` table, never from a stored duration
field. Both count working days on the PH calendar.

**Unresolved:** whether targets are contractually defined, and whether
the clock pauses while awaiting the other party. See Q3, Q4.

## Documents held per pile

The nine sections a user sees on a pile record:

1. Geotechnical reports
2. Bored pile records
3. Concrete records
4. Slurry sample
5. Compressive strength test results
6. Bored pile as-built survey report
7. Working drawings
8. Field data sheet
9. Deep foundation test reports / pile test reports

A later "Engineering design & analysis" section (derived geotechnical
parameters, pile length cross-checking, bearing capacity, structural
analysis) is out of MVP scope but the document type table should not
assume nine is the maximum.

## Coordinates

Pile positions come from the **as-built survey report** as easting /
northing / elevation in a projected Philippine coordinate system.

For the SCRP 4–6 corridor (Cabuyao, Laguna, ≈121.13°E), the PRS92 zone
is **EPSG:3123** (PRS92 / Philippines zone 3, central meridian 121°E,
covering roughly 120°E–122°E). Note that EPSG:3121 is zone 1, central
meridian 117°E — it is the wrong zone for this project despite appearing
on an early mockup.

⚠ **Confirm with the survey team before importing anything.** Many PH
projects work in PTM rather than PRS92 zones, and some use a project grid
with a local origin. Store the EPSG code per package rather than
hardcoding it.

proj4 definition:

```
+proj=tmerc +lat_0=0 +lon_0=121 +k=0.99995 +x_0=500000 +y_0=0
+ellps=clrk66 +towgs84=-127.62,-67.24,-47.04,3.068,-4.903,-1.578,-1.06
+units=m +no_defs
```

Every pile stores both **design coordinates** (from working drawings,
available before construction) and **as-built coordinates** (from survey,
available after). Design is the fallback position for display. The
difference between the two is itself of engineering interest, so never
overwrite one with the other.

## Scale, for sizing decisions

- Corridor: 55.6 km
- Pile diameter: typically 1500 mm
- Pile spacing within a cap: 4500 mm
- Pile length: 20–35 m
- Order of magnitude: thousands of piles across the three packages

At corridor zoom, one pile is smaller than a pixel. This is why there are
two map components rather than one.

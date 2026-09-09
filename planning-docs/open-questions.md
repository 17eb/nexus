# Open questions

Unresolved. **Do not silently pick an answer.** If a task cannot proceed
without one of these, say which question is blocking and stop.

Where a question has a "build for now" line, build that and keep the
alternative cheap to switch to.

| # | Question | Blocks | Build for now |
|---|---|---|---|
| **Q1** | Are the 10% and 3% quotas counted on **assigned**, **executed** or **accepted** tests? Viaduct and station denominators are confirmed separate. | M6 coverage | Parameterised setting, default `accepted`. Show the basis in the UI. |
| **Q2** | Is the Geotechnical Engineer HDDAJV-internal or a third party? | M5 structure | Internal. Keep `Membership.organisation` so the other case is a data change, not a rewrite. |
| **Q3** | Do the clocks count working days or calendar days, and do they pause while awaiting the other party? | M6 clocks | Working days, PH calendar, no pausing. Make the pause rule a setting. |
| **Q4** | Are Clock 1 and Clock 2 targets contractually defined? What are they? | M6 targets | Placeholder 5 and 7 days, editable reference data. |
| **Q5** | What counts as overdue — target exceeded, or a separate threshold? | M6 flags | Target exceeded. |
| **Q6** | Is a contractual DMS (e.g. Aconex) the mandated sole submittal channel? | M5 positioning | Assume it is. The tool prepares and tracks; it does not replace the channel. |
| **Q7** | When are compressive strength (cube) results "applicable" for WIR completeness? | M5 validation | Required unless explicitly marked not applicable, with a reason recorded. |
| **Q8** | Which coordinate system do the surveyors actually deliver — PRS92 zone 3 (EPSG:3123), PTM, or a project grid with a local origin? | **M1 — blocking** | Nothing. Get a real export and confirm before importing. |
| **Q9** | Are design coordinates available from working drawings before as-built survey? | M1 fallback | Yes, both fields exist and design is the display fallback. |
| **Q10** | What is the site connectivity like at the pile head? | Offline decision | No offline sync. `localStorage` drafts only. |
| **Q11** | Which CSLT concrete-age standard applies — 7, 11 or 14 days? | M4 validation | 7 days, as editable reference data. |
| **Q12** | Do HSDT and CSLT field sheets differ enough to need separate templates? | Post-MVP | Assume yes. `FormTemplate` is already per-method. |
| **Q13** | Is Philippine data residency required? | Hosting | Unresolved. Do not deploy real data anywhere until answered. |
| **Q16** | May project data be hosted on third-party infrastructure? | **Everything with real data** | No. Synthetic data only until answered in writing. |
| **Q17** | Who owns the code and the data? | Before serious investment | Unresolved. Settle in writing early. |
| **Q18** | Is there intent to sell this to other contractors? | Multi-tenancy | No. Single tenant. Do not build multi-tenancy. |
| **Q19** | Is `pile_no` guaranteed unique across the whole project, or only within a package? | Registry pile import | Assumed project-wide unique — `Pile.pile_no` has a global `unique=True`, matching `docs/domain.md`'s "project-wide identifier". Both the `design` and `as_built` importers (`apps/registry/import_piles/upsert.py`) rely on this: a `pile_no` match under a different package is treated as an error naming both packages, never as a new pile or a silent cross-package write. If uniqueness turns out to be per-package instead, the model constraint and both `upsert_*_row` package-scoping checks need to change together. |

## Answered

| # | Question | Answer | Source |
|---|---|---|---|
| A1 | Quota denominators split by structure type? | Yes — viaduct and station counted separately, for all three methods | Project slides |
| A2 | Test sequence when a pile carries several methods | HSDT → CSLT → LSDT | Project slides |
| A3 | Minimum concrete age | HSDT 14 d, CSLT 7 d, LSDT same as CSLT | Project slides |
| A4 | Can one pile carry all three tests? | Yes | Project slides |
| A5 | Does "Top of Pile" on drawings mean top of pile? | No — it means cut-off level | Project slides |
| A6 | Who selects HSDT/CSLT piles? | GCR, in advance | Project brief |
| A7 | Direction of increasing chainage on SCRP 4/5/6 | Southbound | Project slides |
| A8 | Pile cap configurations in use | 3, 4, 6, 9 piles, plus straddle caps | Project slides |
| A9 | Why does GCR approval matter commercially? | It gates the contractor's billing | Project slides |

---

## How to use this file

When an agent hits an unknown, the right behaviour is to name the
question number and stop, not to guess. A guess buried in an
implementation is far more expensive than a blocked task.

When a question is answered, move it to the Answered table with its
source, and update `docs/domain.md` in the same change.

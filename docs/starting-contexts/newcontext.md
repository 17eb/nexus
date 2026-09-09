Here is a refined, professionally structured version of your context. I have organized the information into clear categories—moving from the high-level project scope down to the specific software requirements—making it ideal for a project brief, software requirements specification (SRS), or presentation to stakeholders.

# Project Brief: Bored Pile Testing Management Tool

## 1. Project Overview

The software management tool is being developed for the **South Commuter Railway Project (Packages 4, 5, and 6)**, a major international viaduct railway infrastructure initiative.

The project relies on three primary stakeholders:

- **Employer:** DOTr (Department of Transportation)
- **Engineer (Consultant/Supervisor):** GCR
- **Contractor:** HDDAJV (Hyundai E&C and Dong-Ah Joint Venture)

**Contractor Scope:** HDDAJV is responsible for the construction of both the Substructure and Superstructure (including non-structural components like parapets).

## 2. Development Focus: Substructure (Bored Piles)

As an initial minimum viable product (MVP), the software will focus exclusively on the **Bored Pile Substructure Category**, specifically managing the **Pile Testing** workflow.

Pile testing is conducted post-construction to ensure structural integrity. The required test methods and their contractual frequencies are as follows:

| Test Method | Equipment / Standard | Required Frequency |
| --- | --- | --- |
| **LSDT** (Low Strain Dynamic Testing) | Pile Integrity Tester (PIT) | 100% of all bored piles |
| **HSDT** (High Strain Dynamic Testing) | Pile Driving Analyzer (PDA) | 10% of total bored piles* |
| **CSLT** (Crosshole Sonic Logging Test) | CSL by PDI | 3% of total bored piles* |

*Note: The specific Bored Pile IDs for PDA and CSLT are preemptively selected by the Engineer (GCR).*

## 3. Workflow & Documentation (Standard Operating Procedure)

Every bored pile construction and testing activity must be formally documented and supervised by the Engineer (GCR) through a **Work Inspection Request (W.I.R.)**.

1. **W.I.R. Submission:** The Contractor (HDDAJV) files a W.I.R. prior to any test being conducted by the Pile Test Engineer.
2. **Required W.I.R. Attachments:** To conduct PIT, PDA, or CSLT, the W.I.R. must include:
   - Working Drawings
   - Geotechnical Borelog with Standard Penetration Test (SPT) data
   - Isolated Key Plan
   - Bored Pile Records
   - Compressive Strength Test results (if applicable)
3. **Field Data Collection:** The Pile Test Engineer and Geotechnical Engineer use a Field Data Sheet—currently populated based on the W.I.R. attachments—before conducting the test.
4. **Evaluation & Reporting:** After the test, the Pile Test Engineer submits the raw test report to a Geotechnical Engineer, who evaluates it and produces the final Evaluation Report for submission to the GCR.

## 4. Software Requirements & Objectives

The primary goal of this tool is to provide Geotechnical and Pile Test Engineers with a centralized digital workspace to manage data, generate reports, and track deliverables.

**Key System Features:**

- **Digital Field Data Sheets:** Convert paper-based field data sheets into mobile/tablet-friendly digital forms that engineers can fill out directly on-site.
- **Centralized Document Management:** A single domain to store, manage, and access all W.I.R. attachments, raw pile test data, and finalized Geotechnical Evaluation Reports.
- **Automated Time & SLA Tracking:**
  - *Test-to-Evaluation:* Track the exact duration from when the Pile Test Engineer uploads the initial test report to when the Geotechnical Engineer completes the evaluation.
  - *Evaluation-to-Approval:* Track the time it takes the Engineer (GCR) to review the submitted report.
- **Submittal Status Monitoring:** Real-time dashboard tracking of GCR review statuses:
  - **NONO** (No Objection)
  - **NONOC C** (No Objection with Comments - C)
  - **NONOC B** (No Objection with Comments - B)
  - **NOR** (Notice of Rejection)

# Quality Rubric (100 points)

| # | Category | Max | Full marks when… |
|---|----------|-----|------------------|
| 1 | **Groundedness** | 15 | Every statement traces to `SRC-`/`D-`/labelled `A-`; no invented facts |
| 2 | **Clarity & unambiguity** | 15 | No unresolved ambiguity words; one meaning per sentence; consistent terms (glossary) |
| 3 | **Completeness** | 15 | All gap lenses addressed; all flow outcomes, states, permissions, errors covered; UI features have every screen and screen state defined |
| 4 | **Testability** | 15 | Every story has ≥3 Gherkin AC with concrete values; NFRs measurable |
| 5 | **Consistency** | 10 | No contradictions across files; diagrams match text; IDs unique and resolvable |
| 6 | **Traceability** | 10 | Goal → scope → story → AC → test complete both ways; no orphans |
| 7 | **Value & scope alignment** | 10 | SMART goals with baselines; every story serves a goal; out-of-scope explicit; MVP justified by the goals; business owner, PO and area owners named and decisions made by them |
| 8 | **Build-readiness (AI agent)** | 5 | Agent could implement with zero clarifying questions; "do not guess" list present |
| 9 | **Readability for each audience** | 5 | PO / team / builder each get content at the right level; scannable structure |

## Verdict
The verdict is decided by the **defects**; the score is a floor and a trend, because independent reviewers'
scores vary by about ±3 and a hard line at one number invites fix rounds that only chase points.

- **Pass** — zero Critical, every open Major has an owner and a due date (or is fixed), **and** total ≥ 80
- **Conditional** — zero Critical, but some Major has no owner or date, or total 70–79
- **Fail** — any Critical, or total < 70

Only **proven defects** (evidence at a location) count towards the verdict; *risks to verify* are listed
separately and become questions. A **team walkthrough** (Dev/Tech Lead + QA read the stories and spec and
confirm feasibility and testability, recorded as a `D-`) is part of the Review gate in standard and controlled
modes; its findings are added as defects with origin `walkthrough`.

Adjust weights to your organisation (e.g. raise Groundedness/Completeness for regulated domains)
but keep the total at 100.

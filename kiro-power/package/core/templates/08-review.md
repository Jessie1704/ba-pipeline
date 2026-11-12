# 08 · Review — <Feature name>

**Date:** YYYY-MM-DD · **Reviewer:** requirements-reviewer agent + mechanical checks
**Score:** NN / 100 · **Verdict:** Pass · Conditional · Fail (decided by the defects — `checklists/quality-rubric.md`)
**How the review ran:** sub-agent · new session · other tool (same conversation → verdict capped at Conditional)

## Scores
| # | Category | Score | Max | Justification |
|---|----------|-------|-----|---------------|
| 1 | Groundedness | | 15 | |
| 2 | Clarity & unambiguity | | 15 | |
| 3 | Completeness | | 15 | |
| 4 | Testability | | 15 | |
| 5 | Consistency | | 10 | |
| 6 | Traceability | | 10 | |
| 7 | Value & scope alignment | | 10 | |
| 8 | Build-readiness | | 5 | |
| 9 | Readability | | 5 | |

## Mechanical checks
| Check | Result | Details |
|-------|--------|---------|
| ID integrity | | |
| Orphans | | |
| Open blocking Q / high-risk A | | |
| Ambiguity words | | file:line list |
| Gherkin shape | | |
| UX coverage (if UI) | | |

**By origin:** new N · regression N · previously missed N (scores vary about ±3 between independent reviewers)

## Defects (proven — these decide the verdict)
Status: `Open` · `Fixed` · `Deferred (D-NN)` (Majors only, by the PO's decision) — `ba check` *gates* FAILs a passed
Handoff (9) while a Critical or Major is neither fixed nor deferred, and a *Pass* verdict while a Critical is open.

| # | Severity | Category | Origin | Location | Evidence | Problem | Suggested fix | Auto-fixable | Owner | Due | Status |
|---|----------|----------|--------|----------|----------|---------|---------------|--------------|-------|-----|--------|

## Risks to verify (become questions; not counted in the verdict)
| # | Location | What may be wrong | Who confirms | Question |
|---|----------|-------------------|--------------|----------|

## Team walkthrough (Dev/Tech Lead + QA)
| Item | Detail |
|------|--------|
| Date / attended | |
| Feasibility concerns | |
| AC QA cannot test | |
| Test data or environments missing | |
| Confirmation | D-… (actor: Tech Lead / QA lead) |

## Fix-round grounding (only after a fix round)
| Changed item | New statement | Citation (SRC-/D-/A-) |
|--------------|---------------|-----------------------|

## Persona verdicts
- **AI coding agent:**
- **Product Owner:**
- **Designer** (if UI):
- **Team member:**

## Strengths
1. 

## Fix plan
| Artifact | Defects | Owner | Status |
|----------|---------|-------|--------|

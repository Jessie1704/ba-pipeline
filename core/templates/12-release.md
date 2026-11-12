# 12 · Release & handover — <Feature name>

**Release:** <version> · **Accepted:** D-… (<Accept / Conditional acceptance>) · **Date:** YYYY-MM-DD

## Scope reconciliation
From `ba rtm` / `ba check --only rtm`. Every released story's rows must be `Covered`; list everything else.
| Story | AC | Coverage | Why | Reported to PO (D-/date) | Owner of the follow-up |
|-------|----|----------|-----|--------------------------|------------------------|

## Outward documents
| Document | Audience | Version | Updated by | Reviewed by (AI drafts) |
|----------|----------|---------|------------|-------------------------|
| Release notes | users | | | |
| User guide changes | users, support | | | |
| Business-rule catalogue | business, support | | | |
| FAQ | support | | | |

## Known issues and open items
Every item has an owner and a due date; conditions of a conditional acceptance and open change requests count.
| # | Issue | Impact | Workaround | Owner | Due | Source (D-/CR-/defect) |
|---|-------|--------|------------|-------|-----|------------------------|

Support contact after go-live: <name, channel>

## KPIs
Copied from `ba kpi <slug>`, with one line each on what it means. First releases set the baseline.
| KPI | Value | Meaning for this release |
|-----|-------|--------------------------|

## Lessons learned
*AI draft — BA to review.* Every point cites evidence (audit seq, review round, CR, retest).
| What | Evidence | Keep / change | Action (owner, due) |
|------|----------|---------------|---------------------|

Workflow improvements → `/ba-profile` (learn), never an edit to `.ba/core/`.

## Handover
| Receiver (name, team) | Receives | Version | Location | Accepted (D-/SRC-, date) |
|-----------------------|----------|---------|----------|--------------------------|

## Gate 12 checklist
- [ ] Document versions match the released version
- [ ] Every known issue has an owner and a due date
- [ ] AI-drafted documents reviewed (named)
- [ ] Receiver named and accepted the handover

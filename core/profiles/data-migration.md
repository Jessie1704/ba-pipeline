---
name: data-migration
title: Data migration
kind: solution
origin: catalogue
version: 1.0
owner: BA practice
status: active
---

# Profile: Data migration

## 1. Signals
Migrate, convert, cutover, go-live weekend, legacy data, historical data, import into the new system,
decommission/sunset, data clean-up before move, "bring the old records across".

**Usually a secondary profile** alongside `cots-saas`, `legacy-modernisation` or a build profile; primary only
when the migration is the project. For ongoing data feeds use `integration`; for reports use `data`.

## 2. Stage plan
| Stage | Plan | Notes |
|-------|------|-------|
| *data-profiling* | Run (extra) | After Intake — look at the real source data before scoping |
| Model | Adapted | Source and target data models, object inventory, lineage source → target |
| Stories | Adapted | → **migration stories per data object** (+ reconciliation, cutover, rollback stories) |
| UX | Skip | Unless a cleansing/exception-handling screen is built (then Partial) |
| Spec | Adapted | → mapping, cleansing & transformation rules, reconciliation, retention |
| *cutover-plan* | Run (extra) | After Spec — rehearsals, timeline, go/no-go, rollback |
| Review | Run | |
| Handoff | Adapted | Cutover runbook, reconciliation report template, data owner sign-off pack |

## 3. Extra gap questions
- Which source systems and which data objects (customers, accounts, orders, documents…)? Who owns each?
- How much history: all, last N years, open items only? What happens to data not migrated (archive, read-only access, delete)?
- Legal retention or deletion obligations for the old data?
- Known data quality problems (duplicates, missing fields, free-text codes)? Who decides cleansing rules?
- Clean in the source before migration, during transformation, or in the target after?
- Key mapping: how are old IDs kept or cross-referenced? Do users need to search by old numbers?
- Attachments/documents/audit history — migrate, link or leave?
- Open/in-flight items (open orders, pending approvals) at cutover — finish in old, migrate in their state, or restart?
- Cutover style: big bang, phased by object/region, or parallel run? Acceptable downtime/freeze window?
- How will the business prove the migration is correct (counts, sums, samples, user acceptance)?
- Rollback: up to what point can we go back, and how?
- Rehearsals: how many, on what data, with which success criteria?

## 4. Model
- **Object inventory** with dependencies (load order: e.g. customers before accounts before transactions).
- Source and target conceptual models (Mermaid `erDiagram`) for in-scope objects.
- **Lineage**: source object → transformation → target object (Mermaid `flowchart LR`).
- State of in-flight items at cutover (state mapping old → new).

## 5. Stories
Adapted — migration stories per object:
"Migrate <object> from <source> to <target> so that <business can continue X from day 1>."
AC use concrete sample records and reconciliation outcomes:
`Given 12,480 active customers in the source with 37 known duplicates When migration runs Then 12,443 customers exist in the target And each duplicate pair is merged per BR-021 And the reconciliation report shows 0 unexplained differences`.
Add stories for: reconciliation report, exception handling (records that fail), archive/read-only access to old data,
cutover rehearsal, rollback.

## 6. UX
Skip — "UX: N/A — back-end migration". Partial only for exception-handling or archive-viewer screens.

## 7. Spec sections to add
```markdown
## Object inventory
| Object | Source system.table | Records (total / in scope) | History rule | Decision (migrate / archive / discard) | Load order | Data owner |
|--------|---------------------|----------------------------|--------------|----------------------------------------|-----------|------------|

## Field mapping — <Object>
| Target field | Source field(s) | Transformation | Default if missing | Cleansing rule | Required | Rule |
|--------------|-----------------|----------------|--------------------|----------------|----------|------|

## Value mapping (code lists)
| Source code | Source meaning | Target code | Notes |
|-------------|----------------|-------------|-------|

## Cleansing rules
| DQ ID | Object.field | Problem | Rule | Where applied (source / transform / target) | Owner | Records affected |
|-------|--------------|---------|------|---------------------------------------------|-------|------------------|

## Key & reference handling
| Object | Old key | New key | Cross-reference kept where | Searchable by old key? |
|--------|---------|---------|----------------------------|------------------------|

## In-flight items
| Object / state at cutover | Treatment (finish in old / migrate as-is / map to state / restart) | Target state |
|---------------------------|---------------------------------------------------------------------|--------------|

## Reconciliation checks
| Check ID | Object | Type (count / sum / checksum / sample / business test) | Source query | Target query | Tolerance | Owner |
|----------|--------|--------------------------------------------------------|--------------|--------------|-----------|-------|

## Exception handling
| Failure | Detection | Action (fix & reload / manual entry / exclude) | Owner | Report |
|---------|-----------|------------------------------------------------|-------|--------|

## Legacy data after go-live
| Data | Treatment (archive / read-only system / delete) | Access for | Retention | Decommission date |
|------|-------------------------------------------------|-----------|-----------|--------------------|
```

## 8. NFR focus
Data accuracy (reconciliation tolerances), Completeness, Performance (load time fits the cutover window),
Privacy & retention (PII in transit/at rest, deletion of non-migrated data), Audit (traceability old → new),
Reliability (restartable loads, idempotent reruns), Security of extracts.

## 9. Handoff extras
- `cutover-runbook.md` — for the cutover team: minute-by-minute timeline, owners, commands/steps, checkpoints,
  go/no-go criteria, communication points, rollback procedure, contacts.
- `reconciliation-report-template.md` — for data owners: per object counts/sums/samples source vs target,
  exceptions, sign-off line.
- `data-owner-signoff.md` — for each data owner: what was migrated, cleansing decisions, residual issues, approval.
- `agent-brief.md` — mapping, transformation, cleansing and reconciliation rules as implementable specs.
- `qa-pack.md` — mock-load tests per object, reconciliation tests, exception tests, rehearsal success criteria.

## 10. Review checks
- Every source object has a migrate/archive/discard decision and an owner.
- Every target required field has a source or a default; every source field in scope is mapped or explicitly dropped.
- Every code list is value-mapped (no unmapped source codes).
- Every object has at least one reconciliation check with a tolerance.
- In-flight items have a treatment.
- Cutover plan has go/no-go criteria and a rollback point.
- Retention/legal obligations for non-migrated data addressed.

## 11. Extra stages
| Stage ID | Name | After stage | Purpose | Steps | Output document | Gate |
|----------|------|-------------|---------|-------|-----------------|------|
| data-profiling | Data profiling | 1 Intake | Understand real source data quality before scoping | see below | `01a-data-profiling.md` | Profiling results reviewed with data owners; major issues logged as `Q-`/`R-` |
| cutover-plan | Cutover plan | 7 Spec | Plan rehearsals and the go-live event | see below | `07a-cutover-plan.md` | Go/no-go criteria and rollback point agreed by PO and data owners (`D-`) |

### data-profiling — steps
1. List source objects and how profiling data will be obtained (BA-provided extracts, DBA queries, existing
   reports). If no data is available yet, write the profiling queries/requests needed and raise `Q-`s; do not guess figures.
2. Per object and key field: record count, null/blank %, distinct values, invalid formats, out-of-range values,
   duplicates (by business key), orphan references, oldest/newest dates.
3. Highlight findings by severity; estimate records affected.
4. Propose cleansing rules (as `A-` until data owners confirm) and history cut-off options.
5. Feed results into Scope (volumes, history) and into the cleansing rules in Spec.

Template for `01a-data-profiling.md`:
```markdown
## Data sources & access
| Object | Source | Extract / query | Date of extract | Records |
## Profile — <Object>
| Field | Null % | Distinct | Invalid | Duplicates | Min / max | Notes |
## Findings
| # | Object.field | Issue | Records affected | Severity | Proposed rule (A-) | Owner |
```

### cutover-plan — steps
1. Choose cutover strategy (big bang / phased / parallel) with rationale; confirm freeze and downtime windows.
2. Plan **rehearsals** (at least one full dress rehearsal on production-like data): scope, timing, success criteria.
3. Build the timeline: pre-cutover (freeze, final extracts), load sequence by object order, reconciliation
   checkpoints, business verification, go/no-go meeting, go-live, hypercare.
4. Define **go/no-go criteria** (reconciliation within tolerance, critical exceptions = 0, rehearsal duration fits window).
5. Define the **rollback point** and procedure; the point of no return.
6. Communication plan: who is informed when (users, support, customers if needed).
7. Hypercare: duration, support model, issue triage.

Template for `07a-cutover-plan.md`:
```markdown
## Strategy & windows
## Rehearsals
| # | Date | Scope | Success criteria | Result |
## Timeline
| Step | Start | Duration | Owner | Depends on | Checkpoint |
## Go / no-go criteria
## Rollback
| Point | Procedure | Max time to roll back | Decision owner |
## Communications
## Hypercare
```

---
Changelog: 1.0 — installed from catalogue.

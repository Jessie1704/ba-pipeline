---
name: data
title: Data & reporting
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: Data & reporting

## 1. Signals
Reports, BI dashboards, KPIs, analytics, data pipelines/ETL, data warehouse/lake, data migration, data quality.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — **data lineage** and conceptual data model replace most process flows |
| Stories | Run — **report/metric stories** and data stories |
| UX | Partial — dashboard/report layout mock-ups only (if a visual report is delivered) |
| Spec | Run — + metric definitions, source mapping, data quality rules |
| Handoff | Run — + data catalogue entry |

## 3. Extra gap questions
- What **decision** will each report/metric support, and who makes it?
- Exact metric definitions: formula, numerator/denominator, filters, inclusions/exclusions?
- Grain (per order, per day, per customer)? Dimensions and drill-downs?
- Sources for each field? Which source wins when they disagree?
- Freshness: real-time, hourly, daily? Historical depth? Restatement of past periods?
- Data quality rules — completeness, validity, uniqueness thresholds; what if they fail?
- Who may see which rows/columns (row-level security, PII masking)?
- Delivery: BI tool, scheduled e-mail, export, API?
- For **migration**: scope of records, cleansing rules, mapping, cutover plan, reconciliation, rollback?

## 4. Model
Conceptual data model (`erDiagram`), **lineage** diagram (source → transformation → target → report),
dimension/fact list for reporting.

## 5. Stories
"As a <decision maker>, I want <metric/report> by <dimensions> at <freshness>, so that I can <decision>."
AC use sample datasets with expected numbers (`Given these 5 orders … Then revenue for 2026-10 = €1,240.50`).

## 6. UX
Partial `/ba-ux` for dashboards: layout, chart type per metric, filters, drill paths, empty/no-data state. Otherwise N/A.

## 7. Spec sections to add
```markdown
## Metric definitions
| Metric ID | Name | Business question | Formula | Grain | Filters / exclusions | Source fields | Freshness | Owner |
|-----------|------|-------------------|---------|-------|----------------------|---------------|-----------|-------|

## Source-to-target mapping
| Target table.field | Source system.table.field | Transformation | Rule |
|--------------------|---------------------------|----------------|------|

## Data quality rules
| DQ ID | Dataset.field | Rule | Threshold | On failure |
|-------|---------------|------|-----------|-----------|

## Access rules
| Role | Rows visible | Columns masked |
|------|--------------|----------------|

## Migration (if applicable)
| Topic | Requirement |
|-------|-------------|
| Records in scope | |
| Cleansing rules | |
| Cutover approach & freeze window | |
| Reconciliation checks | |
| Rollback | |
```

## 8. NFR focus
Freshness/latency, Query performance, Data quality, Privacy (PII, masking, retention), Audit/lineage, Scalability (volume growth).

## 9. Handoff extras
`data-catalogue.md`: datasets, metric definitions, owners, freshness, lineage — for data consumers.
Reconciliation and sample-data tests with expected numbers in `qa-pack.md`.

## 10. Review checks
Every metric has an unambiguous formula and owner; every reported field traces to a source; DQ rules have thresholds; access rules defined for PII.

## 11. Extra stages
None.

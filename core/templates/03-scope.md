# 03 · Scope — <Feature name>

**Status:** Draft · Confirmed by PO (`D-NNN`, date)

## Problem statement
<Who> struggles with <what> when <situation>, causing <measurable impact>. (SRC-…)

## Goals
Metric, Baseline and Target are never blank: write the value, `unknown — measured by <date>`, or `waived (D-)`.
| ID | Goal | Metric | Baseline | Target | By when | Measured how |
|----|------|--------|----------|--------|---------|--------------|

## Non-goals
- …

## Users & stakeholders
| Role | Job to be done | Primary / secondary |
|------|----------------|---------------------|

## In scope
Every item serves a goal (`G-`) or is mandatory — write `mandatory: <law/policy/constraint> (SRC-/D-)`. *Owner* is the
stakeholder who decides about it (from *Governance*). `ba check` *governance* FAILs on an item with neither.
| ID | Capability | Supports goal | Owner (STK-) | Profile |
|----|-----------|---------------|--------------|---------|

## MVP by value
Slice by the goals, not by feature lists. Value = how much the item moves its goal's metric (H/M/L, with reason);
effort and risk from the builders or `A-`. MVP = the smallest set that reaches every MVP goal's target.
Not needed for `small-change`: the whole change is one slice.
| IS | Value (H/M/L — why) | Effort (S/M/L) | Risk / dependency | Slice (MVP/Next/Later) |
|----|---------------------|----------------|-------------------|------------------------|

## Out of scope
| Item | Reason (later phase / other team / not valuable) |
|------|--------------------------------------------------|

## Assumptions, constraints, dependencies
- **Assumptions:** see `_status.md` (A-…) — key ones: …
- **Constraints:** …
- **Dependencies:** | Dependency | Owner | Needed by | Status |

## Risks
| ID | Risk | L | I | Mitigation | Owner |
|----|------|---|---|-----------|-------|

## Release slicing rationale
Which goals the MVP reaches and by when; what each later slice adds to which metric. Conflicts between area
owners about the slice: escalated to the business owner (`D-`).

## PO confirmation
Please confirm each statement (✔ / ✘ + comment):
- [ ] We are solving <problem> for <users>.
- [ ] Success means <G-01 metric target> by <date>.
- [ ] MVP includes: … — because it reaches <G- targets>.
- [ ] We are NOT doing: …
- [ ] Key risk accepted: …

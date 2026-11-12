# 07 · Specification — <Feature name>

> Sections not applicable: <section — reason>

## 1. Business rules
| ID | Rule (must…) | Type | Inputs | Outcome | Source | Used by |
|----|-------------|------|--------|---------|--------|---------|

### BR-NNN decision table (for multi-condition rules)
| Condition 1 | Condition 2 | → Outcome |
|-------------|-------------|-----------|
| Yes | ≤ 30 days | Full refund |
| Yes | > 30 days | Store credit |
| No | any | Reject (MSG-03) |

## 2. Data dictionary
### <Entity>
| Field | Meaning | Type | Format / length | Req. | Default | Allowed values / range | Validation | Source system | Sensitivity | Retention |
|-------|---------|------|-----------------|------|---------|------------------------|-----------|---------------|-------------|-----------|

## 3. Screen behaviour rules
Layouts, elements and states are in `06-ux.md`. Only behaviour the wireframes can't express goes here.
| Screen | Behaviour (field dependencies, autosave, sort/filter/paging, timeouts…) | Rule | Fields |
|--------|------------------------------------------------------------------------|------|--------|

## 4. Messages
| ID | Trigger | Exact text | Severity | User's next action |
|----|---------|-----------|----------|--------------------|

## 5. Integrations
### <System>
| Aspect | Detail |
|--------|--------|
| Direction / trigger | |
| Data & mapping | |
| Frequency / volume | |
| Success criteria | |
| Failure handling (timeout, retry, idempotency, fallback, alert) | |

## 6. Notifications
| Event | Channel | Recipient | Timing | Content | Opt-out |
|-------|---------|-----------|--------|---------|---------|

## 7. Reporting & audit
| What | Who sees | Frequency | Retention |
|------|----------|-----------|-----------|

## 8. Non-functional requirements
| ID | Category | Requirement (must… under… verified by…) | Source |
|----|----------|------------------------------------------|--------|

## 9. Changes to existing system (if applicable)
- Impacted functions:
- Backward compatibility:
- Data migration (mapping, cleansing, cutover):
- Regression areas:

## 10. Compliance matrix (if applicable)
| Regulation / clause | Requirement IDs | Evidence |
|---------------------|-----------------|----------|

## 11. Proposed defaults awaiting confirmation
Every row's `A-` must also be in `02-questions.md` → *Assumptions* (the single register).
| Item | Proposed value | Why | A-/Q- |
|------|----------------|-----|-------|

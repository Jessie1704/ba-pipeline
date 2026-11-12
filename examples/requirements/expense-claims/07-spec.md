# 07 · Specification — Expense claims & approvals

> v1.0 draft — updated 2026-10-26 for round-2 decisions (SRC-06, SRC-07).
> Section not applicable: Changes to existing system (new feature replacing Excel/email).

## 1. Business rules
| ID | Rule | Type | Source | Used by |
|----|------|------|--------|---------|
| BR-001 | An expense line must be dated no more than 90 calendar days before the claim's **first** submission date and not in the future; resubmission keeps the first submission date. | Validation | SRC-03 §4.1, D-002, D-031, A-082 | US-002, US-014 |
| BR-002 | A line other than mileage must have at least one receipt when its amount is above €25.00, and every meals line marked *abroad* must have a receipt whatever its amount; mileage lines need no receipt. | Validation | SRC-03 §4.2, D-024, A-056 | US-002 |
| BR-003 | Reimbursable **domestic** meals per employee per calendar day, across all claims in the statuses listed in A-057 (Returned counts; Draft, Rejected and Withdrawn don't), must not exceed €40.00; the excess is taken from the line submitted last. Meals abroad have no daily cap. | Calculation | SRC-02, D-012, D-024, A-057 | US-002 |
| BR-004 | Mileage amount = km × €0.30; km is a whole number 1–2,000. | Calculation | SRC-02 (rate); A-033 (range) | US-002 |
| BR-005 | Meals, accommodation and "other" lines require the declaration "excludes alcohol, fines and personal items" to be ticked; the amount entered excludes them. | Validation | SRC-03 §6.1, D-017, A-059 | US-002 |
| BR-006 | A claim must contain at least one line and at most 50 lines. | Validation | A-014 | US-002 |
| BR-007 | Approval chain from the **claimed total**: line manager always; department head if claimed total > €1,000.00; Finance Controller if claimed total > €500.00. Order: manager → department head → Finance Controller. When one person holds consecutive levels, one approval covers those levels. | Routing | SRC-03 §5.1, SRC-03 §5.2, D-003, D-018, D-032 | US-003, US-017 |
| BR-008 | A delegation must cover more than 3 working days and at most 60 calendar days. During it, claims routed to the approver also appear in the delegate's inbox; both may decide and the first decision counts. A delegate may not act as delegate on a claim where they are also a later approver or the claimant. When a delegation ends, undecided claims leave the delegate's inbox; "End now", overlap and self-nomination follow A-081. | Routing | SRC-03 §5.4, D-011, D-020, D-023, A-018, A-079, A-081 | US-005 |
| BR-009 | Nobody may approve, finance-check or be reassigned a claim they submitted; nobody may finance-check a claim they approved at any level (D-033 for the Finance Controller; A-075 for everyone else); the step goes to the next eligible person (own manager for approval, another Finance team member for the check). | Authorisation | SRC-03 §5.3, D-033, A-075 | US-003, US-005, US-007, US-014 |
| BR-010 | A Finance team member must tick all five checklist items before marking a claim OK: (1) itemised receipt present where BR-002 requires it, card slips refused; (2) receipt amount matches the line; (3) supplier VAT number recorded when it is on the receipt; (4) no alcohol, fines or personal items visible on the receipt; (5) cost centre is one of the valid cost centres (A-072). | Validation | D-029, SRC-03 §4.2, A-072 | US-007 |
| BR-011 | At 18:00 Europe/Paris on every calendar day, all ReadyForExport claims are exported in one CSV batch `EXP-YYYYMMDD` (file `EXP_YYYYMMDD.csv`). | Timing | D-013, D-036 | US-008 |
| BR-012 | Receipt files must be JPEG, PNG or PDF, max 10 MB each, max 5 per line. | Validation | A-015 | US-001 |
| BR-013 | Return, reject, reassign and batch release require a reason of 5–500 characters. | Validation | A-034, D-033 | US-004, US-007, US-016, US-019 |
| BR-014 | A resubmitted returned claim restarts the approval chain at the line manager. | Routing | D-007 | US-004 |
| BR-015 | Each approval level: from business day 3 after the claim reached the level the approver gets it in their daily reminder digest (MSG-20); on business day 5 the claim is escalated once to the approver's manager in the HR file — the CFO for the Finance Controller level — who may decide it; the original approver can still decide; no second escalation. | Timing | D-008, D-026, D-041, A-050, A-051 | US-006 |
| BR-016 | Claims of an employee with a leave date in the latest HR file are flagged "Leaver" and sorted first in every inbox; the Finance team is warned once, 10 calendar days before the leave date or at the first import after a later entry (MSG-27, A-073); the flag is removed when the leave date disappears from the HR file (A-061). | Routing/Timing | D-009, D-039, A-061, A-073 | US-011 |
| BR-017 | A Finance team member (incl. the Finance Controller, A-068) may enter a claim on behalf of an employee whose leave date has passed; every line must be dated on or before the leave date; BR-001 applies; the claim routes through BR-007 using the employee's manager and department head on the leave date. A returned on-behalf claim is handled per A-071. | Eligibility | D-021, SRC-06, A-068, A-071 | US-014 |
| BR-018 | A claim from an employee with no manager in the latest HR file waits in *AwaitingApprover*; HR Ops gets the daily list MSG-31; when an HR import gives a manager it routes to that manager; if none by business day 2 it routes to the department head (or BR-019 if vacant). | Routing | D-022, A-050, A-051 | US-003, US-015 |
| BR-019 | Fallback approvers: a vacant department-head level is approved by the Finance Controller; the Finance Controller level of the Finance Controller's own claim is approved by the CFO, who also covers its department-head level (A-077); escalation for an approver with no manager goes to the Finance Controller, or the CFO for the Finance Controller (A-078). | Routing | D-033, A-077, A-078 | US-015, US-017 |
| BR-020 | A batch from the export run of the 20th of a month or earlier (incl. that run's retries) has that month as payroll month; later runs have the next month. A batch may be marked paid only when *Reconciled*; the paid date must be on or after the delivery date (A-062) and not after today. | Timing/Validation | SRC-02, D-019, D-028, A-062, A-070 | US-009 |
| BR-021 | The Finance check has an SLA of 2 business days; once it is exceeded (from business day 3) the claim is listed to the Finance Controller in the daily digest MSG-40. | Timing | D-030, A-045, A-050 | US-007 |
| BR-022 | If delivery of the export file fails, it is retried at 18:15, 18:30 and 18:45; after the third failure the batch is *DeliveryFailed*, claims stay ReadyForExport, MSG-22 goes to Finance and an IT service desk ticket (MSG-43) is opened; no further retry that day. | Timing | D-038 | US-008 |
| BR-023 | At 06:00 the system reads `REJ_<batch>.csv` if present; every claim with a rejected reference becomes *ExportFailed* with the ERP error text; a fixed claim is re-exported with all its lines; unmatched references are logged and alerted (MSG-26). | Derivation | D-036, D-038, A-043 | US-010 |
| BR-024 | At 06:00 the system reads `SUM_<batch>.csv`; the batch is *Reconciled* when LINES_RECEIVED = lines sent, LINES_POSTED + rejected lines = lines sent, and TOTAL_POSTED = sent total − rejected total, where rejected lines = rows in `REJ_` (A-043); otherwise, or if the file is missing (A-063), the batch is *Held* (MSG-36) until the Finance Controller releases it with a reason. | Validation | D-038, A-040, A-043, A-063 | US-019 |
| BR-025 | Only the Finance Controller may reassign an undecided approval step, with a reason; the new approver must be an active employee and not the claimant; the step's SLA clock restarts. | Authorisation | D-033 | US-016 |
| BR-026 | The HR file is imported at 02:00 as a full refresh (A-064); if it is missing or fails file validation (required columns, one row per employee_id), no employee changes, yesterday's data stays in use and an IT service desk ticket is opened (MSG-43). Row errors and missing employees follow A-074. Undecided manager-level steps move to a changed manager (A-041). | Timing/Derivation | D-038, D-039, A-041, A-064, A-074 | US-018 |
| BR-027 | Bulk approve: at most 50 claims at a time, only at the line-manager level (incl. delegate), only claims with a claimed total ≤ €250.00 and no Leaver flag. | Authorisation | D-025 | US-004 |
| BR-028 | Retention end = 31 December of (year of paid date + 7); for claims never paid, year of final status date + 7. After that date, receipts and personal data are deleted and amounts kept in anonymised totals per cost centre × category × month. | Timing | SRC-02, D-034, A-042, A-047, A-048 | US-020 |

### BR-007 decision table (claimed total; one approval per person for consecutive levels)
| Claimed total | Manager | Dept head | Finance Controller |
|-------------|---------|-----------|--------------------|
| ≤ €500.00 | ✔ | — | — |
| €500.01 – €1,000.00 | ✔ | — | ✔ |
| > €1,000.00 | ✔ | ✔ | ✔ |

### Approval matrix incl. fallbacks (workflow-approval profile)
| Request type | Condition | Level 1 | Level 2 | Level 3 | Mode |
|--------------|-----------|---------|---------|---------|------|
| Expense claim | Claimed total ≤ €500.00 | Manager (delegate, escalation target) | — | — | Sequential |
| Expense claim | €500.01 – €1,000.00 | Manager | — | Finance Controller (CFO if FC is claimant) | Sequential |
| Expense claim | > €1,000.00 | Manager | Department head (FC if vacant) | Finance Controller (CFO if FC is claimant) | Sequential |

### Routing & assignment rules
| Rule ID | When | Assign to | Method | Fallback | Source |
|---------|------|-----------|--------|----------|--------|
| BR-007 | Claim submitted | Chain per matrix | Direct (HR file) | BR-018, BR-019 | D-003, D-032 |
| BR-008 | Approver has active delegation | Approver + delegate | Direct | Not delegate if later approver | D-020, D-023 |
| BR-009 | Approver is claimant | Approver's manager | Direct | — | SRC-03 §5.3 |
| BR-015 | Business day 5 at a level | + approver's manager / CFO | Direct | A-052 if the target is a later approver | D-026 |
| BR-018 | No manager on record | Wait; dept head on business day 2 | Direct | BR-019 | D-022 |
| BR-025 | FC reassigns | Named employee | Manual | — | D-033 |

## 2. Data dictionary
### Claim
| Field | Meaning | Type | Format | Req. | Allowed / range | Validation | Source | Sensitivity | Retention |
|-------|---------|------|--------|------|-----------------|-----------|--------|-------------|-----------|
| claim_id | Unique reference | text | C-NNNN (sequential) | Yes | — | — | System | Internal | BR-028 |
| employee_id | Claimant | text | HR id | Yes | In HR file; active, or past leave date for on-behalf | BR-017 | HR file | Personal | BR-028 |
| entered_by | Finance member who entered an on-behalf claim | text | HR id | On-behalf only | Finance team | BR-017 | System | Personal | BR-028 |
| status | Lifecycle state | enum | — | Yes | Draft, Submitted, AwaitingApprover, InApproval, Returned, Rejected, Withdrawn, FinanceCheck, ReadyForExport, Exported, ExportFailed, Paid | 04-model §2 | System | Internal | BR-028 |
| total_claimed | Sum of line amounts entered | money | EUR 2dp | Yes | 0.01–50,000.00 (A-033) | Drives BR-007 | Calc | Internal | Anonymised kept |
| total_reimbursable | Sum after caps | money | EUR 2dp | Yes | — | BR-003, BR-004 | Calc | Internal | Anonymised kept |
| first_submitted_at | First submission time | datetime | ISO 8601, stored UTC, shown Europe/Paris | On submit | — | BR-001, G-01 | System | Internal | BR-028 |
| last_submitted_at | Latest (re)submission time | datetime | as above | On submit | — | — | System | Internal | BR-028 |
| leaver_flag | Employee has a leave date | bool | — | Yes | — | BR-016 | HR file | Personal | BR-028 |
| export_batch_id | Batch exported in | text | EXP-YYYYMMDD | When exported | — | — | System | Internal | BR-028 |
| exported_at | Delivery time of that batch | datetime | ISO 8601 | When exported | — | G-01 leading indicator | System | Internal | BR-028 |
| paid_date | Date paid in payroll | date | YYYY-MM-DD | When paid | ≥ delivery date, ≤ today | BR-020 | Finance | Internal | BR-028 |
| export_error | ERP error text | text | ≤ 200 chars | When ExportFailed | — | BR-023 | ERP | Internal | BR-028 |
| times_returned | How often the claim was returned (approver or Finance) | int | ≥ 0 | Yes | default 0 | G-02 | System | Internal | Anonymised kept |
| current_approver | Person(s) the claim waits for | text list | HR ids | When AwaitingApprover/InApproval | — | BR-007 | System | Personal | BR-028 |
| last_updated_at | Time of the latest status change | datetime | ISO 8601 | Yes | — | — | System | Internal | BR-028 |
| employee_name | Claimant's name for lists and CSV (`employee` column) | text | "first last" | Yes | — | — | HR file | Personal | BR-028 |

### Expense line
| Field | Meaning | Type | Format | Req. | Allowed / range | Validation |
|-------|---------|------|--------|------|-----------------|-----------|
| expense_date | Date incurred | date | YYYY-MM-DD | Yes | ≤ first submission date, ≥ first submission date − 90 days; ≤ leave date for on-behalf | BR-001, BR-017 |
| category | Type | enum | — | Yes | travel, accommodation, meals, mileage, other | — |
| trip_location | Domestic (in France) or abroad | enum | domestic, abroad | Meals only | no default (A-058) | BR-002, BR-003 |
| amount | Amount paid in EUR | money | EUR 2dp | Yes (not mileage) | 0.01–10,000.00 (A-033) | — |
| reimbursable_amount | After caps | money | EUR 2dp | Calc | — | BR-003, BR-004 |
| description | What and why | text | 3–200 chars (A-033) | Yes | — | — |
| km / from / to | Mileage details | int / text / text | — | Mileage only | 1–2,000 km | BR-004 |
| declaration | No alcohol/fines/personal | bool | — | Meals, accommodation, other | true | BR-005 |
| vat_number | Supplier VAT number from the receipt | text | A-049 | No | — | BR-010 item 3 |
| cost_centre | Cost centre to book | text | 4 chars (ERP, SRC-07) | Yes | Default from HR file; editable by Finance (A-017); must be in the valid list (A-072) | BR-010 item 5 |

### Receipt · Approval step · Delegation · Finance check
| Entity.field | Type | Rule |
|--------------|------|------|
| Receipt.file | binary | BR-012; deleted at retention end (BR-028) |
| ApprovalStep.approver_id, level (manager / dept_head / finance_controller), covers_levels, decision (approve / return / reject), reason, decided_at, on_behalf_of, acting_as (approver / delegate / escalation / reassigned), reached_at | — | BR-007, BR-008, BR-009, BR-013, BR-015, BR-025 |
| Delegation.manager_id, delegate_id, from_date, to_date | dates inclusive | BR-008 |
| FinanceCheck.checker_id, items_ticked (1–5), decision, reason, decided_at | — | BR-010 |

### Export batch · Rejection row
| Field | Type | Rule |
|-------|------|------|
| ExportBatch.batch_id | text EXP-YYYYMMDD | BR-011 |
| ExportBatch.state | enum Sent, DeliveryFailed, Held, Reconciled, Paid | 04-model §3 |
| ExportBatch.lines_sent, total_sent | int, money | BR-024 |
| ExportBatch.run_date, delivered_at | date, datetime | BR-020 (payroll month from run_date, A-070) |
| ExportBatch.payroll_month | YYYY-MM | BR-020 |
| ExportBatch.release_reason, released_by | text, HR id | BR-013, BR-024 |
| RejectionRow.reference, error_code, error_text | text | BR-023 |

### Employee (from HR file, INT-03)
| Field | Type | Req. | Rule |
|-------|------|------|------|
| employee_id, first_name, last_name, email | text | Yes | — |
| manager_id, department_head_id | text | No | Empty → BR-018 / BR-019 |
| department_id, cost_centre | text | Yes | cost_centre 4 chars |
| leave_date | date | No | BR-016, BR-017 |
| status | enum active / inactive | Yes | — |

## 3. Screen behaviour rules
Screens, elements and states are in `06-ux.md`; only behaviour wireframes can't show is listed here.
| Screen | Behaviour | Rule |
|--------|-----------|------|
| SCR-02 | Domestic meals line shows "€X of €40 used on this day" from other claims | BR-003 |
| SCR-02 | Trip location shown only for meals; switching to abroad hides the cap hint and makes the receipt required | BR-002, BR-003 |
| SCR-02 | Draft autosaves every 30 s and on leaving a field | A-019 |
| SCR-03 | Default sort: leaver first, then waiting time descending; bulk checkbox only on BR-027-eligible rows | BR-016, BR-027 |
| SCR-04 | Actions hidden for users excluded by BR-008/BR-009, with MSG-42 | BR-008, BR-009 |
| SCR-07 | Mark OK enabled only when all 5 checklist items are ticked | BR-010 |
| SCR-09 | Lists page 25 rows (A-053); filters combine with AND | — |

## 4. Messages
| ID | Trigger | Exact text | Severity |
|----|---------|-----------|----------|
| MSG-01 | BR-001 fail | "This expense is more than 90 days old (policy 4.1) and can't be claimed." | Error |
| MSG-02 | BR-002 fail (> €25) | "Add a receipt — it's required for expenses over €25." | Error |
| MSG-03 | BR-003 cap | "Domestic meals are capped at €40 per day. €{excess} of this line won't be reimbursed." | Warning |
| MSG-04 | BR-004 km invalid | "Enter whole kilometres between 1 and 2,000." | Error |
| MSG-05 | BR-005 not ticked | "Please confirm this excludes alcohol, fines and personal items." | Error |
| MSG-06 | BR-006 fail | "A claim needs between 1 and 50 lines." | Error |
| MSG-07 | BR-012 fail | "Use a JPEG, PNG or PDF up to 10 MB." | Error |
| MSG-08 | BR-013 fail | "Please give a reason (at least 5 characters)." | Error |
| MSG-09 | BR-008 delegation length | "A delegate can be set for absences longer than 3 working days and up to 60 days (policy 5.4)." | Error |
| MSG-20 | BR-015 reminder digest | Email: "Reminder: {n} expense claims are waiting for your approval." + list (claim, claimant, amount, days waiting) | Info |
| MSG-21 | BR-015 escalation | Email to both: "Claim {id} from {name} has waited 5 business days for {approver}. {target} can now decide it too." | Warning |
| MSG-22 | BR-022 delivery failed | Email to Finance: "Today's ERP export could not be delivered after 3 retries. {n} claims are still waiting. IT ticket {ticket}." | Error |
| MSG-23 | Claim paid | Email: "Your claim {id} (€{amount}) was paid on {date}." | Info |
| MSG-24 | BR-020 paid date invalid | "The paid date can't be in the future or before the export date." | Error |
| MSG-25 | BR-023 rejections | Email to Finance: "{n} claims were rejected by the ERP in batch {batch}." | Error |
| MSG-26 | BR-023 unmatched row | Email to Finance: "The ERP rejection file mentions unknown reference {ref}." | Warning |
| MSG-27 | BR-016 warning | Email to Finance: "{name} leaves on {date} with {n} claims not yet exported." | Warning |
| ~~MSG-28~~ | (withdrawn, D-021) | — | — |
| MSG-29 | Withdraw after decision | "This claim can't be withdrawn because an approver has already decided." | Error |
| MSG-30 | Unauthorised page | "You don't have access to this page." | Error |
| MSG-31 | BR-018 daily list | Email to HR Ops: "{n} expense claims are waiting because the employee has no manager in the HR system." + list (employee id, name, claim, days waiting) | Warning |
| MSG-32 | BR-025 reassigned | Email: "Claim {id} from {name} was reassigned to you by {fc}: {reason}." | Info |
| MSG-33 | Invalid transition | "This claim is no longer waiting for you." | Error |
| MSG-34 | Concurrent decision | "Already decided by {name} at {time}." | Info |
| MSG-35 | BR-024 held batch | "This batch is on hold until the Finance Controller releases it." | Error |
| MSG-36 | BR-024 mismatch | Email to Finance Controller: "Batch {batch} doesn't reconcile with the ERP: {detail}. It is on hold." | Error |
| MSG-37 | BR-002 meal abroad | "Meals abroad need a receipt, whatever the amount." | Error |
| MSG-38 | BR-017 date after leave | "This expense is after {name}'s leaving date ({date}) and can't be claimed." | Error |
| MSG-39 | BR-027 bulk limits | "Bulk approve is for up to 50 claims of €250 or less, at manager level, without a Leaver flag." | Info |
| MSG-40 | BR-021 digest | Email to Finance Controller: "{n} claims have waited more than 2 business days in the Finance check." + list | Warning |
| MSG-41 | BR-025 invalid target | "Choose an active employee who didn't submit this claim." | Error |
| MSG-42 | BR-008 / BR-009 exclusion | "You can't decide this claim here because you submitted it or approve it at a later level." | Info |
| MSG-43 | BR-022 / BR-026 ticket | IT ticket: "{interface} failed at {time}: {reason}. Expense claims is using {fallback}." | Error |
| MSG-44 | BR-010 incomplete | "Tick all five checks before marking OK. Missing: {item}." | Error |
| MSG-45 | BR-017 not a leaver | "On-behalf claims are only for employees whose leaving date has passed." | Error |
| MSG-46 | Claim returned (A-069) | Email to claimant: "Your claim {id} was returned by {name}: {reason}. Edit and resubmit it in Expense claims." | Info |
| MSG-47 | Claim rejected (A-069) | Email to claimant: "Your claim {id} was rejected by {name}: {reason}." | Info |

## 5. Request types & approval (workflow-approval profile)
| Type | Workflow | Volume | Owner |
|------|----------|-----------|-------|
| Expense claim | Approval matrix §1 → Finance check | ~900/month (SRC-01), peak in last week of month | Finance Controller |

### SLA & escalation
| Step | SLA | Calendar | Starts | Pauses | Stops | Reminder | Escalate |
|------|-----|----------|--------|--------|-------|----------|----------|
| Each approval level | 5 business days | Mon–Fri, FR holidays, Europe/Paris (D-041) | Claim reaches level / reassigned (BR-025) | — | Decision or withdrawal | Daily digest MSG-20 from business day 3 | Business day 5, once → approver's manager; CFO at FC level (BR-015) |
| AwaitingApprover | 2 business days | same | Claim enters AwaitingApprover | — | HR file gives manager | HR Ops MSG-31 daily | Business day 2 → dept head (BR-018) |
| Finance check | 2 business days (D-030) | same | Claim enters FinanceCheck | — | Mark OK / return | MSG-40 to FC from business day 2 | — |

### Delegation & absence
| Topic | Rule |
|-------|------|
| Who / to whom | Approver nominates any active employee; exclusions per claim in BR-008 and BR-009 |
| Manual / automatic | Manual (D-011) |
| Scope | All claims routed to the approver during the period; approver keeps rights (D-023) |
| Audit | Approval step records `acting_as` and `on_behalf_of` |

### Segregation of duties
| Rule | Enforcement | Exception process |
|------|-------------|-------------------|
| No self-approval / self-check | BR-009 | Next eligible person |
| FC doesn't check claims she approved | BR-009 (D-033) | Another Finance member |
| Delegate not also a later approver | BR-008 (D-020) | Manager or escalation decides level 1 |
| On-behalf entry not checked by the entering member | A-039 | Another Finance member |
| Reassignment only by FC, with reason | BR-025 | — |

### Work queues
| Queue | Contains | Visible to | Default sort | Columns | Bulk actions |
|-------|----------|-----------|--------------|---------|--------------|
| Approvals inbox (SCR-03) | Claims at my level, incl. delegated and escalated | Approvers | Leaver, waiting days desc | Flag, claimant, claim, claimed total, level, waiting days, badge | Bulk approve (BR-027) |
| Finance check (SCR-06) | FinanceCheck claims | Finance team, FC | Leaver, waiting days desc | Flag, claimant, claim, reimbursable total, approved date, waiting days | None |
| Export batches (SCR-08) | Batches and ExportFailed claims | Finance team, FC | Newest first | Batch, state, lines, total, payroll month, rejected | None |

The "No manager" Finance queue in the previous draft is **removed** (D-022).

### Audit trail (in product)
| Event | Captured | Visible to | Retention |
|-------|----------|-----------|-----------|
| Every status change, decision, escalation, reassignment, delegation, batch release, on-behalf entry | who, when, from/to, reason, acting_as, on_behalf_of | Claimant (own), approvers, Finance | BR-028 |

## 6. Integrations (integration profile)
| Interface | Source → Target | Trigger | Transport & format | Volume | Ordering & idempotency | Owner |
|-----------|-----------------|---------|--------------------|--------|-------------|-------|
| INT-01 | Claims → ERP | Daily 18:00 (BR-011); ERP imports at 22:00, file must land by 21:30 | SFTP, key auth; `EXP_YYYYMMDD.csv`, UTF-8, `;`, header row, dot decimal | ≤ 2,000 lines/day | One file per day; ERP refuses a file name already imported | Aisha Khan |
| INT-02 | ERP → Claims | Read at 06:00 next day | SFTP outbound; `REJ_<batch>.csv` (only if rejections), `SUM_<batch>.csv` | — | Processed once per batch | Aisha Khan |
| INT-03 | HR system → Claims | File lands 01:30; import 02:00 | CSV (columns SRC-07); transport and format A-054 | ~420 rows | Full refresh; one row per employee_id (A-064) | Aisha Khan / Marco Rossi |

Sources per value: INT-01 and INT-02 file names, columns, separators, timings, volume, retries and transport — SRC-07
(D-036, D-038); INT-03 timings and columns — SRC-07; everything else cites its `A-` in the tables below.

### Field mapping — INT-01
| Source field | Target field | Transformation / lookup | Default | Required | Rule |
|--------------|-------------|-------------------------|---------|----------|------|
| ExportBatch.batch_id | BATCH_ID | EXP-YYYYMMDD (A-055) | — | Yes | BR-011 |
| ExportBatch.run_date | JOURNAL_DATE | YYYY-MM-DD; export run date (A-055) | — | Yes | — |
| ExpenseLine.category | ACCOUNT | travel 625100, mileage 625150, accommodation 625200, meals 625700, other 628800 | — | Yes | D-037 |
| ExpenseLine.cost_centre | COST_CENTRE | 4 chars | — | Yes | A-072 |
| ExpenseLine.reimbursable_amount | AMOUNT | 2dp, dot decimal | — | Yes | — |
| Claim.employee_id | EMPLOYEE_REF | HR employee_id (A-055) | — | Yes | — |
| claim_id + "/" + line no. | REFERENCE | e.g. "C-1001/2", ≤ 30 chars | — | Yes | — |
| ExpenseLine.description | DESCRIPTION | First 50 chars (A-044) | — | Yes | — |
No balancing line per batch (A-055).

### Field mapping — INT-02
| File | Columns | Use |
|------|---------|-----|
| `REJ_<batch>.csv` | BATCH_ID; REFERENCE; ERROR_CODE; ERROR_TEXT | BR-023 |
| `SUM_<batch>.csv` | LINES_RECEIVED; LINES_POSTED; TOTAL_POSTED | BR-024 |

### Field mapping — INT-03
See §2 *Employee*; columns as listed by SRC-07.

### Error handling
| Failure | Detection | Retry policy | After retries exhausted | Alert | Recovery / replay |
|---------|-----------|--------------|-------------------------|-------|-------------------|
| ERP folder unreachable | Transfer error | 18:15, 18:30, 18:45 (BR-022) | Batch DeliveryFailed; claims stay ReadyForExport | MSG-22 to Finance + IT ticket MSG-43 | Next day's 18:00 batch includes them |
| Line rejected by ERP | `REJ_` file | — | Claim ExportFailed | MSG-25 | Fix → ReadyForExport → next batch (US-010) |
| Unknown reference in `REJ_` | No matching line | — | Logged | MSG-26 | Finance investigates with IT |
| Summary mismatch / missing | `SUM_` check | — | Batch Held | MSG-36 to FC | FC releases with reason (US-019) |
| HR file missing/invalid at 02:00 | No file / validation | — | Yesterday's data in use | IT ticket MSG-43 | Next night's file |

### Reconciliation
| Check | Frequency | Method | Tolerance | Action on mismatch |
|-------|-----------|--------|-----------|--------------------|
| Lines and total exported vs posted | Daily 06:00 per batch | BR-024 against `SUM_` and `REJ_` | 0 lines, €0.00 | Batch Held, MSG-36, no *Paid* until released |

### Security
SFTP with key-based authentication; keys in the company vault, rotated yearly; no passwords in configuration;
files encrypted at rest by the ERP (SRC-07). See NFR-09.

## 7. Notifications
| Event | Channel | Recipient | Timing | Message |
|-------|---------|-----------|--------|---------|
| Claims waiting ≥ 3 business days | Email digest | Each approver (incl. delegate, escalation target) | 08:00 business days (A-050) | MSG-20 |
| Escalation | Email | Approver + escalation target | 08:00 on business day 5 | MSG-21 |
| No manager on record | Email digest | HR Ops | 08:00 business days | MSG-31 |
| Finance check overdue | Email digest | Finance Controller | 08:00 business days | MSG-40 |
| Reassigned | Email | New approver | When the reassignment is saved | MSG-32 |
| Export failed / rejections / unmatched | Email | Finance team | After the run | MSG-22, MSG-25, MSG-26 |
| Reconciliation mismatch | Email | Finance Controller | 06:00 | MSG-36 |
| Leaver warning | Email | Finance team | 10 days before leave date | MSG-27 |
| Paid | Email | Claimant (entering Finance member for on-behalf claims, A-071) | When batch marked paid | MSG-23 |
| Returned | Email | Claimant | When returned | MSG-46 (A-069) |
| Rejected | Email | Claimant | When rejected | MSG-47 (A-069) |
| Next level / withdraw | — | — | No email; next approver sees it in inbox and digest (A-069) | — |
| HR file / export failure | IT service desk ticket | IT | After the failed run | MSG-43 |
No opt-out for any notification in the MVP (A-066).

## 8. Reporting & audit
| Report | Content | Who | Rule |
|--------|---------|-----|------|
| Finance list (SCR-09) | Filter, count, sums, CSV (AC-013.2) | Finance team, FC | D-010 |
| G-01 summary | Avg calendar days first submission → paid; avg business days → exported, per paid month | FC | D-027 |
| G-02 summary | Claims first submitted in a month with times_returned ≥ 1 ÷ claims first submitted that month | FC | D-005 |
| Leaver check | leaver_flag filter | FC | G-04 |
| Anonymised totals | cost centre × category × month after retention | FC | BR-028 |

## 9. Non-functional requirements
| ID | Category | Requirement | Source |
|----|----------|-------------|--------|
| NFR-01 | Performance | Inbox and My claims load within 2 s at p95 with 150 concurrent users | A-024 |
| NFR-02 | Performance | Receipt upload of 10 MB completes within 10 s on 4G | A-024 |
| NFR-03 | Availability | 99.5% monthly, 07:00–22:00 Europe/Paris | A-024 |
| NFR-04 | Security | Entra ID SSO only; role and state checks server-side on every action | D-039 |
| NFR-05 | Privacy | Receipts and claim data are visible only to the claimant, people who are or were an approver on that claim (incl. as delegate, escalation target or reassignee) and the Finance team incl. the Finance Controller; server-side checks on every request | A-060 |
| NFR-06 | Audit & retention | Claims, receipts and approval history are kept until the retention end of BR-028 and then deleted except anonymised totals; approval history cannot be edited by any role | SRC-02, D-034 |
| NFR-07 | Accessibility | WCAG 2.2 AA on SCR-01, SCR-02, SCR-03, SCR-04, SCR-05, SCR-06, SCR-07, SCR-08, SCR-09, SCR-10 | A-011 |
| NFR-08 | Observability | Every run of INT-01, INT-02, INT-03, the digests and the retention job is logged with start, end, row count and result; a failed run raises its alert (MSG-22, MSG-36, MSG-43) in the same run | D-038 (alerts), A-067 (log content) |
| NFR-09 | Security (integration) | SFTP key-based auth, keys from the company vault, rotated yearly; no credentials in code or config files | SRC-07 |
| NFR-10 | Throughput | The 18:00 export of up to 2,000 lines, including all retries, is delivered before 21:30 or marked DeliveryFailed | SRC-07, D-038 |

## 10. Compliance matrix
| Clause | Requirement IDs | Evidence |
|--------|-----------------|----------|
| Policy §4.1 (90 days) | BR-001 | AC-002.2, AC-002.9, AC-014.4 |
| Policy §4.2 (itemised receipt > €25) | BR-002, BR-010 | AC-002.3, AC-002.4, AC-007.1 |
| Policy §5.1, §5.2 + v3.3 dept head | BR-007 | AC-003.2 |
| Policy §5.3 (no self-approval) | BR-009 | AC-003.3, AC-005.3, AC-007.3 |
| Policy §5.4 (delegate > 3 working days) | BR-008 | AC-005.4 |
| Policy §6.1 (alcohol, fines, personal) | BR-005, BR-010 | AC-002.1 |
| Policy §6.2 (leavers paid in final salary) | BR-016, BR-017 | AC-011.1, AC-014.1 |
| Policy v3.3 (domestic cap, receipts abroad) | BR-002, BR-003 | AC-002.5, AC-002.7, AC-002.8 |
| Tax retention 7 years (SRC-02) | BR-028, NFR-06 | AC-020.1, AC-020.2 |

## 11. Web specifics (web-app profile)
| Topic | Requirement |
|-------|-------------|
| Browsers / min width | Latest 2 versions of Chrome and Edge (desktop), Safari iOS, Chrome Android (A-065); 360 px (A-009) |
| Authentication | Entra ID SSO (D-039); session timeout 30 min idle (A-022) |
| Lists | 25 per page (A-053); sort as in §3 |
| Concurrency | Two people able to decide the same step (manager/delegate/escalation target): first decision wins; the other sees MSG-34 (A-023, D-026) |
| Unsaved changes | Autosave (A-019) |

## 12. Proposed defaults awaiting confirmation
Only IDs — the values live in `02-questions.md` → *Assumptions*:
A-004, A-009, A-010, A-011, A-012, A-014, A-015, A-017, A-018, A-019, A-022, A-023, A-024, A-033, A-034, A-035,
A-038, A-039, A-040, A-041, A-042, A-043, A-044, A-045, A-046, A-047, A-048, A-049, A-050, A-051, A-052, A-053,
A-054, A-055, A-056, A-057, A-058, A-059, A-060, A-061, A-062, A-063, A-064, A-065, A-066, A-067, A-068, A-069,
A-070, A-071, A-072, A-073, A-074, A-075, A-076, A-077, A-078, A-079, A-080, A-081, A-082.

### Do not guess — stop and ask
| Topic | Question | Until answered |
|-------|----------|----------------|
| Rejected lines / re-send | Q-039 | **Blocking** — do not build BR-023 re-send or BR-024 counting |
| Interface values not in SRC-07 | Q-042 | Build to A-054, A-055 behind configuration |
| Mileage receipts | Q-043 | A-056 |
| Meal-cap statuses, trip location, declaration categories | Q-044 | A-057, A-058, A-059 |
| Who sees which claims | Q-045 | A-060 (the narrowest reading) |
| Emails on return/reject | Q-046 | A-069 |
| Valid cost centres | Q-049 | A-072 |
| HR row errors / missing employees | Q-051 | A-074 |

## Grounding self-check (step 13) — 2026-10-26
All 28 `BR-` rows cite `SRC-`/`D-`/`A-`; each citation re-read against the source. Qualifiers checked:
"domestic" (BR-003), "absent > 3 working days" (BR-008), "claimed total" (BR-007), "end of financial year"
(BR-028). Values newly registered: A-049 (VAT format), A-053 (25 rows per page). Removed: Finance no-manager queue,
leaver submission block (MSG-28), unsourced 15-minute alert time (NFR-08 rewritten), unsourced volume/day figure.

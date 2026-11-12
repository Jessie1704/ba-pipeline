# 05 · User Stories — Expense claims & approvals

> v1.0 draft — updated 2026-10-26 for round-2 decisions (SRC-06, SRC-07; decision log in `_status.md`).
> Withdrawn: ~~AC-011.3~~ (withdrawn, D-021 — login is disabled at the leave date, no system block needed).

## Example data used in AC
| Id | Who | Notes |
|----|-----|-------|
| E1001 | Employee | Manager M200, department head H300, cost centre 4100 |
| E1002 | Employee | Active, no leave date |
| E1050 | Employee | No manager in the HR file; department head H300 |
| E1051 | Employee | No manager and no department head in the HR file |
| E1070 | Employee | Manager and department head are both H300 |
| E1080 | Employee | Manager M220, no department head in the HR file |
| M200 | Line manager | Reports to H300 |
| M201, M205 | Managers | Both report to M200; M201 is M200's delegate in AC-005.1, AC-005.2, AC-005.3, AC-005.4 |
| M202, M210, M220 | Managers | New managers assigned by HR files in AC-015.1, AC-018.4; M220 manages E1080 |
| H300 | Department head | Reports to P900 |
| F01 | Finance Controller (Linh Tran) | Reports to P900 |
| P900 | CFO (Pierre Laurent) | Escalation target at FC level (D-026) |
| F10, F11 | Finance team members | — |

Calendar: Mon–Fri, French public holidays (2026-11-11, 2026-12-25, 2027-01-01), Europe/Paris (D-041).
Business-day counting: whole days from the business day the claim reached the step (A-051); daily jobs and digests
run at 08:00 (A-050).

## Story map
| Activity → | Submit | Approve | Finance & ERP | Track & leavers | Fallbacks & supervision | Data feeds & lifecycle |
|------------|--------|---------|---------------|-----------------|-------------------------|------------------------|
| **MVP** | US-001, US-002 | US-003, US-004, US-005, US-006 | US-007, US-008, US-009, US-010, US-019 | US-011, US-012, US-013, US-014 | US-015, US-016, US-017 | US-018, US-020 |
| **Later** | Receipt OCR | Mobile push | ERP API | BI dashboard | Admin screen (D-042) | — |

## Epics
| ID | Epic | Goal | Stories |
|----|------|------|---------|
| EP-01 | Submit claims | G-01, G-02 | US-001, US-002 |
| EP-02 | Approve claims | G-01 | US-003, US-004, US-005, US-006 |
| EP-03 | Finance processing & ERP | G-01, G-03 | US-007, US-008, US-009, US-010, US-019 |
| EP-04 | Visibility & leavers | G-01, G-04 | US-011, US-012, US-013, US-014 |
| EP-05 | Fallback approvers & supervision | G-01 | US-015, US-016, US-017 |
| EP-06 | Data feeds & retention | G-01, G-04 | US-018, US-020 |

## Implementation order (dependencies)
US-018 → US-001 → US-002 → US-003 → US-017 → US-015 → US-004 → US-005 → US-006 → US-012 → US-007 → US-008 →
US-010 → US-019 → US-009 → US-011 → US-014 → US-016 → US-013 → US-020

---

## US-001 · Submit a claim with receipts
**Epic:** EP-01 · **Priority:** Must · **Size:** M
**As an** employee, **I want** to create a claim with expense lines and photos of receipts, **so that** I get reimbursed without emailing spreadsheets (G-01).

```gherkin
# AC-001.1 — happy path
Scenario: Employee submits a claim with two lines
  Given employee "E1001" has a draft claim with a train line of €84.00 dated 2026-11-03 with a receipt image
  And a domestic meals line of €32.50 dated 2026-11-03 with a receipt image
  When the employee submits the claim
  Then the claim status is "InApproval" with current approver "M200"
  And the claimed total is €116.50

# AC-001.2 — alternative: receipt from phone camera
Scenario: Employee attaches a receipt from the phone camera
  Given the employee opens a draft claim on a phone browser 360 px wide
  When the employee adds a receipt using the camera option
  Then the photo is attached to the line as a JPEG of at most 10 MB

# AC-001.3 — failure: unsupported file
Scenario: Employee uploads an unsupported file
  Given a draft claim with one line
  When the employee uploads "receipt.heic.zip"
  Then the upload is refused with MSG-07

# AC-001.4 — alternative: delete a draft
Scenario: Employee deletes a draft
  Given employee "E1001" has draft claim C-1020 that was never submitted
  When the employee deletes C-1020 and confirms
  Then C-1020 is "Withdrawn" and no longer listed in My claims
```
| Item | Detail |
|------|--------|
| Business rules | BR-001, BR-002, BR-003, BR-004, BR-005, BR-006 (checked on submit, see US-002), BR-012 |
| UI | SCR-02, SCR-01 |
| Data touched | Claim, ExpenseLine, Receipt |
| Open items | A-009 (360 px), A-015 (file limits) |
| Traces to | G-01, G-02, IS-01, flow step 1, SRC-01, D-004 |

## US-002 · Policy checks at submission
**Epic:** EP-01 · **Priority:** Must · **Size:** M
**As an** employee, **I want** to be told about policy problems before I submit, **so that** my claim isn't returned later (G-02).

```gherkin
# AC-002.1 — happy path
Scenario: A compliant claim passes all checks
  Given today is 2026-11-30
  And a draft claim with a train line of €84.00 dated 2026-11-03 with a receipt
  And a domestic meals line of €18.00 dated 2026-11-03 without a receipt, declaration ticked
  When the employee submits
  Then no policy errors are shown and the claim is submitted

# AC-002.2 — failure: too old (boundary)
Scenario Outline: Expense date limit
  Given today is 2026-11-30 and the claim has never been submitted before
  And a line dated <date>
  When the employee submits
  Then the result is <result>
  Examples:
    | date       | result                    |
    | 2026-09-01 | submitted (day 90)        |
    | 2026-08-31 | blocked with MSG-01 (91)  |

# AC-002.3 — failure: missing receipt above €25
Scenario: Line above €25 without a receipt
  Given a taxi line of €25.01 without a receipt
  When the employee submits
  Then submission is blocked with MSG-02 on that line

# AC-002.4 — boundary: no receipt needed at €25.00
Scenario: Line of exactly €25 without receipt
  Given an "other" line (parking) of €25.00 without a receipt
  When the employee submits
  Then the claim is submitted

# AC-002.5 — calculation: domestic meal cap per day across claims
Scenario: Domestic meals above €40 on one day are capped
  Given employee "E1001" already has an approved domestic meals line of €30.00 dated 2026-11-03
  And a new draft domestic meals line of €25.00 dated 2026-11-03
  When the employee submits
  Then the new line's reimbursable amount is €10.00 and MSG-03 explains the cap

# AC-002.6 — calculation: mileage
Scenario: Mileage is calculated from kilometres
  Given a mileage line from "Lyon" to "Grenoble" of 112 km without a receipt
  When the line is saved and the claim is submitted
  Then the amount is €33.60 and no receipt is required (A-056)

# AC-002.7 — alternative: meals abroad are not capped (D-024)
Scenario: Meals abroad above €40 are fully reimbursable
  Given a meals line marked "abroad" of €62.00 dated 2026-11-04 with a receipt
  When the employee submits
  Then the line's reimbursable amount is €62.00 and no cap message is shown

# AC-002.8 — failure: meals abroad need a receipt at any amount (D-024)
Scenario: Meal abroad of €18 without receipt
  Given a meals line marked "abroad" of €18.00 without a receipt
  When the employee submits
  Then submission is blocked with MSG-37 on that line

# AC-002.9 — alternative: resubmission keeps the first submission date (D-031)
Scenario: Returned claim resubmitted after day 90
  Given claim C-1013 was first submitted on 2026-11-20 with a line dated 2026-08-23 (day 89)
  And C-1013 was returned on 2026-11-25
  When the employee resubmits C-1013 on 2026-12-01
  Then BR-001 is checked against 2026-11-20 and the claim is submitted
```
| Item | Detail |
|------|--------|
| Business rules | BR-001 deadline, BR-002 receipt, BR-003 domestic meal cap, BR-004 mileage, BR-005 exclusions declaration, BR-006 line count |
| UI | SCR-02 |
| Data touched | ExpenseLine.trip_location, Claim.first_submitted_at |
| Traces to | G-02, IS-02, flow step 2, SRC-02, SRC-03, D-002, D-012, D-017, D-024, D-031 |

## US-003 · Route a claim to the right approvers
**Epic:** EP-02 · **Priority:** Must · **Size:** M
**As the** Finance Controller, **I want** each claim to go to exactly the approvers policy requires, **so that** no claim skips a control (G-01).

```gherkin
# AC-003.1 — happy path: small claim
Scenario: Claim of €116.50 needs only the manager
  Given employee "E1001" whose manager is "M200"
  When a claim with a claimed total of €116.50 is submitted
  Then the approval chain is ["M200"]

# AC-003.2 — alternative: > €500 and > €1,000
Scenario Outline: Chain by claimed total
  Given employee "E1001" with manager "M200" and department head "H300"
  When a claim with a claimed total of <total> is submitted
  Then the approval chain is <chain>
  Examples:
    | total     | chain                                  |
    | €500.00   | M200                                   |
    | €500.01   | M200, Finance Controller               |
    | €1,000.00 | M200, Finance Controller               |
    | €1,000.01 | M200, H300, Finance Controller         |

# AC-003.3 — failure: no self-approval
Scenario: Manager's own claim goes to their manager
  Given "M200" reports to "H300"
  When "M200" submits a claim of €80.00
  Then the approval chain is ["H300"] and "M200" cannot approve it

# AC-003.4 — alternative: no manager on record (D-022, see US-015)
Scenario: Employee without a manager in the HR file
  Given employee "E1050" has no manager in the latest HR file
  When "E1050" submits a claim of €60.00
  Then the claim status is "AwaitingApprover" and no approver inbox shows it

# AC-003.5 — alternative: one person at two consecutive levels approves once (D-018)
Scenario: Manager is also the department head
  Given employee "E1070" whose manager and department head are both "H300"
  When a claim with a claimed total of €1,200.00 is submitted
  Then the approval chain is ["H300 (manager + department head)", "Finance Controller"]

# AC-003.6 — boundary: thresholds use the claimed total, not the reimbursable total (D-032)
Scenario: Capped claim still reaches the department head
  Given a claim with a claimed total of €1,050.00 whose reimbursable total after the meal cap is €980.00
  When it is submitted by "E1001"
  Then the approval chain is ["M200", "H300", "Finance Controller"]
```
| Item | Detail |
|------|--------|
| Business rules | BR-007 routing, BR-008 delegation, BR-009 no self-approval, BR-018 no manager, BR-019 fallback approvers |
| Data touched | ApprovalStep, Employee.manager_id, Employee.department_head_id |
| Traces to | G-01, IS-03, flow steps 3, 4, 5, 6, SRC-03 §5, D-003, D-018, D-022, D-032 |

## US-004 · Decide on claims from my inbox
**Epic:** EP-02 · **Priority:** Must · **Size:** M
**As an** approver, **I want** an inbox of claims waiting for me where I can approve, return or reject, **so that** nothing gets lost (G-01).

```gherkin
# AC-004.1 — happy path
Scenario: Manager approves a claim
  Given manager "M200" has claim C-1001 (claimed €116.50) in the inbox
  When "M200" approves C-1001
  Then C-1001 moves to "FinanceCheck" and leaves the inbox

# AC-004.2 — alternative: return for changes restarts the chain
Scenario: Finance Controller returns a claim
  Given claim C-1002 (€650.00) approved by "M200" and waiting for the Finance Controller
  When the Finance Controller returns it with reason "Hotel receipt missing VAT number"
  Then C-1002 is "Returned" to the employee with that reason
  And after resubmission the chain starts again at "M200"

# AC-004.3 — failure: reason mandatory
Scenario: Reject without reason
  Given manager "M200" opens claim C-1003
  When "M200" clicks reject without entering a reason
  Then the rejection is not saved and MSG-08 is shown

# AC-004.4 — alternative: bulk approve at month end (D-025)
Scenario: Manager approves 12 small claims at once
  Given "M200" selects 12 claims in the inbox, all at the manager level, each with a claimed total of €250.00 or less and none with a Leaver flag
  When "M200" chooses bulk approve and confirms
  Then each of the 12 claims moves to its next state per BR-007

# AC-004.5 — alternative: reject
Scenario: Manager rejects a claim
  Given manager "M200" has claim C-1003 (€45.00) in the inbox
  When "M200" rejects it with reason "Personal expense"
  Then C-1003 is "Rejected", leaves the inbox, and the claimant sees the reason

# AC-004.6 — boundary: claims outside the bulk limits can't be selected (D-025)
Scenario Outline: Bulk-approve eligibility
  Given claim <claim> in M200's inbox with claimed total <total>, level <level>, leaver flag <leaver>
  When "M200" views the inbox
  Then the claim's bulk checkbox is <checkbox>
  Examples:
    | claim  | total   | level     | leaver | checkbox                       |
    | C-1101 | €250.00 | manager   | no     | enabled                        |
    | C-1102 | €250.01 | manager   | no     | disabled with tooltip MSG-39   |
    | C-1103 | €80.00  | manager   | yes    | disabled with tooltip MSG-39   |

# AC-004.7 — failure: bulk selection above 50
Scenario: 51 claims selected
  Given "M200" has 60 eligible claims in the inbox
  When "M200" selects a 51st claim
  Then the selection stays at 50 and MSG-39 is shown

# AC-004.8 — failure: invalid transition (claim withdrawn meanwhile)
Scenario: Approve a claim that was withdrawn
  Given "M200" opened claim C-1011 at 10:00
  And the claimant withdrew C-1011 at 10:02
  When "M200" clicks approve at 10:03
  Then the approval is refused with MSG-33 and C-1011 stays "Withdrawn"
```
| Item | Detail |
|------|--------|
| Business rules | BR-007, BR-009, BR-013, BR-014, BR-027 |
| UI | SCR-03, SCR-04 |
| Traces to | G-01, IS-04, flow steps 4, 5, 6, SRC-04 F20, D-007, D-025, R-03 |

## US-005 · Nominate a delegate
**Epic:** EP-02 · **Priority:** Must · **Size:** S
**As a** manager, **I want** to nominate a delegate for my absence, **so that** my team's claims are not stuck (G-01).

```gherkin
# AC-005.1 — happy path: both may decide (D-023)
Scenario: Delegate receives claims during absence
  Given "M200" nominated "M201" from 2026-12-14 to 2026-12-31
  When a claim from M200's team is routed on 2026-12-22
  Then it appears in M201's inbox with badge "for M200" and in M200's inbox
  And whichever of them decides first records the decision (MSG-34 for the other)

# AC-005.2 — boundary: delegation ends
Scenario: Delegation period ended
  Given the delegation ended on 2026-12-31
  When a claim is routed on 2027-01-02
  Then it appears only in M200's inbox

# AC-005.3 — failure: delegate cannot approve own claim
Scenario: Delegate is the claimant
  Given "M201" is delegate for "M200"
  When "M201" submits a claim of €60.00
  Then "M201" cannot approve it and it remains with "M200" only

# AC-005.4 — failure: delegation too short (policy §5.4)
Scenario: Delegation of 3 working days is refused
  Given "M200" nominates "M201" from Monday 2026-12-07 to Wednesday 2026-12-09
  When "M200" saves the delegation
  Then it is refused with MSG-09

# AC-005.5 — failure: delegate who is a later approver on the claim (D-020)
Scenario: Department head is also the manager's delegate
  Given "M200" nominated "H300" as delegate from 2026-12-14 to 2026-12-31
  And "E1001" submits a claim with a claimed total of €1,200.00 on 2026-12-15
  When "H300" opens the claim at the manager level
  Then approve, return and reject are not available to "H300" and MSG-42 explains why
  And after "M200" approves, the claim appears in H300's inbox at the department-head level
```
| Item | Detail |
|------|--------|
| Business rules | BR-008, BR-009 |
| UI | SCR-05, SCR-03 |
| Open items | A-018 (60-day maximum), A-038 (CFO delegation, Q-034) |
| Traces to | G-01, IS-04, SRC-03 §5.4, D-011, D-020, D-023 |

## US-006 · Reminders and escalation
**Epic:** EP-02 · **Priority:** Must · **Size:** M
**As the** Finance Controller, **I want** overdue approvals reminded and escalated, **so that** claims are paid on time (G-01).

```gherkin
# AC-006.1 — reminder in the daily digest from business day 3
Scenario: Claim appears in the reminder digest
  Given claim C-1004 reached "M200" on Monday 2026-11-02
  When the 08:00 digest runs on Thursday 2026-11-05 and C-1004 is still waiting
  Then "M200" receives one MSG-20 digest that lists C-1004

# AC-006.2 — escalation on business day 5 across a weekend and a public holiday
Scenario: Escalation skips the weekend and 11 November
  Given claim C-1005 reached "M200" on Thursday 2026-11-05
  And 2026-11-11 is a French public holiday
  When the 08:00 job runs on Friday 2026-11-13 and C-1005 is still waiting
  Then C-1005 is also added to the inbox of M200's manager "H300" and both are notified with MSG-21

# AC-006.7 — boundary: no escalation one business day early (was AC-006.2b, renamed for the ID convention)
Scenario: No escalation on Thursday 2026-11-12
  Given claim C-1005 reached "M200" on Thursday 2026-11-05
  When the 08:00 job runs on Thursday 2026-11-12
  Then no escalation has been sent

# AC-006.3 — no reminder after decision
Scenario: Decided claims get no reminder
  Given claim C-1006 reached "M200" on Monday 2026-11-02
  And "M200" approved it on Tuesday 2026-11-03
  When the 08:00 jobs run on Thursday 2026-11-05 and Monday 2026-11-09
  Then no reminder or escalation is sent for C-1006

# AC-006.4 — escalation target may decide (D-026)
Scenario: Escalation target approves
  Given C-1005 was escalated to "H300" on 2026-11-13
  When "H300" approves C-1005 at the manager level
  Then the decision is recorded as "H300 (escalation for M200)" and C-1005 leaves M200's inbox

# AC-006.5 — alternative: Finance Controller level escalates to the CFO (D-026)
Scenario: Claim waiting for the Finance Controller
  Given claim C-1007 (€700.00) reached the Finance Controller "F01" on Monday 2026-11-16
  When the 08:00 job runs on Monday 2026-11-23 and C-1007 is still waiting
  Then C-1007 is added to the inbox of CFO "P900" and MSG-21 is sent to "F01" and "P900"

# AC-006.6 — boundary: only one escalation
Scenario: No second escalation
  Given C-1005 was escalated to "H300" on 2026-11-13 and is still waiting
  When the 08:00 job runs on Friday 2026-11-20
  Then no further escalation is sent and C-1005 stays in the MSG-20 digest of "M200" and "H300"
```
| Item | Detail |
|------|--------|
| Business rules | BR-015 |
| ~~AC-006.2b~~ | (withdrawn ID — same scenario now AC-006.7) |
| Open items | A-050 (08:00 run time), A-051 (day counting), A-046 (clock per level), A-052 (escalation target is also a later approver, Q-041) |
| Traces to | G-01, IS-05, D-008, D-026, D-041 |

## US-007 · Finance check
**Epic:** EP-03 · **Priority:** Must · **Size:** M
**As a** Finance team member, **I want** to check approved claims against the Finance checklist and mark them ready or return them, **so that** only correct claims reach the ERP (G-03).

```gherkin
# AC-007.1 — happy path
Scenario: Finance marks a claim ready
  Given claim C-1001 is in "FinanceCheck"
  And finance user "F10" ticks all five checklist items (BR-010)
  When "F10" marks it OK
  Then C-1001 is "ReadyForExport"

# AC-007.2 — alternative: return for VAT number
Scenario: Finance returns for VAT number
  Given claim C-1007 is in "FinanceCheck"
  When "F10" returns it with checklist item "VAT number recorded" unticked and reason "Supplier VAT number not visible"
  Then C-1007 is "Returned" and approval restarts at the manager on resubmission

# AC-007.3 — failure: finance user is the claimant
Scenario: Finance user cannot check own claim
  Given "F10" submitted claim C-1008 and it is in "FinanceCheck"
  When "F10" opens C-1008
  Then the Mark OK and Return actions are not available to "F10"
  And C-1008 stays in the Finance check queue for other Finance team members

# AC-007.4 — failure: Mark OK with an unticked checklist item
Scenario: Checklist incomplete
  Given claim C-1009 is in "FinanceCheck"
  And "F10" has ticked 4 of the 5 checklist items
  When "F10" clicks Mark OK
  Then nothing changes and MSG-44 names the unticked item

# AC-007.5 — alternative: Finance-check SLA reminder (D-030)
Scenario Outline: Claim exceeding the 2-business-day Finance-check SLA
  Given claim C-1014 reached "FinanceCheck" on Monday 2026-11-16
  When the 08:00 digest runs on <date> and C-1014 is still in "FinanceCheck"
  Then <result>
  Examples:
    | date                  | result                                           |
    | Wednesday 2026-11-18  | C-1014 is not in MSG-40 (day 2, SLA not exceeded) |
    | Thursday 2026-11-19   | the Finance Controller receives MSG-40 listing C-1014 |

# AC-007.7 — failure: anyone who approved the claim can't check it (A-075)
Scenario: Finance team member approved the claim as a delegate
  Given "F11" approved claim C-1031 at the manager level as delegate
  When "F11" opens C-1031 in the Finance check queue
  Then the Mark OK and Return actions are not available to "F11"

# AC-007.6 — failure: Finance Controller approved the claim (D-033)
Scenario: Finance Controller cannot check a claim she approved
  Given the Finance Controller "F01" approved claim C-1030 at the Finance Controller level
  When "F01" opens C-1030 in the Finance check queue
  Then the Mark OK and Return actions are not available to "F01"
```
| Item | Detail |
|------|--------|
| Business rules | BR-009, BR-010, BR-013, BR-021 |
| UI | SCR-06, SCR-07 |
| Data touched | ExpenseLine.vat_number, FinanceCheck checklist |
| Open items | A-045 (FC reminder digest), A-039 (on-behalf, Q-035), A-072 (valid cost centres), A-075 |
| Traces to | G-03, IS-06, flow step 7, SRC-01, D-029, D-030, D-033 |

## US-008 · Daily export to ERP
**Epic:** EP-03 · **Priority:** Must · **Size:** M
**As a** Finance team member, **I want** ready claims exported to the ERP every day at 18:00, **so that** nobody re-keys them (G-03).

```gherkin
# AC-008.1 — happy path
Scenario: Ready claims are exported
  Given 37 claims with 112 lines are "ReadyForExport" at 18:00 on 2026-11-16
  When the daily export runs
  Then one file "EXP_20261116.csv" with batch id "EXP-20261116" and 112 lines is delivered to the ERP inbound folder
  And all 37 claims are "Exported" in batch "EXP-20261116"

# AC-008.2 — alternative: nothing to export
Scenario: No ready claims
  Given no claims are "ReadyForExport" at 18:00
  When the daily export runs
  Then no file is sent and the run is logged as "empty"

# AC-008.3 — failure: export cannot be delivered (D-038)
Scenario: ERP inbound folder unavailable
  Given the ERP inbound folder is unreachable from 18:00 to 19:00
  When the export runs at 18:00 and retries at 18:15, 18:30 and 18:45
  Then the batch is "DeliveryFailed", claims stay "ReadyForExport", the Finance team gets MSG-22 and an IT service desk ticket is opened
  And no further retry runs that day

# AC-008.4 — alternative: file content (D-036, D-037)
Scenario: One exported line
  Given claim C-1001 line 2 is a meals line of reimbursable €32.50, cost centre "4100", description "Lunch with client at Lyon site"
  When it is exported on 2026-11-16
  Then its row is "EXP-20261116;2026-11-16;625700;4100;32.50;E1001;C-1001/2;Lunch with client at Lyon site"
```
| Item | Detail |
|------|--------|
| Business rules | BR-011, BR-022, INT-01 mapping |
| Open items | A-044 (description cut to 50 chars) |
| Traces to | G-03, IS-06, flow step 8, SRC-01 F6, D-013, D-036, D-037, D-038 |

## US-009 · Mark exported claims as paid
**Epic:** EP-03 · **Priority:** Must · **Size:** S
**As a** Finance team member, **I want** to mark an export batch as paid after its payroll run, **so that** employees see their claim is paid and G-01 can be measured (G-01).

```gherkin
# AC-009.1 — happy path
Scenario: Batch marked paid
  Given batch EXP-20261116 with 37 claims is "Reconciled" with payroll month 2026-11
  When "F10" marks the batch paid with paid date 2026-11-27 on 2026-11-28
  Then all 37 claims are "Paid" with paid date 2026-11-27 and each claimant gets MSG-23

# AC-009.2 — alternative: failed rows excluded
Scenario: Batch with a failed row
  Given claim C-1010 in batch EXP-20261116 is "ExportFailed"
  When "F10" marks the batch paid
  Then C-1010 stays "ExportFailed"

# AC-009.3 — failure: future date
Scenario: Paid date in the future
  When "F10" enters paid date 2026-12-31 on 2026-11-28
  Then MSG-24 is shown and nothing changes

# AC-009.4 — boundary: payroll month by cut-off (D-028)
Scenario Outline: Payroll month of a batch
  Given batch <batch> from the export run of <date> was delivered at <time>
  When Finance opens the batch on SCR-08
  Then its payroll month is <month>
  Examples:
    | batch        | date       | time  | month   |
    | EXP-20261120 | 2026-11-20 | 18:00 | 2026-11 |
    | EXP-20261120 | 2026-11-20 | 18:15 | 2026-11 |
    | EXP-20261121 | 2026-11-21 | 18:00 | 2026-12 |

# AC-009.5 — failure: held batch (BR-024)
Scenario: Mark paid on a held batch
  Given batch EXP-20261117 is "Held"
  When "F10" tries to mark it paid
  Then MSG-35 is shown and nothing changes
```
| Item | Detail |
|------|--------|
| Business rules | BR-020, BR-024 |
| Open items | A-062, A-070 (Q-047) |
| UI | SCR-08 |
| Traces to | G-01, IS-06, flow step 10, D-019, D-028 |

## US-010 · Handle ERP rejections
**Epic:** EP-03 · **Priority:** Must · **Size:** M
**As a** Finance team member, **I want** claims the ERP rejects to be flagged, **so that** I fix them before payroll (G-01).

```gherkin
# AC-010.1 — happy path
Scenario: Rejection file flags claims
  Given the ERP wrote "REJ_EXP-20261116.csv" by 06:00 on 2026-11-17 listing reference "C-1010/1" with error text "Unknown cost centre"
  When the 06:00 file check runs
  Then C-1010 is "ExportFailed" with that error and the Finance team gets MSG-25

# AC-010.2 — alternative: fixed claim re-exported in full
Scenario: Finance fixes and re-exports
  Given C-1010 (3 lines) is "ExportFailed"
  When "F10" corrects the cost centre and marks it ready
  Then all 3 lines of C-1010 are in the next 18:00 export (A-043)

# AC-010.3 — failure: rejection for unknown claim
Scenario: Rejection references a claim not in the batch
  Given the rejection file lists reference "C-9999/1" not in batch EXP-20261116
  When the rejection file is processed
  Then the row is logged as unmatched and the Finance team is alerted with MSG-26

# AC-010.4 — alternative: no rejection file
Scenario: Nothing rejected
  Given no "REJ_EXP-20261116.csv" exists at 06:00 on 2026-11-17
  When the 06:00 file check runs
  Then no claim in EXP-20261116 changes state
```
| Item | Detail |
|------|--------|
| Business rules | BR-023 |
| UI | SCR-08 |
| Open items | A-043 (Q-039) |
| Traces to | G-01, IS-06, flow step 9, R-02, D-036, D-038 |

## US-011 · Prioritise leavers' claims
**Epic:** EP-04 · **Priority:** Must · **Size:** S
**As** HR Operations, **I want** leavers' open claims flagged and Finance warned, **so that** they are paid in the final salary (G-04).

```gherkin
# AC-011.1 — happy path
Scenario: Leaver's claims flagged
  Given the HR file sets leave date 2026-12-15 for "E1001" on 2026-11-20
  And "E1001" has 2 claims not yet exported
  When the nightly HR import runs
  Then both claims show the "Leaver" flag and sort first in every approver inbox

# AC-011.2 — warning 10 days before
Scenario: Finance warned before leave date
  Given "E1001" leaves on 2026-12-15 with claims not yet exported
  When the date is 2026-12-05
  Then the Finance team receives MSG-27 listing those claims

# AC-011.4 — alternative: leave date removed
Scenario: Resignation withdrawn
  Given "E1001" has the "Leaver" flag from leave date 2026-12-15
  When the HR file of 2026-11-25 has no leave date for "E1001"
  Then the "Leaver" flag is removed from E1001's claims (A-061)

# AC-011.5 — boundary: leave date entered less than 10 days ahead (A-073)
Scenario: Short-notice leaver
  Given the HR file of 2026-12-10 sets leave date 2026-12-15 for "E1001" with 1 claim not yet exported
  When the 02:00 import of 2026-12-10 runs
  Then the Finance team receives MSG-27 once that day and not again on later days

# AC-011.6 — failure: HR import missing on the warning day (A-073)
Scenario: Warning day without an HR import
  Given "E1001" leaves on 2026-12-15 and the HR import of 2026-12-05 failed
  When the 02:00 import of 2026-12-06 succeeds
  Then the Finance team receives MSG-27 on 2026-12-06
```
| Item | Detail |
|------|--------|
| Business rules | BR-016 |
| UI | SCR-03 (flag), SCR-09 (filter) |
| ~~AC-011.3~~ | (withdrawn, D-021) leaver submission block removed — login is disabled at the leave date |
| Traces to | G-04, IS-07, SRC-04, D-009, D-039 |

## US-012 · Track my claims and withdraw
**Epic:** EP-04 · **Priority:** Must · **Size:** S
**As an** employee, **I want** to see the status of my claims and withdraw one, **so that** I don't need to chase anyone (G-01).

```gherkin
# AC-012.1 — happy path
Scenario: Status visible
  Given "E1001" has claims in "Draft", "InApproval" (waiting for "M200") and "Paid"
  When "E1001" opens My claims
  Then each claim shows its status, current approver if any, and last update date

# AC-012.2 — alternative: withdraw before first decision
Scenario: Withdraw a submitted claim
  Given claim C-1011 is "InApproval" and no approver has decided
  When "E1001" withdraws it
  Then C-1011 is "Withdrawn" and leaves M200's inbox

# AC-012.3 — failure: withdraw after a decision
Scenario: Cannot withdraw after approval started
  Given claim C-1012 was approved by "M200" and waits for the Finance Controller
  When "E1001" tries to withdraw it
  Then MSG-29 is shown and the claim is unchanged

# AC-012.4 — alternative: withdraw a returned claim
Scenario: Withdraw instead of resubmitting
  Given claim C-1015 is "Returned"
  When "E1001" withdraws it
  Then C-1015 is "Withdrawn" and can no longer be edited

# AC-012.5 — alternative: withdraw while waiting for a manager record
Scenario: Withdraw an AwaitingApprover claim
  Given claim C-1064 from "E1050" is "AwaitingApprover"
  When "E1050" withdraws it
  Then C-1064 is "Withdrawn" and no longer appears in the HR Ops list MSG-31
```
| Item | Detail |
|------|--------|
| UI | SCR-01 |
| Open items | A-035 (withdraw until first decision) |
| Traces to | G-01, IS-08 |

## US-013 · Finance claims list and export
**Epic:** EP-04 · **Priority:** Must · **Size:** S
**As the** Finance Controller, **I want** to filter all claims and export the list, **so that** I can monitor goals and answer audits (G-01, G-03, G-04).

```gherkin
# AC-013.1 — happy path
Scenario: Filter by status and month
  Given 900 claims first submitted in November 2026
  When the Finance Controller filters status "InApproval" and month "2026-11"
  Then only matching claims are listed with total count and sum of claimed totals

# AC-013.2 — alternative: CSV export of the filtered list
Scenario: Export filtered list
  When the Finance Controller exports the filtered list
  Then a CSV is downloaded with columns claim_id, employee, status, total_claimed, total_reimbursable, first_submitted_at, current_approver, leaver_flag, export_batch_id, paid_date

# AC-013.4 — alternative: leaver check (G-04)
Scenario: Monthly leaver check
  When the Finance Controller filters leaver_flag = yes and month "2026-12"
  Then each leaver's claims are listed with status, so unpaid approved claims are visible

# AC-013.3 — failure: not finance
Scenario: Manager opens the finance list
  When manager "M200" opens the finance list URL
  Then access is denied with MSG-30

# AC-013.5 — alternative: G-01 metrics (D-027)
Scenario: Monthly reimbursement time
  Given 3 claims paid in December 2026, with first_submitted_at → paid_date of 10, 15 and 20 calendar days
  And first_submitted_at → exported_at of 3, 4 and 5 business days
  When the Finance Controller opens the list summary for paid month "2026-12"
  Then it shows "Average days to payment: 15.0" and "Average business days to export: 4.0"

# AC-013.6 — alternative: G-02 return rate
Scenario: Monthly return rate
  Given 200 claims first submitted in November 2026, of which 5 have times_returned ≥ 1
  When the Finance Controller opens the list summary for first-submission month "2026-11"
  Then it shows "Returned at least once: 2.5%"
```
| Item | Detail |
|------|--------|
| UI | SCR-09 |
| Traces to | G-01, G-02, G-03, G-04, IS-09, D-010, D-027, D-005 |

## US-014 · Enter a claim on behalf of a leaver
**Epic:** EP-04 · **Priority:** Must · **Size:** M
**As a** Finance team member, **I want** to enter a claim for an employee who has already left, **so that** expenses they incurred before leaving are still reimbursed (G-04).

```gherkin
# AC-014.1 — happy path
Scenario: Finance enters a leaver's claim
  Given "E1001" left on 2026-12-15 and can no longer sign in
  And "M200" was E1001's manager on 2026-12-15
  When "F10" enters on 2026-12-20 a claim for "E1001" with a taxi line of €45.00 dated 2026-12-14 with a receipt and submits it
  Then the claim is "InApproval" with current approver "M200", flagged "Leaver" and "Entered by F10 on behalf"

# AC-014.2 — failure: expense after the leave date
Scenario: Line dated after leaving
  Given "E1001" left on 2026-12-15
  When "F10" adds a line dated 2026-12-16 to an on-behalf claim and submits
  Then submission is blocked with MSG-38 on that line

# AC-014.3 — failure: employee has not left
Scenario: On-behalf entry for an active employee
  Given "E1002" has no leave date in the past
  When "F10" searches for "E1002" in the on-behalf claim screen
  Then "E1002" can't be selected and MSG-45 is shown

# AC-014.4 — boundary: 90-day rule still applies
Scenario: Leaver's expense older than 90 days
  Given "E1001" left on 2026-12-15
  When "F10" submits on 2027-03-16 an on-behalf claim with a line dated 2026-12-15 (day 91)
  Then submission is blocked with MSG-01

# AC-014.5 — failure: entering Finance member can't check it (A-039)
Scenario: Segregation for on-behalf claims
  Given "F10" entered on-behalf claim C-1050 and it reached "FinanceCheck"
  When "F10" opens C-1050
  Then the Mark OK and Return actions are not available to "F10"

# AC-014.6 — alternative: returned on-behalf claim (A-071)
Scenario: Finance resubmits a returned on-behalf claim
  Given on-behalf claim C-1051 entered by "F10" was returned by "M200" with reason "Add taxi receipt"
  When "F11" adds the receipt and resubmits C-1051
  Then C-1051 is "InApproval" with current approver "M200" and MSG-46 went to "F10", not to the leaver
```
| Item | Detail |
|------|--------|
| Business rules | BR-001, BR-017, BR-009 |
| UI | SCR-10, SCR-02 (on-behalf mode) |
| Open items | A-039 (Q-035), A-068, A-071 (Q-048) |
| Traces to | G-04, IS-10, flow step 1b, D-021, SRC-06 |

## US-015 · Hold claims with no manager on record
**Epic:** EP-05 · **Priority:** Must · **Size:** M
**As** HR Operations, **I want** claims of employees without a manager record held and listed to me daily, **so that** I fix the record before the claim falls back to the department head (G-01).

```gherkin
# AC-015.1 — happy path: HR fixes the record
Scenario: Manager appears in the next HR file
  Given claim C-1060 from "E1050" is "AwaitingApprover" since Monday 2026-11-02
  When the HR file of Tuesday 2026-11-03 gives "E1050" manager "M210"
  Then after the 02:00 import C-1060 is "InApproval" with current approver "M210"

# AC-015.2 — alternative: daily list to HR Ops
Scenario: HR Ops receives the no-manager list
  Given claims C-1060 and C-1061 are "AwaitingApprover"
  When the 08:00 digest runs on a business day
  Then HR Ops receives one MSG-31 listing both claims with employee id and days waiting

# AC-015.3 — boundary: fallback to the department head after 2 business days (D-022)
Scenario Outline: Fallback timing
  Given claim C-1062 from "E1050" (department head "H300") became "AwaitingApprover" on Thursday 2026-11-05
  When the 08:00 job runs on <date> and E1050 still has no manager
  Then C-1062 is <result>
  Examples:
    | date                 | result                                          |
    | Friday 2026-11-06    | still "AwaitingApprover"                        |
    | Monday 2026-11-09    | "InApproval" with current approver "H300"       |

# AC-015.4 — failure: no manager and no department head
Scenario: Department head also missing
  Given claim C-1063 from "E1051" (no manager, no department head) became "AwaitingApprover" on Thursday 2026-11-05
  When the 08:00 job runs on Monday 2026-11-09 and E1051 still has no manager
  Then C-1063 is "InApproval" with the Finance Controller as approver, as fallback for the vacant department head (BR-019)
```
| Item | Detail |
|------|--------|
| Business rules | BR-018, BR-019 |
| Open items | A-050 (08:00) |
| Traces to | G-01, IS-11, flow step 3, D-022, SRC-06 |

## US-016 · Reassign a waiting approval
**Epic:** EP-05 · **Priority:** Must · **Size:** S
**As the** Finance Controller, **I want** to reassign an approval step that waits for someone who has left or is absent without a delegate, **so that** no claim is stuck (G-01).

```gherkin
# AC-016.1 — happy path
Scenario: Finance Controller reassigns a claim
  Given claim C-1070 waits for "M200" at the manager level
  When the Finance Controller reassigns it to "M205" with reason "M200 on sick leave"
  Then C-1070 appears in M205's inbox, leaves M200's inbox, M205 gets MSG-32 and the step's SLA clock restarts

# AC-016.2 — failure: reassign to the claimant
Scenario: Reassign to the person who submitted the claim
  Given claim C-1071 was submitted by "M205"
  When the Finance Controller tries to reassign it to "M205"
  Then the reassignment is refused with MSG-41

# AC-016.3 — failure: reason missing
Scenario: Reassign without reason
  When the Finance Controller reassigns claim C-1070 without a reason
  Then the reassignment is refused with MSG-08

# AC-016.4 — failure: Finance team member can't reassign (D-033)
Scenario: Finance team member opens a waiting claim
  When "F10" opens claim C-1070 from the Finance list
  Then no Reassign action is shown
```
| Item | Detail |
|------|--------|
| Business rules | BR-025, BR-013 |
| UI | SCR-09, SCR-07 (reassign dialog) |
| Traces to | G-01, IS-11, D-033 |

## US-017 · Fallback approvers for vacant and conflicted levels
**Epic:** EP-05 · **Priority:** Must · **Size:** S
**As the** Finance Controller, **I want** claims routed to a fallback approver when a level is vacant or the claim is my own, **so that** every claim has a valid approver (G-01).

```gherkin
# AC-017.1 — happy path: vacant department head
Scenario: Department head position empty
  Given "E1080" with manager "M220" and no department head in the HR file
  When "E1080" submits a claim with a claimed total of €1,200.00
  Then the approval chain is ["M220", "Finance Controller (department head level + Finance Controller level)"]

# AC-017.2 — alternative: Finance Controller's own claim
Scenario: Finance Controller claims €700
  Given the Finance Controller "F01" reports to "P900"
  When "F01" submits a claim with a claimed total of €700.00
  Then the approval chain is ["P900 (manager + Finance Controller level)"]

# AC-017.3 — boundary: Finance Controller's own claim at €500.00
Scenario: Finance Controller claims €500
  When "F01" submits a claim with a claimed total of €500.00
  Then the approval chain is ["P900"]

# AC-017.4 — failure: Finance Controller can't decide her own claim
Scenario: Finance Controller opens her own claim
  Given "F01" submitted claim C-1035 of €700.00
  When "F01" opens C-1035
  Then approve, return and reject are not available and MSG-42 is shown

# AC-017.5 — alternative: Finance Controller's own claim above €1,000 (A-077)
Scenario: Finance Controller claims €1,200
  When "F01" submits a claim with a claimed total of €1,200.00
  Then the approval chain is ["P900 (manager + department head + Finance Controller level)"]
```
| Item | Detail |
|------|--------|
| Business rules | BR-019, BR-009, BR-007 |
| Traces to | G-01, IS-11, D-018, D-033 |

## US-018 · Import the nightly HR org file
**Epic:** EP-06 · **Priority:** Must · **Size:** M
**As the** Finance team, **I need** employees, managers, department heads, cost centres and leave dates refreshed from the HR system every night, **so that** claims route to the right approver and leavers are flagged (G-01, G-04).

```gherkin
# AC-018.1 — happy path
Scenario: Valid HR file imported
  Given a valid HR file with 420 rows landed at 01:30 on 2026-11-17
  When the 02:00 import runs
  Then 420 employees are refreshed and the run is logged "OK, 420 rows"

# AC-018.2 — failure: file missing
Scenario: No HR file at 02:00
  Given no HR file has landed by 02:00 on 2026-11-18
  When the 02:00 import runs
  Then yesterday's employee data stays in use and an IT service desk ticket MSG-43 is opened

# AC-018.3 — failure: invalid file
Scenario: Column manager_id missing
  Given the HR file of 2026-11-19 has no "manager_id" column
  When the 02:00 import runs
  Then no employee is changed and an IT service desk ticket MSG-43 is opened with reason "missing column manager_id"

# AC-018.4 — alternative: manager changed while a claim waits (A-041)
Scenario: Employee moves to a new manager
  Given claim C-1090 from "E1001" waits for "M200" at the manager level with no decision
  When the HR file of 2026-11-20 gives "E1001" manager "M202"
  Then after the import C-1090 waits for "M202" and its SLA clock restarts

# AC-018.5 — failure: row errors (A-074)
Scenario: One row with an unknown manager
  Given the HR file of 2026-11-21 has 420 rows and the row for "E1002" names manager "M999" who is not in the file
  When the 02:00 import runs
  Then 419 rows are imported, the "E1002" row is skipped with E1002's previous data kept, and the IT ticket MSG-43 lists the row
```
| Item | Detail |
|------|--------|
| Business rules | BR-026, BR-016, BR-018 |
| Open items | A-041 (Q-037), A-017 (cost centre) |
| Traces to | G-01, G-04, IS-12, INT-03, D-039, D-038 |

## US-019 · Reconcile each export batch
**Epic:** EP-03 · **Priority:** Must · **Size:** M
**As the** Finance Controller, **I want** each batch checked against the ERP summary file, **so that** no batch is marked paid with missing or wrong postings (G-01, G-03).

```gherkin
# AC-019.1 — happy path
Scenario: Summary matches
  Given batch EXP-20261116 sent 112 lines totalling €4,210.40 and the ERP rejected none
  And "SUM_EXP-20261116.csv" says LINES_RECEIVED 112, LINES_POSTED 112, TOTAL_POSTED 4210.40
  When the 06:00 file check runs on 2026-11-17
  Then the batch is "Reconciled"

# AC-019.2 — alternative: matches after rejections
Scenario: Summary matches with 2 rejected lines
  Given batch EXP-20261117 sent 120 lines totalling €5,000.00 and the rejection file lists 2 lines totalling €80.00
  And the summary file says LINES_POSTED 118, TOTAL_POSTED 4920.00
  When the 06:00 file check runs
  Then the batch is "Reconciled"

# AC-019.3 — failure: mismatch
Scenario: Posted lines don't add up
  Given batch EXP-20261118 sent 120 lines, 2 were rejected, and the summary file says LINES_POSTED 117
  When the 06:00 file check runs
  Then the batch is "Held" and the Finance Controller gets MSG-36

# AC-019.4 — failure: no summary file
Scenario: Summary file missing
  Given no "SUM_EXP-20261119.csv" exists at 06:00 on 2026-11-20
  When the 06:00 file check runs
  Then the batch is "Held" and the Finance Controller gets MSG-36

# AC-019.5 — alternative: Finance Controller releases a held batch
Scenario: Release after investigation
  Given batch EXP-20261118 is "Held"
  When the Finance Controller releases it with reason "ERP posted 1 line late, confirmed with IT"
  Then the batch is "Reconciled" and can be marked paid
```
| Item | Detail |
|------|--------|
| Business rules | BR-024 |
| UI | SCR-08 |
| Open items | A-040 (Q-036) |
| Traces to | G-01, G-03, IS-06, flow step 9, D-038, R-02 |

## US-020 · Delete expired claim data
**Epic:** EP-06 · **Priority:** Must · **Size:** S
**As the** Finance Controller, **I want** receipts and personal data deleted when the retention period ends while anonymised totals are kept, **so that** we keep evidence as long as the tax authority requires and no longer (compliance, SRC-02).

```gherkin
# AC-020.1 — happy path
Scenario: Paid claim past retention
  Given claim C-1001 was paid on 2027-03-31 (retention end 2034-12-31)
  When the nightly retention job runs on 2035-01-01
  Then C-1001's receipts and personal data are deleted and its amounts are kept in the anonymised totals

# AC-020.2 — boundary: last day of retention
Scenario: Claim on its retention end date
  Given claim C-1001 was paid on 2027-03-31
  When the nightly retention job runs on 2034-12-31
  Then nothing about C-1001 is deleted

# AC-020.3 — alternative: claim never paid (A-048)
Scenario: Rejected claim past retention
  Given claim C-1003 was rejected on 2027-02-10 (retention end 2034-12-31, A-048)
  When the nightly retention job runs on 2035-01-01
  Then C-1003's receipts and personal data are deleted

# AC-020.4 — failure: retention run fails (A-083)
Scenario: Retention job stops part-way
  Given 40 claims reach their retention end on 2034-12-31
  When the retention job of 2035-01-01 fails after 25 claims
  Then the 25 claims are fully deleted, the other 15 are untouched, an IT ticket MSG-43 is opened, and the 15 are processed the next night
```
| Item | Detail |
|------|--------|
| Business rules | BR-028 |
| Open items | A-042 (Q-038), A-047 (nightly job), A-048 (Q-040), A-083 (failure handling) |
| Traces to | IS-13, SRC-02, D-034 |

---

## Coverage check
| Item | Covered by |
|------|-----------|
| IS-01 | US-001 |
| IS-02 | US-002 |
| IS-03 | US-003 |
| IS-04 | US-004, US-005 |
| IS-05 | US-006, AC-007.5 |
| IS-06 | US-007, US-008, US-009, US-010, US-019 |
| IS-07 | US-011 |
| IS-08 | US-012 |
| IS-09 | US-013 |
| IS-10 | US-014 |
| IS-11 | US-015, US-016, US-017 |
| IS-12 | US-018 |
| IS-13 | US-020 |
| Draft → Submitted → InApproval | AC-001.1 |
| Draft → Withdrawn | AC-001.4 |
| Submitted → AwaitingApprover | AC-003.4 |
| AwaitingApprover → InApproval | AC-015.1, AC-015.3 |
| AwaitingApprover → Withdrawn | AC-012.5 |
| InApproval → InApproval (next level / escalate / reassign) | AC-003.2, AC-006.2, AC-016.1 |
| InApproval → FinanceCheck | AC-004.1 |
| InApproval → Returned / Rejected / Withdrawn | AC-004.2, AC-004.5, AC-012.2 |
| FinanceCheck → ReadyForExport / Returned | AC-007.1, AC-007.2 |
| Returned → Submitted / Withdrawn | AC-002.9, AC-012.4 |
| ReadyForExport → Exported | AC-008.1 |
| Exported → ExportFailed → ReadyForExport | AC-010.1, AC-010.2 |
| Exported → Paid | AC-009.1 |
| Batch Sent → Reconciled / Held → Reconciled | AC-019.1, AC-019.3, AC-019.5 |
| Batch DeliveryFailed | AC-008.3 |
| Invalid transitions | AC-004.8, AC-012.3, AC-009.5, AC-005.1 (MSG-34) |

## Grounding self-check (step 8) — 2026-10-26
Every capability, behaviour, number, time and limit in the AC above was checked against `SRC-`, `D-` or a
registered `A-`. **Grounding: 20 stories / 98 AC checked (every AC read once; not a per-statement count),
7 newly registered as assumptions** (A-045, A-046, A-047, A-048, A-050, A-051, A-052).
After review 2a the fix round added 10 AC (now 108); review 2b found 4 unsourced statements introduced in that
round (see 08-review D2) — the self-check was not re-run on the fix round. Removed: leaver submission block (AC-011.3, D-021), Finance no-manager queue (D-022).
Example values (ids, amounts, dates, names of claims) are test data, not requirements.

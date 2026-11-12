# Workshop notes — Expense claims round 2 (PILOT — fictional data, simulated answers)

Date: 2026-10-26 · 45 min · Attendees: Linh Tran (Finance Controller, PO), Marco Rossi (HR Operations Lead),
pilot BA. Pre-read: BR-007 decision table, claim state machine.

All answers below are **simulated** by Claude for the pilot. Raw notes as taken, grouped by agenda item.

## 1. Fallbacks & escalation

- **Q-020 (no manager on record):** Marco: "Don't send it to Finance, and don't skip the manager — the record
  is just wrong." Option **(c)**: the claim waits, HR fixes the record. Linh added a limit: if the record is
  still not fixed after **2 business days**, the claim goes to the **department head**. Marco wants HR Ops to get
  a **daily email** listing employees whose claims are waiting for a manager record. When the next HR file
  gives the employee a manager, the claim goes to that manager.
- **Q-024 (escalation):** (a) mostly. The escalation target **may decide** the claim (approve / return /
  reject); the original approver can still decide too, first decision wins. Escalation target = the approver's
  manager in the HR file; for the **Finance Controller level** it is the **CFO, Pierre Laurent**. Only one
  escalation, no second one. Marco: reminders as a **daily digest** per approver, not one email per claim.
- **Q-031 (fallback approvers):** Linh: vacant department head → Finance Controller approves that level.
  Finance Controller's own claim above €500 → CFO. "I must not finance-check a claim I approved myself — another
  Finance team member does it." Who reassigns claims when an approver leaves or is long absent: **only the
  Finance Controller**, not the whole Finance team — "reassigning approvals is a control, I want one owner."
  Reassignment needs a reason.
- **Q-015 (one person at two levels):** (a) approve once, counts for both levels.
- **Q-017 (delegate who is also a later approver):** Linh: **No** — not like Q-015. "A delegate is standing in
  for someone else. If the delegate is also the department head on that claim, they can't approve it as
  delegate; the manager (or the escalation) must do level 1, and the delegate then approves as department head."
- **Q-021 (manager keeps rights during delegation):** (a) yes, either may decide.

## 2. Leavers & payroll timing

- **Q-019 (leaver submits after leave date):** Marco: "Their login is switched off on the leave date — they
  physically can't." So in practice (b). Linh: leavers must be told to submit before leaving; for anything that
  comes in afterwards (by email to Finance), **a Finance team member enters the claim on the leaver's behalf**,
  same 90-day rule, expenses dated on or before the leave date only. It goes through the normal approval chain.
  Marco: the claim goes to the manager the person had on their last day.
- **Q-026 (payroll run):** (a). Batches exported by the **20th at 18:00** go into that month's payroll; later
  batches into next month's. Leavers' claims after the final payroll is closed: Finance adds them to the final
  pay manually (outside the system), and marks them paid as normal.
- **Q-016 (how a claim becomes Paid):** (a) Finance marks the export batch paid after the payroll run.

## 3. Policy details

- **Q-022 (meal cap scope):** (a) — cap €40/day **only for domestic trips**. Linh added a **new constraint**:
  "For trips abroad there is no daily cap, but every meal abroad needs a receipt, even under €25 — that goes in
  policy v3.3 too." Domestic = expense incurred in France (Linh, to be written into v3.3).
- **Q-023 (bulk approve):** Linh: yes, but tighter than proposed — **only claims with a claimed total ≤ €250**,
  at most **50 at a time**, only at the **line-manager level**, and **never for claims with a Leaver flag**
  ("those I want looked at").
- **Q-029 (90 days on resubmission):** (a) date of the **original first submission** counts.
- **Q-030 (threshold basis):** (a) the **claimed total** (what the employee entered), not the reimbursable total.
  "Someone claiming €1,200 of meals should still reach the department head, even if we cap it."
- **Q-014 (alcohol):** (a) employee enters only the non-alcohol amount and ticks the declaration.
- **Q-027 (VAT number & Finance check):** (a). Optional supplier VAT number field per line. The Finance check
  verifies: (1) itemised receipt present where required (card slips refused), (2) amount on receipt matches the
  line, (3) VAT number recorded when it is on the receipt, (4) no alcohol/fines/personal items visible on the
  receipt, (5) cost centre valid.
- **Q-028 (Finance check SLA):** (a) 2 business days; reminder to the Finance Controller when exceeded.
- **Q-032 (after 7 years):** Not (a) as written. Linh: "Seven years counts from the **end of the financial year**
  in which the claim was paid, not from submission — that's what the tax authority means. Then delete receipts
  and personal data automatically; keep anonymised totals per cost centre for statistics."
  Financial year = calendar year (Linh).

## 4. Goal metric G-01

- **Q-025:** Linh chose **(b)**, not the recommendation: "I asked about reimbursement. Employees care when the
  money arrives, not when a file leaves." Measure **submission → Paid**. New target **≤ 15 days on average**
  (baseline 19), because monthly payroll alone makes ≤ 10 impossible. Keep "submission → export ≤ 5 business
  days on average" as a leading indicator Finance watches monthly.

## 5. Other points raised

- Linh: **no admin screen** for thresholds, approvers or SLAs in the MVP — they change with the policy, a few
  times a year at most; IT changes the configuration through a normal change request.
- Marco confirms the business calendar: Monday–Friday, French public holidays, Paris time.
- Marco confirms HR enters the leave date in the HR system as soon as resignation is accepted.

## Decisions & owners (read back at the end)
All of the above read back and agreed by Linh Tran and Marco Rossi (simulated). Linh to publish policy v3.3
(dept-head level, domestic meal cap, receipts for meals abroad) before go-live.

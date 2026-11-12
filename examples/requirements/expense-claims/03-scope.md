# 03 · Scope — Expense claims & approvals

**Status:** Confirmed by PO (D-015, 2026-10-23); re-confirmed after round 2 (D-043, 2026-10-26, simulated)

## Problem statement
Employees and managers at the company handle about 900 expense claims a month through Excel and email.
Claims get lost and managers can't see what is waiting for them. Finance re-keys every claim into the ERP
(about 3 days a month). The result is an average of 19 days from submission to reimbursement, 6% of claims
returned for missing information, and 74 complaints a quarter. (SRC-01, SRC-04)

## Goals
| ID | Goal | Metric | Baseline | Target | By when | Measured how |
|----|------|--------|----------|--------|---------|--------------|
| G-01 | Reimburse faster | Average calendar days from first submission to *Paid* | 19 days (SRC-01) | ≤ 15 days (D-027) | 3 months after go-live (end Jun 2027) | Claim timestamps: `first_submitted_at` → `paid_date`, monthly average in the Finance list (AC-013.5) |
| G-01 · leading indicator | Approval and Finance check don't hold claims | Average business days from first submission to *Exported* | Unknown | ≤ 5 business days (D-027) | End Jun 2027 | `first_submitted_at` → `exported_at`, monthly average (AC-013.5) |
| G-02 | Fewer incomplete claims | % of claims returned to the claimant | 6% (SRC-01) | ≤ 2% (D-005) | End Jun 2027 | Returned ÷ submitted per month |
| G-03 | No re-keying | Finance hours spent keying claims into ERP | ~3 days/month (SRC-01) | 0 (D-005) | Go-live | Finance time log; on-behalf entry for leavers (IS-10) is not re-keying into the ERP |
| G-04 | No missed leaver claims | Approved claims of leavers not paid in final salary | Unknown, occurs (SRC-04) | 0 | Go-live | Monthly leaver filter in the Finance list (AC-013.4) |

> G-01 changed on 2026-10-26: the PO chose to measure to payment, not to export (D-027, SRC-06). The previous
> "≤ 10 days to export" metric is replaced by the leading indicator above.

## Non-goals
- Corporate card reconciliation, travel booking, per-diem allowances, multi-currency (D-006).

## Users & stakeholders
| Role | Job to be done | Primary / secondary |
|------|----------------|---------------------|
| Employee (incl. field technician) | Get money back with little effort | Primary |
| Line manager / delegate | Approve team claims within the 5-business-day SLA (D-008) | Primary |
| Department head | Approve claims with a claimed total > €1,000; fallback when no manager after 2 business days (D-022) | Secondary |
| Finance Controller | Approve claims > €500; control policy compliance; reassign approvals (D-033) | Primary |
| CFO (Pierre Laurent) | Escalation target at Finance Controller level; approves the Finance Controller's own claims (D-026, D-033) | Secondary |
| Finance team | Check claims, enter leavers' claims on their behalf, send claims to the ERP, mark paid | Primary |
| HR Operations | Keep manager records correct; make sure leavers are settled | Secondary |
| IT (ERP owner) | Run the ERP and HR file transfers | Secondary |

## In scope
| ID | Capability | Goal | Profile | Slice |
|----|-----------|------|---------|-------|
| IS-01 | Create and submit a claim with lines and receipt images (incl. phone camera) | G-01, G-02 | web-app | MVP |
| IS-02 | Policy checks at submission (deadline, receipt, caps, mileage) | G-02 | web-app, workflow-approval | MVP |
| IS-03 | Approval routing: manager → dept head (> €1,000) → Finance Controller (> €500), on claimed total (D-032) | G-01 | workflow-approval | MVP |
| IS-04 | Approver inbox, approve / return / reject, bulk approve with limits (D-025), delegation | G-01 | workflow-approval, web-app | MVP |
| IS-05 | SLA reminders (daily digest) and escalation, incl. Finance check SLA | G-01 | workflow-approval | MVP |
| IS-06 | Finance check, daily CSV export to ERP, rejection handling, reconciliation, mark paid | G-01, G-03 | integration, web-app | MVP |
| IS-07 | Leaver flagging and Finance warning | G-04 | workflow-approval | MVP |
| IS-08 | Claim status tracking and withdrawal for the claimant | G-01 | web-app | MVP |
| IS-09 | Finance list with filter and CSV export | G-01, G-03, G-04 | web-app | MVP |
| IS-10 | Finance enters a claim on behalf of a leaver (D-021) | G-04 | workflow-approval, web-app | MVP |
| IS-11 | Fallback approvers (no manager, vacant dept head, FC's own claim) and reassignment by the Finance Controller (D-022, D-033) | G-01 | workflow-approval | MVP |
| IS-12 | Nightly HR org-file import (employees, managers, dept heads, cost centres, leave dates) | G-01, G-04 | integration | MVP |
| IS-13 | Retention: delete receipts and personal data after the retention period, keep anonymised totals (D-034) | — (compliance, SRC-02) | workflow-approval | MVP |

## Out of scope
| Item | Reason |
|------|--------|
| Native mobile app | Responsive web for MVP (D-004) |
| Foreign currency | EUR only (D-006) |
| Receipt OCR / auto-fill | Not requested; later phase |
| ERP API integration | Not licensed (SRC-01) |
| BI dashboards | Finance list is enough (D-010) |
| Admin screen for thresholds, approvers, SLAs | Changed by IT change request (D-042) |
| Adding leavers' claims to the final pay after payroll is closed | Done manually by Finance outside the system (D-028) |
| Migrating claims in progress in Excel/email at go-live | They finish in the old process (A-080, Q-056 — to confirm) |
| Corporate cards, per-diem, travel booking | Not raised; separate processes |

## Assumptions, constraints, dependencies
- **Assumptions (open):** High: A-043. Medium (scope-relevant): A-011 (WCAG 2.2 AA), A-017 (cost centre editable), A-024 (NFR values), A-038, A-039, A-040, A-041, A-080. Full register: `02-questions.md`.
- **Constraints:** daily CSV only, ERP imports at 22:00, file must land by 21:30 (SRC-07); go-live end of Q1 2027;
  policy v3.2 + v3.3 changes (dept-head level, domestic meal cap, receipts for meals abroad — SRC-05, SRC-06);
  retention 7 years from end of the financial year of payment (D-034).
- **Dependencies:**
| Dependency | Owner | Needed by | Status |
|-----------|-------|-----------|--------|
| ERP journal CSV spec, rejection and summary files | Aisha Khan | Spec sign-off | Received (D-036, SRC-07) |
| HR nightly employee/org file | Aisha Khan / Marco Rossi | Build start | Confirmed (D-039) |
| SFTP keys in company vault | Aisha Khan | Integration test (date: Q-054) | Confirmed approach (D-038); keys to be issued for test |
| Policy v3.3 (dept-head rule, domestic cap, receipts abroad) | Linh Tran | Go-live, end of Q1 2027 (publication date: Q-054) | Committed (SRC-05, SRC-06) |
| Valid cost-centre list | Aisha Khan / Linh Tran | Spec sign-off | Open (Q-049, A-072) |

## Risks
| ID | Risk | L | I | Mitigation | Owner |
|----|------|---|---|-----------|-------|
| R-01 | HR file has wrong or missing managers → claims wait | M | M | Wait + HR Ops daily email + dept head after 2 business days (D-022); HR file confirmed (D-039) | Marco |
| R-02 | ERP rejects CSV rows → claims not paid | M | H | Rejection file (US-010), reconciliation (US-018), Finance alerts | Aisha |
| R-03 | Month-end peak overloads approvers → SLA breaches | H | M | Bulk approve for claims ≤ €250 (D-025); daily digest reminders; escalation | Linh |
| ~~R-04~~ | Build vs buy undecided | — | — | Closed: build decided (D-035) | Aisha |
| R-05 | Monthly payroll limits G-01: claims exported after the 20th wait up to a month | H | M | Leading indicator (D-027); export by 20th 18:00 (D-028) | Linh |
| R-06 | Policy v3.3 not published before go-live → system enforces rules that policy doesn't state | L | H | Linh owns v3.3; go-live checklist item | Linh |

## PO confirmation (simulated: all ✔ on 2026-10-26 → D-043)
- [x] We are solving lost, slow and re-keyed expense claims for ~400 employees and their approvers.
- [x] Success = ≤ 15 days to payment and ≤ 2% returns by end of June 2027, and zero re-keying from go-live.
- [x] MVP includes IS-01, IS-02, IS-03, IS-04, IS-05, IS-06, IS-07, IS-08, IS-09, IS-10, IS-11, IS-12, IS-13.
- [x] We are NOT doing: native app, foreign currency, OCR, ERP API, dashboards, admin screen.
- [x] Key risks accepted: R-03 month-end peak, R-05 payroll timing.

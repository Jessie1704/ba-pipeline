# 01 · Intake — Expense claims & approvals

> PILOT — all sources and people are fictional.

## Source register
| ID | Type | Date | Author / attendees | Reliability | File | Summary |
|----|------|------|--------------------|-------------|------|---------|
| SRC-01 | Meeting | 2026-10-20 | Linh Tran, Marco Rossi, Aisha Khan, BA | Primary | `sources/SRC-01-kickoff-meeting.md` | Current process, pains, volumes, thresholds, ERP CSV import, target date |
| SRC-02 | Email | 2026-10-21 | Linh Tran (Finance Controller) | Primary | `sources/SRC-02-email-finance-controller.md` | Categories, mileage rate, meal cap, VAT, payroll cut-off, 7-year retention |
| SRC-03 | Policy doc | 2024-01-01 | Finance (Expense Policy v3.2) | Primary (approved policy) | `sources/SRC-03-expense-policy-v3.2.md` | 90-day limit, receipts > €25, approval rules, delegation, exclusions, leavers |
| SRC-04 | Email | 2026-10-21 | Marco Rossi (HR Ops) | Primary | `sources/SRC-04-email-hr-ops.md` | Complaints, field-staff volumes, manager visibility, leavers |
| SRC-05 | Email | 2026-10-22 | Linh Tran | Primary | `sources/SRC-05-answers-finance.md` | Answers to elicitation round 1 (added by `/ba-elicit`) |
| SRC-06 | Workshop | 2026-10-26 | Linh Tran, Marco Rossi, BA (simulated) | Primary | `sources/SRC-06-workshop-round2.md` | Round-2 answers: fallbacks, escalation, leavers, payroll month, meal cap scope, bulk approve, G-01 metric, retention |
| SRC-07 | Email | 2026-10-26 | Aisha Khan (simulated) | Primary | `sources/SRC-07-email-aisha.md` | Build decided; SSO and HR file confirmed; ERP file spec, rejection & summary files, retries, GL table |

## Facts & statements
| # | Statement | Source |
|---|-----------|--------|
| F1 | Today: Excel template + emailed receipts → manager email approval → Finance re-keys into ERP → paid via payroll | SRC-01 |
| F2 | ~400 employees; ~900 claims/month; peak in last week of month | SRC-01 |
| F3 | Finance spends ~3 days/month re-keying | SRC-01 |
| F4 | Average submission-to-reimbursement time is 19 days | SRC-01 |
| F5 | ~6% of claims are returned for missing information | SRC-01 |
| F6 | ERP accepts one CSV import of journal lines per day; API exists but is not licensed | SRC-01 |
| F7 | Receipt required for expenses above €25; card slips are not itemised receipts | SRC-01, SRC-03 §4.2 |
| F8 | Categories: travel, accommodation, meals, mileage, other | SRC-02 |
| F9 | Mileage €0.30/km with from/to and km | SRC-02 |
| F10 | Domestic meals capped at €40/day; excess not reimbursed | SRC-02 |
| F11 | VAT reclaim needs the supplier VAT number on the receipt | SRC-02 |
| F12 | Paid in monthly payroll; cut-off on the 20th | SRC-02 |
| F13 | Receipts and approvals kept 7 years | SRC-02 |
| F14 | Line manager approves every claim; Finance Controller additionally above €500 | SRC-03 §5.1–5.2, SRC-01 |
| F15 | No self-approval; delegate may approve when manager absent > 3 working days | SRC-03 §5.3–5.4 |
| F16 | Personal expenses, fines and alcohol are never reimbursed | SRC-03 §6.1 |
| F17 | Leavers' approved claims paid in final salary; today some are discovered too late | SRC-03 §6.2, SRC-04 |
| F18 | 74 complaints last quarter about late/missing reimbursements | SRC-04 |
| F19 | 120 field staff submit 10–15 small claims/month each | SRC-04 |
| F20 | Managers don't know which claims are waiting for them | SRC-04 |
| F21 | Target go-live end of Q1 2027 | SRC-01 |

## Actors
| Actor | Type | Mentioned in |
|-------|------|--------------|
| Employee (claimant) | Person role | SRC-01, SRC-03 |
| Field technician (claimant with high volume, mobile) | Person role | SRC-01, SRC-04 |
| Line manager | Person role | SRC-01, SRC-03 |
| Delegate approver | Person role | SRC-03 §5.4 |
| Department head | Person role | SRC-01 (Marco) — not in policy |
| Finance Controller | Person role | SRC-01, SRC-03 |
| Finance team (processing) | Person role | SRC-01 |
| HR Operations | Person role | SRC-04 |
| ERP | System | SRC-01 |
| Payroll | System/process | SRC-01, SRC-02 |

## Goals & desired outcomes (as stated)
- Stop lost claims; manager sees what's waiting (SRC-01, SRC-04)
- Remove Finance re-keying (3 days/month) (SRC-01)
- Faster reimbursement than 19 days (SRC-01) — no target given
- Fewer returned claims than 6% (SRC-01) — no target given
- No unpaid claims at leaver's final pay (SRC-04)

## Pain points today
- Lost emails; no status visibility (SRC-01, SRC-04) · manual re-keying (SRC-01) · slow (19 days) · returns (6%) · 74 complaints/quarter (SRC-04)

## Constraints
- ERP integration via daily CSV only (SRC-01) · go-live end Q1 2027 (SRC-01) · 7-year retention (SRC-02) · policy v3.2 (SRC-03)

## Implicit / inferred needs
- Validation at submission (receipt present, within time limit, caps) to cut the 6% returns (inferred from SRC-01 F5)
- Approver inbox with reminders (inferred from SRC-04 "don't know which claims are waiting")
- Leaver check before final pay (inferred from SRC-04)
- Bulk/quick entry for high-volume field staff (inferred from SRC-04 F19)
- Mobile-friendly submission for field staff (inferred from SRC-01) — channel to be decided

## Contradictions
| # | Statement A | Statement B | Who can resolve | Raised as |
|---|-------------|-------------|-----------------|-----------|
| C1 | Submit within **60 days** (Marco, SRC-01) | Within **90 days** (Policy §4.1, SRC-03) | Linh Tran (policy owner) | Q-001 |
| C2 | Department head approves **> €1,000** (Marco, SRC-01) | Policy has no department-head level (SRC-03 §5) | Linh Tran | Q-002 |

## Approach (summary — full plan in `_status.md`)
| Profile / modifier | Role | Evidence | Covers |
|--------------------|------|----------|--------|
| `workflow-approval` | Primary | Submit → approve → finance check; thresholds; delegation; managers can't see queue (SRC-01, SRC-03, SRC-04) | Claim lifecycle, approvals, SLAs |
| `web-app` | Secondary | "Web portal", laptop users (SRC-01) | Employee, approver, finance screens |
| `integration` | Secondary | Daily CSV import into ERP (SRC-01) | ERP export |
| New feature (work type) | Modifier | Replaces Excel/email, no existing system | — |

Not chosen: `mobile-app` (field staff "would love" phone — responsive web may suffice; Q-003);
`data` (no reporting requirement stated yet; Q-009); `cots-saas` (no buy option raised; Q-010).

**Confidence:** Medium — channel for field staff unclear (Q-003). · **Status:** Confirmed (D-001)

## Terms for glossary
| Term | Meaning as used | Source |
|------|-----------------|--------|
| Claim | One submission by an employee containing one or more expense lines | SRC-01 (inferred structure) |
| Expense line | One expense: date, category, amount, receipt | SRC-02 |
| Itemised receipt | Receipt listing items and amounts; card slip is not one | SRC-03 §4.2 |
| Delegate | Person nominated by a manager to approve while absent > 3 working days | SRC-03 §5.4 |

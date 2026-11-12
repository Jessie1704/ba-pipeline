# Expense claims & approvals — Status

> PILOT — fictional company, people and data; BA and stakeholder decisions are simulated.

| Field | Value |
|-------|-------|
| Slug | `expense-claims` |
| Why (one line) | Replace Excel/email expense claims with a portal: faster, fewer returns, no re-keying |
| Type of work | new feature |
| Approach | `workflow-approval` + `web-app`, `integration` (see *Approach*) |
| Product Owner | Linh Tran (Finance Controller) |
| BA | pilot-BA |
| Builders | AI coding agent — stack: not decided |
| Target date / release | End of Q1 2027 |
| Current stage | 8 Review (failed, round 2b) → back to 2 Elicit round 3 |
| Status | Draft v1.0-rc — review failed; handoff blocked (D-045) |
| Version | v1.0-rc |
| Last updated | 2026-10-26 |

## Next action
> Run the round-3 workshop (Linh + Aisha; agenda in `02-questions.md`): **Q-039 first (Blocking, A-043 High)**, then
> policy §5.3 "named on" (review 2b D3, to raise as Q-057) and the 2b Majors needing input. Meanwhile apply the 2b
> auto-fixes (D2 labels, D5, D8, D9, D17, D20, Minors). Then `/ba-review` round 3.

## Preferences
| Setting | Value |
|---------|-------|
| Stage prompts | on-deviation |
| Elicitation round | 2 |

## Gates
Result: Passed · Failed · Skipped (O-NN) · Deferred · –
| Stage | Gate | Result | Date | Notes |
|-------|------|--------|------|-------|
| 1 Intake | All sources registered & summarised; approach confirmed | Passed | 2026-10-26 | 7 sources (SRC-06, SRC-07 added) |
| 2 Elicit | No blocking questions open | **Failed (reopened)** | 2026-10-26 | Passed after round 2, reopened when review 2a made Q-039 Blocking |
| 3 Scope | PO confirmed scope | Passed | 2026-10-26 | D-043 (re-confirmed: IS-10, IS-11, IS-12, IS-13; G-01 re-based) |
| 4 Model | Flows, states, permissions complete | Passed | 2026-10-26 | + batch state machine, invalid transitions, integration context/sequences |
| 5 Stories | INVEST + ≥3 AC each, scope covered, grounding self-check | Passed | 2026-10-26 | 20 stories, 98 AC (108 after review fix round); 7 new A- registered |
| 6 UI/UX | UI stories → screens with all states | Passed (full) | 2026-10-26 | O-01 removed (D-040); 10 screens |
| 7 Spec | No undefined refs; NFRs measurable; grounding self-check | Passed | 2026-10-26 | 28 BR, 36 active MSG (34 at the gate; MSG-46, MSG-47 added in the review fix round), 10 NFR |
| 8 Review | Score ≥ 85, zero Critical | **Failed** (72, 3 Critical) | 2026-10-26 | Rounds: 64 → 75 (2a) → 72 (2b) after one fix round |
| 9 Handoff | Packs generated; traceability 100 % | **Blocked** (D-045) | 2026-10-26 | Not generated: review Fail + Q-039 Blocking + A-043 High; no override |

## Open items snapshot
| Type | Open | Blocking / High-risk |
|------|------|----------------------|
| Questions `Q-` | 24 open (Q-034, Q-035, Q-036, Q-037, Q-038, Q-039, Q-040, Q-041, Q-042, Q-043, Q-044, Q-045, Q-046, Q-047, Q-048, Q-049, Q-050, Q-051, Q-052, Q-053, Q-054, Q-055, Q-056, Q-057) | **2 Blocking: Q-039, Q-057** |
| Assumptions `A-` | 61 open of 83 (register: 02-questions): 1 High, 24 Medium, 36 Low | **High: A-043** |
| Risks `R-` | 5 open (R-01, R-02, R-03, R-05, R-06); R-04 closed | R-02, R-06 High impact |

## Approach
**Status:** Confirmed (D-001) · **Confidence:** High (build confirmed D-035; integration spec received D-036)

| Profile | Role | Covers (scope) | Evidence |
|---------|------|----------------|----------|
| `workflow-approval` | Primary | IS-02, IS-03, IS-04, IS-05, IS-07, IS-10, IS-11, IS-13 | SRC-01, SRC-03, SRC-04, SRC-06 |
| `web-app` | Secondary | IS-01, IS-04, IS-06, IS-08, IS-09, IS-10 | SRC-01 |
| `integration` | Secondary | IS-06, IS-12 | SRC-01, SRC-07 |
| New feature | Modifier | all | SRC-01 |

### Stage plan
| Stage | Plan | From profile / override | What's different for this feature | Output documents | Command |
|-------|------|-------------------------|-----------------------------------|------------------|---------|
| 4 Model | Run | workflow-approval, integration | State machines central; SLA events; context + sequence diagrams | `04-model.md` | `/ba-model` |
| 5 Stories | Run | workflow-approval, integration | Stories per transition; supervisor; HR import; reconciliation | `05-stories.md` | `/ba-stories` |
| 6 UI/UX | Run | web-app (O-01 removed, D-040) | Claimant, approver and Finance screens | `06-ux.md` | `/ba-ux` |
| 7 Spec | Run | all three | + approval matrix, SLA, delegation, queues; interface spec, mapping, errors, reconciliation; web specifics | `07-spec.md` | `/ba-spec` |
| 8 Review | Run | — | | `08-review.md` | `/ba-review` |
| 9 Handoff | Run | all three | + supervisor guide, ops runbook, design brief | `handoff/…` | `/ba-handoff` |

### Overrides
| ID | Target | Change | Reason | Decision |
|----|--------|--------|--------|----------|
| ~~O-01~~ | Stage: UX | Run → Lite | (withdrawn, D-040) — review rated Lite Critical | D-016, D-040 |

### Deliverables
- [ ] `handoff/po-approval.md`
- [ ] `handoff/agent-brief.md`
- [ ] `handoff/qa-pack.md`
- [ ] `handoff/team-summary.md`
- [ ] `handoff/traceability.md`
- [ ] `handoff/design-brief.md` (web-app)
- [ ] `handoff/supervisor-guide.md` (workflow-approval)
- [ ] `handoff/ops-runbook.md` (integration)

## Stakeholders
| ID | Name | Role | Interest | Influence | Can answer about |
|----|------|------|----------|-----------|------------------|
| STK-01 | Linh Tran | Finance Controller (PO) | Control, speed, no re-keying | H | Policy, thresholds, finance process |
| STK-02 | Marco Rossi | HR Operations Lead | Complaints, leavers, field staff | M | HR data, leavers, org chart |
| STK-03 | Aisha Khan | IT — ERP owner | Integration, build/buy | H | ERP CSV, SSO, HR file |
| STK-04 | Pierre Laurent | CFO | Escalation target at FC level; approves FC's own claims | M | Not consulted directly (named by Linh, SRC-06) |

## Decision log
| ID | Decision | Decided by | Date | Source | Affects | Revisit at |
|----|----------|------------|------|--------|---------|-----------|
| D-001 | Approach: workflow-approval + web-app + integration | pilot-BA | 2026-10-23 | 01-intake | all | — |
| D-002 | Claim deadline 90 days | Linh Tran | 2026-10-22 | SRC-05 | BR-001 | — |
| D-003 | Dept head approves > €1,000 on claim total; order manager → dept head → FC | Linh Tran | 2026-10-22 | SRC-05 | BR-007 | — |
| D-004 | Responsive web, phone camera; no native app | Linh Tran, Marco Rossi | 2026-10-22 | SRC-05 | IS-01 | — |
| D-005 | Targets ≤ 10 days, ≤ 2% returns, 0 re-keying (reimbursement target re-based by D-027) | Linh Tran | 2026-10-22 | SRC-05 | G-01, G-02, G-03 | — |
| D-006 | EUR only | Linh Tran | 2026-10-22 | SRC-05 | scope | — |
| D-007 | Returned claims restart at manager | Linh Tran | 2026-10-22 | SRC-05 | BR-014 | — |
| D-008 | SLA 5 business days; reminder day 3; escalate day 5 | Linh Tran, Marco Rossi | 2026-10-22 | SRC-05 | BR-015 | — |
| D-009 | Leaver flag + Finance warning 10 days before | Marco Rossi | 2026-10-22 | SRC-05 | BR-016 | — |
| D-010 | Reporting = finance list + CSV | Linh Tran | 2026-10-22 | SRC-05 | IS-09 | — |
| D-011 | Delegation self-service; org chart from HR system | Marco Rossi | 2026-10-22 | SRC-05 | BR-008 | — |
| D-012 | Meal cap per day across all claims | Linh Tran | 2026-10-22 | SRC-05 | BR-003 | — |
| D-013 | Export daily at 18:00 | Aisha Khan (via Linh) | 2026-10-22 | SRC-05 | BR-011 | — |
| D-014 | Proceed past Elicit gate with A-006 | pilot-BA | 2026-10-23 | — | INT-01 | 7 Spec — **resolved**: Q-013 answered (D-036) |
| D-015 | PO confirmed scope | Linh Tran (simulated) | 2026-10-23 | 03-scope | scope | — |
| D-016 | UX Run Lite (superseded by D-040) | pilot-BA (simulated) | 2026-10-23 | — | 06-ux | — |
| D-017 | Alcohol: employee enters non-alcohol amount and ticks declaration | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-005 | — |
| D-018 | Same person at consecutive levels approves once | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-007 | — |
| D-019 | Finance marks export batch paid after payroll | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-020 | — |
| D-020 | Delegate who is a later approver can't act as delegate on that claim | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-008 | — |
| D-021 | Leavers: login disabled at leave date; Finance enters claims on behalf | Linh Tran, Marco Rossi (simulated) | 2026-10-26 | SRC-06 | BR-017, US-014 | — |
| D-022 | No manager: wait for HR, HR Ops daily list, dept head after 2 business days | Linh Tran, Marco Rossi (simulated) | 2026-10-26 | SRC-06 | BR-018, US-015 | — |
| D-023 | Manager keeps approval rights during delegation | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-008 | — |
| D-024 | Meal cap domestic only; meals abroad always need a receipt | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-002, BR-003 | — |
| D-025 | Bulk approve ≤ 50 claims, each ≤ €250, manager level, no leavers | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-027 | — |
| D-026 | Escalation target may decide; CFO at FC level; one escalation; daily digest | Linh Tran, Marco Rossi (simulated) | 2026-10-26 | SRC-06 | BR-015 | — |
| D-027 | G-01 measured to Paid, ≤ 15 days; ≤ 5 business days to export as leading indicator | Linh Tran (simulated) | 2026-10-26 | SRC-06 | G-01 | — |
| D-028 | Batches exported by 20th 18:00 → that month's payroll; leavers added manually | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-020 | — |
| D-029 | Optional VAT number field; 5-point Finance checklist | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-010 | — |
| D-030 | Finance check SLA 2 business days; reminder to FC | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-021 | — |
| D-031 | 90 days counted from first submission | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-001 | — |
| D-032 | Thresholds on claimed total | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-007 | — |
| D-033 | Fallbacks (vacant dept head → FC; FC's own → CFO); FC no self-check; reassignment by FC only | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-009, BR-019, BR-025 | — |
| D-034 | Retention 7 years from end of financial year of payment; delete receipts + personal data; anonymised totals kept | Linh Tran (simulated) | 2026-10-26 | SRC-06 | BR-028, NFR-06 | — |
| D-035 | Build in-house (ARB-2026-14) | Aisha Khan (simulated) | 2026-10-26 | SRC-07 | approach | — |
| D-036 | ERP journal CSV spec and rejection file | Aisha Khan (simulated) | 2026-10-26 | SRC-07 | INT-01, INT-02 | — |
| D-037 | GL account per category | Aisha Khan (simulated, table from Finance) | 2026-10-26 | SRC-07 | INT-01 | — |
| D-038 | Integration values: SFTP keys, 2,000 lines/day, retries, REJ/SUM by 06:00, HR file 01:30/02:00, tickets | Aisha Khan (simulated) | 2026-10-26 | SRC-07 | 07-spec §6 | — |
| D-039 | Entra ID SSO and nightly HR file confirmed | Aisha Khan (simulated) | 2026-10-26 | SRC-07 | NFR-04, INT-03 | — |
| D-040 | Remove O-01; run UX in full incl. Finance screens | pilot-BA (simulated) | 2026-10-26 | 08-review #7 | 06-ux | — |
| D-041 | Business calendar Mon–Fri, French holidays, Europe/Paris | Marco Rossi (simulated) | 2026-10-26 | SRC-06 | BR-015 | — |
| D-042 | No admin screen in MVP; configuration by IT change request | Linh Tran (simulated) | 2026-10-26 | SRC-06 | scope | — |
| D-043 | PO re-confirmed scope after round 2 | Linh Tran (simulated) | 2026-10-26 | 03-scope | scope | — |
| D-044 | PO accepted wireframes with one change (claimant sees "Waiting for a manager record") | Linh Tran (simulated) | 2026-10-26 | 06-ux | SCR-01 | — |
| D-045 | Review still Fail after one fix round: handoff not generated, no override; return to Elicit round 3 | pilot-BA (simulated) | 2026-10-26 | 08-review | 9 Handoff | 8 Review round 3 |

## Assumptions
| ID | Assumption | Risk | Status |
|----|-----------|------|--------|
| All | Single register in `02-questions.md` → *Assumptions* (83 IDs) | 1 High open (A-043) | 61 open |

## Risks
See `03-scope.md` (R-01, R-02, R-03, R-05, R-06; R-04 closed).

## Review score history
| Date | Score | Verdict | Critical | Major | Minor |
|------|-------|---------|----------|-------|-------|
| 2026-10-23 | 64 | Fail | 8 | 19 | 9 |
| 2026-10-26 (2a) | 75 | Fail | 5 | 15 | 15 |
| 2026-10-26 (2b, after fix round) | 72 | Fail | 3 | 18 | 12 |

## Change log
| CR | Request | Requester | Date | Decision | Version |
|----|---------|-----------|------|----------|---------|

## History
- 2026-10-23 — Feature created; stages 1–7 run in pilot. `_status.md` written late (pilot finding).
- 2026-10-23 — Review 64/100 Fail. Auto-fixable defects fixed; 13 invented behaviours labelled as
  assumptions; 15 round-2 questions raised. Returning to Elicit; handoff deferred.
- 2026-10-26 — Round 2 (simulated): SRC-06 workshop, SRC-07 email; 28 decisions recorded (see log); 6 high-risk
  assumptions closed. Back through Scope, Model, Stories, UX (full, O-01 removed), Spec.
- 2026-10-26 — Review 2a: 75 Fail (5 Critical). One fix round: 30 assumptions and 15 questions registered,
  10 AC added; Q-039 made Blocking, A-043 High. Review 2b: 72 Fail (3 Critical). Stopped per D-045: handoff
  blocked, no override; back to Elicit round 3.
- 2026-10-26 — Migrated to current status template: added *Elicitation round* (2 rounds completed: SRC-05;
  SRC-06 and SRC-07). Register: A-028 status made canonical (Rejected; SFTP part confirmed, D-038).

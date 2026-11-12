# 08 · Review — Expense claims & approvals

> **Current verdict (round 2b, 2026-10-26): 72 / 100 — Fail (3 Critical).** Handoff blocked; see the end of this file.

**Round 2a** · **Date:** 2026-10-26 · **Reviewer:** `requirements-reviewer` agent (project agent type, loaded
natively this session) + `ba-check.ps1`
**Score:** 75 / 100 · **Verdict:** **Fail** (Conditional band, but 5 Critical)
Round 1 (2026-10-23): 64 / 100, Fail, 8 Critical — see score history in `_status.md`.

## Scores
| # | Category | Score | Max | Justification |
|---|----------|-------|-----|---------------|
| 1 | Groundedness | 10 | 15 | Round-2 decisions traced well, but some interface values (INT-03 transport/format, JOURNAL_DATE, EMPLOYEE_REF, BATCH_ID), money-affecting rules (meal-cap statuses, trip default, declaration scope) and view rights had no source; "All values from SRC-07" wrong |
| 2 | Clarity & unambiguity | 12 | 15 | Precise rules; unclear "delivered by 18:00 on the 20th", "cost centre valid", day-2 vs day-3 Finance reminder |
| 3 | Completeness | 10 | 15 | No return/reject notification; returned on-behalf claims, mileage receipts, cost-centre source, short-notice leavers, HR row errors, go-live in-flight claims missing |
| 4 | Testability | 13 | 15 | 98 AC, arithmetic verified; AC-005.3 not set-up-able; AC-015.4 no dates; US-011 no failure path |
| 5 | Consistency | 7 | 10 | Notify column vs spec §7; view rights vs NFR-05; wireframe total; status words |
| 6 | Traceability | 8 | 10 | G-02 not measurable; AwaitingApprover → Withdrawn untested |
| 7 | Value & scope alignment | 8 | 10 | G-01 now right; dependency dates and in-flight claims missing |
| 8 | Build-readiness | 3 | 5 | No "do not guess" list; 32 open A-; stack undecided |
| 9 | Readability | 4 | 5 | Some ID ordering; example-data table incomplete |

## Mechanical checks (`ba-check.ps1`, before → after fix round)
| Check | Before | After | Details |
|-------|--------|-------|---------|
| status | PASS | PASS | |
| ids | PASS | PASS | 442 IDs, all defined |
| ranges | WARN | WARN | only this file's round-1 history (now removed) |
| register | PASS | PASS | 139 A-/Q- in 02-questions |
| ground | PASS | PASS | 34 BR rows cite SRC-/D-/A- (routing table counted — see PILOT-FINDINGS round 2) |
| gherkin | PASS | PASS | 20 stories, 98 → 108 AC |
| tables | PASS | PASS | |
| ambiguity | WARN | WARN | 2 hits in 01-intake quoting sources (kept: BA's voice, rule 9) |
| open | PASS (false) | WARN | Q-039 Blocking, A-043 High. The first run missed them because the cells were bold/annotated (ba-check bug) |

## Round-1 Critical/Major status (reviewer)
Resolved: 1, 2, 3, 4, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 27. Partly open after 2a:
5 (interface values), 11 (AC-005.3 data), 23 (view rights), 25 (dependency dates), 26 (G-04 shows status only).

## Defects round 2a and fix-round status
| # | Sev | Location | Problem (short) | Action taken | Status |
|---|-----|----------|-----------------|--------------|--------|
| 1 | Critical | 07 §6, 04 §5 | Interface values not in SRC-07 | Labelled A-054, A-055; Q-042 to Aisha; "All values" sentence replaced by per-value sources | Labelled → needs answer |
| 2 | Critical | BR-002 vs AC-002.6 | Mileage receipt contradiction | BR-002 excludes mileage (A-056); AC-002.6 explicit; Q-043 | Labelled → needs answer |
| 3 | Critical | BR-003, BR-005, trip_location | Money rules unsourced | A-057, A-058 (no default), A-059 (+ accommodation); Q-044 | Labelled → needs answer |
| 4 | Critical | 04 §6 vs NFR-05 | View rights unsourced, contradictory | Both now say "claims they are/were an approver on" (A-060); Q-045 | Labelled → needs answer |
| 5 | Critical | BR-016, BR-020, BR-024, BR-026, §7, §11, NFR-08, on-behalf FC | Unsourced behaviour | A-061, A-062, A-063, A-064, A-065, A-066, A-067, A-068 cited in rules | Fixed (labels) |
| 6 | Major | 04 Notify vs 07 §7 | Return/reject notifications missing | MSG-46, MSG-47 + §7 rows (A-069); Notify column aligned; Q-046 | Labelled → needs answer |
| 7 | Major | BR-020 | Payroll month with retries | Rule by export run date (A-070); AC-009.4 retry row; Q-047 | Labelled → needs answer |
| 8 | Major | BR-017 | Returned on-behalf claims | A-071; AC-014.6; permission row; Q-048 | Labelled → needs answer |
| 9 | Major | BR-010 item 5 | "Cost centre valid" undefined | A-072; dependency row; Q-049 | Labelled → needs answer |
| 10 | Major | BR-016 | Short-notice leavers | A-073; AC-011.5, AC-011.6; Q-050 | Labelled → needs answer |
| 11 | Major | BR-026 | HR row errors, missing employees | A-074; AC-018.5; Q-051 | Labelled → needs answer |
| 12 | Major | BR-009 | Approver at any level may check | A-075; AC-007.7; Q-052 | Labelled → needs answer |
| 13 | Major | BR-024, A-043 | Rejected-line counting; double posting | A-043 raised to **High**, Q-039 **Blocking**; BR-024 defines counting | **Open — blocks Handoff** |
| 14 | Major | G-02 | Not measurable | times_returned field, G-02 summary, AC-013.6 | Fixed |
| 15 | Major | ExportFailed fix | Undefined | A-076 in SCR-07; Q-053 | Labelled → needs answer |
| 16 | Major | 03 dependencies | No dates | Q-054 to owners; not invented | Open — owners |
| 17 | Major | Routing edge cases | Undefined | A-077, A-078, A-079 in BR-019/BR-008; AC-017.5; Q-055 | Labelled → needs answer |
| 18 | Major | AC-005.3 | Not set-up-able | Example data: M201 reports to M200 | Fixed |
| 19 | Major | Go-live in-flight claims | Not addressed | Out of scope via A-080; Q-056 | Labelled → needs answer |
| 20 | Major | 32 open A- | Need confirmation before Handoff | Round-3 pack with owners; workshop proposed | Open — stakeholders |
| 21 | Minor | SCR-02 | Wrong total | €43.60 | Fixed |
| 22 | Minor | SCR-01 words | ExportFailed/Exported words | Fixed | Fixed |
| 23 | Minor | 07 §11 | Safari Android | A-065 | Fixed |
| 24 | Minor | 05 example data | Missing ids | Added | Fixed |
| 25 | Minor | IDs | AC-006.2b, ordering | AC-006.7 (old ID struck); Q/A order fixed | Fixed |
| 26 | Minor | Coverage | AwaitingApprover → Withdrawn | AC-012.5 | Fixed |
| 27 | Minor | AC-015.4 | No dates | Concrete dates | Fixed |
| 28 | Minor | BR-021 wording | Day 2 vs 3 | "exceeded" = from business day 3 everywhere (D-030); AC-007.5 outline | Fixed |
| 29 | Minor | BR-004 | Rounding unsourced | Clause removed | Fixed |
| 30 | Minor | Data dictionary | Missing fields | current_approver, last_updated_at, employee_name, run_date, delivered_at | Fixed |
| 31 | Minor | SCR-05 | Delegation edges | A-081 | Fixed (label) |
| 32 | Minor | BR-001 | Lines added while Returned | "not in the future" (A-082) | Fixed (label) |
| 33 | Minor | US-011, US-017, US-020 | No failure AC | AC-011.6, AC-017.4, AC-020.4 (A-083) | Fixed |
| 34 | Minor | SCR-09 | Month labels | Labelled | Fixed |
| 35 | Minor | INT-01 mapping | Default column | Added | Fixed |

## Persona verdicts (reviewer, round 2a)
- **AI coding agent:** ~85% buildable; would stop on mileage receipts, interface values, meal-cap statuses,
  rejected-line counting, payroll month after retry, notifications.
- **Product Owner:** value and G-01 right; must decide view rights, mileage evidence, returned leaver claims,
  segregation, in-flight claims.
- **Designer:** all 10 screens usable; total, status word, month labels, fix flow, return/reject email needed.
- **Team member:** QA examples verifiable; ops blocked on HR-file failures and reconciliation hold.

## Strengths
1. Round-2 answers carried into every artifact with decision IDs; rejected assumptions kept visible.
2. Time and money AC are exact (holiday calendar, 90-day, thresholds on claimed total, CSV rows).
3. All three profiles' spec sections present and filled.

## Re-review (round 2b) — 2026-10-26
Substantive content changed (30 new A-, 15 new Q-, 10 new AC, rule rewrites), so a re-review was run with the
`requirements-reviewer` agent type (fresh context; no shell, so `ba-check` was run separately — results above).

**Score:** 72 / 100 · **Verdict:** **Fail** (3 Critical, 18 Major, 12 Minor)

| # | Category | 2a | 2b | Why it moved |
|---|----------|----|----|--------------|
| 1 | Groundedness | 10 | 10 | Labels fixed the 2a gaps, but the fix round itself added 4 unsourced behaviours (SLA clock restart on reassignment/manager change, MSG-46 recipient for on-behalf claims, "(policy 5.4)" quoted for the 60-day limit) and 5 older ones surfaced; policy §5.3 "named on" half not implemented |
| 2 | Clarity | 12 | 12 | Day-2/day-3 Finance alert still in §5 SLA table; two payroll-month definitions; cost centre per claim vs per line |
| 3 | Completeness | 10 | 9 | Leavers' own returned claims, CFO's own claim, ExportFailed dead end, > 2,000 lines/day, ticket and email interfaces, configuration list, security/backup NFRs |
| 4 | Testability | 13 | 12 | 8 rules without failure/boundary AC; AC-011.6 contradicts BR-026 |
| 5 | Consistency | 7 | 6 | `_status.md` misreported open blocking/high-risk items; SLA table, permission cell, glossary |
| 6 | Traceability | 8 | 8 | G-04 still not measurable; MSG-46/47 never asserted |
| 7 | Value & scope | 8 | 8 | G-04 method; dependency dates |
| 8 | Build-readiness | 3 | 3 | "Do not guess" list now exists, but 1 Blocking Q, ~62 open A-, stack undecided |
| 9 | Readability | 4 | 4 | Status file misleads; dense spec tables |

### Critical (2b)
| # | Location | Problem | Needs |
|---|----------|---------|-------|
| D1 | Q-039, A-043, BR-023, BR-024, AC-010.2 | Blocking question + High-risk assumption open: re-sending a partly rejected claim may double-post | Aisha's answer to Q-039 |
| D2 | BR-025, AC-016.1, AC-018.4, BR-017, BR-020, AC-014.6, MSG-09, `export_error`, NFR-06, BR-016 | 9 behaviours without source (4 of them introduced by the fix round) | Labelling (auto) + Linh/Marco/Aisha answers |
| D3 | BR-009, §10 row §5.3 | Policy §5.3 "or a claim they are named on" silently dropped — no attendee concept | Linh: meaning of "named on" |

### Major (2b) — summary
D4 status misreporting (fixed in `_status.md` after this review — see below) · D5 §5 SLA table still day 2 (2a #28
claimed fixed but wasn't) · D6 leavers' own claims after leave date · D7 CFO's own claim · D8 8 rules without
boundary/failure AC, MSG-46/47 not asserted · D9 AC-011.6 vs BR-026 · D10 ExportFailed dead end · D11 claim in two
batches · D12 > 2,000 lines/day · D13 service-desk ticket and email interfaces unspecified (no INT- ID yet) · D14 no configuration list (incl.
holiday calendar owner) · D15 encryption, backup, notification reliability NFRs · D16 cost centre per claim vs line ·
D17 segregation rules split across files · D18 dependency dates · D19 G-04 not measurable · D20 A-055 should be High ·
D21 ~62 open assumptions vs CLAUDE.md rule 1.

### Minor (2b)
D22–D33: glossary payroll month, missing citations (A-083, A-055, A-023), AC order, §7 leaver row, wireframe
example data, "Ready for payment" wording, delegation messages, deep-link rules and session-timeout state, stale
round-3 pack, G-02 "measured how", escalated-row bulk rule, working vs business days.

### Fix-round claims checked by the reviewer
Verified 27 of 35; **#28 claimed fixed but not**; partly fixed #7, #8, #12, #13, #15; still open as stated #16, #19, #20.

## Decision: stop, no override (D-045)
The task allowed one fix round. The verdict is still **Fail** after it, so handoff is **not** generated and no
override is recorded. What blocks handoff:
1. **Q-039 / A-043** (Blocking / High) — ERP partial-rejection behaviour (Aisha).
2. **Policy §5.3 "named on"** (D3) — raised as Q-057 to Linh.
3. **Unsourced behaviours D2** — label as A- (auto) and confirm.
4. **Definition of Ready:** ~62 open assumptions (rule 1), dependency dates (Q-054), G-04 measurement (D19).
5. Majors D6, D7, D10, D12, D13, D14, D15, D16 need business/IT input; D5, D8, D9, D17, D20 and the Minors are auto-fixable.

**Next:** run the round-3 workshop (Linh + Aisha, agenda in `02-questions.md`) incl. Q-039 and "named on";
apply the auto-fixes; re-run `/ba-review`.

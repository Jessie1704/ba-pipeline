# 02 · Questions & Gap Analysis — Expense claims & approvals

## Gap lens coverage
| # | Lens | Status | Note |
|---|------|--------|------|
| 1 | Why & value | Covered | Targets D-005; G-01 re-based to payment (D-027) |
| 2 | Who | Covered | Dept head (D-003); CFO as escalation/fallback (D-026, D-033); Finance team vs Controller (D-033) |
| 3 | Scope edges | Covered | Responsive web (D-004); EUR only (D-006); build (D-035) |
| 4 | Process & triggers | Covered | Submit → approve → finance → ERP → payroll |
| 5 | Alternatives & exceptions | Covered | Return (D-007); leavers (D-009, D-021); no manager (D-022) |
| 6 | States & time | Covered | SLA (D-008, D-030); calendar (D-041); payroll month (D-028) |
| 7 | Rules & calculations | Covered | Thresholds on claimed total (D-032); domestic meal cap (D-024) |
| 8 | Data | Covered | VAT number field (D-029); GL table (D-037); retention (D-034) |
| 9 | Permissions & security | Covered | SSO (D-039); delegation (D-020, D-023); reassignment by FC only (D-033) |
| 10 | Integrations & dependencies | Covered | ERP files, rejection, reconciliation, HR file (D-036, D-038) |
| 11 | Experience & communication | Covered | Daily digest reminders (D-026) |
| 12 | Operate & measure | Covered | G-01 leading indicator (D-027); service desk tickets (D-038); support A-004 |

## Question log
| ID | Lens / profile | Question | Why it matters | Options (★ = recommended) | Priority | Ask | Status | Answer / D- |
|----|----------------|----------|----------------|---------------------------|----------|-----|--------|-------------|
| Q-001 | 6 | Claim deadline: 60 days (SRC-01) or 90 days (policy §4.1)? | Wrong limit rejects valid claims or breaches policy | (a) 90 per policy ★ (b) 60 and update policy | Blocking | Linh | Answered | 90 days — D-002 |
| Q-002 | 7 · workflow-approval | Department-head approval above €1,000 — new rule? Threshold on claim total or per line? Order of approvers? | Defines the routing engine | (a) Manager → Dept head (>€1,000) → Finance Controller (>€500), on claim total ★ (b) policy as-is | Blocking | Linh | Answered | (a), on claim total — D-003 |
| Q-003 | 3 · web-app | Field staff on phones: responsive web, or native app? | Native app = different profile, cost, timeline | (a) Responsive web incl. phone camera upload ★ (b) native app | Blocking | Linh, Marco | Answered | (a) for MVP — D-004 |
| Q-004 | 1 | Targets: reimbursement time, return rate, re-keying? | Goals need metrics | (a) ≤ 10 days avg, ≤ 2% returns, 0 re-keying ★ | Important | Linh | Answered | (a) — D-005; reimbursement target re-based by D-027 |
| Q-005 | 3 | Foreign-currency expenses in MVP? | Exchange-rate source & rules | (a) EUR only; employee enters EUR amount charged ★ (b) multi-currency | Important | Linh | Answered | (a) — D-006 |
| Q-006 | 5 · workflow-approval | When an approver returns a claim for changes, does it restart at the first approver? | Avoids double approvals or skipped checks | (a) Restart from line manager ★ (b) resume at returning approver | Blocking | Linh | Answered | (a) — D-007 |
| Q-007 | 6 · workflow-approval | Approval SLA, reminders, escalation? | Managers forget; 19-day delay | (a) 5 business days; reminder day 3; escalate to approver's manager day 5 ★ | Blocking | Linh, Marco | Answered | (a) — D-008 |
| Q-008 | 5 | Leavers: how do we know someone is leaving, and what happens to pending claims? | Final-pay misses (SRC-04) | (a) HR sets leave date; claims auto-flagged and prioritised; Finance warned 10 days before ★ | Important | Marco | Answered | (a) — D-009; HR sets date (A-002 confirmed, SRC-06) |
| Q-009 | 12 | Reporting needs in MVP? | May add `data` profile | (a) Finance status list + CSV export only ★ (b) BI dashboard | Important | Linh | Answered | (a) — D-010 |
| Q-010 | 3 | Buy a SaaS expense tool instead? | Changes the whole approach | (a) Build (IT decision already taken) (b) evaluate SaaS | Important | Aisha | Answered | (a) build, ARB-2026-14 — D-035 (SRC-07) |
| Q-011 | 9 · workflow-approval | Who maintains delegates, the org chart (manager, dept head)? | Routing depends on it | (a) Delegates: manager self-service; org chart: imported from HR system ★ | Blocking | Marco, Aisha | Answered | (a) — D-011; nightly HR file confirmed — D-039 |
| Q-012 | 7 | Meal cap €40/day: per calendar day across all claims, or per line? | Calculation rule | (a) Per employee per calendar day across all claims ★ | Important | Linh | Answered | (a) — D-012 |
| Q-013 | 10 · integration | CSV: who defines the format, when does it run, what about rejected rows? | Integration failure handling | (a) ERP team provides spec; export 18:00 daily; rejections returned as file and reprocessed next day ★ | Blocking | Aisha | Answered | Spec + rejection file — D-036 (SRC-07) |
| Q-014 | 7 | Alcohol on a meal receipt: whole line rejected or employee deducts it? | Policy §6.1 enforcement | (a) Employee enters only the non-alcohol amount and ticks a declaration ★ | Nice to know | Linh | Answered | (a) — D-017 |
| Q-015 | 5 · workflow-approval (from model) | If the same person holds two approval levels for a claim (e.g. manager is also dept head), approve once or twice? | Duplicate approvals annoy; skipped levels breach policy | (a) Approve once; the step counts for both levels ★ | Important | Linh | Answered | (a) — D-018 |
| Q-016 | 6 (from model) | How does a claim become *Paid* — payroll file or Finance marks it? | Employee status accuracy | (a) Finance marks the export batch paid after payroll run ★ (b) payroll file | Important | Linh | Answered | (a) — D-019 |
| Q-017 | 9 · workflow-approval (from model) | A delegate who is also a later approver in the chain? | Self-reinforcing approval | (a) Treated like Q-015: one approval covers both ★ | Important | Linh | Answered | **Not (a)**: delegate can't act as delegate on that claim — D-020 |
| Q-018 | 10 · integration (from spec) | Which GL account does each expense category post to? | INT-01 can't be built without it | Table from Finance | Blocking | Linh | Answered | GL table via Aisha — D-037 (SRC-07) |
| Q-019 | 5 (review #1) | Can a leaver submit expenses incurred before their leave date after that date? | Draft blocked it without a source | (a) Yes, within 90 days; routed with leaver flag ★ (b) Blocked; Finance enters manually | Blocking | Linh, Marco | Answered | **(b)**: login disabled at leave date; Finance enters on behalf — D-021 |
| Q-020 | 9 (review #2) | Who approves when an employee has no manager on record? | Nobody can approve today | (a) Department head ★ (b) Finance Controller (c) HR fixes the record first, claim waits | Blocking | Linh, Marco | Answered | **(c)** + fallback to dept head after 2 business days — D-022 |
| Q-021 | 9 (review #3) | During a delegation, does the manager keep approval rights? | Dual approvers vs single | (a) Yes, either may decide ★ (b) Only the delegate | Important | Linh | Answered | (a) — D-023 |
| Q-022 | 7 (review #4) | Meal cap €40/day: domestic trips only (SRC-02) or all meals? | Over/under-reimbursement | (a) Add "domestic trip" flag; cap only domestic ★ (b) Cap all meals; update policy | Blocking | Linh | Answered | (a) + **new constraint**: meals abroad always need a receipt — D-024 |
| Q-023 | 9 (review #6) | May approvers bulk-approve without opening each claim? | Control risk | (a) Yes, up to 50, only claims ≤ €500 ★ (b) No | Important | Linh | Answered | **Tighter than (a)**: ≤ €250, manager level, no leavers — D-025 |
| Q-024 | 6 · workflow-approval (review #10, #29) | After escalation: may the approver's manager decide? Escalation target for dept-head and FC levels? Second escalation? Reminder per claim or daily digest? | Escalation behaviour undefined | (a) Escalation target may decide; FC-level escalates to CFO; no second escalation; daily digest ★ | Blocking | Linh, Marco | Answered | (a) — D-026 |
| Q-025 | 1 (review #13) | G-01: measure to reimbursement (your 19-day baseline) or to ERP export? With payroll monthly, ≤ 10 days to payment may be impossible. | Goal must measure what you asked | (a) Measure to export, target ≤ 10 days ★ (b) Measure to payment, new target | Blocking | Linh | Answered | **(b)**: to Paid, ≤ 15 days; export ≤ 5 business days as leading indicator — D-027 |
| Q-026 | 6 (review #14) | Which payroll run pays which export batch (cut-off 20th)? How are leavers' claims put into the final salary? | Payment timing promise | (a) Batches exported by 20th 18:00 → that month's payroll; leavers: Finance adds manually ★ | Important | Linh | Answered | (a) — D-028 |
| Q-027 | 8 (review #15) | Is the supplier VAT number captured per line, and what exactly does the Finance check verify? | VAT reclaim; returns | (a) Optional VAT number field; Finance checklist: itemised receipt, VAT number for reclaim, exclusions ★ | Important | Linh | Answered | (a) with 5-point checklist — D-029 |
| Q-028 | 6 (review #16) | SLA for the Finance check? | G-01 depends on it | (a) 2 business days, reminder to Finance Controller ★ | Important | Linh | Answered | (a) — D-030 |
| Q-029 | 6 (review #17) | 90-day limit on resubmission: original submission date or resubmission date? | Approver delay could time-bar a claim | (a) Original first submission ★ (b) Resubmission | Important | Linh | Answered | (a) — D-031 |
| Q-030 | 7 (review #18) | Approval thresholds on claimed total or reimbursable total (after caps)? | Routing of capped claims | (a) Claimed total ★ (b) Reimbursable | Important | Linh | Answered | (a) — D-032 (A-037 rejected) |
| Q-031 | 9 (review #19, #23, #24) | Fallback approvers: vacant dept head; Finance Controller's own claim > €500; may the FC also finance-check a claim they approved? Who reassigns claims when an approver leaves? | Segregation of duties, no dead ends | (a) Vacant dept head → FC; FC's own claim → CFO; FC can't check own approvals; Finance team reassigns ★ | Blocking | Linh | Answered | (a) except **reassignment by the Finance Controller only** — D-033 |
| Q-032 | 12 (review #8) | After 7 years: delete claims and receipts, or keep? | Retention & privacy | (a) Delete automatically ★ (b) Keep | Important | Linh | Answered | **Changed**: 7 years from end of financial year of payment; delete receipts + personal data; keep anonymised totals — D-034 |
| Q-033 | 10 · integration (review #5, #20) | Confirm: SFTP transport, volume, rejection file (exists? when?), HR file time, retry policy, reconciliation action on mismatch, encryption & credentials | All integration values are assumptions | See A-028, A-029, A-030, A-031 | Blocking | Aisha | Answered | D-038 (SRC-07); several values differ from the assumptions |
| Q-034 | 9 (from SRC-06) | May the CFO nominate a delegate, and who decides when the CFO is absent? | CFO is a new escalation/fallback level with no fallback | (a) CFO uses delegation like any approver ★ (b) no fallback | Important | Linh | Open | A-038 |
| Q-035 | 9 (from SRC-06) | On-behalf claims for leavers: may the Finance team member who entered the claim also finance-check it? | Segregation of duties for D-021 | (a) No — another Finance member checks it ★ | Important | Linh | Open | A-039 |
| Q-036 | 10 (from SRC-07) | Reconciliation mismatch: hold the whole batch from *Paid*, or only the claims in question? | Payroll timing for all claimants in the batch | (a) Hold the whole batch until the Finance Controller releases it ★ (b) only unmatched claims | Important | Aisha, Linh | Open | A-040 |
| Q-037 | 9 (from model) | When the HR file changes an employee's manager, do claims already waiting at the manager level move to the new manager? | Claims stuck with an ex-manager | (a) Yes, undecided manager-level steps move; decided steps stay ★ | Important | Marco | Open | A-041 |
| Q-038 | 12 (from SRC-06) | Anonymised totals kept after deletion: at what level of detail? | Retention job needs a target structure | (a) Per cost centre × category × month ★ | Nice to know | Linh | Open | A-042 |
| Q-039 | 10 (from SRC-07) | If one line of a claim is rejected, does the ERP reject all lines of that claim, or post the others? Does the REJ file list every line of the claim or only the failing one? | Double posting when the fixed claim is re-sent; reconciliation counting (BR-024) | (a) ERP rejects all lines of the claim and lists them all ★ (b) posts the others → re-send only fixed lines | Blocking | Aisha | Open | A-043 (High; raised to Blocking by review 2 #13) |
| Q-040 | 8 (from stories) | Retention for claims never paid (Rejected, Withdrawn): 7 years from the end of which financial year? | Retention job needs an end date for every claim | (a) Year of the final status date ★ | Important | Linh | Open | A-048 |
| Q-041 | 9 (from stories) | Escalation target who is also a later approver on the same claim (e.g. H300 is M200's delegate *and* manager): who gets the escalation? | D-020 forbids the same person covering both roles | (a) One manager higher ★ (b) Finance Controller | Important | Linh | Open | A-052 |
| Q-042 | 10 (review 2 #1) | (1) HR file transport and format (delimiter, encoding, header, date format)? (2) JOURNAL_DATE = export date, expense date or paid date? (3) EMPLOYEE_REF = HR employee_id or payroll number? (4) BATCH_ID format rule? (5) Does the ERP need a balancing (credit) line per batch? | Interface contract values not in SRC-07 | (a) as A-054, A-055 ★ | Important | Aisha | Open | A-054, A-055 |
| Q-043 | 7 (review 2 #2) | Do mileage lines need a receipt above €25? | BR-002 vs AC-002.6 contradiction | (a) No — from/to/km is the evidence ★ (b) Receipt rule applies | Important | Linh | Open | A-056 |
| Q-044 | 7 (review 2 #3) | Meal cap: which claim statuses count (does a Returned claim count?) and which line loses the excess? Trip location: default or required? Which categories need the exclusions declaration (accommodation — minibar)? | Changes the amount paid | (a) as A-057, A-058, A-059 ★ | Important | Linh | Open | A-057, A-058, A-059 |
| Q-045 | 9 (review 2 #4) | May a department head (or manager) see every claim in their department/team, or only claims they approve? | Privacy (NFR-05) | (a) Only claims they are or were an approver on ★ (b) whole department | Important | Linh | Open | A-060 |
| Q-046 | 11 (review 2 #6) | Which events email the claimant / approver: return, reject, next level, withdraw? | A field technician never learns a claim was returned (G-02) | (a) Claimant emailed on return and reject; others see it in inbox/digest ★ | Important | Linh | Open | A-069 |
| Q-047 | 6 (review 2 #7) | Payroll month: set by the export run date (run of the 20th incl. retries) or delivery time? | 18:15 retry would move a batch a month | (a) Run date ★ | Important | Linh | Open | A-070 |
| Q-048 | 5 (review 2 #8) | Who edits, resubmits or withdraws a returned on-behalf claim, and who gets its MSG-23? | Leaver can't sign in | (a) Any Finance member except its checker; MSG-23 to the entering member ★ | Important | Linh | Open | A-071 |
| Q-049 | 8 (review 2 #9) | Where does the list of valid cost centres come from? | "Cost centre valid" check undefined | (a) Values in the latest HR file ★ (b) ERP extract (c) config list | Important | Aisha, Linh | Open | A-072 |
| Q-050 | 5 (review 2 #10) | Leave date entered less than 10 days ahead: when is Finance warned? Once or daily? | G-04 failure mode | (a) Once, at the first import after entry ★ | Important | Marco | Open | A-073 |
| Q-051 | 10 (review 2 #11) | HR file row errors (unknown manager_id, bad date) and employees missing from the file: what happens? | Routing and pending approvals | (a) as A-074 ★ | Important | Aisha, Marco | Open | A-074 |
| Q-052 | 9 (review 2 #12) | May anyone finance-check a claim they approved at any level? | Segregation of duties | (a) No ★ | Important | Linh | Open | A-075 |
| Q-053 | 6 (review 2 #15) | Fixing an ExportFailed claim: which fields may Finance change, checklist again, who may fix? | ExportFailed fix flow | (a) Cost centre only; checklist re-ticked; not the claimant ★ | Important | Linh | Open | A-076 |
| Q-054 | 12 (review 2 #16) | Dates for each dependency (SFTP test keys, policy v3.3 publication) | DoR: dependencies need dates | Dates from owners | Important | Aisha, Linh | Open | — |
| Q-055 | 9 (review 2 #17) | Routing edge cases: FC's own claim > €1,000; escalation when the approver has no manager; claims in a delegate's inbox when the delegation ends | Dead ends | (a) as A-077, A-078, A-079 ★ | Important | Linh | Open | A-077, A-078, A-079 |
| Q-056 | 3 (review 2 #19) | Claims in progress in Excel/email at go-live: finish in the old process or migrate? | Initial load (integration profile) | (a) Finish in the old process ★ (b) migrate | Important | Linh | Open | A-080 |
| Q-057 | 9 (review 2b D3) | Policy §5.3 "or a claim they are named on": who is "named on" a claim? | Policy clause not implemented; manager could approve a lunch they attended | (a) Attendees listed on meals/other lines → add attendees field, exclude them from approving ★ (b) only the claimant; v3.3 rewords | Blocking | Linh | Open | — |
## Assumptions
| ID | Assumption | Risk | Status |
|----|-----------|------|--------|
| A-001 | Login via company Microsoft Entra ID single sign-on | Medium | **Confirmed** — Aisha, SRC-07 (D-039) |
| A-002 | HR enters leave date in the HR system, which flows in the nightly org file | Medium | **Confirmed** — Marco, SRC-06 |
| A-003 | Build in-house (no SaaS evaluation) | High | **Confirmed** — D-035 (SRC-07) |
| A-004 | Support via existing IT service desk | Low | Open |
| A-005 | HR system can provide a nightly file of employees, managers, department heads, leave dates | High | **Confirmed** — D-039 (SRC-07) |
| A-006 | ERP CSV format follows the ERP team's standard journal import (to be supplied) | Medium | **Confirmed** — spec received, D-036 |
| A-007 | When one person holds consecutive approval levels for a claim, one approval covers those levels | Medium | **Confirmed for Q-015 (D-018); rejected for delegates (D-020)** |
| A-008 | Finance marks an export batch *Paid* after the payroll run | Low | **Confirmed** — D-019 |
| A-009 | Minimum screen width 360 px | Low | Open |
| A-010 | Company intranet UI kit is the design system | Low | Open |
| A-011 | Accessibility target WCAG 2.2 AA | Medium | Open |
| A-012 | English only for MVP | Low | Open |
| A-013 | Alcohol/fines/personal handled by a declaration tick, amount entered excludes them | Medium | **Confirmed** — D-017 |
| A-014 | Max 50 lines per claim | Low | Open |
| A-015 | Receipts JPEG/PNG/PDF, ≤ 10 MB, ≤ 5 per line | Low | Open |
| A-016 | Business calendar Mon–Fri excluding French public holidays | Medium | **Confirmed** — Marco, D-041 |
| A-017 | Cost centre defaults from HR file, editable by Finance | Medium | Open (HR file has cost_centre — SRC-07) |
| A-018 | Delegation at most 60 days | Low | Open |
| A-019 | Draft autosave every 30 s | Low | Open |
| A-020 | Bulk approve max 50 claims | Low | **Confirmed** — D-025 |
| A-021 | HR file failure alerts IT by email | Low | **Rejected** — service desk ticket instead (D-038) |
| A-022 | Session timeout 30 min idle | Low | Open |
| A-023 | Concurrent decisions: first wins | Low | **Confirmed** for escalation (D-026); kept for manager/delegate |
| A-024 | NFR-01, NFR-02, NFR-03 performance/availability values | Medium | Open |
| A-025 | Leavers can't submit after leave date (**invented in draft**) | High | **Rejected as a system rule** — login disabled by SSO; Finance enters on behalf (D-021) |
| A-026 | No-manager claims go to Finance team queue (**invented in draft**) | High | **Rejected** — D-022 |
| A-027 | Meal cap applies to all meals, not only domestic | High | **Rejected** — D-024 |
| A-028 | INT-01 via SFTP, ≤ 1,500 lines/day | Medium | Rejected — volume is 2,000 lines/day; SFTP part confirmed (D-038) |
| A-029 | Rejection file arrives 07:00 next day | High | **Rejected** — 06:00 (D-038) |
| A-030 | HR file at 02:00, cut-off 02:30 | Medium | **Rejected** — lands 01:30, cut-off 02:00 (D-038) |
| A-031 | Export retries 18:30 and 19:00 | Low | **Rejected** — 18:15, 18:30, 18:45 (D-038) |
| A-032 | Bulk approve allowed | Medium | **Confirmed with limits** — D-025 |
| A-033 | Value ranges in data dictionary (km 1–2,000, amounts, description 3–200) | Low | Open |
| A-034 | Return/reject reason 5–500 characters | Low | Open |
| A-035 | Withdraw allowed until first decision | Low | Open |
| A-036 | Time zone Europe/Paris | Low | **Confirmed** — Marco, D-041 |
| A-037 | Thresholds on reimbursable total | Medium | **Rejected** — claimed total (D-032) |
| A-038 | The CFO may nominate a delegate under the same rules as other approvers (BR-008) | Medium | Open — Q-034 |
| A-039 | The Finance team member who entered an on-behalf claim may not finance-check it | Medium | Open — Q-035 |
| A-040 | A reconciliation mismatch holds the whole batch from *Paid* until the Finance Controller releases it | Medium | Open — Q-036 |
| A-041 | When the HR file changes a claimant's manager, undecided manager-level steps move to the new manager | Medium | Open — Q-037 |
| A-042 | Anonymised totals kept per cost centre × category × month | Low | Open — Q-038 |
| A-043 | The ERP rejects all lines of a claim when any line fails and lists every one of them in `REJ_`, so a fixed claim is re-sent in full and "rejected lines" in BR-024 = rows in `REJ_` | High | Open — Q-039 (raised from Medium by review 2 #13: double posting if wrong) |
| A-044 | Line description is cut to the first 50 characters in the ERP file (ERP limit, SRC-07) | Low | Open |
| A-045 | Overdue Finance-check reminder goes to the Finance Controller in the daily 08:00 digest (MSG-40) | Low | Open |
| A-046 | When a claim's SLA clock restarts at a new level, a new reminder/escalation cycle starts for that level | Low | Open |
| A-047 | The retention job runs nightly and deletes claims whose retention end date has passed | Low | Open |
| A-048 | Claims never paid (Rejected, Withdrawn) use the end of the financial year of their final status date + 7 years | Medium | Open — Q-040 |
| A-049 | Supplier VAT number format: 2-letter country prefix + 2–13 letters/digits (EU VAT format) | Low | Open |
| A-050 | Daily digests and SLA jobs (MSG-20, MSG-31, MSG-40, escalation, no-manager fallback) run at 08:00 Europe/Paris on business days | Low | Open |
| A-051 | Business days are counted in whole days from the business day the claim reached the step (non-business arrival day → next business day = day 0) | Low | Open |
| A-052 | If the escalation target is also a later approver of the claim, the escalation goes one manager higher | Medium | Open — Q-041 |
| A-053 | Lists (inbox, Finance queues, Finance list) show 25 rows per page | Low | Open |
| A-054 | HR file: SFTP like the ERP files; UTF-8, `;`-separated, header row, dates YYYY-MM-DD | Medium | Open — Q-042 |
| A-055 | INT-01: JOURNAL_DATE = export run date; EMPLOYEE_REF = HR employee_id; BATCH_ID = `EXP-YYYYMMDD`; no balancing line | Medium | Open — Q-042 |
| A-056 | Mileage lines need no receipt; from/to/km is the evidence | Medium | Open — Q-043 |
| A-057 | Meal cap counts lines on claims in Submitted, AwaitingApprover, InApproval, Returned, FinanceCheck, ReadyForExport, Exported, ExportFailed, Paid; the excess is taken from the line submitted last | Medium | Open — Q-044 |
| A-058 | Trip location is required on meals lines, with no default | Low | Open — Q-044 |
| A-059 | The exclusions declaration is required on meals, accommodation and other lines | Medium | Open — Q-044 |
| A-060 | Approvers see only claims they are or were an approver on (incl. as delegate, escalation target or reassignee); Finance team and Finance Controller see all | Medium | Open — Q-045 |
| A-061 | The Leaver flag is removed when the leave date disappears from the HR file | Low | Open |
| A-062 | Paid date must be on or after the batch delivery date | Low | Open |
| A-063 | A missing `SUM_` file at 06:00 holds the batch | Medium | Open — Q-036 |
| A-064 | HR import is a full refresh; file fails validation if a required column is missing or an employee_id appears twice | Low | Open — Q-051 |
| A-065 | Supported browsers: latest 2 versions of Chrome and Edge (desktop), Safari iOS, Chrome Android | Low | Open |
| A-066 | No opt-out for any notification in the MVP | Low | Open |
| A-067 | Each run log holds start, end, row count and result | Low | Open |
| A-068 | The Finance Controller counts as a Finance team member for on-behalf entry (SRC-06 says "a Finance team member") | Low | Open |
| A-069 | Claimant gets an email on return (MSG-46) and reject (MSG-47); next-level approvers see the claim in inbox and digest only; withdraw sends no email | Medium | Open — Q-046 |
| A-070 | Payroll month is set by the export run date: runs on or before the 20th (incl. their retries) → that month | Low | Open — Q-047 |
| A-071 | A returned on-behalf claim may be edited, resubmitted or withdrawn by any Finance team member except the one who checked it; MSG-23 for on-behalf claims goes to the entering Finance member | Medium | Open — Q-048 |
| A-072 | Valid cost centres = the set of cost_centre values in the latest HR file | Medium | Open — Q-049 |
| A-073 | The leaver warning is sent once: on leave date − 10 days, or at the first HR import after entry if the leave date is entered later | Low | Open — Q-050 |
| A-074 | HR rows failing row checks (unknown manager_id, invalid date) are skipped and listed in the ticket; employees missing from the file become inactive; undecided steps waiting for an inactive approver go to that approver's escalation target at the next 08:00 run | Medium | Open — Q-051 |
| A-075 | Nobody may finance-check a claim they approved at any level | Medium | Open — Q-052 |
| A-076 | Fixing an ExportFailed claim: Finance may change only the cost centre; all five checklist items are ticked again; the fixer may not be the claimant | Low | Open — Q-053 |
| A-077 | The Finance Controller's own claim > €1,000: the CFO also covers the department-head level | Medium | Open — Q-055 |
| A-078 | Escalation when the approver has no manager in the HR file goes to the Finance Controller (CFO if the approver is the Finance Controller) | Medium | Open — Q-055 |
| A-079 | When a delegation ends, undecided claims leave the delegate's inbox and stay with the approver | Low | Open — Q-055 |
| A-080 | Claims in progress in Excel/email at go-live finish in the old process; no migration | Medium | Open — Q-056 |
| A-081 | Delegation: "End now" is allowed whatever the remaining length; no overlapping delegations per approver; nobody can name themself | Low | Open |
| A-082 | Lines added while a claim is Returned must not be dated in the future; the 90-day check still uses the first submission date | Low | Open |
| A-083 | The retention job deletes each claim in one transaction; a failed run leaves unfinished claims untouched, opens an IT ticket (MSG-43) and they are processed the next night | Low | Open |

> This table is the **single assumption register** for the feature (review #22).
> High-risk assumptions open: **A-043** (raised by review round 2, Q-039 Blocking) — blocks Handoff (DoR).

## Ready-to-send packs

### Round 3 — after review round 2 (2026-10-26)
**Aisha Khan — Blocking first:** Q-039 (rejected lines — blocks handoff), Q-042 (interface values), Q-036, Q-049, Q-051, Q-054.
**Linh Tran:** Q-043, Q-044, Q-045, Q-046, Q-047, Q-048, Q-052, Q-053, Q-055, Q-056, Q-054 (policy v3.3 date); confirm
Medium assumptions A-011 (WCAG 2.2 AA) and A-024 (NFR-01, NFR-02, NFR-03 values).
**Marco Rossi:** Q-050, Q-051.
> 21 questions for 3 people → recommend a 45-min workshop with Linh + Aisha (agenda: integration contract
> Q-039, Q-042, Q-036, Q-049 — 20 min; money rules Q-043, Q-044, Q-047 — 10 min; privacy & segregation Q-045,
> Q-052, Q-048 — 10 min; go-live Q-056 — 5 min).

### Round 3 — written, non-blocking (2026-10-26, before review round 2)
**Linh Tran:** Q-034 (CFO delegate), Q-035 (on-behalf segregation), Q-038 (anonymised totals), Q-040 (retention
of unpaid claims), Q-041 (escalation target who is also a later approver).
**Marco Rossi:** Q-037 (manager change while a claim waits).
**Aisha Khan:** Q-036 (reconciliation hold — with Linh), Q-039 (partial rejection of a claim).

### Earlier rounds
Round 1 (SRC-05) and round 2 (SRC-06 workshop, SRC-07 email) are answered; see the question log.

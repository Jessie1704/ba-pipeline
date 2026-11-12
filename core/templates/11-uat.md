# 11 · Test & UAT — <Feature name>

Results are written only from a real run, with evidence and the name of who recorded it. The RTM (`rtm.md`,
built by `ba rtm`) holds the per-AC results; this file holds the UAT rounds, the discrepancies and the decision.

## Round <n> · <YYYY-MM-DD>
| Item | Detail |
|------|--------|
| Release / build tested | <exact build or version> |
| Environment | UAT · staging · … |
| Business owner | |
| Participants (who actually ran scenarios) | |
| Test data | <approved data sets; no real personal data outside approved environments> |

### Scenarios
Status: `Not run` · `Pass` · `Fail` · `Blocked` · `Skipped` (out of this round's scope, with reason and who agreed)
| ID | Scenario | Covers AC | Expected (from the AC) | Actual | Status | Defect | Evidence | Run by |
|----|----------|-----------|------------------------|--------|--------|--------|----------|--------|

### Discrepancies
Class: `Defect` · `Requirement gap` · `Change request` · `Unknown` (ask the area owner)
| # | Seen in | What happened | Class | Goes to | Severity (QA) | Owner | Status |
|---|---------|---------------|-------|---------|---------------|-------|--------|

### Summary
| Item | Value |
|------|-------|
| Total scenarios | <must equal Pass + Fail + Blocked + Not run + Skipped> |
| Pass · Fail · Blocked · Not run · Skipped | |
| Open defects by severity | |
| Open risks (owner) | |
| RTM (`ba rtm`, `ba kpi`) | Covered … · Pending … · Missing link … |

### Decision
Decision: `Pending` · `Accept` · `Conditional acceptance` · `Reject` — by the approver only.
| Item | Value |
|------|-------|
| Decision | Pending |
| Approver | |
| Date | |
| Conditions (owner, due date) | |
| Decision record | D-… · evidence SRC-… |

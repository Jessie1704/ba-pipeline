---
name: ba-audit
description: Show, filter, verify and export the audit trail of the requirements workflow — who did what and when for a feature (stage runs and skips, decisions, approvals, changes, file edits) or for the workspace (profile/template changes). Verifies the tamper-evident hash chain and produces an auditor-ready report. Use when the BA asks "who approved…", "when did we decide…", "why was X skipped", "show the history", "audit report", or before a compliance review. Tiếng Việt: xem, lọc, xác minh và xuất audit trail — ai quyết định gì, khi nào, vì sao bỏ qua.
---

# /ba-audit — The record of how the requirements were made

Logs (append-only JSON Lines, SHA-256 hash-chained — see `MANUAL.md` §9):
- `requirements/<slug>/_audit/events.jsonl` — one per feature
- `audit/workspace.jsonl` — profiles, templates, checklists, glossary, configuration

Each line: `seq`, `ts` (UTC), `source` (hook = per-edit file record, sync = file record from `ba audit sync`,
skill = workflow event), `type`,
`actor`, `session`, `feature`, `stage`, `summary`, `reason`, `decision`, `severity`, `refs`, `file`,
`sha256` (file content after the change), `prev`, `hash`.

**Read-only stage.** Never edit an audit file. To correct an entry, log a `correction` event that names the
`seq` being corrected and why.

Sub-commands (infer from the BA's words): `show` · `verify` · `report` · `ask`.

## show [feature] [filters]
Read the log and present a timeline table: time (BA's local time), actor, event, stage, summary, refs.
Filters the BA may give: date range, type (`stage.*`, `decision.*`, `approval.*`…), stage, actor, ID
(`D-012` → every event referencing it), `--files` (include file records; hidden by default because
they are numerous — show a count instead). Group consecutive file edits of the same file in one session.

## verify [feature | all]
Run:
```
ba audit verify <slug>
ba audit verify --all
```
Report OK / FAILED per log. On failure: say which line and what it means (edited vs. removed/reordered),
and recommend restoring the log from version control and investigating; never "repair" the chain.
Also check `audit/hook-errors.log`: if it has entries, file records may be missing for those times — report them.
Then run `ba audit sync <slug> --dry-run`: it compares every artifact's current hash with its latest `file.*`
record and lists files changed, added or removed since. Report them (a change isn't necessarily wrong, but it
isn't recorded yet) and offer to record them with `ba audit sync <slug>`.

## report [feature]
Write `requirements/<slug>/_audit/report-<YYYY-MM-DD>.md` (the only file this stage may create in `_audit/`)
for auditors, containing:
1. Feature, PO, approach, current version and status; chain verification result and entry count.
2. **Stage record** — per stage: ran / ran lite / skipped / deferred, who chose, when, recommendation vs
   choice, skip reason and severity, gate result.
3. **Decisions & approvals** — every `D-` and approval with actor, date and evidence refs.
4. **Changes after approval** — change requests with decision and version.
5. **Review history** — scores over time.
6. **Deviations** — every choice that differed from the recommendation, every Critical/High skip,
   every handoff made with known defects.
7. **File activity summary** — files changed, number of edits, by whom, first/last change.
Log `audit.report-generated` afterwards.

## ask "<question>"
Answer from the log with citations to `seq` numbers, e.g. "Who skipped UX and why?" →
"pilot-ba skipped 6 UI/UX on 2026-10-23 14:12 UTC (seq 7): reuses existing screens; warned High; O-02 / D-014."
If the log doesn't contain the answer, say so — don't infer from artifacts without saying that you did.

## Limits to state when relevant
- File changes are recorded per edit only where the tool has hooks; elsewhere `ba audit sync` records them per
  stage, so several edits between two syncs appear as one `file.changed`. Changes made between syncs are
  detected (hash), but not attributed edit by edit.
- The hash chain detects edits, deletions and reordering **inside** a log; it cannot detect the newest lines
  being cut off. Committing the workspace to version control (or exporting reports) anchors the history.
- `actor` is the operating-system user; approvals given outside the tool are recorded as the BA reports them,
  with evidence references.

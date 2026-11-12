---
name: ba-audit
description: "Show, filter, verify and export the audit trail of the requirements workflow — who did what and when for a feature (stage runs and skips, decisions, approvals, changes, file edits) or for the workspace (profile/template changes). Verifies the tamper-evident hash chain and produces an auditor-ready report. Use when the BA asks \"who approved…\", \"when did we decide…\", \"why was X skipped\", \"show the history\", \"audit report\", or before a compliance review. Tiếng Việt: xem, lọc, xác minh và xuất audit trail — ai quyết định gì, khi nào, vì sao bỏ qua."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-audit

## Running BA Pipeline from this power

This power carries the whole workflow in its `package/` folder; the project keeps only its data (`requirements/`,
`audit/`, `.ba/config.json`, `.ba/local/` overrides). Once per session, find the copy to use:

1. **The project pinned its own copy?** If `.ba/tools/ba.py` exists in the project, use it: `python .ba/tools/ba.py`
   and the files in `.ba/core/`.
2. **Otherwise use the power's package** — the folder that holds `ba-pipeline.package`, i.e. `package/` next to this power's
   `skills/` folder. If `.ba/config.json` has `"package"`, that is the path. If you don't know this skill's folder,
   find the marker:
   - Windows (PowerShell): `Get-ChildItem -Path "$env:USERPROFILE\.kiro" -Recurse -Filter ba-pipeline.package -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName`
   - macOS / Linux: `find ~/.kiro -name ba-pipeline.package 2>/dev/null | head -1 | xargs dirname`
   - Not found (the power was imported from a folder elsewhere): ask the BA where the `kiro-power` folder is.
3. Run `python "<package>/tools/ba.py" where --save` from the project root (use `python3` on macOS/Linux; Python
   3.9+ is needed — if it is missing, ask the BA to install it). It prints the command, the manual and the core
   folder to use from now on, and saves the package path in `.ba/config.json` for the next sessions.

In the text below, `ba <command>` means that command (`python "<package>/tools/ba.py" <command>`), `.ba/core/` means
the core folder `ba where` printed, and `templates/…`, `checklists/…`, `profiles/…`, `reference/…` resolve to
`.ba/local/<path>` if the project has it, otherwise `<core>/<path>`. Run commands from the project root.

In Kiro: use a normal chat (Vibe) session, not Spec mode. Human gates are closed by the approver — never by you; in
controlled mode the approver runs `ba approve` in an operating-system terminal outside Kiro.

Read the operating manual (`<core>/MANUAL.md`, or the **ba-pipeline** skill) once per session before the first
stage, then follow this playbook exactly.

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

# Mechanical checks

Summary in MANUAL §10. `ba turn --gate` runs them at the end of a stage and logs the result.

`ba check <slug> [--only <check,check>]` checks in seconds:
*status* (`_status.md` present, current, template-complete, Open-items snapshot equal to the register),
*ids* (every referenced ID defined; `~~ID~~` defines a withdrawn one), *ranges* (History prose exempt),
*register* (every `A-`/`Q-` in `02-questions.md`), *ground* (every row of the business-rules table cites
`SRC-`/`D-`/`A-` in its Source column), *gherkin* (≥ 3 AC per story, every scenario has When/Then), *tables*
(data in header rows), *ambiguity* (ignores MoSCoW priority lines, quoted message text and the business's own
wording recorded in intake), *open* (canonical register values; Blocking and Decision-critical questions; open assumptions by risk),
*governance* (business owner and PO named in `_status.md` → *Governance* — WARN before `03-scope.md` exists, FAIL
after, also for every named area; every goal's Metric, Baseline and Target filled — FAIL if blank, WARN on
"unknown" with no plan to measure; a Foundations row with no status WARNs; every in-scope `IS-` cites a `G-` or `mandatory: … (SRC-/D-)` and has an owner; the BA also holding the PO
or business-owner role without a `D-` in *Role conflicts* WARNs), *rtm* (`rtm.md` from `ba rtm`, one row per AC and test: canonical Test/UAT result and Link values; FAIL on a result without *Evidence* and *Recorded by*, on evidence that points nowhere ('x', 'ok'), on a result recorded by the assistant, when the *Result log* differs from the audit log's `result.recorded` events, and when rows or Coverage are out of date — run `ba rtm`; WARN on Missing / Inferred / Stale link, Failed, Blocked, Orphan, and on recorders not named in the status page), *handoff* (once `handoff/` exists: every `handoff/*.md` in *Approach → Deliverables* exists — placeholder lines with `<…>` ignored; packs carry the *Skipped stages & known gaps* heading when a stage was skipped), *docs* (each `docs/*.md` has a canonical *Review status*; *Approved* needs an approval of exactly that file by the PO or business owner — not a rejection — and, when it was approved with `ba approve`, the file must not have changed since; a user guide describes only AC whose RTM rows are Covered), *gates* (the *Gates* table is found by its columns or a heading naming Gates/Cổng — a missing table or a row without its stage number FAILs; the *Mode* cell must name one mode (English or Vietnamese, notes allowed) and agree with the latest mode change by the PO or business owner; a *Defects* table without a Severity column (Severity · Sev · Mức độ) WARNs; *Gates* results must be canonical — `Passed`, `Failed`, `Skipped (O-NN)`, `Deferred`, `Blocked`, `–` — with notes after them; words like "Đạt", "Pass", "Approved" FAIL and are still compared with the log as passed; a human gate shown as passed or skipped needs its `gate.passed` / `stage.skipped` in the log by a person; one the AI tool relayed without a `SRC-` WARNs (FAILs in controlled mode); 8 Review Passed needs a Pass in *Review score history*; a Pass verdict with an open Critical, or below 80, FAILs (verdict, score and severities read without markdown, emoji or case); 9 Handoff Passed with a Critical or Major neither *Fixed* nor *Deferred (D-)* by the PO or business owner FAILs; 11 Test/UAT Passed with the PO's UAT thresholds not met FAILs; a non-standard *Mode* needs a `settings.changed` by the PO or business owner; `human_gates` in the config needs a workspace `settings.changed` run by a person outside the AI tool), *audit* (every `D-` of the Decision log is in
the audit log; no file change unrecorded).
Tables are read by column name with markdown stripped. FAIL blocks a gate; WARN is reported for the BA to judge.

**Change workflow files with your tool's file-editing feature**, not shell commands (sed, scripts): hooks
only see the former. Either way, `ba audit sync` records the result at the end of the stage. If a bulk shell
edit is truly needed, log a `files.bulk-edit` event listing the files afterwards.

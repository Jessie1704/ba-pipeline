---
name: ba-uat
description: "Testing, UAT and business acceptance for a built feature — check the AC → test links in the live RTM, support testers with the rules and expected results, triage every discrepancy as a defect, requirement gap or change request, prepare and record UAT scenarios with evidence in 11-uat.md, and prepare the acceptance decision for the approver. Use when a build is ready to test, when UAT with business users is organised, or when acceptance evidence must be consolidated. Tiếng Việt: kiểm thử, UAT và nghiệm thu — phân loại defect / requirement gap / change request, ghi kết quả có bằng chứng, chuẩn bị quyết định nghiệm thu."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-uat

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

# /ba-uat — Prove it with evidence

> **Start:** `ba context <slug> ba-uat`, then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "11 Test/UAT"`.
> **Human gate** in every mode: the acceptance decision belongs to the approver named in *Governance*.

**Never write `Pass` (or any result) without a real run.** Test results come from QA, UAT results from the
business users, each with an evidence link and the name of who recorded it. You do not set defect severity and you
do not recommend Accept or Reject — you present the evidence (guardrails 3–5).

## Steps

1. **Links before testing.** Run `ba rtm <slug>` and `ba check <slug> --only rtm`.
   - `Missing link` (an AC with no test): tell QA; QA may ask you for draft test cases — derive them only from
     the AC and the rules (happy, alternative, negative, boundary, role, state), mark them *AI draft — QA to
     review*, and add them to `handoff/qa-pack.md` once QA accepts them. Re-run `ba rtm`.
   - `Inferred link` (a test that probably covers an AC): QA confirms or removes it; only `Confirmed` counts.
   - `Orphan` (a row for an AC that no longer exists): explain it from the change log; never delete the row.

2. **Support execution.** Answer testers' questions from `05-stories.md` / `07-spec.md` with the rule ID and its
   source. A question the documents can't answer is a `Q-` for the owner in *Governance*, not a guess.

3. **Triage every discrepancy** into exactly one class, in `11-uat.md` → *Discrepancies*:
   | Class | Means | Goes to |
   |-------|-------|---------|
   | Defect | The build does not do what an approved AC says | QA/Dev (defect tracker); retest on a new build |
   | Requirement gap | No AC or rule describes this behaviour | `/ba-change` (returns to Spec/Stories per its table) |
   | Change request | The business wants a different behaviour than the approved AC | `/ba-change` |
   Not sure which → `Unknown`, ask the area owner; never pick a class to close the gate.

4. **Prepare UAT** in `11-uat.md` (from `templates/11-uat.md`): one scenario `UAT-NN` per approved AC or group of
   AC (always naming the `AC-` IDs), test data the business users may use (no real personal data in
   non-approved environments), instructions in the business's language (Preferences → *Language*).

5. **Record UAT as it happens.** Actual result, status, evidence link, who ran it — from the business user, not
   inferred. QA records *Test result*, the BA records *UAT result*, both in `rtm.md` (one row per AC and test) with
   *Evidence* (a link, a run or ticket ID, a file or a `SRC-` — not "ok") and *Recorded by* (the person who ran it,
   never the assistant). Then run `ba rtm`: it copies every new or changed result into the *Result log* and logs
   `result.recorded` with that person as actor. `ba check --only rtm` FAILs on a result without real evidence or a
   person's name.

5b. **Thresholds.** If the PO set acceptance thresholds (`_status.md` → *Preferences* → *UAT thresholds*, e.g.
   `coverage 100, pass 95`), `ba kpi` shows whether they are met; a threshold not met is reported to the approver
   with the failing rows, never rounded up.

6. **Summary.** Totals (Pass, Fail, Blocked, Not run, Skipped — they must add up), open defects with the
   severity QA gave them, open risks, and the build/version tested. Run `ba rtm` and `ba kpi <slug>`.

7. **Acceptance decision** — by the approver: *Accept*, *Conditional acceptance* (every condition with an owner
   and a date), *Reject* or *Pending*. Record it as a `D-` and log `approval.recorded` (actor = the approver, refs =
   the `D-` and the evidence `SRC-`). Reject → triage the reasons (step 3), fix, and run a new UAT round on the
   new build; the old round stays in `11-uat.md`.

8. **Gate 11 Test/UAT:** `ba check --only rtm` has no FAIL and no `Missing link`, `Inferred link` or `Failed`
   rows in the release scope (or each is covered by a condition with owner and date), severe defects are fixed
   or risk-accepted by the right person, and the decision is Accept or Conditional acceptance. Log `gate.passed`
   with the approver as `actor` and the decision's `D-` in `refs`.

## Finish with
- **Done:** scenarios run, results with evidence, discrepancies by class, the decision.
- **Needs your decision:** discrepancies of class `Unknown`; conditions without an owner.
- **Next step:** `/ba-release`; change requests go to `/ba-change`.

---
name: ba-scope
description: "Define the problem, measurable goals, success metrics, in-scope and out-of-scope items, assumptions, constraints, dependencies and risks for a requirements feature in 03-scope.md. Use after intake/elicitation, or when the BA needs to align with the Product Owner on what is being built and why. Tiếng Việt: vấn đề, mục tiêu đo được, trong và ngoài phạm vi, MVP, PO xác nhận."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-scope

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

# /ba-scope — Agree on the problem and the boundaries

> **Start:** `ba context <slug> ba-scope` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "3 Scope"`.

## Steps

1. Start from `ba context <slug> ba-scope` (governance, open Decision-critical questions, decisions to revisit
   at Scope, the profiles' §2). Open `01-intake.md` → *Foundations*, *Goals* and *Constraints*, and the decisions
   it cites. If a foundation is still open (success metric, business owner, PO, an area owner), draft what you
   can but say the scope is **provisional** and ask that question first.
2. Draft `03-scope.md` from `templates/03-scope.md`:
   - **Problem statement** — "<who> struggles with <what> when <situation>, causing <measurable impact>."
     Cite sources. If impact is unknown, raise a `Q-`.
   - **Goals** `G-NN` — SMART: metric, baseline, target, by when, how measured. A goal without a metric
     is a hope; flag it. A baseline may be "unknown — measured by <date>" with an owner, never blank.
   - **Non-goals** — what this deliberately won't try to achieve.
   - **Users & stakeholders** — primary/secondary users, with the job they're trying to get done.
   - **In scope** — capabilities, numbered (`IS-NN`), each linked to at least one `G-` (or `mandatory: <law/
     policy/constraint> (SRC-/D-)`), with its **owner** from *Governance*, and tagged with the profile that covers
     it (update `_status.md` → *Approach* → *Covers* with the final `IS-` IDs).
   - **Out of scope** — explicit list with reason (later phase / other team / not valuable). This list
     prevents most scope creep; push for at least 3 items.
   - **Assumptions** `A-`, **Constraints**, **Dependencies** (teams, systems, vendors, data).
   - **Risks** `R-NN` — likelihood × impact, mitigation, owner.
   - **MVP by value** (not for `small-change`: the whole change is one slice) — fill the *MVP by value* table: for each `IS-`, value (H/M/L and why, from the
     metric of the goal it serves), effort and risk (from builders or an `A-`). The MVP is the smallest set that reaches
     every MVP goal's target; say which goal each later slice serves. Never slice by feature count or by the
     order things were mentioned.
   - **Owners agree** — each area owner confirms the items of their area. When two owners want different
     things (priority, slice, rule), don't pick: write a Decision-critical `Q-` to the business owner with both
     positions and your recommendation.
3. **Self-check** before showing the BA:
   - Every in-scope item supports a goal (or is mandatory) and has an owner; every goal has at least one
     in-scope item; the MVP reaches the MVP goals' targets.
   - Provisional decisions with "Revisit at: 3 Scope" (e.g. a phase split made before goals existed) are
     re-decided now against the goals — keep, change or confirm each, as a new `D-`.
   - Nothing in scope contradicts a decision.
   - Run the ambiguity scan (`checklists/ambiguity-words.md`) on this file.
4. Write a **PO confirmation block** at the end: 5–8 bullet statements the PO can tick
   ("We are solving X for Y", "Success = Z by date", "Not doing A, B, C").

## Gate
No Decision-critical question open; `ba turn <slug> --events … --gate --stage "3 Scope"` has no *governance* FAIL
(business owner and PO named, every `IS-` has a goal and an owner); the PO confirms the confirmation block (BA
records it as `D-NNN` with date, `approval.recorded`). Until then status = *Draft*.

## Re-confirmation (scope changed after the gate, before handoff approval)
A new Decision-critical question re-opens the gate too (`gate.reopened`) until it is answered.
When an answer, review or stakeholder adds, removes or changes an `IS-` after the PO confirmed scope: log `gate.reopened` for Scope, mark the new or changed items
*Pending PO* in `03-scope.md`, update the PO confirmation block to show the delta (added / removed / changed,
with the reason and effect on goals and MVP), and get a new `D-` + `approval.recorded`. Later stages may
continue on pending items, but `/ba-review` treats unconfirmed scope as a Major defect and `/ba-handoff`
won't run until it is confirmed. After handoff approval, use `/ba-change` instead.

## Finish with
- **Done:** goals, scope items, out-of-scope items, risks.
- **Needs your decision:** scope items you flagged as debatable (with recommendation).
- **Next step:** send confirmation block to PO; proceed to `/ba-model`.

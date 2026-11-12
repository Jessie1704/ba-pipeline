---
name: ba-change
description: "Handle a change request against an existing requirements feature at any stage, from drafting to after release — log it as CR-NN, run an impact analysis across scope, model, stories, spec, handoff packs, sprints, tests and the RTM, apply approved changes with versioning, and send each part back to the right control point. Use when a stakeholder asks to add, remove or modify something, when UAT finds a requirement gap, or when a sprint question changes behaviour. Tiếng Việt: quản lý thay đổi (CR) — phân tích tác động, quay lại đúng điểm kiểm soát."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-change

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

# /ba-change — Controlled change with full impact view

## Steps

0. **Audit**: log `cr.logged` at step 1, `cr.decided` at step 5 (`decision`, `actor` = decider, `refs` = the
   evidence) and `cr.applied` at step 6 (new version in summary); log `approach.changed` if the approach changes.
   A CR may come from anyone at any stage — including a *Requirement gap* or *Change request* triaged in
   `/ba-uat` (cite its discrepancy number) and a question from the team during a sprint. A question that only
   clarifies existing behaviour is a `D-` (no CR); answer it from the confirmed sources or raise a `Q-`.

1. **Log** the request in `_status.md` → *Change log* as `CR-NN`: requester (`STK-`), date, description,
   reason / business value, urgency. Save the raw request as a source `SRC-NN`.

2. **Clarify** — if the request is vague, run a mini-elicitation (≤5 questions with options).

3. **Impact analysis** — search all artifacts for affected IDs. Produce a table:
   | Artifact | ID | Change type (add/modify/remove) | Description |
   Cover: goals & scope (is this scope creep? does it contradict out-of-scope?), flows/states/permissions,
   **approach** (does the change add or remove a solution type, e.g. "add a mobile app"? → update
   `_status.md` → *Approach*, stage plan, extra stages, overrides and deliverables), stories & AC, screens/wireframes/prototype (`06-ux.md`; a change may also make UX newly applicable), rules/data/messages/NFRs, integrations, handoff packs, tests, and anything already built
   (if the BA says so).

4. **Assess**: effect on goals, MVP slice, risks, dependencies, stories already in a sprint, tests already run
   (`rtm.md` rows with results); the size of the change in artifacts (number of AC, rules, screens touched) — the
   effort estimate is the team's, ask for it. Give a recommendation: accept / accept in later slice / reject, with
   reasons. Budget, contract or formal-acceptance changes go beyond the PO: name who decides (*Governance*).

5. **Decision** — the person with that right decides (PO by default, *Governance* otherwise); record as `D-NNN`
   linked to `CR-NN`. *Deferred* or *Pending* keeps the CR open with a review date.

6. **Apply** (only after acceptance):
   - Edit artifacts; mark changed items with `(changed CR-NN)`; withdrawn items with strikethrough.
   - Re-run mechanical checks from `/ba-review` step 3, and `ba rtm <slug>`: rows of changed AC that were already
     tested are **superseded** automatically and get a new row to retest.
   - Regenerate affected handoff packs; bump version (`v1.0 → v1.1`) and add a *What changed* section at the
     top of `agent-brief.md` and `qa-pack.md` so builders and testers see the delta first.

7. **Return to the right control point** — every row that matches the approved change applies; the CR is
   *Implemented* only when they are done:
   | The change touches | Return to | What must happen there |
   |--------------------|-----------|------------------------|
   | Clarification only, no behaviour change | — | a `D-` in the decision log |
   | A business rule or the to-be process | `/ba-model`, `/ba-spec` | the area owner re-confirms the changed part (`D-`); gate 7 for that part |
   | A story or AC | `/ba-stories` (then Review Lite) | changed AC re-reviewed; gate 5 and 8 for that part |
   | A story already Ready or in a sprint | `/ba-refine` | team and PO re-check the Definition of Ready |
   | A tested AC | `/ba-uat` | superseded RTM rows retested on the new build |
   | Scope (`IS-`) or the approach | `/ba-scope` / `/ba-intake` step 5 | PO re-confirms (`gate.reopened`, `approval.recorded`) |
   Log `gate.reopened` for every gate the change reopens.

## Finish with
- **Done:** CR logged, N items impacted, recommendation.
- **Needs your decision:** accept / defer / reject.
- **Next step:** apply, then notify owners of changed packs.

---
name: ba-step
description: "Run an extra stage that an approach profile adds to the workflow (for example vendor evaluation, fit-gap analysis, threat model, data profiling, cutover plan, experiment plan, autonomy review). Use when _status.md lists an extra stage as next, or the BA names one with /ba-step <stage-id>. Tiếng Việt: chạy stage bổ sung do profile thêm vào (đánh giá nhà cung cấp, threat model, cutover…)."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-step

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

# /ba-step <stage-id> — Run a profile-defined stage

> **Start:** `ba context <slug> ba-step` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "<n> <extra stage name>"`.

1. **Find the stage.** Read `_status.md` → *Approach* → *Stage plan*. Locate `<stage-id>`; find its definition
   in §11 *Extra stages* of the profile that owns it (or in an override). If no ID was given, list the extra
   stages in order with their status and run the first one not done.
   Unknown ID → list valid ones; never improvise a stage that isn't defined.

2. **Check readiness.** The stage named in *After stage* must have passed its gate (or the BA accepts
   proceeding — record a `D-`). Say which inputs you'll use.

3. **Run it.** Follow the defined *Steps* exactly, applying all `MANUAL.md` rules: cite sources, never invent
   facts, raise `Q-`/`A-` for unknowns, kill ambiguity, use IDs. If the profile names a template or table
   skeleton, use it; otherwise structure the output as: Purpose · Inputs · Method · Results · Findings ·
   Decisions needed · Impact on other artifacts.

4. **Write the output** to the document named in the definition (e.g. `05a-vendor-eval.md`).

5. **Propagate.** Results often change other artifacts (a selected vendor changes Spec; a threat model adds
   NFRs; data profiling adds DQ rules). List affected IDs and offer to update them now.

6. **Gate & status.** Evaluate the defined gate; update `_status.md` → *Gates* (add a row for the extra stage
   if missing), open-items counts, next action.

## Finish with
- **Done:** output document, key results, gate result.
- **Needs your decision:** the decisions the stage surfaced, with options and a recommendation.
- **Next step:** next stage in the plan (core or extra).

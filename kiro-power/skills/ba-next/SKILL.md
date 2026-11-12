---
name: ba-next
description: "Tell the business analyst the single best next action for a requirements feature, based on _status.md, open questions, gates and artifact state. Use when the BA asks \"what next?\", \"what should I do now?\", \"status\", or seems unsure how to proceed. Tiếng Việt: việc tiếp theo nên làm là gì? trạng thái hiện tại."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-next

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

# /ba-next — Guidance in one glance

1. Identify the feature (ask if several exist and none was named).
2. Start from `ba context <slug> ba-next`; open an artifact only if something there needs it. Include **deferred** stages ("Not now") and **skipped** stages
   with their severity — offer to revisit a skipped High/Critical stage when circumstances changed. Determine:
   - **Revisit triggers**: decisions that accepted a failed gate ("Revisit at: <stage>") — if that stage is
     current or past and the assumption is still open, this is the top blocker.
   - Current stage and whether its gate passes; the approach's stage plan including extra stages and overrides
     (never recommend a stage it marks Skip; recommend `/ba-step <id>` when an extra stage is next).
   - If the approach is weak (Low confidence, many overrides), suggest `/ba-profile` to install or create a better fit.
   - Open Blocking and Decision-critical `Q-` (and how long they've been open), High-risk `A-`, latest review score.
     Before the Scope gate, an open Decision-critical question is the top blocker, ahead of the next stage.
   - Artifacts that are stale (an answer or CR arrived after the artifact was last updated).
3. Reply in this exact shape (max ~12 lines):

```
📍 <feature> — Stage <n> <name> · Gate: <pass/fail: reason>
🧭 Approach: <primary> + <secondaries> (<Proposed/Confirmed>) · Skipped stages: <list or none>
🔴 Blockers: <count> (<top one, who owns it>)
✅ Next: <one action> → <command>
⏭  Then: <the action after that>
💡 Meanwhile you can: <work not blocked by the blocker>
```

Prioritisation rules: unblock others first (send questions) → fix Critical review defects → finish the current
gate → move forward. Never recommend skipping `/ba-review` before handoff.

After handoff the next stages are `/ba-refine` (sprints), `/ba-uat` (a build is ready) and `/ba-release`
(accepted). There, the blockers are RTM rows (`Missing link`, `Failed`, `Inferred link`, results without
evidence — `ba check <slug> --only rtm`), discrepancies of class `Unknown`, and human gates waiting for their
approver: name the approver and what they need to see. `ba status <slug>` gives the plain-language picture
("waiting for Linh: 3 questions") that the BA can paste to stakeholders.

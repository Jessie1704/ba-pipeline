---
name: ba-release
description: "Release, handover and improvement for an accepted feature — reconcile the release scope with the RTM row by row, update release notes, user guide, business-rule catalogue and FAQ with confirmed behaviour only, hand over known issues with owners, compute release KPIs, draft lessons learned for the BA to review, and feed improvements back into profiles. Writes 12-release.md. Use after the acceptance decision, at the end of a release, or when the BA asks for release notes, a handover pack or a retrospective. Tiếng Việt: phát hành, bàn giao và cải tiến — release notes, known issues có owner, KPI, bài học kinh nghiệm."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-release

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

# /ba-release — Hand over what was really built

> **Start:** `ba context <slug> ba-release`, then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "12 Release"`.
> **Human gate** (standard and controlled modes): the person receiving the handover accepts it.

Requires the acceptance decision from `/ba-uat` (Accept or Conditional acceptance). Without it, stop: there is
nothing to hand over yet.

## Steps

1. **Reconcile scope with the RTM, row by row.** `ba rtm <slug>` and `ba check <slug> --only rtm`. Every story in
   the release must have its rows `Covered`; anything else (Pending, Failed, Missing link, Inferred link) is listed
   in `12-release.md` → *Scope reconciliation* and reported to the PO — never "close enough". Rows of a
   *Conditional acceptance* carry the condition's owner and date.

2. **Outward documents** — release notes, user-guide changes, business-rule catalogue, FAQ (and the profile
   extras listed in *Deliverables*, e.g. `ops-runbook.md`). Write only behaviour that passed testing; anything
   unclear becomes a known issue or a `Q-`. Write in the readers' language (Preferences → *Language*).

3. **Known issues and open items.** Each with impact, workaround, **owner** and due date; every condition of a
   conditional acceptance and every open change request is one. An item without an owner fails the gate. Name the
   support contact after go-live.

4. **KPIs.** `ba kpi <slug>` and copy the table into `12-release.md` → *KPIs*, with one line per KPI on what it
   means for this release. The first releases set the baseline; don't judge them against targets nobody agreed.

5. **Lessons learned (AI draft).** Draft what went well and what to change, each with evidence from this feature
   (audit events, review history, change requests, retests). Mark it *AI draft — BA to review*; drop anything
   without evidence. Agreed actions get an owner and a date. Improvements to the workflow itself become a profile
   proposal (`/ba-profile` → learn) — never an edit to `.ba/core/`.

6. **Handover.** `12-release.md` → *Handover*: who receives what, version of every document (they must match the
   released version), where they are stored. AI-drafted documents are listed with who reviewed them. If the
   approach lists a user guide, run `/ba-docs user-guide` now (only tested behaviour). If the release changed an
   existing system that has a knowledge base, update its pages through `/ba-discover <system>` so the next
   feature starts from the truth.

7. **Gate 12 Release:** versions match, every known issue has an owner, AI drafts are reviewed, the receiver is
   named and accepted the handover (`D-` / `SRC-`). Log `gate.passed` with the receiver or the PO as `actor`.
   Update `_status.md`: *Status* → Released, version, and *History*.

## Finish with
- **Done:** release reconciled, documents updated, issues handed over, KPIs recorded.
- **Needs your decision:** items without an owner; lessons to turn into profile changes.
- **Next step:** the next request starts with `/ba-start`; changes to this feature go through `/ba-change`.

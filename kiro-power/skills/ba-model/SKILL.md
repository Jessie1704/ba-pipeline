---
name: ba-model
description: "Model a requirements feature — business process flows (as-is and to-be), entity state machines, domain/data model, roles and permissions matrix, and feature glossary — as Mermaid diagrams plus text in 04-model.md. Use after scope is drafted, or when the BA needs to visualise how the process, data or permissions work. Tiếng Việt: mô hình hoá quy trình, trạng thái, dữ liệu, vai trò và phân quyền."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-model

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

# /ba-model — Make the system visible

> **Start:** `ba context <slug> ba-model` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "4 Model"`.

Models are where most hidden gaps surface: every arrow, state and permission cell forces a question.

## Steps

1. Start from `ba context <slug> ba-model` (status, decisions to revisit, open items, and §4 *Model* of every
   active profile). Then read only what the model is built on: `03-scope.md` → *In scope* and *Goals*,
   `01-intake.md` → *Actors*, the process facts and *Terms for glossary*, `glossary.md`, and the decisions those
   cite. The open questions listed by `ba context` are not settled: model them as open (`Q-`), never as facts.
   Each profile's §4 says which diagrams matter (e.g. sequence diagrams for API, context diagram for integration, job flow
   for batch, lineage for data, human-in-the-loop flow for AI). Produce those in addition to, or instead of,
   the defaults below, as the profile states.
2. Build `04-model.md` from `templates/04-model.md`:

   **a. Process flows** (Mermaid `flowchart`, one per main scenario)
   - As-is (only if changing an existing process) and to-be.
   - Swimlanes by actor (use subgraphs). Mark system steps vs manual steps.
   - Every decision diamond has *all* outcomes drawn, including "invalid / timeout / cancelled".
   - Below each diagram: numbered step table (step, actor, action, rule refs `BR-`, notes).

   **b. State machines** (Mermaid `stateDiagram-v2`) for every entity with a lifecycle
   (order, request, application, account…). List each transition: from → to, trigger, who, guard rule.
   Ask: can it go back? be cancelled? expire? what's terminal?

   **c. Domain model** (Mermaid `erDiagram` or `classDiagram`) — business entities, key attributes,
   relationships with cardinality. Business view, not database design.

   **d. Roles & permissions matrix** — rows = actions, columns = roles, cells = Allow / Deny / Own only /
   Approval needed. Every empty cell is a question.

   **e. Feature glossary** — new terms; check against `glossary.md` for conflicts.

3. **Gap sweep from the models** — for every unexplained arrow, missing outcome, unreachable or dead-end
   state, empty permission cell, or cardinality nobody stated → add a `Q-` to `02-questions.md`
   (or an `A-`), and mention it in your summary.
4. Validate Mermaid syntax mentally: quote labels containing special characters, avoid parentheses in
   unquoted node text, keep IDs alphanumeric.

## Gate
Every in-scope item `IS-` appears in at least one flow; every entity with status has a state machine;
permissions matrix has no empty cells (answered or assumed).

## Finish with
- **Done:** diagrams created, new questions found by modelling.
- **Needs your decision:** top 3 modelling questions with recommended answers.
- **Next step:** `/ba-stories`.

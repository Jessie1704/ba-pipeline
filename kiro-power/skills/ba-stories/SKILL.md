---
name: ba-stories
description: "Write epics and user stories with Gherkin acceptance criteria, edge cases, priorities (MoSCoW), dependencies and a story map for a requirements feature in 05-stories.md. Use after modelling, or when the BA asks to create, split, refine or prioritise user stories / backlog items. Tiếng Việt: viết epic, user story và tiêu chí chấp nhận Gherkin."
metadata:
  version: "1.0.0"
  package: ba-pipeline
---

# ba-stories

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

# /ba-stories — Backlog that can be built and tested

> **Start:** `ba context <slug> ba-stories` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "5 Stories"`.

## Steps

1. Start from `ba context <slug> ba-stories` (status, open items, and §5 *Stories* of every active profile).
   Then read what the stories are built on: `03-scope.md` → *In scope* and *Goals*, `04-model.md` (including its *Feature
   glossary*), `glossary.md`, and the decisions they cite. The open questions listed by `ba context` are not
   settled: a story that depends on one cites it (`⚠ Q-NNN`) or a registered `A-`. Use each profile's §5 story style for the scope that profile covers
   (consumer stories for API, job stories for batch, metric stories for data, golden-set examples for AI, etc.).
2. **Derive epics** `EP-NN` from in-scope items / main flows. Each epic: goal link (`G-`), summary, story list.
3. **Derive stories** systematically — walk every flow step, state transition and permission row;
   each meaningful user-visible behaviour becomes a story. Then add stories for:
   admin/config, notifications, reporting/audit, error recovery, migration/first-time data, as relevant.
4. **Write each story** (format in `templates/05-stories.md`):
   - `US-NNN` title (verb + object), "As a <role from matrix>, I want <capability>, so that <benefit tied to G->".
   - **Acceptance criteria** in Gherkin, IDs `AC-NNN.n`. Minimum set:
     - 1+ happy path
     - 1+ alternative path
     - 1+ failure / validation / permission-denied path
     - boundary cases where numbers exist (min, max, just over, empty, zero)
   - Concrete example values in steps (`Given an order of €49.99 placed 31 days ago`), not placeholders.
   - **Business rules** referenced (`BR-`; define them in `07-spec.md`), **UI notes**, **Data touched**.
   - **Out of scope for this story**, **Dependencies** (`US-`, systems), **Open items** (`Q-`, `A-`).
   - **Priority** (MoSCoW) proposed with one-line reason; **Size hint** (S/M/L) — large → split.
   - **Traces to:** `G-`, `IS-`, flow step, `SRC-`/`D-`.
5. **INVEST check** every story; split anything failing *Small* or *Testable* using the splitting
   patterns in `checklists/story-splitting.md`.
6. **Story map** — table: backbone (activities from the flow) × release slices (MVP / Next / Later).
7. **Coverage check:** every `IS-` has stories; every flow step and state transition is covered by an AC;
   list anything uncovered.
8. **Grounding self-check** (the most common failure: plausible "filler" behaviour written as fact).
   Re-read every story and AC and ask of each **capability, behaviour, number, time and limit**: *which `SRC-`,
   `D-` or registered `A-` says so?* Anything without one is either deleted, or registered now in
   `02-questions.md` → *Assumptions* (with risk) and marked inline `⚠ A-NNN`. Typical traps: convenience
   features (bulk actions, auto-routing fallbacks), blocking rules nobody asked for, retry/timeout values,
   field ranges, and qualifiers dropped from the source ("domestic", "absent > 3 days").
   Report the count: "Grounding: N statements checked, M newly registered as assumptions."
9. **Mechanical check:** `ba turn <slug> --events … --gate --stage "5 Stories"` runs the checks and logs them;
   fix every FAIL and run it again before logging `gate.passed`. While drafting, a quick unlogged
   `ba check <slug> --only gherkin,ids` on what you just wrote is fine.

## Gate
All stories INVEST; every story has ≥3 AC covering happy/alt/failure; no `IS-` uncovered; grounding
self-check done (every behaviour cites `SRC-`/`D-`/`A-`); `ba check` has no FAIL.

## Finish with
- **Done:** epics, stories, AC counts, MVP size.
- **Needs your decision:** MoSCoW for stories where you weren't confident; stories you split.
- **Next step:** `/ba-ux` if any story has a user interface (it will mark itself N/A otherwise), then `/ba-spec`.

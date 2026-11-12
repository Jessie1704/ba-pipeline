---
name: ba-review
description: Independent quality gate for a requirements feature. Delegates to the requirements-reviewer agent to score all artifacts against the quality rubric and Definition of Ready, lists defects by severity with fixes, and writes 08-review.md. Use before handoff, before PO sign-off, or whenever the BA asks "is this good enough?" / "review my requirements". Tiếng Việt: review độc lập, chấm điểm, danh sách lỗi có bằng chứng, walkthrough với Dev và QA.
---

# /ba-review — Fresh-eyes quality gate

> **Start:** `ba context <slug> ba-review` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "8 Review"`.

## Steps

1. Identify the feature folder. Confirm artifacts 01–07 exist (list any missing — review proceeds but
   missing artifacts score 0 in their category). `06-ux.md` may be absent only if `_status.md` marks UX
   as N/A with a reason; if stories mention screens/forms but UX is N/A, that is a Major defect.

2. **Hand the review to an independent reviewer** (`MANUAL.md` §7: a sub-agent if your tool has one,
   otherwise a new chat or another tool, with the prompt given there). Brief:
   > You are the independent requirements reviewer. Read `.ba/core/agents/requirements-reviewer.md` and follow
   > it exactly. Review `requirements/<slug>/` against `checklists/quality-rubric.md` and
   > `checklists/definition-of-ready.md`, plus the active profiles listed in `_status.md` → *Approach*
   > (`profiles/<name>.md`). Read `.ba/core/MANUAL.md` for conventions. Check groundedness explicitly: every
   > behaviour, value and limit must trace to a source, decision or registered assumption; anything else is an
   > invented fact (Critical). Do not edit any files.
   Do not pass your own opinion of the artifacts — the value is independence. Record in `08-review.md` how the
   review ran (sub-agent / new session / other tool) — and if it had to run in this same conversation, say so
   and cap the verdict at *Conditional*.

3. **Run mechanical checks yourself** in parallel (they're deterministic):
   - Run `ba turn <slug> --events … --gate --stage "8 Review"` (all checks: status, IDs, ranges, register,
     grounding, Gherkin, tables, ambiguity, open items, governance, rtm, handoff, audit; it logs `check.run`) and copy its
     PASS/WARN/FAIL lines into the *Mechanical checks* table.
   - Orphans (judgement): stories with no `G-`; goals with no stories; rules used by nothing.
   - Approach conformance: approach is *Confirmed*; every stage marked Run/Adapted/Partial has its output;
     every profile spec section (§7) exists and is filled; every profile §10 *Review check* passes;
     every `IS-` is covered by a profile; every extra stage in the plan has its output document and passed
     its gate; every override has a reason and a `D-`.
   - UX coverage (if UX applies): every UI story maps to an `SCR-`; every screen has all states filled;
     every `SCR-` element field and `MSG-` resolves in `07-spec.md`.

4. **Merge** into `08-review.md` (from `templates/08-review.md`): score per rubric category, total, the
   **proven defects** sorted by severity (each with its evidence), the **risks to verify** (each becomes a `Q-`
   for the owner), and a **fix plan** grouped by artifact with an owner and due date for every Major. The verdict
   follows `checklists/quality-rubric.md`: **Pass** = no Critical, every Major fixed or owned with a date, score
   ≥ 80 · **Conditional** = no Critical but an unowned Major, or 70–79 · **Fail** = any Critical, or < 70.

4b. **Team walkthrough** (standard and controlled modes; Lite in quick mode = QA only). When the AI verdict is
   Pass or Conditional, walk the Dev/Tech Lead and QA through the stories and spec (30–45 minutes: the flows, the
   rules with numbers, the error paths, the NFRs). Record in `08-review.md` → *Team walkthrough*: who attended,
   feasibility concerns, untestable AC, missing test data — each as a defect with origin `walkthrough` or a `Q-`.
   The walkthrough's confirmation is a `D-` ("Dev + QA reviewed; concerns: …"), logged `decision.recorded` with
   the Tech Lead or QA lead as `actor`. Only people who will build or test it can say it is buildable and testable.

4b'. **Majors before build.** A Major that is *owned* is not *fixed*. Every Critical and Major keeps a *Status*
   (`Open` → `Fixed` when the fix is verified, or `Deferred (D-NN)` when the PO decides to build with it). Handoff
   (gate 9) cannot pass while one is `Open` — `ba check --only gates` FAILs it — so an owned Major either gets fixed
   before the builder starts or goes on record as a decision.

4c. **Gate 8** is a human gate (MANUAL §8 step 5): the PO (or the approver named in *Governance*) accepts the
   verdict and the owned Majors. Log `gate.passed` with that person as `actor` and the walkthrough `D-` plus the
   PO's acceptance in `refs`.

5. Offer to **auto-fix** mechanical and Minor defects now; Critical/Major ones that need business input
   become `Q-`s. **Fix rounds invent facts too** — quick fixes tend to add unsourced timings, recipients and
   policy wording. Before any re-review:
   1. Run `ba turn <slug>`, then list every line the fix round changed (the `file.*` records since the
      review show which files; compare against the review's version for the lines).
   2. Re-run the grounding self-check (`/ba-stories` step 8, `/ba-spec` step 13) **on those lines only**:
      every new number, behaviour, recipient or policy quote gets a citation or becomes a registered `A-`.
   3. Run `ba turn <slug> --events … --gate --stage "8 Review"` and fix every FAIL.
   4. Add a *Fix-round grounding* table to `08-review.md`: changed item · new statement · citation.
   Then re-run steps 3–4 (re-run step 2 only if substantive content changed).

6. Update `_status.md` with score history (date, score, verdict) so improvement is visible, and log
   `review.scored` (summary: score, verdict, defect counts by severity, and counts by origin).

**Comparing reviews.** A fresh reviewer samples differently, so scores move by about **±3** between runs even
when nothing changed. Ask the reviewer to tag every defect's origin: **new** (introduced since the last
review), **regression** (was fixed, broke again), or **previously missed** (was there before, not reported).
Judge progress by *new + regression* falling and all earlier Critical defects staying fixed, not by the total
alone. When a score sits within 3 points of a threshold (70 or 80), and always in *controlled* mode, run a
**second independent reviewer** and use the average score and the union of Critical defects.

**Skipped stages:** for every gate marked *Skipped (O-NN)*, add a finding at the severity from
`checklists/stage-skip-impact.md` (one level lower if its minimum mitigation was applied) and ask the
reviewer to judge whether the skip reason holds. If this review itself is run Lite or skipped, the handoff
packs must say "Not independently reviewed".

## Finish with
- **Done:** score, verdict, defect counts by severity.
- **Needs your decision:** "Shall I fix the N auto-fixable defects?" + business questions.
- **Next step:** fix → re-review, or `/ba-handoff` when passed.

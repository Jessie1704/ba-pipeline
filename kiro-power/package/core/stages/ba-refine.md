---
name: ba-refine
description: Backlog refinement and sprint preparation for a handed-off feature — prepare the stories and open questions, let the PO explain value and order, let Dev/Tech Lead check feasibility and dependencies and QA check testability, record the team's split and estimate, and check the Definition of Ready per story in 10-refinement.md. Use after handoff when stories go into a sprint, when a story is too big for one sprint, or when the BA asks "are these stories ready?". Tiếng Việt: refinement và chuẩn bị sprint — kiểm tra Definition of Ready, tách story, ghi ước lượng của team.
---

# /ba-refine — Make stories ready for a sprint

> **Start:** `ba context <slug> ba-refine`, then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "10 Refine"`.
> **Human gate** (standard and controlled modes): the team and the PO decide a story is Ready — you prepare it.

**You never estimate, never set priority or order, and never mark a story Ready.** Estimates come from the team,
order from the PO; you record them with who said it (MANUAL §4a, guardrails 3–4).

## Steps

1. **Prepare** (before the session) in `10-refinement.md` (from `templates/10-refinement.md`):
   - The stories proposed for the sprint (the PO names them; if not, ask — don't choose), each with its open
     `Q-`/`A-` IDs, dependencies and the stories that look too big (more than one sprint, more than ~8 AC, or
     several actors/flows — `checklists/story-splitting.md`).
   - Business context and the sources the team may ask about, so answers in the session cite `SRC-`/`D-`.

2. **During the session — record, don't decide.** One row per story in the *Readiness* table:
   - **PO:** value and order (`D-` when the order changes).
   - **Dev / Tech Lead:** feasible? architecture constraints? technical dependencies (with owner and date)?
   - **QA:** is every AC testable? which test data and environments are needed?
   - **Team:** split (new stories keep the parent's AC IDs or get new ones — never renumber), estimate in the
     team's unit, and "fits one sprint: yes/no".
   Anything that changes a story's behaviour, a rule or the scope after handoff approval is a change request:
   `/ba-change` (it decides which gates reopen), not an in-place edit.

3. **Splits.** Apply agreed splits in `05-stories.md` (withdrawn parts as `~~AC-…~~ (split into US-…, D-…)`), then
   run `ba rtm <slug>` so every AC still has its row, and `ba check <slug> --only ids,gherkin,rtm`.

4. **Definition of Ready** per story (`checklists/definition-of-ready.md` → *Sprint level*): each criterion is
   confirmed by the role named in the checklist, with a name — not by you. Criteria not met stay *Not ready* with
   the reason. A story the PO wants in the sprint although not Ready → the PO's risk acceptance is a `D-`
   ("enter sprint not ready: <criteria>, owner, date"), logged as `approval.recorded` with the PO as actor.

5. **Optional AI checklist pass** — offer to run the DoR checklist over the prepared stories and list gaps as
   questions for the team. Label it *AI draft — for the team to confirm*; it never ticks a box.

6. **Gate 10 Refine:** every story selected for the sprint is *Ready* (or has the PO's `D-`), the RTM is current,
   and the minutes name who attended. Log `gate.passed` with `actor` = the PO (or the team lead named in
   *Governance → Gate approvers*) and `refs` = the `D-`/`SRC-` (minutes) — `ba turn` refuses it otherwise.

## Finish with
- **Done:** stories Ready / not Ready (with the missing criteria), splits applied, decisions recorded.
- **Needs your decision:** questions still open for the sprint, with owners and dates.
- **Next step:** sprint; when a build is ready for testing, `/ba-uat`.

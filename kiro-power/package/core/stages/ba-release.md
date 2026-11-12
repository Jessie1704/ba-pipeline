---
name: ba-release
description: Release, handover and improvement for an accepted feature — reconcile the release scope with the RTM row by row, update release notes, user guide, business-rule catalogue and FAQ with confirmed behaviour only, hand over known issues with owners, compute release KPIs, draft lessons learned for the BA to review, and feed improvements back into profiles. Writes 12-release.md. Use after the acceptance decision, at the end of a release, or when the BA asks for release notes, a handover pack or a retrospective. Tiếng Việt: phát hành, bàn giao và cải tiến — release notes, known issues có owner, KPI, bài học kinh nghiệm.
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

---
name: ba-handoff
description: Generate role-specific deliverables from a reviewed requirements feature — PO approval one-pager, AI coding agent build brief, QA test pack, designer brief (UI features), plain-language team summary, traceability and the live RTM — in requirements/<slug>/handoff/, plus Excel and dashboard copies for stakeholders. Optionally push stories to Jira/Azure DevOps if a connector is available. Use when review has passed, or when the BA asks to "hand off", "package", "send to dev/PO/QA". Tiếng Việt: bàn giao — gói tài liệu cho PO, dev/AI agent, QA, designer, team; RTM; xuất Excel.
---

# /ba-handoff — One source, every audience

> **Start:** `ba context <slug> ba-handoff` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "9 Handoff"`.

## Pre-check
- `08-review.md` verdict is **Pass**. If not, say so, show the blocking defects, and only continue if
  the BA explicitly overrides (record as `D-` "handoff with known defects: …").
- No open **High** or **Medium** assumptions (`ba check <slug> --only open`). Open **Low** assumptions are allowed only
  if a `D-` records the PO's bulk acceptance of exactly those IDs (`MANUAL.md` rule 1); list them in every pack
  under *Skipped stages & known gaps*. If Lows are open without that `D-`, offer the bulk-acceptance card from
  `/ba-elicit` → *Converging* instead of stopping.
- `ba check` has no FAIL.

## Generate (from `templates/handoff/`)

Generate exactly the documents in `_status.md` → *Approach* → *Deliverables*. The packs below are the
defaults; a *process-only* feature replaces `agent-brief.md` with procedures, a RACI and training notes.

1. **`po-approval.md`** — max ~1 page. Problem & value (with goal metrics), scope in/out (bullets),
   MVP slice, key decisions taken, **decisions still needed** (yes/no form), top risks, cost of delay if known,
   approval line (name / date / approve · approve with changes · reject). No Gherkin, no field lists.

2. **`agent-brief.md`** — self-contained build brief for an AI coding agent or developer. It must be
   implementable *without reading anything else*:
   - Context in 5 lines; glossary of domain terms used.
   - Scope / explicit non-scope ("Do NOT build …").
   - Domain model, state machines (Mermaid), permission matrix.
   - Business rules (full text + decision tables), data dictionary, messages (exact text).
   - Stories in implementation order (respect dependencies), each with full Gherkin AC.
   - Integrations & failure handling; NFRs as testable constraints.
   - Assumptions the builder may rely on; **open items the builder must NOT guess** (stop and ask).
   - Definition of Done: all AC pass as automated tests; IDs referenced in commits/tests
     (e.g. test names contain `AC-021.3`).
   - Write imperatively and literally. No "etc.", no "similar to", no references to conversations.

3. **`qa-pack.md`** — test scenarios derived from every AC plus extra negative/boundary/role/state-transition
   cases; test data table (realistic example values); environment & data prerequisites; NFR test approach;
   regression areas (if change to existing system); mapping scenario → `AC-`.

3b. **`design-brief.md`** — *only if UX applies.* For designers: context, users & journeys, constraints
   (channels, design system, accessibility target, languages), screens to design with priorities,
   must-haves per screen (elements, states, role differences, microcopy, `MSG-` texts), decisions taken,
   open design questions, link to `ux/prototype.html`.
   Also: in `agent-brief.md` add a *Screens* section (navigation map, wireframes, elements, states per
   `SCR-`), and in `qa-pack.md` add UI-state, responsive and accessibility scenarios per screen.

4. **`team-summary.md`** — plain language, ≤ 2-minute read: what's changing, for whom, why, when,
   what it means for each team (support, ops, sales, training…), who to ask. No IDs except a link to details.

4b. **Profile extras** — produce every document in `_status.md` → *Approach* → *Deliverables*, using the
   §9 *Handoff extras* of each active profile (e.g. `api-consumer-guide.md`, `ops-runbook.md`,
   `data-catalogue.md`, `eval-pack.md`, `release-notes.md`). Add the profile-specific sections to
   `agent-brief.md` and `qa-pack.md` that §9 lists. Skip `design-brief.md` when UX is N/A.

5. **RTM and `traceability.md`.** After writing `qa-pack.md`, run `ba rtm <slug>`: it builds `rtm.md` (one row per
   AC with its story, goal, rules and the `TS-` that cover it, version and AC hash) — the live matrix QA and UAT fill
   in later. Then write `traceability.md`: the goal-level view `G- → IS- → EP- → US- → AC- → BR-/NFR- → TS-`, the
   reverse checks (orphan list must be empty), and a pointer to `rtm.md` for per-AC results.
   `ba check --only rtm` must show no `Missing link` before the gate.

6. **Optional push to tools.** If a Jira / Azure DevOps / Linear / Confluence connector is available, ask
   before creating anything; then create epics/stories with AC in the description and IDs in the title,
   and record the external keys in `05-stories.md`.

6b. **Skipped stages & known gaps** — every pack starts with this box (omit only if nothing was skipped):
   stage, reason (`O-`/`D-`), severity, mitigation applied, open Low/Medium assumptions. For the PO pack
   make it prominent; for the agent brief add "do not assume anything the skipped stage would have defined".

6c. Log `handoff.generated` (summary: version and files). When the BA reports the PO's decision, log
   `approval.recorded` with `actor` = the approver, `decision` approved | approved-with-changes | rejected,
   and `refs` = the `D-` and the evidence `SRC-` (`ba turn` refuses an approval without them).

6d. **Stakeholder copies.** Offer `ba export <slug>` (Excel: registers, decisions, AC, spec tables, RTM) and
   `ba status <slug> --html exports/<slug>.html` (one-page dashboard) for people who don't read markdown.

7. **Gate 9** is a human gate: run `ba turn … --gate --stage "9 Handoff"` (the *handoff* check FAILs if a listed
   deliverable is missing), then log `gate.passed` only with the PO's approval (`actor` = PO, `refs` = `D-`, `SRC-`).
   Update `_status.md`: stage = Handoff, handoff date, version tag (e.g. `v1.0`), and freeze note: further changes
   go through `/ba-change`. Next: `/ba-refine` when the team runs sprints, otherwise `/ba-uat` when a build is ready.

## Finish with
- **Done:** files created, with one line on who should receive each.
- **Needs your decision:** send / push confirmations.
- **Next step:** PO approval; on approval record `D-` and set status *Approved*.

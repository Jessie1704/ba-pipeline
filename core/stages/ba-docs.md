---
name: ba-docs
description: Produce formal documents from a feature's artifacts for readers outside the delivery team — a Business Requirements Document (BRD) for sponsors and the business, a User Requirements Document (URD) from the end users' point of view, and a user guide for end users (per role, task by task, only behaviour that passed UAT) — in requirements/<slug>/docs/, each with evidence labels, full source traceability and its own approval. Use when the organisation requires a BRD or URD, when the BA asks for a user guide, user manual or training material, or before go-live. Tiếng Việt: tạo tài liệu chính thức — BRD, URD, tài liệu hướng dẫn sử dụng cho người dùng cuối — có truy vết nguồn và phê duyệt riêng.
---

# /ba-docs <brd | urd | user-guide> — Formal documents, generated from the truth

> **Start:** `ba context <slug> ba-docs`. Each turn ends with `ba turn <slug> --events …`.
> Documents have no numbered gate: each one is approved on its own (step 6), and `ba check --only docs` guards it.

Documents are **views of the artifacts, not new requirements**. Every statement comes from `01`–`12`, `rtm.md` or a
source, with its ID; a gap is a `Q-` in `02-questions.md`, never filler text. Write in the feature's *Language*;
keep IDs and canonical values in English. If the BA didn't name a document, ask which one and for whom.

## When each document can be written

| Document | Reader | Earliest | Final when | Approver (from *Governance*) |
|----------|--------|----------|------------|------------------------------|
| `docs/brd.md` | sponsor, business owner, steering committee | Scope gate (3) passed | Spec (7) done; re-issued on every approved CR | Business owner / sponsor; PO confirms |
| `docs/urd.md` | user representatives, UX, UAT | Stories (5) done (and UX 6 if there is a UI) | Spec (7) done | A user representative reviews; PO approves |
| `docs/user-guide[-<role>].md` | end users, support, trainers | Handoff (9), as a draft | After the acceptance decision (11): only behaviour whose RTM rows are `Covered` | PO or business owner; support lead reviews |

Stop and say why (keep the document *Draft*) when: the earliest point isn't reached; the business owner or PO isn't
named in *Governance*; two sources contradict each other with no decision; an approver is asked to approve a
document that still has open *Unknown* items.

## Steps

1. **Pick the template** — `templates/docs/brd.md`, `urd.md` or `user-guide.md` (a project override in
   `.ba/local/templates/docs/` wins: many organisations have a house BRD format; keep their headings and map the
   content). Copy it to `requirements/<slug>/docs/`.

2. **Fill it from the artifacts, by reference.** The template says which artifact feeds each section (goals from
   `03-scope.md`, rules from `07-spec.md`, roles from `04-model.md`, use cases from flows and stories, messages from
   the `MSG-` catalogue, screens from `06-ux.md`…). Quote IDs; copy exact wording for rules and messages. Label every
   statement that is not a plain copy of an approved artifact: **[Fact]** (cites `SRC-`/`D-`), **[Assumption]**
   (`A-`), **[Inference]** (with its basis) or **[Unknown]** (a `Q-`, with an owner).

3. **User guide only — what really works.** Run `ba rtm <slug>`. Describe a task only if all its AC rows are
   `Covered`; tasks still pending go to *Coming soon / known limitations* with the known-issue owner from
   `12-release.md`. Per task: who, when, steps with the screen (`SCR-`) and the exact messages (`MSG-`), what to do
   when it goes wrong, who to ask. No screenshots invented: mark `[screenshot: SCR-04, state Empty]` for the
   team to capture from the tested build.

4. **No new requirements.** Anything the document needs that the artifacts don't say (a KPI target, an SLA, a
   persona, a usability threshold) becomes a `Q-` for its owner and an *Unknown* line — or goes back to the right
   stage (`/ba-scope`, `/ba-spec`) — never a number you made up.

5. **Self-check before review:** every section filled or explicitly "not applicable (why)"; every rule and message
   identical to `07-spec.md`; every *Unknown* is a registered `Q-` with an owner; `ba check <slug> --only
   docs,ids,ambiguity` has no FAIL. Set *Review status* to `In review`. Mark it *AI draft — <approver> to review*.

6. **Approval.** Send the document to its approver (table above). Their decision is a `D-` ("BRD v1.0 approved
   by …", with the email or minutes as a `SRC-`); then set *Review status* `Approved`, fill the approval table, and
   log `docs.generated` (summary: document and version) and `approval.recorded` with the approver as `actor`, the
   `D-`/`SRC-` in `refs`, and the document's file name in the summary (`brd.md v1.0 approved`). `ba check
   --only docs` FAILs a document marked Approved without that event.

7. **Keep it current.** An approved CR that changes what a document says re-opens it: bump the version, list the
   changes in *Document history*, and repeat steps 5–6. A user guide is re-issued with each release.

## Finish with
- **Done:** document, version, status, open *Unknown* items with owners.
- **Needs your decision:** who approves (if *Governance* doesn't say), and the open questions.
- **Next step:** send it for approval; for user guides, `/ba-release` hands it over with the release.

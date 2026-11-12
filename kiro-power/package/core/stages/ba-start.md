---
name: ba-start
description: Start a new requirements feature or resume an existing one. Triages the request (new feature, enhancement, defect, technical change, compliance, process-only), proposes the mode (quick, standard, controlled) and language, and creates requirements/<feature-slug>/ with _status.md and sources/ — or summarises where an existing feature stands. Use when the BA begins work on a new request, feature, epic or project, or says "continue", "resume", "where was I". Tiếng Việt: bắt đầu hoặc tiếp tục một feature, phân loại yêu cầu, chọn chế độ và ngôn ngữ.
---

# /ba-start — Start or resume a feature

## Steps

1. **Detect intent.** List folders in `requirements/`.
   - If the BA named a feature that exists (fuzzy-match the slug) → **resume** (step 5).
   - If none named and several exist → show a table (feature, stage, open Blocking and Decision-critical Qs, last updated)
     and ask which one.
   - Otherwise → **create** (step 2).

2. **Collect the minimum** (ask in one message, accept partial answers, mark the rest `Q-`):
   - Feature name (one line) and a one-sentence "why" — and how we'll know it worked (a number, if they have one)
   - **Business owner** (funds it, final say when stakeholders disagree) and **Product Owner** (decides scope and
     acceptance) — names and roles; they may be the same person. If the BA is one of them, note it.
   - Known stakeholders and their roles, and which areas (modules, processes) each one owns
   - Target outcome date or release, if any
   - **Request type** (one): new product · new feature · enhancement · defect · technical change · compliance ·
     process-only. Not enough evidence → `unknown` with a `Q-`; the feature waits for the answer.
   - Kind of solution, if known: web app · mobile app · API · integration · batch · data/reporting · AI feature
   - Delivery context: who builds it (AI coding agent, in-house team, vendor) and the tech stack, if known;
     whether the team runs sprints (stages 10–12) or hands over to another delivery process
   - Language for documents and chat: English (`en`), Vietnamese (`vi`) or another

2b. **Route by request type and propose the mode** (MANUAL §1; the BA confirms, record a `D-`):
   | Request type | Route | Mode |
   |--------------|-------|------|
   | new product, new feature, compliance | full Define → Deliver | standard (controlled for regulated, payments, high-security, vendor-delivered) |
   | enhancement | full, profiles decide what runs Lite | standard, or quick if ≤ 5 stories and one area |
   | defect that breaks an approved AC | no new requirements: link the AC, go to `/ba-uat` for the retest | quick |
   | defect where no AC describes the behaviour | it is a requirement gap: `/ba-change` on the feature that owns it | quick |
   | technical change, no business behaviour change (Tech Lead confirms, `D-`) | Intake + dependencies and impact; stories only if needed | quick |
   | technical change that changes behaviour | full | standard |
   | process-only | process-only modifier: no agent brief; procedures, RACI, training | standard |
   Shortcuts never skip the Handoff (9) or Test/UAT (11) gates.

3. **Create the folder**, in this order (so the audit log starts with the feature's creation):
   1. Create the empty directories `requirements/<kebab-case-slug>/sources/` and `.../handoff/`.
   2. Log `feature.created` (see `MANUAL.md` §9) with the PO and type of work in the summary —
      **before writing any file**.
   3. Write `sources/README.md`: "Raw inputs. Never edit. Name files `SRC-NN-<short-name>.<ext>`."
   4. Write `_status.md` from `templates/_status.md`, filled with step-2 answers.
   5. Ask once, in one message: "Before each stage I'll recommend run/skip with warnings — show the full card
      **always**, only **on deviation** (default), or **never**?" and "When I have questions: **walkthrough**
      (I ask a few at a time with suggestions — how many per message? default 5) or **file** (I write an answer
      form, you fill it in and say 'done')?" Record them in `_status.md` → *Preferences* (*Stage prompts*,
      *Answer mode*, *Questions per message*, plus *Mode* and *Language* from step 2b); the names go to
      *Governance*, including **Gate approvers** for the human gates of the mode (who approves Scope, Review,
      Handoff, Ready, acceptance and the release handover). A mode other than *standard* is a decision: record
      the `D-` and log `settings.changed` with summary `Mode: <mode>` (the *gates* check asks for it).
   6. Ask once: "Does your organisation need formal documents — a **BRD**, a **URD**, a **user guide** for end
      users?" Add each one to *Approach* → *Deliverables* (`docs/brd.md`, `docs/urd.md`,
      `docs/user-guide-<role>.md`); `/ba-docs` produces them at the right stage.
   7. If the request changes an **existing system** and `ba context` lists no knowledge base for it — or the BA is
      new to the project — offer `/ba-discover <system>` first: a day spent learning the system saves rounds of
      questions later. Never block the feature on it.

4. **Note a first guess, don't decide yet.** Record in `_status.md` → *Initial notes from /ba-start* the BA's
   view of the type of work and the kind of solution (web, mobile, API, integration, batch, data, AI…).
   The approach is decided from evidence in `/ba-intake` step 5 using `profiles/`.

5. **Resume.** Run `ba context <slug> ba-start` and `ba check <slug> --only status,open,governance`, and give the
   "Where we are" recap from them (stage, gate status, open Blocking and Decision-critical Qs, unconfirmed
   high-risk assumptions, last decision). If it reports **missing template parts**
   (templates change; existing features don't follow automatically), offer to migrate: add the missing
   sections and columns from `templates/_status.md`, keep every existing value, fill new columns
   with `—`, and add a *History* line "Migrated to current status template".

## Finish with

- **Done:** folder created / resumed.
- **Needs your decision:** anything missing from step 2.
- **Next step:** usually `/ba-intake` — "Drop your notes, emails, transcripts into
  `requirements/<slug>/sources/` or paste them here."

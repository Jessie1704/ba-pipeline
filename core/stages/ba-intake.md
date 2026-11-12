---
name: ba-intake
description: Ingest raw inputs (meeting notes, transcripts, emails, tickets, screenshots, existing documents, pasted text) for a requirements feature and extract facts, actors, goals, pain points, constraints and contradictions into 01-intake.md, then determine the analysis approach (solution type profiles such as web app, mobile app, API, integration, batch, data, AI feature) that decides which stages run and which documents are produced. Use when the BA shares new material or says "here are my notes". Tiếng Việt: tiếp nhận ghi chú, email, tài liệu, ảnh chụp; trích xuất dữ kiện có nguồn, chọn hướng tiếp cận.
---

# /ba-intake — Capture and digest every source

> **Start:** `ba context <slug> ba-intake` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "1 Intake"`.

Goal: nothing the business said gets lost, and every later statement can cite where it came from.

## Steps

1. **Register sources.** For each new input (files in `sources/` not yet listed, or text pasted in chat):
   - Pasted text → save verbatim as `sources/SRC-NN-<short-name>.md` (never paraphrase raw input).
   - Add a row to the *Source register* in `01-intake.md`: ID, type, date, author/attendees, reliability
     (primary = decision-maker said it; secondary = second-hand; legacy = old document).
   - Images/PDFs: read them; transcribe relevant text and describe UI screenshots field by field.
   - Log `source.added` per source (`--refs SRC-NN`, summary: type and author).

2. **Extract, per source**, into `01-intake.md` (create from `templates/01-intake.md` on first run):
   - **Facts / statements** — atomic, each tagged `(SRC-NN)`.
   - **Actors** — people, roles, systems, external parties.
   - **Goals & desired outcomes** — including any numbers mentioned.
   - **Pain points** in today's process.
   - **Constraints** — deadlines, budget, technology, regulation, policy.
   - **Implicit requirements** — things stated as complaints or examples ("last week a customer had to call us
     three times") → convert to candidate needs, mark `(inferred)`.
   - **Terms** — business vocabulary to add to the glossary.

3. **Cross-check.** Compare all sources:
   - **Contradictions** — list both statements with sources, and who can resolve it → becomes a `Q-`.
   - **Duplicates** — merge, keep both citations.
   - **Gaps already obvious** — e.g. a role mentioned but never described.

4. **Stakeholders and governance.** Update the `STK-` table: name, role, interest, influence (H/M/L), what they
   can answer, **what they decide on**. Then fill `_status.md` → *Governance* from the sources — never by guessing:
   - **Business owner** — who funds the work and has the final say when stakeholders disagree.
   - **Product Owner** — who decides scope, story priority and acceptance.
   - **Area owners** — list every area the sources name (module, process, integration, report: e.g. "Culture
     module", "payroll file") and who owns its rules and data. An area with nobody named is a gap.
   - **Escalation path** and **gate approvers**.
   - **Role conflicts** — if the BA is also the PO or business owner, say so once and ask who reviews the BA's
     decisions (or that the BA accepts it, a `D-`).

4a. **Existing system knowledge.** If `ba context` lists a knowledge base for the system this feature changes
   (`knowledge/<system>/`, built by `/ba-discover`), register the **verified** pages you rely on as sources
   (`SRC-NN: knowledge/<system>/03-rules.md, verified <date>`) and cite its `KB-` rules instead of re-asking.
   Draft or stale pages are leads, not facts: confirm them like any other source. If there is none and the system
   is poorly documented, offer `/ba-discover <system>`.

4b. **Foundations.** Before any feature question, check the sources for each item below. Every one that is
   missing or vague becomes a **Decision-critical** `Q-` (asked first, of the business owner or PO, with
   options and a recommendation):
   | Foundation | Good enough when |
   |------------|------------------|
   | Problem and its cost today | who struggles, how often, what it costs (time, money, errors, complaints) |
   | Success metrics | each goal has a metric, a **baseline** (today's value, or "unknown — measure by <date>"), a **target** and a date |
   | Business owner and PO | named people (*Governance*) |
   | Area owners | one per area named in the sources |
   | Hard constraints | deadline, budget, law/policy, fixed technology — or "none" confirmed |
   Write them in `01-intake.md` → *Foundations* (status per row: Known (SRC-) / Asked (Q-)). Until they are
   answered, any MVP or priority suggestion is **provisional** — say so, and record it with "Revisit at: 3 Scope".

5. **Determine the approach.** `ba context <slug> ba-intake` lists every candidate's *Signals* and the catalogue;
   open `profiles/README.md` only for the combination rules (§5) and overrides (§6):
   - **Candidates** — every profile with `status: active` (built-in *and* custom, solution *and* modifier kinds),
     plus the entries in `profiles/catalogue.md`.
   - **Solution types** — match the extracted facts against each profile's *Signals*. Pick one **primary**
     (the type the main goal depends on) and any **secondaries**. Cite the evidence (`SRC-`) for each.
     If a **catalogue** entry fits better than any active profile, recommend installing it
     (`/ba-profile install <name>`) and continue with the closest active profile until the BA decides.
     If **nothing fits well**, say so and offer `/ba-profile new` (or an override on the closest profile).
   - **Work-type modifiers** — confirm or correct the type of work recorded by `/ba-start`
     (new product, change to existing system, regulatory, process-only), and apply any custom
     `kind: modifier` profiles whose signals match.
   - **Map profiles to scope** — which candidate capabilities each profile covers (refined to `IS-` in `/ba-scope`).
   - **Confidence** — High / Medium / Low. If Low, or signals conflict (e.g. "app" could mean web or mobile),
     raise a Blocking `Q-` with options and a recommendation, and keep the approach as *Proposed*.
   - **Stage plan** — combine the active profiles' *Stage plan* tables (rules in `profiles/README.md` §5) into
     one table: stage → Run / Adapted / Lite / Partial / Skip → output documents for this feature. Insert each
     profile's **extra stages** (§11) in the right position, marked "run with `/ba-step <id>`".
   - **Overrides** — ask the BA: "Anything you want different for this feature?" Record each as `O-NN`
     (rules in `profiles/README.md` §6) and apply it to the stage plan.
   - **Deliverables list** — the exact documents this feature will produce, including profile extras
     (e.g. `api-consumer-guide.md`, `ops-runbook.md`, `data-catalogue.md`, `eval-pack.md`, `release-notes.md`).
   Write all of this to `_status.md` → *Approach* (from the template), and a short *Approach* section in
   `01-intake.md` with the evidence. Present it to the BA as a one-screen summary and ask them to confirm;
   on confirmation record a `D-` and set the approach status to *Confirmed*.
   Log `approach.proposed` when you present it, `approach.confirmed` (with the `D-`) when the BA confirms,
   and `override.added` for each `O-`.

6. **Update `_status.md`**: sources count, stage = Intake, gate check:
   *every source registered and summarised; contradictions logged as questions; every foundation known or asked
   (Decision-critical `Q-`); approach confirmed (or its open question logged as Blocking)*. Close with
   `ba turn <slug> --events … --gate --stage "1 Intake"`.

> Re-run step 5 whenever new sources change the picture (e.g. "we'll also need a mobile app"). A changed
> approach after Scope is a change request → `/ba-change`.

## Output quality checks
- No statement without a `SRC-` tag.
- Inferences are labelled `(inferred)`, never presented as facts.
- Numbers and names are copied exactly.

## Finish with
- **Done:** N sources processed, X facts, Y actors, Z contradictions; proposed approach
  (primary + secondaries + modifiers) and the resulting stage plan and deliverables.
- **Needs your decision:** the foundation questions (Decision-critical) first; confirm the approach;
  contradictions you can resolve on the spot (offer options). Ask the answer mode if *Preferences* says `ask`.
- **Next step:** `/ba-elicit` to hunt the gaps.

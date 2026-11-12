---
name: ba-elicit
description: Gap analysis and elicitation for a requirements feature. Systematically finds what is missing, vague or contradictory using 12 gap lenses, then produces prioritised questions grouped by stakeholder (ready to send), interview/workshop agendas, and records answers as decisions. Use after intake, when answers come back from stakeholders, or when the BA asks "what am I missing?". Tiếng Việt: tìm khoảng trống, đặt câu hỏi cho stakeholder theo từng người, ghi nhận câu trả lời.
---

# /ba-elicit — Find the gaps, ask the right people

> **Start:** `ba context <slug> ba-elicit` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "2 Elicit"`.

## Mode A — Hunt gaps (default)

1. Start from `ba context <slug> ba-elicit` (open items, governance, the profiles' §3 questions). Open
   `01-intake.md` and later artifacts only where a lens needs the detail.
2. Apply **every lens** in `checklists/gap-lenses.md`. For each lens, decide: covered / partially / missing.
   Do not skip a lens because it "probably doesn't apply" — say why it doesn't.
   Lens 1 (*Why & value*) and lens 2 (*Who*, including who decides) come first: unanswered foundations from
   intake stay **Decision-critical** and are asked before anything else.
   Then apply the **Extra gap questions** of every active profile (§3, in `ba context`), limited to the scope
   that profile covers. Tag these questions with the profile name.
   If the approach is still *Proposed*, its confirming question goes first.
3. For each gap, write a question in `02-questions.md` (from `templates/02-questions.md`):
   - `Q-NNN` · lens · the question · **why it matters** (what breaks if we guess wrong)
   - **Options with a recommendation** where possible (BAs and POs answer faster when choosing)
   - **Follow-ups inside the options**: if picking an option would raise another question, ask it there and
     then ("(b) escalate ★ — to whom, after how many working days?"), so the answer closes the gap in one go
     instead of opening the next round
   - Priority: **Blocking** (can't write stories/spec without it) · **Decision-critical** (the answer changes
     scope, the MVP or who decides — success metrics, owners, conflicts between stakeholders) · **Important** ·
     **Nice to know**
   - Who can answer (`STK-`) · status `Open`
4. Where a sensible default exists and risk is low, propose an **assumption** `A-NNN` instead of a question,
   with risk level. High-risk assumptions must also have a question.
5. **One round, fixed up front.** Finish steps 2–4 completely before asking anything: the round is every
   open Blocking, Decision-critical and Important question, grouped by who answers, highest priority first.
   Nice to know is parked (`--all` includes it). Don't store packs in `02-questions.md`. Deliver the round in the
   **answer mode** from *Preferences* (ask once if it says `ask`, and save the choice):
   - **walkthrough** — `ba answers new <slug> --chat` prints the round in the order to ask it (run it once, at
     the start of the round; it numbers the questions). Tell the BA its size ("Round 2: 24 questions, 5 at a
     time"), then present *Questions per message* (Preferences, default 5) at a time with options and your ★,
     each message headed "Questions 6–10 of 24". Record each batch's answers (Mode B) and continue with the next
     batch. The BA may skip (it stays open for the next round) or say "★ for the rest" (record the remaining
     recommendations as their decisions, with the BA as who decided). New questions raised by answers:
     Blocking and Decision-critical ones join the next message ("Questions 11–15 of 26 — 2 new from your
     answers"); Important ones wait for the next round.
   - **file** — `ba answers new <slug> --who "<name>"` (one form per person, or `--ids` for a set); tell the BA
     the file path(s), then wait for **"done"**.
   - More than ~15 questions for one person → recommend **file** mode (or a workshop) for that person.
   - More than 5 Blocking or Decision-critical questions for one group, or two owners disagree → suggest a
     45-minute workshop (objective, attendees — the business owner for conflicts — timeboxed topics, decisions
     needed).

## Mode B — Record answers

When the BA pastes answers, says "STK-02 replied …", or says **"done"** after filling an answer form:
1. Pasted reply → save it verbatim as `sources/SRC-NN-...`. Answer form → `ba answers read <slug>` prints the
   answers compactly and files the form as the next `SRC-` (don't open the form yourself). Register the source
   in `01-intake.md` (log `source.added`). For each answered **Blocking** or **Decision-critical** question log `question.answered`; for each new
   `D-` log `decision.recorded` with who decided as `--actor`.
2. For each answered question: status → `Answered`, record the answer, and create a
   `D-NNN` decision (what, who decided, date, source) in `_status.md` → *Decision log*. Check the person had
   that right (*Governance*): an area owner decides their area; a conflict between owners goes to the business
   owner — record it as a Decision-critical `Q-` for them, not as a `D-`.
3. Confirm or reject assumptions touched by the answer.
4. **Check for new gaps the answer created** (answers often open new questions) and add them.
5. If an answer affects an artifact already written (scope, stories, spec), list the affected IDs and
   offer to update them (or suggest `/ba-change` if the feature is already approved).
6. **Track convergence.** Increase *Elicitation round* in `_status.md` → *Preferences* (round 1 = first pack
   sent). Report: questions opened vs closed this round, open assumptions by risk (`ba context` / `ba turn` output).
   Then `ba questions archive <slug>` moves the closed rows to `02-closed.md` so later stages read less.
   Answers usually raise new questions; if every round opens more than it closes, the feature never reaches handoff.

## Converging (from round 3, or whenever a round opens more questions than it closes)
Offer the BA a **scope-freeze** card instead of another open-ended round:
```
🧊 Round 3 — opened 14, closed 9. Open: 2 Blocking · 1 Decision-critical · A: High 1 · Medium 24 · Low 36
Recommend: freeze scope and close out
 1 Ask only Blocking + Decision-critical + High/Medium questions; park the rest as "Later" (Nice to know → backlog)
 2 Ask the PO to accept the Low assumptions in bulk (D- listing them; they ride into every handoff pack)
 3 New capabilities raised by answers → out of scope for this release, unless the PO re-confirms scope
Choose: 1+2+3 · pick · keep eliciting
```
Record the choice as a `D-` and log `decision.recorded`. Bulk acceptance of Low assumptions is logged as
`approval.recorded` with the PO as `--actor` and the accepted IDs in `--refs`.

## Gate
No `Blocking` questions open, or the BA explicitly accepts proceeding with named assumptions, recorded as `D-`
with **"Revisit at: <stage>"** — the stage by which the assumption must be confirmed; later stage cards and
`/ba-next` raise it as a prerequisite. Decision-critical questions may stay open here; they block the Scope gate.

## Finish with
- **Done:** questions by priority, assumptions proposed, answers recorded.
- **Needs your decision:** quick-win questions the BA can answer themselves right now.
- **Next step:** the answer forms or walkthrough; meanwhile `/ba-scope` can draft the non-blocked parts.

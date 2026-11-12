# Definition of Ready

## Feature level (checked by `/ba-review` before `/ba-handoff`)

- [ ] Problem statement agreed and cited
- [ ] Every goal `G-` is SMART (metric, baseline, target, date, measurement method)
- [ ] Governance named: business owner, PO, an owner for every area in scope, escalation path; role conflicts
      reviewed or accepted (`D-`)
- [ ] Every `IS-` serves a goal (or is mandatory, with its source) and has an owner; MVP justified by the goals
- [ ] In-scope and out-of-scope lists confirmed by PO (`D-` recorded)
- [ ] All actors and roles identified; permissions matrix has no empty cells
- [ ] Main flows modelled with all decision outcomes; every lifecycle entity has a state machine
- [ ] UI features: every UI story mapped to a screen `SCR-` with wireframe, elements and all states;
      accessibility target set; heuristics check done — or UX marked N/A with a reason
- [ ] Business rules catalogued with examples / decision tables; every rule cites `SRC-`/`D-`/`A-`
- [ ] No behaviour, number or limit without a source, decision or registered assumption (grounding self-check done)
- [ ] `ba check` reports no FAIL
- [ ] Data dictionary covers every field referenced in AC
- [ ] All user-facing messages have exact text
- [ ] Integrations specify failure handling
- [ ] NFRs measurable, all categories considered
- [ ] No open **Blocking** or **Decision-critical** questions
- [ ] No open **High** or **Medium** assumptions; open **Low** ones accepted in bulk by the PO (`D-` listing their IDs)
- [ ] Traceability complete both ways (no orphan stories, no uncovered goals/scope items)
- [ ] Review verdict Pass (zero Critical, Majors owned, score ≥ 80) and team walkthrough (Dev + QA) recorded
- [ ] Dependencies on other teams/systems have owners and dates

## Story level

- [ ] **I**ndependent — can be built/delivered without waiting on an unbuilt story (or dependency stated)
- [ ] **N**egotiable — describes the need, not a UI/tech solution (unless a decision fixes it)
- [ ] **V**aluable — "so that" links to a goal `G-`
- [ ] **E**stimable — team could size it; no unknowns hidden inside
- [ ] **S**mall — fits in one iteration (size S or M)
- [ ] **T**estable — ≥3 Gherkin AC: happy, alternative, failure; boundaries where numbers exist
- [ ] Role is a named role from the matrix (not "user")
- [ ] Rules, fields and messages referenced by ID and defined in `07-spec.md`
- [ ] Every capability and value in the AC traces to `SRC-`/`D-`/`A-` (no "filler" behaviour)
- [ ] Concrete example values in AC
- [ ] Open items listed (none Blocking or Decision-critical)
- [ ] Traces to `G-`, `IS-`, and a source/decision

## Sprint level (checked in `/ba-refine`, per story selected for a sprint)

Each box is confirmed by the role in brackets — never by the assistant. A story that is not Ready enters the
sprint only with the PO's risk acceptance (`D-` naming the missing criteria, owner and date).

- [ ] Goal clear: "so that" points to a `G-` the PO confirms (BA + PO)
- [ ] Every main behaviour has an AC with an ID (BA)
- [ ] Every AC is testable: Given/When/Then can be set up and observed (QA)
- [ ] No open Blocking or Decision-critical question on the story (BA)
- [ ] Dependencies named, with owner and status (Dev / Tech Lead)
- [ ] Test data and environment exist or are planned (QA)
- [ ] Every AC has its row in `rtm.md` (`ba rtm`) (BA)
- [ ] Fits one sprint, by the team's own estimate (team)

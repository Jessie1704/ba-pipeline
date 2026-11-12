# ID conventions

Mandatory: traceability depends on them. Summary in MANUAL §3.

| Prefix | Meaning | Example |
|--------|---------|---------|
| `SRC-` | Source document / conversation | `SRC-03` |
| `G-`   | Business goal / objective | `G-01` |
| `STK-` | Stakeholder | `STK-02` |
| `Q-`   | Open question | `Q-014` |
| `A-`   | Assumption (unconfirmed) | `A-005` |
| `D-`   | Decision (confirmed, with who/when) | `D-007` |
| `R-`   | Risk | `R-02` |
| `BR-`  | Business rule | `BR-012` |
| `IS-`  | In-scope capability | `IS-04` |
| `EP-`  | Epic | `EP-02` |
| `US-`  | User story | `US-021` |
| `AC-`  | Acceptance criterion (`AC-021.3` = story 21, criterion 3) | `AC-021.3` |
| `NFR-` | Non-functional requirement | `NFR-04` |
| `MSG-` | User-facing message (exact text in `07-spec.md`) | `MSG-03` |
| `SCR-` | Screen (in `06-ux.md`) | `SCR-04` |
| `TS-`  | Test scenario (in `handoff/qa-pack.md`) | `TS-017` |
| `CR-`  | Change request | `CR-01` |
| `O-`   | Approach override for one feature | `O-02` |

IDs are never reused or renumbered. Deleted items are marked `~~US-009~~ (withdrawn, D-012)` — in the row
or heading where the item lived (for an AC, in its story's *Item / Detail* table). A renamed item keeps its
old ID as `~~AC-006.2b~~ → AC-006.7`. `ba check` accepts `~~ID~~` anywhere as the definition of a withdrawn ID.
Register cells use **canonical values first**, notes after: Priority `Blocking`/`Decision-critical`/`Important`/`Nice to know`;
Risk `High`/`Medium`/`Low`; Status `Open`/`Answered`/`Confirmed`/`Rejected`/`Withdrawn`/`Closed` — e.g.
`Rejected — SFTP yes, volume 2,000 (D-038)`. `ba check` FAILs on anything else, so nothing hides in formatting.
**Always list IDs explicitly** (`US-003, US-004, US-005`) — never as ranges (`US-003 … US-005`); ranges hide
IDs from traceability checks. Every `A-` and `Q-` lives in one register: `02-questions.md`, with closed rows archived in `02-closed.md`
(`ba questions archive`).

## Workflow terms

| Term | Meaning |
|------|---------|
| Business owner | Funds the work; final say when stakeholders disagree |
| Area owner | Decides the rules and data of one module, process or integration |
| Foundations | Problem and its cost, success metrics (baseline, target), business owner, PO, area owners, hard constraints |
| Decision-critical | The answer changes scope, the MVP or who decides; blocks the Scope gate |
| Round | One complete set of questions, fixed before the first is asked (*Elicitation round*) |

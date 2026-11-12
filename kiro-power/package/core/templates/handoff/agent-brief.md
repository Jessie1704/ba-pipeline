# Build Brief — <Feature name>

**Version:** vX.Y · **Status:** Approved (`D-NNN`) · **Generated:** YYYY-MM-DD

> **Instructions to the builder (AI agent or developer)**
> - This brief is self-contained. Implement exactly what it says; do not add unrequested features.
> - If anything is missing, contradictory or listed under *Do not guess*, **stop and ask** — do not invent behaviour.
> - Reference requirement IDs in code comments where behaviour is non-obvious, and in test names
>   (e.g. `test_AC_021_3_rejects_refund_after_30_days`).
> - Done = every acceptance criterion below passes as an automated test and all NFRs are met.

## Skipped stages & known gaps
<Remove if none. Stage · reason · what it would have defined. Do not assume anything a skipped stage would have
defined — ask instead.>

## What changed in this version
<only for v1.1+: list of changed / added / withdrawn IDs with CR reference>

## 1. Context
<5 lines: problem, users, goal metric, where this fits in the product.>

## 2. Glossary
| Term | Meaning |
|------|---------|

## 3. Scope
**Build:** …
**Do NOT build:** …

## 4. Domain model, states, permissions
<Mermaid ER + state diagrams; permission matrix>

## 5. Business rules
<Full BR catalogue with decision tables>

## 6. Data dictionary
<Per entity>

## 7. Messages (exact text)
| ID | Trigger | Text |
|----|---------|------|

## 7b. Screens (UI features only)
<Navigation map, then per SCR-: wireframe, elements table, states, responsive & accessibility notes.
Build the layout and states exactly as listed; visual styling follows the named design system.>

## 8. Integrations
<Contracts, mapping, failure handling>

## 9. Stories — in implementation order
### Step 1 — US-NNN <title>
Depends on: –
<story + full Gherkin AC>

## 10. Non-functional constraints
| ID | Constraint | How to verify |
|----|-----------|---------------|

## 11. Assumptions you may rely on
- A-NNN …

## 12. Do not guess — ask first
- Q-NNN … (owner, expected date)

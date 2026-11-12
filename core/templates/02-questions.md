# 02 · Questions & Gap Analysis — <Feature name>

## Gap lens coverage
| # | Lens | Status (Covered/Partial/Missing/N/A) | Note |
|---|------|------|------|
| 1 | Why & value | | |
| 2 | Who | | |
| 3 | Scope edges | | |
| 4 | Process & triggers | | |
| 5 | Alternatives & exceptions | | |
| 6 | States & time | | |
| 7 | Rules & calculations | | |
| 8 | Data | | |
| 9 | Permissions & security | | |
| 10 | Integrations & dependencies | | |
| 11 | Experience & communication | | |
| 12 | Operate & measure | | |

## Question log
Priority: **Blocking** — nothing can be built without it (blocks the Elicit gate) · **Decision-critical** — the
answer changes what is in scope, the MVP or who decides (blocks the Scope gate; foundation questions are this) ·
**Important** — needed for a complete spec; may stay open with an `A-` · **Nice to know**. Closed rows move to `02-closed.md` with
`ba questions archive`; the register is both files.

| ID | Lens | Question | Why it matters | Options (★ = recommended) | Priority | Ask | Status | Answer / `D-` |
|----|------|----------|----------------|---------------------------|----------|-----|--------|---------------|

## Assumptions
> **Single register** for every `A-` in this feature — including values proposed in `07-spec.md` §11 and
> anything flagged `⚠ A-NNN` in stories. Other files reference the ID only. `ba check` *register* enforces this.

| ID | Assumption | Reasoning | Risk (H/M/L) | Status (Open/Confirmed/Rejected) | Linked Q |
|----|-----------|-----------|--------------|----------------------------------|----------|

## Sending questions
Not stored here — generate them when needed:
- **Answer form** for one person or a set of questions: `ba answers new <slug> --who "<name>"` (or `--ids Q-…`) →
  `answers/round-NN.md`. They tick options or write answers, save, and say "done"; `ba answers read <slug>`.
- **Workshop** (when more than 5 Blocking or Decision-critical for one group, or two owners disagree): objective, attendees (include the
  business owner for conflicts), 45 min agenda, decisions needed — in the chat or the meeting invite.

---
name: small-change
title: Small change / enhancement
kind: solution
origin: catalogue
version: 1.1
owner: BA practice
status: active
---

# Profile: Small change / enhancement

## 1. Signals
A ticket rather than a project: "small fix", "just add a field", "change the wording", "extend the rule to…",
one screen, one rule, one report or one job affected; expected 1–5 stories; existing system already documented.

**Not this profile when:** more than ~5 stories emerge, a new role or new entity is introduced, an
integration changes, or money/security/compliance behaviour changes → switch to the matching full profile
(re-run `/ba-intake` step 5). Scope creep beyond these limits is itself a finding to raise with the PO.

## 2. Stage plan
| Stage | Plan | Notes |
|-------|------|-------|
| Intake / Elicit / Scope | Lite | One combined pass: change summary, affected areas, 3–8 questions, in/out in a few bullets |
| Model | Lite | Only the affected flow fragment or state transition, before and after |
| Stories | Run | 1–5 stories, full Gherkin AC (no shortcut on testability) |
| UX | Partial | Only if a screen changes: before/after wireframe of that screen and its affected states |
| Spec | Lite | Only the *Change summary* section plus changed rules, fields and messages |
| Review | Lite | Mechanical checks + reviewer on changed items and their neighbours |
| Handoff | Adapted | `agent-brief.md` + `qa-pack.md` (with regression checklist); others only if needed |

## 3. Extra gap questions
**Foundations, relaxed** (MANUAL rule 3): ask only what a small change needs.
- **Business owner** — the PO stands in; write `= PO (small-change)` in *Governance*. Ask for a separate
  business owner only if another team or budget holder is affected.
- **Success metric** — optional: the PO may waive it with a `D-` ("no metric: wording fix"). The *why now*
  question below is still asked and its answer is the goal (`G-`).
- **Area owner** — the PO, unless the changed screen, rule, report or job belongs to another team: then that
  team's owner is named and confirms the change.
- **Hard constraints** — only the release date, if there is one.
- **MVP by value** — not filled: the whole change is one slice.

- What exactly changes? Describe **before** and **after** with one concrete example.
- What must **not** change? (behaviour others rely on)
- Who else uses this screen, rule, field, report or job? Other teams, integrations, exports?
- Does existing data need to be updated, back-filled or left as is?
- Does the change apply to records created before the release, or only new ones?
- Are reports, notifications, help texts or training materials affected?
- Is a feature flag or gradual rollout needed? Rollback if it goes wrong?
- Why now — what is the cost of not doing it (to confirm it's worth the change)?

## 4. Model
Before/after fragment only: the affected flow steps or state transitions as a small Mermaid diagram, or a
two-column table "Before | After". No full domain model; link to existing documentation instead.

## 5. Stories
Standard user stories, ≤ 5. Each AC set must include at least one **regression AC** proving unchanged
behaviour still works (`Given … when … then (unchanged) …`). Title starts with the verb of the change
("Extend…", "Rename…", "Allow…").

## 6. UX
Partial — only changed screens: before/after wireframe and the states that change. N/A otherwise.

## 7. Spec sections to add
```markdown
## Change summary
| # | Item (screen / rule / field / message / report / job) | Before | After | Reason | Story |
|---|--------------------------------------------------------|--------|-------|--------|-------|

## Impact & regression
| Area | Impacted? (Yes/No/Check) | How | Regression check |
|------|--------------------------|-----|------------------|
| Other screens using the same data | | | |
| Reports / exports | | | |
| Integrations / APIs | | | |
| Notifications / messages | | | |
| Existing records | | | |
| Permissions | | | |

## Rollout
| Topic | Decision |
|-------|----------|
| Applies to existing records? | |
| Feature flag / phased rollout | |
| Data fix / back-fill | |
| Rollback | |
```

## 8. NFR focus
Only NFRs the change touches; state explicitly "No NFR impact" otherwise. Always confirm performance is not degraded on the changed path.

## 9. Handoff extras
- `agent-brief.md` — short form: change summary, changed rules/fields/messages, stories with AC, do-not-change list.
- `qa-pack.md` — scenarios for the change + **regression checklist** from *Impact & regression*.
- `team-summary.md` and `po-approval.md` only if users or other teams will notice the change (decide at intake).
- Release note line (one or two sentences) appended to `_status.md` → *History*.

## 10. Review checks
- Every change has before, after and reason.
- Impact table complete (no blank "Impacted?" cells); each "Yes" has a regression check.
- Each story has a regression AC.
- Story count ≤ 5 and no new role/entity/integration — otherwise flag "outgrew small-change" as Major.

## 11. Extra stages
None.

---
Changelog: 1.0 — installed from catalogue. 1.1 — relaxed foundations: the PO stands in as business owner,
success metric optional (waived by `D-`), no *MVP by value* table.

# <Feature name> — Status

| Field | Value |
|-------|-------|
| Slug | `<feature-slug>` |
| Why (one line) | |
| Type of work | new product · new feature · enhancement · defect · technical change · compliance · process-only |
| Approach | <primary profile> + <secondaries> (see *Approach*) |
| Product Owner | <name> — see *Governance* |
| BA | |
| Builders | AI coding agent · in-house team · vendor — stack: |
| Target date / release | |
| Current stage | 0 Start |
| Status | Draft · In review · Ready · Approved · Changed |
| Version | v0.1 |
| Last updated | YYYY-MM-DD |

## Next action
> <single most important next step and who owns it>

## Preferences
| Setting | Value |
|---------|-------|
| Stage prompts | on-deviation · always · never |
| Mode | quick · standard · controlled |
| Language | en · vi |
| Elicitation round | 0 |
| Answer mode | ask · walkthrough · file |
| Questions per message | 5 |
| UAT thresholds | — (the PO may set e.g. coverage 100, pass 95) |

## Gates
Result: Passed · Failed · Skipped (O-NN) · Deferred · –  ·  👤 = human gate in the standard mode (closed by the approver)
| Stage | Gate | Result | Date | Notes |
|-------|------|--------|------|-------|
| 1 Intake | Sources registered & summarised; foundations asked (why, success metrics, who decides); approach confirmed | – | | |
| 2 Elicit | No Blocking questions open | – | | |
| 3 Scope | 👤 No Decision-critical open; every IS- has a goal and an owner; PO confirmed scope (`D-`) | – | | |
| 4 Model | Flows, states, permissions complete | – | | |
| 5 Stories | INVEST + ≥3 AC each, scope covered | – | | |
| <extra stages> | Gate defined in the profile's §11 | – | | |
| 6 UI/UX | UI stories → screens with all states, or N/A (reason) | – | | |
| 7 Spec | No undefined refs; NFRs measurable | – | | |
| 8 Review | 👤 No Critical; Majors owned; score ≥ 80; team walkthrough (Dev + QA) | – | | |
| 9 Handoff | 👤 Packs generated; every AC in the RTM; PO approval | – | | |
| 10 Refine | 👤 Every story in the sprint meets the Definition of Ready (team + PO confirmed) | – | | |
| 11 Test/UAT | 👤 RTM: every AC has a test with a real result and evidence; acceptance decision by the approver | – | | |
| 12 Release | 👤 Scope reconciled with the RTM; known issues owned; handover accepted | – | | |

## Open items snapshot
| Type | Open | Blocking / High-risk |
|------|------|----------------------|
| Questions `Q-` | 0 | 0 |
| Assumptions `A-` | 0 | 0 |
| Risks `R-` | 0 | 0 |

## Approach
**Status:** Proposed · Confirmed (`D-`) · **Confidence:** High / Medium / Low

| Profile | Role | Covers (scope) | Evidence |
|---------|------|----------------|----------|
| e.g. `web-app` | Primary | <IS-nn, IS-nn> | <SRC-nn> |
| e.g. `integration` | Secondary | <IS-nn> | <SRC-nn> |
| e.g. Change to existing system | Modifier | all | <SRC-nn> |

### Stage plan
| Stage | Plan (Run / Adapted / Lite / Partial / Skip) | From profile / override | What's different for this feature | Output documents | Command |
|-------|----------------------------------------------|-------------------------|-----------------------------------|------------------|---------|
| 4 Model | | | | `04-model.md` | `/ba-model` |
| 5 Stories | | | | `05-stories.md` | `/ba-stories` |
| 5a <extra stage, e.g. vendor-eval> | Run | cots-saas | | `05a-vendor-eval.md` | `/ba-step vendor-eval` |
| 6 UI/UX | | | | `06-ux.md` / N/A | `/ba-ux` |
| 7 Spec | | | profile spec sections to add: … | `07-spec.md` | `/ba-spec` |
| 8 Review | | | | `08-review.md` | `/ba-review` |
| 9 Handoff | | | | `handoff/…`, `rtm.md` | `/ba-handoff` |
| 10 Refine | | | | `10-refinement.md` | `/ba-refine` |
| 11 Test/UAT | | | | `11-uat.md` | `/ba-uat` |
| 12 Release | | | | `12-release.md` | `/ba-release` |

### Overrides
| ID | Target (stage / section / document) | Change | Reason | Decision |
|----|-------------------------------------|--------|--------|----------|

### Deliverables
- [ ] `handoff/po-approval.md`
- [ ] `handoff/agent-brief.md`
- [ ] `handoff/qa-pack.md`
- [ ] `handoff/team-summary.md`
- [ ] `handoff/traceability.md`
- [ ] <profile extras, e.g. `handoff/design-brief.md`, `handoff/ops-runbook.md`>
- [ ] <formal documents if the organisation needs them: `docs/brd.md`, `docs/urd.md`, `docs/user-guide-<role>.md`>

## Initial notes from /ba-start
- <BA's first view of the type of work, before sources were read>

## Stakeholders
| ID | Name | Role | Interest | Influence | Can answer about | Decides on |
|----|------|------|----------|-----------|------------------|------------|

## Governance
Who decides. Filled at intake (foundation questions); `ba check` *governance* FAILs from Scope on if the business owner
or the PO is not named. One row per area (module, process, integration) that has its own owner.
| Role | Who (STK-) | Decides on | Source |
|------|-----------|------------|--------|
| Business owner (final say in conflicts) | | Priorities and conflicts between stakeholders; funds the work | |
| Product Owner | | Scope, story priority, acceptance | |
| Area owner: <area> | | Rules and data of <area> | |
| Gate approvers | | Scope (3), Review (8), Handoff (9): PO · Ready (10): team + PO · Acceptance (11): business approver · Release (12): receiver | |
| Escalation path | | <area owner> → PO → business owner | |
| Role conflicts | none | e.g. BA is also PO: name who reviews the BA's decisions, or accept it (`D-`) | |

## Decision log
| ID | Decision | Decided by | Date | Source | Affects | Revisit at |
|----|----------|------------|------|--------|---------|-----------|

## Assumptions
Register: `02-questions.md` → *Assumptions*. Snapshot here: total open, High-risk open (IDs).

## Risks
| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|-----------|--------|-----------|-------|

## Review score history
| Date | Score | Verdict | Critical | Major | Minor |
|------|-------|---------|----------|-------|-------|

## Change log
| CR | Request | Requester | Date | Decision (`D-`) | Version |
|----|---------|-----------|------|-----------------|---------|

## History
- YYYY-MM-DD — Feature created.

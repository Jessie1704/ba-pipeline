---
name: cots-saas
title: Buy / configure a product (COTS / SaaS)
kind: solution
origin: catalogue
version: 1.0
owner: BA practice
status: active
---

# Profile: Buy / configure a product (COTS / SaaS)

## 1. Signals
"Buy rather than build", vendor, RFP/RFI/RFQ, tender, off-the-shelf, SaaS subscription, "implement Salesforce /
SAP / ServiceNow / Workday / Dynamics…", licence, configuration, customisation, partner/integrator.

**Two entry points:** (a) product **not yet chosen** → run both extra stages; (b) product **already chosen** →
skip `vendor-eval` with an override (`O-`, reason + `D-`) and start at `fit-gap`.

**Not this profile when:** only integrating with an existing vendor system (→ `integration`), or building
custom code on a platform with no package functionality being used (→ the matching build profile).

## 2. Stage plan
| Stage | Plan | Notes |
|-------|------|-------|
| Model | Run | To-be process **independent of any vendor**; capability map; integration context |
| Stories | Adapted | → **requirement list** (`REQ-` style: one capability per line, MoSCoW, weight, scenario) suitable for an RFP |
| *vendor-eval* | Run (extra) | After Stories — select a product |
| *fit-gap* | Run (extra) | After vendor-eval — map every requirement to the chosen product |
| UX | Skip | Product UI is given; configuration of layouts goes in the configuration workbook. Partial only if custom screens are built (then those screens only) |
| Spec | Adapted | → configuration workbook + integrations, data migration, roles/licences; custom extensions specified as normal stories |
| Review | Run | |
| Handoff | Adapted | RFP pack, fit-gap summary, configuration workbook, training & change plan |

## 3. Extra gap questions
- Has a product already been chosen, shortlisted, or is the market open? Any mandated vendors/platforms?
- Budget envelope: licences, implementation, run cost; contract length; pricing model preference?
- Decision makers and evaluation panel; procurement rules (tender thresholds, number of bids)?
- Hosting, data residency and security certifications required (ISO 27001, SOC 2…)?
- Which existing systems must it integrate with? Which systems will it replace?
- How much do we accept changing our process to fit the product vs customising the product?
- Customisation policy: configuration only / low-code extensions / custom code allowed?
- Data to migrate into the product? Historical depth?
- Users: number by role (drives licences), languages, locations?
- Vendor support expectations: SLA, support hours, roadmap influence, exit/portability (data export)?
- Implementation partner: vendor, integrator, or in-house?
- Go-live constraints: contract end of the current system, peak business periods to avoid?

## 4. Model
- To-be process (swimlanes), described in business terms, **without** vendor-specific screens or terms.
- **Capability map**: capability → sub-capabilities → requirement IDs (used for scoring).
- Integration context diagram: product in the middle, connected systems and data exchanged.
- Roles and approximate user counts per role (input to licensing).

## 5. Stories
Adapted to a **requirement list** in `05-stories.md`, vendor-neutral, RFP-ready:

| REQ ID | Capability | Requirement (one testable statement, "must") | MoSCoW | Weight (1–5) | Demo scenario | Source |
|--------|-----------|----------------------------------------------|--------|--------------|---------------|--------|

- Use `US-` IDs for the requirement rows (so traceability stays consistent); label the column "REQ".
- **Demo scenarios**: 5–10 end-to-end business scenarios vendors must demonstrate live, with sample data.
- Non-functional requirements go in the same list (category NFR) because vendors respond to them too.
- Custom extensions identified later in `fit-gap` become normal user stories with Gherkin AC.

## 6. UX
Skip — record "UX: N/A — product UI; layout configuration in workbook". Partial if custom screens are built.

## 7. Spec sections to add
```markdown
## Configuration workbook
| Config ID | Module / area | Setting | Value | Reason / rule | Requirement | Owner | Status |
|-----------|---------------|---------|-------|---------------|-------------|-------|--------|

## Roles, profiles & licences
| Business role | Product role / profile | Permission set | Licence type | Users | Cost / month |
|---------------|------------------------|----------------|--------------|-------|--------------|

## Extensions (custom build)
| Ext ID | Gap (from fit-gap) | Approach (low-code / code / workaround) | Stories | Upgrade risk |
|--------|--------------------|------------------------------------------|---------|--------------|

## Integrations
| Interface | Product ↔ System | Standard connector / custom | Data | Frequency | Owner |
|-----------|------------------|-----------------------------|------|-----------|-------|

## Data migration
| Object | Source | Volume | Migrate / archive / discard | Load method (product tool / API) |
|--------|--------|--------|------------------------------|----------------------------------|

## Commercial & contractual requirements
| Topic | Requirement |
|-------|-------------|
| SLA (availability, support response) | |
| Data ownership, export & exit | |
| Security certifications & audits | |
| Data residency | |
| Price protection / renewal terms | |
```

## 8. NFR focus
Security & certifications, Data residency & privacy, Availability SLA, Scalability (user growth, licensing),
Integration capability (APIs, limits), Upgradeability (impact of vendor releases on configuration/extensions),
Exit/portability.

## 9. Handoff extras
- `rfp-requirements.md` — for procurement/vendors: context, scope, requirement list (with MoSCoW, weights hidden
  or shown per procurement policy), demo scenarios, NFRs, commercial requirements, response format, timeline.
- `fit-gap-summary.md` — for the PO/steering group: fit %, gaps with decisions, extensions, workarounds, cost & risk.
- `config-workbook.md` — for the implementation team: the configuration workbook, roles/licences, integrations.
- `training-change-plan.md` — for business leads: process changes vs today, who needs training on what, comms.
- `agent-brief.md` only covers **extensions** (custom build); `qa-pack.md` covers demo scenarios as acceptance
  tests, configuration verification and extension tests.

## 10. Review checks
- Requirement list is vendor-neutral (no product names, screens or proprietary terms) before selection.
- Every Must requirement has a weight, a demo scenario or test, and a fit-gap result.
- Every gap has a decision (accept workaround / configure / extend / drop) recorded as `D-`.
- Extensions list upgrade risk; every extension has stories with AC.
- Licence counts reconcile with roles and user counts.
- Exit/data-export requirement present.

## 11. Extra stages
| Stage ID | Name | After stage | Purpose | Steps | Output document | Gate |
|----------|------|-------------|---------|-------|-----------------|------|
| vendor-eval | Vendor evaluation | 5 Stories | Choose the product objectively | see below | `05a-vendor-eval.md` | Selection decision recorded as `D-` with scores and rationale |
| fit-gap | Fit-gap analysis | vendor-eval | Map every requirement to the chosen product | see below | `05b-fit-gap.md` | Every requirement classified; every gap has a decision |

### vendor-eval — steps
1. **Criteria & weights**: from the requirement list (functional weight by MoSCoW × weight), plus NFR,
   commercial, vendor viability, implementation and support criteria. Agree weights with the PO **before** scoring.
2. **Long list → short list**: list candidates (from sources, BA, market knowledge — mark knowledge-based
   entries as `A-` to verify); apply knock-out criteria (must-haves, hosting, certification, budget). Keep 3–5.
3. **Demo scripts**: turn demo scenarios into scripts with sample data and scoring sheets.
4. **Scoring matrix**: criterion × vendor, score 0–5 with evidence (RFP response, demo, reference call).
   Never score from assumption — missing evidence = question to the vendor.
5. **Total cost of ownership** (3–5 years): licences, implementation, integrations, run, training, exit.
6. **Risks** per vendor (lock-in, roadmap, financial, partner capacity).
7. **Recommendation** with rationale and sensitivity check (would a different weighting change the winner?).

Template for `05a-vendor-eval.md`:
```markdown
## Criteria & weights
| Criterion | Category | Weight | Knock-out? |
## Short list
| Vendor / product | Why shortlisted | Knock-out result |
## Scoring
| Criterion | Weight | Vendor A (score · evidence) | Vendor B | Vendor C |
## Total cost of ownership (n years)
| Cost item | Vendor A | Vendor B | Vendor C |
## Risks
| Vendor | Risk | Likelihood | Impact | Mitigation |
## Recommendation & sensitivity
```

### fit-gap — steps
1. For every requirement: classify **Fit (standard)** · **Configure** · **Extend (low-code/code)** ·
   **Workaround (process change)** · **Gap (not possible)**, with evidence (vendor doc, demo, sandbox test).
2. Estimate effort (S/M/L) and upgrade risk for Configure/Extend.
3. For every Extend/Workaround/Gap: options with a recommendation; record decisions as `D-`.
4. Configure items → rows in the configuration workbook (`07-spec.md`). Extend items → new stories with AC.
   Workarounds → process changes in `04-model.md` and the training & change plan.
5. Summarise: % fit by MoSCoW, total extension effort, decisions needed.

Template for `05b-fit-gap.md`:
```markdown
## Summary
| MoSCoW | Fit | Configure | Extend | Workaround | Gap |
## Detail
| Requirement | Classification | Evidence | Effort | Upgrade risk | Option chosen | D- |
## Decisions needed
```

---
Changelog: 1.0 — installed from catalogue.

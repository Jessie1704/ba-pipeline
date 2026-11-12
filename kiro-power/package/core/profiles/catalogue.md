# Profile Catalogue — suggested profiles

Compact suggestions ready to install with `/ba-profile install <name>`, which expands an entry into a full
11-section profile. Edit freely before or after installing. Status column is updated on install.

Stage plan key: **R** Run · **A** Adapted · **L** Lite · **P** Partial · **—** Skip.
Intake, Elicit and Scope always run (L = lite).

## Overview

| # | Profile | Use when | Model | Stories | UX | Spec | Review | Extra stages | Status |
|---|---------|----------|-------|---------|----|------|--------|--------------|--------|
| 1 | `small-change` | Bug fix, tweak, small enhancement (≤ 5 stories) | L | R | P | L | L | — | **Installed** |
| 2 | `discovery` | Idea not yet validated; need evidence before building | L | A | P | — | L | hypotheses, experiment-plan | Suggested |
| 3 | `cots-saas` | Buying/configuring a product instead of building | R | A | — | A | R | vendor-eval, fit-gap | **Installed** |
| 4 | `workflow-approval` | Requests, approvals, case management, SLAs | R | R | R | R | R | — | **Installed** |
| 5 | `payments` | Checkout, payments, refunds, payouts, billing | R | R | R | R | R | security-review | Suggested |
| 6 | `identity-access` | Login, SSO, MFA, roles, user provisioning | R | R | P | R | R | threat-model | Suggested |
| 7 | `ai-agent` | AI that takes actions with tools, not just generates text | R | A | P | R | R | autonomy-review | Suggested |
| 8 | `conversational` | Chatbot or voice assistant (scripted or AI) | A | A | A | R | R | — | Suggested |
| 9 | `website-cms` | Marketing/content website, CMS, SEO | L | R | R | R | R | — | Suggested |
| 10 | `notifications` | Email/SMS/push messages, campaigns, alerts | A | R | P | R | R | — | Suggested |
| 11 | `data-migration` | Moving data from old to new system | A | A | — | A | R | data-profiling, cutover-plan | **Installed** |
| 12 | `legacy-modernisation` | Rebuilding/re-platforming an existing system | A | R | R | R | R | reverse-engineer, parity-matrix | Suggested |
| 13 | `rpa-automation` | Bots/low-code automating manual steps in existing apps | A | A | — | A | R | — | Suggested |
| 14 | `iot-device` | Connected devices, sensors, firmware + cloud | R | R | P | R | R | hardware-constraints | Suggested |
| 15 | `desktop-app` | Installed Windows/macOS/Linux application | R | R | R | R | R | — | Suggested |
| 16 | `process-redesign` | Changing how people work, little or no system change | A | — | — | A | L | change-impact | Suggested |

Suggested **modifiers** (`kind: modifier`): `multi-country` (localisation, tax, legal per country),
`multi-tenant` (tenant isolation, per-tenant config), `vendor-delivered` (contractual AC, acceptance testing,
stricter handoff), `high-security-pii` (threat model mandatory, privacy impact assessment),
`accessibility-critical` (public sector / WCAG AAA, assistive-tech testing), `fast-track` (all stages Lite,
review mandatory).

---

## 1. `small-change` — Small change / enhancement
- **Signals:** "small fix", "just add a field", one screen or rule, a ticket rather than a project.
- **Stage plan:** Model L (only the affected flow/state) · Stories R (1–5) · UX P (only changed screens) · Spec L (only changed rules, fields, messages) · Review L.
- **Key questions:** What exactly changes and what must stay the same? Who else uses this screen/rule/data? Any existing data affected?
- **Spec adds:** *Change summary* table — item · before · after · reason.
- **Handoff:** `agent-brief.md` and `qa-pack.md` only (+ regression checklist); skip team summary unless users notice the change.
- **Review checks:** before/after stated for every change; regression area named.

## 2. `discovery` — Discovery / idea validation
- **Signals:** "we think customers want…", no proven demand, new market, PO unsure of value.
- **Stage plan:** Model L (journey only) · Stories A (→ hypotheses, not stories) · UX P (prototype to test) · Spec — · Review L.
- **Extra stages:**
  - `hypotheses` after Scope → `03a-hypotheses.md`: problem/value/usability/feasibility hypotheses, riskiest assumption first. Gate: each hypothesis has a measurable success signal.
  - `experiment-plan` after `hypotheses` → `03b-experiment-plan.md`: experiment per hypothesis (interview, prototype test, fake door, concierge), audience, sample size, pass/fail threshold, duration. Gate: PO agrees thresholds.
- **Handoff:** `po-decision.md` (go / pivot / stop with evidence), `experiment-brief.md`; no agent brief.
- **Review checks:** no building commitments before evidence; thresholds numeric.

## 3. `cots-saas` — Buy / configure a product
- **Signals:** "buy", "vendor", "RFP", "off-the-shelf", "configure Salesforce/SAP/ServiceNow…".
- **Stage plan:** Model R (to-be process, independent of vendor) · Stories A (→ requirement list with MoSCoW and weights, RFP-ready) · UX — · Spec A (→ configuration workbook) · Review R.
- **Extra stages:**
  - `vendor-eval` after Stories → `05a-vendor-eval.md`: long list → short list, weighted scoring matrix, demo scripts per key scenario, reference checks, total cost of ownership. Gate: selection decision recorded.
  - `fit-gap` after `vendor-eval` → `05b-fit-gap.md`: each requirement → fit / configure / extend / workaround / gap, effort, decision. Gate: every gap has a decision.
- **Spec adds:** configuration workbook (setting · value · reason · requirement), integrations, data migration, licences/roles.
- **Handoff:** `rfp-requirements.md`, `fit-gap` summary, `config-workbook.md`, training & change plan.
- **Review checks:** requirements vendor-neutral before selection; every Must has a fit-gap result.

## 4. `workflow-approval` — Workflow, approvals & case management
- **Signals:** request, approve, reject, escalate, queue, SLA, assign, delegate, case.
- **Stage plan:** all R; Model emphasises state machines, SLAs and escalation.
- **Key questions:** approval levels and thresholds; delegation/out-of-office; SLA clocks (start, pause, stop); escalation chain; reassignment; parallel vs sequential approval; what happens on timeout.
- **Spec adds:** routing/assignment rules table; SLA & escalation matrix; approval matrix (amount × role); work-queue definitions.
- **Handoff:** supervisor guide (queues, SLAs, reassignment).
- **Review checks:** every state has an exit; every SLA has start/pause/stop events; no approval path without a fallback approver.

## 5. `payments` — Payments, checkout & billing
- **Signals:** pay, checkout, card, wallet, refund, invoice, subscription, payout, PSP name.
- **Stage plan:** all R; Model includes sequence diagram with the payment provider and payment state machine.
- **Extra stages:** `security-review` after Spec → `07a-security-review.md`: PCI scope, threat model (STRIDE) for payment flows, fraud rules, data storage. Gate: no card data stored outside the provider; every threat has a mitigation.
- **Spec adds:** payment state machine; refund/chargeback rules; currencies, rounding, fees, tax; reconciliation with provider; idempotency and duplicate-payment prevention.
- **NFR focus:** PCI-DSS, audit, availability during peaks, fraud monitoring.
- **Handoff:** finance reconciliation runbook; finance summary for approvals.
- **Review checks:** every failure (decline, timeout, duplicate callback) has AC; amounts have currency and rounding.

## 6. `identity-access` — Login, SSO, roles, provisioning
- **Signals:** login, sign-up, SSO, MFA, password, roles, permissions, onboarding/offboarding users.
- **Stage plan:** Model R (auth sequences) · Stories R · UX P (login/MFA/recovery screens) · Spec R · Review R.
- **Extra stages:** `threat-model` after Spec → `07a-threat-model.md`: assets, actors, attack paths (account takeover, privilege escalation), mitigations. Gate: High threats mitigated.
- **Spec adds:** authentication methods; password/MFA policy; session rules; role model & permission catalogue; joiner-mover-leaver provisioning; account lockout & recovery.
- **Handoff:** security pack for security team; admin guide.
- **Review checks:** deprovisioning defined; recovery flow can't bypass MFA; every role has an owner.

## 7. `ai-agent` — Agentic AI (takes actions)
- **Signals:** "the AI will do / book / update / send", tools, autonomy, agent, automation with judgement.
- **Stage plan:** Model R (agent loop, human checkpoints) · Stories A (task scenarios + golden set) · UX P (oversight/approval console) · Spec R · Review R.
- **Extra stages:** `autonomy-review` after Spec → `07a-autonomy-review.md`: per action — act alone / ask first / never; blast radius; reversibility; worst-case scenario. Gate: every irreversible action requires approval or has a documented exception with a `D-`.
- **Spec adds:** tool catalogue (tool, what it can do, limits, credentials scope); autonomy matrix; stop conditions; cost/time budgets; audit trail; escalation to human; plus `ai-feature` behaviour & evaluation sections.
- **Handoff:** `eval-pack.md` incl. misuse/prompt-injection cases; oversight runbook.
- **Review checks:** least-privilege tools; kill switch defined; every tool call logged.

## 8. `conversational` — Chatbot / voice assistant
- **Signals:** chatbot, virtual assistant, IVR, voice, WhatsApp/Teams bot.
- **Stage plan:** Model A (conversation flows / intents) · Stories A (conversation scenarios) · UX A (conversation design: persona, sample dialogues, fallback, human handover) · Spec R · Review R.
- **Spec adds:** intent/entity catalogue or topic list; channel specifics (rich cards, voice limits); handover rules; persona & tone; unsupported-request handling.
- **Handoff:** conversation script pack; `eval-pack.md` if AI-driven.
- **Review checks:** every flow has a fallback and a way to reach a human; sample dialogues cover failure.

## 9. `website-cms` — Content website / CMS
- **Signals:** website, landing pages, CMS, content editors, SEO, blog, marketing site.
- **Stage plan:** Model L (site map, content model) · Stories R (visitor + editor) · UX R · Spec R · Review R.
- **Spec adds:** content model (types, fields, relationships); editorial workflow & roles; SEO (meta, URLs, redirects, sitemap); analytics & consent; localisation.
- **Handoff:** content editor guide; redirect map.
- **Review checks:** every page template maps to a content type; redirects for changed URLs; cookie consent defined.

## 10. `notifications` — Messages & campaigns
- **Signals:** email, SMS, push, newsletter, reminders, alerts, templates.
- **Stage plan:** Model A (event → message matrix) · Stories R · UX P (template layouts) · Spec R · Review R.
- **Spec adds:** notification catalogue (event, audience, channel, template, timing, frequency cap, priority); consent & unsubscribe rules; personalisation fields; quiet hours; bounce handling.
- **Handoff:** template pack for marketing/legal approval.
- **Review checks:** every message has exact text, consent basis and opt-out.

## 11. `data-migration` — Data migration
- **Signals:** migrate, cutover, legacy data, import historical, decommission.
- **Stage plan:** Model A (source & target models, lineage) · Stories A (migration stories per data object) · UX — · Spec A (mapping & cleansing) · Review R.
- **Extra stages:**
  - `data-profiling` after Intake → `01a-data-profiling.md`: volumes, completeness, duplicates, invalid values per source object. Gate: profiling results reviewed with data owners.
  - `cutover-plan` after Spec → `07a-cutover-plan.md`: rehearsal runs, freeze window, step-by-step timeline, go/no-go criteria, rollback. Gate: go/no-go criteria agreed.
- **Spec adds:** object inventory; field mapping; cleansing & transformation rules; reconciliation checks; archive/retention of unmigrated data.
- **Handoff:** cutover runbook; reconciliation report template.
- **Review checks:** every source object has migrate/archive/discard decision; reconciliation per object.

## 12. `legacy-modernisation` — Rebuild / re-platform
- **Signals:** rewrite, replace old system, end-of-life, "same as today but…".
- **Stage plan:** Model A (as-is extracted from the old system) · Stories R · UX R · Spec R · Review R.
- **Extra stages:**
  - `reverse-engineer` after Intake → `01a-reverse-engineer.md`: extract existing behaviour from screens, reports, documentation and (if provided) code; list hidden rules. Gate: SMEs confirmed extracted rules.
  - `parity-matrix` after Stories → `05a-parity-matrix.md`: each existing function → keep / change / drop / new, with reason. Gate: every existing function has a decision.
- **Handoff:** parity matrix in `agent-brief.md`; regression and parallel-run plan in `qa-pack.md`.
- **Review checks:** no "same as today" without the rule written out.

## 13. `rpa-automation` — Bots / low-code automation
- **Signals:** RPA, bot, automate clicks, Power Automate, UiPath, manual copy-paste between apps.
- **Stage plan:** Model A (keystroke-level as-is, to-be bot flow) · Stories A (automation steps) · UX — · Spec A (process definition document) · Review R.
- **Spec adds:** application inventory & versions; step-level actions with selectors/screens; business & system exceptions; credentials handling; schedule & volume; human handoff on exception.
- **Handoff:** `pdd.md` (process definition document); bot operations runbook.
- **Review checks:** every exception has a handling path; credentials not embedded.

## 14. `iot-device` — Connected devices
- **Signals:** device, sensor, firmware, telemetry, gateway, Bluetooth, fleet.
- **Stage plan:** Model R (device states, device→cloud data flow) · Stories R · UX P (companion app) · Spec R · Review R.
- **Extra stages:** `hardware-constraints` after Scope → `03a-hardware-constraints.md`: power, connectivity, memory, environment, certification. Gate: constraints confirmed by hardware owner.
- **Spec adds:** device provisioning; telemetry catalogue; command catalogue; firmware update (OTA, rollback); connectivity loss behaviour; device security.
- **Handoff:** device integration brief; field operations runbook.
- **Review checks:** offline behaviour defined; OTA failure rollback defined.

## 15. `desktop-app` — Installed desktop application
- **Signals:** Windows/macOS app, installer, runs locally, files, peripherals (printer, scanner).
- **Stage plan:** all R; like `web-app` plus desktop specifics.
- **Spec adds:** supported OS versions; install/update/uninstall; offline use & sync; file system access; peripherals; multi-window behaviour.
- **Handoff:** install & deployment guide for IT.
- **Review checks:** update path and offline behaviour defined.

## 16. `process-redesign` — Business process change
- **Signals:** "how we work", procedure, roles & responsibilities, handoffs between teams, no new software.
- **Stage plan:** Model A (as-is & to-be, RACI) · Stories — (→ procedure steps) · UX — · Spec A (SOPs, controls, KPIs) · Review L.
- **Extra stages:** `change-impact` after Spec → `07a-change-impact.md`: who is affected, what changes for them, readiness, training needs, communication plan. Gate: impacted teams' leads reviewed it.
- **Handoff:** SOPs, RACI, training plan, communication pack; no agent brief.
- **Review checks:** every to-be step has an owner; controls cover the risks named in Scope.

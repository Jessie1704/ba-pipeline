# Credits

BA Pipeline (formerly BA Guardian Angel, 1.0 – 1.2) combines two earlier toolkits.

## BA Copilot (0.1 – 0.5)

The engine and the Define phase: the tool-neutral manual and stages, approach profiles, gap lenses, the
independent reviewer, the `ba` tooling (checks, `turn`, `context`, answer forms, the hash-chained audit trail),
the adapters and the installer. BA Pipeline continues it (its history is in CHANGELOG.md) and
upgrades BA Copilot projects in place.

## ba-workflow — Kiro Power `ba-agile-ai` 1.0 by toaidx1

<https://github.com/kakama89/ba-workflow> — used with the author's permission.

An Agile/Scrum business-analysis SOP with AI guardrails (BA-01 … BA-07, gates G1 – G4, six draft-only agents).
BA Pipeline adapts from it, rewritten for this workflow rather than copied:

| From ba-workflow | Where it lives in BA Pipeline |
|------------------|-------------------------------------|
| The ten mandatory guardrails; Fact / Assumption / Inference / Unknown labels; "AI output is a draft" | `core/MANUAL.md` §4a (one copy, not one per skill) |
| Human authority over gates and approvals; RACI per process | Human gates (`MANUAL.md` §8 step 5), enforced by `ba turn`; *Governance → Gate approvers* |
| BA-01 request types and shortened paths | `/ba-start` step 2b (request type → route → mode) |
| BA-04 refinement and the reference Definition of Readiness | `/ba-refine`, `templates/10-refinement.md`, `checklists/definition-of-ready.md` → *Sprint level* |
| BA-05 "return to the right control point" | `/ba-change` step 7 |
| BA-06 discrepancy classes (defect / requirement gap / change request), evidence rules, UAT report, acceptance decisions | `/ba-uat`, `templates/11-uat.md` |
| BA-07 release reconciliation, known issues with owners, KPIs (SOP §9), lessons learned | `/ba-release`, `templates/12-release.md`, `ba kpi` |
| RTM with test/UAT results, evidence, versions, Confirmed vs Inferred links | `ba rtm` / `rtm.md` and the *rtm* check |
| QA review: findings need evidence; proven defects vs risks to verify | `core/agents/requirements-reviewer.md`, `templates/08-review.md` |
| AI run log (prompt version, model) | `model`, `tool` and `reported_by` on every audit event |
| Vietnamese-first writing and bilingual triggers | *Language* preference, `core/README.vi.md`, Vietnamese stage triggers and ambiguity words |
| `ba-doc-brd`, `ba-doc-urd` (BRD and URD templates, their quality gates and stop rules) — added in BA Guardian Angel 1.1 | `/ba-docs`, `templates/docs/brd.md`, `templates/docs/urd.md` (mapped to this workflow's IDs and artifacts) |
| KPIs of SOP §9 (requirement completeness, AC testability, AI acceptance rate, AI unsupported claims) and the G4 pass-rate rule — added in BA Guardian Angel 1.1 | `ba kpi`; *UAT thresholds* preference |

### Not carried over, on purpose

| From ba-workflow | Why |
|------------------|-----|
| Six separate draft-only agent skills with their own output schemas | Their checks live in the stages and the independent reviewer; one reviewer in a fresh context replaces the in-session QA agent |
| The Excel-workbook column layouts and `validate_power.py` | The `ba` checks validate the project's own records instead; `ba export` produces Excel for stakeholders |
| `ba-records/<project>/` layout and the hand-filled AI run log | `requirements/<feature>/` and the hash-chained audit log, which records model, tool and reporter on every event |
| — | Kiro Power packaging was added in BA Guardian Angel 1.2 (`kiro-power/`, built by `tools/build_power.py`) |

### Licence

No open-source licence is granted: all rights are reserved by the repository owner. The material adapted from
ba-workflow is included with the permission of its author, toaidx1.

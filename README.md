# BA Pipeline

*Formerly BA Guardian Angel (1.0 – 1.2.1); projects on it or on BA Copilot upgrade in place — see the release notes.*

An AI-assisted business analysis workflow that runs in the AI tool you already use, from the first request to the
release. It turns messy inputs into **build-ready, approvable, readable requirements**, then helps prove — with
evidence — that what was built matches them. The AI drafts, checks and records; **people decide**, and the gates
that belong to a person are closed on that person's own recorded decision. The tools detect and flag what doesn't
fit — they don't make cheating impossible: keep the approvals themselves (emails, minutes) as sources.

**Version:** 1.0.0 (`VERSION`) · **Licence:** all rights reserved (no open-source licence) · **Changes:** [CHANGELOG.md](CHANGELOG.md) · **Release notes:**
[RELEASE_NOTES.md](RELEASE_NOTES.md) · **Tiếng Việt:** [README.vi.md](README.vi.md) · **Credits:** [CREDITS.md](CREDITS.md)

> **Using it as a BA?** Read the user guide: [core/README.md](core/README.md)
> ([tiếng Việt](core/README.vi.md)). It is installed into every project as `.ba/core/README.md`.

## What you get

| | |
|---|---|
| **A full lifecycle** | Define (start, intake, elicit, scope, model, stories, UX, spec, review, handoff) → Deliver (refine, test & UAT, release) → change requests at any time |
| **Formal documents** | `/ba-docs`: BRD, URD and end-user guides generated from the artifacts, cited and labelled, each with its own approval; a user guide only describes tested behaviour |
| **Learn an existing system** | `/ba-discover`: a shared, sourced knowledge base per system (landscape and who knows what, current processes and rules, data, glossary, open questions) with an onboarding brief; features cite verified pages |
| **Talk, don't memorise commands** | Requests in English or Vietnamese are routed to the right stage (`reference/routing.md`); ambiguous ones get one clarifying question; every stage ends with the next step |
| **Three modes** | *quick* for defects and small changes, *standard*, *controlled* for regulated or vendor work |
| **Human gates** | Scope, review, handoff, Definition of Ready, acceptance and release need the gate's approver (full name, a unique given name or `STK-` ID — Vietnamese names, forms of address and missing diacritics handled) and that person's own dated decision for this run; only the PO or business owner changes the mode, and editing the cell alone changes nothing; `ba check` FAILs a *Gates* table that disagrees with the log or can't be read; in the controlled mode the approver confirms with `ba approve` in an operating-system terminal |
| **AI guardrails** | Evidence labels (fact / assumption / inference / unknown); the AI never sets priority, estimates, severity, results or acceptance; drafts stay drafts until a person reviews them |
| **Gap hunting** | 12 gap lenses, profile-specific questions, questions with options and a recommendation, grouped by stakeholder; answer by chat or form |
| **Adapts to the work** | Profiles for web, mobile, API, integration, batch, data, AI, small change, workflow & approvals, SaaS, data migration, plus your own |
| **Independent review** | A fresh-context reviewer; every defect cites evidence; the verdict depends on defects, not on one score; a Dev + QA walkthrough before handoff |
| **Live RTM** | `ba rtm` keeps one row per acceptance criterion and test, with results, evidence and the person who recorded them; results without real evidence, or recorded by the assistant, fail the check; changed AC are re-tested; every result is kept in a result log |
| **Mechanical checks** | `ba check`: IDs, grounding, Gherkin, ambiguity (English and Vietnamese), open items, governance, RTM, handoff, documents, gates, audit — in seconds |
| **Tamper-evident audit trail** | Hash-chained log of decisions, approvals, gates and file changes, with the approver, the account that recorded it, the AI tool it ran from and the AI model |
| **For stakeholders** | `ba status` (plain-language, English or Vietnamese), an HTML dashboard, an Excel export, KPIs |
| **Any AI tool** | Claude Code, GitHub Copilot, Cursor, Gemini CLI, Kiro (as steering files or as a **Kiro Power**), and any tool that reads `AGENTS.md` (Codex and others) |

## Install into a project

Python 3.9+ (standard library only).

```bash
git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline
python ba-pipeline/install.py init   --target <project> --tools claude,agents-md --model <AI model>   # or: all
python ba-pipeline/install.py update --target <project>      # later, from a newer package
python ba-pipeline/install.py status --target <project>
```

- **init** copies `core/`, `tools/` and `VERSION` into `<project>/.ba/`, creates `.ba/local/` for your own
  templates, profiles and checklists, writes `.ba/config.json`, and generates the files your AI tools read.
- **update** shows the changelog since your version, replaces `core/` and `tools/`, keeps `.ba/local/` and the
  config, migrates every feature's `_status.md` (each migration recorded in its audit trail), refuses downgrades
  unless `--force`. **Projects on BA Copilot (0.x) upgrade in place.**
- `--dry-run` previews init and update. Start a **new session** in your AI tool afterwards.

Then open the project in your AI tool and say *"start a new feature"* (or `/ba-start`).

## Kiro: use it as a Kiro Power (no install)

The repository ships a self-contained **Kiro Power** in [`kiro-power/`](kiro-power/) (Agent Plugins layout:
`plugin.json`, 22 skills, plus `POWER.md` for Kiro's earlier power format). The workflow runs from the power's
`package/` folder; your project keeps only its data.

1. In Kiro: **Powers** panel → **Add Custom Power** → **Import power from GitHub** →
   `https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`
   (or clone the repository and use **Import power from a folder** → `kiro-power/`).
2. Open your project, start a normal (Vibe) chat — not Spec mode — and describe the work in English or Vietnamese
   (*"start a new feature: …"*, *"đây là ghi chú họp"*), or call a skill: `/ba-start`, `/ba-intake`, …
   Python 3.9+ must be installed; Kiro asks before running a command.
3. The first command the AI runs finds the power's package and saves its path in `.ba/config.json`
   (`ba where --save`), so later sessions find it straight away.
4. Optional: *"pin BA Pipeline in this project"* (**ba-setup**) copies the workflow into `.ba/` so the project
   keeps one version, and adds files for other AI tools.

After changing the package, rebuild the power with `python tools/build_power.py` (a test fails if the committed
power is out of date).

## Tools

```bash
python .ba/tools/ba.py check <feature> [--only status,ids,ranges,register,ground,gherkin,tables,ambiguity,open,governance,rtm,handoff,docs,gates,audit]
python .ba/tools/ba.py turn <feature> [--events <file|->] [--gate --stage "<n Name>"]   # once per turn: events, counts, file changes
python .ba/tools/ba.py context <feature> <stage>         # what a stage needs (incl. mode, human gates, RTM)
python .ba/tools/ba.py rtm <feature>                     # build/refresh rtm.md, the live traceability matrix
python .ba/tools/ba.py kpi <feature> [--json]            # release KPIs from the RTM and the audit log
python .ba/tools/ba.py status <feature> [--html FILE] [--lang en|vi]   # plain-language status / one-page dashboard
python .ba/tools/ba.py export <feature> [--out FILE.xlsx]               # registers, decisions, gates, AC, spec, RTM to Excel
python .ba/tools/ba.py approve <feature> --gate "8 Review" | --doc docs/brd.md | --mode quick --as "<name>" --decision D-NN
                                                         # the approver confirms, in their own terminal
python .ba/tools/ba.py where [--save]                    # which copy of the workflow this project uses (pinned or the power's)
python .ba/tools/ba.py discover <system>                 # create or show knowledge/<system>/ (learn an existing system)
python .ba/tools/ba.py answers new|read <feature> …      # answer forms for stakeholders
python .ba/tools/ba.py questions archive <feature>       # move closed questions to 02-closed.md
python .ba/tools/ba.py audit event|sync|verify|hook …    # the audit trail
```

Settings in `.ba/config.json`: `requirements_dir`, `tools`, optional `model` (recorded on every event; set with
`install.py --model`), `human_gates` (per mode, e.g. `{"standard": [3, 8, 9, 11]}`) and `knowledge_max_age_days`
(default 180). Environment: `BA_ROOT`, `BA_ACTOR`, `BA_MODEL`, `BA_VIA`, `BA_SESSION`.

## Layout

```
core/                         the workflow — installed as .ba/core/, replaced on update
  README.md, README.vi.md     user guide for BAs (English, Vietnamese)
  MANUAL.md                   rules the AI follows (§0 maps its terms to any tool; §4a AI guardrails)
  stages/ba-*.md              20 stage playbooks (13 stages + docs, discover, change, next, step, profile, audit)
  agents/requirements-reviewer.md
  reference/                  IDs, audit, checks, routing (English and Vietnamese examples)
  templates/                  stage templates; docs/ (BRD, URD, user guide); knowledge/ (system knowledge base)
  checklists/ profiles/ glossary.md
tools/ba.py                   checks, RTM, KPIs, status, export, audit trail
tools/adapters.py             per-tool files (Claude Code, AGENTS.md, Copilot, Cursor, Gemini, Kiro)
tools/build_power.py          builds kiro-power/ (the Kiro Power) from the package
kiro-power/                   the Kiro Power: plugin.json, POWER.md, skills/ (22, playbooks inline), package/ (the workflow)
install.py                    init · update · status (version pin, overrides, migrations)
adapters/CAPABILITIES.md      what each tool gets; format confidence; degraded-but-safe behaviour
examples/requirements/expense-claims/   a fictional pilot, used as a test fixture
tests/                        202 tests
```

## Development

```bash
python -m unittest discover -s tests -v
```

Tests run on throwaway copies of `examples/`. Keep the example's `ba check` free of FAIL; if a rule changes on
purpose, update the example and the tests together. Keep LF line endings (`.gitattributes` sets `-text`;
`core.autocrlf` must stay off) so the example's hash-chained audit log verifies after a clone.

## Status and limits

The workflow has been piloted on a fictional feature with simulated stakeholder answers (see the example), not
yet with real stakeholders and a real delivery team; the delivery stages (refine, UAT, release)
have test coverage for their tooling, not field experience. Three rounds of independent review were fixed
before this release. See *Known limitations* in
[RELEASE_NOTES.md](RELEASE_NOTES.md).

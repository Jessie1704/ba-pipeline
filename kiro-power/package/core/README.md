# BA Pipeline — how to use the workflow

BA Pipeline is an AI-assisted workflow for business analysts, from the first request to the release. You
bring the raw material (meeting notes, emails, policies, screenshots); the AI assistant in your tool turns it into
requirements that are:

- **build-ready** — a developer or AI coding agent can implement them without guessing,
- **approvable** — the Product Owner decides on one page,
- **readable** — every team member finds what their role needs quickly,

and then helps you **prove, with evidence, that what was built matches them** (refinement, test and UAT, release).

The AI drafts, checks and chases gaps. **People decide**: the AI recommends, the person with the right decides,
and every decision is recorded with their name. Some gates can only be closed by a named approver.

> Vietnamese: [README.vi.md](README.vi.md). This guide is for the BA. The rules the AI follows are in `MANUAL.md`
> (same folder) — you don't need to read it, but it explains *why* the AI does something.

---

## 1. Before you start

- BA Pipeline is installed in your project's `.ba/` folder (`.ba/VERSION` shows the version). If it isn't,
  see *Installing* at the end.
- Open the **project folder** in your AI tool (Claude Code, GitHub Copilot, Cursor, Gemini CLI, Kiro, Codex…).
- Start a **new chat/session** after installing or updating, so the tool loads the commands.
- Python 3.9 or newer must be installed (`python --version`); the AI uses it for checks, the RTM and the audit trail.

**Check it's working:** ask *"What workflow do you follow for requirements work here?"* — it should name
BA Pipeline and suggest starting with `ba-start`.

## 2. Quick start (first feature in 10 minutes)

1. **Start:** run `ba-start` and say what the request is, who the Product Owner is, and which language you want.
   *"New feature: refund self-service. PO is Anna Lee. It changes our existing customer portal. Vietnamese please."*
   The AI classifies the request (new feature, enhancement, defect…) and proposes a **mode** (quick, standard,
   controlled). Confirm it.
2. **Give it the material:** put your notes, emails and documents in `requirements/<feature>/sources/`, or paste them.
3. **Intake:** run `ba-intake`. It lists facts with their source, spots contradictions, and proposes an *approach*.
4. **Questions:** run `ba-elicit`. You get questions grouped by stakeholder, each with options and a recommendation.
5. Whenever you're unsure: `ba-next` tells you the single best next step; `python .ba/tools/ba.py status <feature>`
   gives a plain-language status you can paste to stakeholders.

## 3. How to run a stage in your tool

| Tool | Type |
|------|------|
| Claude Code | `/ba-intake` |
| GitHub Copilot (VS Code) | `/ba-intake` (prompt files) |
| Cursor | `/ba-intake` |
| Gemini CLI | `/ba-intake` |
| Kiro (Kiro Power) | just describe the work, or `/ba-intake` (skills of the power) |
| Kiro (installed steering files) | `#ba-intake` |
| Codex and other tools | *"run intake"* or just describe what you want |

You can always just say what you want (*"here are the answers from Finance"*, *"the build is ready for UAT"*) —
the AI maps it to the right stage with a routing table of English and Vietnamese examples
(`.ba/core/reference/routing.md`). Vietnamese works too (*"đây là ghi chú họp"*, *"chuẩn bị UAT"*). When a request
could mean two things (*"here's Linh's email"* after approval: answers or a change request?), the AI asks one
short question instead of guessing. Naming the stage always works.

Each stage ends with **Done**, **Needs your decision** and **Next step** (the exact command); `ba-next` tells you
the single best next action at any time. The AI suggests the next stage but doesn't start it on its own.

## 4. The journey

**Define** — from raw material to approved requirements:

| # | Stage | You give / do | You get |
|---|-------|---------------|---------|
| 0 | `ba-start` | Request, PO, language | `requirements/<feature>/` with a status page; request type and mode |
| 1 | `ba-intake` | Raw material | `01-intake.md`: facts with sources, actors, contradictions; the **approach** |
| 2 | `ba-elicit` | Send questions, paste answers | `02-questions.md`: questions, assumptions, decisions; ready-to-send packs |
| 3 | `ba-scope` | 👤 PO confirms | `03-scope.md`: problem, measurable goals, in/out of scope, risks |
| 4 | `ba-model` | Sanity-check | `04-model.md`: process flows, status lifecycles, data model, permissions |
| 5 | `ba-stories` | Prioritise | `05-stories.md`: user stories with Given/When/Then acceptance criteria |
| 6 | `ba-ux` *(only if there's a UI)* | Review screens | `06-ux.md`: journeys, screens, every screen state; optional prototype |
| 7 | `ba-spec` | Confirm rules and numbers | `07-spec.md`: business rules, data fields, exact messages, integrations, NFRs |
| 8 | `ba-review` | 👤 Review in a **new chat**; walkthrough with Dev + QA | `08-review.md`: defects with evidence, score, verdict |
| 9 | `ba-handoff` | 👤 PO approves | `handoff/` packs, `rtm.md` (live traceability), Excel copy |

**Deliver** — prove the build matches:

| # | Stage | You give / do | You get |
|---|-------|---------------|---------|
| 10 | `ba-refine` | 👤 Refinement session with PO, Dev, QA | `10-refinement.md`: Definition of Ready per story, splits, the team's estimates |
| 11 | `ba-uat` | 👤 Testers and business users run tests | `11-uat.md` + RTM results with evidence; defect / requirement gap / change request; the acceptance decision |
| 12 | `ba-release` | 👤 Receiver accepts the handover | `12-release.md`: scope reconciled, known issues with owners, KPIs, lessons learned |

👤 = a **human gate**: the AI prepares everything, then asks the approver. The tool only logs the gate when the
approver is named in *Governance*, the decision (`D-`) exists and was taken by that person, and the evidence is
cited; `ba check` FAILs a *Gates* row that says Passed without that record. The tool can't hear the meeting, so
keep the approval itself (email, minutes) as a source. Teams that hand over to another delivery process mark
10–12 *Skip*.

**Writing people's names.** Use the same name everywhere (*Stakeholders*, *Governance*, *Decided by*): the full
name or the `STK-` ID. "chị Lan Anh", "Lan Anh - PO", a name typed without diacritics and "PO" (in *Decided by*)
are understood; a given name counts only if no one else on the status page has it; a single word like "An" or
"Lan", or a family and middle name like "Nguyễn Thị", never counts. The person who approves is written by name or
`STK-`, never as "PO". Write dates as 2026-11-12 or 12/11/2026. *Gate approvers* can say who closes which gate: `3,8,9: STK-02; 11: STK-05`.

**`ba approve` — the approver confirms themselves.** In the controlled mode (and whenever you want the strongest
record), the approver runs, in their own terminal:
`python .ba/tools/ba.py approve <feature> --gate "8 Review" --as "Nguyễn Thị Lan Anh" --decision D-60`
and types their name to confirm. It is refused inside an AI tool's terminal (including Kiro's) and without a real
terminal: use Windows Terminal, PowerShell or macOS Terminal. It also approves a document (`--doc docs/brd.md`, pinned to its content) or a
mode change (`--mode quick`). The AI tool can't run it for them.

**Anytime:** `ba-next` (what now?), `ba-change` (a change request — also from UAT), `ba-docs` (formal documents:
BRD, URD, user guide), `ba-discover` (learn an existing system), `ba-audit` (who decided what, when), `ba-profile`
(adapt the workflow), `ba-step` (an extra stage a profile adds).

### Formal documents: BRD, URD, user guide (`ba-docs`)

Many organisations need a **BRD** (for sponsors), a **URD** (the users' view) or a **user guide** for end users.
`ba-docs brd | urd | user-guide` builds them from the feature's artifacts — no new requirements, every statement
cited or labelled *Fact / Assumption / Inference / Unknown* — into `requirements/<feature>/docs/`. Each document has
its own approver: the BRD the business owner, the URD a user representative and the PO, the user guide the PO with
support. A user guide describes **only behaviour that passed UAT**. Your house BRD format goes in
`.ba/local/templates/docs/brd.md` and wins over the default.

### New on a running project (`ba-discover`)

Joining a project whose system already exists? Run `ba-discover <system>` (*"I'm new here, help me learn the
current system"*). It builds a shared, sourced knowledge base in `knowledge/<system>/` — the parts of the system
and **who knows what**, today's processes and rules (as they really work, including workarounds), key data, the
glossary, open questions by person — plus a 10-minute onboarding brief. The system owner verifies each page;
later features cite the verified pages instead of asking again, and `ba discover <system>` shows what is stale.

## 5. Modes: as light or as strict as the work needs

| Mode | For | What changes |
|------|-----|--------------|
| **quick** | defects, small changes, one rule or screen | Model, UX, Spec and Review run Lite; handoff = build brief + QA pack; human gates 9 and 11 |
| **standard** | most features | the full plan from the approach; human gates 3, 8, 9, 10, 11, 12 |
| **controlled** | regulated, payments, high-security, vendor-delivered | every gate is a human gate; a second independent reviewer always runs; the AI model is recorded on every event |

The AI proposes the mode at `ba-start` from the request type; you can change it in `_status.md` → *Preferences*.

## 6. You decide what runs: the stage card

```
▶ Stage 6 · UI/UX — plan: Partial (web-app: admin screens only)
✅ Recommended: RUN LITE — only the changed screens; the rest reuses existing UI
⚠ If skipped or Lite (Critical: AI-agent builder): builders invent screen states
🩹 Minimum if Lite (must be done): ☐ states for every screen ☐ undesigned screens named
Choose: 1 Run · 2 Run Lite · 3 Skip · 4 Not now
```

**Run** — the full stage. **Run Lite** — the minimum, with the checklist shown. **Skip** — give a one-line reason;
it warns once and records it. **Not now** — it comes back via `ba-next`. Skipped and Lite stages appear in the
review and in a *Skipped stages & known gaps* box in every handoff pack.

## 7. Working with stakeholders

- **Questions come with options and a recommendation** — stakeholders can answer with a letter.
- **Answer by chat or by file**: *walkthrough* (a few questions at a time) or *file* (an answer form people fill in).
- **Paste answers back with who said it**: *"Answers from Linh (Finance) by email: …"*. Each becomes a decision
  (`D-…`) with the decider's name.
- **Blocking questions** stop a gate. You can proceed on a stated assumption; the decision records *Revisit at*.
- **Rounds that don't converge** get a *scope freeze* offer from round 3.
- **For people who don't read markdown:** `ba export <feature>` writes an Excel workbook (questions, assumptions,
  decisions, gates, acceptance criteria, rules, RTM); `ba status <feature> --html exports/<feature>.html` writes a
  one-page dashboard in the feature's language.

## 8. The approach adapts the workflow

At intake the AI picks one or more **profiles**, which decide which stages run, how, and which documents you get:
web app, mobile app, API, integration, batch job, data & reporting, AI feature, small change, workflow & approvals,
buy/configure (SaaS), data migration — plus 12 suggestions to install and your own (`ba-profile new`).

## 9. Language

Set *Language* in `_status.md` → *Preferences* (`en`, `vi`, …). Questions, documents, packs and chat follow it.
IDs (`US-003`), section headings, column names, canonical values (`Blocking`, `Open`, `Pass`) and the Gherkin
keywords `Given/When/Then` stay in English — the checks read them. The ambiguity check knows Vietnamese vague
words too (*nhanh, thân thiện, phù hợp, v.v.*).

## 10. Quality: how the workflow keeps requirements honest

- **Nothing invented.** Every rule, number and behaviour traces to a source (`SRC-`), a decision (`D-`) or a
  labelled assumption (`A-`). The AI labels what it infers.
- **Mechanical checks** run in seconds — the AI runs them at gates, and you can too:
  `python .ba/tools/ba.py check <feature>` → PASS / WARN (your judgement) / FAIL (blocks the gate).
- **Independent review** by a reviewer that did **not** write the requirements (a sub-agent, or a new chat). Every
  defect cites its evidence; *risks to verify* are listed separately and become questions.
- **Verdict by defects, not by a magic number:** *Pass* = no Critical, every Major fixed or owned with a date, score
  ≥ 80 · *Conditional* = no Critical but an unowned Major, or 70–79 · *Fail* = any Critical, or below 70.
- **Team walkthrough:** before handoff, the Dev/Tech Lead and QA confirm the stories are buildable and testable.
- **Live RTM:** `ba rtm <feature>` builds `rtm.md` — one row per acceptance criterion with its tests, results,
  evidence and who recorded them. A result without evidence FAILs the check; an AC changed after testing gets a
  new row to retest, and the old result stays in the history.

## 11. Handoff: who gets what

| Reader | File |
|--------|------|
| Product Owner | `handoff/po-approval.md` — one page: value, scope, decisions needed, risks, approval line |
| Developer / AI coding agent | `handoff/agent-brief.md` — self-contained build brief with a "don't guess, ask" list |
| QA | `handoff/qa-pack.md` — test scenarios and data; `rtm.md` for results |
| Designer | `handoff/design-brief.md` (if there's a UI) |
| Everyone else | `handoff/team-summary.md` — plain language, 2-minute read |
| Auditors / leads | `handoff/traceability.md` + `rtm.md` |
| Sponsor, business | `docs/brd.md` (if your organisation needs a BRD) |
| User representatives | `docs/urd.md` (if needed) |
| End users, support, trainers | `docs/user-guide-<role>.md` |
| Stakeholders without git | `exports/<feature>.xlsx`, `exports/<feature>.html` |

## 12. After handoff: refine, test, release, change

- **Refinement** (`ba-refine`): the PO names the sprint stories; Dev and QA assess them; the team splits and
  estimates. The AI records — it never estimates, prioritises or marks a story Ready.
- **Test and UAT** (`ba-uat`): every discrepancy is a *defect* (build ≠ approved AC), a *requirement gap* (no AC
  covers it → change request) or a *change request*. Results only from real runs, with evidence. The approver
  decides: Accept, Conditional acceptance (conditions with owners and dates), Reject or Pending.
- **Release** (`ba-release`): scope reconciled with the RTM row by row, known issues with owners, KPIs
  (`ba kpi <feature>`), lessons learned (an AI draft you review).
- **Change requests** (`ba-change`): impact analysis, then each part goes back to the right control point (e.g. a
  changed rule → the area owner re-confirms; a tested AC → retest).

## 13. Audit trail

Everything is recorded in a tamper-evident log per feature (`requirements/<feature>/_audit/events.jsonl`): stage
choices, gates, decisions, approvals (with the approver's name and evidence), reviews, handoffs, change requests,
and every file change with its fingerprint. Each event also records who reported it and which AI model was used.

- Ask in plain words: `ba-audit` *"Who approved the scope, and which stages were skipped?"*
- Verify nothing was altered: `python .ba/tools/ba.py audit verify --all`
- Never edit `_audit/` files. Keep the project in git: it anchors the history.

## 14. Where things are

```
requirements/<feature>/
  _status.md          progress, gates, governance, decisions, preferences — start here
  sources/            raw inputs as received (SRC-01, SRC-02…) — never edit
  01-intake.md … 08-review.md, 10-refinement.md, 11-uat.md, 12-release.md
  rtm.md              live traceability matrix (ba rtm)
  handoff/            the packs for each reader
  _audit/             the audit trail — never edit
exports/              Excel and dashboard copies (ba export, ba status --html)
.ba/core/             the workflow (replaced on update — don't edit)
.ba/local/            your own templates, profiles, checklists, glossary (override core)
```

**ID cheat sheet:** `SRC` source · `G` goal · `Q` question · `A` assumption · `D` decision · `R` risk · `IS` scope
item · `US` story · `AC` acceptance criterion (`AC-021.3` = story 21, criterion 3) · `BR` business rule · `NFR`
non-functional need · `MSG` message · `SCR` screen · `TS` test scenario · `CR` change request · `O` override.

## 15. Make it yours

- **House style:** copy a template from `.ba/core/templates/` to `.ba/local/templates/` and edit the copy.
- **Quality bar and human gates:** copy and edit `checklists/quality-rubric.md`; change which gates are human per
  mode in `.ba/config.json` → `"human_gates": {"standard": [3, 8, 9, 11]}`.
- **AI model on record:** `.ba/config.json` → `"model": "<model name>"` (or the `BA_MODEL` environment variable).
- **Glossary:** your organisation's terms in `.ba/local/glossary.md` on day one.
- **Kinds of work:** `ba-profile new` or `ba-profile install <name>`.

## 16. Tips

- **Give it everything early** — old policies and screenshots catch contradictions at intake, when they're cheap.
- **Answer with names and dates** (*"Linh, by email 22 Oct"*) — decisions and approvals need an owner.
- **Read the assumptions list** before PO sign-off: that's where plausible-but-unconfirmed details hide.
- **Don't skip the independent review or the walkthrough** — they find what drafting missed.
- **Treat a quick fix round with suspicion** — fixes can invent facts too; the workflow re-checks them.
- **Never let anyone (or the AI) type `Pass` without a run** — the RTM check will refuse it anyway.

## 17. Troubleshooting

| Problem | Fix |
|---------|-----|
| `/ba-…` or `#ba-…` commands don't appear | Start a new chat/session; check `.claude/skills`, `.github/prompts`, `.cursor/commands`, `.gemini/commands`, `.kiro/steering` |
| The AI doesn't follow the workflow | Ask it to *"read .ba/core/MANUAL.md and follow it"*; name the stage |
| `python` not found | Install Python 3.9+; on macOS/Linux use `python3` |
| `ba check` shows FAIL | The line names the file and the problem; fix it, then `ba turn <feature>` |
| "gate.passed … is a human gate" | Expected: the approver must approve. Record their decision (`D-`) and log the gate with their name and the evidence |
| `rtm` says "out of date" | Run `python .ba/tools/ba.py rtm <feature>` |
| `audit verify` says FAILED | A log was edited or a line removed. Restore it from git and find out why — never "repair" it |
| Kiro creates a "spec" | Use a normal chat session, not Kiro's Spec mode |
| Kiro Power: "can't find the package" | Run `python "<folder of the power>/package/tools/ba.py" where --save` once in the project; the folder is where Kiro keeps powers (`~/.kiro/powers/installed/…`) or where you cloned the repository |
| "Mode cell says … but the last change approved …" | The Mode changes only with the PO's or business owner's decision: log `settings.changed` "Mode: …" with their `D-` (or `ba approve --mode`) |

## Installing and updating

**Kiro:** import the Kiro Power from GitHub (`https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`) —
nothing to install. To pin a copy in a project, or for the other tools:

```bash
git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline
python ba-pipeline/install.py init   --target <your-project> --tools claude,agents-md --model <AI model>   # tools: or all
python ba-pipeline/install.py update --target <your-project>
python ba-pipeline/install.py status --target <your-project>
```

`update` keeps your `.ba/local/`, settings and requirements, and migrates existing status pages (mode, language,
delivery gates). Projects running **BA Copilot** upgrade in place with `update`. Start a new session afterwards.

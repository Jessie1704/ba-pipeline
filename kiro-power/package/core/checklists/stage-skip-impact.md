# Stage Skip Impact

Used by the *Stage entry protocol* (`MANUAL.md` §8) to warn the BA before a stage is skipped or run Lite.
Severity is the **default**; raise it one level when the feature is regulatory, high-security, payments, or
built by an AI agent/vendor without access to the BA, and lower it one level for `small-change`.
Always show and log the **adjusted** severity. It applies to **Run Lite** as well as Skip, and the
*minimum mitigation* becomes a checklist the Lite run must complete before its gate passes.

| Stage | Why it matters | If skipped — what breaks downstream | Default severity | Minimum mitigation if skipped | Skipping is reasonable when… |
|-------|----------------|-------------------------------------|------------------|-------------------------------|------------------------------|
| 1 Intake | Every later statement must cite a source | Nothing is grounded; reviewer flags facts as invented; approach can't be chosen from evidence | **Critical** | Paste the sources anyway and register them; at minimum record the approach as a `D-` from the BA | Never — use Lite instead |
| Approach (intake step 5) | Decides stages, documents, questions | Wrong stages run; profile questions and spec sections missed | High | BA states the approach explicitly (`D-`) | The BA already knows and records it |
| 2 Elicit | Finds gaps before they become defects | Unknowns are guessed or surface late as rework; blocking questions hidden | High | Run the gap lenses on the stage you're in; ask the foundation questions (success metrics, who decides); keep assumptions explicit (`A-`) | Sources are complete and recent; small change with a clear ticket |
| 3 Scope | Agreement on problem, goals, in/out | Scope creep; no measurable goals → traceability has no top; PO approval is blind | High | Write a 5-line scope (problem, 1 goal with its metric, in, out), name the business owner and PO in *Governance*, and get PO OK | Scope is fixed by an approved parent epic (link it) |
| 4 Model | Forces every path, state, permission | Missing alternative/error paths, dead-end states, permission gaps — the most common production defects | Medium | Stories must cover alt/failure paths explicitly; list states in the spec | Single-screen or single-rule change |
| 5 Stories | Unit of build & test | No AC → nothing testable; agent brief can't be produced | **Critical** | — (use Lite: fewer stories, never fewer AC) | Never for build work; process-only profile may skip |
| Extra stage (profile §11) | Whatever the profile defined it for | See the profile's gate; its outputs feed later stages | Medium (or as profile states) | Record what replaces it (e.g. vendor already chosen → `D-` with contract ref) | The decision it produces was already made and is documented |
| 6 UI/UX | Screens, states, accessibility | Builders invent screens; missing empty/error/permission states; accessibility not designed | High if users see a UI, otherwise N/A | Wireframe only changed screens; list states per screen in stories | No UI, or reusing existing screens unchanged |
| 7 Spec | Exact rules, fields, messages, NFRs | Agent guesses limits, formats, error text; NFRs untested | High | Put rules/fields/messages inline in stories; list NFRs in handoff | Small change where the change summary covers everything |
| 8 Review | Independent quality gate | Defects reach build; no score; PO approves unreviewed work | High | Run mechanical checks at least (`/ba-review` Lite) | Never fully — Lite is the floor recommendation |
| 9 Handoff | Role-specific packs and traceability | Each reader digs through raw artifacts; no traceability; no build brief | Medium | Produce at least `agent-brief.md` + `qa-pack.md`, and run `ba rtm` | Work is handed over in a tool (Jira/ADO) with the same content |
| 10 Refine | Stories understood, split and confirmed ready by the people who build and test them | Sprint starts with untestable or oversized stories; dependencies found mid-sprint; estimates guessed | Medium | PO names the sprint stories; QA confirms AC testability; dependencies listed with owners | The team refines in its own tool and records Ready there (link it) |
| 11 Test/UAT | Proof that the build matches the approved AC | Defects and requirement gaps reach production; acceptance without evidence; RTM never filled in | **Critical** | — (use Lite: the RTM rows of the release scope with real results and evidence, and the approver's decision) | Never for a release; another team's test process may supply the evidence (link it in the RTM) |
| 12 Release | Handover of what was really built | Release notes describe planned, not built, behaviour; known issues without owners; nothing learned | Medium | Scope reconciled with the RTM; known issues with owners | The feature is folded into a larger release that does this (link it) |

## Effects of a skip that every later stage must respect

- The skipped stage's gate is marked **Skipped (O-NN)** in `_status.md`, never *Passed*.
- Later stages apply the listed **minimum mitigation** themselves where possible.
- `/ba-review` raises a finding for each skip at the severity above, downgraded one level if the mitigation
  was applied, and the reviewer comments on whether the reason holds.
- Every handoff pack shows a **Skipped stages & known gaps** box so readers know what wasn't done.

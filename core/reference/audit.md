# Audit trail

Summary in MANUAL §9. Normally everything below happens through one `ba turn` per turn.

Two layers write to the same tamper-evident log (JSON Lines, SHA-256 hash chain):
- **File changes** — recorded with user, session, file and content hash, in one of two ways:
  - *Automatic*, where the tool has post-edit hooks (the Claude Code adapter registers `ba audit hook`).
  - **Otherwise, by `ba turn` (or `ba audit sync <slug>`)** at the end of every turn (and before `/ba-review` and
    `/ba-handoff`). It hashes every artifact and logs what was added, changed or removed since the last record.
    Run it even with hooks: it also catches edits made in other editors.
- **Workflow events** — you log them, normally as the `--events` array of `ba turn`; the single-event form is:
  ```
  ba audit event --feature <slug> --type <type> [--stage "<n Name>"] [--summary "<what>"] [--reason "<why>"] [--decision <choice>] [--severity Critical|High|Medium|Low] [--refs "D-012,O-03"] [--actor "<name if not the OS user>"] [--model "<AI model>"]
  ```
  Leave out `--feature` for workspace events (profiles, templates). It prints `audit #N <type> logged`; if that
  line is missing, the event was not recorded — log it again. **More than ~5 events at once** (e.g. a round of
  decisions): write them to a JSON array in a temporary file and log them in one call with
  `ba audit event --json-file <path>` (keys: `feature`, `type`, `stage`, `summary`, `reason`, `decision`,
  `severity`, `refs`, `actor`; `--feature` is the default for entries without one). Every entry is validated
  first; if one is invalid, none is logged.

Logs: `requirements/<slug>/_audit/events.jsonl` per feature; `audit/workspace.jsonl` for profiles,
templates, checklists, glossary and configuration. **Never edit or delete audit files** (write-protect them
where your tool allows); correct a mistake by logging a new `correction` event that references the `seq` it
corrects. `ba audit verify <slug>` (or `--all`) checks the chain.

| Type | When |
|------|------|
| `feature.created` | `/ba-start`, immediately after creating the folder (before writing any file) |
| `source.added` | a source is registered (`SRC-`) |
| `approach.proposed` / `approach.confirmed` / `approach.changed` | intake step 5, `/ba-change` |
| `override.added` / `override.removed` | an `O-` is recorded / withdrawn (with the `D-` that removes it) |
| `stage.started` / `stage.skipped` / `stage.deferred` | Stage entry protocol |
| `gate.passed` / `gate.failed` | end of each stage — this event also closes the stage |
| `gate.reopened` | a gate that passed is invalidated later (new Blocking or Decision-critical question, scope change before approval) |
| `check.run` | `ba check` run at a gate or review (summary: FAIL/WARN counts) |
| `file.added` / `file.changed` / `file.removed` | written by `ba audit sync` (and `file.write` / `file.edit` by hooks) |
| `question.raised` / `question.answered` | Blocking and Decision-critical questions only (others are in the files) |
| `assumption.confirmed` / `assumption.rejected` | high-risk assumptions |
| `decision.recorded` | every `D-` |
| `review.scored` | `/ba-review` (score and verdict in summary) |
| `approval.recorded` | PO/stakeholder approval or rejection — `--actor` is the approver as the BA reports it |
| `cr.logged` / `cr.decided` / `cr.applied` | `/ba-change` |
| `handoff.generated` | `/ba-handoff` (version in summary) |
| `profile.changed` | `/ba-profile` install/new/edit/retire (workspace log) |
| `correction` | fixing an earlier log entry |
| `rtm.updated` | optional: a round of test or UAT results recorded in `rtm.md` (summary: build, rows, who recorded) |
| `result.recorded` | written by `ba rtm` for every new or changed result (actor = *Recorded by*) |
| `settings.changed` | the feature's *Mode* changes (summary `Mode: <mode>`, refs the `D-`), or `human_gates` in the config (workspace) |
| `docs.generated` | `/ba-docs`: a document version is issued (summary: file and version) |
| `draft.reviewed` | a person reviewed an AI draft (decision `accepted` · `accepted-with-changes` · `rejected`; feeds the AI acceptance KPI) |
| `knowledge.updated` | `/ba-discover`: a knowledge base is created, extended or verified (workspace log) |
| `note` | anything else worth recording |
| `uat.round` | `/ba-uat`: a UAT round started or finished (summary: build, totals) |
| `release.completed` | `/ba-release`: handover accepted (refs: the `D-`) |

**Rules the log enforces** (MANUAL §4a, §8 step 5):
- the event type must be one of this table (exact, lower case); `stage.*` and `gate.*` need a feature and a
  numbered stage (`3 Scope`); `approval.recorded` needs a feature;
- **guarded events** — `approval.recorded`, `gate.passed` / `stage.skipped` on a human gate of the feature's mode, and
  `settings.changed` about the Mode or `human_gates`:
  - `actor` is a person, not the assistant;
  - `refs` are IDs only (`D-NN`, `SRC-NN`, `O-NN`) that exist, and include a `D-` from *Decision log* decided by
    the actor — one person, written as a full name, a given name of two words or more that no one else on the status
    page shares, the `STK-` ID, with or without diacritics or a form of address ("chị"); never a role word as the
    actor, though "PO" / "business owner" in *Decided by* resolves through *Governance*; the log also stores
    `actor_resolved`, the status page's own spelling;
  - for a gate, that `D-` has a readable date (2026-11-12 or 12/11/2026) not older than the latest `stage.started`
    of the stage;
  - a gate's actor is one of its approvers: *Gate approvers* may map gates to people (`3,8,9: STK-02; 11:
    STK-05`); otherwise the PO, the business owner and unmapped gate approvers; area owners only for approvals
    outside a gate; the BA only with an accepted role conflict (`D-` in *Role conflicts*);
  - a Mode / human-gates change is decided by the PO or the business owner; the rules use the latest such change
    (editing the Mode cell alone changes nothing — the *gates* check FAILs the mismatch);
  - in *controlled* mode a human gate is closed with `ba approve` (refused inside an AI tool or without a terminal;
    the approver types their name); every workflow event carries a real `model` name.

Each event stores `reported_by` (the OS account), `via` (`assistant:<tool>` when an AI tool's shell ran it — Kiro is
recognised by `TERM_PROGRAM=kiro`, so `ba approve` runs in an operating-system terminal outside Kiro — `BA_VIA`
can name a tool but can't turn an assistant's command into `cli`; `approve` for `ba approve`), `model` only for what
an AI tool ran, and `tool` (version). `ba check --only gates` WARNs (FAILs in controlled mode) on a human gate the AI
tool relayed without a `SRC-`. The log shows who ran what, from where, citing which decision; it cannot prove what a
person said in a meeting — the `SRC-` does.

**Actor honesty:** file records and `actor` default to the operating-system user. When you record someone
else's decision or approval (e.g. the PO approved in a meeting), set `actor` to that person **and** name the
evidence (`refs` = `SRC-NN` for the email/minutes) — the log shows who *reported* it via `session`.

`/ba-audit` shows, filters, verifies and exports the trail.

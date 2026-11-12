---
name: ba-spec
description: Produce the detailed functional and non-functional specification for a requirements feature in 07-spec.md — business rules catalogue, data dictionary with validations, screen behaviour rules (linked to 06-ux.md), error and message catalogue, integrations and interface contracts, notifications, reporting, NFRs, migration and compliance. Use after stories are drafted, or when the BA needs rules, fields, validations or NFRs written precisely enough for an AI agent or developer to implement. Tiếng Việt: đặc tả quy tắc nghiệp vụ, dữ liệu, thông báo, tích hợp, NFR.
---

# /ba-spec — Precision layer for builders

> **Start:** `ba context <slug> ba-spec` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "7 Spec"`.

Stories say *what*; the spec removes every remaining guess about *exactly how the business wants it to behave*.
Stay technology-neutral unless the BA provided the stack or a decision fixes it.

## Steps

1. Start from `ba context <slug> ba-spec` (status, open items, and §7–8 of every active profile). Then read what
   the spec is built on: `05-stories.md`, `04-model.md`, `06-ux.md` (if any), `03-scope.md` → *In scope* and
   *Constraints*, `04-model.md` → *Feature glossary* and `glossary.md`; open earlier files only where they are
   cited. The open questions listed by `ba context` are not settled: an unknown value is a `Q-` or an `A-`. Build `07-spec.md` from `templates/07-spec.md`. Include only sections that apply,
   but list skipped sections with a one-line reason.
   **Append the *Spec sections to add* (§7) of every active profile** (e.g. API contract, interface spec &
   field mapping, job specification, metric definitions & data quality rules, mobile specifics, AI behaviour
   & evaluation criteria) and fill them. Use each profile's §8 *NFR focus* as mandatory NFR categories.

2. **Business rules catalogue** `BR-NNN`: rule statement (one sentence, "must"), type (validation /
   calculation / eligibility / authorisation / timing / derivation), inputs, outcome, examples
   (a decision table for any rule with ≥2 conditions), source, stories using it.

3. **Data dictionary** per entity: field, business meaning, type, format/length, required, default,
   allowed values / range, validation rule (`BR-`), source system, PII/sensitivity class, retention.

4. **Screens / interactions** (if UI): don't duplicate `06-ux.md` — link each `SCR-` to its fields in the
   dictionary and its rules. Add here only behaviour the wireframes can't express (e.g. field dependencies,
   autosave, sort/filter/paging rules). If `/ba-ux` was skipped but a UI exists, flag it as a gap.

5. **Messages catalogue**: `MSG-NN` · trigger · exact user-facing text · severity · next action for user.

6. **Integrations** (per external system): direction, trigger, data exchanged (field mapping),
   frequency/volume, success criteria, failure handling (retry, timeout, idempotency, fallback, alert who).

7. **Notifications**: event, channel, recipient, timing, content summary, opt-out rules.

8. **Reporting & audit**: what must be reported/logged, who sees it, retention.

9. **NFRs** `NFR-NN` — every one measurable. Walk the categories in `checklists/nfr-checklist.md`
   (performance, scalability, availability, security, privacy, accessibility, usability, audit,
   localisation, compatibility, maintainability/observability). "Not applicable" needs a reason.

10. **Change-to-existing-system extras**: impacted existing functions, backward compatibility, data
    migration (mapping, cleansing, cutover), regression areas.

11. **Compliance matrix** (if regulatory): clause → requirement IDs → evidence.

12. **Cross-check:** every `BR-` referenced in stories exists here and vice versa; every field used in AC is in
    the dictionary; every error path in AC has a `MSG-`; every screen element and `MSG-` in `06-ux.md`
    resolves here. Add `Q-`s for any unknown values (limits, timeouts,
    text, retention) — never fill numbers by guesswork; propose a default as `A-` with risk.

13. **Grounding self-check.** The *Source* column of every `BR-` row must cite `SRC-`, `D-` or `A-` — and the
    citation must actually support the rule (not a nearby decision about something else). Every value you
    proposed (ranges, limits, timeouts, retries, schedules, transports, volumes, retention actions) is an `A-`
    in the single register `02-questions.md` → *Assumptions*; §9 *Proposed defaults* only lists those IDs.
    Check that no qualifier from the source was dropped or widened.
14. **Mechanical check:** `ba turn <slug> --events … --gate --stage "7 Spec"` runs the checks and logs them;
    fix every FAIL and run it again before logging `gate.passed`. While drafting, a quick unlogged
    `ba check <slug> --only ground,ids` on what you just wrote is fine.

## Gate
No undefined `BR-`/field/message references; all NFRs measurable; unknown values captured as `Q-`/`A-`;
every `BR-` cites `SRC-`/`D-`/`A-` (`ba check` *ground* passes); `ba check` has no FAIL.

## Finish with
- **Done:** counts of rules, fields, messages, NFRs.
- **Needs your decision:** proposed default values awaiting confirmation (table: item · proposed · why).
- **Next step:** `/ba-review`.

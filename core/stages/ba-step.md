---
name: ba-step
description: Run an extra stage that an approach profile adds to the workflow (for example vendor evaluation, fit-gap analysis, threat model, data profiling, cutover plan, experiment plan, autonomy review). Use when _status.md lists an extra stage as next, or the BA names one with /ba-step <stage-id>. Tiếng Việt: chạy stage bổ sung do profile thêm vào (đánh giá nhà cung cấp, threat model, cutover…).
---

# /ba-step <stage-id> — Run a profile-defined stage

> **Start:** `ba context <slug> ba-step` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "<n> <extra stage name>"`.

1. **Find the stage.** Read `_status.md` → *Approach* → *Stage plan*. Locate `<stage-id>`; find its definition
   in §11 *Extra stages* of the profile that owns it (or in an override). If no ID was given, list the extra
   stages in order with their status and run the first one not done.
   Unknown ID → list valid ones; never improvise a stage that isn't defined.

2. **Check readiness.** The stage named in *After stage* must have passed its gate (or the BA accepts
   proceeding — record a `D-`). Say which inputs you'll use.

3. **Run it.** Follow the defined *Steps* exactly, applying all `MANUAL.md` rules: cite sources, never invent
   facts, raise `Q-`/`A-` for unknowns, kill ambiguity, use IDs. If the profile names a template or table
   skeleton, use it; otherwise structure the output as: Purpose · Inputs · Method · Results · Findings ·
   Decisions needed · Impact on other artifacts.

4. **Write the output** to the document named in the definition (e.g. `05a-vendor-eval.md`).

5. **Propagate.** Results often change other artifacts (a selected vendor changes Spec; a threat model adds
   NFRs; data profiling adds DQ rules). List affected IDs and offer to update them now.

6. **Gate & status.** Evaluate the defined gate; update `_status.md` → *Gates* (add a row for the extra stage
   if missing), open-items counts, next action.

## Finish with
- **Done:** output document, key results, gate result.
- **Needs your decision:** the decisions the stage surfaced, with options and a recommendation.
- **Next step:** next stage in the plan (core or extra).

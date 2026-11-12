---
name: ba-profile
description: Manage approach profiles — list available profiles, install a suggested one from the catalogue, create a custom profile through a short interview, edit or retire one, validate profile files, override the approach for a single feature, or learn improvements from completed features. Use when the BA wants a new type of project/solution handled differently, says "we also do X kinds of projects", wants to change which stages or documents a type produces, or wants to tweak one feature's plan. Tiếng Việt: quản lý profile theo loại công việc; thay đổi kế hoạch của một feature.
---

# /ba-profile — Define how each kind of work is analysed

Profiles live in `profiles/`. Rules for anatomy, stage-plan values, extra stages, combining and overrides are
in `profiles/README.md` — read it first every time.

Sub-commands (infer from the BA's words if not given): `list` · `install <name>` · `new` · `edit <name>` ·
`retire <name>` · `validate [name]` · `override` · `learn`.

## list
Table of every profile: name, title, kind, origin, status, version, and how many features in `requirements/`
use it (grep `_status.md` → *Approach*). Then a second table of catalogue entries not yet installed with
their one-line "use when". End with: "Install one, create your own, or override a feature?"

## install <name>
1. Read the entry in `profiles/catalogue.md`.
2. Expand it into a full profile from `profiles/_template.md` (`origin: catalogue`, `status: active`, `version: 1.0`):
   write concrete extra questions (8–12), the spec section skeletons as markdown tables, handoff extras with
   contents, review checks, and extra stages with full steps and gates.
3. Show the BA a summary (stage plan + extra stages + deliverables); adjust on feedback.
4. Save as `profiles/<name>.md`, add a row to `profiles/README.md` §2, mark the catalogue entry *Installed*.
5. Run `validate <name>`.

## new — interview, then generate
Ask in **one message** (accept partial answers; propose defaults for the rest and show them back):
1. Name and one-line description — what kind of work is this?
2. Example: a recent project of this kind, and what went wrong or was missed in its requirements.
3. Signals — how would we recognise it in notes/emails? When is it *not* this?
4. Is it a **solution** type or a **modifier** that adds to other types?
5. Which standard stages change? (for each of Model, Stories, UX, Spec, Review, Handoff: Run / Adapted / Lite / Partial / Skip)
6. Extra stages needed that the workflow doesn't have? (name, after which stage, what it produces)
7. Documents the team expects at the end, and who reads each.
8. Questions BAs always forget to ask for this kind of work; mandatory NFRs; rules a reviewer should check.

Then:
- Draft the profile from `_template.md` (`origin: custom`, `status: draft`). Fill gaps from your own
  expertise but **mark every section you invented with `<!-- proposed -->`** so the BA can see what's theirs.
- Compare with existing profiles and the catalogue: if > 70 % overlaps an existing one, recommend a
  **modifier** or an **override** instead, and say why.
- Show the stage plan as a one-screen summary; iterate until the BA approves; set `status: active`.
- Save, register in `profiles/README.md` §2, run `validate`.

## edit <name>
Make the change, bump `version` (minor for wording, major for stage plan/deliverable changes), append a
*Changelog* line at the bottom. List features whose `_status.md` uses this profile and are past Scope; ask
per feature whether to re-apply (if yes, treat it like a change request via `/ba-change`).

## retire <name>
Set `status: retired`, keep the file, update README table. Never delete — past features reference it.

## validate [name]
For each (or the named) profile check:
- Front-matter has all 7 keys; `name` equals the file name; `kind` ∈ {solution, modifier}.
- Headings `## 1.` … `## 11.` all present, in order.
- Stage plan values ∈ {Run, Adapted, Lite, Partial, Skip}; Review not Skip; Intake/Elicit/Scope not Skip.
- Extra stages: unique IDs (no clash with other profiles), *After stage* refers to a real stage or another
  extra stage, output file name follows `<NN><letter>-<id>.md`, gate is stated.
- Handoff extras have a file name and an audience.
Report pass/fail per check with fixes.

## override (one feature)
Ask which feature and what to change. Write a row in that feature's `_status.md` → *Approach* →
*Overrides* (`O-NN`, target, change, reason, `D-`), then update its stage plan and deliverables.
If the same override already exists in 2+ other features, suggest `edit` or `new` instead.

## learn
Scan finished features (`requirements/*/_status.md` with stage Handoff or Approved) and their `08-review.md`:
- Overrides repeated across features using the same profile → propose a profile edit.
- Review defects that recur for a profile (e.g. "missing retry policy" in integration features) → propose
  an extra gap question or review check.
- Questions that were Blocking in most features of a profile → propose adding them to §3.
Present proposals as a numbered list; apply only the ones the BA accepts.

## Audit
Log `profile.changed` (no `--feature`, so it goes to the workspace log) for install, new, edit and retire,
with the profile name and version in the summary. `override` logs `override.added` in the feature's log.

## Finish with
- **Done:** what was created/changed, validation result.
- **Needs your decision:** draft sections marked `proposed`, re-apply to existing features.
- **Next step:** usually "Run `/ba-intake` on your feature — the new profile will be considered."
